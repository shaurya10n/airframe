"""Decode readsb heatmap files (``globe_history/YYYY/MM/DD/heatmap/NN.bin.ttf``).

adsb.lol runs readsb, which writes one heatmap file per half hour containing a position
for every tracked aircraft every 10 seconds. Format (readsb ``globe_index.c``, tar1090
``drawHeatmap``): a flat array of 16-byte little-endian records
``(int32 hex, int32 lat, int32 lon, int16 alt, int16 gs)``, usually gzip-compressed.

* The file starts with an index section (one record per time slice), skipped here.
* Each slice starts with a marker record: ``hex == 0x0E7F7C9D``; ``lat``/``lon`` are the
  high/low 32 bits of the slice start in epoch milliseconds; ``alt`` is the interval (s).
* Position records: the low 25 bits of ``hex`` are the address (bit 24 = non-ICAO), the top
  5 bits the address type; ``lat``/``lon`` are degrees x 1e6; ``alt`` is altitude / 25 ft
  (-123 = on ground, -124 = unknown); ``gs`` is ground speed x 10 kt (-1 = unknown).
* Callsign records: ``lat`` has bit 30 set (low bits hold the squawk) and the 8 bytes of
  ``lon`` + ``alt`` + ``gs`` are the ASCII callsign. readsb emits one per aircraft at least
  once a minute and whenever the callsign or squawk changes.
"""

from __future__ import annotations

import gzip
import math

import numpy as np

from airframe.analysis import geo

SLICE_MARKER = 0x0E7F7C9D
CALLSIGN_FLAG = 1 << 30
ADDR_MASK = 0x1FFFFFF
NON_ICAO_FLAG = 1 << 24
ALT_GROUND = -123
ALT_UNKNOWN = -124
GS_UNKNOWN = -1

RECORD_DTYPE = np.dtype(
    [("hex", "<u4"), ("lat", "<i4"), ("lon", "<i4"), ("alt", "<i2"), ("gs", "<i2")]
)
POSITION_DTYPE = np.dtype(
    [
        ("addr", "<u4"),
        ("ts", "<i8"),  # epoch seconds (slice start)
        ("lat", "<f8"),
        ("lon", "<f8"),
        ("alt_ft", "<f4"),  # NaN when on ground or unknown
        ("ground", "?"),
        ("gs_kt", "<f4"),  # NaN when unknown
    ]
)
CALLSIGN_DTYPE = np.dtype([("addr", "<u4"), ("ts", "<i8"), ("callsign", "S8")])


def addr_to_hex(addr: int) -> str:
    """Format an address the way readsb/tar1090 do: 6 hex digits, ``~`` prefix if non-ICAO."""
    prefix = "~" if addr & NON_ICAO_FLAG else ""
    return f"{prefix}{addr & 0xFFFFFF:06x}"


def decode(raw: bytes, lat0: float, lon0: float, radius_nm: float) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(positions, callsigns)`` within ``radius_nm`` of (lat0, lon0) from one file.

    Callsign records are kept only for addresses with at least one position in range.
    """
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    if len(raw) % RECORD_DTYPE.itemsize:
        raise ValueError(f"heatmap length {len(raw)} is not a multiple of 16")
    rec = np.frombuffer(raw, dtype=RECORD_DTYPE)

    is_marker = rec["hex"] == SLICE_MARKER
    markers = np.flatnonzero(is_marker)
    if markers.size == 0:
        raise ValueError("heatmap has no slice markers")
    slice_start_ms = (rec["lat"][markers].astype(np.int64) << 32) | (
        rec["lon"][markers].astype(np.int64) & 0xFFFFFFFF
    )
    slice_idx = np.cumsum(is_marker) - 1  # -1 marks the leading index section
    body = ~is_marker & (slice_idx >= 0)

    lat = rec["lat"].astype(np.int64)
    lon = rec["lon"].astype(np.int64)
    is_callsign = body & (lat >= CALLSIGN_FLAG)

    # Cheap integer bounding box over the whole file, exact circle on the survivors.
    dlat = math.ceil(radius_nm / geo.NM_PER_DEG_LAT * 1e6)
    dlon = math.ceil(radius_nm / (geo.NM_PER_DEG_LAT * math.cos(math.radians(lat0))) * 1e6)
    in_box = (
        body
        & ~is_callsign
        & (np.abs(lat - round(lat0 * 1e6)) <= dlat)
        & (np.abs(lon - round(lon0 * 1e6)) <= dlon)
    )
    idx = np.flatnonzero(in_box)
    plat = lat[idx] / 1e6
    plon = lon[idx] / 1e6
    in_circle = geo.distance_nm(plat, plon, lat0, lon0) <= radius_nm
    idx, plat, plon = idx[in_circle], plat[in_circle], plon[in_circle]

    alt = rec["alt"][idx]
    gs = rec["gs"][idx]
    positions = np.empty(idx.size, dtype=POSITION_DTYPE)
    positions["addr"] = rec["hex"][idx] & ADDR_MASK
    positions["ts"] = slice_start_ms[slice_idx[idx]] // 1000
    positions["lat"] = plat
    positions["lon"] = plon
    positions["ground"] = alt == ALT_GROUND
    positions["alt_ft"] = np.where((alt == ALT_GROUND) | (alt == ALT_UNKNOWN), np.nan, alt * 25.0)
    positions["gs_kt"] = np.where(gs == GS_UNKNOWN, np.nan, gs / 10.0)

    cs_idx = np.flatnonzero(is_callsign)
    cs_idx = cs_idx[np.isin(rec["hex"][cs_idx] & ADDR_MASK, positions["addr"])]
    record_bytes = np.frombuffer(raw, dtype=np.uint8).reshape(-1, RECORD_DTYPE.itemsize)
    callsigns = np.empty(cs_idx.size, dtype=CALLSIGN_DTYPE)
    callsigns["addr"] = rec["hex"][cs_idx] & ADDR_MASK
    callsigns["ts"] = slice_start_ms[slice_idx[cs_idx]] // 1000
    callsigns["callsign"] = np.ascontiguousarray(record_bytes[cs_idx, 8:]).view("S8").ravel()
    callsigns = callsigns[np.char.strip(callsigns["callsign"]) != b""]
    return positions, callsigns
