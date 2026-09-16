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
| 41 | `ANY_DA40` | generic subtype | Diamond DA40 | 3 | fixed gear |
| 42 | `ANY_KINGAIR` | generic family | twin-engine light aircraft reference | 3 | prompted as `ANY_GA-TWIN`, but the template was a King Air, so it was renamed to the family it depicts |
| 43 | `ANY_C208` | generic subtype | single-engine turboprop template | 3 | prompted as `ANY_TURBOPROP-SINGLE`, came back a Caravan, so it was renamed |
| 44 | `netjets_BIZJET-MIDSIZE` | brand + family | midsize business jet | 3 | first brand + family image; covers the NetJets midsize fleet |
| 45 | `delta_A330-FAM` | brand + family | Airbus A330-300 | 3 | covers the A330-200, -300 and -900 |
| 46 | `ANY_777-FAM` | generic family | Boeing 777-300ER | 3 | |
| 47 | `ANY_A350-FAM` | generic family | Airbus A350-900 | 3 | |
| 48 | `ANY_GA-TWIN` | generic family | Cessna 310 | 3 | regenerated with an in-family template |
| 49 | `ANY_TURBOPROP-SINGLE` | generic family | Pilatus PC-12 | 3 | regenerated with an in-family template |
| 50 | `alaska_B739` | brand + subtype | Boeing 737-900ER | 4 | 74/week |
| 51 | `jetblue_A321` | brand + subtype | Airbus A321 | 4 | 73/week |
| 52 | `netjets_C68A` | brand + subtype | Cessna Citation Latitude | 4 | 71/week |
| 53 | `united_A21N` | brand + subtype | Airbus A321neo | 4 | 68/week |
| 54 | `alaska_B39M` | brand + subtype | Boeing 737 MAX 9 | 4 | 60/week |
| 55 | `american-eagle_CRJ7` | brand + subtype | Bombardier CRJ-700 | 4 | 58/week; titles read "American Eagle" |
| 56 | `delta-connection_E75L` | brand + subtype | Embraer E175 | 4 | 57/week; titles read "Delta Connection" |
| 57 | `netjets_E55P` | brand + subtype | Embraer Phenom 300 | 4 | 57/week |
| 58 | `delta_B763` | brand + subtype | Boeing 767-300 | 4 | 54/week |
| 59 | `united_A319` | brand + subtype | Airbus A319 | 4 | 51/week |
| 60 | `american_A21N` | brand + subtype | Airbus A321neo | 4 | 47/week |
| 61 | `united-express_CRJ7` | brand + subtype | Bombardier CRJ-700 | 4 | 47/week; titles read "UNITED EXPRESS" |
| 62 | `american_A319` | brand + subtype | Airbus A319 | 4 | 45/week |
| 63 | `jetblue_BCS3` | brand + subtype | Airbus A220-300 | 4 | 44/week |
| 64 | `united_A320` | brand + subtype | Airbus A320 | 4 | 44/week |
| 65 | `air-canada_BCS3` | brand + subtype | Airbus A220-300 | 4 | 44/week; only non-US brand in the library |
| 66 | `delta_A320` | brand + subtype | Airbus A320 | 4 | 41/week |
| 67 | `flexjet_E545` | brand + subtype | Embraer Praetor 500 / Legacy 450 | 4 | 38/week |
| 68 | `delta_BCS3` | brand + subtype | Airbus A220-300 | 4 | 36/week |
| 69 | `delta_B753` | brand + subtype | Boeing 757-300 | 4 | 36/week |
| 70 | `american_B38M` | brand + subtype | Boeing 737 MAX 8 | 4 | 35/week |
| 71 | `flexjet_CL35` | brand + subtype | Bombardier Challenger 350 | 4 | 34/week |
| 72 | `delta-connection_E170` | brand + subtype | Embraer E170 | 4 | 33/week; correctly shorter than the E175 |
| 73 | `united_B737` | brand + subtype | Boeing 737-700 | 4 | 30/week |
| 74 | `frontier_A20N` | brand + subtype | Airbus A320neo | 4 | 30/week; photographic animal tail |
| 75 | `flexjet_E55P` | brand + subtype | Embraer Phenom 300 | 4 | 25/week; same airframe as 57, different livery |

