import gzip
from datetime import UTC, datetime, timedelta

import pytest

from airframe import adsb, aircraft_db, config, scoring
from airframe.adsb import Contact
from airframe.aircraft_db import Aircraft
from airframe.app import FrameApp
from airframe.artwork import ArtworkLibrary
from airframe.enrich import Enricher
from airframe.livery import LiveryResolver, LiveryTables
from airframe.names import Names, from_description
from airframe.operators import Operator
from airframe.paths import ASSETS_DIR, REFERENCE_DIR
from airframe.routes import RouteAirport

LAT, LON = 42.2768, -83.7382
FREQUENCY_ROWS = "type,C172,30\ncombo,delta-connection_CRJ9,57\ncombo,delta_A339,1\n"
T0 = datetime(2026, 9, 15, 18, 30, tzinfo=UTC)

DTW = RouteAirport("DTW", "KDTW", 42.2124, -83.3534, "Detroit")
MBS = RouteAirport("MBS", "KMBS", 43.5329, -84.0796, "Saginaw")
FRA = RouteAirport("FRA", "EDDF", 50.0264, 8.5431, "Frankfurt-am-Main")
PHX = RouteAirport("PHX", "KPHX", 33.4343, -112.0120, "Phoenix")
GJT = RouteAirport("GJT", "KGJT", 39.1224, -108.5270, "Grand Junction")

CRJ9_RECORD = Aircraft(
    "N821SK", "CRJ9", "BOMBARDIER Regional Jet CRJ-900", 2014, "SKYWEST AIRLINES INC"
)


class FakeRoutes:
    def __init__(self, routes=None):
        self.routes = routes or {}
        self.requested = set()

    def prefetch(self, callsigns):
        self.requested |= {c for c in callsigns if c}

    def get(self, callsign):
        return self.routes.get(callsign, [])


class FakeDB:
    def __init__(self, records=None):
        self.records = records or {}

    def lookup(self, hex_code):
        return self.records.get(hex_code)


class FakeDisplay:
    def __init__(self):
        self.shown = []

    def show(self, image):
        self.shown.append(image)


def contact(hex_code, callsign, type_code, *, distance_nm=3.0, altitude_ft=8000, **kw):
    fields = dict(
        hex=hex_code,
        callsign=callsign,
        registration=kw.pop("registration", ""),
        type_code=type_code,
        lat=LAT + 0.02,
        lon=LON + 0.02,
        altitude_ft=altitude_ft,
        on_ground=False,
        ground_speed_kt=300.0,
        track_deg=90.0,
        distance_nm=distance_nm,
        db_flags=0,
        seen_at=T0,
    )
    fields.update(kw)
    return Contact(**fields)


def make_enricher(tmp_path, routes=None, records=None, frequency_rows=""):
    frequency = tmp_path / "traffic_frequency.csv"
    frequency.write_text("kind,key,per_day\n" + frequency_rows)
    tables = LiveryTables.load(REFERENCE_DIR)
    routes = routes if routes is not None else FakeRoutes()
    return Enricher(
        lat=LAT,
        lon=LON,
        home_country="United States",
        scale_nm=15,
        weights=scoring.Weights(),
        aircraft_db=FakeDB(records),
        operators={
            "DAL": Operator("Delta Air Lines", "United States"),
            "SKW": Operator("Sky West Aviation", "United States"),
            "QTR": Operator("Qatar Airways Group", "Qatar"),
        },  # fmt: skip
        names=Names(REFERENCE_DIR),
        livery=LiveryResolver(tables, lat=LAT, lon=LON, routes=routes),
        routes=routes,
        artwork=ArtworkLibrary(ASSETS_DIR / "aircraft", REFERENCE_DIR / "aircraft_families.csv"),
        frequency=scoring.TrafficFrequency(frequency),
    )


def test_parse_skips_ground_stale_and_positionless_aircraft():
    payload = {
        "now": T0.timestamp() * 1000,
        "ac": [
            {"hex": "a33ed6", "flight": "AAL2224 ", "r": "N308UK", "t": "B38M", "alt_baro": 37000,
             "gs": 492.0, "track": 90.7, "lat": 42.117966, "lon": -83.903587, "dst": 12.043,
             "seen_pos": 0.5, "dbFlags": 8},
            {"hex": "a23a04", "flight": "CXK232  ", "t": "C172", "alt_baro": "ground",
             "lat": 42.22, "lon": -83.74, "seen_pos": 1.0},
            {"hex": "abcdef", "flight": "OLD123  ", "t": "B738", "alt_baro": 30000,
             "lat": 42.3, "lon": -83.7, "seen_pos": 300},
            {"hex": "fedcba", "flight": "NOPOS   ", "t": "B738", "alt_baro": 30000},
        ],
    }  # fmt: skip
    contacts = adsb.parse(payload, LAT, LON)
    assert [c.hex for c in contacts] == ["a33ed6", "a23a04"]
    first = contacts[0]
    assert (first.callsign, first.registration, first.type_code) == ("AAL2224", "N308UK", "B38M")
    assert first.distance_nm == pytest.approx(12.043) and first.altitude_ft == 37000
    assert first.seen_at == T0 - timedelta(seconds=0.5)
    assert contacts[1].on_ground


