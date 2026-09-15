import gzip
import struct

import numpy as np

from airframe.analysis import heatmap

LAT0, LON0 = 42.2768, -83.7382
T0_MS = 1_789_257_600_000  # 2026-09-13 00:00:00 UTC


def _record(hex_, lat, lon, alt=0, gs=0):
    return struct.pack("<IIIhh", hex_ & 0xFFFFFFFF, lat & 0xFFFFFFFF, lon & 0xFFFFFFFF, alt, gs)


def _marker(ts_ms):
    return _record(heatmap.SLICE_MARKER, ts_ms >> 32, ts_ms & 0xFFFFFFFF, alt=10)


def _callsign(addr, callsign, squawk=1200):
    return struct.pack("<II8s", addr, heatmap.CALLSIGN_FLAG | squawk, callsign)


def _deg(value):
    return round(value * 1e6)


def _sample_file():
    near, far, ground, non_icao = 0xA7E24A, 0x3C6444, 0xA13441, heatmap.NON_ICAO_FLAG | 0x123456
    return gzip.compress(
        b"".join(
            [
                _record(2, 0, 0),  # index section
                _record(9, 0, 0),
                _marker(T0_MS),
                _record(near, _deg(LAT0 + 0.1), _deg(LON0), alt=400, gs=2500),
                _record(far, _deg(50.0), _deg(8.5), alt=1400, gs=4500),
                _record(ground, _deg(LAT0 - 0.05), _deg(LON0), alt=heatmap.ALT_GROUND, gs=-1),
                _callsign(near, b"EDV5041 "),
                _callsign(far, b"DLH431  "),
                _marker(T0_MS + 10_000),
                _record(
                    near | (5 << 27),
                    _deg(LAT0 + 0.09),
                    _deg(LON0),
                    alt=heatmap.ALT_UNKNOWN,
                    gs=2480,
                ),
                _record(non_icao, _deg(LAT0), _deg(LON0 + 0.1), alt=40, gs=900),
            ]
        )
    )


def test_decode_keeps_only_positions_in_radius():
    positions, callsigns = heatmap.decode(_sample_file(), LAT0, LON0, radius_nm=20)

    assert [heatmap.addr_to_hex(int(a)) for a in positions["addr"]] == [
        "a7e24a",
        "a13441",
        "a7e24a",
        "~123456",
    ]
    assert positions["ts"].tolist() == [
        T0_MS // 1000,
        T0_MS // 1000,
        T0_MS // 1000 + 10,
        T0_MS // 1000 + 10,
    ]
    assert positions["lat"][0] == np.float64(round(LAT0 + 0.1, 6))
    assert positions["alt_ft"][0] == 10_000
    assert positions["gs_kt"][0] == np.float32(250.0)
    assert positions["ground"].tolist() == [False, True, False, False]
    assert np.isnan(positions["alt_ft"][1]) and np.isnan(positions["gs_kt"][1])
    assert np.isnan(positions["alt_ft"][2])

    assert callsigns["callsign"].tolist() == [b"EDV5041 "]
    assert callsigns["addr"].tolist() == [0xA7E24A]


def test_decode_accepts_uncompressed_data():
    raw = gzip.decompress(_sample_file())
    positions, _ = heatmap.decode(raw, LAT0, LON0, radius_nm=5)
    assert heatmap.addr_to_hex(int(positions["addr"][0])) == "a13441"
