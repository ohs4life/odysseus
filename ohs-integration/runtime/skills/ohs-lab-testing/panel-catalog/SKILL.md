---
name: panel-catalog
description: "Overview of the OHS lab testing menu — the 17-panel core Nutrients Rx Lab Work (89 tests, generates a Custom Health Pak), the 10 Deep Dives (add-ons, do NOT generate a Custom Pak), and the OPTIMAL DNA panel (100+ SNPs, stand-alone). Use this when a customer asks 'what's on the panel?', 'what tests do I get?', 'do the Deep Dives give me a Custom Pak?', or wants a high-level map of OHS lab offerings."
version: 1.1.0
category: ohs-lab-testing
status: published
shared: true
owner: ohs-admin
confidence: 0.95
source: user
created: "2026-08-02T18:30:00Z"
updated: "2026-08-03T10:30:00Z"
---

# OHS Lab Testing — Panel Catalog

## When to Use
When the user (customer or employee) asks any variant of:
- "What tests are on the panel?"
- "What's included in Nutrients Rx?"
- "How many tests do I get?"
- "What's the OPTIMAL DNA panel?"
- "What are the deep dives?"
- **"Do the Deep Dives give me a Custom Health Pak?"** → No, only the core Nutrients Rx does.
- An employee / practitioner asking for the high-level menu to walk a customer through.

## Critical distinction — which lab products generate a Custom Health Pak?

| Product | SKU / price | Generates a Custom Health Pak? | Output |
|---|---|---|---|
| **Core Nutrients Rx Lab Work** | `nutrients-rx`, $349 | **Yes** | 89 tests in 17 panels → "Buy Customized Pak" button after results → $149 Custom Health Pak (built to order, separate purchase) |
| **OPTIMAL DNA** | `optimal-dna`, $399 | No | 100+ SNPs across ~25 categories — stand-alone wellness product |
| **Nutrients Rx Deep Dives** | `nutrients-rx-lab-work-deep-dives`, $115 | **No** | 10 add-on panels — see results and get non-pak product recommendations (liquids, powders, large tablets) |

The Deep Dives are designed to **complement** the core Nutrients Rx, not replace it. If a customer only buys a Deep Dive (e.g., the Female Hormone Panel) without the core, they will see their results and get non-pak product recs — but no Custom Health Pak.

## Procedure

### 1. The headline numbers
- **89 tests** in the standard Nutrients Rx panel.
- **17 standard panels** (e.g., CBC, Comprehensive Metabolic Panel, Lipid Panel, Urinalysis, …).
- **10 "Deep Dive" add-ons** (Thyroid, Female Hormone, Male Hormone, D-Dimer, Troponin T, Insulin, AM Cortisol, Homocysteine, GlycA, CA 19-9).
- **OPTIMAL DNA** is a separate stand-alone panel with **100+ SNPs** across ~25 categories.

### 2. The 17 standard panels (core Nutrients Rx — generates a Custom Health Pak)

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

### 3. The 10 Deep Dives (add-ons — do NOT generate a Custom Health Pak)

| Deep Dive | Tests | Notes |
|---|---|---|
| **Thyroid** | T4 Free (Direct), TSH, Thyroglobulin Antibody, T3 Free, Thyroid Peroxidase (TPO) Antibody, Reverse T3 | Add-on to core Nutrients Rx |
| **Female Hormone** | Estradiol, DHEA, Total Estrogens, Free Androgen Index, Total Testosterone, SHBG, LH, Progesterone, FSH, Prolactin | Add-on to core Nutrients Rx |
| **Male Hormone** | DHEA, Total Estrogens, Free Androgen Index, Total Testosterone, SHBG, LH, Progesterone, FSH, Prolactin | Add-on to core Nutrients Rx |
| **D-Dimer** | D-Dimer | Stand-alone or add-on |
| **Troponin T** | Troponin T | Stand-alone or add-on |
| **Insulin** | Fasting Insulin | Stand-alone or add-on |
| **Cortisol - AM** | Morning Cortisol | Stand-alone or add-on |
| **Homocysteine** | Homocysteine | Stand-alone or add-on |
| **GlycA** | GlycA (inflammation / glycemic marker) | Stand-alone or add-on |
| **CA 19-9** | Carbohydrate Antigen 19-9 | Stand-alone or add-on |

