from datetime import UTC, datetime
from pathlib import Path

import pytest

from airframe.analysis import artwork, geo, livery
from airframe.analysis.encounters import Encounter
from airframe.analysis.routes import RouteAirport

REFERENCE_DIR = Path(__file__).resolve().parents[2] / "data" / "reference"
LAT0, LON0 = 42.2768, -83.7382

DTW = RouteAirport("DTW", "KDTW", 42.2124, -83.3534)
ORD = RouteAirport("ORD", "KORD", 41.9786, -87.9048)
CLE = RouteAirport("CLE", "KCLE", 41.4117, -81.8498)
XNA = RouteAirport("XNA", "KXNA", 36.2819, -94.3068)
DCA = RouteAirport("DCA", "KDCA", 38.8521, -77.0377)
MVY = RouteAirport("MVY", "KMVY", 41.3931, -70.6143)


def _tables():
    brand_rows = [
        ("delta", ()),
        ("delta-connection", ("DTW", "MSP")),
        ("united-express", ("ORD", "DEN")),
        ("american-eagle", ("DCA", "CLT")),
        ("military", ()),
    ]
    brands = {b: livery.Brand(b, b.title(), "United States", frozenset(h)) for b, h in brand_rows}
    operators = {
        "DAL": (livery.OperatorBrand("delta", ("DELTA AIR LINES",)),),
        "EDV": (livery.OperatorBrand("delta-connection", ("DELTA AIR LINES",)),),
        "SKW": (
            livery.OperatorBrand("delta-connection", ("DELTA AIR LINES",)),
            livery.OperatorBrand("united-express", ("UNITED AIRLINES",)),
            livery.OperatorBrand("american-eagle", ("AMERICAN AIRLINES",)),
        ),
        "KFS": (livery.OperatorBrand("", ()),),
    }
    return livery.LiveryTables(brands, operators, {"N999SK": "united-express"})


def _enc(callsign, registration="N100SK", owner="SKYWEST AIRLINES INC", military=False):
    t = datetime(2026, 9, 13, 12, tzinfo=UTC)
    prefix = callsign[:3] if callsign[:3].isalpha() and callsign[3:4].isdigit() else ""
    return Encounter(
        hex="a00001",
        callsign=callsign,
        registration=registration,
        type_code="CRJ9",
        type_description="",
        airline_icao=prefix,
        airline_name="",
        airline_country="United States",
        operator=owner,
        entered_utc=t,
        closest_utc=t,
        closest_nm=5.0,
        altitude_ft=9000,
        year=2010,
        military=military,
        interesting=False,
        airport_ops=(),
    )


class FakeRoutes:
    def __init__(self, routes):
        self.routes = routes
        self.requested = set()

    def prefetch(self, callsigns):
        self.requested |= set(callsigns)

    def get(self, callsign):
        return self.routes.get(callsign, [])


def _resolver(routes=None, learn=()):
    resolver = livery.LiveryResolver(_tables(), lat=LAT0, lon=LON0, routes=routes)
    resolver.learn(list(learn))
    return resolver


def _summary(r):
    return (r.brand, r.confidence, r.method)


def test_airframe_evidence_gives_registration_confidence():
    resolver = _resolver()
    assert _summary(resolver.resolve(_enc("SKW3456", owner="DELTA AIR LINES INC"))) == (
        "delta-connection",
        "registration",
        "owner",
    )
    assert _summary(resolver.resolve(_enc("SKW3456", registration="N999SK"))) == (
        "united-express",
        "registration",
        "registration_csv",
    )
    assert _summary(resolver.resolve(_enc("N123AB", owner="", military=True))) == (
        "military",
        "registration",
        "military_flag",
    )


def test_flight_level_inference_and_unresolved_cases():
    resolver = _resolver()
    assert _summary(resolver.resolve(_enc("EDV5041", owner="BANK OF UTAH TRUSTEE"))) == (
        "delta-connection",
        "inferred",
        "sole_operator",
    )
    assert _summary(resolver.resolve(_enc("KFS123"))) == ("", "unresolved", "mixed_liveries")
    assert _summary(resolver.resolve(_enc("XYZ1234"))) == ("", "unresolved", "operator_unmapped")
    assert _summary(resolver.resolve(_enc("N123AB"))) == ("", "unresolved", "no_airline_callsign")
    assert _summary(resolver.resolve(_enc("SKW3456"))) == ("", "unresolved", "ambiguous")


