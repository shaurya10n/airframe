"""The frame's main loop: poll, choose an aircraft, and redraw only when the picture changes.

Every ``refresh_seconds``:

1. Fetch airborne aircraft within ``radius_nm``; if there are none, widen to
   ``fallback_radius_nm``.
2. Score them (see ``scoring.py``) and pick the best, with two rules:
   * the current aircraft stays for at least ``min_display_seconds`` while still in range;
   * an aircraft shown recently isn't picked again within ``repeat_cooldown_minutes`` unless
     nothing else is around.
3. If nothing is around, hold the last aircraft. The frame is redrawn once so its footer reads
   "Last seen at ..." and then left alone.

E-ink refreshes are slow and flash, so the display is only redrawn when the chosen aircraft
changes (or first goes into hold).
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from airframe.adsb import Contact
from airframe.config import FrameConfig
from airframe.display.base import Display
from airframe.enrich import Candidate, Enricher
from airframe.models import Sighting
from airframe.render import poster

log = logging.getLogger(__name__)


@dataclass
class Shown:
    candidate: Candidate
    sighting: Sighting
    shown_at: datetime
    held: bool = False


class FrameApp:
    def __init__(
        self,
        cfg: FrameConfig,
        *,
        fetch: Callable[[float], list[Contact]],
        enricher: Enricher,
        display: Display,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ):
        self.cfg = cfg
        self._fetch = fetch
        self._enricher = enricher
        self._display = display
        self._clock = clock
        self.current: Shown | None = None
        self._recent: dict[str, datetime] = {}  # hex -> when it was replaced

    def run(self) -> None:
        while True:
            started = time.monotonic()
            try:
                self.tick()
            except Exception:
                log.exception("update failed; keeping the current frame")
            time.sleep(max(1.0, self.cfg.refresh_seconds - (time.monotonic() - started)))

    def tick(self) -> str:
        """One update. Returns "shown", "kept", "held" or "idle"."""
        now = self._clock()
        candidates = self._enricher.candidates(self._fetch(self.cfg.radius_nm))
        if not candidates and self.cfg.fallback_radius_nm > self.cfg.radius_nm:
            candidates = self._enricher.candidates(self._fetch(self.cfg.fallback_radius_nm))
        _log_candidates(candidates)

        choice = self._choose(candidates, now)
        if choice is None:
            if self.current and not self.current.held:
                self.current.held = True
                self._draw(self.current, now)
                log.info("nothing in range; holding %s", self.current.candidate.hex)
                return "held"
            return "idle"

        if self.current and not self.current.held and choice.hex == self.current.candidate.hex:
            return "kept"

        if self.current and self.current.candidate.hex != choice.hex:
            self._recent[self.current.candidate.hex] = now
        self.current = Shown(choice, self._enricher.sighting(choice), now)
        self._draw(self.current, now)
        log.info(
            "showing %s %s (%s) score %.1f",
            choice.hex,
            self.current.sighting.title,
            self.current.sighting.subtitle,
            choice.score,
        )
        return "shown"

    def _choose(self, candidates: list[Candidate], now: datetime) -> Candidate | None:
        if not candidates:
            return None
        current = self.current if self.current and not self.current.held else None
        if current and now - current.shown_at < timedelta(seconds=self.cfg.min_display_seconds):
            for c in candidates:
                if c.hex == current.candidate.hex:
                    return c

        cooldown = timedelta(minutes=self.cfg.repeat_cooldown_minutes)
        self._recent = {h: t for h, t in self._recent.items() if now - t < cooldown}
        fresh = [c for c in candidates if c.hex not in self._recent]
        return (fresh or candidates)[0]

    def _draw(self, shown: Shown, now: datetime) -> None:
        image = poster.render(
            shown.sighting,
            shown.candidate.artwork,
            now=now,
            place=self.cfg.place,
            tz=self.cfg.tz,
            units=self.cfg.units,
        )
        self._display.show(image)


def _log_candidates(candidates: list[Candidate]) -> None:
    log.info("%d aircraft in range", len(candidates))
    for c in candidates[:5]:
        log.debug(
            "  %5.1f  %-8s %-6s %-4s %-18s I %.2f P %.2f art %s",
            c.score,
            c.contact.callsign or "-",
            c.hex,
            c.type_code or "?",
            c.brand or c.airline_icao or "-",
            c.interestingness,
            c.proximity,
            c.artwork_level or "none",
        )