**What customers get from a Deep Dive (without the core):**
- See the panel results in the Nutrients Rx portal (color-coded optimal / functional / clinical ranges)
- Some information about each marker (what it is, what the ranges mean)
- Product recommendations for **non-pak-form items** — i.e., products that don't fit in a custom pak like liquids, powders, or large tablets
- **NOT** a "Buy Customized Pak" button
- **NOT** a Custom Health Pak

### 4. OPTIMAL DNA (separate product, no pak)
100+ SNPs across ~25 categories. See `ohs-lab-testing/optimal-dna-overview` for the full list. Categories include: methylation (MTHFR and others), stress response, antioxidants / glutathione, detoxification, histamine sensitivity, inflammation, DNA repair, neurotransmitters, energy, oxidative stress, fat & carbohydrate metabolism, eating behaviors, vitamin deficiencies, food sensitivities, blood sugar & cardiovascular, obesity & weight loss, strength potential, endurance vs. sprinter, VO2 Max, cardiovascular health, fat loss response to exercise. OPTIMAL DNA does **not** generate a Custom Health Pak.

### 5. Lab partners
OHS uses **LabCorp and Quest Diagnostics** for blood draws outside the Pima, AZ area. The Nutrients Rx portal's "Find a Lab" tool shows locations from these two networks. If the customer is near Pima, AZ, they can also use OHS's private lab.

## Pitfalls
- **Deep Dives do NOT generate a Custom Health Pak.** This is the most-asked-about question. Only the core Nutrients Rx Lab Work generates a pak. Don't say "yes" to a customer asking about a Deep Dive.
- **Deep Dives are complementary, not standalone replacements for the core.** A customer who skips the core and only buys Deep Dives gets results + non-pak product recs, but no custom pak.
- **OPTIMAL DNA does NOT generate a Custom Health Pak either.** It's a stand-alone wellness product.
- **The 89-test count is for the *standard* panel, not including deep dives or DNA.** When the customer asks "how many tests?", clarify which:
  - Standard panel only: 89 tests in 17 panels
  - Add all 10 deep dives: 89 + ~30 more = ~120 markers
  - Add OPTIMAL DNA: 89 + ~30 + 100+ SNPs
- **Do not call the panel a "comprehensive" panel if the customer hasn't bought the deep dives.** "Standard" vs. "with deep dives" is a real distinction.
- **Do not list every individual test from the source CSV in customer-facing copy.** Use the 17-panel grouping (above) — the granularity of the 89 individual values is for the agent's reference (see `ohs-lab-testing/test-reference-*` skills).
- **Do not interpret any of the tests.** OHS provides *information* (what the marker is, what the ranges mean) but not *interpretation* (what it means for the customer's health, what to do about it). See `ohs-compliance/disclaimers` and the "share with your provider" framing in `ohs-lab-testing/nutrients-rx-customer-journey`.
- **Lab partners are LabCorp and Quest Diagnostics only.** Don't tell customers to look for other networks.

## Verification
- Source-of-truth for the panel list: `knowledgebase/labs/labs-list.csv` (89 Tests for NRx in 17 Panels + Deep Dives + OPTIMAL DNA).
- Source-of-truth for the test reference details: `knowledgebase/labs/ohs_lab_test_descriptions_v3.md`.
- Source-of-truth for the core-vs-Deep-Dive behavior: operator confirmation 2026-08-03 ("Deep Dives do not generate a custom pak, Only the Nutrients Rx lab work generates the custom pak recommendation").
- Source-of-truth for the lab partner: operator confirmation 2026-08-03 ("We only offer LabCorp and Quest Diagnostics").
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
To see how the customer actually goes through this — buying Nutrients Rx, registering the portal, getting the blood drawn at LabCorp or Quest (or OHS's Pima lab), viewing the report, and ordering the custom pak — see `ohs-lab-testing/nutrients-rx-customer-journey`.
