# Artwork prompt log

Every image in `assets/aircraft/` gets an entry here with the exact prompt used, so the
series stays consistent and any image can be regenerated.

**Process:** give GPT a blank side-profile template of the aircraft, then a prompt that
applies a specific or generic livery in the shared house style. Save the result as
`assets/aircraft/<artwork key>.png`. See the README for the key naming rules.

## Image spec

Settled once the poster layout was finalized:

- **Transparent PNG**, one aircraft, side profile, facing left to right.
- **Fill the canvas edge to edge.** Canvas size and aspect don't matter: the renderer trims
  to the visible pixels and scales every aircraft into the same box, so all planes end up
  about the same size on the frame.
- **Landing gear:** retracted for airliners and jets; down for fixed-gear GA aircraft
  (Cessna 172/152, DA20, PA-28), where retracted would be wrong.
- **No registration, no scenery, no text, no poster framing.**
- **Partner liveries must carry the partner titles:** "United Express", "Delta Connection",
  "American Eagle" — not the mainline wordmark.
- **Check each image in the e-ink simulation** (`python -m airframe.preview`, then look at
  the `-eink.png` files) before accepting it.

## Verification checklist

After each batch:

1. File name matches the artwork key exactly (brand and type/family must both resolve).
2. RGBA with real transparency, aircraft edge to edge after trimming.
3. Recompute coverage against the sample week, and confirm every image matches real traffic.
4. Build a contact sheet and spot-check a few rendered frames.
5. Eyeball partner-livery titles and any aircraft that could be confused with another type.

## Status

| # | Artwork key | Level | Base template | Batch | Notes |
|---|---|---|---|---|---|
| 1 | `united_B39M` | brand + subtype | Boeing 737 MAX 9 | 1 | reference image for the series style |
| 2 | `delta-connection_CRJ9` | brand + subtype | Bombardier CRJ-900 | 1 | titles correctly read "Delta Connection" |
| 3 | `american_B788` | brand + subtype | Boeing 787-8 | 1 | low frequency (31/week); fine to keep |
| 4 | `ANY_A320-FAM` | generic family | Airbus A320 | 1 | |
| 5 | `ANY_CRJ-FAM` | generic family | Bombardier CRJ-900 | 1 | |
| 6 | `ANY_787-FAM` | generic family | Boeing 787-9 | 1 | |
| 7 | `ANY_BIZJET-MIDSIZE` | generic family | Learjet 60 | 1 | most midsize traffic is Citation Excel / Challenger 300 / Hawker 800 |
| 8 | `ANY_GA-HIGHWING` | generic family | high-wing single | 1 | fixed gear is correct here |
| 9 | `united-express_E75L` | brand + subtype | Embraer E175 | 2 | regenerated: first attempt read "UNITED"; prompt now calls out the titles |
| 10 | `delta_A21N` | brand + subtype | Airbus A321neo | 2 | |
| 11 | `delta-connection_CRJ7` | brand + subtype | Bombardier CRJ-700 | 2 | |
| 12 | `delta_B739` | brand + subtype | Boeing 737-900ER | 2 | |
| 13 | `american_B738` | brand + subtype | Boeing 737-800 | 2 | |
| 14 | `delta_B712` | brand + subtype | Boeing 717-200 | 2 | |
| 15 | `delta_A321` | brand + subtype | Airbus A321 | 2 | |
| 16 | `southwest_B38M` | brand + subtype | Boeing 737 MAX 8 | 2 | |
| 17 | `delta_A319` | brand + subtype | Airbus A319 | 2 | |
| 18 | `american-eagle_E75L` | brand + subtype | Embraer E175 | 2 | |
| 19 | `southwest_B737` | brand + subtype | Boeing 737-700 | 2 | |
| 20 | `american-eagle_E170` | brand + subtype | Embraer E170 | 2 | |
| 21 | `delta_B752` | brand + subtype | Boeing 757-200 | 2 | |
| 22 | `united_B739` | brand + subtype | Boeing 737-900ER | 2 | |
| 23 | `united_B738` | brand + subtype | Boeing 737-800 | 2 | |
| 24 | `atp-flight-school_C172` | brand + subtype | Cessna 172 | 2 | fixed gear |
| 25 | `american-eagle_CRJ9` | brand + subtype | Bombardier CRJ-900 | 2 | |
| 26 | `american_A321` | brand + subtype | Airbus A321 | 2 | |
| 27 | `southwest_B738` | brand + subtype | Boeing 737-800 | 2 | |
| 28 | `delta_BCS1` | brand + subtype | Airbus A220-100 | 2 | Delta's A220-300 falls back to `ANY_A220-FAM` until `delta_BCS3` exists |
| 29 | `united_B38M` | brand + subtype | Boeing 737 MAX 8 | 2 | |
| 30 | `ANY_737NG` | generic family | Boeing 737-800 | 2 | |
| 31 | `ANY_EJET-E1` | generic family | Embraer E175 | 2 | |
| 32 | `ANY_737MAX` | generic family | Boeing 737 MAX 8 | 2 | |
| 33 | `ANY_GA-LOWWING` | generic family | low-wing single | 2 | fixed gear |
| 34 | `ANY_BIZJET-LIGHT` | generic family | Learjet 45 | 2 | |
| 35 | `ANY_BIZJET-LARGE` | generic family | Bombardier Global 5000 | 2 | |
| 36 | `ANY_A220-FAM` | generic family | Airbus A220-300 | 2 | |
| 37 | `ANY_757-FAM` | generic family | Boeing 757-200 | 2 | |
| 38 | `ANY_DC9-MD80` | generic family | McDonnell Douglas MD-80 | 2 | least used image (20 sightings/week) |
| 39 | `ANY_DV20` | generic subtype | Diamond DA20 | 2 | regenerated: first attempt was a high-wing Cessna |
| 40 | `ANY_767-FAM` | generic family | Boeing 767-300 | 2 | |

