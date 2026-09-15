"""Render sample frames to PNG for previewing on a laptop: ``python -m airframe.preview``."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image

from airframe import samples
from airframe.artwork import ArtworkLibrary
from airframe.display.png import PngDisplay
from airframe.paths import ASSETS_DIR, OUTPUT_DIR, REFERENCE_DIR
from airframe.render import format, poster, theme


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m airframe.preview", description="Render sample frames to PNG files."
    )
    parser.add_argument("--out", type=Path, default=OUTPUT_DIR / "preview")
    parser.add_argument("--units", choices=format.UNITS, default="imperial")
    parser.add_argument("--no-eink", action="store_true", help="skip the Spectra 6 simulation")
    args = parser.parse_args(argv)

    library = ArtworkLibrary(ASSETS_DIR / "aircraft", REFERENCE_DIR / "aircraft_families.csv")
    tz = ZoneInfo(samples.TIMEZONE)
    frames = []
    for i, (name, sighting, now) in enumerate(samples.SAMPLES, 1):
        artwork = library.resolve(sighting.brand, sighting.type_code)
        image = poster.render(
            sighting, artwork, now=now, place=samples.PLACE, tz=tz, units=args.units
        )
        path = args.out / f"{i:02d}-{name}.png"
        PngDisplay(path, eink_preview=not args.no_eink).show(image)
        frames.append(image)
        print(f"{path}  [{artwork.stem if artwork else 'no artwork'}]")

    sheet_path = args.out / "contact-sheet.png"
    contact_sheet(frames).save(sheet_path)
    print(sheet_path)
    return 0


def contact_sheet(frames: list[Image.Image], columns: int = 5, scale: float = 0.25) -> Image.Image:
    gap = 24
    w, h = round(theme.WIDTH * scale), round(theme.HEIGHT * scale)
    rows = math.ceil(len(frames) / columns)
    sheet = Image.new(
        "RGB", (columns * w + (columns + 1) * gap, rows * h + (rows + 1) * gap), (70, 70, 70)
    )
    for i, frame in enumerate(frames):
        row, col = divmod(i, columns)
        sheet.paste(
            frame.resize((w, h), Image.Resampling.LANCZOS),
            (gap + col * (w + gap), gap + row * (h + gap)),
        )
    return sheet


if __name__ == "__main__":
    sys.exit(main())
