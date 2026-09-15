"""Small geometry helpers.

Distances use a flat local projection around a reference point. Within ~25 NM that is
accurate to well under 1% (a few hundredths of a mile), which is plenty for traffic stats.
"""

from __future__ import annotations

import math

import numpy as np

NM_PER_DEG_LAT = 60.0
EARTH_RADIUS_NM = 3440.065


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


def segment_distance_nm(
    lat: float, lon: float, lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Distance from a point to the great-circle segment between two points (any length)."""
    p, a, b = _unit(lat, lon), _unit(lat1, lon1), _unit(lat2, lon2)
    normal = np.cross(a, b)
    norm = float(np.linalg.norm(normal))
    if norm > 1e-12:
        normal /= norm
        sin_cross = float(np.dot(p, normal))
        foot = p - sin_cross * normal
        foot_norm = float(np.linalg.norm(foot))
        if foot_norm > 1e-12:
            foot /= foot_norm
            if abs(_angle(a, foot) + _angle(foot, b) - _angle(a, b)) < 1e-9:
                return abs(math.asin(max(-1.0, min(1.0, sin_cross)))) * EARTH_RADIUS_NM
    return min(_angle(p, a), _angle(p, b)) * EARTH_RADIUS_NM


def _unit(lat: float, lon: float) -> np.ndarray:
    phi, lam = math.radians(lat), math.radians(lon)
    return np.array([math.cos(phi) * math.cos(lam), math.cos(phi) * math.sin(lam), math.sin(phi)])


def _angle(u: np.ndarray, v: np.ndarray) -> float:
    return math.atan2(float(np.linalg.norm(np.cross(u, v))), float(np.dot(u, v)))