**Coverage with these 40 images** (Ann Arbor, 15 NM, sample week): 83.7% of sightings get an
image, 36.0% get their exact livery. Across daytime refreshes, something is showable 97.8%
of the time and an exact-livery aircraft is available 84.9% of the time.

### Up next (candidates, no prompts yet)

Biggest remaining blanks, in order: `ANY_DA40` (87 sightings/week), `ANY_TURBOPROP-SINGLE`
(PC-12, TBM; 38), `ANY_HELI-TWIN` (28), `ANY_KINGAIR` (22), `ANY_DASH8` (Porter),
`delta_BCS3` (36). After that, liveries ranked 24+ in `artwork_library.csv`: `alaska_B739`,
`jetblue_A321`, `netjets_C68A`, `united_A21N`, `alaska_B39M`, `american-eagle_CRJ7`,
`delta-connection_E75L`, `netjets_E55P`.

## Prompt template

Prompts are built from these blocks. Reuse them so new images match the series.

**1. Reference**
> Use the uploaded blank {AIRCRAFT} template as the main reference and keep its exact side-profile geometry.

**2a. Livery (specific)**
> Apply the current {AIRLINE / BRAND} livery accurately using the provided references, including {KEY LIVERY ELEMENTS: wordmark, tail design, fuselage colors, engine/winglet markings}.

For partner liveries, name the titles explicitly:
> Make sure the fuselage titles read "{United Express / Delta Connection / American Eagle}", not just "{United / Delta / American}".

**2b. Livery (generic)**
> Render it as a generic {FAMILY} aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for {FAMILY} aircraft.

**3. Style (identical for every image)**
> Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail.

**4. Composition**
> Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number.

Drop "with landing gear retracted" for fixed-gear GA aircraft.

**5. Background**
> Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.

## Batch 1 prompts (2026-09-15)

### 1. `united_B39M`
- **Template:** blank Boeing 737 MAX 9

```text
Use the uploaded blank Boeing 737 MAX 9 template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately: white fuselage, blue UNITED wordmark, blue engines, blue globe tail, and correct winglet colors. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, so avoid glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 2. `delta-connection_CRJ9`
- **Template:** blank Bombardier CRJ-900, plus Delta Connection livery references
- **Note:** sent as a follow-up in the same chat as #1, hence "That is good. Now…"

```text
That is good. Now use the uploaded blank Bombardier CRJ-900 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Connection livery accurately using the provided references, including the correct Delta wordmark, tail design, fuselage colors, and engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, so avoid glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 3. `american_B788`
- **Template:** blank Boeing 787-8, plus American Airlines livery references

```text
Use the uploaded blank Boeing 787-8 template as the main reference and keep its exact side-profile geometry. Apply the current American Airlines livery accurately using the provided references, including the silver/gray fuselage treatment, American wordmark, striped red-white-blue tail, and correct engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, so avoid glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 4. `ANY_A320-FAM`
- **Template:** blank Airbus A320

```text
Use the uploaded blank Airbus A320 template as the main reference and keep its exact side-profile geometry. Render it as a generic A320-family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple, elegant, and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback aircraft image. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, so avoid glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 5. `ANY_CRJ-FAM`
- **Template:** blank Bombardier CRJ-900