**Coverage with these 75 images** (Ann Arbor, 15 NM, sample week): 89.4% of sightings get an
image, 50.6% get their exact livery. Batch 4 raised exact livery from 36.0% to 50.6% without
moving the "any image" number, which is exactly what a batch of exact liveries should do: it
replaces generic silhouettes on aircraft that were already covered.

### Lesson from batch 3

Two prompts produced the right *style* but the wrong *aircraft*, both for the same reason:
**the uploaded template decides the shape, and naming an out-of-family example invites it.**

- `ANY_GA-TWIN` asked for "a generic light twin-engine GA aircraft ... such as the Cessna 310,
  Beechcraft Baron", but the uploaded reference was a King Air, and the King Air is what came
  back. The family covers piston twins only.
- `ANY_TURBOPROP-SINGLE` listed "the Pilatus PC-12, Cessna Caravan" as examples. The Caravan
  is high-wing and isn't in that family; the model drew the Caravan.

So: upload a template that is already in the family, and name only in-family examples.

Both were then regenerated with an in-family template — a Cessna 310 for the piston twin and a
PC-12 for the turboprop single — and both came back correct (entries 48 and 49). The two
mistakes were kept as `ANY_KINGAIR` and `ANY_C208`, which they fit exactly, so nothing was lost.

### Lesson from batch 4

Two things that went wrong earlier were fixed by saying them out loud in the prompt, and both
worked on every attempt:

- **Naming the operating brand in the titles.** `american-eagle_CRJ7`, `united-express_CRJ7`
  and both Delta Connection E-Jets carry the regional brand, not the mainline one, because the
  prompt said "Make sure the fuselage titles read X, not just Y". Batch 2's
  `united-express_E75L` had to be regenerated for exactly this.
- **Naming the subtype to exclude.** The business jets each named the airframe to match *and*
  the one to avoid ("not a Citation X", "not a different Challenger variant"). All four
  distinct bizjet airframes came back correct and measurably different from each other.

The corollary to batch 3's lesson: the template drives the shape, but an explicit negative
("not an E175") is what keeps a near-identical subtype from drifting.

### Up next (candidates, no prompts yet)

The remaining blanks, unchanged by batch 4 since it only replaced generic silhouettes with
exact liveries: `ANY_BE35` (36 sightings/week), `ANY_DH8D` (35), `ANY_F900` (32), `ANY_EC55`
(28), `ANY_E120` (18), `ANY_A306` (17), `ANY_SF50` (15). The single biggest gap is the 379
sightings/week with no type code at all, which no image can fix.

With the planned library complete, the remaining gains are small and scattered: the seven keys
above are worth about 3% of "any image" combined. The higher-value work now is a second pass on
exact liveries for brands that still fall back to a family image.

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

## Batch 3 prompts (2026-09-16)

Nine images aimed at the biggest remaining blanks. Two of the first seven came back as a
different aircraft than the key expects and were renamed to what they actually depict, then
regenerated from an in-family template as entries 48 and 49 (see the lesson above).

### 41. `ANY_DA40`
- **Template:** Diamond DA40

```text
Use the uploaded Diamond DA40 template as the main reference and keep its exact side-profile geometry, including the low-wing layout, T-tail, and fixed landing gear. Render it as a generic Diamond DA40 in a clean neutral livery, with no branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 42. `ANY_KINGAIR`
- **Template:** twin-engine light aircraft reference (a King Air)
- **Note:** prompted as `ANY_GA-TWIN`. The uploaded template was a King Air, a cabin-class
  twin turboprop, so the result was renamed to `ANY_KINGAIR`, which it fits exactly
  (69 sightings/week). `ANY_GA-TWIN` still needs a piston twin.

```text
Use the uploaded twin-engine light aircraft reference as the main structural guide and preserve its side-profile geometry. Render it as a generic light twin-engine GA aircraft in a clean neutral livery, with no branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for aircraft such as the Cessna 310, Beechcraft Baron, and similar piston twins. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 43. `ANY_C208`
- **Template:** single-engine turboprop template (a Caravan)
- **Note:** prompted as `ANY_TURBOPROP-SINGLE`. Naming the Caravan among the examples got a
  Caravan, which is high-wing and outside that family, so it was renamed to `ANY_C208`
  (6 sightings/week). `ANY_TURBOPROP-SINGLE` still needs a PC-12.

