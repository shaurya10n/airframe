"""Command line entry point: ``python -m airframe.analysis`` / ``airframe-analyze``."""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

from airframe.analysis import (
    artwork,
    config,
    encounters,
    heatmap,
    livery,
    reference,
    report,
    sources,
    stats,
)
from airframe.analysis.routes import RouteLookup

log = logging.getLogger("airframe.analysis")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="airframe-analyze",
        description="Analyze adsb.lol historical traffic around a location.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="TOML config (default: config/analysis.toml, "
        "falling back to config/analysis.example.toml)",
    )
    parser.add_argument("--dates", help="comma-separated UTC dates, e.g. 2026-09-01,2026-09-02")
    parser.add_argument("--days", type=int, help="analyze the N most recent complete UTC days")
    parser.add_argument("--end", help="last UTC date for --days (default: yesterday)")
    parser.add_argument("--source", choices=config.SOURCES, help="where to fetch heatmaps from")
    parser.add_argument(
        "--out", type=Path, help="output directory (default: data/analysis/<first>_<last>)"
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    try:
        cfg = config.load(
            args.config or config.default_path(),
            dates=args.dates.split(",") if args.dates else None,
            days=args.days,
            end=args.end,
            source=args.source,
        )
        tables = livery.LiveryTables.load(cfg.reference_dir)
        families = artwork.Families.load(cfg.reference_dir / "aircraft_families.csv")
    except (OSError, KeyError, ValueError) as exc:
        parser.error(str(exc))

    session = sources.make_session(pool_size=max(16, cfg.concurrency))
    extracts, missing = [], []
    for day in cfg.dates:
        try:
            extracts.append(sources.load_day(day, cfg, session))
        except sources.DayUnavailable as exc:
            log.warning("%s", exc)
            missing.append(day.isoformat())
    if not extracts:
        log.error("no data for any requested day")
        return 1

    positions = np.concatenate([x.positions for x in extracts])
    callsigns = encounters.CallsignIndex(np.concatenate([x.callsigns for x in extracts]))
    days = sum(x.slots for x in extracts) / sources.SLOTS_PER_DAY

    ref_dir = cfg.data_dir / "cache" / "reference"
    hexes = {heatmap.addr_to_hex(int(a)) for a in np.unique(positions["addr"])}
    aircraft = reference.load_aircraft(ref_dir, hexes, session)
    operators = reference.load_operators(ref_dir, session)

    airport_ops = encounters.AirportOps(
        positions, cfg.airports, cfg.airport_radius_nm, cfg.airport_max_agl_ft
    )
    tracked = positions if cfg.include_ground else positions[~positions["ground"]]
    points = encounters.closest_points(tracked, cfg.lat, cfg.lon, cfg.max_segment_gap_s)
    by_radius = {
        radius: encounters.enrich(
            encounters.find_passes(points, radius, cfg.encounter_gap_s),
            callsigns,
            aircraft,
            operators,
            airport_ops,
            cfg.airport_window_s,
        )
        for radius in cfg.radii_nm
    }

    routes = (
        RouteLookup(cfg.data_dir / "cache" / "routes.json", session, cfg.concurrency)
        if cfg.use_routes
        else None
    )
    resolver = livery.LiveryResolver(
        tables,
        lat=cfg.lat,
        lon=cfg.lon,
        routes=routes,
        block_min_support=cfg.flight_block_min_support,
        block_min_purity=cfg.flight_block_min_purity,
        route_max_offset_nm=cfg.route_max_offset_nm,
    )
    resolver.learn(by_radius[cfg.radii_nm[-1]])  # the largest radius sees every aircraft

    results = []
    for radius, encs in by_radius.items():
        annotated = [
            replace(e, **resolver.fields(e), family=families.family(e.type_code)) for e in encs
        ]
        results.append(stats.analyze(annotated, radius, cfg, days))

    primary = next(r for r in results if r.radius_nm == cfg.primary_radius_nm)
    library = artwork.build_library(primary.encounters, cfg.library, cfg.home_country)
    stability = artwork.split_half_stability(primary.encounters, cfg.library, cfg.home_country)

    out_dir = args.out or cfg.data_dir / "analysis" / f"{extracts[0].day}_{extracts[-1].day}"
    path = report.write(out_dir, cfg, extracts, missing, results, library, resolver, stability)

    for r in results:
        s = r.summary
        ops = ", ".join(f"{a.code} ops {s[f'{a.code}_ops_share']:.0%}" for a in cfg.airports)
        print(
            f"{r.radius_nm:>4g} NM: {s['encounters']:,} encounters "
            f"({s['encounters_per_day']:.0f}/day), {s['unique_registrations']:,} registrations, "
            f"{s['unique_types']} types, {ops}"
        )
    conf = {row["confidence"]: row["share"] for row in primary.confidence}
    levels = artwork.level_coverage(primary.encounters, {i.artwork_key for i in library})
    print(
        f"Livery at {cfg.primary_radius_nm:g} NM: registration {conf['registration']:.1%}, "
        f"inferred {conf['inferred']:.1%}, unresolved {conf['unresolved']:.1%}"
    )
    print(
        f"Library: {len(library)} images; brand+subtype {levels['brand_type']:.1%}, "
        f"brand+family {levels['brand_family']:.1%}, generic subtype {levels['generic_type']:.1%}, "
        f"generic family {levels['generic_family']:.1%}, no match {levels['none']:.1%}"
    )
    print(f"Report: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