```text
Use the uploaded blank Bombardier CRJ-900 template as the main reference and keep its exact side-profile geometry. Render it as a generic CRJ-family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for CRJ-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 6. `ANY_787-FAM`
- **Template:** blank Boeing 787-9

```text
Use the uploaded blank Boeing 787-9 template as the main reference and keep its exact side-profile geometry. Render it as a generic 787-family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for 787-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 7. `ANY_BIZJET-MIDSIZE`
- **Template:** blank Learjet 60

```text
Use the uploaded blank Learjet 60 template as the main reference and keep its exact side-profile geometry. Render it as a generic midsize business jet in a clean neutral livery, with no company branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for midsize business jets. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 8. `ANY_GA-HIGHWING`
- **Template:** high-wing single-engine aircraft reference

```text
Use the uploaded high-wing single-engine aircraft reference as the main structural guide and preserve its side-profile geometry. Render it as a generic high-wing GA aircraft in a clean neutral livery, with no branding and no registration number. Keep the paint scheme simple and realistic using soft whites and light grays with subtle neutral accents so it works well as a fallback image for Cessna-style high-wing piston aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right. Prefer the landing gear retracted if it can be done without distorting the aircraft. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

## Batch 2 prompts (2026-09-16)

### 9. `united-express_E75L`
- **Template:** Embraer E175, plus United Express livery references

```text
Use the uploaded Embraer E175 template as the main reference and keep its exact side-profile geometry. Apply the current United Express livery accurately using the provided references. Make sure the fuselage titles read “United Express”, not just “United,” and match the correct blue globe tail, fuselage colors, engine markings, and winglet details. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 10. `delta_A21N`
- **Template:** Airbus A321neo

```text
Use the uploaded Airbus A321neo template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 11. `delta-connection_CRJ7`
- **Template:** Bombardier CRJ-700

```text
Use the uploaded Bombardier CRJ-700 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Connection livery accurately using the provided references, including the Delta Connection wordmark, tail design, fuselage colors, and correct engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 12. `delta_B739`
- **Template:** Boeing 737-900ER

```text
Use the uploaded Boeing 737-900ER template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 13. `american_B738`
- **Template:** Boeing 737-800

```text
Use the uploaded Boeing 737-800 template as the main reference and keep its exact side-profile geometry. Apply the current American Airlines livery accurately using the provided references, including the American wordmark, silver-gray fuselage treatment, red-white-blue tail design, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 14. `delta_B712`
- **Template:** Boeing 717-200

```text
Use the uploaded Boeing 717-200 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 15. `delta_A321`
- **Template:** Airbus A321

```text
Use the uploaded Airbus A321 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 16. `southwest_B38M`
- **Template:** Boeing 737 MAX 8

```text
Use the uploaded Boeing 737 MAX 8 template as the main reference and keep its exact side-profile geometry. Apply the current Southwest Airlines livery accurately using the provided references, including the Southwest wordmark, red-yellow-blue tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 17. `delta_A319`
- **Template:** Airbus A319

```text
Use the uploaded Airbus A319 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 18. `american-eagle_E75L`
- **Template:** Embraer E175

```text
Use the uploaded Embraer E175 template as the main reference and keep its exact side-profile geometry. Apply the current American Eagle livery accurately using the provided references, including the American Eagle wordmark, red-white-blue tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 19. `southwest_B737`
- **Template:** Boeing 737-700

```text
Use the uploaded Boeing 737-700 template as the main reference and keep its exact side-profile geometry. Apply the current Southwest Airlines livery accurately using the provided references, including the Southwest wordmark, red-yellow-blue tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 20. `american-eagle_E170`
- **Template:** Embraer E170

```text
Use the uploaded Embraer E170 template as the main reference and keep its exact side-profile geometry. Apply the current American Eagle livery accurately using the provided references, including the American Eagle wordmark, red-white-blue tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 21. `delta_B752`
- **Template:** Boeing 757-200

```text
Use the uploaded Boeing 757-200 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 22. `united_B739`
- **Template:** Boeing 737-900ER

```text
Use the uploaded Boeing 737-900ER template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately using the provided references, including the United wordmark, blue globe tail, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 23. `united_B738`
- **Template:** Boeing 737-800

```text
Use the uploaded Boeing 737-800 template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately using the provided references, including the United wordmark, blue globe tail, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 24. `atp-flight-school_C172`
- **Template:** Cessna 172

```text
Use the uploaded Cessna 172 template as the main reference and keep its exact side-profile geometry. Apply the current ATP Flight School livery accurately using the provided references, including the ATP branding, fuselage striping/colors, tail markings, and correct wheel/gear details. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 25. `american-eagle_CRJ9`
- **Template:** Bombardier CRJ-900