def test_names_and_flight_numbers():
    names = Names(REFERENCE_DIR)
    assert names.aircraft_name("B39M", "").full == "Boeing 737 MAX 9"
    assert names.aircraft_name("C172", "").manufacturer == "Cessna"
    assert names.aircraft_name("ZZZZ", "CESSNA 402 Businessliner") == from_description(
        "CESSNA 402 Businessliner"
    )
    assert from_description("DE HAVILLAND CANADA DHC-8-400 Dash 8").manufacturer == (
        "De Havilland Canada"
    )
    assert names.flight_number("DAL16", "DAL") == "DL16"
    assert names.flight_number("SKW3898", "SKW") == ""  # regional: callsign shown instead
    assert names.flight_number("QTR1X", "QTR") == ""


def test_scoring_parts(tmp_path):
    path = tmp_path / "frequency.csv"
    path.write_text(
        "kind,key,per_day\ncombo,delta_A21N,24\ncombo,qatar-airways_A35K,1\ntype,C172,30\n"
    )
    frequency = scoring.TrafficFrequency(path)
    assert frequency.rarity("delta", "A21N") == pytest.approx(0.0)
    assert 0.3 < frequency.rarity("qatar-airways", "A35K") < 0.9
    assert frequency.rarity("delta", "A359") == 1.0  # never seen here
    assert frequency.rarity("", "") == scoring.UNKNOWN_RARITY

    common = scoring.interestingness(
        0.0, type_code="A21N", military=False, flagged=False, foreign=False
    )
    heavy = scoring.interestingness(
        0.8, type_code="A35K", military=False, flagged=False, foreign=True
    )
    assert heavy > common
    assert scoring.proximity(0, 0, 15) == 1.0
    assert scoring.proximity(3, 37000, 15) < scoring.proximity(3, 3000, 15)
    assert scoring.proximity(40, 0, 15) == 0.0
    assert scoring.score(scoring.Weights(), 1.0, 1.0, "brand_type") == pytest.approx(100.0)


def test_candidates_rank_and_resolve_livery(tmp_path):
    routes = FakeRoutes({"SKW3898": [MBS, DTW, MBS]})
    records = {
        "a52736": Aircraft("N431DX", "A339", "AIRBUS A-330-900", 2022, "DELTA AIR LINES INC"),
        "ab362c": CRJ9_RECORD,
        "ad6d6e": Aircraft("N9640V", "C172", "CESSNA 172 Skyhawk", 1978, "FLYERS LLC"),
    }  # fmt: skip
    enricher = make_enricher(tmp_path, routes, records, FREQUENCY_ROWS)
    contacts = [
        contact("ad6d6e", "N9640V", "C172", distance_nm=1.0, altitude_ft=3000),
        contact("a52736", "DAL16", "A339", distance_nm=4.0, altitude_ft=6775),
        contact("ab362c", "SKW3898", "CRJ9", distance_nm=2.0, altitude_ft=4300),
    ]
    candidates = enricher.candidates(contacts)
    by_hex = {c.hex: c for c in candidates}

    assert candidates[0].hex == "a52736"  # widebody, rare, close: the most interesting
    assert by_hex["a52736"].brand == "delta"  # Delta-owned + DAL callsign
    assert by_hex["ab362c"].brand == "delta-connection"  # SkyWest, route touches a Delta hub
    assert by_hex["ad6d6e"].brand == ""
    assert by_hex["ad6d6e"].artwork_level == "generic_family"  # ANY_GA-HIGHWING
    assert "SKW3898" in routes.requested


