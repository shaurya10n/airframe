"""Callsign -> route lookups from adsb.lol's route database (VRS standing data), cached on disk.

The database maps a callsign to its current scheduled route. It says nothing about the
analyzed dates and is sometimes stale, so routes are only ever used as low-confidence
evidence, and only when the route plausibly passes near the analysis location.
Delete ``data/cache/routes.json`` to refresh.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import requests

log = logging.getLogger(__name__)

ROUTE_URL = "https://vrs-standing-data.adsb.lol/routes/{prefix}/{callsign}.json"
_FAILED = object()  # transient error: don't cache


@dataclass(frozen=True)
class RouteAirport:
    iata: str
    icao: str
    lat: float
    lon: float


class RouteLookup:
    def __init__(self, cache_path: Path, session: requests.Session, concurrency: int = 4):
        self._path = cache_path
        self._session = session
        self._concurrency = concurrency
        self._cache: dict[str, list[dict] | None] = (
            json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
        )

    def prefetch(self, callsigns: Iterable[str]) -> None:
        missing = sorted({c for c in callsigns if c} - self._cache.keys())
        if not missing:
            return
        log.info("looking up %d callsign routes", len(missing))
        with ThreadPoolExecutor(max_workers=self._concurrency) as pool:
            for callsign, result in zip(missing, pool.map(self._fetch, missing), strict=True):
                if result is not _FAILED:
                    self._cache[callsign] = result
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._cache, sort_keys=True), encoding="utf-8")

    def get(self, callsign: str) -> list[RouteAirport]:
        return [RouteAirport(**a) for a in self._cache.get(callsign) or []]

    def _fetch(self, callsign: str):
        url = ROUTE_URL.format(prefix=callsign[:2], callsign=callsign)
        try:
            resp = self._session.get(url, timeout=30)
        except requests.RequestException as exc:
            log.warning("route %s: %s", callsign, exc)
            return _FAILED
        if resp.status_code == 404:
            return None
        if not resp.ok:
            log.warning("route %s: HTTP %d", callsign, resp.status_code)
            return _FAILED
        try:
            airports = [
                {
                    "iata": a.get("iata") or "",
                    "icao": a.get("icao") or "",
                    "lat": float(a["lat"]),
                    "lon": float(a["lon"]),
                }
                for a in resp.json().get("_airports") or []
            ]
        except (ValueError, KeyError, TypeError, AttributeError):
            return None
        return airports or None
