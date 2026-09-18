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
4. **Render** a portrait 1200×1600 poster with Pillow. The poster combines:
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
- **Few dependencies at runtime.** Pillow and requests, plus `inky` on the Pi
  (which brings numpy, spidev, smbus2 and gpiodevice with it). Config uses the
  stdlib `tomllib`. The analysis tooling is an extra that's never installed on
  the Pi.
- **Don't redraw for nothing.** Only re-render and refresh the panel when the
  selected aircraft changes. This saves the panel and the CPU.
- **Precompute offline, look up at runtime.** Rarity weights and airline and
  type names are small static files in `data/reference/`, produced or curated
  on a laptop. The Pi does lookups; it doesn't run analysis.
- **Display behind an interface.** Rendering produces a `PIL.Image`. A display
  backend decides what to do with it (`png` or `inky`), selected by config.

---

## Repository layout

The analysis package exists. The other modules are planned and listed here for orientation.

```
.
├── pyproject.toml
├── README.md
├── config/                  # *.example.toml (committed); local copies without .example are gitignored
├── src/airframe/
│   ├── __main__.py          # run the frame: python -m airframe [--once]
│   ├── app.py               # poll, choose, redraw only when the aircraft changes
│   ├── config.py            # frame TOML: location, radius, refresh, weights
│   ├── adsb.py              # adsb.lol live API client
│   ├── aircraft_db.py       # registration/type/owner by hex (SQLite built from tar1090-db)
│   ├── operators.py         # ICAO airline designators (which callsigns are airlines)
│   ├── routes.py            # callsign -> scheduled route lookups, cached
│   ├── livery.py            # visible livery brand + confidence (shared with the analysis)
│   ├── names.py             # airline and aircraft display names, IATA flight numbers
│   ├── enrich.py            # contacts -> scored candidates -> the Sighting on the frame
│   ├── scoring.py           # interestingness + proximity + artwork match
│   ├── models.py            # Sighting / Airport: what the frame shows
│   ├── artwork.py           # pick the image via the fallback hierarchy
│   ├── geo.py, http.py, refdata.py, paths.py   # small shared helpers
│   ├── preview.py           # render sample frames to PNG on a laptop
│   ├── samples.py           # real sample sightings for the preview
│   ├── render/              # implemented
│   │   ├── poster.py        # compose the portrait 1200×1600 poster
│   │   ├── route_map.py     # faint map, great-circle route, aircraft marker
│   │   ├── aircraft.py      # trim and scale every plane to the same box
│   │   ├── format.py        # altitude, speed, heading, distance, footer status
│   │   ├── text.py          # letter-spacing and shrink-to-fit
│   │   └── theme.py         # canvas, colors, fonts, layout positions
│   ├── display/
│   │   ├── base.py          # Display interface: show(image)
│   │   ├── png.py           # dev: write PNG (+ e-ink simulation) — implemented
│   │   ├── spectra6.py      # simulate the 6-color panel — implemented
│   │   └── inky.py          # prod: Inky Impression driver (untested on the panel)
│   └── analysis/            # offline tooling (requires the `analysis` extra) — implemented
│       ├── __main__.py      # CLI: python -m airframe.analysis / airframe-analyze
│       ├── config.py        # analysis TOML: location, radii, dates, source
│       ├── sources.py       # fetch heatmaps (adsb.lol web or GitHub release tar), cache regional extract
│       ├── heatmap.py       # decode readsb heatmap binary format, geographic filter
│       ├── reference.py     # aircraft DB (reg/type) + airline designators
│       ├── livery.py        # visible livery brand + confidence per encounter
│       ├── routes.py        # callsign route lookups (low-confidence livery evidence)
│       ├── artwork.py       # fallback hierarchy, recommended library, split-half check
│       ├── encounters.py    # dedupe passes, closest approach, enrichment
│       ├── stats.py         # top types/airlines/combos, coverage, rare candidates
│       └── report.py        # CSVs + report.md
├── assets/
│   ├── aircraft/            # curated final artwork (see naming below)
│   ├── fonts/               # bundled fonts (check licenses)
│   └── prompts/             # style guide + generation prompts for consistent artwork
├── data/
│   └── reference/           # committed, editable CSVs: brands, operator/registration→brand, families
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

File names in `assets/aircraft/` follow the fallback hierarchy. The frame shows the
first image that exists:

```
<brand>_<TYPE>.png      # 1. brand + exact subtype   delta-connection_CRJ9.png
<brand>_<FAMILY>.png    # 2. brand + family          delta-connection_CRJ-FAM.png
ANY_<TYPE>.png          # 3. generic subtype         ANY_C172.png
ANY_<FAMILY>.png        # 4. generic family          ANY_GA-HIGHWING.png
```

Brands are visible liveries, so the brand is `delta-connection`, not `SKW`. They're
defined in [data/reference/brands.csv](data/reference/brands.csv). Families come from
[data/reference/aircraft_families.csv](data/reference/aircraft_families.csv). The
offline analysis recommends which images to create first.

Finals are stored already trimmed and sized for the poster's aircraft box, so the Pi never
scales a multi-megapixel PNG. Run new artwork through
[scripts/resize_artwork.py](scripts/resize_artwork.py), which does exactly what the renderer
would have done at render time.

---

## Offline analysis

This runs on a laptop only. It turns historical traffic near the configured location
into decisions about artwork and radius:

```bash
pip install -e ".[analysis]"
python -m airframe.analysis                     # last 7 complete UTC days, config/analysis.example.toml
python -m airframe.analysis --days 14
python -m airframe.analysis --dates 2026-09-01,2026-09-02 --source github
```

Settings live in [config/analysis.example.toml](config/analysis.example.toml). To change
them, copy it to `config/analysis.toml`, which is gitignored and used automatically. The
defaults are:
- center point: U-M Central Campus (42.2768, -83.7382)
- primary radius: 15 NM, compared against 10 and 20 NM
- airports checked: DTW, YIP and ARB

Output goes to `data/analysis/<first-date>_<last-date>/`. It contains `report.md` and
these CSVs:

| File | Contents |
|------|----------|
| `radius_comparison.csv`, `radius_rings.csv` | 10/15/20 NM side by side, and what each ring adds (including the DTW arrival/departure share) |
| `encounters_<r>nm.csv` | one row per deduplicated encounter: hex, callsign, registration, type, airline, operator, entered/closest time, closest distance, altitude at closest approach, airport ops |
| `top_types_`, `top_airlines_`, `top_combinations_<r>nm.csv` | ranked frequency tables |
| `artwork_coverage_<r>nm.csv` | share of encounters covered by the top 10/20/30/50/75/100 combinations |
| `rare_interesting_<r>nm.csv` | notable combinations below the coverage set, with reasons |
| `top_brands_`, `livery_confidence_`, `livery_methods_`, `unresolved_registrations_<r>nm.csv` | visible livery brands, confidence shares, evidence used, and the unresolved registrations most worth checking |
| `artwork_library.csv`, `artwork_level_coverage.csv` | recommended starting library (ranked by marginal coverage) and coverage at each fallback level per radius |
| `livery_flight_blocks.csv` | flight-number blocks learned from owner-confirmed aircraft |

### How the historical data is accessed

adsb.lol publishes each UTC day as a GitHub release (`adsblol/globe_history_YYYY`). A
release is a ~3.5–4 GB tar of per-aircraft trace files, plus 48 half-hour **heatmap**
files. It has no geographic index. The options, measured in September 2026:

| Approach | Transfer per day | Verdict |
|----------|------------------|---------|
| Release tar, parse every trace file | ~4 GB, plus gunzip and JSON-parse of every aircraft seen worldwide | Slowest. There's no way to skip aircraft that never came near Ann Arbor. |
| Per-aircraft trace URLs | small per file | Needs the list of nearby aircraft first, then one request per aircraft. |
| **Heatmap files from adsb.lol** (default, `web`) | 48 × 12–18 MB ≈ 0.7 GB | **Chosen.** Each file is a 10-second position snapshot of every aircraft, in fixed 16-byte records. numpy filters a file to the 25 NM circle in about 12 ms. |
| Heatmaps from the release tar (`github`) | ~4 GB, streamed without saving to disk | Fallback for days the website no longer serves. Heatmaps are the last tar members, so the whole tar has to be read. |

Each day is reduced to the positions and callsigns inside `extract_radius_nm` (25 NM)
and cached in `data/cache/heatmap_extracts/`. Re-runs and radius changes don't
re-download anything.

### Method

- **Encounter:** one airborne pass of one aircraft through a radius. Samples of the same
  hex less than 30 minutes apart merge into one encounter, so loitering or pattern work
  counts once.
- **Closest approach and altitude:** taken from the samples and from the closest point on
  the straight segment between consecutive 10-second samples, which interpolates between
  them.
- **Registration, type and owner/operator:** from the
  [tar1090-db](https://github.com/wiedehopf/tar1090-db) aircraft database, the same one
  readsb uses. Its military and "interesting" flags feed the rare list.
- **Airline:** the 3-letter ICAO designator at the start of the callsign (e.g. `SKW5501`),
  looked up in readsb's operator list. Non-airline callsigns such as `N12345` have no
  airline. This is the *operating carrier*. The livery is estimated separately (below).
- **Airport ops:** within 20 minutes of the pass, the aircraft was on the ground or below
  2,500 ft AGL within 4 NM of the airport. This is how DTW arrivals and departures are
  measured per radius and per ring.

### Livery brands

Regional operators fly partner liveries. SkyWest and Republic fly Delta Connection, United
Express and American Eagle aircraft, so each encounter gets an estimated visible brand
and a confidence level:

| Confidence | Evidence |
|------------|----------|
| `registration` | Tied to the airframe: an entry in `livery_registrations.csv`, the aircraft DB military flag, or a registered owner that matches one of the operator's brands (`owner_patterns` in `operator_brands.csv`; e.g. a Delta-owned CRJ-900 flown by SkyWest). |
| `inferred` | From the flight: an operator that flies for one brand only; a flight-number block (e.g. `RPA5xxx`) flown only by owner-confirmed aircraft of one brand in the same run; a callsign route (adsb.lol route DB) that touches exactly one candidate brand's hub and passes within 75 NM; or other flights of the same registration. |
| `unresolved` | No evidence, conflicting evidence, a mixed-livery charter operator, or no airline callsign. Nothing is guessed. |

The mappings live in editable CSVs in `data/reference/`: `brands.csv`,
`operator_brands.csv`, `livery_registrations.csv` and `aircraft_families.csv`. Lines
starting with `#` are comments. The report lists the most common unresolved
registrations. Verify them from photos and add them to `livery_registrations.csv` to
upgrade them to `registration` confidence.

