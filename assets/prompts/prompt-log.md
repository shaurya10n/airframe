# Artwork prompt log

Every image in `assets/aircraft/` gets an entry here with the exact prompt used, so the
series stays consistent and any image can be regenerated.

**Process:** give GPT a blank side-profile template of the aircraft, then a prompt that
applies a specific or generic livery in the shared house style. Save the result as
`assets/aircraft/<artwork key>.png`. See the README for the key naming rules.

## Status

| # | Artwork key | Level | Base template | Batch | Status | Notes |
|---|---|---|---|---|---|---|
| 1 | `united_B39M` | brand + subtype | Boeing 737 MAX 9 | 1 (2026-09-15) | generated | Reference image for the series style |
| 2 | `delta-connection_CRJ9` | brand + subtype | Bombardier CRJ-900 | 1 | generated | Check the titles read "Delta Connection", not just "Delta" |
| 3 | `american_B788` | brand + subtype | Boeing 787-8 | 1 | generated | |
| 4 | `ANY_A320-FAM` | generic family | Airbus A320 | 1 | generated | |
| 5 | `ANY_CRJ-FAM` | generic family | Bombardier CRJ-900 | 1 | generated | |
| 6 | `ANY_787-FAM` | generic family | Boeing 787-9 | 1 | generated | |
| 7 | `ANY_BIZJET-MIDSIZE` | generic family | Learjet 60 | 1 | generated | Most midsize traffic is Citation Excel, Challenger 300/350 and Hawker 800. The LJ60 is slimmer, and `aircraft_families.csv` files it as a light jet |
| 8 | `ANY_GA-HIGHWING` | generic family | High-wing single (Cessna-style) | 1 | generated | Cessna 172/152/182 have fixed gear, so gear down is the accurate look |

### Up next (planned, no prompt yet)

`ANY_737NG`, `ANY_EJET-E1`, `united-express_E75L`, `delta_A21N`, `delta-connection_CRJ7`,
`delta_B739`, `american_B738`, `delta_B712`.

## Prompt template

Batch 1 prompts are built from these blocks. Reuse them so new images match the series.

**1. Reference**
> Use the uploaded blank {AIRCRAFT} template as the main reference and keep its exact side-profile geometry.

**2a. Livery (specific)**
> Apply the current {AIRLINE / BRAND} livery accurately using the provided references, including {KEY LIVERY ELEMENTS: wordmark, tail design, fuselage colors, engine markings}.

**2b. Livery (generic)**
> Render it as a generic {FAMILY} aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for {FAMILY} aircraft.

**3. Style (identical for every image)**
> Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail.

**4. Composition**
> Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number.

**5. Background**
> Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.

## Prompts used

### 1. `united_B39M`
- **File:** `assets/aircraft/united_B39M.png`
- **Template:** blank Boeing 737 MAX 9
- **Batch:** 1 (2026-09-15)

```text
Use the uploaded blank Boeing 737 MAX 9 template as the main reference and keep its exact side-profile geometry. Apply the current United Airlines livery accurately: white fuselage, blue UNITED wordmark, blue engines, blue globe tail, and correct winglet colors. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, so avoid glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 2. `delta-connection_CRJ9`
- **File:** `assets/aircraft/delta-connection_CRJ9.png`
- **Template:** blank Bombardier CRJ-900, plus Delta Connection livery reference images
- **Batch:** 1 (2026-09-15)
- **Note:** sent as a follow-up in the same chat as #1, hence "That is good. Now…"

```text
That is good. Now use the uploaded blank Bombardier CRJ-900 template as the main reference and keep its exact side-profile geometry. Apply the current Delta Connection livery accurately using the provided references, including the correct Delta wordmark, tail design, fuselage colors, and engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, so avoid glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 3. `american_B788`
- **File:** `assets/aircraft/american_B788.png`
- **Template:** blank Boeing 787-8, plus American Airlines livery reference images
- **Batch:** 1 (2026-09-15)

```text
Use the uploaded blank Boeing 787-8 template as the main reference and keep its exact side-profile geometry. Apply the current American Airlines livery accurately using the provided references, including the silver/gray fuselage treatment, American wordmark, striped red-white-blue tail, and correct engine markings. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, so avoid glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text, and do not include a specific registration number. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 4. `ANY_A320-FAM`
- **File:** `assets/aircraft/ANY_A320-FAM.png`
- **Template:** blank Airbus A320
- **Batch:** 1 (2026-09-15)

```text
Use the uploaded blank Airbus A320 template as the main reference and keep its exact side-profile geometry. Render it as a generic A320-family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple, elegant, and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback aircraft image. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, so avoid glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 5. `ANY_CRJ-FAM`
- **File:** `assets/aircraft/ANY_CRJ-FAM.png`
- **Template:** blank Bombardier CRJ-900
- **Batch:** 1 (2026-09-15)

```text
Use the uploaded blank Bombardier CRJ-900 template as the main reference and keep its exact side-profile geometry. Render it as a generic CRJ-family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for CRJ-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 6. `ANY_787-FAM`
- **File:** `assets/aircraft/ANY_787-FAM.png`
- **Template:** blank Boeing 787-9
- **Batch:** 1 (2026-09-15)

```text
Use the uploaded blank Boeing 787-9 template as the main reference and keep its exact side-profile geometry. Render it as a generic 787-family aircraft in a clean neutral livery, with no airline branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for 787-family aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 7. `ANY_BIZJET-MIDSIZE`
- **File:** `assets/aircraft/ANY_BIZJET-MIDSIZE.png`
- **Template:** blank Learjet 60
- **Batch:** 1 (2026-09-15)

```text
Use the uploaded blank Learjet 60 template as the main reference and keep its exact side-profile geometry. Render it as a generic midsize business jet in a clean neutral livery, with no company branding and no specific registration number. Keep the paint scheme simple and realistic, using soft whites and light grays with subtle neutral accents so it works well as a fallback image for midsize business jets. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right, with landing gear retracted. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```

### 8. `ANY_GA-HIGHWING`
- **File:** `assets/aircraft/ANY_GA-HIGHWING.png`
- **Template:** high-wing single-engine aircraft reference
- **Batch:** 1 (2026-09-15)

```text
Use the uploaded high-wing single-engine aircraft reference as the main structural guide and preserve its side-profile geometry. Render it as a generic high-wing GA aircraft in a clean neutral livery, with no branding and no registration number. Keep the paint scheme simple and realistic using soft whites and light grays with subtle neutral accents so it works well as a fallback image for Cessna-style high-wing piston aircraft. Render it as a premium printed aviation illustration with a soft papery matte aesthetic — subtle paper texture, muted colors, gentle shading, clean edges, and a calm editorial feel. Keep it optimized for a color e-ink display, avoiding glossy reflections, heavy gradients, and overly fine detail. Show a single isolated aircraft only, centered, facing left-to-right. Prefer the landing gear retracted if it can be done without distorting the aircraft. Do not add scenery, poster elements, or extra text. Prefer a transparent background; if not possible, use a flat warm off-white paper-like background.
```
