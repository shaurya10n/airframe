from datetime import UTC, datetime

import pytest

from airframe.analysis import artwork
from airframe.analysis.config import ARTWORK_LEVELS, LibraryConfig
from airframe.analysis.encounters import Encounter


def _enc(hex_, type_code, brand="", family="", day=13, **kw):
    t = datetime(2026, 9, day, 12, tzinfo=UTC)
    fields = dict(
        hex=hex_,
        callsign="",
        registration="",
        type_code=type_code,
        type_description="",
        airline_icao="",
        airline_name="",
        airline_country="",
        operator="",
        entered_utc=t,
        closest_utc=t,
        closest_nm=5.0,
        altitude_ft=9000,
        year=2010,
        military=False,
        interesting=False,
        airport_ops=(),
        brand=brand,
        family=family,
    )
    fields.update(kw)
    return Encounter(**fields)


def test_candidate_keys_follow_the_fallback_hierarchy():
    e = _enc("1", "CRJ9", brand="delta-connection", family="CRJ-FAM")
    assert artwork.candidate_keys(e) == [
        ("delta-connection_CRJ9", "brand_type"),
        ("delta-connection_CRJ-FAM", "brand_family"),
        ("ANY_CRJ9", "generic_type"),
        ("ANY_CRJ-FAM", "generic_family"),
    ]
    library = {"ANY_CRJ-FAM", "delta-connection_CRJ-FAM"}
    assert artwork.best_match(e, library) == ("delta-connection_CRJ-FAM", "brand_family")
    assert artwork.candidate_keys(_enc("2", "CRJ7", family="CRJ-FAM"))[0] == (
        "ANY_CRJ7",
        "generic_type",
    )
    assert artwork.best_match(_enc("3", ""), library) == ("", "")


def test_level_coverage_shares_sum_to_one():
    encs = [
        _enc(
            "1", "CRJ9", brand="delta-connection", family="CRJ-FAM", brand_confidence="registration"
        ),
        _enc("2", "CRJ7", brand="delta-connection", family="CRJ-FAM", brand_confidence="inferred"),
        _enc("3", "CRJ2", family="CRJ-FAM"),
        _enc("4", "C172"),
    ]
    row = artwork.level_coverage(encs, {"delta-connection_CRJ9", "ANY_CRJ-FAM"})
    assert row["brand_type"] == 0.25 and row["generic_family"] == 0.5 and row["none"] == 0.25
    assert sum(row[level] for level in (*ARTWORK_LEVELS, "none")) == pytest.approx(1)
    assert row["brand_level_registration"] == 0.25 and row["brand_level_inferred"] == 0


def _library_traffic():
    return (
        [_enc(f"a{i}", "CRJ9", "delta-connection", "CRJ-FAM", day=8 + i % 7) for i in range(40)]
        + [_enc(f"b{i}", "CRJ7", "delta-connection", "CRJ-FAM", day=8 + i % 7) for i in range(20)]
        + [_enc(f"c{i}", "C172", family="GA-HIGHWING", day=8 + i % 7) for i in range(30)]
        + [
            _enc(f"q{i}", "A35K", "qatar-airways", "A350-FAM", day=8 + i, brand_country="Qatar")
            for i in range(3)
        ]
        + [_enc("m1", "C17", "military", "MIL-TRANSPORT", military=True)]
    )


def test_build_library_ranks_by_weighted_marginal_coverage_then_adds_extras():
    cfg = LibraryConfig(
        brand_min=0,
        brand_max=10,
        generic_max=10,
        min_marginal_share=0.05,
        always_include=("military_MIL-TRANSPORT", "ANY_NOT-OBSERVED"),
        hero_min_days=3,
        hero_max=5,
    )
    items = artwork.build_library(_library_traffic(), cfg, home_country="United States")

    assert [(i.artwork_key, i.source) for i in items] == [
        ("delta-connection_CRJ-FAM", "coverage"),  # 60 x 0.8
        ("ANY_C172", "coverage"),  # 30 x 0.5
        ("delta-connection_CRJ9", "coverage"),  # upgrades 40 by 0.2
        ("military_MIL-TRANSPORT", "required"),
        ("qatar-airways_A35K", "hero"),
    ]
    assert {i.artwork_key: i.encounters_covered for i in items} == {
        "delta-connection_CRJ-FAM": 20,
        "ANY_C172": 30,
        "delta-connection_CRJ9": 40,
        "military_MIL-TRANSPORT": 1,
        "qatar-airways_A35K": 3,
    }
    assert items[2].newly_matched == 0 and items[2].upgraded == 40
    assert items[-1].cumulative_match_share == 1.0
    assert "foreign (Qatar)" in items[-1].reason and "widebody" in items[-1].reason


def test_brand_minimum_and_redundant_images_are_dropped():
    # Forcing brand picks makes delta-connection_CRJ-FAM redundant once CRJ9 and CRJ7 exist,
    # so it is dropped and the selection rerun without it.
    cfg = LibraryConfig(brand_min=5, brand_max=10, generic_max=10, min_marginal_share=0.05)
    items = artwork.build_library(_library_traffic(), cfg, "United States", extras=False)
    assert [i.artwork_key for i in items] == [
        "delta-connection_CRJ9",
        "delta-connection_CRJ7",
        "ANY_C172",
        "qatar-airways_A35K",
        "military_C17",
    ]
    assert all(i.encounters_covered > 0 for i in items)


def test_heroes_need_a_resolved_foreign_brand_and_skip_aircraft_already_in_livery():
    encs = (
        [_enc(f"d{i}", "A333", "delta", "A330-FAM", day=8 + i) for i in range(3)]
        + [_enc(f"c{i}", "CL60", day=8 + i, airline_country="Canada") for i in range(3)]
        + [
            _enc(f"s{i}", "B77W", "swiss", "777-FAM", day=8 + i, brand_country="Switzerland")
            for i in range(3)
        ]
        + [_enc(f"f{i}", "B763", "fedex", "767-FAM", day=8 + i) for i in range(4)]
        + [_enc("q1", "A35K", "qatar-airways", day=8, brand_country="Qatar")]
    )
    picks = artwork.heroes(encs, {"delta_A330-FAM"}, "United States", min_days=3, limit=5)
    assert picks == [
        ("swiss_B77W", "hero: widebody/heavy; foreign (Switzerland); seen on 3 days"),
        ("fedex_B763", "hero: widebody/heavy; seen on 4 days"),
    ]


def test_split_half_needs_at_least_four_days():
    cfg = LibraryConfig()
    assert artwork.split_half_stability([_enc("1", "C172")], cfg, "United States") is None
    result = artwork.split_half_stability(_library_traffic(), cfg, "United States")
    assert result["images_a"] > 0 and 0 <= result["a_on_b_weighted"] <= 1