```text
Use the uploaded single-engine turboprop template as the main reference and keep its exact side-profile geometry. Render it as a generic single-engine turboprop aircraft in a clean neutral livery, with no branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for aircraft such as the Pilatus PC-12, Cessna Caravan, and similar utility/business turboprops. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 44. `netjets_BIZJET-MIDSIZE`
- **Template:** midsize business jet, plus NetJets livery references

```text
Use the uploaded midsize business jet template as the main reference and keep its exact side-profile geometry. Apply a clean NetJets-style livery using the provided references, including the correct dark gray/black striping, understated branding, and neutral premium color treatment, but do not include a specific registration number. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text beyond the real livery markings. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 45. `delta_A330-FAM`
- **Template:** Airbus A330-300, plus Delta livery references

```text
Use the uploaded Airbus A330-300 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 46. `ANY_777-FAM`
- **Template:** Boeing 777-300ER

```text
Use the uploaded Boeing 777-300ER template as the main reference and keep its exact side-profile geometry. Render it as a generic Boeing 777 family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for 777-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 47. `ANY_A350-FAM`
- **Template:** Airbus A350-900

```text
Use the uploaded Airbus A350-900 template as the main reference and keep its exact side-profile geometry. Render it as a generic Airbus A350 family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for A350-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 48. `ANY_GA-TWIN`
- **Template:** Cessna 310
- **Note:** regeneration of entry 42. The in-family template and in-family examples fixed it.

```text
Use the uploaded Cessna 310 template as the main reference and keep its exact side-profile geometry. Render it as a generic light twin-engine piston GA aircraft in a clean neutral livery, with no branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for aircraft such as the Cessna 310/414, Beechcraft Baron, Piper PA-31/PA-34, and similar light piston twins. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 49. `ANY_TURBOPROP-SINGLE`
- **Template:** Pilatus PC-12
- **Note:** regeneration of entry 43. Naming the PC-12 as the template and dropping the Caravan
  from the examples fixed it.

```text
Use the uploaded Pilatus PC-12 template as the main reference and keep its exact side-profile geometry. Render it as a generic low-wing single-engine turboprop aircraft in a clean neutral livery, with no branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for aircraft such as the Pilatus PC-12, Daher TBM, Piper PA-46 turboprop variants, and similar low-wing retractable turboprops. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

## Batch 4 prompts (2026-09-16)

The 26 exact liveries. This is the batch called **C** when it was planned; it was generated
after batch 3 (planned as D), so the log numbering and the planning letters differ from here on.

### 50. `alaska_B739`
- **Template:** blank Boeing 737-900ER

```text
Use the uploaded blank Boeing 737-900ER template as the main reference and keep its exact side-profile geometry, including the split-scimitar winglets. Apply the current Alaska Airlines livery accurately using the provided references, including the Alaska wordmark, the signature Eskimo tail artwork, the correct fuselage colors, and the proper engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 51. `jetblue_A321`
- **Template:** blank Airbus A321

```text
Use the uploaded blank Airbus A321 template as the main reference and keep its exact side-profile geometry. Apply the current JetBlue livery accurately using the provided references, including the JetBlue wordmark, the correct tail pattern and colors, the fuselage treatment, and the proper engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 52. `netjets_C68A`
- **Template:** blank Cessna Citation Latitude
- **Note:** names the subtype explicitly to avoid a Citation X.

```text
Use an accurate blank Cessna Citation Latitude side-profile template as the main reference and keep its exact side-profile geometry. Be careful to match the Citation Latitude specifically, not a Citation X or another business jet subtype. Apply the current NetJets livery accurately using the provided references, including the correct dark gray and black striping, understated NetJets branding, tail treatment, and overall premium neutral color scheme. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text beyond the real livery markings, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 53. `united_A21N`
- **Template:** Airbus A321neo

