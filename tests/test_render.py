from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from PIL import Image

from airframe import samples
from airframe.artwork import ArtworkLibrary, candidate_keys
from airframe.display import spectra6
from airframe.models import Sighting
from airframe.paths import ASSETS_DIR, REFERENCE_DIR
from airframe.render import format, poster, route_map, text, theme

TZ = ZoneInfo("America/Detroit")


def test_formatting():
    assert format.altitude(34125) == "34,125 ft"
    assert format.altitude(None) == format.MISSING
    assert format.speed(450) == "518 mph"
    assert format.speed(450, "aviation") == "450 kt"
    assert format.distance(7.3) == "8.4 mi"
    assert format.heading(45) == "045° NE"
    assert format.heading(74) == "074° E"
    assert format.heading(359.6) == "000° N"
    assert format.coordinates(41.9742, -87.9073) == "41.9742° N   87.9073° W"


def test_footer_status_switches_to_last_seen():
    seen = datetime(2026, 9, 10, 18, 33, tzinfo=UTC)
    assert format.seen(seen, seen + timedelta(seconds=40), "Ann Arbor", TZ) == (
        "Over Ann Arbor · 2:33 PM"
    )
    assert (
        format.seen(seen, seen + timedelta(minutes=14), "Ann Arbor", TZ) == "Last seen at 2:33 PM"
    )
    assert format.seen(seen, seen + timedelta(hours=2), "Ann Arbor", TZ) == "Last seen at 2:33 PM"


def test_artwork_fallback_order(tmp_path):
    for key in ("united_B39M", "ANY_737MAX", "ANY_A320-FAM"):
        (tmp_path / f"{key}.png").write_bytes(b"")
    families = tmp_path / "families.csv"
    families.write_text("# comment\ntype,family\nB39M,737MAX\nB38M,737MAX\nA321,A320-FAM\n")
    library = ArtworkLibrary(tmp_path, families)

    assert candidate_keys("united", "B39M", "737MAX") == [
        "united_B39M", "united_737MAX", "ANY_B39M", "ANY_737MAX",
    ]  # fmt: skip
    assert library.resolve("united", "B39M").stem == "united_B39M"
    assert library.resolve("united", "B38M").stem == "ANY_737MAX"
    assert library.resolve("", "A321").stem == "ANY_A320-FAM"
    assert library.resolve("delta", "CRJ9") is None


def test_great_circle_and_world_projection():
    tokyo, san_francisco = (35.55, 139.78), (37.62, -122.38)
    route = route_map.great_circle(tokyo, san_francisco)
    assert route[0] == pytest.approx(tokyo) and route[-1][0] == pytest.approx(san_francisco[0])
    assert max(lat for lat, _ in route) > 45  # arcs north over the Pacific

    projection = route_map.WorldProjection(640, 325)
    assert projection.x(route_map.CENTER_LON) == pytest.approx(320)
    assert projection.x(route_map.CENTER_LON + 360) == pytest.approx(320)  # wraps
    assert projection.y(route_map.NORTH_LAT) == pytest.approx(0)
    assert projection.y(route_map.SOUTH_LAT) == pytest.approx(325)
    assert 0 < projection.y(42.27) < 325 / 2  # Ann Arbor sits in the upper half
    assert route_map.natural_aspect() == pytest.approx(640 / 325, rel=0.01)


def test_route_map_always_draws_the_world():
    for origin, destination, position, track in (
        (None, None, None, None),
        (None, None, (42.27, -83.74), 90),
        (samples.MBS, samples.DTW, (42.27, -83.74), 182),  # short route: one combined label
        (samples.DFW, samples.FRA, (42.27, -83.76), 60),
    ):
        image = route_map.render((320, 163), origin, destination, position, track)
        assert image.size == (320, 163) and image.mode == "RGBA" and image.getbbox()


def test_text_fit_shrinks_then_gives_up():
    font = text.fit(theme.serif, "Dallas–Fort Worth  →  Frankfurt", 610, 46, 30)
    assert font is not None and font.size <= 46
    assert text.fit(theme.serif, "x" * 200, 610, 46, 30) is None


def test_spectra6_simulation_uses_only_panel_colors():
    gradient = Image.linear_gradient("L").convert("RGB").resize((64, 64))
    colors = {c for _, c in spectra6.simulate(gradient).getcolors(maxcolors=256)}
    assert colors <= set(spectra6.MEASURED)


@pytest.mark.parametrize(
    "name, sighting, now", samples.SAMPLES, ids=[s[0] for s in samples.SAMPLES]
)
def test_samples_render(name, sighting, now):
    library = ArtworkLibrary(ASSETS_DIR / "aircraft", REFERENCE_DIR / "aircraft_families.csv")
    image = poster.render(
        sighting,
        library.resolve(sighting.brand, sighting.type_code),
        now=now,
        place="Ann Arbor",
        tz=TZ,
    )
    assert image.size == (theme.WIDTH, theme.HEIGHT)


def test_minimal_sighting_renders():
    sighting = Sighting(title="", subtitle="", seen_at=datetime(2026, 9, 10, tzinfo=UTC))
    image = poster.render(sighting, None, now=sighting.seen_at, place="Ann Arbor", tz=TZ)
    assert image.size == (theme.WIDTH, theme.HEIGHT)
