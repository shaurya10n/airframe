"""Great-circle helpers in plain Python."""

from __future__ import annotations

import math

EARTH_RADIUS_NM = 3440.065


def distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_NM * math.asin(math.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial true bearing from point 1 to point 2."""
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360


def segment_distance_nm(
    lat: float, lon: float, lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Distance from a point to the great-circle segment between two points."""
    p, a, b = _unit(lat, lon), _unit(lat1, lon1), _unit(lat2, lon2)
    normal = _cross(a, b)
    norm = _norm(normal)
    if norm > 1e-12:
        normal = tuple(c / norm for c in normal)
        sin_cross = _dot(p, normal)
        foot = tuple(pc - sin_cross * nc for pc, nc in zip(p, normal, strict=True))
        foot_norm = _norm(foot)
        if foot_norm > 1e-12:
            foot = tuple(c / foot_norm for c in foot)
            if abs(_angle(a, foot) + _angle(foot, b) - _angle(a, b)) < 1e-9:
                return abs(math.asin(max(-1.0, min(1.0, sin_cross)))) * EARTH_RADIUS_NM
    return min(_angle(p, a), _angle(p, b)) * EARTH_RADIUS_NM


def _unit(lat: float, lon: float) -> tuple[float, float, float]:
    phi, lam = math.radians(lat), math.radians(lon)
    return (math.cos(phi) * math.cos(lam), math.cos(phi) * math.sin(lam), math.sin(phi))


def _cross(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def _dot(u, v) -> float:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def _norm(u) -> float:
    return math.sqrt(_dot(u, u))


def _angle(u, v) -> float:
    return math.atan2(_norm(_cross(u, v)), _dot(u, v))