```text
Use the uploaded Airbus A321neo template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately using the provided references, including the United wordmark, blue globe tail, fuselage colors, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 54. `alaska_B39M`
- **Template:** blank Boeing 737 MAX 9

```text
Use the uploaded blank Boeing 737 MAX 9 template as the main reference and keep its exact side-profile geometry. Apply the current Alaska Airlines livery accurately using the provided references, including the Alaska wordmark, the signature Eskimo tail artwork, the correct fuselage colors, and the proper engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 55. `american-eagle_CRJ7`
- **Template:** Bombardier CRJ-700
- **Note:** the explicit titles instruction worked; the fuselage reads "American Eagle".

```text
Use the uploaded Bombardier CRJ-700 template as the main reference and keep its exact side-profile geometry. Apply the current American Eagle livery accurately using the provided references, including the American Eagle wordmark, red-white-blue tail design, fuselage colors, and correct engine markings. Make sure the fuselage titles read “American Eagle,” not just “American.” Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 56. `delta-connection_E75L`
- **Template:** Embraer E175
- **Note:** titles correctly read "Delta Connection".

```text
Use the uploaded Embraer E175 template as the main reference and keep its exact side-profile geometry, preferably preserving the newer-style winglet shape if shown in the reference. Apply the current Delta Connection livery accurately using the provided references, including the Delta Connection wordmark, tail design, fuselage colors, and correct engine and winglet markings. Make sure the fuselage titles read “Delta Connection,” not just “Delta.” Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 57. `netjets_E55P`
- **Template:** blank Embraer Phenom 300

```text
Use an accurate blank Embraer Phenom 300 side-profile template as the main reference and keep its exact side-profile geometry. Be careful to match the Phenom 300 specifically, not a different light business jet subtype. Apply the current NetJets livery accurately using the provided references, including the correct dark gray and black striping, understated NetJets branding, tail treatment, and overall premium neutral color scheme. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text beyond the real livery markings, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 58. `delta_B763`
- **Template:** Boeing 767-300

```text
Use the uploaded Boeing 767-300 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 59. `united_A319`
- **Template:** Airbus A319

```text
Use the uploaded Airbus A319 template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately using the provided references, including the United wordmark, blue globe tail, fuselage colors, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 60. `american_A21N`
- **Template:** Airbus A321neo

```text
Use the uploaded Airbus A321neo template as the main reference and keep its exact side-profile geometry. Apply the current American Airlines livery accurately using the provided references, including the American wordmark, silver-gray fuselage treatment, red-white-blue tail design, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 61. `united-express_CRJ7`
- **Template:** Bombardier CRJ-700
- **Note:** titles correctly read "UNITED EXPRESS" — the batch 2 failure did not recur.

```text
Use the uploaded Bombardier CRJ-700 template as the main reference and keep its exact side-profile geometry. Apply the current United Express livery accurately using the provided references, including the correct United Express titles, blue globe tail, fuselage colors, and correct engine markings. Make sure the fuselage titles read “United Express,” not just “United.” Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 62. `american_A319`
- **Template:** Airbus A319

```text
Use the uploaded Airbus A319 template as the main reference and keep its exact side-profile geometry. Apply the current American Airlines livery accurately using the provided references, including the American wordmark, silver-gray fuselage treatment, red-white-blue tail design, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 63. `jetblue_BCS3`
- **Template:** Airbus A220-300

```text
Use the uploaded Airbus A220-300 template as the main reference and keep its exact side-profile geometry. Apply the current JetBlue livery accurately using the provided references, including the JetBlue wordmark, the correct tail pattern and colors, the fuselage treatment, and the proper engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 64. `united_A320`
- **Template:** Airbus A320

```text
Use the uploaded Airbus A320 template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately using the provided references, including the United wordmark, blue globe tail, fuselage colors, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 65. `air-canada_BCS3`
- **Template:** Airbus A220-300

