import numpy as np
import pytest

from airframe.analysis import geo


def test_closest_on_segment():
    frac, dist = geo.closest_on_segment(
        np.array([-5.0, 3.0, 2.0]),
        np.array([1.0, 4.0, 2.0]),
        np.array([5.0, 6.0, 2.0]),
        np.array([1.0, 4.0, 2.0]),
    )
    assert frac.tolist() == [0.5, 0.0, 0.0]  # crossing, pointing away, zero-length
    assert dist == pytest.approx([1.0, 5.0, np.hypot(2, 2)])


def test_distance_matches_known_airport_offsets():
    # Ann Arbor Municipal is ~3.2 NM south of central campus, Willow Run ~9.5 NM east.
    assert geo.distance_nm(42.2231, -83.7456, 42.2768, -83.7382) == pytest.approx(3.2, abs=0.1)
    assert geo.distance_nm(42.2375, -83.5306, 42.2768, -83.7382) == pytest.approx(9.5, abs=0.2)
