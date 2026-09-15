"""Fetch a day of adsb.lol heatmaps and reduce it to a small regional extract.

The same heatmap data is available two ways:

* ``web``: the 48 half-hour files adsb.lol serves at ``/globe_history/YYYY/MM/DD/heatmap/``.
  They're about 12-18 MB each (~0.7 GB/day). This is the fast path, but the site doesn't
  keep every past day.
* ``github``: the daily ``adsblol/globe_history_YYYY`` release tar (~3.5-4 GB/day). It's
  the complete archive, but the heatmaps are the last members, so the whole tar has to be
  streamed. It's never written to disk.

Either way, only positions within ``extract_radius_nm`` of the configured location are kept
and cached as a small ``.npz`` per day. Re-runs and radius changes don't download anything.
"""

from __future__ import annotations

import io
import logging
import os
import re
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import requests

from airframe.analysis import heatmap
from airframe.analysis.config import AnalysisConfig

log = logging.getLogger(__name__)

SLOTS_PER_DAY = 48
WEB_URL = "https://adsb.lol/globe_history/{day:%Y/%m/%d}/heatmap/{slot:02d}.bin.ttf"
GITHUB_TAG = "v{day:%Y.%m.%d}-planes-readsb-prod-0"
GITHUB_RELEASE_API = (
    "https://api.github.com/repos/adsblol/globe_history_{day:%Y}/releases/tags/{tag}"
)
HEATMAP_MEMBER = re.compile(r"(?:^|/)heatmap/\d{2}\.bin\.ttf$")
USER_AGENT = "airframe-analysis (+https://github.com/shaurya10n/airframe)"


class DayUnavailable(Exception):
    """The selected source has no heatmap data for a day."""


@dataclass
class DayExtract:
    day: date
    positions: np.ndarray  # heatmap.POSITION_DTYPE
    callsigns: np.ndarray  # heatmap.CALLSIGN_DTYPE
    slots: int  # half-hour files present; 48 is a complete day


def make_session(pool_size: int = 16) -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    session.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=pool_size))
    return session


def load_day(day: date, cfg: AnalysisConfig, session: requests.Session) -> DayExtract:
    path = _cache_path(cfg, day)
    if path.exists():
        with np.load(path) as z:
            return DayExtract(day, z["positions"], z["callsigns"], int(z["slots"]))

    started = time.monotonic()
    parts = (
        _fetch_web(day, cfg, session) if cfg.source == "web" else _fetch_github(day, cfg, session)
    )
    if not parts:
        hint = (
            " (the website only keeps some past days; try --source github)"
            if cfg.source == "web"
            else ""
        )
        raise DayUnavailable(f"{day}: no heatmap data from {cfg.source}{hint}")

    extract = DayExtract(
        day,
        np.concatenate([p for p, _ in parts]),
        np.concatenate([c for _, c in parts]),
        len(parts),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.stem + ".tmp.npz")
    np.savez_compressed(
        tmp, positions=extract.positions, callsigns=extract.callsigns, slots=np.int64(extract.slots)
    )
    tmp.replace(path)

    log.info(
        "%s: %d/%d heatmap files, %s positions within %g NM (%.0f s)",
        day,
        extract.slots,
        SLOTS_PER_DAY,
        f"{extract.positions.size:,}",
        cfg.extract_radius_nm,
        time.monotonic() - started,
    )
    if extract.slots < SLOTS_PER_DAY:
        log.warning(
            "%s: day is incomplete (%d of %d half-hours)", day, extract.slots, SLOTS_PER_DAY
        )
    return extract


def _cache_path(cfg: AnalysisConfig, day: date) -> Path:
    region = f"{cfg.lat:.4f}_{cfg.lon:.4f}_{cfg.extract_radius_nm:g}nm"
    return cfg.data_dir / "cache" / "heatmap_extracts" / region / f"{day.isoformat()}.npz"


def _fetch_web(day: date, cfg: AnalysisConfig, session: requests.Session) -> list:
    def fetch_slot(slot: int):
        raw = _get(session, WEB_URL.format(day=day, slot=slot))
        if raw is None:
            return None
        return heatmap.decode(raw, cfg.lat, cfg.lon, cfg.extract_radius_nm)

    log.info("%s: downloading %d heatmap files from adsb.lol", day, SLOTS_PER_DAY)
    with ThreadPoolExecutor(max_workers=cfg.concurrency) as pool:
        return [part for part in pool.map(fetch_slot, range(SLOTS_PER_DAY)) if part is not None]


def _get(session: requests.Session, url: str, attempts: int = 4) -> bytes | None:
    """GET with retries. Returns None on 404 (file doesn't exist)."""
    for attempt in range(attempts):
        try:
            resp = session.get(url, timeout=120)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.content
        except requests.RequestException as exc:
            if attempt == attempts - 1:
                raise
            wait = 5 * 2**attempt
            log.warning("%s: %s; retrying in %d s", url, exc, wait)
            time.sleep(wait)
    return None


def _fetch_github(day: date, cfg: AnalysisConfig, session: requests.Session) -> list:
    tag = GITHUB_TAG.format(day=day)
    headers = {}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    resp = session.get(GITHUB_RELEASE_API.format(day=day, tag=tag), headers=headers, timeout=60)
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    assets = sorted(
        (a for a in resp.json()["assets"] if ".tar" in a["name"]), key=lambda a: a["name"]
    )
    if not assets:
        return []

    total_gb = sum(a["size"] for a in assets) / 1e9
    log.info("%s: streaming %.1f GB release %s (heatmaps are at the end)", day, total_gb, tag)
    stream = io.BufferedReader(
        _ConcatenatedDownload(session, [a["browser_download_url"] for a in assets]),
        buffer_size=1 << 20,
    )
    parts = []
    with tarfile.open(fileobj=stream, mode="r|", bufsize=1 << 20) as tar:
        for member in tar:
            if member.isfile() and HEATMAP_MEMBER.search(member.name):
                raw = tar.extractfile(member).read()
                parts.append(heatmap.decode(raw, cfg.lat, cfg.lon, cfg.extract_radius_nm))
    return parts


class _ConcatenatedDownload(io.RawIOBase):
    """Read several URLs back to back as one stream (release tars are split into parts)."""

    def __init__(self, session: requests.Session, urls: list[str]):
        self._session = session
        self._urls = iter(urls)
        self._resp: requests.Response | None = None

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        while True:
            if self._resp is None:
                url = next(self._urls, None)
                if url is None:
                    return 0
                self._resp = self._session.get(url, stream=True, timeout=120)
                self._resp.raise_for_status()
            n = self._resp.raw.readinto(buffer)
            if n:
                return n
            self._resp.close()
            self._resp = None

    def close(self) -> None:
        if self._resp is not None:
            self._resp.close()
        super().close()
