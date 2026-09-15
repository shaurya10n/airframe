"""Frame settings, loaded from TOML (see config/airframe.example.toml).

Relative paths are resolved against the repository root, so the service can run from any
working directory.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

from airframe.adsb import API_URL
from airframe.paths import REPO_ROOT
from airframe.render.format import UNITS
from airframe.scoring import Weights

DEFAULT_CONFIG = REPO_ROOT / "config" / "airframe.toml"
EXAMPLE_CONFIG = REPO_ROOT / "config" / "airframe.example.toml"
DISPLAYS = ("png", "inky")


@dataclass(frozen=True)
class FrameConfig:
    place: str
    lat: float
    lon: float
    timezone: str
    home_country: str
    radius_nm: float
    fallback_radius_nm: float
    refresh_seconds: float
    min_display_seconds: float
    repeat_cooldown_minutes: float
    api_url: str
    weights: Weights
    display: str
    output_path: Path
    eink_preview: bool
    units: str
    reference_dir: Path
    assets_dir: Path
    cache_dir: Path

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


def default_path() -> Path:
    return DEFAULT_CONFIG if DEFAULT_CONFIG.exists() else EXAMPLE_CONFIG


def load(path: Path) -> FrameConfig:
    with path.open("rb") as f:
        raw = tomllib.load(f)
    loc = raw["location"]
    traffic = raw.get("traffic", {})
    weights = raw.get("scoring", {})
    display = raw.get("display", {})
    paths = raw.get("paths", {})

    radius = float(traffic.get("radius_nm", 15))
    cfg = FrameConfig(
        place=loc.get("name", "here"),
        lat=float(loc["lat"]),
        lon=float(loc["lon"]),
        timezone=loc.get("timezone", "UTC"),
        home_country=loc.get("home_country", ""),
        radius_nm=radius,
        fallback_radius_nm=float(traffic.get("fallback_radius_nm", radius)),
        refresh_seconds=float(traffic.get("refresh_seconds", 180)),
        min_display_seconds=float(traffic.get("min_display_seconds", 180)),
        repeat_cooldown_minutes=float(traffic.get("repeat_cooldown_minutes", 30)),
        api_url=traffic.get("api_url", API_URL),
        weights=Weights(
            interestingness=float(weights.get("interestingness", 55)),
            proximity=float(weights.get("proximity", 30)),
            artwork=float(weights.get("artwork", 15)),
        ),
        display=display.get("backend", "png"),
        output_path=_path(display.get("path", "output/frame.png")),
        eink_preview=bool(display.get("eink_preview", True)),
        units=display.get("units", "imperial"),
        reference_dir=_path(paths.get("reference_dir", "data/reference")),
        assets_dir=_path(paths.get("assets_dir", "assets")),
        cache_dir=_path(paths.get("cache_dir", "data/cache")),
    )
    if cfg.display not in DISPLAYS:
        raise ValueError(f"display.backend must be one of {DISPLAYS}, got {cfg.display!r}")
    if cfg.units not in UNITS:
        raise ValueError(f"display.units must be one of {UNITS}, got {cfg.units!r}")
    if min(cfg.weights.interestingness, cfg.weights.proximity, cfg.weights.artwork) < 0:
        raise ValueError("scoring weights must not be negative")
    cfg.tz  # noqa: B018 - fail early on an unknown timezone
    return cfg


def _path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path
