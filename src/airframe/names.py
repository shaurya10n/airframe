"""Display names: airlines (with IATA codes for flight numbers) and aircraft models."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from airframe.operators import Operator
from airframe.refdata import read_reference_csv

FLIGHT_NUMBER = re.compile(r"^[A-Z]{3}(\d{1,4})$")


@dataclass(frozen=True)
class Airline:
    icao: str
    iata: str  # blank when callsign numbers don't match marketed flight numbers
    name: str


@dataclass(frozen=True)
class AircraftName:
    manufacturer: str
    model: str

    @property
    def full(self) -> str:
        return f"{self.manufacturer} {self.model}".strip()


class Names:
    def __init__(self, reference_dir: Path):
        self.airlines = {
            row["icao"].upper(): Airline(row["icao"].upper(), row.get("iata", ""), row["name"])
            for row in read_reference_csv(reference_dir / "airlines.csv")
        }
        self.aircraft = {
            row["type"].upper(): AircraftName(row["manufacturer"], row["model"])
            for row in read_reference_csv(reference_dir / "aircraft_names.csv")
        }

    def aircraft_name(self, type_code: str, description: str) -> AircraftName:
        return (
            self.aircraft.get(type_code.upper())
            or from_description(description)
            or AircraftName("", type_code)
        )

    def airline_name(self, icao: str, operators: dict[str, Operator]) -> str:
        if icao in self.airlines:
            return self.airlines[icao].name
        return operators[icao].name if icao in operators else ""

    def flight_number(self, callsign: str, airline_icao: str) -> str:
        """``DAL1234`` -> ``DL1234`` for airlines with a usable IATA code, else ""."""
        airline = self.airlines.get(airline_icao)
        match = FLIGHT_NUMBER.match(callsign)
        if not (airline and airline.iata and match):
            return ""
        return f"{airline.iata}{int(match.group(1))}"


def from_description(description: str) -> AircraftName | None:
    """``"CESSNA 172 Skyhawk"`` -> Cessna / 172 Skyhawk (manufacturer is the leading caps)."""
    words = description.split()
    if not words:
        return None
    maker = []
    for word in words:
        if len(word) > 1 and word.isupper() and not any(ch.isdigit() for ch in word):
            maker.append(word)
        else:
            break
    if not maker:
        maker = words[:1]
    manufacturer = " ".join("-".join(p.capitalize() for p in w.split("-")) for w in maker)
    return AircraftName(manufacturer, " ".join(words[len(maker) :]))
