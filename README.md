# airframe

Framed aviation wall art. A Raspberry Pi Zero 2 W watches the sky over a
configured location using the [adsb.lol](https://adsb.lol) API. It picks the
most interesting aircraft nearby and shows it as a poster on a 13.3" Pimoroni
Inky Impression e-ink display.

> **Status:** skeleton only. This repo has the directory layout and packaging,
> but no implementation code yet.

---

## What it will do

1. **Poll** adsb.lol for aircraft within a radius of the configured lat/lon.
2. **Score** each aircraft by "interestingness" (rarity of type or livery,
   proximity, altitude, special flags such as military or vintage) and pick one.
3. **Enrich** the chosen aircraft with airline, aircraft type, registration,
   callsign, route (origin → destination), altitude, ground speed, heading,
   distance from home, and current position, where each is available.
4. **Render** a 1600×1200 poster with Pillow. The poster combines:
   - curated, consistently styled artwork of the aircraft in its livery,
   - a route graphic showing origin, destination, and the aircraft's current
     position along the route,
   - typography for the flight details.
5. **Display** the frame through a small display interface:
   - **dev (laptop):** save the frame to `output/` as a PNG.
   - **prod (Pi):** push the frame to the Inky Impression.

A separate, **offline analysis** toolkit runs on a laptop. It processes
adsb.lol historical data to tune the scoring and to decide which artwork to
create.

---

## Hardware

| Part    | Notes |
|---------|-------|
| Raspberry Pi Zero 2 W | Quad-core A53, **512 MB RAM**. The runtime must stay lean. |
| Pimoroni Inky Impression 13.3" | 1600×1200, E Ink Spectra 6 (6-color) panel. A full refresh takes tens of seconds, so update every few minutes at most, not in real time. |

---

## Architecture

```
            ┌──────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌───────────────┐
 config ──▶ │  adsb    │──▶│ scoring │──▶│  enrich  │──▶│  render  │──▶│   display     │
            │  (poll)  │   │ (select)│   │ (details)│   │ (Pillow) │   │ PNG │ Inky    │
            └──────────┘   └─────────┘   └──────────┘   └──────────┘   └───────────────┘
                                ▲              ▲              ▲
                                │              │              │
                        data/reference/   data/reference/   assets/
                        (rarity weights)  (airlines, types) (artwork, fonts)

 analysis (laptop only):  adsb.lol history ──▶ traffic stats ──▶ rarity weights + artwork shortlist
```

Design principles:

- **One process, one loop.** A systemd service runs poll → select → render →
  display on a timer. There's no web server, database, or message queue.
- **Few dependencies at runtime.** Pillow and requests, plus `inky` on the Pi.
  Config uses the stdlib `tomllib`. Heavy data tooling (polars) is an optional
  extra that's never installed on the Pi.
- **Don't redraw for nothing.** Only re-render and refresh the panel when the
  selected aircraft changes. This saves the panel and the CPU.
- **Precompute offline, look up at runtime.** Rarity weights and airline and
  type names are small static files in `data/reference/`, produced or curated
  on a laptop. The Pi does lookups; it doesn't run analysis.
- **Display behind an interface.** Rendering produces a `PIL.Image`. A display
  backend decides what to do with it (`png` or `inky`), selected by config.

---

## Repository layout

Planned modules are listed here for orientation. None of them exist yet.

```
.
├── pyproject.toml
├── README.md
├── config/                  # settings.example.toml (committed), settings.toml (local, gitignored)
├── src/airframe/
│   ├── __main__.py          # entry point: run loop / run once
│   ├── config.py            # load + validate TOML config
│   ├── adsb.py              # adsb.lol client (nearby aircraft, route lookup)
│   ├── models.py            # small dataclasses: Aircraft, Route, Airport
│   ├── scoring.py           # interestingness score + selection
│   ├── enrich.py            # airline/type names, route, distance/bearing
│   ├── artwork.py           # resolve best matching image for airline + type
│   ├── render/
│   │   ├── poster.py        # compose the 1600×1200 frame
│   │   ├── route.py         # origin → destination graphic with current position
│   │   └── palette.py       # layout constants, fonts, Spectra 6 color handling
│   ├── display/
│   │   ├── base.py          # Display interface: show(image)
│   │   ├── png.py           # dev: write PNG to output/
│   │   └── inky.py          # prod: Inky Impression driver (imports `inky` lazily)
│   └── analysis/            # offline tooling (requires the `analysis` extra)
│       ├── ingest.py        # read adsb.lol historical dumps, filter to local area
│       ├── stats.py         # frequency tables, coverage curves
│       └── export.py        # write rarity weights / artwork shortlist to data/reference/
├── assets/
│   ├── aircraft/            # curated final artwork (see naming below)
│   ├── fonts/               # bundled fonts (check licenses)
│   └── prompts/             # style guide + generation prompts for consistent artwork
├── data/
│   └── reference/           # committed small lookup tables (airlines, types, rarity weights)
│                            # everything else in data/ is gitignored (history dumps, caches)
├── deploy/                  # systemd unit, Pi install notes
├── scripts/                 # one-off helpers (e.g. fetch historical data, preview render)
└── tests/
```

`output/` is created at runtime for dev PNGs and is gitignored.

---

## Data sources

- **Live aircraft:** adsb.lol REST API, e.g. `https://api.adsb.lol/v2/point/{lat}/{lon}/{radius_nm}`.
  The response includes type (`t`), registration (`r`), callsign (`flight`),
  altitude, ground speed, track, and position.
- **Routes:** adsb.lol's route lookup by callsign. It returns origin and
  destination airports with coordinates.
- **Historical:** adsb.lol publishes daily `globe_history` archives on GitHub.
  They're large, so download them on a laptop only.
- adsb.lol data is licensed under the ODbL. Credit it wherever the art is shown
  or shared.

Route data is often missing or wrong for small operators, private flights, and
military traffic. Every enrichment field is optional, and the renderer must
degrade gracefully when one is missing.

---

## Artwork conventions

Artwork is AI-generated and curated by hand so the whole library looks like one
consistent series. Keep the style guide and prompts in `assets/prompts/` so new
pieces match the existing ones.

Proposed file naming in `assets/aircraft/`, using ICAO codes:

```
<AIRLINE_ICAO>_<TYPE_ICAO>.png   # exact livery, e.g. UAL_B39M.png
ANY_<TYPE_ICAO>.png              # generic livery for a type, e.g. ANY_A320.png
```

The renderer tries a specific livery first, then the generic type, then a
family-level fallback. Store finals already sized for the poster layout so the
Pi never resizes large source images.

---

## Offline analysis

This runs on a laptop with `pip install -e ".[analysis]"`. Its goal is to turn
historical traffic near the configured location into decisions:

| Question | Output |
|----------|--------|
| Which aircraft types or families appear most often? | frequency table |
| Which airlines appear most often? | frequency table |
| Which airline + type combinations appear most often? | ranked list of artwork candidates |
| What share of nearby traffic do the top 20, 50, or 100 combinations cover? | coverage curve, used to plan the artwork budget |
| Which uncommon aircraft deserve a high interestingness score? | rarity weights, exported to `data/reference/` |

Count unique aircraft per day (by ICAO hex) rather than raw position reports.
Otherwise slow or loitering aircraft would dominate the counts.

---

## Getting started

### Development (laptop)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"            # add ,analysis for the offline tooling
cp config/settings.example.toml config/settings.toml   # once it exists
```

In dev, set the display backend to `png`. Rendered frames go to `output/`.

### Production (Raspberry Pi Zero 2 W)

1. Raspberry Pi OS Lite (Bookworm or later), with SPI and I2C enabled via `raspi-config`.
2. `python3 -m venv .venv && .venv/bin/pip install -e ".[pi]"`
3. Set the display backend to `inky` in `config/settings.toml`.
4. Install the systemd unit from `deploy/` (to be added).

---

## Roadmap

- [ ] Config loading and example settings
- [ ] adsb.lol client and data models
- [ ] Display interface with PNG and Inky backends
- [ ] Scoring and selection (initial heuristics)
- [ ] Enrichment (reference tables, route lookup, distance and bearing)
- [ ] Poster renderer and route graphic
- [ ] Artwork style guide and first batch of images
- [ ] Historical ingest and traffic statistics
- [ ] Export rarity weights and artwork shortlist
- [ ] systemd deployment on the Pi
