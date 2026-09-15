import math

import numpy as np
import pytest

from airframe.analysis import encounters, geo, heatmap, reference
from airframe.analysis.config import Airport
from airframe.operators import Operator, airline_code

LAT0, LON0 = 42.2768, -83.7382
T0 = 1_789_257_600
DTW = Airport("DTW", 42.2124, -83.3534, 645)


def _to_latlon(x_nm, y_nm):
    lat = LAT0 + y_nm / geo.NM_PER_DEG_LAT
    lon = LON0 + x_nm / (geo.NM_PER_DEG_LAT * math.cos(math.radians(LAT0)))
    return lat, lon


def _track(addr, start, offset_nm=5.0, step_s=60, alt_ft=8000.0):
    """Eastbound at 250 kt passing `offset_nm` north of the center, sampled every `step_s`."""
    rows = []
    for i in range(16):
        x = -31.1 + i * 250 * step_s / 3600
        lat, lon = _to_latlon(x, offset_nm)
        rows.append((addr, start + i * step_s, lat, lon, alt_ft + i * 100, False, 250.0))
    return rows


def _positions(rows):
    return np.array(rows, dtype=heatmap.POSITION_DTYPE)


def _passes(rows, radius, gap_s=1800):
    points = encounters.closest_points(_positions(rows), LAT0, LON0, max_segment_gap_s=60)
    return encounters.find_passes(points, radius, gap_s)


def test_closest_approach_is_interpolated_between_samples():
    (p,) = _passes(_track(0xA7E24A, T0), radius=15)
    assert p.closest_nm == pytest.approx(5.0, abs=0.01)
    assert 8000 < p.altitude_ft < 9500
    assert p.entered < p.closest_time < p.exited


def test_radius_smaller_than_closest_approach_has_no_encounter():
    assert _passes(_track(0xA7E24A, T0), radius=4.9) == []


def test_repeat_passes_are_merged_only_within_gap():
    addr = 0xA7E24A
    assert len(_passes(_track(addr, T0) + _track(addr, T0 + 20 * 60), radius=15)) == 1
    assert len(_passes(_track(addr, T0) + _track(addr, T0 + 3 * 3600), radius=15)) == 2
    assert len(_passes(_track(addr, T0) + _track(0xACDBF4, T0), radius=15)) == 2


def test_enrich_adds_callsign_airline_aircraft_and_airport_ops():
    addr = 0xA7E24A
    rows = _track(addr, T0)
    rows.append((addr, T0 + 1500, DTW.lat, DTW.lon + 0.01, np.nan, True, 12.0))  # on ground at DTW
    positions = _positions(rows)
    callsigns = np.array([(addr, T0 + 120, b"EDV5041 ")], dtype=heatmap.CALLSIGN_DTYPE)

    points = encounters.closest_points(positions[~positions["ground"]], LAT0, LON0, 60)
    passes = encounters.find_passes(points, 15, 1800)
    (enc,) = encounters.enrich(
        passes,
        encounters.CallsignIndex(callsigns),
        {
            "a7e24a": reference.Aircraft(
                "N607LR", "CRJ9", "BOMBARDIER CRJ-900", 2008, "DELTA AIR LINES INC"
            )
        },
        {"EDV": Operator("Endeavor Air", "United States")},
        encounters.AirportOps(positions, (DTW,), radius_nm=4, max_agl_ft=2500),
        airport_window_s=1200,
    )
    assert (enc.hex, enc.callsign, enc.registration, enc.type_code) == (
        "a7e24a",
        "EDV5041",
        "N607LR",
        "CRJ9",
    )
    assert (enc.airline_icao, enc.airline_name) == ("EDV", "Endeavor Air")
    assert enc.airport_ops == ("DTW",)
    assert enc.closest_utc.tzinfo is not None


def test_callsign_lookup_respects_max_gap():
    index = encounters.CallsignIndex(np.array([(1, T0, b"N12345  ")], dtype=heatmap.CALLSIGN_DTYPE))
    assert index.nearest(1, T0 + 60) == "N12345"
    assert index.nearest(1, T0 + 7200) == ""
    assert index.nearest(2, T0) == ""


def test_airline_code_requires_known_designator_and_flight_number():
    ops = {"DAL": Operator("Delta Air Lines", "United States")}
    assert airline_code("DAL1234", ops) == "DAL"
    assert airline_code("N393FR", ops) == ""
    assert airline_code("DALTON", ops) == ""
    assert airline_code("XXX123", ops) == ""
