"""Estimate the visible livery brand of an aircraft, with a confidence level.

The operating carrier from the callsign isn't the livery: SkyWest, Republic and others fly
Delta Connection, United Express and American Eagle aircraft. Evidence, strongest first:

1. ``registration``: evidence tied to the airframe itself
   * an entry in ``livery_registrations.csv``
   * the aircraft DB military flag (brand ``military``)
   * the aircraft DB owner matching one of the operator's brands in ``operator_brands.csv``
     (e.g. a Delta-owned CRJ-900 flown by SkyWest is a Delta Connection aircraft)
2. ``inferred``: evidence from the flight rather than the airframe
   * the operator flies for exactly one brand
   * the flight-number block (e.g. SKW3xxx) is flown only by owner-confirmed aircraft of one
     brand (learned by the offline analysis)
   * the callsign's route touches a hub of exactly one of the operator's brands and plausibly
     passes near the location
   * other flights of the same registration were inferred to a single brand (analysis)
3. ``unresolved``: no evidence, or conflicting evidence. Never guessed.

Used by both the frame and the offline analysis.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from airframe import geo
from airframe.refdata import read_reference_csv
from airframe.routes import RouteLookup

REGISTRATION = "registration"
INFERRED = "inferred"
UNRESOLVED = "unresolved"
CONFIDENCES = (REGISTRATION, INFERRED, UNRESOLVED)
MILITARY = "military"

METHOD_LABELS = {
    "registration_csv": "listed in livery_registrations.csv",
    "military_flag": "aircraft DB military flag",
    "owner": "registered owner matches one of the operator's brands",
    "sole_operator": "operator flies for one brand only",
    "flight_block": "flight-number block flown by owner-confirmed aircraft",
    "route_hub": "route touches a hub of one candidate brand",
    "registration_consensus": "same registration inferred on other flights",
    "no_airline_callsign": "no airline callsign (GA, business, other)",
    "operator_unmapped": "operator not in operator_brands.csv",
    "mixed_liveries": "operator flies mixed liveries",
    "ambiguous": "multi-brand operator, no distinguishing evidence",
    "conflict": "registration inferred to different brands",
}

FLIGHT_NUMBER = re.compile(r"^[A-Z]{3}(\d{4})[A-Z]?$")


class AircraftFacts(Protocol):
    registration: str
    military: bool
    operator: str  # registered owner/operator from the aircraft DB
    airline_icao: str
    callsign: str


def flight_block(callsign: str) -> str:
    """Thousand-block of a 4-digit airline flight number: ``SKW3456`` -> ``3xxx``."""
    match = FLIGHT_NUMBER.match(callsign)
    return f"{match.group(1)[0]}xxx" if match else ""


@dataclass(frozen=True)
class Brand:
    brand: str
    name: str
    country: str
    hubs: frozenset[str]


@dataclass(frozen=True)
class OperatorBrand:
    brand: str  # "" marks an operator known to fly mixed or unbranded liveries
    owner_patterns: tuple[str, ...]


@dataclass(frozen=True)
class LiveryTables:
    brands: dict[str, Brand]
    operators: dict[str, tuple[OperatorBrand, ...]]
    registrations: dict[str, str]

    @classmethod
    def load(cls, reference_dir: Path) -> LiveryTables:
        brands = {
            row["brand"]: Brand(
                row["brand"],
                row["name"],
                row.get("country", ""),
                frozenset(_split(row.get("hubs", ""))),
            )
            for row in read_reference_csv(reference_dir / "brands.csv")
        }
        if MILITARY not in brands:
            raise ValueError(f"brands.csv must define the {MILITARY!r} brand")

        operators: dict[str, list[OperatorBrand]] = defaultdict(list)
        for row in read_reference_csv(reference_dir / "operator_brands.csv"):
            op, brand = row["operator_icao"].upper(), row.get("brand", "")
            if brand and brand not in brands:
                raise ValueError(f"operator_brands.csv: unknown brand {brand!r} for {op}")
            patterns = tuple(p.upper() for p in _split(row.get("owner_patterns", "")))
            operators[op].append(OperatorBrand(brand, patterns))

        registrations = {}
        for row in read_reference_csv(reference_dir / "livery_registrations.csv"):
            if row.get("brand") not in brands:
                raise ValueError(
                    f"livery_registrations.csv: unknown brand {row.get('brand')!r} "
                    f"for {row['registration']}"
                )
            registrations[row["registration"].upper()] = row["brand"]
        return cls(brands, {op: tuple(rows) for op, rows in operators.items()}, registrations)


@dataclass(frozen=True)
class Resolution:
    brand: str
    confidence: str
    method: str
    basis: str


class LiveryResolver:
    def __init__(
        self,
        tables: LiveryTables,
        *,
        lat: float,
        lon: float,
        routes: RouteLookup | None = None,
        block_min_support: int = 10,
        block_min_purity: float = 0.95,
        route_max_offset_nm: float = 75.0,
    ):
        self.tables = tables
        self._lat, self._lon = lat, lon
        self._routes = routes
        self._block_min_support = block_min_support
        self._block_min_purity = block_min_purity
        self._route_max_offset_nm = route_max_offset_nm
        self._options = {
            op: sorted({r.brand for r in rows if r.brand}) for op, rows in tables.operators.items()
        }
        self._blocks: dict[tuple[str, str], str] = {}
        self._consensus: dict[str, str] = {}
        self._conflicts: dict[str, set[str]] = {}
        self.flight_blocks: list[dict] = []  # learned block statistics, for the report

    def learn(self, aircraft: Iterable[AircraftFacts]) -> None:
        """Learn flight-number blocks and per-registration consensus from many sightings."""
        aircraft = list(aircraft)
        votes: dict[tuple[str, str], Counter] = defaultdict(Counter)
        for e in aircraft:
            block = flight_block(e.callsign)
            if block and len(self._options.get(e.airline_icao, ())) > 1:
                airframe = self._airframe(e)
                if airframe and airframe.method != "military_flag":
                    votes[(e.airline_icao, block)][airframe.brand] += 1

        self._blocks, self.flight_blocks = {}, []
        for (op, block), counter in sorted(votes.items()):
            brand, top = counter.most_common(1)[0]
            total = sum(counter.values())
            used = top >= self._block_min_support and top / total >= self._block_min_purity
            if used:
                self._blocks[(op, block)] = brand
            self.flight_blocks.append(
                {
                    "operator_icao": op,
                    "block": block,
                    "brand": brand,
                    "confirmed_encounters": total,
                    "purity": top / total,
                    "used": used,
                    "all_brands": "; ".join(f"{b} {n}" for b, n in counter.most_common()),
                }
            )

        if self._routes is not None:
            self._routes.prefetch(e.callsign for e in aircraft if self.needs_route(e))

        brands_by_registration: dict[str, set[str]] = defaultdict(set)
        for e in aircraft:
            if e.registration and self._airframe(e) is None:
                flight = self._flight(e)
                if flight:
                    brands_by_registration[e.registration].add(flight.brand)
        self._consensus = {
            reg: next(iter(b)) for reg, b in brands_by_registration.items() if len(b) == 1
        }
        self._conflicts = {reg: b for reg, b in brands_by_registration.items() if len(b) > 1}

    def resolve(self, e: AircraftFacts) -> Resolution:
        airframe = self._airframe(e)
        if airframe:
            return airframe
        op = e.airline_icao
        if not op:
            return Resolution("", UNRESOLVED, "no_airline_callsign", "no airline callsign")
        if op not in self._options:
            return Resolution(
                "", UNRESOLVED, "operator_unmapped", f"{op} is not in operator_brands.csv"
            )
        options = self._options[op]
        if not options:
            return Resolution("", UNRESOLVED, "mixed_liveries", f"{op} flies mixed liveries")
        if e.registration in self._conflicts:
            brands = " and ".join(sorted(self._conflicts[e.registration]))
            return Resolution(
                "",
                UNRESOLVED,
                "conflict",
                f"{e.registration} inferred as {brands} on different flights",
            )
        flight = self._flight(e)
        if flight:
            return flight
        if brand := self._consensus.get(e.registration):
            return Resolution(
                brand,
                INFERRED,
                "registration_consensus",
                f"other flights of {e.registration} inferred as {brand}",
            )
        return Resolution(
            "",
            UNRESOLVED,
            "ambiguous",
            f"{op} flies for {', '.join(options)}; no distinguishing evidence",
        )

    def fields(self, e: AircraftFacts) -> dict[str, str]:
        """Encounter fields for ``dataclasses.replace``."""
        r = self.resolve(e)
        brand = self.tables.brands.get(r.brand)
        return {
            "brand": r.brand,
            "brand_name": brand.name if brand else "",
            "brand_country": brand.country if brand else "",
            "brand_confidence": r.confidence,
            "brand_method": r.method,
            "brand_basis": r.basis,
        }

    def needs_route(self, e: AircraftFacts) -> bool:
        """Whether a route lookup could still decide this aircraft's brand."""
        return (
            len(self._options.get(e.airline_icao, ())) > 1
            and self._airframe(e) is None
            and (e.airline_icao, flight_block(e.callsign)) not in self._blocks
        )

    def _airframe(self, e: AircraftFacts) -> Resolution | None:
        if e.registration and (brand := self.tables.registrations.get(e.registration.upper())):
            return Resolution(
                brand,
                REGISTRATION,
                "registration_csv",
                f"{e.registration} in livery_registrations.csv",
            )
        if e.military:
            return Resolution(MILITARY, REGISTRATION, "military_flag", "aircraft DB military flag")
        owner = e.operator.upper()
        if owner and e.airline_icao:
            matches = {
                r.brand
                for r in self.tables.operators.get(e.airline_icao, ())
                if r.brand and any(p in owner for p in r.owner_patterns)
            }
            if len(matches) == 1:
                brand = next(iter(matches))
                return Resolution(
                    brand,
                    REGISTRATION,
                    "owner",
                    f"owner {e.operator!r} + operator {e.airline_icao}",
                )
        return None

    def _flight(self, e: AircraftFacts) -> Resolution | None:
        options = self._options.get(e.airline_icao, [])
        if len(options) == 1:
            return Resolution(
                options[0],
                INFERRED,
                "sole_operator",
                f"{e.airline_icao} flies only for {options[0]}",
            )
        if len(options) < 2:
            return None
        block = flight_block(e.callsign)
        if brand := self._blocks.get((e.airline_icao, block)):
            return Resolution(
                brand,
                INFERRED,
                "flight_block",
                f"{e.airline_icao}{block} flights are flown by owner-confirmed {brand} aircraft",
            )
        return self._route_brand(e, options)

    def _route_brand(self, e: AircraftFacts, options: list[str]) -> Resolution | None:
        if self._routes is None:
            return None
        airports = self._routes.get(e.callsign)
        if len(airports) < 2:
            return None
        offset = min(
            geo.segment_distance_nm(self._lat, self._lon, a.lat, a.lon, b.lat, b.lon)
            for a, b in zip(airports, airports[1:], strict=False)
        )
        if offset > self._route_max_offset_nm:
            return None
        codes = [a.iata for a in airports]
        matches = [b for b in options if self.tables.brands[b].hubs & set(codes)]
        if len(matches) != 1:
            return None
        return Resolution(
            matches[0], INFERRED, "route_hub", f"route {'-'.join(codes)} touches a {matches[0]} hub"
        )


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip()]