```text
Use the uploaded Airbus A220-300 template as the main reference and keep its exact side-profile geometry. Apply the current Air Canada livery accurately using the provided references, including the Air Canada wordmark, the black-and-white fuselage treatment, the red maple leaf roundel tail design, and the correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 66. `delta_A320`
- **Template:** Airbus A320

```text
Use the uploaded Airbus A320 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 67. `flexjet_E545`
- **Template:** blank Embraer Praetor 500 / Legacy 450

```text
Use an accurate blank Embraer Praetor 500 / Legacy 450 side-profile template as the main reference and keep its exact side-profile geometry. Be careful to match the Praetor 500 / Legacy 450 airframe specifically, not a different Embraer business jet. Apply the current Flexjet livery accurately using the provided references, including the correct Flexjet branding, fuselage striping and color treatment, tail design, and engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text beyond the real livery markings, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 68. `delta_BCS3`
- **Template:** Airbus A220-300

```text
Use the uploaded Airbus A220-300 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 69. `delta_B753`
- **Template:** Boeing 757-300

```text
Use the uploaded Boeing 757-300 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Air Lines livery accurately using the provided references, including the Delta wordmark, tail design, fuselage colors, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 70. `american_B38M`
- **Template:** Boeing 737 MAX 8

```text
Use the uploaded Boeing 737 MAX 8 template as the main reference and keep its exact side-profile geometry. Apply the current American Airlines livery accurately using the provided references, including the American wordmark, silver-gray fuselage treatment, red-white-blue tail design, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 71. `flexjet_CL35`
- **Template:** blank Bombardier Challenger 350

```text
Use an accurate blank Bombardier Challenger 350 side-profile template as the main reference and keep its exact side-profile geometry. Be careful to match the Challenger 350 specifically, not a different Challenger variant or another large-cabin business jet. Apply the current Flexjet livery accurately using the provided references, including the correct Flexjet branding, fuselage striping and color treatment, tail design, and engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text beyond the real livery markings, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 72. `delta-connection_E170`
- **Template:** Embraer E170
- **Note:** drawn shorter than entry 56's E175, in the right direction and proportion.

```text
Use an exact Embraer E170 side-profile template as the main reference and keep its exact side-profile geometry. Do not substitute an E175 or preserve E175 proportions if the uploaded reference is not a true E170. Apply the current Delta Connection livery accurately using the provided references, including the Delta Connection wordmark, tail design, fuselage colors, and correct engine and winglet markings. Make sure the fuselage titles read “Delta Connection,” not just “Delta.” Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 73. `united_B737`
- **Template:** Boeing 737-700

```text
Use the uploaded Boeing 737-700 template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately using the provided references, including the United wordmark, blue globe tail, fuselage colors, and correct engine and winglet markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 74. `frontier_A20N`
- **Template:** Airbus A320neo
- **Note:** the only livery in the library with photographic tail artwork (a mountain lion).

```text
Use the uploaded Airbus A320neo template as the main reference and keep its exact side-profile geometry. Apply the current Frontier Airlines livery accurately using the provided references, including the large green FRONTIER wordmark, white fuselage, green engine treatment, current wildlife-themed tail artwork, and correct winglet markings. Use a representative current Frontier animal-tail design from the provided references without including a specific registration number. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text beyond the real livery markings, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 75. `flexjet_E55P`
- **Template:** blank Embraer Phenom 300
- **Note:** same airframe as entry 57 in a different livery, which is the point of the library.

```text
Use an accurate blank Embraer Phenom 300 side-profile template as the main reference and keep its exact side-profile geometry. Be careful to match the Phenom 300 specifically, not a different light business jet subtype. Apply the current Flexjet livery accurately using the provided references, including the correct Flexjet branding, fuselage striping and color treatment, tail design, and engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text beyond the real livery markings, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```
