"""Write analysis results as CSV tables plus a Markdown report."""

from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from airframe.analysis import artwork, stats
from airframe.analysis.config import ARTWORK_LEVELS, AnalysisConfig
from airframe.analysis.encounters import Encounter
from airframe.analysis.livery import METHOD_LABELS, LiveryResolver
from airframe.analysis.sources import SLOTS_PER_DAY, DayExtract

ENCOUNTER_FIELDS = [
    "hex",
    "callsign",
    "registration",
    "type",
    "type_description",
    "family",
    "airline_icao",
    "airline_name",
    "operator",
    "brand",
    "brand_name",
    "brand_confidence",
    "brand_method",
    "brand_basis",
    "artwork_match",
    "artwork_level",
    "entered_utc",
    "closest_utc",
    "closest_nm",
    "altitude_ft",
    "airport_ops",
    "military",
    "interesting",
    "year",
]


def write(
    out_dir: Path,
    cfg: AnalysisConfig,
    extracts: list[DayExtract],
    missing_days: list[str],
    results: list[stats.RadiusResult],
    library: list[artwork.LibraryItem],
    resolver: LiveryResolver,
    stability: dict | None,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    days = sum(x.slots for x in extracts) / SLOTS_PER_DAY
    codes = [a.code for a in cfg.airports]
    keys = {item.artwork_key for item in library}
    levels = [
        {"radius_nm": r.radius_nm, **artwork.level_coverage(r.encounters, keys)} for r in results
    ]

    for r in results:
        tag = f"{r.radius_nm:g}nm"
        _write_csv(
            out_dir / f"encounters_{tag}.csv",
            [_encounter_row(e, keys) for e in r.encounters],
            ENCOUNTER_FIELDS,
        )
        tables = {
            "top_types": r.types,
            "top_airlines": r.airlines,
            "top_brands": r.brands,
            "top_combinations": r.combos,
            "combination_coverage": r.coverage,
            "rare_interesting": r.rare,
            "livery_confidence": r.confidence,
            "livery_methods": r.methods,
            "unresolved_registrations": r.unresolved,
        }
        for name, rows in tables.items():
            _write_csv(out_dir / f"{name}_{tag}.csv", rows)
    _write_csv(
        out_dir / "radius_comparison.csv",
        [{"radius_nm": r.radius_nm, **r.summary} for r in results],
    )
    rings = stats.ring_breakdown(results, codes, days)
    _write_csv(out_dir / "radius_rings.csv", rings)
    _write_csv(out_dir / "artwork_library.csv", [asdict(item) for item in library])
    _write_csv(out_dir / "artwork_level_coverage.csv", levels)
    _write_csv(out_dir / "livery_flight_blocks.csv", resolver.flight_blocks)

    primary = next(r for r in results if r.radius_nm == cfg.primary_radius_nm)
    sections = [
        _header(cfg, extracts, missing_days, days),
        _radius_section(results, primary, rings, levels, codes),
        _details_section(cfg, primary),
        _livery_section(cfg, primary, resolver),
        _library_section(cfg, results, primary, library, levels),
        _sensitivity_section(cfg, extracts, library, stability, resolver),
        _files_section(),
    ]
    path = out_dir / "report.md"
    path.write_text("\n".join(line for s in sections for line in s), encoding="utf-8")
    return path


def _header(cfg, extracts, missing_days, days) -> list[str]:
    incomplete = [
        f"{x.day} ({x.slots}/{SLOTS_PER_DAY})" for x in extracts if x.slots < SLOTS_PER_DAY
    ]
    lines = [
        f"# Traffic analysis: {cfg.location_name}",
        "",
        f"- **Center:** {cfg.lat:.4f}, {cfg.lon:.4f}",
        f"- **Dates (UTC):** {extracts[0].day} to {extracts[-1].day}: {len(extracts)} days, "
        f"{days:.1f} day-equivalents of data",
        f"- **Source:** adsb.lol heatmaps via `{cfg.source}` (10 s position snapshots)",
    ]
    if missing_days:
        lines.append(f"- **Unavailable days skipped:** {', '.join(missing_days)}")
    if incomplete:
        lines.append(f"- **Incomplete days:** {', '.join(incomplete)}")
    lines += [
        f"- **Generated:** {datetime.now(UTC):%Y-%m-%d %H:%M} UTC",
        "",
        "An *encounter* is one airborne pass of one aircraft through the radius. Repeat samples "
        f"less than {cfg.encounter_gap_s / 60:g} min apart are merged. *Airport ops* means that "
        f"within {cfg.airport_window_s / 60:g} min of the pass, the aircraft was on the ground or "
        f"below {cfg.airport_max_agl_ft:g} ft AGL within {cfg.airport_radius_nm:g} NM of that "
        "airport, i.e. it was landing or departing. *Airline* is the operating carrier from the "
        "callsign; *brand* is the estimated visible livery. Artwork keys are `<brand>_<TYPE>`, "
        "or `ANY_<TYPE>` when the brand is unresolved.",
        "",
    ]
    return lines


def _radius_section(results, primary, rings, levels, codes) -> list[str]:
    headers = [f"{r.radius_nm:g} NM" + (" (primary)" if r is primary else "") for r in results]
    return [
        "## Radius comparison",
        "",
        _table(["Metric", *headers], _comparison_rows(results, levels, codes)),
        "",
        "### What each ring adds",
        "",
        "Encounters whose closest approach falls in each distance band.",
        "",
        _table(
            ["Ring", "Encounters/day", "Airline share", "Median alt", "< 10,000 ft"]
            + [f"{c} ops" for c in codes],
            [
                [
                    row["ring"],
                    f"{row['encounters_per_day']:.1f}",
                    _pct(row["airline_share"]),
                    _ft(row["median_altitude_ft"]),
                    _pct(row["below_10000ft_share"]),
                    *[_pct(row[f"{c}_ops_share"]) for c in codes],
                ]
                for row in rings
            ],
        ),
        "",
        "### Top brand + type combinations by radius",
        "",
        _table(
            ["#", *headers],
            [
                [i + 1, *[_combo_cell(r.combos, i) for r in results]]
                for i in range(min(15, max(len(r.combos) for r in results)))
            ],
        ),
        "",
    ]


def _comparison_rows(results, levels, codes) -> list[list[str]]:
    metrics = [
        ("Encounters", "encounters", _int),
        ("Encounters per day", "encounters_per_day", lambda v: f"{v:.1f}"),
        ("Unique aircraft (ICAO hex)", "unique_aircraft", _int),
        ("Unique registrations", "unique_registrations", _int),
        ("Unique aircraft types", "unique_types", _int),
        ("Unique airlines (operating carriers)", "unique_airlines", _int),
        ("Unique livery brands", "unique_brands", _int),
        ("Airline-callsign share", "airline_share", _pct),
        ("Median altitude at closest approach", "median_altitude_ft", _ft),
        ("Below 10,000 ft at closest approach", "below_10000ft_share", _pct),
        *[(f"{c} arrivals/departures", f"{c}_ops_share", _pct) for c in codes],
        ("Military share", "military_share", _pct),
        ("Brand from registration", "brand_registration_share", _pct),
        ("Brand inferred", "brand_inferred_share", _pct),
        ("Brand unresolved", "brand_unresolved_share", _pct),
        ("Top-20 brand+type coverage", "top20_coverage", _pct),
        ("Top-50 brand+type coverage", "top50_coverage", _pct),
        ("Brand+type combinations for 80%", "combos_for_80pct", _int),
    ]
    rows = [[label, *[fmt(r.summary.get(key)) for r in results]] for label, key, fmt in metrics]
    rows.append(["Recommended library: any match", *[_pct(1 - lv["none"]) for lv in levels]])
    rows.append(
        ["Recommended library: brand + subtype", *[_pct(lv["brand_type"]) for lv in levels]]
    )
    return rows


def _details_section(cfg, primary) -> list[str]:
    s = primary.summary
    return [
        f"## {cfg.primary_radius_nm:g} NM details",
        "",
        "### Top aircraft types",
        "",
        _table(
            ["#", "Type", "Description", "Family", "Encounters", "Share", "Aircraft"],
            [
                [
                    t["rank"],
                    t["type"],
                    t["description"],
                    t["family"],
                    t["encounters"],
                    _pct(t["share"]),
                    t["unique_aircraft"],
                ]
                for t in primary.types[: cfg.top_n]
            ],
        ),
        "",
        "### Top operating airlines",
        "",
        f"Airline callsigns account for {_pct(s['airline_share'])} of encounters. This is the "
        "operating carrier (e.g. SkyWest); the livery brands it flies are listed alongside.",
        "",
        _table(
            ["#", "ICAO", "Airline", "Encounters", "Share", "Aircraft", "Main types", "Brands"],
            [
                [
                    a["rank"],
                    a["airline_icao"],
                    a["airline_name"],
                    a["encounters"],
                    _pct(a["share"]),
                    a["unique_aircraft"],
                    a["top_types"],
                    a["brands"],
                ]
                for a in primary.airlines[: cfg.top_n]
            ],
        ),
        "",
        "### Top livery brands",
        "",
        _table(
            ["#", "Brand", "Encounters", "Share", "From registration", "Operators", "Main types"],
            [
                [
                    b["rank"],
                    b["brand_name"],
                    b["encounters"],
                    _pct(b["share"]),
                    _pct(b["registration_share"]),
                    b["operators"],
                    b["top_types"],
                ]
                for b in primary.brands[: cfg.top_n]
            ],
        ),
        "",
        "### Top brand + aircraft-type combinations",
        "",
        _table(
            ["#", "Artwork key", "Type", "Encounters", "Share", "Cumulative", "Days", "Operators"],
            [
                [
                    c["rank"],
                    f"`{c['artwork_key']}`",
                    c["description"] or c["type"],
                    c["encounters"],
                    _pct(c["share"]),
                    _pct(c["cumulative_share"]),
                    c["days_seen"],
                    c["operators"],
                ]
                for c in primary.combos[: cfg.top_n]
            ],
        ),
        "",
        "Exact-combination coverage (no fallbacks): "
        + ", ".join(f"top {c['top_n']} {_pct(c['share_of_all'])}" for c in primary.coverage)
        + f". {_pct(s['unknown_type_share'])} of encounters have no known aircraft type.",
        "",
        "### Rare / interesting combinations",
        "",
        f"Combinations ranked below #{cfg.rare_outside_top} that are military, flagged "
        "interesting in the aircraft DB, widebody/heavy, vintage (built "
        f"{stats.VINTAGE_MAX_YEAR} or earlier), or flown by a non-{cfg.home_country or 'home'} "
        "airline.",
        "",
        _table(
            ["Artwork key", "Aircraft", "Encounters", "Days", "Examples", "Why"],
            [
                [
                    f"`{r['artwork_key']}`",
                    r["description"] or r["type"],
                    r["encounters"],
                    r["days_seen"],
                    r["example_registrations"],
                    r["reasons"],
                ]
                for r in primary.rare[:30]
            ],
        )
        if primary.rare
        else "_None found._",
        "",
    ]


def _livery_section(cfg, primary, resolver) -> list[str]:
    lines = [
        f"## Livery resolution ({cfg.primary_radius_nm:g} NM)",
        "",
        "- **registration:** tied to the airframe. Sources are `livery_registrations.csv`, the "
        "aircraft DB military flag, or a registered owner that matches one of the operator's "
        "brands (e.g. a Delta-owned CRJ-900 flown by SkyWest).",
        "- **inferred:** from the flight. Sources are an operator that flies for one brand only, "
        "a flight-number block flown only by owner-confirmed aircraft of one brand, a plausible "
        "route touching one candidate brand's hub, or other flights of the same registration.",
        "- **unresolved:** no evidence, or conflicting evidence. Nothing is guessed.",
        "",
        _table(
            ["Confidence", "Encounters", "Share of all", "Share of airline-callsign encounters"],
            [
                [
                    c["confidence"],
                    c["encounters"],
                    _pct(c["share"]),
                    _pct(c["airline_callsign_share"]),
                ]
                for c in primary.confidence
            ],
        ),
        "",
        _table(
            ["Confidence", "Evidence", "Encounters", "Share"],
            [
                [
                    m["confidence"],
                    METHOD_LABELS.get(m["method"], m["method"]),
                    m["encounters"],
                    _pct(m["share"]),
                ]
                for m in primary.methods
            ],
        ),
        "",
        "### Flight-number blocks learned this run",
        "",
        f"A block is used when at least {cfg.flight_block_min_support} owner-confirmed "
        f"encounters agree at {cfg.flight_block_min_purity:.0%} purity (all radii combined).",
        "",
    ]
    lines.append(
        _table(
            [
                "Operator",
                "Block",
                "Majority brand",
                "Confirmed encounters",
                "Purity",
                "Used",
                "All",
            ],
            [
                [
                    b["operator_icao"],
                    b["block"],
                    b["brand"],
                    b["confirmed_encounters"],
                    _pct(b["purity"]),
                    "yes" if b["used"] else "no",
                    b["all_brands"],
                ]
                for b in resolver.flight_blocks
            ],
        )
        if resolver.flight_blocks
        else "_No multi-brand operators with owner-confirmed aircraft._"
    )
    lines += [
        "",
        "### Most common unresolved registrations",
        "",
        "Only aircraft with airline callsigns are listed. Once a livery is verified, add it to "
        "`data/reference/livery_registrations.csv`; add missing operators to "
        "`operator_brands.csv`.",
        "",
        _table(
            [
                "#",
                "Registration",
                "Operator",
                "Type",
                "Registered owner",
                "Encounters",
                "Days",
                "Why unresolved",
            ],
            [
                [
                    u["rank"],
                    u["registration"],
                    u["operators"],
                    u["type"],
                    u["owner"],
                    u["encounters"],
                    u["days_seen"],
                    METHOD_LABELS.get(u["reason"], u["reason"]),
                ]
                for u in primary.unresolved[:25]
            ],
        )
        if primary.unresolved
        else "_None._",
        "",
    ]
    return lines


def _library_section(cfg, results, primary, library, levels) -> list[str]:
    lib = cfg.library
    w = lib.weights
    by_source = {s: [i for i in library if i.source == s] for s in ("coverage", "required", "hero")}
    brand_images = sum(1 for i in library if i.level.startswith("brand"))
    missing = [k for k in lib.always_include if k not in {i.artwork_key for i in library}]
    headers = [f"{r.radius_nm:g} NM" for r in results]
    level_rows = [
        [artwork.LEVEL_LABELS[level], *[_pct(lv[level]) for lv in levels]]
        for level in ARTWORK_LEVELS
    ]
    level_rows += [
        ["no match", *[_pct(lv["none"]) for lv in levels]],
        [
            "(brand levels, registration-confirmed brand)",
            *[_pct(lv["brand_level_registration"]) for lv in levels],
        ],
        ["(brand levels, inferred brand)", *[_pct(lv["brand_level_inferred"]) for lv in levels]],
    ]
    lines = [
        f"## Recommended artwork library ({cfg.primary_radius_nm:g} NM)",
        "",
        f"{len(library)} images: {brand_images} brand-specific and "
        f"{len(library) - brand_images} generic. By source: {len(by_source['coverage'])} ranked "
        f"by coverage, {len(by_source['required'])} required fallbacks, "
        f"{len(by_source['hero'])} hero images.",
        "",
        "Each frame shows the most specific image available: brand + subtype, then brand + "
        "family, then generic subtype, then generic family. Coverage images are added greedily "
        "by *marginal weighted coverage*: each encounter scores the weight of its best match "
        f"(brand + subtype {w['brand_type']:g}, brand + family {w['brand_family']:g}, generic "
        f"subtype {w['generic_type']:g}, generic family {w['generic_family']:g}). Adding stops "
        f"when the best image adds under {lib.min_marginal_share:.1%}, once at least "
        f"{lib.brand_min} brand images are in (limits: {lib.brand_max} brand, "
        f"{lib.generic_max} generic). Hero images are widebody, foreign or military aircraft "
        f"seen on at least {lib.hero_min_days} days.",
        "",
        "### Coverage by fallback level",
        "",
        _table(["Level", *headers], level_rows),
        "",
        "### Library",
        "",
        "*Covered* counts encounters that would display that image with the full library. "
        "*Marginal* is the weighted-coverage gain when the image was added.",
        "",
        _table(
            [
                "#",
                "Artwork key",
                "Level",
                "Covered",
                "Marginal",
                "New",
                "Upgraded",
                "Cumulative match",
                "Cumulative weighted",
                "Days",
                "Reason",
            ],
            [
                [
                    i.rank,
                    f"`{i.artwork_key}`",
                    artwork.LEVEL_LABELS[i.level],
                    i.encounters_covered,
                    _pct(i.marginal_coverage_added),
                    i.newly_matched,
                    i.upgraded,
                    _pct(i.cumulative_match_share),
                    _pct(i.cumulative_weighted_coverage),
                    i.days_seen,
                    i.reason,
                ]
                for i in library
            ],
        ),
        "",
    ]
    if missing:
        lines += [f"Required fallbacks not observed in this data: {', '.join(missing)}.", ""]
    return lines


def _sensitivity_section(cfg, extracts, library, stability, resolver) -> list[str]:
    n_days = len(extracts)
    few_days = [
        i.artwork_key for i in library if i.source == "coverage" and i.days_seen <= n_days // 2
    ]
    blocks = [b for b in resolver.flight_blocks if b["used"]]
    lines = ["## Sensitivity to the sample period", ""]
    if stability:
        top = stability["top20_shared"]
        verdict = (
            "The top of the list is stable; most differences are in the tail."
            if top >= 16
            else "Even the top of the list shifts between halves; gather more days first."
        )
        lines.append(
            f"- **Split-half check:** libraries built separately from alternating days "
            f"({stability['days_a']} vs {stability['days_b']}) share {stability['shared']} of "
            f"{stability['union']} coverage-ranked images, including {top} of their top 20. The "
            f"first half's library reaches {_pct(stability['a_on_b_weighted'])} weighted "
            f"coverage ({_pct(stability['a_on_b_matched'])} any match) on the second half's "
            f"traffic, vs {_pct(stability['b_on_b_weighted'])} "
            f"({_pct(stability['b_on_b_matched'])}) for a library built on the second half "
            f"itself. {verdict}"
        )
    if few_days:
        days_note = (
            f"{len(few_days)} coverage-ranked images were seen on {n_days // 2} or fewer of "
            f"{n_days} days ({', '.join(few_days)}). Their ranks could change a lot with more data."
        )
    else:
        days_note = (
            f"every coverage-ranked image was seen on more than {n_days // 2} of {n_days} days, "
            f"but images near the {cfg.library.min_marginal_share:.1%} marginal cutoff can swap "
            "in or out with more data."
        )
    lines += [
        f"- **Days seen:** {days_note}",
        f"- **Hero images** qualify on days seen (at least {cfg.library.hero_min_days}), not "
        "volume. A different week could add or drop several.",
        f"- **Flight-number rules** ({len(blocks)} used) are learned from this period's "
        "owner-confirmed aircraft. Airlines reshuffle flight numbers at schedule changes, so "
        "relearn them every run rather than hard-coding them.",
        "- **Weekday mix:** one week has each weekday once. Business-jet and flight-school "
        "traffic varies strongly by weekday and weather.",
        "- **Season:** schedules change at the IATA season change (late October) and around "
        "holidays, and GA flying drops in winter.",
        "- **Runway flow:** wind direction decides which DTW arrival and departure paths cross "
        "the circle. A week dominated by one flow skews the DTW share and the regional-jet mix.",
        "- **Route data** used for inference reflects today's schedule, not the sample period.",
        "- **Rare aircraft** (military, charters, one-off widebodies) are the noisiest. One week "
        "can't separate regular visitors from one-offs, so rerun with more days before "
        "commissioning hero art.",
        "",
    ]
    return lines


def _files_section() -> list[str]:
    return [
        "## Files",
        "",
        "- Per radius: `encounters_`, `top_types_`, `top_airlines_`, `top_brands_`, "
        "`top_combinations_`, `combination_coverage_`, `rare_interesting_`, "
        "`livery_confidence_`, `livery_methods_`, `unresolved_registrations_`.",
        "- Library: `artwork_library.csv`, `artwork_level_coverage.csv`.",
        "- Livery: `livery_flight_blocks.csv`.",
        "- Radius: `radius_comparison.csv`, `radius_rings.csv`.",
        "",
    ]


def _combo_cell(combos: list[dict], i: int) -> str:
    return f"`{combos[i]['artwork_key']}` {_pct(combos[i]['share'])}" if i < len(combos) else ""


def _encounter_row(e: Encounter, library_keys: set[str]) -> dict:
    match, level = artwork.best_match(e, library_keys)
    return {
        "hex": e.hex,
        "callsign": e.callsign,
        "registration": e.registration,
        "type": e.type_code,
        "type_description": e.type_description,
        "family": e.family,
        "airline_icao": e.airline_icao,
        "airline_name": e.airline_name,
        "operator": e.operator,
        "brand": e.brand,
        "brand_name": e.brand_name,
        "brand_confidence": e.brand_confidence,
        "brand_method": e.brand_method,
        "brand_basis": e.brand_basis,
        "artwork_match": match,
        "artwork_level": level,
        "entered_utc": e.entered_utc.isoformat(timespec="seconds"),
        "closest_utc": e.closest_utc.isoformat(timespec="seconds"),
        "closest_nm": round(e.closest_nm, 2),
        "altitude_ft": e.altitude_ft if e.altitude_ft is not None else "",
        "airport_ops": "|".join(e.airport_ops),
        "military": int(e.military),
        "interesting": int(e.interesting),
        "year": e.year or "",
    }


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    fieldnames = fieldnames or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: round(v, 4) if isinstance(v, float) else v for k, v in row.items()})


def _table(headers: list[str], rows: list[list]) -> str:
    def cell(value) -> str:
        return str(value).replace("|", "\\|")

    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
    return "\n".join(lines)


def _pct(value) -> str:
    return "–" if value is None else f"{value:.1%}"


def _int(value) -> str:
    return "–" if value is None else f"{value:,}"


def _ft(value) -> str:
    return "–" if value is None else f"{value:,.0f} ft"