### Recommended artwork library

The library is built from primary-radius traffic in three parts:
1. **Coverage images, added greedily by marginal weighted coverage.** Each encounter
   scores the weight of its best match: brand + subtype 1.0, brand + family 0.8,
   generic subtype 0.5, generic family 0.3. An image that upgrades encounters from a
   generic fallback to their real livery still counts as progress. Picks continue until
   the gain drops below 0.2%, with 30–50 brand images and at most 20 generic ones.
2. **Required fallbacks:** GA singles and twins, business jets and military.
3. **Hero images:** widebody, foreign or military aircraft seen on at least 3 days.

The report shows coverage at each fallback level for every radius. It also runs a
split-half check: libraries built from alternating days are compared to show how much a
single week's conclusions can be trusted. Weights and limits are in the `[library]`
section of the config.

### Known limitations

- Livery brands are estimates. `inferred` brands can be wrong when an operator
  reassigns aircraft between partners or reshuffles flight numbers.
- Special or retro liveries aren't detected unless added to `livery_registrations.csv`.
- The aircraft DB reflects today's registry, not the registry on the analyzed dates.
- Coverage depends on adsb.lol's volunteer feeders. Low-altitude traffic far from any
  feeder can be missed.
- Heatmap altitude is barometric, in 25 ft steps.

