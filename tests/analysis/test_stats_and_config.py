from datetime import UTC, date, datetime

import pytest

from airframe.analysis import config, geo, stats
from airframe.analysis.encounters import Encounter


def _enc(hex_, type_code="A320", airline="", country="", day=13, **kw):
    t = datetime(2026, 9, day, 12, tzinfo=UTC)
    fields = dict(
        hex=hex_,
        callsign="",
        registration=f"N{hex_}",
        type_code=type_code,
        type_description="",
        airline_icao=airline,
        airline_name=airline.title(),
        airline_country=country,
        operator="",
        entered_utc=t,
        closest_utc=t,
        closest_nm=5.0,
        altitude_ft=9000,
        year=2010,
        military=False,
        interesting=False,
        airport_ops=(),
    )
    fields.update(kw)
    return Encounter(**fields)


def test_artwork_key_uses_brand_or_any():
    assert stats.artwork_key(_enc("1", airline="SKW", brand="delta-connection")) == (
        "delta-connection_A320"
    )
    assert stats.artwork_key(_enc("1", airline="SKW")) == "ANY_A320"
    assert stats.artwork_key(_enc("1", type_code="")) is None


def test_combos_and_coverage():
    encs = (
        [_enc(str(i), airline="DAL", brand="delta") for i in range(6)]
        + [_enc(str(i), type_code="C172") for i in range(3)]
        + [_enc("x", type_code="")]
    )
    combos = stats.top_combos(encs)
    assert [(c["artwork_key"], c["encounters"]) for c in combos] == [
        ("delta_A320", 6),
        ("ANY_C172", 3),
    ]
    assert combos[-1]["cumulative_share"] == pytest.approx(0.9)

    top1, top10 = stats.coverage(combos, encs, [1, 10])
    assert top1["share_of_all"] == pytest.approx(0.6)
    assert top1["share_of_known_type"] == pytest.approx(6 / 9)
    assert top10["combinations"] == 2 and top10["share_of_all"] == pytest.approx(0.9)
    assert stats.combos_needed(combos, 0.8) == 2


def test_rare_interesting_skips_top_combos_and_explains_reasons():
    encs = (
        [_enc(str(i), airline="DAL", brand="delta") for i in range(50)]
        + [_enc("k1", type_code="K35R", military=True, brand="military")]
        + [_enc("d1", type_code="A359", airline="DLH", brand="lufthansa", brand_country="Germany")]
        + [_enc("p1", type_code="PA28")]
    )
    rows = stats.rare_interesting(
        encs, outside_top=1, rare_type_share=0.05, home_country="United States"
    )
    by_key = {r["artwork_key"]: r["reasons"] for r in rows}
    assert "delta_A320" not in by_key and "ANY_PA28" not in by_key
    assert by_key["military_K35R"] == "military; widebody/heavy; rare type"
    assert by_key["lufthansa_A359"] == "widebody/heavy; foreign airline (Germany); rare type"


def test_brand_confidence_and_unresolved_registrations():
    encs = [
        _enc(
            "a",
            airline="SKW",
            registration="N1",
            brand="delta-connection",
            brand_confidence="registration",
            brand_method="owner",
        ),
        _enc("b", airline="SKW", registration="N2", brand_method="ambiguous"),
        _enc("b", airline="SKW", registration="N2", brand_method="ambiguous", day=14),
        _enc("c", brand_method="no_airline_callsign"),
    ]
    rows = {r["confidence"]: r for r in stats.brand_confidence(encs)}
    assert rows["registration"]["share"] == 0.25
    assert rows["unresolved"]["airline_callsign_share"] == pytest.approx(2 / 3)

    (top,) = stats.unresolved_registrations(encs)
    assert (top["registration"], top["encounters"], top["days_seen"], top["reason"]) == (
        "N2",
        2,
        2,
        "ambiguous",
    )


def test_ring_breakdown_splits_by_closest_distance():
    inner = _enc("a", closest_nm=4.0)
    outer = _enc("b", closest_nm=12.0, airport_ops=("DTW",))
    results = [stats.RadiusResult(10, [inner]), stats.RadiusResult(15, [inner, outer])]
    rings = stats.ring_breakdown(results, ["DTW"], days=1)
    assert [(r["ring"], r["encounters"], r["DTW_ops_share"]) for r in rings] == [
        ("0-10 NM", 1, 0.0),
        ("10-15 NM", 1, 1.0),
    ]


def test_resolve_dates():
    today = date(2026, 9, 15)
    assert config.resolve_dates({"last_n_days": 3}, today) == (
        date(2026, 9, 12),
        date(2026, 9, 13),
        date(2026, 9, 14),
    )
    assert config.resolve_dates({"last_n_days": 2, "end": "2026-09-01"}, today) == (
        date(2026, 8, 31),
        date(2026, 9, 1),
    )
    spec = {"list": ["2026-09-03", date(2026, 9, 1)], "last_n_days": 9}
    assert config.resolve_dates(spec, today) == (date(2026, 9, 1), date(2026, 9, 3))
    with pytest.raises(ValueError):
        config.resolve_dates({"list": ["2026-09-15"]}, today)


def test_example_config_loads_and_covers_airports():
    cfg = config.load(config.EXAMPLE_CONFIG, dates=["2026-09-01"])
    assert cfg.radii_nm == (10, 15, 20) and cfg.primary_radius_nm == 15
    dtw = next(a for a in cfg.airports if a.code == "DTW")
    distance = float(geo.distance_nm(dtw.lat, dtw.lon, cfg.lat, cfg.lon))
    assert distance == pytest.approx(17.5, abs=0.3)
    assert cfg.library.weights == config.DEFAULT_LEVEL_WEIGHTS
    assert "ANY_GA-HIGHWING" in cfg.library.always_include