def test_sighting_uses_brand_flight_number_and_route_leg(tmp_path):
    routes = FakeRoutes({"SKW3898": [MBS, DTW, MBS], "DAL16": [DTW, FRA]})
    records = {"ab362c": CRJ9_RECORD}
    enricher = make_enricher(tmp_path, routes, records)
    # Heading south towards DTW, so the Saginaw -> Detroit leg is the one being flown.
    candidate = enricher.candidates([contact("ab362c", "SKW3898", "CRJ9", track_deg=182)])[0]
    sighting = enricher.sighting(candidate)
    assert sighting.title == "Delta Connection" and sighting.subtitle == "Bombardier CRJ-900"
    assert (sighting.origin.code, sighting.destination.code) == ("MBS", "DTW")
    assert sighting.destination.city == "Detroit"
    assert sighting.flight == "" and sighting.callsign == "SKW3898"  # regional keeps the callsign

    delta = enricher.candidates([contact("a52736", "DAL16", "A339")])[0]
    assert enricher.sighting(delta).flight == "DL16"


def test_route_ignored_when_it_does_not_pass_near_the_frame(tmp_path):
    # Stale route: this callsign is listed as flying PHX-GJT-PHX, nowhere near Ann Arbor.
    routes = FakeRoutes({"SKW6255": [PHX, GJT, PHX]})
    enricher = make_enricher(tmp_path, routes)
    assert enricher.route(contact("ab362c", "SKW6255", "CRJ7", track_deg=294)) == (None, None)


class Clock:
    def __init__(self, start=T0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, minutes):
        self.now += timedelta(minutes=minutes)
        return self.now


def make_app(tmp_path, ticks, clock, records=None):
    cfg = config.load(config.EXAMPLE_CONFIG)
    enricher = make_enricher(tmp_path, None, records, "type,C172,30\n")
    display = FakeDisplay()
    batches = iter(ticks)
    current = {"batch": []}

    def fetch(radius):
        if radius == cfg.radius_nm:
            current["batch"] = next(batches, [])
        return current["batch"]

    return FrameApp(cfg, fetch=fetch, enricher=enricher, display=display, clock=clock), display


def test_tick_shows_keeps_holds_and_resumes(tmp_path):
    clock = Clock()
    plane = contact("a52736", "DAL16", "A339", distance_nm=4.0)
    other = contact("ad6d6e", "N9640V", "C172", distance_nm=1.0, altitude_ft=3000)
    app, display = make_app(tmp_path, [[plane], [plane], [], [], [other]], clock)

    assert app.tick() == "shown"
    clock.advance(3)
    assert app.tick() == "kept"  # same aircraft: no redraw
    clock.advance(3)
    assert app.tick() == "held"  # nothing in range: redraw once as "last seen"
    clock.advance(3)
    assert app.tick() == "idle"  # still nothing: leave the frame alone
    clock.advance(3)
    assert app.tick() == "shown"
    assert len(display.shown) == 3
    assert app.current.sighting.title == "Cessna"


def test_minimum_display_time_and_repeat_cooldown(tmp_path):
    clock = Clock()
    boring = contact("ad6d6e", "N9640V", "C172", distance_nm=1.0, altitude_ft=3000)
    exciting = contact("a52736", "DAL16", "A339", distance_nm=4.0)
    app, _ = make_app(tmp_path, [[boring], [boring, exciting], [boring, exciting]], clock)

    assert app.tick() == "shown" and app.current.candidate.hex == "ad6d6e"
    clock.advance(1)  # less than min_display_seconds: keep the Cessna
    assert app.tick() == "kept"
    clock.advance(5)
    assert app.tick() == "shown" and app.current.candidate.hex == "a52736"
    assert "ad6d6e" in app._recent  # skipped until the cooldown expires


def test_aircraft_database_build_and_lookup(tmp_path):
    csv_path = tmp_path / "aircraft.csv.gz"
    rows = "a52736;N431DX;A339;00;AIRBUS A-330-900;2022;DELTA AIR LINES INC;\n"
    rows += "ae01c5;01-0041;C17;10;Boeing C-17A Globemaster III;2001;;\n"
    csv_path.write_bytes(gzip.compress(rows.encode()))
    db_path = tmp_path / "aircraft.sqlite"
    aircraft_db.build(csv_path, db_path)

    db = aircraft_db.AircraftDB(db_path)
    assert db.lookup("a52736").registration == "N431DX"
    assert db.lookup("AE01C5").military is True
    assert db.lookup("000000") is None


def test_example_config_loads():
    cfg = config.load(config.EXAMPLE_CONFIG)
    assert (cfg.radius_nm, cfg.fallback_radius_nm) == (15, 20)
    assert cfg.refresh_seconds == 180 and cfg.min_display_seconds == 180
    assert (cfg.weights.interestingness, cfg.weights.proximity, cfg.weights.artwork) == (45, 20, 35)
    assert cfg.tz.key == "America/Detroit"
