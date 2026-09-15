"""Aircraft and airline reference tables used to enrich encounters.

* Aircraft DB: wiedehopf/tar1090-db ``aircraft.csv.gz``, the database readsb uses for
  registration/type. Rows are ``hex;registration;type;flags;description;year;owner_operator;``
  where ``flags`` is a string of 0/1 digits: military, interesting, PIA, LADD.
* Operators: Mictronics readsb-protobuf ``operators.json``, mapping ICAO 3-letter airline
  designator to ``[name, country, telephony]``.

Both are downloaded once into ``data/cache/reference/``. Delete the files to refresh them.
Note that the aircraft DB reflects today's registry, not the registry on the analyzed dates.
"""

from __future__ import annotations

import gzip
import io
import json
import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import requests

log = logging.getLogger(__name__)

AIRCRAFT_DB_URL = "https://raw.githubusercontent.com/wiedehopf/tar1090-db/csv/aircraft.csv.gz"
OPERATORS_URL = (
    "https://raw.githubusercontent.com/Mictronics/readsb-protobuf/dev/webapp/src/db/operators.json"
)
# Airline flights use a 3-letter ICAO designator followed by a flight number, e.g. DAL1234, SKW5501.
AIRLINE_CALLSIGN = re.compile(r"^([A-Z]{3})\d[0-9A-Z]{0,4}$")


@dataclass(frozen=True)
class Aircraft:
    registration: str = ""
    type_code: str = ""
    description: str = ""
    year: int | None = None
    owner_operator: str = ""
    military: bool = False
    interesting: bool = False


@dataclass(frozen=True)
class Operator:
    name: str
    country: str


def load_aircraft(
    cache_dir: Path, hexes: Iterable[str], session: requests.Session
) -> dict[str, Aircraft]:
    """Look up only the given hex codes (keeps memory small; the full DB has ~600k rows)."""
    path = _download(cache_dir / "aircraft.csv.gz", AIRCRAFT_DB_URL, session)
    wanted = set(hexes)
    found: dict[str, Aircraft] = {}
    with _open_text(path) as f:
        for line in f:
            fields = line.rstrip("\n").split(";")
            if len(fields) < 7 or fields[0].lower() not in wanted:
                continue
            flags = fields[3]
            found[fields[0].lower()] = Aircraft(
                registration=fields[1],
                type_code=fields[2],
                description=fields[4],
                year=int(fields[5]) if fields[5].isdigit() else None,
                owner_operator=fields[6],
                military=flags[:1] == "1",
                interesting=flags[1:2] == "1",
            )
    return found


def load_operators(cache_dir: Path, session: requests.Session) -> dict[str, Operator]:
    path = _download(cache_dir / "operators.json", OPERATORS_URL, session)
    data = json.loads(path.read_text(encoding="utf-8"))
    return {code: Operator(v[0], v[1] if len(v) > 1 else "") for code, v in data.items()}


def airline_code(callsign: str, operators: dict[str, Operator]) -> str:
    """ICAO airline designator from a callsign, or "" for non-airline callsigns (e.g. N12345)."""
    match = AIRLINE_CALLSIGN.match(callsign)
    return match.group(1) if match and match.group(1) in operators else ""


def _download(path: Path, url: str, session: requests.Session) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        log.info("downloading %s", url)
        resp = session.get(url, timeout=120)
        resp.raise_for_status()
        tmp = path.with_name(path.name + ".part")
        tmp.write_bytes(resp.content)
        tmp.replace(path)
    return path


def _open_text(path: Path) -> io.TextIOBase:
    # The HTTP layer may already have undone the gzip, so sniff rather than trust the name.
    with path.open("rb") as f:
        gzipped = f.read(2) == b"\x1f\x8b"
    if gzipped:
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("r", encoding="utf-8", errors="replace")
