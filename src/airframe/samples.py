"""Sample sightings for previewing the poster.

Positions, altitudes, speeds and tracks are real adsb.lol traffic over Ann Arbor
(September 2026). Routes come from the adsb.lol route database and were only kept where
they match what the aircraft was doing.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airframe.models import Airport, Sighting

PLACE = "Ann Arbor"
TIMEZONE = "America/Detroit"

DFW = Airport("DFW", "Dallas–Fort Worth", 32.8968, -97.0380)
DOH = Airport("DOH", "Doha", 25.2731, 51.6081)
DTW = Airport("DTW", "Detroit", 42.2124, -83.3534)
EWR = Airport("EWR", "Newark", 40.6925, -74.1687)
FRA = Airport("FRA", "Frankfurt", 50.0264, 8.5431)
GRR = Airport("GRR", "Grand Rapids", 42.8808, -85.5228)
IAH = Airport("IAH", "Houston", 29.9844, -95.3414)
JAX = Airport("JAX", "Jacksonville", 30.4941, -81.6879)
MBS = Airport("MBS", "Saginaw", 43.5329, -84.0796)
MSP = Airport("MSP", "Minneapolis", 44.8820, -93.2218)


def _at(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


_UNITED = Sighting(
    title="United Airlines", subtitle="Boeing 737 MAX 9", seen_at=_at("2026-09-10T16:33:00+00:00"),
    brand="united", type_code="B39M", registration="N37563", flight="UA1737",
    origin=MSP, destination=EWR, lat=42.2819, lon=-83.7388,
    altitude_ft=27000, ground_speed_kt=542, track_deg=98, distance_nm=0.30,
)  # fmt: skip

SAMPLES: list[tuple[str, Sighting, datetime]] = [
    ("united-737max9", _UNITED, _UNITED.seen_at + timedelta(seconds=40)),
    (
        "delta-connection-crj900",
        Sighting(
            title="Delta Connection",
            subtitle="Bombardier CRJ-900",
            seen_at=_at("2026-09-11T16:18:56+00:00"),
            brand="delta-connection",
            type_code="CRJ9",
            registration="N821SK",
            callsign="SKW3898",
            origin=MBS,
            destination=DTW,
            lat=42.2710,
            lon=-83.7353,
            altitude_ft=4301,
            ground_speed_kt=267,
            track_deg=182,
            distance_nm=0.14,
        ),
        _at("2026-09-11T16:19:30+00:00"),
    ),
    (
        "american-787-8",
        Sighting(
            title="American Airlines",
            subtitle="Boeing 787-8 Dreamliner",
            seen_at=_at("2026-09-09T23:37:18+00:00"),
            brand="american",
            type_code="B788",
            registration="N809AA",
            flight="AA70",
            origin=DFW,
            destination=FRA,
            lat=42.2675,
            lon=-83.7649,
            altitude_ft=36986,
            ground_speed_kt=571,
            track_deg=60,
            distance_nm=0.10,
        ),
        _at("2026-09-09T23:38:00+00:00"),
    ),
    (
        "allegiant-a320-generic",
        Sighting(
            title="Allegiant Air",
            subtitle="Airbus A320",
            seen_at=_at("2026-09-11T15:56:01+00:00"),
            brand="allegiant",
            type_code="A320",
            registration="N198NV",
            flight="G4584",
            origin=JAX,
            destination=GRR,
            lat=42.2625,
            lon=-83.7411,
            altitude_ft=28551,
            ground_speed_kt=443,
            track_deg=296,
            distance_nm=0.83,
        ),
        _at("2026-09-11T15:56:30+00:00"),
    ),
    (
        "skywest-crj700-unknown-livery",
        Sighting(
            title="SkyWest Airlines",
            subtitle="Bombardier CRJ-700",
            seen_at=_at("2026-09-12T14:42:23+00:00"),
            type_code="CRJ7",
            registration="N751SK",
            callsign="SKW6255",
            lat=42.2880,
            lon=-83.8818,
            altitude_ft=12406,
            ground_speed_kt=324,
            track_deg=294,
            distance_nm=1.37,
        ),
        _at("2026-09-12T14:43:00+00:00"),
    ),
    (
        "lufthansa-787-9-generic",
        Sighting(
            title="Lufthansa",
            subtitle="Boeing 787-9 Dreamliner",
            seen_at=_at("2026-09-10T20:39:52+00:00"),
            brand="lufthansa",
            type_code="B789",
            registration="D-ABPB",
            flight="LH443",
            origin=DTW,
            destination=FRA,
            lat=42.2591,
            lon=-83.6900,
            altitude_ft=10464,
            ground_speed_kt=309,
            track_deg=10,
            distance_nm=2.37,
        ),
        _at("2026-09-10T20:40:30+00:00"),
    ),
    (
        "citation-private",
        Sighting(
            title="Cessna",
            subtitle="Citation 650",
            seen_at=_at("2026-09-11T21:53:40+00:00"),
            type_code="C650",
            registration="N806SQ",
            callsign="N806SQ",
            lat=42.2816,
            lon=-83.7403,
            altitude_ft=2925,
            ground_speed_kt=238,
            track_deg=81,
            distance_nm=0.30,
        ),
        _at("2026-09-11T21:54:10+00:00"),
    ),
    (
        "cessna-172",
        Sighting(
            title="Cessna",
            subtitle="172 Skyhawk",
            seen_at=_at("2026-09-12T18:42:54+00:00"),
            type_code="C172",
            registration="N9640V",
            callsign="N9640V",
            lat=42.2739,
            lon=-83.7414,
            altitude_ft=3125,
            ground_speed_kt=101,
            track_deg=38,
            distance_nm=0.01,
        ),
        _at("2026-09-12T18:43:30+00:00"),
    ),
    (
        "qatar-a350-no-artwork",
        Sighting(
            title="Qatar Airways",
            subtitle="Airbus A350-1000",
            seen_at=_at("2026-09-13T01:30:16+00:00"),
            brand="qatar-airways",
            type_code="A35K",
            registration="A7-ANT",
            callsign="QTR1X",
            origin=IAH,
            destination=DOH,
            lat=42.2587,
            lon=-83.7438,
            altitude_ft=35000,
            ground_speed_kt=542,
            track_deg=36,
            distance_nm=0.44,
        ),
        _at("2026-09-13T01:31:00+00:00"),
    ),
    ("united-held-14-min", _UNITED, _UNITED.seen_at + timedelta(minutes=14)),
]
