"""Human-readable values for the frame."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

MISSING = "—"
MILES_PER_NM = 1.150779
COMPASS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
UNITS = ("imperial", "aviation")


def altitude(ft: int | None) -> str:
    return MISSING if ft is None else f"{ft:,} ft"


def speed(kt: float | None, units: str = "imperial") -> str:
    if kt is None:
        return MISSING
    if units == "aviation":
        return f"{round(kt):,} kt"
    return f"{round(kt * MILES_PER_NM):,} mph"


def distance(nm: float | None, units: str = "imperial") -> str:
    if nm is None:
        return MISSING
    if units == "aviation":
        return f"{nm:.1f} NM"
    return f"{nm * MILES_PER_NM:.1f} mi"


def heading(deg: float | None) -> str:
    if deg is None:
        return MISSING
    whole = round(deg) % 360
    return f"{whole:03d}° {COMPASS[round(whole / 45) % 8]}"


def coordinates(lat: float | None, lon: float | None) -> str:
    if lat is None or lon is None:
        return ""
    return (
        f"{abs(lat):.4f}° {'N' if lat >= 0 else 'S'}   {abs(lon):.4f}° {'E' if lon >= 0 else 'W'}"
    )


def clock(moment: datetime, tz: ZoneInfo) -> str:
    return moment.astimezone(tz).strftime("%I:%M %p").lstrip("0")


def seen(
    seen_at: datetime, now: datetime, place: str, tz: ZoneInfo, fresh_minutes: float = 2
) -> str:
    """Footer status: live location, or when a held aircraft was last seen."""
    if (now - seen_at).total_seconds() / 60 < fresh_minutes:
        return f"Over {place} · {clock(seen_at, tz)}"
    return f"Last seen at {clock(seen_at, tz)}"
