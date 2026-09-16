"""Replay cached historical traffic through the live frame pipeline.

Feeds positions from the offline analysis cache (``data/cache/heatmap_extracts``) to the same
Enricher and FrameApp the real frame uses, so selection, artwork and rendering can be watched
and tuned without waiting for real time. Frames are written to ``output/frame.png`` exactly
as the live app writes them.

    python -m airframe.analysis.replay --switches 100 --frame-seconds 3

Simulated time advances by the configured refresh interval. Updates that don't change the
aircraft are processed instantly; the pause happens only when the frame actually changes,
so ``--frame-seconds`` is the time you get to look at each new frame.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np

from airframe import adsb, aircraft_db, config, geo
from airframe.analysis import encounters as analysis_encounters
from airframe.analysis import geo as array_geo
from airframe.analysis import heatmap
from airframe.app import FrameApp
from airframe.artwork import ArtworkLibrary
from airframe.display.png import PngDisplay
from airframe.enrich import Enricher
from airframe.http import make_session
from airframe.livery import LiveryResolver, LiveryTables
from airframe.names import Names
from airframe.operators import load_operators
from airframe.routes import RouteLookup
from airframe.scoring import TrafficFrequency

log = logging.getLogger("airframe.replay")

POSITION_WINDOW_S = 60  # how far back a position may be, as in the live API


class HistoricalTraffic:
    """Cached positions, served as if they were live API contacts."""

    def __init__(self, cfg: config.FrameConfig, db: aircraft_db.AircraftDB):
        pattern = f"{cfg.lat:.4f}_{cfg.lon:.4f}_*nm/*.npz"
        paths = sorted((cfg.cache_dir / "heatmap_extracts").glob(pattern))
        if not paths:
            raise SystemExit(
                f"no cached extracts matching {pattern}; run python -m airframe.analysis first"
            )
        positions, callsigns = [], []
        for path in paths:
            with np.load(path) as z:
                positions.append(z["positions"])
                callsigns.append(z["callsigns"])
        pos = np.concatenate(positions)
        pos = pos[~pos["ground"]]
        self._pos = pos[np.argsort(pos["ts"], kind="stable")]
        self._times = self._pos["ts"].astype(np.float64)
        self._callsigns = analysis_encounters.CallsignIndex(np.concatenate(callsigns))
        self._db = db
        self._lat, self._lon = cfg.lat, cfg.lon
        self.start = datetime.fromtimestamp(float(self._times[0]), UTC)
        self.end = datetime.fromtimestamp(float(self._times[-1]), UTC)
        log.info(
            "replaying %d positions from %d day(s): %s to %s UTC",
            len(self._pos), len(paths), self.start.date(), self.end.date(),
        )  # fmt: skip

    def contacts_at(self, when: datetime, radius_nm: float) -> list[adsb.Contact]:
        t = when.timestamp()
        lo = int(np.searchsorted(self._times, t - POSITION_WINDOW_S, "right"))
        hi = int(np.searchsorted(self._times, t, "right"))
        window = self._pos[lo:hi]
        if not window.size:
            return []
        near = array_geo.distance_nm(window["lat"], window["lon"], self._lat, self._lon)
        window = window[near <= radius_nm]

        contacts = []
        for addr in np.unique(window["addr"]):
            samples = window[window["addr"] == addr]
            last, first = samples[-1], samples[0]
            track = None
            if len(samples) > 1 and (last["lat"], last["lon"]) != (first["lat"], first["lon"]):
                track = geo.bearing_deg(first["lat"], first["lon"], last["lat"], last["lon"])
            hex_code = heatmap.addr_to_hex(int(addr))
            record = None if hex_code.startswith("~") else self._db.lookup(hex_code)
            contacts.append(
                adsb.Contact(
                    hex=hex_code,
                    callsign=self._callsigns.nearest(int(addr), t),
                    registration=record.registration if record else "",
                    type_code=record.type_code if record else "",
                    lat=float(last["lat"]),
                    lon=float(last["lon"]),
                    altitude_ft=None if np.isnan(last["alt_ft"]) else int(last["alt_ft"]),
                    on_ground=False,
                    ground_speed_kt=None if np.isnan(last["gs_kt"]) else float(last["gs_kt"]),
                    track_deg=track,
                    distance_nm=float(
                        geo.distance_nm(self._lat, self._lon, last["lat"], last["lon"])
                    ),
                    db_flags=0,  # military comes from the aircraft DB record
                    seen_at=datetime.fromtimestamp(float(last["ts"]), UTC),
                )
            )
        return contacts


@dataclass
class Clock:
    now: datetime

    def __call__(self) -> datetime:
        return self.now


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m airframe.analysis.replay",
        description="Replay cached traffic through the live frame pipeline.",
    )
    parser.add_argument("--config", type=Path, help="frame TOML (default: the live app's)")
    parser.add_argument("--switches", type=int, default=100, help="stop after this many new frames")
    parser.add_argument(
        "--frame-seconds", type=float, default=3.0, help="how long to show each new frame"
    )
    parser.add_argument("--start", help="first simulated time, e.g. 2026-09-08T13:00")
    parser.add_argument("--day-start", type=int, default=6, help="first local hour to replay")
    parser.add_argument("--day-end", type=int, default=23, help="last local hour to replay")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    for noisy in ("urllib3", "PIL", "airframe.app"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    cfg = config.load(args.config or config.default_path())

    session = make_session()
    ref_cache = cfg.cache_dir / "reference"
    db = aircraft_db.open_database(ref_cache, session)
    traffic = HistoricalTraffic(cfg, db)
    routes = RouteLookup(cfg.cache_dir / "routes.json", session)
    tables = LiveryTables.load(cfg.reference_dir)
    enricher = Enricher(
        lat=cfg.lat,
        lon=cfg.lon,
        home_country=cfg.home_country,
        scale_nm=cfg.radius_nm,
        weights=cfg.weights,
        aircraft_db=db,
        operators=load_operators(ref_cache, session, max_age_days=30),
        names=Names(cfg.reference_dir),
        livery=LiveryResolver(tables, lat=cfg.lat, lon=cfg.lon, routes=routes),
        routes=routes,
        artwork=ArtworkLibrary(
            cfg.assets_dir / "aircraft", cfg.reference_dir / "aircraft_families.csv"
        ),
        frequency=TrafficFrequency(cfg.reference_dir / "traffic_frequency.csv"),
    )

    clock = Clock(_first_moment(traffic, cfg, args))
    app = FrameApp(
        cfg,
        fetch=lambda radius: traffic.contacts_at(clock.now, radius),
        enricher=enricher,
        display=PngDisplay(cfg.output_path, eink_preview=cfg.eink_preview),
        clock=clock,
    )

    step = timedelta(seconds=cfg.refresh_seconds)
    shown: list[tuple[datetime, str, str, str, float]] = []
    ticks = held = 0
    while len(shown) < args.switches and clock.now < traffic.end:
        local = clock.now.astimezone(cfg.tz)
        if not args.day_start <= local.hour < args.day_end:
            clock.now += step
            continue
        outcome = app.tick()
        ticks += 1
        if outcome == "held":
            held += 1
        if outcome == "shown":
            current = app.current
            shown.append(
                (
                    local,
                    current.sighting.title,
                    current.sighting.subtitle,
                    current.candidate.artwork_level or "none",
                    current.candidate.score,
                )
            )
            log.info(
                "%3d  %s  %-22s %-26s %-14s score %4.1f",
                len(shown), local.strftime("%a %H:%M"), current.sighting.title[:22],
                current.sighting.subtitle[:26], current.candidate.artwork_level or "NO ARTWORK",
                current.candidate.score,
            )  # fmt: skip
            time.sleep(args.frame_seconds)
        clock.now += step

    _summarize(shown, ticks, held, cfg)
    return 0


def _first_moment(traffic: HistoricalTraffic, cfg: config.FrameConfig, args) -> datetime:
    if args.start:
        return datetime.fromisoformat(args.start).replace(tzinfo=cfg.tz).astimezone(UTC)
    moment = traffic.start
    while not args.day_start <= moment.astimezone(cfg.tz).hour < args.day_end:
        moment += timedelta(seconds=cfg.refresh_seconds)
    return moment


def _summarize(shown, ticks: int, held: int, cfg: config.FrameConfig) -> None:
    if not shown:
        log.warning("no frames were shown")
        return
    levels = Counter(level for *_, level, _ in shown)
    brands = Counter(title for _, title, *_ in shown)
    span = shown[-1][0] - shown[0][0]
    print(f"\n{len(shown)} frames over {span} of simulated time ({ticks} updates, {held} held)")
    print("\nartwork level of the frames shown:")
    for level in ("brand_type", "brand_family", "generic_type", "generic_family", "none"):
        count = levels.get(level, 0)
        if count:
            print(f"  {level:16} {count:>4}  {count / len(shown):5.1%}")
    print(
        f"\nexact livery on {levels.get('brand_type', 0) / len(shown):.0%} of frames, "
        f"no artwork on {levels.get('none', 0) / len(shown):.0%}"
    )
    print("\nmost shown:")
    for title, count in brands.most_common(8):
        print(f"  {title:26} {count:>3}")
    print(f"\nlast frame: {cfg.output_path}")


if __name__ == "__main__":
    sys.exit(main())
