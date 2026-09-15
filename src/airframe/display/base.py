"""The interface every display backend implements."""

from __future__ import annotations

from typing import Protocol

from PIL import Image


class Display(Protocol):
    def show(self, image: Image.Image) -> None:
        """Show a portrait 1200 x 1600 RGB frame."""
