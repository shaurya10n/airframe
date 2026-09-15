"""Route graphic: a world map with the great-circle route and the aircraft's position.

The whole world is always shown, in a Miller projection from 60°S to 84°N. It's centered on
the Atlantic, so routes from North America to Europe or the Middle East never cross the map
edge; routes that do (e.g. across the Pacific) are drawn on both sides. Shapes are drawn at
2x and downscaled for smooth edges; the land layer is cached between frames.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from airframe.models import Airport
from airframe.paths import ASSETS_DIR
from airframe.render import text, theme

MAP_FILE = ASSETS_DIR / "map" / "world.json"
SUPERSAMPLE = 2
CENTER_LON = -10.0
NORTH_LAT, SOUTH_LAT = 84.0, -60.0
FADE_PX = 10
SHORT_ROUTE_PX = 60  # endpoints closer than this get one combined label
LABEL_SIZE = 18

# Aircraft marker, nose pointing up, in units of the marker radius.
PLANE = [
    (0.0, -1.0), (0.11, -0.62), (0.11, -0.2), (0.92, 0.26), (0.92, 0.42), (0.11, 0.2),
    (0.08, 0.66), (0.38, 0.86), (0.38, 0.98), (0.0, 0.9), (-0.38, 0.98), (-0.38, 0.86),
    (-0.08, 0.66), (-0.11, 0.2), (-0.92, 0.42), (-0.92, 0.26), (-0.11, -0.2), (-0.11, -0.62),
]  # fmt: skip


def miller_y(lat: float) -> float:
    phi = math.radians(max(min(lat, 89.0), -89.0))
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * phi))


def natural_aspect() -> float:
    """Width / height of the undistorted world map."""
    return 2 * math.pi / (miller_y(NORTH_LAT) - miller_y(SOUTH_LAT))


@dataclass(frozen=True)
class WorldProjection:
    width: float
    height: float
    center_lon: float = CENTER_LON

    def x(self, lon: float, wrap: bool = True) -> float:
        offset = lon - (self.center_lon - 180)
        return (offset % 360 if wrap else offset) / 360 * self.width

    def y(self, lat: float) -> float:
        top, bottom = miller_y(NORTH_LAT), miller_y(SOUTH_LAT)
        return (top - miller_y(lat)) / (top - bottom) * self.height

    def xy(self, lat: float, lon: float) -> tuple[float, float]:
        return self.x(lon), self.y(lat)


@dataclass(frozen=True)
class _Shape:
    points: tuple[tuple[float, float], ...]  # (lon, lat)
    bbox: tuple[float, float, float, float]  # min lon, min lat, max lon, max lat


@lru_cache(maxsize=1)
def _world(path: str) -> dict[str, list[_Shape]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    shapes = {}
    for key in ("land", "lakes"):
        shapes[key] = []
        for ring in data[key]:
            lons = [p[0] for p in ring]
            lats = [p[1] for p in ring]
            points = tuple((p[0], p[1]) for p in ring)
            shapes[key].append(_Shape(points, (min(lons), min(lats), max(lons), max(lats))))
    return shapes


def great_circle(a: tuple[float, float], b: tuple[float, float], steps: int = 64):
    """Points (lat, lon) along the great circle from a to b, with continuous longitudes."""
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = 2 * math.asin(
        math.sqrt(
            math.sin((lat2 - lat1) / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
        )
    )
    if d < 1e-9:
        return [a, b]
    points, previous = [], None
    for i in range(steps + 1):
        f = i / steps
        k1, k2 = math.sin((1 - f) * d) / math.sin(d), math.sin(f * d) / math.sin(d)
        x = k1 * math.cos(lat1) * math.cos(lon1) + k2 * math.cos(lat2) * math.cos(lon2)
        y = k1 * math.cos(lat1) * math.sin(lon1) + k2 * math.cos(lat2) * math.sin(lon2)
        z = k1 * math.sin(lat1) + k2 * math.sin(lat2)
        lat = math.degrees(math.atan2(z, math.hypot(x, y)))
        lon = math.degrees(math.atan2(y, x))
        if previous is not None:
            lon = previous + (lon - previous + 180) % 360 - 180
        points.append((lat, lon))
        previous = lon
    return points


def render(
    size: tuple[int, int],
    origin: Airport | None,
    destination: Airport | None,
    position: tuple[float, float] | None,
    track_deg: float | None,
) -> Image.Image:
    """Transparent RGBA world map of ``size`` with the route and aircraft drawn on it."""
    w, h = size
    s = SUPERSAMPLE
    layer = _land_layer((w * s, h * s)).copy()
    projection = WorldProjection(w * s, h * s)
    canvas = ImageDraw.Draw(layer)

    if origin and destination:
        route = great_circle((origin.lat, origin.lon), (destination.lat, destination.lon))
        line = [(projection.x(lon, wrap=False), projection.y(lat)) for lat, lon in route]
        start = projection.x(route[0][1]) - line[0][0]  # move the line onto the map
        for copy in (-projection.width, 0.0, projection.width):
            points = [(x + start + copy, y) for x, y in line]
            canvas.line(points, fill=theme.NAVY, width=3 * s, joint="curve")
        for airport in (origin, destination):
            x, y = projection.xy(airport.lat, airport.lon)
            canvas.ellipse((x - 5 * s, y - 5 * s, x + 5 * s, y + 5 * s), fill=theme.NAVY)
    if position:
        _draw_marker(canvas, projection.xy(*position), track_deg, 15 * s)

    image = layer.resize(size, Image.Resampling.LANCZOS)
    if origin and destination:
        _label_endpoints(ImageDraw.Draw(image), WorldProjection(w, h), origin, destination)
    return image


@lru_cache(maxsize=2)
def _land_layer(size: tuple[int, int]) -> Image.Image:
    w, h = size
    projection = WorldProjection(w, h)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas = ImageDraw.Draw(layer)
    world = _world(str(MAP_FILE))
    for key, fill in (("land", theme.LAND + (255,)), ("lakes", (0, 0, 0, 0))):
        for shape in world[key]:
            min_lon, min_lat, max_lon, max_lat = shape.bbox
            if max_lat < SOUTH_LAT or min_lat > NORTH_LAT:
                continue
            ys = [projection.y(lat) for _, lat in shape.points]
            for shift in (-360.0, 0.0, 360.0):
                left = projection.x(min_lon + shift, wrap=False)
                right = projection.x(max_lon + shift, wrap=False)
                if right < 0 or left > w:
                    continue
                points = [
                    (projection.x(lon + shift, wrap=False), y)
                    for (lon, _), y in zip(shape.points, ys, strict=True)
                ]
                canvas.polygon(points, fill=fill)

    inset = FADE_PX * SUPERSAMPLE
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((inset, inset, w - inset, h - inset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(inset / 2))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    return layer


def _draw_marker(canvas, center, track_deg, radius) -> None:
    cx, cy = center
    if track_deg is None:
        r = radius * 0.45
        canvas.ellipse((cx - r, cy - r, cx + r, cy + r), fill=theme.NAVY)
        return
    t = math.radians(track_deg)
    cos_t, sin_t = math.cos(t), math.sin(t)

    def outline(scale: float):
        return [
            (
                cx + (x * cos_t - y * sin_t) * radius * scale,
                cy + (x * sin_t + y * cos_t) * radius * scale,
            )
            for x, y in PLANE
        ]

    canvas.polygon(outline(1.35), fill=theme.PAPER)  # halo so the marker reads over the line
    canvas.polygon(outline(1.0), fill=theme.NAVY)


def _label_endpoints(canvas, projection: WorldProjection, origin: Airport, destination: Airport):
    ox, oy = projection.xy(origin.lat, origin.lon)
    dx, dy = projection.xy(destination.lat, destination.lon)
    if math.hypot(dx - ox, dy - oy) < SHORT_ROUTE_PX:
        label = f"{origin.code} → {destination.code}"
        _label(canvas, projection, label, max(ox, dx), (oy + dy) / 2, "left")
        return
    _label(canvas, projection, origin.code, ox, oy, "right" if ox < dx else "left")
    _label(canvas, projection, destination.code, dx, dy, "right" if dx < ox else "left")


def _label(canvas, projection: WorldProjection, label: str, x: float, y: float, align: str):
    font = theme.sans(LABEL_SIZE)
    tracking = 0.12 * LABEL_SIZE
    label_w = text.width(label, font, tracking)
    lx = x - 12 if align == "right" else x + 12
    if align == "right":
        lx = min(max(lx, label_w + 4), projection.width - 4)
    else:
        lx = min(max(lx, 4), projection.width - label_w - 4)
    ly = min(max(y + 30, LABEL_SIZE + 4), projection.height - 6)
    text.draw(canvas, lx, ly, label, font, theme.NAVY, align=align, tracking=tracking)
