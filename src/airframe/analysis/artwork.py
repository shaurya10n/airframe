"""Artwork keys, the fallback hierarchy, and a recommended starting library.

For each encounter the frame would show the most specific image in the library:

1. ``<brand>_<TYPE>``    brand + exact subtype    e.g. ``delta-connection_CRJ9``
2. ``<brand>_<FAMILY>``  brand + aircraft family  e.g. ``delta-connection_CRJ-FAM``
3. ``ANY_<TYPE>``        generic subtype          e.g. ``ANY_C172``
4. ``ANY_<FAMILY>``      generic family           e.g. ``ANY_GA-HIGHWING``

Brands come from livery.py; unresolved encounters start at level 3. Families come from
``data/reference/aircraft_families.csv``.

The library is built greedily. Each step adds the image with the largest gain in *weighted
coverage*, where an encounter scores the weight of the best level it matches (config
``library.weights``). A brand-specific image that upgrades encounters from a generic
fallback therefore still counts as progress.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from airframe.analysis.config import ARTWORK_LEVELS, LibraryConfig
from airframe.analysis.encounters import Encounter
from airframe.analysis.livery import read_reference_csv
from airframe.analysis.stats import WIDEBODY_TYPES

GENERIC = "ANY"
BRAND_LEVELS = ("brand_type", "brand_family")
LEVEL_LABELS = {
    "brand_type": "brand + subtype",
    "brand_family": "brand + family",
    "generic_type": "generic subtype",
    "generic_family": "generic family",
}


@dataclass(frozen=True)
class Families:
    by_type: dict[str, str]
    names: dict[str, str]

    @classmethod
    def load(cls, path: Path) -> Families:
        by_type: dict[str, str] = {}
        names: dict[str, str] = {}
        for row in read_reference_csv(path):
            type_code, family = row["type"].upper(), row["family"]
            if type_code in by_type:
                raise ValueError(f"{path.name}: type {type_code} is listed twice")
            by_type[type_code] = family
            names.setdefault(family, row.get("family_name") or family)
        clashes = sorted(set(names) & set(by_type))
        if clashes:
            raise ValueError(f"{path.name}: family codes must not reuse type codes: {clashes}")
        return cls(by_type, names)

    def family(self, type_code: str) -> str:
        return self.by_type.get(type_code, "")


@dataclass
class LibraryItem:
    rank: int
    artwork_key: str
    level: str
    source: str  # coverage | required | hero
    encounters_covered: int  # encounters that would show this image, given the full library
    marginal_coverage_added: float  # weighted-coverage gain when the image was added
    newly_matched: int
    upgraded: int
    cumulative_match_share: float
    cumulative_weighted_coverage: float
    days_seen: int
    reason: str


def candidate_keys(e: Encounter) -> list[tuple[str, str]]:
    """(artwork key, level) pairs that could depict an encounter, most specific first."""
    keys = []
    if e.brand and e.type_code:
        keys.append((f"{e.brand}_{e.type_code}", "brand_type"))
    if e.brand and e.family:
        keys.append((f"{e.brand}_{e.family}", "brand_family"))
    if e.type_code:
        keys.append((f"{GENERIC}_{e.type_code}", "generic_type"))
    if e.family:
        keys.append((f"{GENERIC}_{e.family}", "generic_family"))
    return keys


def best_match(e: Encounter, library_keys: set[str]) -> tuple[str, str]:
    """(key, level) of the image the frame would show, or ("", "") without a match."""
    for key, level in candidate_keys(e):
        if key in library_keys:
            return key, level
    return "", ""


def level_coverage(encounters: list[Encounter], library_keys: set[str]) -> dict:
    """Share of encounters matched at each fallback level (plus ``none``)."""
    levels: Counter = Counter()
    brand_confidence: Counter = Counter()
    for e in encounters:
        level = best_match(e, library_keys)[1] or "none"
        levels[level] += 1
        if level.startswith("brand"):
            brand_confidence[e.brand_confidence] += 1
    n = len(encounters)
    row: dict = {"encounters": n}
    for level in (*ARTWORK_LEVELS, "none"):
        row[level] = _share(levels[level], n)
    row["brand_level_registration"] = _share(brand_confidence["registration"], n)
    row["brand_level_inferred"] = _share(brand_confidence["inferred"], n)
    return row


def score(
    encounters: list[Encounter], library_keys: set[str], weights: dict[str, float]
) -> tuple[float, float]:
    """(share matched at any level, weighted coverage) of a library on some encounters."""
    matched = weighted = 0.0
    for e in encounters:
        level = best_match(e, library_keys)[1]
        if level:
            matched += 1
            weighted += weights[level]
    n = len(encounters)
    return _share(matched, n), _share(weighted, n)


def build_library(
    encounters: list[Encounter], cfg: LibraryConfig, home_country: str, *, extras: bool = True
) -> list[LibraryItem]:
    """Greedy coverage picks, then required fallbacks and hero images (if ``extras``).

    Images that would end up showing no encounters (e.g. a family image made redundant by
    exact subtypes picked after it) are dropped, and the selection is rerun without them.
    """
    if not encounters:
        return []
    excluded: set[str] = set()
    while True:
        greedy = _select(encounters, cfg, excluded)
        shown = Counter(best_match(e, greedy.chosen)[0] for e in encounters)
        redundant = {key for key in greedy.chosen if not shown[key]}
        if not redundant:
            break
        excluded |= redundant

    if extras:
        for key in cfg.always_include:
            if key in greedy.members and key not in greedy.chosen:
                greedy.add(key, "required", "required fallback category")
        for key, reason in heroes(
            encounters, greedy.chosen, home_country, cfg.hero_min_days, cfg.hero_max
        ):
            greedy.add(key, "hero", reason)

    shown = Counter(best_match(e, greedy.chosen)[0] for e in encounters)
    for item in greedy.items:
        item.encounters_covered = shown[item.artwork_key]
    return greedy.items


def _select(encounters: list[Encounter], cfg: LibraryConfig, excluded: set[str]) -> _Greedy:
    greedy = _Greedy(encounters, cfg.weights)
    counts: Counter = Counter()
    while True:
        best_any = best_brand = None
        for key, level in greedy.levels.items():
            kind = _kind(level)
            limit = cfg.brand_max if kind == "brand" else cfg.generic_max
            if key in greedy.chosen or key in excluded or counts[kind] >= limit:
                continue
            candidate = (greedy.gain(key), cfg.weights[level], key)
            if best_any is None or _better(candidate, best_any):
                best_any = candidate
            if kind == "brand" and (best_brand is None or _better(candidate, best_brand)):
                best_brand = candidate
        if best_any is None:
            break
        pick = best_any
        if pick[0] / greedy.n < cfg.min_marginal_share:
            if counts["brand"] < cfg.brand_min and best_brand and best_brand[0] > 0:
                pick = best_brand
            else:
                break
        greedy.add(pick[2], "coverage")
        counts[_kind(greedy.levels[pick[2]])] += 1
    return greedy


def heroes(
    encounters: list[Encounter], chosen: set[str], home_country: str, min_days: int, limit: int
) -> list[tuple[str, str]]:
    """Visually interesting widebody, foreign or military aircraft seen on enough days.

    Foreign means a resolved brand from another country; callsign-prefix countries are too
    noisy for business jets. Aircraft the library already shows in their own livery are
    skipped. Candidates with more reasons rank first, then days seen, then encounters.
    """
    groups: dict[str, list[Encounter]] = defaultdict(list)
    for e in encounters:
        specific = next(
            (k for k, level in candidate_keys(e) if level in ("brand_type", "generic_type")), None
        )
        if specific:
            groups[specific].append(e)

    rows = []
    for key, group in groups.items():
        days = len({e.closest_utc.date() for e in group})
        if key in chosen or days < min_days:
            continue
        if all(best_match(e, chosen)[1] in BRAND_LEVELS for e in group):
            continue
        reasons = []
        if group[0].type_code in WIDEBODY_TYPES:
            reasons.append("widebody/heavy")
        foreign = sorted({e.brand_country for e in group} - {home_country, ""})
        if foreign:
            reasons.append(f"foreign ({', '.join(foreign)})")
        if any(e.military for e in group):
            reasons.append("military")
        if reasons:
            rows.append((-len(reasons), -days, -len(group), key, "; ".join(reasons), days))
    rows.sort()
    return [
        (key, f"hero: {reasons}; seen on {days} days") for *_, key, reasons, days in rows[:limit]
    ]


def split_half_stability(
    encounters: list[Encounter], cfg: LibraryConfig, home_country: str
) -> dict | None:
    """Build libraries from alternating days and compare them (one-week sensitivity check)."""
    days = sorted({e.closest_utc.date() for e in encounters})
    if len(days) < 4:
        return None
    first = set(days[0::2])
    half_a = [e for e in encounters if e.closest_utc.date() in first]
    half_b = [e for e in encounters if e.closest_utc.date() not in first]
    ranked_a = [i.artwork_key for i in build_library(half_a, cfg, home_country, extras=False)]
    ranked_b = [i.artwork_key for i in build_library(half_b, cfg, home_country, extras=False)]
    keys_a, keys_b = set(ranked_a), set(ranked_b)
    a_matched, a_weighted = score(half_b, keys_a, cfg.weights)
    b_matched, b_weighted = score(half_b, keys_b, cfg.weights)
    return {
        "days_a": ", ".join(str(d) for d in sorted(first)),
        "days_b": ", ".join(str(d) for d in days if d not in first),
        "images_a": len(keys_a),
        "images_b": len(keys_b),
        "shared": len(keys_a & keys_b),
        "top20_shared": len(set(ranked_a[:20]) & set(ranked_b[:20])),
        "union": len(keys_a | keys_b),
        "a_on_b_matched": a_matched,
        "a_on_b_weighted": a_weighted,
        "b_on_b_matched": b_matched,
        "b_on_b_weighted": b_weighted,
    }


class _Greedy:
    def __init__(self, encounters: list[Encounter], weights: dict[str, float]):
        self.n = len(encounters)
        self.weights = weights
        members: dict[str, list[int]] = defaultdict(list)
        self.levels: dict[str, str] = {}
        for i, e in enumerate(encounters):
            for key, level in candidate_keys(e):
                members[key].append(i)
                self.levels[key] = level
        self.members = {key: np.asarray(idx) for key, idx in members.items()}
        self.days = np.array([e.closest_utc.date().toordinal() for e in encounters])
        self.best = np.zeros(self.n)
        self.chosen: set[str] = set()
        self.items: list[LibraryItem] = []

    def gain(self, key: str) -> float:
        weight = self.weights[self.levels[key]]
        return float(np.maximum(weight - self.best[self.members[key]], 0.0).sum())

    def add(self, key: str, source: str, reason: str = "") -> None:
        idx = self.members[key]
        weight = self.weights[self.levels[key]]
        before = self.best[idx]
        gain = float(np.maximum(weight - before, 0.0).sum())
        newly = int((before == 0).sum())
        upgraded = int(((before > 0) & (before < weight)).sum())
        self.best[idx] = np.maximum(before, weight)
        self.chosen.add(key)
        self.items.append(
            LibraryItem(
                rank=len(self.items) + 1,
                artwork_key=key,
                level=self.levels[key],
                source=source,
                encounters_covered=0,
                marginal_coverage_added=gain / self.n,
                newly_matched=newly,
                upgraded=upgraded,
                cumulative_match_share=float((self.best > 0).mean()),
                cumulative_weighted_coverage=float(self.best.mean()),
                days_seen=len(np.unique(self.days[idx])),
                reason=reason or f"coverage: {newly} newly matched, {upgraded} upgraded",
            )
        )


def _better(a: tuple[float, float, str], b: tuple[float, float, str]) -> bool:
    """Higher gain wins; ties go to the more specific level, then the key name."""
    if abs(a[0] - b[0]) > 1e-9:
        return a[0] > b[0]
    if a[1] != b[1]:
        return a[1] > b[1]
    return a[2] < b[2]


def _kind(level: str) -> str:
    return "brand" if level.startswith("brand") else "generic"


def _share(part: float, whole: float) -> float:
    return part / whole if whole else 0.0
