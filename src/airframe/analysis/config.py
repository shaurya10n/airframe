"""Analysis settings, loaded from TOML (see config/analysis.example.toml)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from airframe.analysis import geo

SOURCES = ("web", "github")
DEFAULT_CONFIG = Path("config/analysis.toml")
EXAMPLE_CONFIG = Path("config/analysis.example.toml")

# Artwork fallback levels, most specific first, with default match-quality weights.
ARTWORK_LEVELS = ("brand_type", "brand_family", "generic_type", "generic_family")
DEFAULT_LEVEL_WEIGHTS = {
    "brand_type": 1.0,
    "brand_family": 0.8,
    "generic_type": 0.5,
    "generic_family": 0.3,
}


@dataclass(frozen=True)
class Airport:
    code: str
    lat: float
    lon: float
    elevation_ft: float


@dataclass(frozen=True)
class LibraryConfig:
    brand_min: int = 30
    brand_max: int = 50
    generic_max: int = 20
    min_marginal_share: float = 0.002
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_LEVEL_WEIGHTS))
    always_include: tuple[str, ...] = ()
    hero_min_days: int = 3
    hero_max: int = 15


@dataclass(frozen=True)
class AnalysisConfig:
    location_name: str
    lat: float
    lon: float
    home_country: str
    primary_radius_nm: float
    radii_nm: tuple[float, ...]  # sorted ascending, includes the primary radius
    dates: tuple[date, ...]
    source: str
    concurrency: int
    extract_radius_nm: float
    encounter_gap_s: float
    max_segment_gap_s: float
    include_ground: bool
    airports: tuple[Airport, ...]
    airport_radius_nm: float
    airport_max_agl_ft: float
    airport_window_s: float
    top_n: int
    coverage_levels: tuple[int, ...]
    rare_outside_top: int
    rare_type_share: float
    data_dir: Path
    reference_dir: Path
    use_routes: bool
    route_max_offset_nm: float
    flight_block_min_support: int
    flight_block_min_purity: float
    library: LibraryConfig


def default_path() -> Path:
    return DEFAULT_CONFIG if DEFAULT_CONFIG.exists() else EXAMPLE_CONFIG


def resolve_dates(spec: dict, today: date | None = None) -> tuple[date, ...]:
    """Explicit ``list`` wins; otherwise the ``last_n_days`` complete UTC days ending ``end``."""
    today = today or datetime.now(UTC).date()
    if spec.get("list"):
        days = sorted({_as_date(d) for d in spec["list"]})
    else:
        end = _as_date(spec["end"]) if spec.get("end") else today - timedelta(days=1)
        count = int(spec.get("last_n_days", 7))
        if count < 1:
            raise ValueError("last_n_days must be at least 1")
        days = [end - timedelta(days=i) for i in range(count - 1, -1, -1)]
    incomplete = [d.isoformat() for d in days if d >= today]
    if incomplete:
        raise ValueError(f"only complete UTC days before {today} can be analyzed: {incomplete}")
    return tuple(days)


def load(
    path: Path,
    *,
    dates: list[str] | None = None,
    days: int | None = None,
    end: str | None = None,
    source: str | None = None,
) -> AnalysisConfig:
    """Load a config file, applying command-line overrides."""
    with path.open("rb") as f:
        raw = tomllib.load(f)

    date_spec = dict(raw.get("dates", {}))
    if dates:
        date_spec = {"list": dates}
    elif days is not None or end is not None:
        date_spec.pop("list", None)
        if days is not None:
            date_spec["last_n_days"] = days
        if end is not None:
            date_spec["end"] = end

    loc = raw["location"]
    radius = raw["radius"]
    src = raw.get("source", {})
    enc = raw.get("encounters", {})
    ops = raw.get("airport_ops", {})
    rep = raw.get("report", {})
    liv = raw.get("livery", {})
    lib = raw.get("library", {})

    primary = float(radius["primary_nm"])
    cfg = AnalysisConfig(
        location_name=loc.get("name", "configured location"),
        lat=float(loc["lat"]),
        lon=float(loc["lon"]),
        home_country=loc.get("home_country", ""),
        primary_radius_nm=primary,
        radii_nm=tuple(sorted({primary, *(float(r) for r in radius.get("compare_nm", []))})),
        dates=resolve_dates(date_spec),
        source=source or src.get("kind", "web"),
        concurrency=int(src.get("concurrency", 4)),
        extract_radius_nm=float(src.get("extract_radius_nm", 25)),
        encounter_gap_s=float(enc.get("gap_minutes", 30)) * 60,
        max_segment_gap_s=float(enc.get("max_segment_gap_seconds", 60)),
        include_ground=bool(enc.get("include_ground", False)),
        airports=tuple(
            Airport(a["code"], float(a["lat"]), float(a["lon"]), float(a.get("elevation_ft", 0)))
            for a in raw.get("airports", [])
        ),
        airport_radius_nm=float(ops.get("radius_nm", 4)),
        airport_max_agl_ft=float(ops.get("max_agl_ft", 2500)),
        airport_window_s=float(ops.get("window_minutes", 20)) * 60,
        top_n=int(rep.get("top_n", 25)),
        coverage_levels=tuple(
            int(n) for n in rep.get("coverage_levels", [10, 20, 30, 50, 75, 100])
        ),
        rare_outside_top=int(rep.get("rare_outside_top", 50)),
        rare_type_share=float(rep.get("rare_type_share", 0.005)),
        data_dir=Path(raw.get("data_dir", "data")),
        reference_dir=Path(liv.get("reference_dir", "data/reference")),
        use_routes=bool(liv.get("use_routes", True)),
        route_max_offset_nm=float(liv.get("route_max_offset_nm", 75)),
        flight_block_min_support=int(liv.get("flight_block_min_support", 10)),
        flight_block_min_purity=float(liv.get("flight_block_min_purity", 0.95)),
        library=LibraryConfig(
            brand_min=int(lib.get("brand_images_min", 30)),
            brand_max=int(lib.get("brand_images_max", 50)),
            generic_max=int(lib.get("generic_images_max", 20)),
            min_marginal_share=float(lib.get("min_marginal_share", 0.002)),
            weights={
                **DEFAULT_LEVEL_WEIGHTS,
                **{k: float(v) for k, v in lib.get("weights", {}).items()},
            },
            always_include=tuple(lib.get("always_include", [])),
            hero_min_days=int(lib.get("hero_min_days", 3)),
            hero_max=int(lib.get("hero_max", 15)),
        ),
    )
    _validate(cfg)
    return cfg


def _validate(cfg: AnalysisConfig) -> None:
    if cfg.source not in SOURCES:
        raise ValueError(f"source must be one of {SOURCES}, got {cfg.source!r}")
    if cfg.radii_nm[-1] > cfg.extract_radius_nm:
        raise ValueError("extract_radius_nm must be at least the largest analysis radius")
    for ap in cfg.airports:
        reach = float(geo.distance_nm(ap.lat, ap.lon, cfg.lat, cfg.lon)) + cfg.airport_radius_nm
        if reach > cfg.extract_radius_nm:
            raise ValueError(
                f"airport {ap.code} checks need extract_radius_nm >= {reach:.1f} "
                f"(currently {cfg.extract_radius_nm:g})"
            )
    weights = cfg.library.weights
    if set(weights) != set(ARTWORK_LEVELS):
        raise ValueError(f"library.weights must have exactly these keys: {ARTWORK_LEVELS}")
    ordered = [weights[level] for level in ARTWORK_LEVELS]
    if not all(1 >= a > b > 0 for a, b in zip(ordered, ordered[1:], strict=False)):
        raise ValueError(
            "library.weights must decrease from brand_type to generic_family, in (0, 1]"
        )
    if cfg.library.brand_min > cfg.library.brand_max:
        raise ValueError("library.brand_images_min must not exceed brand_images_max")


def _as_date(value) -> date:
    return value if isinstance(value, date) else date.fromisoformat(str(value))
