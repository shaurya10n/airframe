"""Simulate how a frame looks on the 6-color E Ink Spectra 6 panel.

Palette values come from Pimoroni's driver (``inky/inky_el133uf1.py``): the panel is driven
with six pure colors, and ``SATURATED_PALETTE`` is their measured on-screen appearance. The
driver dithers against a blend of the two (``saturation`` 0.5 by default); this reproduces
that and then paints each pixel in its measured color.
"""

from __future__ import annotations

from PIL import Image

DRIVEN = [(0, 0, 0), (255, 255, 255), (255, 255, 0), (255, 0, 0), (0, 0, 255), (0, 255, 0)]
MEASURED = [(0, 0, 0), (161, 164, 165), (208, 190, 71), (156, 72, 75), (61, 59, 94), (58, 91, 70)]


def simulate(image: Image.Image, saturation: float = 0.5) -> Image.Image:
    target = [
        tuple(round(m * saturation + d * (1 - saturation)) for m, d in zip(mc, dc, strict=True))
        for mc, dc in zip(MEASURED, DRIVEN, strict=True)
    ]
    quantized = image.convert("RGB").quantize(
        palette=_palette_image(target), dither=Image.Dither.FLOYDSTEINBERG
    )
    quantized.putpalette(_flat(MEASURED))
    return quantized.convert("RGB")


def _palette_image(colors: list[tuple[int, int, int]]) -> Image.Image:
    palette = Image.new("P", (1, 1))
    palette.putpalette(_flat(colors))
    return palette


def _flat(colors: list[tuple[int, int, int]]) -> list[int]:
    flat = [channel for color in colors for channel in color]
    return flat + list(colors[0]) * (256 - len(colors))