---

## Getting started

### Development (laptop)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"            # add ,analysis for the offline tooling
cp config/airframe.example.toml config/airframe.toml   # optional: edit location, radius, weights
```

### Run the frame

```bash
python -m airframe --once -v   # one update, with candidate scores
python -m airframe             # keep running (every 3 minutes)
```

The frame is written to `output/frame.png` (plus `frame-eink.png`). On the first run it
downloads the aircraft database and indexes it into SQLite in `data/cache/`.

Each update:
1. Fetches airborne aircraft within `radius_nm` of the location, widening to
   `fallback_radius_nm` if nothing is in range.
2. Scores each one: `55 × interestingness + 30 × proximity + 15 × artwork match`.
   - **interestingness:** 60% rarity (from `traffic_frequency.csv`) and 40% notability
     (military, flagged interesting, widebody, foreign airline).
   - **proximity:** slant distance, so a jet at 37,000 ft overhead counts as further away
     than a Cessna at 3,000 ft.
   - **artwork match:** exact livery 1.0, brand + family 0.8, generic type 0.5, family 0.3.
3. Keeps the current aircraft for at least `min_display_seconds`, and doesn't repeat one
   within `repeat_cooldown_minutes` unless nothing else is around.
4. Holds the last aircraft when nothing is in range: the frame is redrawn once, with the
   footer reading "Last seen at …", then left alone.

The display is only redrawn when the chosen aircraft changes, since e-ink refreshes are slow
and flash.

### Replay past traffic

```bash
python -m airframe.analysis.replay --switches 100 --frame-seconds 3
python -m airframe.analysis.replay --start 2026-09-09T09:00 --day-start 6 --day-end 23
```

Feeds the cached week of positions (`data/cache/heatmap_extracts/`, written by the offline
analysis) through the same scoring, selection and rendering the live app uses, writing to
`output/frame.png`. Simulated time advances by the refresh interval; updates that don't
change the aircraft are processed instantly, so `--frame-seconds` is how long each *new*
frame stays up. It prints a summary of which artwork levels and aircraft were shown, which
is the quickest way to judge a scoring change or a new artwork batch.

### Poster preview

```bash
python -m airframe.preview              # sample frames → output/preview/
python -m airframe.preview --units aviation   # kt and NM instead of mph and mi
```

Each sample frame is written twice:
- `NN-name.png`: what the poster looks like on a normal screen.
- `NN-name-eink.png`: a simulation of the 6-color Spectra 6 panel, using the palette measured in Pimoroni's driver.

`contact-sheet.png` shows all frames side by side.

The samples cover these states:
- exact livery with route
- generic fallback image
- livery unresolved
- private aircraft with no route
- no artwork yet
- holding an aircraft seen 14 minutes ago

The poster uses IBM Plex Serif and Sans (SIL Open Font License, `assets/fonts/`) and
simplified Natural Earth land and lakes (public domain, `assets/map/world.json`, built by
`scripts/build_map_data.py`).

### Production (Raspberry Pi Zero 2 W)

Full instructions, including the service user and the buses to enable, are in
[deploy/README.md](deploy/README.md). In short:

1. Raspberry Pi OS Lite (Bookworm or later), with SPI and I2C enabled via `raspi-config`.
2. `python3 -m venv .venv && .venv/bin/pip install -e ".[pi]"`
3. In `config/airframe.toml`, set `[display] backend = "inky"` and `rotation` to `90` or
   `270`. The poster is portrait (1200 × 1600) and the panel is landscape (1600 × 1200), so
   the frame is rotated on the way out; the rotation is which way up it hangs.
4. Install [deploy/airframe.service](deploy/airframe.service) and
   `systemctl enable --now airframe`.

The panel driver is written against `inky` 2.5 and covered by tests with a fake panel, but it
hasn't yet run on real hardware.

---

## Roadmap

- [x] Config loading and example settings
- [x] adsb.lol client and data models
- [x] Display interface with PNG backend and e-ink simulation
- [x] Inky Impression backend (written and tested against a fake panel; unverified on hardware)
- [x] Scoring and selection (interestingness, proximity, artwork match)
- [x] Enrichment (livery brand, display names, flight numbers, route leg)
- [x] Poster renderer and route graphic
- [x] Artwork prompt log and first batch of images
- [x] Historical ingest and traffic statistics (radius comparison, coverage, rare candidates)
- [x] Export traffic frequency to `data/reference/` for the frame's scoring
- [x] systemd deployment on the Pi (unit and install notes in `deploy/`; unverified on hardware)
