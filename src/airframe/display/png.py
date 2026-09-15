"""Development display: write the frame to a PNG, plus an e-ink simulation next to it."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from airframe.display import spectra6


class PngDisplay:
    def __init__(self, path: Path, eink_preview: bool = True):
        self.path = path
        self.eink_preview = eink_preview

    def show(self, image: Image.Image) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        image.save(self.path)
        if self.eink_preview:
            spectra6.simulate(image).save(self.path.with_name(f"{self.path.stem}-eink.png"))
