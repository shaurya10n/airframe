from dataclasses import replace
from datetime import UTC, datetime

import numpy as np
import pytest

from airframe import config
from airframe.aircraft_db import Aircraft
from airframe.analysis.heatmap import CALLSIGN_DTYPE, POSITION_DTYPE
from airframe.analysis.replay import HistoricalTraffic

LAT, LON = 42.2768, -83.7382
T0 = int(datetime(2026, 9, 9, 13, 0, tzinfo=UTC).timestamp())


class FakeDB:
    def lookup(self, hex_code):
        return Aircraft("N431DX", "A339", "AIRBUS A-330-900") if hex_code == "a52736" else None


def _position(addr, ts, lat, lon, alt=8000.0, gs=300.0, ground=False):
    return (addr, ts, lat, lon, alt, ground, gs)


def _traffic(tmp_path, positions, callsigns=()):
    cfg = replace(config.load(config.EXAMPLE_CONFIG), cache_dir=tmp_path)
    extracts = tmp_path / "heatmap_extracts" / f"{cfg.lat:.4f}_{cfg.lon:.4f}_25nm"
    extracts.mkdir(parents=True)
    np.savez(
        extracts / "2026-09-09.npz",
        positions=np.array(positions, dtype=POSITION_DTYPE),
        callsigns=np.array(list(callsigns), dtype=CALLSIGN_DTYPE),
    )
    return HistoricalTraffic(cfg, FakeDB()), cfg


def test_contacts_at_uses_recent_nearby_airborne_positions(tmp_path):
    delta = 0xA52736
    far = 0xAD6D6E
    positions = [
        _position(delta, T0 - 40, LAT + 0.05, LON),  # 40 s before "now": in the window
        _position(delta, T0 - 10, LAT + 0.10, LON),  # latest fix, flying north
        _position(delta, T0 - 600, LAT, LON),  # too old
        _position(far, T0 - 20, LAT + 1.5, LON),  # ~90 NM away
        _position(0xABCDEF, T0 - 20, LAT, LON, ground=True),  # on the ground
    ]
    callsigns = [(delta, T0 - 30, b"DAL16   ")]
    traffic, _ = _traffic(tmp_path, positions, callsigns)

    contacts = traffic.contacts_at(datetime.fromtimestamp(T0, UTC), radius_nm=15)
    assert [c.hex for c in contacts] == ["a52736"]
    contact = contacts[0]
    assert contact.callsign == "DAL16"
    assert (contact.registration, contact.type_code) == ("N431DX", "A339")
    assert contact.track_deg == pytest.approx(0, abs=1)  # flying due north
    assert contact.distance_nm == pytest.approx(6.0, abs=0.2)
    assert contact.seen_at == datetime.fromtimestamp(T0 - 10, UTC)
    assert contact.altitude_ft == 8000 and not contact.on_ground


def test_contacts_at_returns_nothing_outside_the_data(tmp_path):
    traffic, _ = _traffic(tmp_path, [_position(0xA52736, T0, LAT, LON)])
    assert traffic.contacts_at(datetime.fromtimestamp(T0 + 3600, UTC), 15) == []


def test_unknown_aircraft_still_becomes_a_contact(tmp_path):
    addr = 0xAAAAAA
    traffic, _ = _traffic(tmp_path, [_position(addr, T0 - 5, LAT, LON, alt=np.nan, gs=np.nan)])
    (contact,) = traffic.contacts_at(datetime.fromtimestamp(T0, UTC), 15)
    assert contact.registration == "" and contact.type_code == ""
    assert contact.altitude_ft is None and contact.ground_speed_kt is None
    assert contact.track_deg is None  # a single position has no direction