def test_flight_blocks_are_learned_from_owner_confirmed_aircraft():
    delta = [
        _enc(f"SKW3{i:03d}", registration=f"N{i}DL", owner="DELTA AIR LINES INC") for i in range(10)
    ]
    mixed = [_enc("SKW4001", registration="N1UA", owner="UNITED AIRLINES INC")] * 10 + [
        _enc("SKW4002", registration="N2DL", owner="DELTA AIR LINES INC")
    ]
    resolver = _resolver(learn=delta + mixed)

    assert _summary(resolver.resolve(_enc("SKW3999"))) == (
        "delta-connection",
        "inferred",
        "flight_block",
    )
    assert _summary(resolver.resolve(_enc("SKW4999"))) == ("", "unresolved", "ambiguous")
    blocks = {b["block"]: b for b in resolver.flight_blocks}
    assert blocks["3xxx"]["used"] and not blocks["4xxx"]["used"]
    assert blocks["4xxx"]["purity"] == pytest.approx(10 / 11)


def test_route_hub_needs_one_candidate_hub_and_a_plausible_path():
    routes = FakeRoutes(
        {"SKW5001": [DTW, XNA], "SKW5002": [DTW, ORD], "SKW5003": [DCA, MVY], "SKW6001": [ORD, CLE]}
    )
    encs = [_enc(c, registration=f"N{c}") for c in routes.routes]
    resolver = _resolver(routes, learn=encs)

    assert routes.requested == set(routes.routes)
    assert _summary(resolver.resolve(encs[0])) == ("delta-connection", "inferred", "route_hub")
    assert _summary(resolver.resolve(encs[1])) == ("", "unresolved", "ambiguous")  # two hubs
    assert _summary(resolver.resolve(encs[2])) == ("", "unresolved", "ambiguous")  # far away
    assert _summary(resolver.resolve(encs[3])) == ("united-express", "inferred", "route_hub")


def test_registration_consensus_and_conflicts():
    routes = FakeRoutes({"SKW5001": [DTW, XNA], "SKW6001": [ORD, CLE]})
    consistent = [_enc("SKW5001", registration="N500SK"), _enc("SKW7777", registration="N500SK")]
    conflicting = [_enc("SKW5001", registration="N600SK"), _enc("SKW6001", registration="N600SK")]
    resolver = _resolver(routes, learn=consistent + conflicting)

    assert _summary(resolver.resolve(consistent[1])) == (
        "delta-connection",
        "inferred",
        "registration_consensus",
    )
    for e in conflicting:
        assert _summary(resolver.resolve(e)) == ("", "unresolved", "conflict")


def test_flight_block():
    assert livery.flight_block("SKW3456") == "3xxx"
    assert livery.flight_block("DAL363") == ""
    assert livery.flight_block("N12345") == ""


def test_segment_distance():
    assert geo.segment_distance_nm(LAT0, LON0, DTW.lat, DTW.lon, XNA.lat, XNA.lon) < 20
    assert geo.segment_distance_nm(LAT0, LON0, DCA.lat, DCA.lon, MVY.lat, MVY.lon) > 300
    # Beyond the ORD end of an ORD-XNA segment: nearest point is ORD itself (~186 NM).
    ord_distance = geo.segment_distance_nm(LAT0, LON0, ORD.lat, ORD.lon, XNA.lat, XNA.lon)
    assert ord_distance == pytest.approx(186, abs=6)


def test_repository_reference_tables_load():
    tables = livery.LiveryTables.load(REFERENCE_DIR)
    assert {r.brand for r in tables.operators["SKW"]} >= {"delta-connection", "united-express"}
    assert [r.brand for r in tables.operators["EDV"]] == ["delta-connection"]
    families = artwork.Families.load(REFERENCE_DIR / "aircraft_families.csv")
    assert families.family("CRJ9") == families.family("CRJ7") == "CRJ-FAM"
    assert families.family("B738") == "737NG" and families.family("B38M") == "737MAX"
    assert families.family("E75L") == "EJET-E1" and families.family("E295") == "EJET-E2"
    assert families.family("BE35") == ""
