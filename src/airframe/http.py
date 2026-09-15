"""HTTP session and cached downloads."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import requests

log = logging.getLogger(__name__)

USER_AGENT = "airframe (+https://github.com/shaurya10n/airframe)"


def make_session(pool_size: int = 8) -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    session.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=pool_size))
    return session


def download(
    path: Path, url: str, session: requests.Session, max_age_days: float | None = None
) -> Path:
    """Download ``url`` to ``path`` unless a fresh enough copy is already there."""
    if path.exists() and (
        max_age_days is None or time.time() - path.stat().st_mtime < max_age_days * 86400
    ):
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    log.info("downloading %s", url)
    try:
        resp = session.get(url, timeout=120)
        resp.raise_for_status()
    except requests.RequestException:
        if path.exists():
            log.warning("could not refresh %s; using the cached copy", path.name)
            return path
        raise
    tmp = path.with_name(path.name + ".part")
    tmp.write_bytes(resp.content)
    tmp.replace(path)
    return path
