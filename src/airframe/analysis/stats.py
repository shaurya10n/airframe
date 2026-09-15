"""Aggregate encounters into the tables used to plan artwork and sanity-check the radius."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from statistics import median

from airframe.analysis.config import AnalysisConfig
from airframe.analysis.encounters import Encounter
from airframe.analysis.livery import CONFIDENCES, REGISTRATION, UNRESOLVED

GENERIC = "ANY"
VINTAGE_MAX_YEAR = 1955
WIDEBODY_TYPES = frozenset(
    """
    A306 A30B A310 A332 A333 A338 A339 A342 A343 A345 A346 A359 A35K A388 A3ST A124 A225
    B741 B742 B743 B744 B748 B74S B762 B763 B764 B772 B77L B773 B77W B778 B779 B788 B789
    B78X BLCF BSCA C5M C17 DC10 E3TF E6 IL76 IL96 K35R KC10 KC46 L101 MD11 VC25
    """.split()
)


@dataclass
class RadiusResult:
    radius_nm: float
    encounters: list[Encounter]
    summary: dict = field(default_factory=dict)
    types: list[dict] = field(default_factory=list)
    airlines: list[dict] = field(default_factory=list)
    brands: list[dict] = field(default_factory=list)
    combos: list[dict] = field(default_factory=list)
    coverage: list[dict] = field(default_factory=list)
    rare: list[dict] = field(default_factory=list)
    confidence: list[dict] = field(default_factory=list)
    methods: list[dict] = field(default_factory=list)
    unresolved: list[dict] = field(default_factory=list)


def artwork_key(e: Encounter) -> str | None:
    """Exact artwork key: ``<brand>_<TYPE>``, or ``ANY_<TYPE>`` when the brand is unresolved."""
    if not e.type_code:
        return None
    return f"{e.brand or GENERIC}_{e.type_code}"


def analyze(
    encounters: list[Encounter], radius_nm: float, cfg: AnalysisConfig, days: float
) -> RadiusResult:
    result = RadiusResult(radius_nm, encounters)
    result.types = top_types(encounters)
    result.airlines = top_airlines(encounters)
    result.brands = top_brands(encounters)
    result.combos = top_combos(encounters)
    result.coverage = coverage(result.combos, encounters, cfg.coverage_levels)
    result.rare = rare_interesting(
        encounters, cfg.rare_outside_top, cfg.rare_type_share, cfg.home_country
    )
    result.confidence = brand_confidence(encounters)
    result.methods = brand_methods(encounters)
    result.unresolved = unresolved_registrations(encounters)
    result.summary = summarize(encounters, result.combos, [a.code for a in cfg.airports], days)
    for row in result.coverage:
        result.summary[f"top{row['top_n']}_coverage"] = row["share_of_all"]
    return result


def top_types(encounters: list[Encounter]) -> list[dict]:
    total = len(encounters)
    return [
        {
            "rank": rank,
            "type": type_code,
            "description": _most_common(e.type_description for e in group),
            "family": group[0].family,
            "encounters": len(group),
            "share": _share(len(group), total),
            "unique_aircraft": len({e.hex for e in group}),
        }
        for rank, (type_code, group) in enumerate(
            _group(encounters, lambda e: e.type_code or None), 1
        )
    ]


def top_airlines(encounters: list[Encounter]) -> list[dict]:
    """Operating carriers from the callsign (not necessarily the livery)."""
    total = len(encounters)
    return [
        {
            "rank": rank,
            "airline_icao": code,
            "airline_name": group[0].airline_name,
            "country": group[0].airline_country,
            "encounters": len(group),
            "share": _share(len(group), total),
            "unique_aircraft": len({e.hex for e in group}),
            "top_types": _top(e.type_code for e in group),
            "brands": _top(e.brand or "(unresolved)" for e in group),
        }
        for rank, (code, group) in enumerate(
            _group(encounters, lambda e: e.airline_icao or None), 1
        )
    ]


def top_brands(encounters: list[Encounter]) -> list[dict]:
    """Visible livery brands (registration-confirmed or inferred)."""
    total = len(encounters)
    return [
        {
            "rank": rank,
            "brand": brand,
            "brand_name": group[0].brand_name,
            "encounters": len(group),
            "share": _share(len(group), total),
            "registration_share": _share(
                sum(1 for e in group if e.brand_confidence == REGISTRATION), len(group)
            ),
            "unique_aircraft": len({e.hex for e in group}),
            "operators": _top(e.airline_icao for e in group),
            "top_types": _top(e.type_code for e in group),
        }
        for rank, (brand, group) in enumerate(_group(encounters, lambda e: e.brand or None), 1)
    ]


def top_combos(encounters: list[Encounter]) -> list[dict]:
    total = len(encounters)
    rows, cumulative = [], 0
    for rank, (key, group) in enumerate(_group(encounters, artwork_key), 1):
        cumulative += len(group)
        rows.append(
            {
                "rank": rank,
                "artwork_key": key,
                "brand": group[0].brand or GENERIC,
                "brand_name": group[0].brand_name,
                "type": group[0].type_code,
                "description": _most_common(e.type_description for e in group),
                "encounters": len(group),
                "share": _share(len(group), total),
                "cumulative_share": _share(cumulative, total),
                "unique_aircraft": len({e.hex for e in group}),
                "days_seen": len({e.closest_utc.date() for e in group}),
                "operators": _top(e.airline_icao for e in group),
            }
        )
    return rows


def coverage(combos: list[dict], encounters: list[Encounter], levels: Iterable[int]) -> list[dict]:
    """Share of encounters that would get exact artwork if the top-N combinations existed."""
    total = len(encounters)
    typed = sum(1 for e in encounters if e.type_code)
    rows = []
    for n in levels:
        covered = sum(row["encounters"] for row in combos[:n])
        rows.append(
            {
                "top_n": n,
                "combinations": min(n, len(combos)),
                "encounters_covered": covered,
                "share_of_all": _share(covered, total),
                "share_of_known_type": _share(covered, typed),
            }
        )
    return rows


def combos_needed(combos: list[dict], target_share: float) -> int | None:
    for row in combos:
        if row["cumulative_share"] >= target_share:
            return row["rank"]
    return None


def rare_interesting(
    encounters: list[Encounter], outside_top: int, rare_type_share: float, home_country: str
) -> list[dict]:
    """Combinations below the coverage set that are notable enough to deserve artwork anyway."""
    total = len(encounters)
    type_counts = Counter(e.type_code for e in encounters if e.type_code)
    rows = []
    for rank, (key, group) in enumerate(_group(encounters, artwork_key), 1):
        if rank <= outside_top:
            continue
        first = group[0]
        reasons = []
        if any(e.military for e in group):
            reasons.append("military")
        if any(e.interesting for e in group):
            reasons.append("flagged interesting")
        if first.type_code in WIDEBODY_TYPES:
            reasons.append("widebody/heavy")
        years = [e.year for e in group if e.year]
        if years and min(years) <= VINTAGE_MAX_YEAR:
            reasons.append(f"vintage (built {min(years)})")
        country = first.brand_country or first.airline_country
        if country and home_country and country != home_country:
            reasons.append(f"foreign airline ({country})")
        if not reasons:
            continue
        if type_counts[first.type_code] <= rare_type_share * total:
            reasons.append("rare type")
        rows.append(
            {
                "artwork_key": key,
                "brand": first.brand or GENERIC,
                "brand_name": first.brand_name,
                "type": first.type_code,
                "description": _most_common(e.type_description for e in group),
                "encounters": len(group),
                "unique_aircraft": len({e.hex for e in group}),
                "days_seen": len({e.closest_utc.date() for e in group}),
                "combo_rank": rank,
                "example_registrations": ", ".join(
                    sorted({e.registration for e in group if e.registration})[:3]
                ),
                "reasons": "; ".join(reasons),
            }
        )
    rows.sort(key=lambda r: (-r["reasons"].count(";"), -r["encounters"], r["artwork_key"]))
    return rows


def brand_confidence(encounters: list[Encounter]) -> list[dict]:
    airline = [e for e in encounters if e.airline_icao]
    everyone = Counter(e.brand_confidence for e in encounters)
    with_callsign = Counter(e.brand_confidence for e in airline)
    return [
        {
            "confidence": c,
            "encounters": everyone[c],
            "share": _share(everyone[c], len(encounters)),
            "airline_callsign_encounters": with_callsign[c],
            "airline_callsign_share": _share(with_callsign[c], len(airline)),
        }
        for c in CONFIDENCES
    ]


def brand_methods(encounters: list[Encounter]) -> list[dict]:
    counts = Counter((e.brand_confidence, e.brand_method) for e in encounters)
    return [
        {"confidence": c, "method": m, "encounters": n, "share": _share(n, len(encounters))}
        for (c, m), n in sorted(
            counts.items(), key=lambda kv: (CONFIDENCES.index(kv[0][0]), -kv[1])
        )
    ]


def unresolved_registrations(encounters: list[Encounter]) -> list[dict]:
    """Airline-callsign aircraft whose livery couldn't be determined, most frequent first."""
    unresolved = [e for e in encounters if e.brand_confidence == UNRESOLVED and e.airline_icao]
    return [
        {
            "rank": rank,
            "registration": registration,
            "hex": group[0].hex,
            "operators": _top(e.airline_icao for e in group),
            "type": _most_common(e.type_code for e in group),
            "owner": _most_common(e.operator for e in group),
            "encounters": len(group),
            "days_seen": len({e.closest_utc.date() for e in group}),
            "reason": _most_common(e.brand_method for e in group),
            "detail": group[0].brand_basis,
        }
        for rank, (registration, group) in enumerate(
            _group(unresolved, lambda e: e.registration or f"(hex {e.hex})"), 1
        )
    ]


