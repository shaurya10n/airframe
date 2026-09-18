"""Trim and pre-size artwork to the poster's aircraft box, so the Pi never scales a big PNG.

Every image is trimmed to its visible pixels and scaled to the largest size that fits
``theme.AIRCRAFT_BOX`` — exactly what ``render.aircraft.fit`` does at render time, done once
here instead. The renderer then uses the file as-is: no resample, no multi-megabyte RGBA
buffer held in its cache.

Run it over the whole library, or over the files from a new batch:

    python scripts/resize_artwork.py --dry-run
    python scripts/resize_artwork.py
    python scripts/resize_artwork.py assets/aircraft/delta_A21N.png

Images are rewritten in place. The originals stay in git history, which is the place to go if
the poster layout ever grows and they need to be re-derived.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from airframe.paths import ASSETS_DIR  # noqa: E402
from airframe.render.aircraft import ALPHA_THRESHOLD  # noqa: E402
from airframe.render.theme import AIRCRAFT_BOX  # noqa: E402

LEFT, TOP, RIGHT, BOTTOM = AIRCRAFT_BOX
BOX = (RIGHT - LEFT, BOTTOM - TOP)


def resized(path: Path) -> Image.Image | None:
    """The trimmed, box-fitted image, or None when the file is already exactly that."""
    image = Image.open(path).convert("RGBA")
    mask = image.getchannel("A").point(lambda a: 255 if a > ALPHA_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox:
        image = image.crop(bbox)
    scale = min(BOX[0] / image.width, BOX[1] / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    if size == image.size and bbox == (0, 0, *image.size):
        return None
    return image.resize(size, Image.Resampling.LANCZOS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "paths", nargs="*", type=Path, help="PNGs to process (default: all of assets/aircraft)"
    )
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    args = parser.parse_args(argv)

    paths = args.paths or sorted((ASSETS_DIR / "aircraft").glob("*.png"))
    before = after = 0
    changed = 0
    for path in paths:
        was = path.stat().st_size
        image = resized(path)
        if image is None:
            before += was
            after += was
            print(f"  ok       {path.name}")
            continue
        if args.dry_run:
            buffer = io.BytesIO()
            image.save(buffer, "PNG", optimize=True)
            now = buffer.tell()
        else:
            image.save(path, "PNG", optimize=True)
            now = path.stat().st_size
        before += was
        after += now
        changed += 1
        print(f"  resized  {path.name}  {was / 1024:.0f} KB -> {now / 1024:.0f} KB  {image.size}")

    verb = "would shrink" if args.dry_run else "shrank"
    print(
        f"\n{changed}/{len(paths)} images {verb} the library "
        f"{before / 1e6:.1f} MB -> {after / 1e6:.1f} MB (box {BOX[0]}x{BOX[1]})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
