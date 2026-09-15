"""Build the compact world map used by the route graphic (assets/map/world.json).

Input: Natural Earth 1:50m land and lakes GeoJSON (public domain), e.g.
    https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson
    https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_lakes.geojson

Usage: python scripts/build_map_data.py ne_50m_land.geojson ne_50m_lakes.geojson

Outer rings only, coordinates rounded and thinned, tiny polygons dropped. The result is
small enough to load quickly on a Raspberry Pi Zero.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "map" / "world.json"
MIN_STEP_DEG = 0.08  # drop vertices closer than this to the previous kept vertex
MIN_AREA_DEG2 = {"land": 0.02, "lakes": 0.3}


def outer_rings(geojson_path: str) -> list[list[list[float]]]:
    features = json.loads(Path(geojson_path).read_text(encoding="utf-8"))["features"]
    rings = []
    for feature in features:
        geometry = feature["geometry"]
        polygons = (
            [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
        )
        rings.extend(polygon[0] for polygon in polygons)
    return rings


def thin(ring: list[list[float]]) -> list[list[float]]:
    kept = [ring[0]]
    for lon, lat in ring[1:]:
        if math.hypot(lon - kept[-1][0], lat - kept[-1][1]) >= MIN_STEP_DEG:
            kept.append([lon, lat])
    return [[round(lon, 2), round(lat, 2)] for lon, lat in kept]


def area(ring: list[list[float]]) -> float:
    return (
        abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:] + ring[:1], strict=True)))
        / 2
    )


def main(land_path: str, lakes_path: str) -> None:
    data = {"source": "Natural Earth 1:50m land and lakes (public domain), simplified"}
    for name, path in (("land", land_path), ("lakes", lakes_path)):
        rings = [thin(r) for r in outer_rings(path)]
        data[name] = [r for r in rings if len(r) >= 4 and area(r) >= MIN_AREA_DEG2[name]]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    points = sum(len(r) for key in ("land", "lakes") for r in data[key])
    print(
        f"{OUTPUT}: {len(data['land'])} land, {len(data['lakes'])} lakes, {points} points, "
        f"{OUTPUT.stat().st_size / 1e3:.0f} kB"
    )


if __name__ == "__main__":
    main(*sys.argv[1:3])
