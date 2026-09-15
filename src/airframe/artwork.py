"""Choose the aircraft image for a sighting.

Images live in ``assets/aircraft/<key>.png``. The most specific existing key wins:

1. ``<brand>_<TYPE>``    e.g. ``united_B39M``
2. ``<brand>_<FAMILY>``  e.g. ``united_737MAX``
3. ``ANY_<TYPE>``        e.g. ``ANY_C172``
4. ``ANY_<FAMILY>``      e.g. ``ANY_GA-HIGHWING``
"""

from __future__ import annotations

from pathlib import Path

from airframe.refdata import load_families

GENERIC = "ANY"


def candidate_keys(brand: str, type_code: str, family: str) -> list[str]:
    keys = []
    if brand and type_code:
        keys.append(f"{brand}_{type_code}")
    if brand and family:
        keys.append(f"{brand}_{family}")
    if type_code:
        keys.append(f"{GENERIC}_{type_code}")
    if family:
        keys.append(f"{GENERIC}_{family}")
    return keys


class ArtworkLibrary:
    def __init__(self, image_dir: Path, families_csv: Path | None = None):
        self._images = {path.stem: path for path in sorted(image_dir.glob("*.png"))}
        self._families = (
            load_families(families_csv) if families_csv and families_csv.exists() else {}
        )

    def family(self, type_code: str) -> str:
        return self._families.get(type_code.upper(), "")

    def resolve(self, brand: str, type_code: str) -> Path | None:
        for key in candidate_keys(brand, type_code, self.family(type_code)):
            if key in self._images:
                return self._images[key]
        return None
