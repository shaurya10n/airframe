"""Turn raw ADS-B contacts into scored candidates, and the chosen one into a Sighting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from airframe import geo, scoring
from airframe.adsb import INTERESTING_FLAG, MILITARY_FLAG, Contact
from airframe.aircraft_db import Aircraft, AircraftDB
from airframe.artwork import ArtworkLibrary
from airframe.livery import MILITARY, LiveryResolver
from airframe.models import Airport, Sighting
from airframe.names import Names
from airframe.operators import Operator, airline_code
from airframe.routes import RouteAirport, RouteLookup

ROUTE_MAX_OFFSET_NM = 75.0  # routes passing further from the frame are stale or wrong


@dataclass(frozen=True)
class Facts:
    """What livery resolution needs to know about an aircraft."""

    registration: str
    military: bool
    operator: str
    airline_icao: str
    callsign: str


@dataclass(frozen=True)
class Candidate:
    contact: Contact
    aircraft: Aircraft
    type_code: str
    airline_icao: str
    brand: str
    military: bool
    artwork: Path | None
    artwork_level: str
    interestingness: float
    proximity: float
    score: float

    @property
    def hex(self) -> str:
        return self.contact.hex


class Enricher:
    def __init__(
        self,
        *,
        lat: float,
        lon: float,
        home_country: str,
        scale_nm: float,
        weights: scoring.Weights,
        aircraft_db: AircraftDB,
        operators: dict[str, Operator],
        names: Names,
        livery: LiveryResolver,
        routes: RouteLookup | None,
        artwork: ArtworkLibrary,
        frequency: scoring.TrafficFrequency,
    ):
        self._lat, self._lon = lat, lon
        self._home_country = home_country
        self._scale_nm = scale_nm
        self._weights = weights
        self._db = aircraft_db
        self._operators = operators
        self._names = names
        self._livery = livery
        self._routes = routes
        self._artwork = artwork
        self._frequency = frequency

    def candidates(self, contacts: list[Contact]) -> list[Candidate]:
        """Airborne aircraft, best score first."""
        rows = []
        for c in contacts:
            if c.on_ground:
                continue
            record = (None if c.hex.startswith("~") else self._db.lookup(c.hex)) or Aircraft()
            airline = airline_code(c.callsign, self._operators)
            military = record.military or bool(c.db_flags & MILITARY_FLAG)
            registration = c.registration or record.registration
            facts = Facts(registration, military, record.owner_operator, airline, c.callsign)
            rows.append((c, record, airline, military, facts))

        if self._routes is not None:
            self._routes.prefetch(f.callsign for *_, f in rows if self._livery.needs_route(f))

        brands = self._livery.tables.brands
        result = []
        for c, record, airline, military, facts in rows:
            brand = self._livery.resolve(facts).brand
            type_code = c.type_code or record.type_code
            artwork, level = self._artwork.match(brand, type_code)
            country = brands[brand].country if brand in brands else ""
            interest = scoring.interestingness(
                self._frequency.rarity(brand, type_code),
                type_code=type_code,
                military=military,
                flagged=record.interesting or bool(c.db_flags & INTERESTING_FLAG),
                foreign=bool(country) and country != self._home_country,
            )
            prox = scoring.proximity(c.distance_nm, c.altitude_ft, self._scale_nm)
            result.append(
                Candidate(
                    contact=c,
                    aircraft=record,
                    type_code=type_code,
                    airline_icao=airline,
                    brand=brand,
                    military=military,
                    artwork=artwork,
                    artwork_level=level,
                    interestingness=interest,
                    proximity=prox,
                    score=scoring.score(self._weights, interest, prox, level),
                )
            )
        return sorted(result, key=lambda x: x.score, reverse=True)

    def sighting(self, candidate: Candidate) -> Sighting:
        c = candidate.contact
        name = self._names.aircraft_name(candidate.type_code, candidate.aircraft.description)
        brand = self._livery.tables.brands.get(candidate.brand)
        airline = self._names.airline_name(candidate.airline_icao, self._operators)
        if brand and brand.brand != MILITARY:
            title, subtitle = brand.name, name.full
        elif airline:
            title, subtitle = airline, name.full
        elif candidate.military:
            title, subtitle = "Military", name.full
        elif name.manufacturer:
            title, subtitle = name.manufacturer, name.model
        else:
            title, subtitle = "Aircraft", name.model
        flight = self._names.flight_number(c.callsign, candidate.airline_icao)
        origin, destination = self.route(c) if candidate.airline_icao else (None, None)
        return Sighting(
            title=title,
            subtitle=subtitle,
            seen_at=c.seen_at,
            brand=candidate.brand,
            type_code=candidate.type_code,
            registration=c.registration or candidate.aircraft.registration,
            flight=flight,
            callsign="" if flight else c.callsign,
            origin=origin,
            destination=destination,
            lat=c.lat,
            lon=c.lon,
            altitude_ft=c.altitude_ft,
            ground_speed_kt=c.ground_speed_kt,
            track_deg=c.track_deg,
            distance_nm=c.distance_nm,
        )

    def route(self, c: Contact) -> tuple[Airport | None, Airport | None]:
        """The leg of the callsign's route this aircraft is flying, if the route is plausible."""
        if self._routes is None or not c.callsign:
            return None, None
        self._routes.prefetch([c.callsign])
        airports = self._routes.get(c.callsign)
        best = None
        for a, b in zip(airports, airports[1:], strict=False):
            offset = geo.segment_distance_nm(self._lat, self._lon, a.lat, a.lon, b.lat, b.lon)
            if offset > ROUTE_MAX_OFFSET_NM:
                continue
            # On multi-leg routes (DTW-MBS-DTW) pick the leg the aircraft is heading along.
            turn = 0.0
            if c.track_deg is not None:
                bearing = geo.bearing_deg(c.lat, c.lon, b.lat, b.lon)
                turn = abs((bearing - c.track_deg + 180) % 360 - 180)
            if best is None or turn < best[0]:
                best = (turn, a, b)
        if best is None:
            return None, None
        return _airport(best[1]), _airport(best[2])


def _airport(a: RouteAirport) -> Airport:
    code = a.iata or a.icao
    return Airport(code=code, city=a.city or code, lat=a.lat, lon=a.lon)
