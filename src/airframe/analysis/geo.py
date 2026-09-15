"""Small geometry helpers.

Distances use a flat local projection around a reference point. Within ~25 NM that is
accurate to well under 1% (a few hundredths of a mile), which is plenty for traffic stats.
"""

from __future__ import annotations

import numpy as np

NM_PER_DEG_LAT = 60.0


def to_local_nm(lat, lon, lat0: float, lon0: float) -> tuple[np.ndarray, np.ndarray]:
    """Project degrees to (east, north) nautical miles relative to (lat0, lon0)."""
    x = (np.asarray(lon, dtype=np.float64) - lon0) * NM_PER_DEG_LAT * np.cos(np.radians(lat0))
    y = (np.asarray(lat, dtype=np.float64) - lat0) * NM_PER_DEG_LAT
    return x, y


def distance_nm(lat, lon, lat0: float, lon0: float) -> np.ndarray:
    x, y = to_local_nm(lat, lon, lat0, lon0)
    return np.hypot(x, y)


def closest_on_segment(x0, y0, x1, y1) -> tuple[np.ndarray, np.ndarray]:
    """For segments (x0, y0) -> (x1, y1), find the point closest to the origin.

    Returns (fraction along each segment in [0, 1], distance of that point from the origin).
    """
    dx = x1 - x0
    dy = y1 - y0
    length_sq = dx * dx + dy * dy
    frac = np.divide(
        -(x0 * dx + y0 * dy),
        length_sq,
        out=np.zeros_like(length_sq, dtype=np.float64),
        where=length_sq > 0,
    )
    frac = np.clip(frac, 0.0, 1.0)
    return frac, np.hypot(x0 + frac * dx, y0 + frac * dy)
