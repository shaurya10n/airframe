"""Canvas, colors, fonts and layout for the portrait poster (1200 x 1600)."""

from __future__ import annotations

from functools import lru_cache

from PIL import ImageFont

from airframe.paths import ASSETS_DIR

WIDTH, HEIGHT = 1200, 1600  # portrait; the panel itself is 1600 x 1200
MARGIN = 80

PAPER = (233, 231, 225)
INK = (40, 40, 40)
NAVY = (31, 46, 74)
MUTED = (108, 108, 108)
RULE = (150, 150, 150)
LAND = (196, 196, 196)

# Layout, as (left, top, right, bottom) boxes and baselines, in pixels.
AIRCRAFT_BOX = (70, 110, 1130, 560)
TITLE_BASELINE = 650
SUBTITLE_BASELINE = 722
REGISTRATION_BASELINE = 780
TOP_RULE_Y = 830
COLUMNS_TOP = 870
COLUMN_DIVIDER_X = 740
LEFT_COLUMN = (100, 710)
RIGHT_COLUMN = (790, 1120)
MAP_BOX = (85, 1135, 725, 1460)  # 640 x 325, the world map's natural ~2:1 shape
BOTTOM_RULE_Y = 1490
FOOTER_BASELINE = 1540

FONT_DIR = ASSETS_DIR / "fonts"


@lru_cache(maxsize=32)
def serif(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / "IBMPlexSerif-Regular.ttf"), size)


@lru_cache(maxsize=32)
def serif_medium(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / "IBMPlexSerif-Medium.ttf"), size)


@lru_cache(maxsize=32)
def sans(size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(FONT_DIR / "IBMPlexSans-Variable.ttf"), size)
    font.set_variation_by_name("Regular")
    return font
