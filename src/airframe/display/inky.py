"""Production display: push the frame to a Pimoroni Inky Impression 13.3" (Spectra 6).

The panel is 1600 x 1200 landscape and ``set_image`` rejects anything else, so the portrait
1200 x 1600 poster is rotated to fit. Which way round depends on how the frame is hung, hence
``display.rotation`` in the config.

The driver quantizes to the six panel colors itself, dithering against the same blend of
driven and measured palettes that ``spectra6`` simulates, so the frame is handed over as RGB
and left alone. A full refresh takes tens of seconds and blocks in ``show``.
"""

from __future__ import annotations

import logging

from PIL import Image

log = logging.getLogger(__name__)

PANEL_RESOLUTION = (1600, 1200)  # landscape, as the driver wants it
SATURATION = 0.5  # the driver's own default; matches display.spectra6
ROTATIONS = (90, 270)


class InkyDisplay:
    """Show frames on the panel. ``panel`` is injected in tests; otherwise it is opened here."""

    def __init__(self, panel=None, *, rotation: int = 90, saturation: float = SATURATION):
        if rotation not in ROTATIONS:
            raise ValueError(f"rotation must be one of {ROTATIONS}, got {rotation!r}")
        self.rotation = rotation
        self.saturation = saturation
        self._panel = panel if panel is not None else open_panel()

    def show(self, image: Image.Image) -> None:
        frame = image.convert("RGB").rotate(self.rotation, expand=True)
        expected = (self._panel.width, self._panel.height)
        if frame.size != expected:
            raise ValueError(f"frame is {frame.size} after rotation; the panel wants {expected}")
        self._panel.set_image(frame, saturation=self.saturation)
        self._panel.show()


def open_panel():
    """Return the Inky driver, preferring EEPROM detection and falling back to the 13.3" panel.

    Detection needs I2C. When it isn't enabled or the EEPROM doesn't answer, the panel is
    driven directly over SPI instead, which is what ``auto`` would have selected anyway.
    """
    try:
        from inky.auto import auto
        from inky.inky_el133uf1 import Inky as InkyEL133UF1
    except ImportError as exc:
        raise RuntimeError(
            "display.backend is 'inky' but the inky package isn't installed; "
            'on the Pi: pip install -e ".[pi]"'
        ) from exc

    try:
        panel = auto()
    except (RuntimeError, OSError) as exc:
        log.warning('Inky auto-detection failed (%s); assuming the 13.3" Spectra 6 panel', exc)
        return InkyEL133UF1(resolution=PANEL_RESOLUTION)
    if (panel.width, panel.height) != PANEL_RESOLUTION:
        raise RuntimeError(
            f"detected a {panel.width}x{panel.height} Inky; this frame needs "
            f'{PANEL_RESOLUTION[0]}x{PANEL_RESOLUTION[1]} (Impression 13.3")'
        )
    return panel
