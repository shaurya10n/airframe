"""Sweep scoring weights against cached traffic and report which ones suit the frame best.

Replays every daytime update in the analysis cache once to extract each candidate's
components (interestingness, proximity, artwork level), then evaluates every weight
combination against that table using the same selection rules as the live app.

The artwork library can be projected forward (``--with-batches``) so weights can be tuned for
the library that is about to exist rather than the one on disk.

Configs are ranked by the average value of the frames they would have shown:

    frame value = w_image x artwork quality + w_interest x interestingness + w_near x proximity

Three profiles are reported, since the right balance is a matter of taste:

* **image first** - a good picture matters most
* **balanced** - the default
* **cool first** - unusual aircraft matter most

    python scripts/sweep_weights.py --step 5 --with-batches
"""

from __future__ import annotations

import argparse
import itertools
import logging
import statistics
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from airframe import aircraft_db, config, scoring  # noqa: E402
from airframe.analysis.replay import HistoricalTraffic  # noqa: E402
from airframe.artwork import ArtworkLibrary  # noqa: E402
from airframe.enrich import Enricher  # noqa: E402
from airframe.http import make_session  # noqa: E402
from airframe.livery import LiveryResolver, LiveryTables  # noqa: E402
from airframe.names import Names  # noqa: E402
from airframe.operators import load_operators  # noqa: E402
from airframe.routes import RouteLookup  # noqa: E402
from airframe.scoring import WIDEBODY_TYPES, TrafficFrequency, Weights  # noqa: E402

log = logging.getLogger("sweep")

BATCH_C = """alaska_B739 jetblue_A321 netjets_C68A united_A21N alaska_B39M american-eagle_CRJ7
delta-connection_E75L netjets_E55P delta_B763 united_A319 american_A21N united-express_CRJ7
american_A319 jetblue_BCS3 united_A320 air-canada_BCS3 delta_A320 flexjet_E545 delta_BCS3
delta_B753 american_B38M flexjet_CL35 delta-connection_E170 united_B737 frontier_A20N
flexjet_E55P""".split()
BATCH_D = "ANY_DA40 ANY_GA-TWIN ANY_TURBOPROP-SINGLE delta_A330-FAM netjets_BIZJET-MIDSIZE".split()

# How good the picture is: an exact livery is the goal, a generic silhouette is acceptable.
IMAGE_VALUE = {"brand_type": 1.0, "brand_family": 0.75, "generic_type": 0.5, "generic_family": 0.45}

# (image, interestingness, proximity) weights for judging the frames a config would show.
PROFILES = {
    "image first": (0.60, 0.25, 0.15),
    "balanced": (0.45, 0.35, 0.20),
    "cool first": (0.30, 0.50, 0.20),
}


@dataclass(frozen=True)
class Option:
    """One aircraft the frame could have shown at one update."""

    hex: str
    title: str
    type_code: str
    interestingness: float
    proximity: float
    artwork_level: str
    notable: bool
    distance_nm: float


def build_options(cfg, library_keys: set[str], days: int | None):
    """One pass over the cache: every update's candidates and their score components."""
    session = make_session()
    ref_cache = cfg.cache_dir / "reference"
    db = aircraft_db.open_database(ref_cache, session)
    traffic = HistoricalTraffic(cfg, db)
    routes = RouteLookup(cfg.cache_dir / "routes.json", session)
    tables = LiveryTables.load(cfg.reference_dir)
    artwork = ArtworkLibrary(
        cfg.assets_dir / "aircraft", cfg.reference_dir / "aircraft_families.csv"
    )
    # Project the library forward: pretend the planned images already exist.
    artwork._images = {key: Path(f"{key}.png") for key in library_keys}  # noqa: SLF001
    enricher = Enricher(
        lat=cfg.lat,
        lon=cfg.lon,
        home_country=cfg.home_country,
        scale_nm=cfg.radius_nm,
        weights=Weights(),  # the components are weight-independent
        aircraft_db=db,
        operators=load_operators(ref_cache, session, max_age_days=30),
        names=Names(cfg.reference_dir),
        livery=LiveryResolver(tables, lat=cfg.lat, lon=cfg.lon, routes=routes),
        routes=routes,
        artwork=artwork,
        frequency=TrafficFrequency(cfg.reference_dir / "traffic_frequency.csv"),
    )
    brands = tables.brands

    moments: list[datetime] = []
    step = timedelta(seconds=cfg.refresh_seconds)
    moment, end = traffic.start, traffic.end
    if days:
        end = min(end, traffic.start + timedelta(days=days))
    while moment < end:
        if 6 <= moment.astimezone(cfg.tz).hour < 23:
            moments.append(moment)
        moment += step

    log.info("reading %d updates from the cache", len(moments))
    callsigns: set[str] = set()
    contacts_by_moment = []
    for moment in moments:
        contacts = traffic.contacts_at(moment, cfg.radius_nm)
        contacts_by_moment.append(contacts)
        callsigns.update(c.callsign for c in contacts if c.callsign)
    routes.prefetch(callsigns)  # one bulk lookup instead of thousands of small ones

    log.info("scoring candidates")
    table = []
    for moment, contacts in zip(moments, contacts_by_moment, strict=True):
        options = []
        for c in enricher.candidates(contacts):
            country = brands[c.brand].country if c.brand in brands else ""
            foreign = bool(country and country != cfg.home_country)
            words = c.aircraft.description.split()
            options.append(
                Option(
                    hex=c.hex,
                    title=c.brand or c.airline_icao or (words[0] if words else "unknown"),
                    type_code=c.type_code,
                    interestingness=c.interestingness,
                    proximity=c.proximity,
                    artwork_level=c.artwork_level,
                    notable=c.military or c.type_code in WIDEBODY_TYPES or foreign,
                    distance_nm=c.contact.distance_nm,
                )
            )
        table.append((moment, options))
    return table


