"""Turn regional position samples into deduplicated, enriched encounters for a radius.

An encounter is one pass of one aircraft through the radius. Samples of the same aircraft
less than ``gap`` apart belong to the same encounter, so an aircraft circling or flying
pattern work counts once. Heatmaps sample every 10 s, so the closest approach is refined by
also checking the closest point on the straight segment between consecutive samples.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NamedTuple

import numpy as np

from airframe.analysis import geo, heatmap, reference
from airframe.analysis.config import Airport

CALLSIGN_MAX_GAP_S = 30 * 60


class Pass(NamedTuple):
    addr: int
    entered: float  # epoch seconds
    exited: float
    closest_time: float
    closest_nm: float
    altitude_ft: float  # NaN when unknown


@dataclass(frozen=True)
class Encounter:
    hex: str
    callsign: str
    registration: str
    type_code: str
    type_description: str
    airline_icao: str
    airline_name: str
    airline_country: str
    operator: str  # registered owner/operator from the aircraft DB
    entered_utc: datetime
    closest_utc: datetime
    closest_nm: float
    altitude_ft: int | None
    year: int | None
    military: bool
    interesting: bool
    airport_ops: tuple[str, ...]  # airports it landed at or departed from around this pass
    # Visible livery and artwork family, filled in by livery.py / artwork.py.
    brand: str = ""
    brand_name: str = ""
    brand_country: str = ""
    brand_confidence: str = "unresolved"
    brand_method: str = ""
    brand_basis: str = ""
    family: str = ""


@dataclass
class TrackPoints:
    """Samples plus interpolated closest points on segments, sorted by (addr, time)."""

    addr: np.ndarray
    time: np.ndarray
    dist: np.ndarray
    alt: np.ndarray


def closest_points(
    positions: np.ndarray, lat0: float, lon0: float, max_segment_gap_s: float
) -> TrackPoints:
    p = positions[np.lexsort((positions["ts"], positions["addr"]))]
    x, y = geo.to_local_nm(p["lat"], p["lon"], lat0, lon0)
    t = p["ts"].astype(np.float64)
    alt = p["alt_ft"].astype(np.float64)

    dt = np.diff(t)
    seg = np.flatnonzero((p["addr"][1:] == p["addr"][:-1]) & (dt > 0) & (dt <= max_segment_gap_s))
    frac, seg_dist = geo.closest_on_segment(x[seg], y[seg], x[seg + 1], y[seg + 1])
    a0, a1 = alt[seg], alt[seg + 1]
    seg_alt = a0 + frac * (a1 - a0)
    seg_alt = np.where(np.isnan(seg_alt), np.fmax(a0, a1), seg_alt)

    addr = np.concatenate([p["addr"], p["addr"][seg]])
    time = np.concatenate([t, t[seg] + frac * dt[seg]])
    order = np.lexsort((time, addr))
    return TrackPoints(
        addr=addr[order],
        time=time[order],
        dist=np.concatenate([np.hypot(x, y), seg_dist])[order],
        alt=np.concatenate([alt, seg_alt])[order],
    )


def find_passes(points: TrackPoints, radius_nm: float, gap_s: float) -> list[Pass]:
    inside = points.dist <= radius_nm
    addr, time, dist, alt = (
        points.addr[inside],
        points.time[inside],
        points.dist[inside],
        points.alt[inside],
    )
    if addr.size == 0:
        return []

    new = np.ones(addr.size, dtype=bool)
    new[1:] = (addr[1:] != addr[:-1]) | (np.diff(time) > gap_s)
    group = np.cumsum(new) - 1
    starts = np.flatnonzero(new)
    ends = np.r_[starts[1:], addr.size] - 1
    by_dist = np.lexsort((dist, group))
    closest = by_dist[np.searchsorted(group[by_dist], np.arange(starts.size))]

    return [
        Pass(
            int(addr[c]),
            float(time[s]),
            float(time[e]),
            float(time[c]),
            float(dist[c]),
            float(alt[c]),
        )
        for s, e, c in zip(starts, ends, closest, strict=True)
    ]


class CallsignIndex:
    def __init__(self, callsigns: np.ndarray):
        keys = _key(callsigns["addr"], callsigns["ts"])
        order = np.argsort(keys, kind="stable")
        self._keys = keys[order]
        self._names = callsigns["callsign"][order]

    def nearest(self, addr: int, t: float, max_gap_s: float = CALLSIGN_MAX_GAP_S) -> str:
        i = int(np.searchsorted(self._keys, _key(addr, int(t)), side="right"))
        best, best_gap = "", max_gap_s
        for j in (i - 1, i):
            if 0 <= j < self._keys.size and int(self._keys[j]) >> 32 == addr:
                gap = abs((int(self._keys[j]) & 0xFFFFFFFF) - t)
                if gap < best_gap or (gap == best_gap and not best):
                    best, best_gap = self._names[j].decode("ascii", "replace").strip(), gap
        return best


class AirportOps:
    """Records when each aircraft was on the ground or low near each airport."""

    def __init__(
        self,
        positions: np.ndarray,
        airports: tuple[Airport, ...],
        radius_nm: float,
        max_agl_ft: float,
    ):
        self._keys: dict[str, np.ndarray] = {}
        for ap in airports:
            near = geo.distance_nm(positions["lat"], positions["lon"], ap.lat, ap.lon) <= radius_nm
            low = positions["ground"] | (positions["alt_ft"] <= ap.elevation_ft + max_agl_ft)
            sel = positions[near & low]
            self._keys[ap.code] = np.sort(_key(sel["addr"], sel["ts"]))

    def between(self, addr: int, start: float, end: float) -> tuple[str, ...]:
        lo, hi = _key(addr, math.floor(start)), _key(addr, math.ceil(end))
        return tuple(
            code
            for code, keys in self._keys.items()
            if np.searchsorted(keys, hi, side="right") > np.searchsorted(keys, lo, side="left")
        )


def enrich(
    passes: list[Pass],
    callsigns: CallsignIndex,
    aircraft: dict[str, reference.Aircraft],
    operators: dict[str, reference.Operator],
    airport_ops: AirportOps,
    airport_window_s: float,
) -> list[Encounter]:
    unknown = reference.Aircraft()
    encounters = []
    for p in passes:
        hex_code = heatmap.addr_to_hex(p.addr)
        info = aircraft.get(hex_code, unknown)
        callsign = callsigns.nearest(p.addr, p.closest_time)
        code = reference.airline_code(callsign, operators)
        airline = operators.get(code)
        encounters.append(
            Encounter(
                hex=hex_code,
                callsign=callsign,
                registration=info.registration,
                type_code=info.type_code,
                type_description=info.description,
                airline_icao=code,
                airline_name=airline.name if airline else "",
                airline_country=airline.country if airline else "",
                operator=info.owner_operator,
                entered_utc=datetime.fromtimestamp(p.entered, UTC),
                closest_utc=datetime.fromtimestamp(p.closest_time, UTC),
                closest_nm=p.closest_nm,
                altitude_ft=None if math.isnan(p.altitude_ft) else int(round(p.altitude_ft)),
                year=info.year,
                military=info.military,
                interesting=info.interesting,
                airport_ops=airport_ops.between(
                    p.addr, p.entered - airport_window_s, p.exited + airport_window_s
                ),
            )
        )
    return encounters


def _key(addr, ts) -> np.ndarray:
    """Pack (address, epoch seconds) into one sortable int64."""
    return (np.asarray(addr, dtype=np.int64) << 32) | np.asarray(ts, dtype=np.int64)
