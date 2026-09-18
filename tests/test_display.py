import dataclasses
import sys
import types

import pytest
from PIL import Image

from airframe import config
from airframe.__main__ import build_display
from airframe.config import EXAMPLE_CONFIG
from airframe.display import inky as inky_module
from airframe.display.inky import PANEL_RESOLUTION, InkyDisplay, open_panel
from airframe.display.png import PngDisplay
from airframe.render import theme


class FakePanel:
    """Stands in for inky's driver: the attributes and calls InkyDisplay relies on."""

    def __init__(self, resolution=PANEL_RESOLUTION):
        self.width, self.height = resolution
        self.images = []
        self.shown = 0

    def set_image(self, image, saturation=0.5):
        if image.size != (self.width, self.height):
            raise ValueError(f"Image must be ({self.width}x{self.height}) pixels!")
        self.images.append((image, saturation))

    def show(self, busy_wait=True):
        self.shown += 1


def fake_inky(monkeypatch, *, detected=None, error=None):
    """Install a stand-in ``inky`` package, so open_panel can be tested off the Pi."""
    package = types.ModuleType("inky")
    auto = types.ModuleType("inky.auto")
    driver = types.ModuleType("inky.inky_el133uf1")
    built = []

    def _auto():
        if error is not None:
            raise error
        return detected

    def _direct(resolution=None):
        built.append(resolution)
        return FakePanel(resolution or PANEL_RESOLUTION)

    auto.auto = _auto
    driver.Inky = _direct
    for name, module in [("inky", package), ("inky.auto", auto), ("inky.inky_el133uf1", driver)]:
        monkeypatch.setitem(sys.modules, name, module)
    return built


def poster(corner=(255, 0, 0)):
    """A portrait frame with its top-left corner marked, so the rotation is visible."""
    image = Image.new("RGB", (theme.WIDTH, theme.HEIGHT), (233, 231, 225))
    image.putpixel((0, 0), corner)
    return image


def test_portrait_frame_is_rotated_onto_the_landscape_panel():
    panel = FakePanel()
    InkyDisplay(panel).show(poster())

    image, saturation = panel.images[0]
    assert image.size == PANEL_RESOLUTION
    assert saturation == 0.5
    assert panel.shown == 1
    # 90 degrees counter-clockwise: the poster's top-left corner lands bottom-left.
    assert image.getpixel((0, image.height - 1)) == (255, 0, 0)


def test_rotation_270_hangs_the_frame_the_other_way_up():
    panel = FakePanel()
    InkyDisplay(panel, rotation=270).show(poster())

    image, _ = panel.images[0]
    assert image.size == PANEL_RESOLUTION
    assert image.getpixel((image.width - 1, 0)) == (255, 0, 0)


def test_rotation_must_land_the_frame_on_the_panel():
    with pytest.raises(ValueError, match="rotation must be one of"):
        InkyDisplay(FakePanel(), rotation=180)


def test_a_wrong_sized_frame_is_caught_before_it_reaches_the_panel():
    panel = FakePanel()
    with pytest.raises(ValueError, match="the panel wants"):
        InkyDisplay(panel).show(Image.new("RGB", (800, 600)))
    assert not panel.images


def test_open_panel_uses_the_detected_display(monkeypatch):
    built = fake_inky(monkeypatch, detected=FakePanel())
    assert open_panel().width == PANEL_RESOLUTION[0]
    assert built == []  # detection succeeded, so nothing was constructed by hand


def test_open_panel_falls_back_when_detection_fails(monkeypatch, caplog):
    built = fake_inky(monkeypatch, error=RuntimeError("No EEPROM detected!"))
    panel = open_panel()
    assert (panel.width, panel.height) == PANEL_RESOLUTION
    assert built == [PANEL_RESOLUTION]
    assert "auto-detection failed" in caplog.text


def test_open_panel_refuses_a_different_inky(monkeypatch):
    fake_inky(monkeypatch, detected=FakePanel((800, 480)))
    with pytest.raises(RuntimeError, match="Impression 13.3"):
        open_panel()


def test_the_config_chooses_the_backend(monkeypatch):
    cfg = config.load(EXAMPLE_CONFIG)
    assert cfg.display == "png"
    assert cfg.rotation == 90
    assert isinstance(build_display(cfg), PngDisplay)

    panel = FakePanel()
    monkeypatch.setattr(inky_module, "open_panel", lambda: panel)
    display = build_display(dataclasses.replace(cfg, display="inky", rotation=270))
    assert isinstance(display, InkyDisplay)
    assert display.rotation == 270

    display.show(poster())
    assert panel.shown == 1


def test_the_config_rejects_a_rotation_that_would_not_fit(tmp_path):
    path = tmp_path / "airframe.toml"
    path.write_text(
        '[location]\nlat = 42.2768\nlon = -83.7382\n[display]\nbackend = "inky"\nrotation = 45\n'
    )
    with pytest.raises(ValueError, match="display.rotation must be one of"):
        config.load(path)


def test_a_missing_inky_package_says_what_to_install(monkeypatch):
    monkeypatch.setitem(sys.modules, "inky", None)  # import raises ImportError
    with pytest.raises(RuntimeError, match=r'pip install -e "\.\[pi\]"'):
        open_panel()
