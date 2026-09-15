"""Text drawing helpers: letter-spacing and shrink-to-fit. All ``y`` values are baselines."""

from __future__ import annotations

from collections.abc import Callable

from PIL import ImageDraw, ImageFont

Font = ImageFont.FreeTypeFont


def width(text: str, font: Font, tracking: float = 0.0) -> float:
    if not tracking:
        return font.getlength(text)
    return sum(font.getlength(ch) for ch in text) + tracking * max(len(text) - 1, 0)


def draw(
    canvas: ImageDraw.ImageDraw,
    x: float,
    y: float,
    text: str,
    font: Font,
    fill,
    *,
    align: str = "left",
    tracking: float = 0.0,
) -> float:
    """Draw text on a baseline; ``align`` is left/center/right of ``x``. Returns the width."""
    w = width(text, font, tracking)
    start = x - w / 2 if align == "center" else x - w if align == "right" else x
    if not tracking:
        canvas.text((start, y), text, font=font, fill=fill, anchor="ls")
        return w
    for ch in text:
        canvas.text((start, y), ch, font=font, fill=fill, anchor="ls")
        start += font.getlength(ch) + tracking
    return w


def fit(
    make_font: Callable[[int], Font],
    text: str,
    max_width: float,
    size: int,
    min_size: int,
    tracking_em: float = 0.0,
) -> Font | None:
    """Largest font from ``size`` down to ``min_size`` that fits, or None."""
    for s in range(size, min_size - 1, -2):
        font = make_font(s)
        if width(text, font, tracking_em * s) <= max_width:
            return font
    return None