def evaluate(table, weights: Weights, cfg) -> dict:
    """Run the live selection rules with these weights and summarize what would be shown."""
    cooldown = timedelta(minutes=cfg.repeat_cooldown_minutes)
    recent: dict[str, datetime] = {}
    current: Option | None = None
    shown: list[Option] = []
    for moment, options in table:
        if not options:
            continue
        scored = sorted(
            options,
            key=lambda o: scoring.score(weights, o.interestingness, o.proximity, o.artwork_level),
            reverse=True,
        )
        recent = {h: t for h, t in recent.items() if moment - t < cooldown}
        fresh = [o for o in scored if o.hex not in recent or (current and o.hex == current.hex)]
        choice = (fresh or scored)[0]
        if current is None or choice.hex != current.hex:
            if current is not None:
                recent[current.hex] = moment
            current = choice
            shown.append(choice)
    if not shown:
        return {}
    n = len(shown)
    levels = Counter(o.artwork_level or "none" for o in shown)
    titles = Counter(o.title for o in shown)
    summary = {
        "frames": n,
        "exact": levels["brand_type"] / n,
        "any_image": 1 - levels["none"] / n,
        "notable": sum(o.notable for o in shown) / n,
        "brands": len(titles),
        "top_share": titles.most_common(1)[0][1] / n,
        "median_nm": statistics.median(o.distance_nm for o in shown),
    }
    for name, (w_image, w_interest, w_near) in PROFILES.items():
        summary[name] = statistics.fmean(
            w_image * IMAGE_VALUE.get(o.artwork_level, 0.0)
            + w_interest * o.interestingness
            + w_near * o.proximity
            for o in shown
        )
    return summary


HEADER = (
    f"{'weights':>12} {'value':>6} {'exact':>6} {'image':>6} {'cool':>6} "
    f"{'brands':>7} {'top':>5} {'median':>7} {'frames':>7}"
)


def line(w: Weights, s: dict, profile: str) -> str:
    return (
        f"{w.interestingness:.0f}/{w.proximity:.0f}/{w.artwork:.0f}".rjust(12)
        + f" {s[profile]:6.3f} {s['exact']:6.0%} {s['any_image']:6.0%} {s['notable']:6.0%}"
        + f" {s['brands']:7} {s['top_share']:5.0%} {s['median_nm']:6.1f}nm {s['frames']:7}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sweep scoring weights against cached traffic.")
    parser.add_argument("--step", type=int, default=5, help="weight grid step")
    parser.add_argument("--days", type=int, help="limit to the first N cached days")
    parser.add_argument(
        "--with-batches", action="store_true", help="include the planned batch C and D artwork"
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    cfg = config.load(config.default_path())
    keys = {p.stem for p in (cfg.assets_dir / "aircraft").glob("*.png")}
    if args.with_batches:
        keys |= set(BATCH_C) | set(BATCH_D)
    log.info("library: %d images", len(keys))

    started = time.monotonic()
    table = build_options(cfg, keys, args.days)
    log.info(
        "%d updates with traffic (%.0f s)",
        sum(1 for _, options in table if options),
        time.monotonic() - started,
    )

    grid = [
        Weights(i, p, a)
        for i, p, a in itertools.product(range(0, 101, args.step), repeat=3)
        if i + p + a == 100
    ]
    log.info("evaluating %d weight combinations", len(grid))
    results = [(w, evaluate(table, w, cfg)) for w in grid]
    results = [(w, s) for w, s in results if s]

    for profile in PROFILES:
        ranked = sorted(results, key=lambda r: -r[1][profile])
        print(f"\nbest 10 for '{profile}' ({PROFILES[profile]} on image/interest/near):")
        print(HEADER)
        for w, s in ranked[:10]:
            print(line(w, s, profile))

    print("\nreference points (value column: balanced):")
    print(HEADER)
    for w in (
        Weights(55, 30, 15),
        Weights(55, 30, 25),
        Weights(45, 30, 25),
        Weights(100, 0, 0),
        Weights(0, 100, 0),
        Weights(0, 0, 100),
    ):
        s = evaluate(table, w, cfg)
        print(line(w, s, "balanced"))

    print("\nbest by single metric:")
    for label, key in (
        ("most exact livery", "exact"),
        ("most frames with any image", "any_image"),
        ("most widebody/foreign/military", "notable"),
        ("most variety", "brands"),
        ("closest overhead", "median_nm"),
    ):
        w, s = (min if key == "median_nm" else max)(results, key=lambda r: r[1][key])
        print(f"  {label:32} " + line(w, s, "balanced").strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
