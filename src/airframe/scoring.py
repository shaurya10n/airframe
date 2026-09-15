"""Score aircraft to decide which one the frame shows.

``score = w_i * interestingness + w_p * proximity + w_a * artwork_match`` with each part in
[0, 1] and default weights 55 / 30 / 15, so scores run from 0 to 100.

* **interestingness**: 60% rarity (how seldom this brand + type, or type, passes here, from
  ``traffic_frequency.csv`` exported by the offline analysis) and 40% notability (military,
  flagged interesting, widebody, or a foreign airline).
* **proximity**: 1 overhead at ground level, falling to 0 at the search radius, using the
  slant distance so a jet at 37,000 ft overhead is "further" than one at 3,000 ft.
* **artwork_match**: how specific the available image is (exact livery 1.0 ... none 0).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from airframe.refdata import read_reference_csv

FEET_PER_NM = 6076.12
UNKNOWN_RARITY = 0.5
ARTWORK_MATCH = {
    "brand_type": 1.0,
    "brand_family": 0.8,
    "generic_type": 0.5,
    "generic_family": 0.3,
}
WIDEBODY_TYPES = frozenset(
    """
    A306 A30B A310 A332 A333 A338 A339 A342 A343 A345 A346 A359 A35K A388 A3ST A124 A225
    B741 B742 B743 B744 B748 B74S B762 B763 B764 B772 B77L B773 B77W B778 B779 B788 B789
    B78X BLCF BSCA C5M C17 DC10 E3TF E6 IL76 IL96 K35R KC10 KC46 L101 MD11 VC25
    """.split()
)


@dataclass(frozen=True)
class Weights:
    interestingness: float = 55
    proximity: float = 30
    artwork: float = 15


class TrafficFrequency:
    """Sightings per day near the location, by brand + type ("combo") and by type."""

    def __init__(self, path: Path | None):
        self._per_day: dict[str, dict[str, float]] = {"combo": {}, "type": {}}
        if path and path.exists():
            for row in read_reference_csv(path):
                self._per_day.setdefault(row["kind"], {})[row["key"]] = float(row["per_day"])
        self._most = {
            kind: max(values.values(), default=1.0) for kind, values in self._per_day.items()
        }

    def rarity(self, brand: str, type_code: str) -> float:
        """1 for never seen, 0 for the most common; UNKNOWN_RARITY without a type."""
        if not type_code:
            return UNKNOWN_RARITY
        kind, key = ("combo", f"{brand}_{type_code}") if brand else ("type", type_code)
        per_day = self._per_day[kind].get(key, 0.0)
        return max(0.0, 1.0 - math.log1p(per_day) / math.log1p(self._most[kind]))


def interestingness(
    rarity: float, *, type_code: str, military: bool, flagged: bool, foreign: bool
) -> float:
    if military or flagged or type_code in WIDEBODY_TYPES:
        notability = 1.0
    elif foreign:
        notability = 0.8
    else:
        notability = 0.0
    return 0.6 * rarity + 0.4 * notability


def proximity(distance_nm: float, altitude_ft: int | None, scale_nm: float) -> float:
    slant = math.hypot(distance_nm, (altitude_ft or 0) / FEET_PER_NM)
    return max(0.0, 1.0 - slant / scale_nm)


def score(weights: Weights, interest: float, prox: float, artwork_level: str) -> float:
    return (
        weights.interestingness * interest
        + weights.proximity * prox
        + weights.artwork * ARTWORK_MATCH.get(artwork_level, 0.0)
    )