```text
Use the uploaded Bombardier CRJ-900 template as the main reference and keep its exact side-profile geometry. Apply the current American Eagle livery accurately using the provided references, including the American Eagle wordmark, red-white-blue tail design, fuselage colors, and correct engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 26. `american_A321`
- **Template:** Airbus A321

```text
Use the uploaded Airbus A321 template as the main reference and keep its exact side-profile geometry. Apply the current American Airlines livery accurately using the provided references, including the American wordmark, silver-gray fuselage treatment, red-white-blue tail design, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 27. `southwest_B738`
- **Template:** Boeing 737-800

```text
Use the uploaded Boeing 737-800 template as the main reference and keep its exact side-profile geometry. Apply the current Southwest Airlines livery accurately using the provided references, including the Southwest wordmark, red-yellow-blue tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 28. `delta_BCS1`
- **Template:** Airbus A220-100

```text
Use the uploaded Airbus A220-100 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 29. `united_B38M`
- **Template:** Boeing 737 MAX 8

```text
Use the uploaded Boeing 737 MAX 8 template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately using the provided references, including the United wordmark, blue globe tail, fuselage colors, and correct engine/winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 30. `ANY_737NG`
- **Template:** Boeing 737-800

```text
Use the uploaded Boeing 737-800 template as the main reference and keep its exact side-profile geometry. Render it as a generic Boeing 737 Next Generation aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for 737NG-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 31. `ANY_EJET-E1`
- **Template:** Embraer E175

```text
Use the uploaded Embraer E175 template as the main reference and keep its exact side-profile geometry. Render it as a generic Embraer E-Jet E1 family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for E170/E175-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 32. `ANY_737MAX`
- **Template:** Boeing 737 MAX 8

```text
Use the uploaded Boeing 737 MAX 8 template as the main reference and keep its exact side-profile geometry. Render it as a generic Boeing 737 MAX family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for 737 MAX-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 33. `ANY_GA-LOWWING`
- **Template:** low-wing single-engine piston aircraft

```text
Use the uploaded low-wing single-engine piston aircraft template as the main reference and keep its exact side-profile geometry. Render it as a generic low-wing GA aircraft in a clean neutral livery, with no branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for Piper PA-28, Cirrus SR22, Mooney, and similar low-wing piston aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 34. `ANY_BIZJET-LIGHT`
- **Template:** Learjet 45

```text
Use the uploaded Learjet 45 template as the main reference and keep its exact side-profile geometry. Render it as a generic light business jet in a clean neutral livery, with no company branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for light business jets such as the Phenom 300, Learjet 45, Citation CJ3/CJ4, and similar aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 35. `ANY_BIZJET-LARGE`
- **Template:** Bombardier Global 5000

```text
Use the uploaded Bombardier Global 5000 template as the main reference and keep its exact side-profile geometry. Render it as a generic large-cabin business jet in a clean neutral livery, with no company branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for large business jets such as the Global 5000/6000, Gulfstream IV/V/600, Challenger 600-series, and similar aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 36. `ANY_A220-FAM`
- **Template:** Airbus A220-300

```text
Use the uploaded Airbus A220-300 template as the main reference and keep its exact side-profile geometry. Render it as a generic Airbus A220 family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for A220-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 37. `ANY_757-FAM`
- **Template:** Boeing 757-200

```text
Use the uploaded Boeing 757-200 template as the main reference and keep its exact side-profile geometry. Render it as a generic Boeing 757 family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for 757-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 38. `ANY_DC9-MD80`
- **Template:** McDonnell Douglas MD-80

```text
Use the uploaded McDonnell Douglas MD-80 template as the main reference and keep its exact side-profile geometry. Render it as a generic DC-9 / MD-80 / MD-90 / Boeing 717-family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for this rear-engined narrowbody family. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 39. `ANY_DV20`
- **Template:** Diamond DA20
- **Note:** regenerated; the first attempt came back as a high-wing Cessna

```text
Use the uploaded Diamond DA20 template as the main reference and keep its exact side-profile geometry. Render it as a generic Diamond DA20 in a clean neutral livery, with no flight-school branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for DA20 flight-training aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 40. `ANY_767-FAM`
- **Template:** Boeing 767-300

```text
Use the uploaded Boeing 767-300 template as the main reference and keep its exact side-profile geometry. Render it as a generic Boeing 767 family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for 767-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```
