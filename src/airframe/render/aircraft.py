"""Load aircraft artwork and scale every plane to fill the same box."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image

ALPHA_THRESHOLD = 16  # ignore faint halo pixels when trimming


@lru_cache(maxsize=8)
def _trimmed(path: str) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    mask = image.getchannel("A").point(lambda a: 255 if a > ALPHA_THRESHOLD else 0)
    bbox = mask.getbbox()
    return image.crop(bbox) if bbox else image


def fit(path: Path, box_width: int, box_height: int) -> Image.Image:
    """Trim transparent margins, then scale to the largest size that fits the box."""
    image = _trimmed(str(path))
    scale = min(box_width / image.width, box_height / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)
