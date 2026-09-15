"""What the frame shows about one aircraft."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Airport:
    code: str  # IATA code, e.g. "ORD"
    city: str  # display name, e.g. "Chicago"
    lat: float
    lon: float


@dataclass(frozen=True)
class Sighting:
    """One aircraft, ready to display. Unknown values are ``None`` or ``""``."""

    title: str  # livery brand or operator, e.g. "United Airlines"
    subtitle: str  # aircraft, e.g. "Boeing 737 MAX 9"
    seen_at: datetime  # when the position was reported (timezone-aware)
    brand: str = ""  # artwork brand key, e.g. "united"
    type_code: str = ""  # ICAO type designator, e.g. "B39M"
    registration: str = ""
    flight: str = ""  # flight number, e.g. "UA1737"
    callsign: str = ""  # used when there is no flight number, e.g. "N9640V"
    origin: Airport | None = None
    destination: Airport | None = None
    lat: float | None = None
    lon: float | None = None
    altitude_ft: int | None = None
    ground_speed_kt: float | None = None
    track_deg: float | None = None
    distance_nm: float | None = None  # from the frame's location
