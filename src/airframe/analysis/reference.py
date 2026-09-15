"""Aircraft reference data for the analysis: registration, type and owner for many hex codes.

See ``airframe.aircraft_db`` for the source and row format.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import requests

from airframe.aircraft_db import AIRCRAFT_DB_URL, Aircraft, open_text, parse_row
from airframe.http import download


def load_aircraft(
    cache_dir: Path, hexes: Iterable[str], session: requests.Session
) -> dict[str, Aircraft]:
    """Look up only the given hex codes (keeps memory small; the full DB has ~600k rows)."""
    path = download(cache_dir / "aircraft.csv.gz", AIRCRAFT_DB_URL, session)
    wanted = set(hexes)
    found: dict[str, Aircraft] = {}
    with open_text(path) as f:
        for line in f:
            if line.split(";", 1)[0].lower() not in wanted:
                continue
            parsed = parse_row(line)
            if parsed:
                found[parsed[0]] = parsed[1]
    return found
