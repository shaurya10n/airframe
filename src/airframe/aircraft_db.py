"""Aircraft database: registration, type, description and owner by ICAO hex.

Source: wiedehopf/tar1090-db ``aircraft.csv.gz``, the database readsb uses. Rows are
``hex;registration;type;flags;description;year;owner_operator;`` where ``flags`` is a string
of 0/1 digits (military, interesting, PIA, LADD).

The file has ~600k rows, too many to hold in memory on a Pi Zero, so it is converted once
into an indexed SQLite file and queried per aircraft.
"""

from __future__ import annotations

import gzip
import io
import logging
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import requests

from airframe.http import download

log = logging.getLogger(__name__)

AIRCRAFT_DB_URL = "https://raw.githubusercontent.com/wiedehopf/tar1090-db/csv/aircraft.csv.gz"


@dataclass(frozen=True)
class Aircraft:
    registration: str = ""
    type_code: str = ""
    description: str = ""
    year: int | None = None
    owner_operator: str = ""
    military: bool = False
    interesting: bool = False


def parse_row(line: str) -> tuple[str, Aircraft] | None:
    fields = line.rstrip("\n").split(";")
    if len(fields) < 7 or not fields[0]:
        return None
    flags = fields[3]
    return fields[0].lower(), Aircraft(
        registration=fields[1],
        type_code=fields[2],
        description=fields[4],
        year=int(fields[5]) if fields[5].isdigit() else None,
        owner_operator=fields[6],
        military=flags[:1] == "1",
        interesting=flags[1:2] == "1",
    )


def open_text(path: Path) -> io.TextIOBase:
    # The HTTP layer may already have undone the gzip, so sniff rather than trust the name.
    with path.open("rb") as f:
        gzipped = f.read(2) == b"\x1f\x8b"
    if gzipped:
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("r", encoding="utf-8", errors="replace")


def build(csv_path: Path, db_path: Path) -> None:
    tmp = db_path.with_name(db_path.name + ".tmp")
    tmp.unlink(missing_ok=True)
    conn = sqlite3.connect(tmp)
    conn.execute(
        "CREATE TABLE aircraft (hex TEXT PRIMARY KEY, registration TEXT, type_code TEXT, "
        "description TEXT, year INTEGER, owner TEXT, military INTEGER, interesting INTEGER) "
        "WITHOUT ROWID"
    )
    with open_text(csv_path) as f:
        conn.executemany(
            "INSERT OR REPLACE INTO aircraft VALUES (?, ?, ?, ?, ?, ?, ?, ?)", _rows(f)
        )
    conn.commit()
    conn.close()
    tmp.replace(db_path)


def _rows(lines) -> Iterator[tuple]:
    for line in lines:
        parsed = parse_row(line)
        if parsed:
            hex_code, a = parsed
            yield (
                hex_code, a.registration, a.type_code, a.description, a.year,
                a.owner_operator, int(a.military), int(a.interesting),
            )  # fmt: skip


class AircraftDB:
    def __init__(self, path: Path):
        self._conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)

    def lookup(self, hex_code: str) -> Aircraft | None:
        row = self._conn.execute(
            "SELECT registration, type_code, description, year, owner, military, interesting "
            "FROM aircraft WHERE hex = ?",
            (hex_code.lower(),),
        ).fetchone()
        if row is None:
            return None
        reg, type_code, desc, year, owner, military, interesting = row
        return Aircraft(reg, type_code, desc, year, owner, bool(military), bool(interesting))


def open_database(
    cache_dir: Path, session: requests.Session, max_age_days: float = 14
) -> AircraftDB:
    """Download (or refresh) the CSV and rebuild the SQLite index when the CSV is newer."""
    csv_path = download(cache_dir / "aircraft.csv.gz", AIRCRAFT_DB_URL, session, max_age_days)
    db_path = cache_dir / "aircraft.sqlite"
    if not db_path.exists() or db_path.stat().st_mtime < csv_path.stat().st_mtime:
        log.info("building %s (one-time, takes a minute on a Pi)", db_path)
        build(csv_path, db_path)
    return AircraftDB(db_path)
