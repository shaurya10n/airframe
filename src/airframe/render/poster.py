"""Compose the portrait poster for one sighting."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

from airframe.models import Sighting
from airframe.render import aircraft, format, route_map, text, theme

LABEL_SIZE = 28
VALUE_SIZE = 46
ROW_GAP = 150  # right column: label-to-label spacing
TRACKED_EM = 0.13


def render(
    sighting: Sighting,
    artwork: Path | None,
    *,
    now: datetime,
    place: str,
    tz: ZoneInfo,
    units: str = "imperial",
) -> Image.Image:
    image = Image.new("RGB", (theme.WIDTH, theme.HEIGHT), theme.PAPER)
    canvas = ImageDraw.Draw(image)
    _aircraft(image, canvas, artwork)
    _titles(canvas, sighting)
    left, right = theme.MARGIN, theme.WIDTH - theme.MARGIN
    canvas.line((left, theme.TOP_RULE_Y, right, theme.TOP_RULE_Y), fill=theme.RULE, width=2)
    canvas.line(
        (
            theme.COLUMN_DIVIDER_X,
            theme.COLUMNS_TOP,
            theme.COLUMN_DIVIDER_X,
            theme.BOTTOM_RULE_Y - 40,
        ),
        fill=theme.RULE,
        width=2,
    )
    _flight_and_route(image, canvas, sighting)
    _stats(canvas, sighting, units)
    canvas.line((left, theme.BOTTOM_RULE_Y, right, theme.BOTTOM_RULE_Y), fill=theme.RULE, width=2)
    _footer(canvas, sighting, now, place, tz)
    return image


def _aircraft(image: Image.Image, canvas: ImageDraw.ImageDraw, artwork: Path | None) -> None:
    left, top, right, bottom = theme.AIRCRAFT_BOX
    if artwork is None:
        font = theme.sans(24)
        text.draw(
            canvas, (left + right) / 2, (top + bottom) / 2, "ARTWORK COMING SOON", font,
            theme.MUTED, align="center", tracking=TRACKED_EM * 24,
        )  # fmt: skip
        return
    plane = aircraft.fit(artwork, right - left, bottom - top)
    x = left + (right - left - plane.width) // 2
    y = top + (bottom - top - plane.height) // 2
    image.paste(plane, (x, y), plane)


def _titles(canvas: ImageDraw.ImageDraw, sighting: Sighting) -> None:
    center = theme.WIDTH / 2
    max_width = theme.WIDTH - 2 * theme.MARGIN
    title = sighting.title.upper()
    font = text.fit(theme.serif_medium, title, max_width, 64, 40, TRACKED_EM)
    if font:
        text.draw(
            canvas, center, theme.TITLE_BASELINE, title, font, theme.NAVY,
            align="center", tracking=TRACKED_EM * font.size,
        )  # fmt: skip
    font = text.fit(theme.serif, sighting.subtitle, max_width, 48, 32)
    if font:
        text.draw(
            canvas,
            center,
            theme.SUBTITLE_BASELINE,
            sighting.subtitle,
            font,
            theme.INK,
            align="center",
        )
    if sighting.registration:
        label = f"Registration: {sighting.registration}"
        text.draw(
            canvas, center, theme.REGISTRATION_BASELINE, label, theme.serif(30), theme.MUTED,
            align="center", tracking=1.5,
        )  # fmt: skip


def _label_value(canvas, x: float, top: float, label: str, value: str, max_width: float) -> None:
    text.draw(canvas, x, top + 22, label, theme.serif(LABEL_SIZE), theme.MUTED)
    font = text.fit(theme.serif, value, max_width, VALUE_SIZE, 30) or theme.serif(30)
    text.draw(canvas, x, top + 78, value, font, theme.INK)


def _flight_and_route(image: Image.Image, canvas: ImageDraw.ImageDraw, sighting: Sighting) -> None:
    x, right = theme.LEFT_COLUMN
    top = theme.COLUMNS_TOP
    if sighting.flight:
        _label_value(canvas, x, top, "Flight", sighting.flight, right - x)
    else:
        _label_value(canvas, x, top, "Callsign", sighting.callsign or format.MISSING, right - x)

    route_top = top + 130
    origin, destination = sighting.origin, sighting.destination
    text.draw(canvas, x, route_top + 22, "Route", theme.serif(LABEL_SIZE), theme.MUTED)
    if origin and destination:
        arrow = "  →  "
        value = f"{origin.city}{arrow}{destination.city}"
        font = text.fit(theme.serif, value, right - x, VALUE_SIZE, 30)
        if font is None:  # long city names: fall back to airport codes
            value = f"{origin.code}{arrow}{destination.code}"
            font = theme.serif(VALUE_SIZE)
            origin_label, destination_start = "", text.width(f"{origin.code}{arrow}", font)
        else:
            origin_label, destination_start = origin.code, text.width(f"{origin.city}{arrow}", font)
        text.draw(canvas, x, route_top + 78, value, font, theme.INK)
        codes_font, tracking = theme.sans(22), 0.14 * 22
        if origin_label:
            text.draw(
                canvas, x, route_top + 116, origin.code, codes_font, theme.MUTED, tracking=tracking
            )
            text.draw(
                canvas, x + destination_start, route_top + 116, destination.code, codes_font,
                theme.MUTED, tracking=tracking,
            )  # fmt: skip
    else:
        text.draw(canvas, x, route_top + 78, "Not available", theme.serif(VALUE_SIZE), theme.MUTED)

    left, map_top, map_right, map_bottom = theme.MAP_BOX
    position = (
        (sighting.lat, sighting.lon)
        if sighting.lat is not None and sighting.lon is not None
        else None
    )
    graphic = route_map.render(
        (map_right - left, map_bottom - map_top), origin, destination, position, sighting.track_deg
    )
    if graphic is not None:
        image.paste(graphic, (left, map_top), graphic)


def _stats(canvas: ImageDraw.ImageDraw, sighting: Sighting, units: str) -> None:
    x, right = theme.RIGHT_COLUMN
    rows = (
        ("Altitude", format.altitude(sighting.altitude_ft)),
        ("Ground speed", format.speed(sighting.ground_speed_kt, units)),
        ("Heading", format.heading(sighting.track_deg)),
        ("Distance away", format.distance(sighting.distance_nm, units)),
    )
    for i, (label, value) in enumerate(rows):
        _label_value(canvas, x, theme.COLUMNS_TOP + i * ROW_GAP, label, value, right - x)


def _footer(canvas, sighting: Sighting, now: datetime, place: str, tz: ZoneInfo) -> None:
    font = theme.sans(20)
    tracking = 0.18 * 20
    status = format.seen(sighting.seen_at, now, place, tz).upper()
    text.draw(
        canvas, theme.MARGIN, theme.FOOTER_BASELINE, status, font, theme.MUTED, tracking=tracking
    )
    coords = format.coordinates(sighting.lat, sighting.lon)
    if coords:
        text.draw(
            canvas, theme.WIDTH - theme.MARGIN, theme.FOOTER_BASELINE, coords, font, theme.MUTED,
            align="right", tracking=tracking,
        )  # fmt: skip
