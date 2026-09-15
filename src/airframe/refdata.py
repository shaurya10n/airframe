"""Readers for the editable reference CSVs in ``data/reference/`` (stdlib only)."""

from __future__ import annotations

import csv
from pathlib import Path


def read_reference_csv(path: Path) -> list[dict[str, str]]:
    """Read an editable reference CSV, skipping blank lines and ``#`` comments."""
    with path.open(encoding="utf-8", newline="") as f:
        lines = [line for line in f if line.strip() and not line.lstrip().startswith("#")]
    return [
        {k.strip(): (v or "").strip() for k, v in row.items() if k} for row in csv.DictReader(lines)
    ]


def load_families(path: Path) -> dict[str, str]:
    """ICAO type designator -> artwork family code, from ``aircraft_families.csv``."""
    return {row["type"].upper(): row["family"] for row in read_reference_csv(path)}
