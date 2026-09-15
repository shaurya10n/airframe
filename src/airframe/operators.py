"""ICAO airline designators: which callsigns belong to airlines.

Source: Mictronics readsb-protobuf ``operators.json`` (designator -> [name, country,
telephony]), downloaded once into the cache directory.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import requests

from airframe.http import download

OPERATORS_URL = (
    "https://raw.githubusercontent.com/Mictronics/readsb-protobuf/dev/webapp/src/db/operators.json"
)
# Airline flights use a 3-letter ICAO designator followed by a flight number, e.g. DAL1234.
AIRLINE_CALLSIGN = re.compile(r"^([A-Z]{3})\d[0-9A-Z]{0,4}$")


@dataclass(frozen=True)
class Operator:
    name: str
    country: str


def load_operators(
    cache_dir: Path, session: requests.Session, max_age_days: float | None = None
) -> dict[str, Operator]:
    path = download(cache_dir / "operators.json", OPERATORS_URL, session, max_age_days)
    data = json.loads(path.read_text(encoding="utf-8"))
    return {code: Operator(v[0], v[1] if len(v) > 1 else "") for code, v in data.items()}


def airline_code(callsign: str, operators: dict[str, Operator]) -> str:
    """ICAO airline designator from a callsign, or "" for non-airline callsigns (e.g. N12345)."""
    match = AIRLINE_CALLSIGN.match(callsign)
    return match.group(1) if match and match.group(1) in operators else ""