def summarize(
    encounters: list[Encounter], combos: list[dict], airport_codes: list[str], days: float
) -> dict:
    n = len(encounters)
    alts = [e.altitude_ft for e in encounters if e.altitude_ft is not None]
    confidence = Counter(e.brand_confidence for e in encounters)
    summary = {
        "encounters": n,
        "encounters_per_day": n / days if days else 0.0,
        "unique_aircraft": len({e.hex for e in encounters}),
        "unique_registrations": len({e.registration for e in encounters if e.registration}),
        "unique_types": len({e.type_code for e in encounters if e.type_code}),
        "unique_airlines": len({e.airline_icao for e in encounters if e.airline_icao}),
        "unique_brands": len({e.brand for e in encounters if e.brand}),
        "airline_share": _share(sum(1 for e in encounters if e.airline_icao), n),
        "unknown_type_share": _share(sum(1 for e in encounters if not e.type_code), n),
        "military_share": _share(sum(1 for e in encounters if e.military), n),
        "brand_registration_share": _share(confidence["registration"], n),
        "brand_inferred_share": _share(confidence["inferred"], n),
        "brand_unresolved_share": _share(confidence["unresolved"], n),
        "median_altitude_ft": median(alts) if alts else None,
        "below_10000ft_share": _share(sum(1 for a in alts if a < 10_000), len(alts)),
    }
    for code in airport_codes:
        summary[f"{code}_ops_share"] = _share(
            sum(1 for e in encounters if code in e.airport_ops), n
        )
    for pct in (50, 80, 90):
        summary[f"combos_for_{pct}pct"] = combos_needed(combos, pct / 100)
    return summary


def ring_breakdown(
    results: list[RadiusResult], airport_codes: list[str], days: float
) -> list[dict]:
    """Stats for the band each radius adds beyond the previous one (e.g. 10-15 NM)."""
    rows, inner = [], 0.0
    for result in sorted(results, key=lambda r: r.radius_nm):
        ring = [e for e in result.encounters if e.closest_nm > inner]
        summary = summarize(ring, [], airport_codes, days)
        rows.append({"ring": f"{inner:g}-{result.radius_nm:g} NM", **summary})
        inner = result.radius_nm
    return rows


def _group(
    encounters: list[Encounter], key: Callable[[Encounter], str | None]
) -> list[tuple[str, list[Encounter]]]:
    groups: dict[str, list[Encounter]] = defaultdict(list)
    for e in encounters:
        k = key(e)
        if k is not None:
            groups[k].append(e)
    return sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))


def _top(values: Iterable[str], n: int = 3) -> str:
    return ", ".join(v for v, _ in Counter(v for v in values if v).most_common(n))


def _most_common(values: Iterable[str]) -> str:
    counts = Counter(v for v in values if v)
    return counts.most_common(1)[0][0] if counts else ""


def _share(part: float, whole: float) -> float:
    return part / whole if whole else 0.0
