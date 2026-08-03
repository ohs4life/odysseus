---
name: panel-catalog
description: "Overview of the Nutrients Rx lab panel — 17 panels containing 89 tests, plus 10 deep-dive add-ons and the OPTIMAL DNA panel (100+ SNPs). Use this when a customer asks 'what's on the panel?', 'what tests do I get?', 'what's included?', or wants a high-level map of what Nutrients Rx measures."
version: 1.0.0
category: ohs-lab-testing
status: published
shared: true
owner: ohs-admin
confidence: 0.95
source: user
created: "2026-08-02T18:30:00Z"
---

# Nutrients Rx — Lab Panel Catalog

## When to Use
When the user (customer or employee) asks any variant of:
- "What tests are on the panel?"
- "What's included in Nutrients Rx?"
- "How many tests do I get?"
- "What's the OPTIMAL DNA panel?"
- "What are the deep dives?"
- An employee / practitioner asking for the high-level menu to walk a customer through.

## Procedure

### 1. The headline numbers
- **89 tests** in the standard panel.
- **17 standard panels** (e.g., CBC, Comprehensive Metabolic Panel, Lipid Panel, Urinalysis, …).
- **10 "Deep Dive" add-ons** (Thyroid, Female Hormone, Male Hormone, D-Dimer, Troponin T, Insulin, AM Cortisol, Homocysteine, GlycA, CA 19-9).
- **OPTIMAL DNA** is a separate panel with **100+ SNPs** across ~25 categories.

### 2. The 17 standard panels and their major markers

| Panel | Key tests |
|---|---|
| **CBC (Includes Diff/PLT)** | Hemoglobin, Hematocrit, WBC, RBC, MCV, MCH, MCHC, RDW, Platelet Count, MPV, all absolute and % differentials (21 values total) |
| **Comprehensive Metabolic Panel (CMP)** | Glucose, Calcium, Sodium, Potassium, Chloride, CO2, Total Protein, Albumin, Globulin, A/G ratio, ALP, AST, ALT, Bilirubin (Direct + Total), eGFR, Creatinine, BUN, BUN/Creatinine ratio (~20 values) |
| **Hemoglobin A1c** | A1c |
| **hs-CRP** | High-sensitivity C-Reactive Protein (inflammation) |
| **Iron and Total Iron Binding Capacity** | Iron, TIBC, % Saturation |
| **Lipid Panel, Standard** | Total Cholesterol, HDL, LDL, Non-HDL, Triglycerides, CHOL/HDL ratio |
| **Magnesium** | Magnesium (RBC) |
| **Sex Hormone Binding Globulin (SHBG)** | SHBG |
| **Testosterone, Free, Bio And Total, MS** | Total / Free / Bioavailable Testosterone (sex-specific ranges) |
| **TSH** | Thyroid-Stimulating Hormone |
| **Uric Acid** | Uric Acid |
| **Urinalysis, Complete** | Color, Appearance, Specific Gravity, pH, Protein, Glucose, Ketones, Occult Blood, Leukocyte Esterase, Nitrite, WBC, RBC, Epithelial cells, Bacteria, Casts, Crystals (~26 values) |
| **Vitamin B12** | B12 |
| **Vitamin D, 25-OH, Total, LA** | Vitamin D |
| **Estrogen** | Total Estrogens |
| **PSA** | Prostate-Specific Antigen (Total) |
| **Ferritin** | Ferritin (sex-specific ranges) |

### 3. The 10 Deep Dives (sold separately as add-ons)

| Deep Dive | Tests |
|---|---|
| **Thyroid** | T4 Free (Direct), TSH, Thyroglobulin Antibody, T3 Free, Thyroid Peroxidase (TPO) Antibody, Reverse T3 |
| **Female Hormone** | Estradiol, DHEA, Total Estrogens, Free Androgen Index, Total Testosterone, SHBG, LH, Progesterone, FSH, Prolactin |
| **Male Hormone** | DHEA, Total Estrogens, Free Androgen Index, Total Testosterone, SHBG, LH, Progesterone, FSH, Prolactin |
| **D-Dimer** | D-Dimer |
| **Troponin T** | Troponin T |
| **Insulin** | Fasting Insulin |
| **Cortisol - AM** | Morning Cortisol |
| **Homocysteine** | Homocysteine |
| **GlycA** | GlycA (inflammation / glycemic marker) |
| **CA 19-9** | Carbohydrate Antigen 19-9 |

### 4. OPTIMAL DNA (separate product)
100+ SNPs across ~25 categories. See `ohs-lab-testing/optimal-dna-overview` for the full list. Categories include: methylation (MTHFR and others), stress response, antioxidants / glutathione, detoxification, histamine sensitivity, inflammation, DNA repair, neurotransmitters, energy, oxidative stress, fat & carbohydrate metabolism, eating behaviors, vitamin deficiencies, food sensitivities, blood sugar & cardiovascular, obesity & weight loss, strength potential, endurance vs. sprinter, VO2 Max, cardiovascular health, fat loss response to exercise.

## Pitfalls
- **The 89-test count is for the *standard* panel, not including deep dives or DNA.** When the customer asks "how many tests?", clarify which:
  - Standard panel only: 89 tests in 17 panels
  - Add all 10 deep dives: 89 + ~30 more = ~120 markers
  - Add OPTIMAL DNA: 89 + ~30 + 100+ SNPs
- **Do not call the panel a "comprehensive" panel if the customer hasn't bought the deep dives.** "Standard" vs. "with deep dives" is a real distinction.
- **Do not list every individual test from the source CSV in customer-facing copy.** Use the 17-panel grouping (above) — the granularity of the 89 individual values is for the agent's reference (see `ohs-lab-testing/test-reference-*` skills).
- **Do not interpret any of the tests** — see `ohs-compliance/disclaimers`. Describe what's on the panel; let the customer's provider interpret.

## Verification
- Source-of-truth for the panel list: `knowledgebase/labs/labs-list.csv` (89 Tests for NRx in 17 Panels + Deep Dives + OPTIMAL DNA).
- Source-of-truth for the test reference details: `knowledgebase/labs/ohs_lab_test_descriptions_v3.md`.
- Related skills: `ohs-lab-testing/nutrients-rx-customer-journey` (how the program works), `ohs-lab-testing/optimal-dna-overview` (DNA detail), `ohs-lab-testing/test-reference-*` (per-group test details), `ohs-compliance/disclaimers` (required framing).

## Anything else

### Five-level range system (used on every test result)
Every test on the panel is reported with **five levels** to distinguish "lab says you're fine" from "your body is at its best":

- **Clinical Low** — below the lab range. Often means a real health problem.
- **Functional Low** — in the lab range but on the low end. Not sick, but not at your best.
- **Optimal** — the level where your body works its best. The goal.
- **Functional High** — in the lab range but on the high end. Body is under stress.
- **Clinical High** — above the lab range. Often means a real health problem.

The functional / optimal ranges are tighter than the lab's clinical range. Being "in range" by the lab's standard does **not** mean you're at your best — it just means no disease has been diagnosed.

### Sex-specific ranges
Many markers have separate reference ranges for males vs. females (e.g., testosterone, ferritin, hemoglobin). The skill descriptions in `test-reference-*` mark these with **M** / **F** / **B** (both).

### Customer journey
To see how the customer actually goes through this — buying Nutrients Rx, registering the portal, getting the blood drawn, viewing the report, and ordering the custom pak — see `ohs-lab-testing/nutrients-rx-customer-journey`.
