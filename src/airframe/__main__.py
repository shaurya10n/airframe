"""Run the frame: ``python -m airframe`` (loop) or ``python -m airframe --once``."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from airframe import adsb, aircraft_db, config
from airframe.app import FrameApp
from airframe.artwork import ArtworkLibrary
from airframe.display.base import Display
from airframe.display.png import PngDisplay
from airframe.enrich import Enricher
from airframe.http import make_session
from airframe.livery import LiveryResolver, LiveryTables
from airframe.names import Names
from airframe.operators import load_operators
from airframe.routes import RouteLookup
from airframe.scoring import TrafficFrequency


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m airframe", description="Run the frame.")
    parser.add_argument(
        "--config", type=Path, help="TOML config (default: config/airframe.toml or the example)"
    )
    parser.add_argument("--once", action="store_true", help="run one update and exit")
    parser.add_argument("-v", "--verbose", action="store_true", help="log candidate scores")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    for noisy in ("urllib3", "PIL"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    try:
        cfg = config.load(args.config or config.default_path())
    except (OSError, KeyError, ValueError) as exc:
        parser.error(str(exc))

    app = build_app(cfg)
    if args.once:
        print(app.tick())
        return 0
    app.run()
    return 0


def build_app(cfg: config.FrameConfig) -> FrameApp:
    session = make_session()
    ref_cache = cfg.cache_dir / "reference"
    tables = LiveryTables.load(cfg.reference_dir)
    routes = RouteLookup(cfg.cache_dir / "routes.json", session)
    enricher = Enricher(
        lat=cfg.lat,
        lon=cfg.lon,
        home_country=cfg.home_country,
        scale_nm=cfg.radius_nm,
        weights=cfg.weights,
        aircraft_db=aircraft_db.open_database(ref_cache, session),
        operators=load_operators(ref_cache, session, max_age_days=30),
        names=Names(cfg.reference_dir),
        livery=LiveryResolver(tables, lat=cfg.lat, lon=cfg.lon, routes=routes),
        routes=routes,
        artwork=ArtworkLibrary(
            cfg.assets_dir / "aircraft", cfg.reference_dir / "aircraft_families.csv"
        ),
        frequency=TrafficFrequency(cfg.reference_dir / "traffic_frequency.csv"),
    )
    return FrameApp(
        cfg,
        fetch=lambda radius: adsb.fetch(session, cfg.lat, cfg.lon, radius, cfg.api_url),
        enricher=enricher,
        display=build_display(cfg),
    )


def build_display(cfg: config.FrameConfig) -> Display:
    if cfg.display == "inky":
        from airframe.display.inky import InkyDisplay

        return InkyDisplay(rotation=cfg.rotation)
    return PngDisplay(cfg.output_path, eink_preview=cfg.eink_preview)


if __name__ == "__main__":
    sys.exit(main())
