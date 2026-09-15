"""adsb.lol live API: aircraft near a point.

``GET https://api.adsb.lol/v2/point/{lat}/{lon}/{radius}`` (radius in NM) returns readsb-style
JSON ``{"ac": [...], "now": <epoch ms>}``. Each aircraft has ``hex``, ``flight`` (callsign),
``r`` (registration), ``t`` (type), ``alt_baro`` (feet or ``"ground"``), ``gs`` (ground speed,
kt), ``track``, ``lat``/``lon``, ``dst`` (NM from the point), ``seen_pos`` (seconds since
the position) and ``dbFlags`` (1 military, 2 interesting, 4 PIA, 8 LADD).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import requests

from airframe import geo

API_URL = "https://api.adsb.lol/v2/point/{lat}/{lon}/{radius}"
MAX_POSITION_AGE_S = 60
MILITARY_FLAG = 1
INTERESTING_FLAG = 2


@dataclass(frozen=True)
class Contact:
    hex: str
    callsign: str
    registration: str
    type_code: str
    lat: float
    lon: float
    altitude_ft: int | None
    on_ground: bool
    ground_speed_kt: float | None
    track_deg: float | None
    distance_nm: float
    db_flags: int
    seen_at: datetime


def fetch(
    session: requests.Session,
    lat: float,
    lon: float,
    radius_nm: float,
    url: str = API_URL,
    timeout: float = 20,
) -> list[Contact]:
    resp = session.get(
        url.format(lat=f"{lat:.4f}", lon=f"{lon:.4f}", radius=f"{radius_nm:g}"), timeout=timeout
    )
    resp.raise_for_status()
    return parse(resp.json(), lat, lon)


def parse(payload: dict, lat0: float, lon0: float) -> list[Contact]:
    now = (payload.get("now") or 0) / 1000 or datetime.now(UTC).timestamp()
    contacts = []
    for ac in payload.get("ac") or []:
        lat, lon = ac.get("lat"), ac.get("lon")
        age = ac.get("seen_pos") or 0
        if lat is None or lon is None or age > MAX_POSITION_AGE_S:
            continue
        altitude = next(
            (int(ac[k]) for k in ("alt_baro", "alt_geom") if isinstance(ac.get(k), int | float)),
            None,
        )
        dst = ac.get("dst")
        contacts.append(
            Contact(
                hex=str(ac.get("hex", "")).lower(),
                callsign=str(ac.get("flight") or "").strip(),
                registration=str(ac.get("r") or ""),
                type_code=str(ac.get("t") or ""),
                lat=float(lat),
                lon=float(lon),
                altitude_ft=altitude,
                on_ground=ac.get("alt_baro") == "ground",
                ground_speed_kt=_number(ac.get("gs")),
                track_deg=_number(ac.get("track")),
                distance_nm=(
                    float(dst)
                    if isinstance(dst, int | float)
                    else geo.distance_nm(lat0, lon0, lat, lon)
                ),
                db_flags=int(ac.get("dbFlags") or 0),
                seen_at=datetime.fromtimestamp(now - age, UTC),
            )
        )
    return contacts


def _number(value) -> float | None:
    return float(value) if isinstance(value, int | float) else None
