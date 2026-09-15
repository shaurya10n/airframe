"""Repository locations used at runtime."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = REPO_ROOT / "assets"
REFERENCE_DIR = REPO_ROOT / "data" / "reference"
OUTPUT_DIR = REPO_ROOT / "output"
