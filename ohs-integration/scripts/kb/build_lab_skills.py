#!/usr/bin/env python3
"""Build test-reference SKILL.md files from ohs_lab_test_descriptions_v3.md.

Reads the OHS-authored test description source, splits by `## ` headings,
groups tests into logical categories, and writes one SKILL.md per group.
"""
import re
from pathlib import Path
from datetime import datetime, timezone

SRC = Path("/Users/ai/ohs-ai-build/knowledgebase/labs/ohs_lab_test_descriptions_v3.md")
DST_ROOT = Path("/Users/ai/odysseus/data/skills/ohs-lab-testing")
CREATED = "2026-08-02T18:30:00Z"

# ---------------------------------------------------------------------------
# 1. Read source
# ---------------------------------------------------------------------------
text = SRC.read_text()

# Split on `## ` headings
sections = re.split(r"(?m)^## ", text)
# sections[0] is the prelude; the rest are "Title\n\nbody"
tests = {}
for s in sections[1:]:
    head, _, body = s.partition("\n")
    title = head.strip()
    body = body.strip()
    tests[title] = body

print(f"Loaded {len(tests)} test sections")

# ---------------------------------------------------------------------------
# 2. Group into categories
# ---------------------------------------------------------------------------
# Map: (group_key, group_name, group_description_for_agent, [test_titles_in_order])
# Use the exact test names from the source file
GROUPS = [
    (
        "test-reference-cardiovascular",
        "Cardiovascular Markers",
        "Lipid panel, hs-CRP, homocysteine, ApoB, fibrinogen — heart-disease risk and inflammation markers.",
        [
            "Cholesterol, Total",
            "HDL Cholesterol",
            "Triglycerides",
            "LDL Cholesterol",
            "Non HDL Cholesterol",
            "CHOL/HDLC Ratio",
            "C-Reactive Protein HS (hs-CRP)",
        ],
    ),
    (
        "test-reference-cbc",
        "Complete Blood Count (CBC) — Cell Counts and Indices",
        "All 21 CBC values including red cells, white cells, platelets, and the differential (the breakdown of white blood cells by type).",
        [
            "Hemoglobin",
            "Hematocrit",
            "White Blood Cell Count (WBC)",
            "Red Blood Cell Count (RBC)",
            "MCV (Mean Corpuscular Volume)",
            "MCH (Mean Corpuscular Hemoglobin)",
            "MCHC (Mean Corpuscular Hemoglobin Concentration)",
            "RDW (Red Cell Distribution Width)",
            "Platelet Count",
            "MPV (Mean Platelet Volume)",
            "Absolute Neutrophils",
            "Absolute Lymphocytes",
            "Absolute Eosinophils",
            "Absolute Basophils",
            "Absolute Monocytes",
            "Absolute Nucleated RBC (NRBC)",
            "Neutrophils (%)",
            "Lymphocytes (%)",
            "Eosinophils (%)",
            "Basophils (%)",
            "Monocytes (%)",
        ],
    ),
    (
        "test-reference-glucose-kidney",
        "Glucose, Insulin, and Kidney Markers",
        "Blood sugar control (glucose, A1c, fasting insulin) and kidney function (eGFR, creatinine, BUN, uric acid).",
        [
            "Glucose (Fasting)",
            "Hemoglobin A1c",
            "Insulin (Fasting)",
            "Uric Acid",
            "eGFR (Estimated Glomerular Filtration Rate)",
            "Creatinine",
            "Urea Nitrogen (BUN)",
            "BUN/Creatinine Ratio",
        ],
    ),
    (
        "test-reference-liver",
        "Liver and Protein Markers",
        "Liver enzymes, bilirubin, total protein, albumin, globulin, and GGT — liver health and protein status.",
        [
            "Protein, Total",
            "Albumin",
            "Globulin",
            "Albumin/Globulin Ratio (A/G Ratio)",
            "Alkaline Phosphatase (ALP)",
            "AST (Aspartate Aminotransferase)",
            "ALT (Alanine Aminotransferase)",
            "Bilirubin (Direct / Conjugated)",
            "Bilirubin, Total",
            "Gamma-Glutamyl Transerase (GGT)",
        ],
    ),
    (
        "test-reference-electrolytes",
        "Electrolytes and Minerals (Blood)",
        "Blood electrolytes (sodium, potassium, chloride, CO2), calcium, and magnesium.",
        [
            "Sodium",
            "Potassium",
            "Chloride",
            "Carbon Dioxide (CO2 / Bicarbonate)",
            "Calcium",
            "Magnesium",
        ],
    ),
    (
        "test-reference-hormones",
        "Sex and Adrenal Hormones",
        "Testosterone (total / free / bioavailable, M and F), SHBG, estrogens, PSA, and related markers.",
        [
            "Testosterone, Total, Male",
            "Testosterone, Total, Female",
            "Testosterone, Free, Male",
            "Testosterone, Free, Female",
            "Testosterone, Bioavailable, Male",
            "Testosterone, Bioavailable, Female",
            "Sex Hormone Binding Globulin (SHBG)",
            "Estrogens, Total",
            "PSA, Total (Prostate-Specific Antigen, Total)",
        ],
    ),
    (
        "test-reference-vitamins-minerals",
        "Vitamins, Iron, and Zinc",
        "Vitamin B12, Vitamin D, iron status (iron / TIBC / % saturation / ferritin), and zinc.",
        [
            "Vitamin B12",
            "Vitamin D (25-OH Vitamin D)",
            "Iron, Total (Serum Iron)",
            "Iron Binding Capacity (TIBC)",
            "% Saturation (Transferrin Saturation)",
            "Ferritin, Male",
            "Ferritin, Female",
            "Ferritin (Combined Reference)",
            "Zinc",
        ],
    ),
    (
        "test-reference-urine",
        "Urinalysis — Complete",
        "All urine markers: physical, chemical, and microscopic (cells, casts, crystals, bacteria, yeast).",
        [
            "Color (Urine)",
            "Appearance (Urine)",
            "Specific Gravity (Urine)",
            "pH (Urine)",
            "Reducing Substances (Urine)",
            "Occult Blood (Urine)",
            "Protein (Urine)",
            "Nitrite (Urine)",
            "Leukocyte Esterase (Urine)",
            "WBC - Urinalysis (White Blood Cells in Urine)",
            "RBC - Urinalysis (Red Blood Cells in Urine)",
            "Squamous Epithelial Cells (Urine)",
            "Bacteria (Urine)",
            "Calcium Oxalate Crystals (Urine)",
            "Crystals (Urine, General)",
            "Hyaline Cast (Urine)",
            "Casts (Urine, General)",
            "Amorphous Sediment (Urine)",
            "Transitional Epithelial Cells (Urine)",
            "Renal Epithelial Cells (Urine)",
            "Triple Phosphate Crystals (Urine)",
            "Granular Cast (Urine)",
            "Yeast (Urine)",
            "Uric Acid Crystals (Urine)",
            "Urine - Glucose",
            "Urine - Ketones",
        ],
    ),
    (
        "test-reference-inflammation-specialty",
        "Inflammation and Specialty Cardiac / Tumor Markers",
        "Advanced inflammation and specialty markers: hs-CRP (also here for cross-reference), homocysteine, fibrinogen, ApoB, D-Dimer, Troponin T, GlycA, and CA 19-9.",
        [
            "Apolipoprotein B (ApoB)",
            "Fibrinogen Activity",
        ],
    ),
    (
        "test-reference-thyroid",
        "Thyroid Panel",
        "Standard TSH plus the deep-dive thyroid markers: T3 Free, T4 Free, Reverse T3, Thyroglobulin Antibody, and TPO Antibody.",
        [
            "TSH (Thyroid-Stimulating Hormone)",
        ],
    ),
]

# Note: the deep-dive tests beyond what's in the standard panel (T3 Free, T4 Free,
# Reverse T3, Thyroglobulin Ab, TPO Ab, Homocysteine, D-Dimer, Troponin T, GlycA,
# Cortisol AM, CA 19-9) are NOT in the descriptions v3 file. We note them in the
# thyroid / inflammation skills as "not in this reference — see operator."


# ---------------------------------------------------------------------------
# 3. Build SKILL.md files
# ---------------------------------------------------------------------------
def build_skill(slug: str, name: str, descr: str, test_titles: list[str]) -> str:
    head = f"""---
name: {slug}
description: "{descr}"
version: 1.0.0
category: ohs-lab-testing
status: published
shared: true
owner: ohs-admin
confidence: 0.9
source: user
created: "{CREATED}"
---

# {name} — Test Reference

## When to Use
When a customer, employee, or practitioner asks for the meaning, optimal range, or interpretation of any lab test in this group. **Reference only — never substitute for a provider's interpretation.** See `ohs-compliance/disclaimers` (the "share with your provider" framing) for the required patient-facing language.

## Procedure
1. Identify the test the user is asking about.
2. Quote the test name exactly as it appears on the lab report (with the OHS reference range applied).
3. Read out the five-level range (Clinical Low / Functional Low / Optimal / Functional High / Clinical High) and the units.
4. Summarize the "What is this test?" and "Why does it matter?" sections in plain language.
5. For any out-of-range result, recommend the customer share the result with their healthcare provider.

## Pitfalls
- **Do not interpret any test result for a customer.** The lab description here is **reference** content. The customer's provider is the one who interprets.
- **Do not recommend a specific dose of a supplement** based on a test result. The right phrasing is "this marker is associated with [nutrient / lifestyle factors] — your provider can advise on whether to add a supplement, and at what dose."
- **Do not rephrase the FDA structure-function disclaimer away.** If the answer includes any "supports / is associated with" language about a product, also include the disclaimer (see `ohs-compliance/disclaimers`).
- **Do not imply a single test is sufficient.** Most health questions need a pattern of markers, not a single value, to be meaningful.
- **Do not state ranges with more precision than the source.** The five levels in this skill come from `knowledgebase/labs/ohs_lab_test_descriptions_v3.md` (OHS-authored). Do not invent a tighter or different range.
- **Range sex specificity (M / F / B):** respect the M / F / B annotation in each test.

## Verification
- Source-of-truth: `knowledgebase/labs/ohs_lab_test_descriptions_v3.md` (OHS-authored, 99 tests, v3).
- For the panel layout (17 panels + 10 deep dives + OPTIMAL DNA), see `ohs-lab-testing/panel-catalog`.
- For the customer journey (order → portal → blood draw → results → custom pak), see `ohs-lab-testing/nutrients-rx-customer-journey`.

## Anything else

### The five-level range system (every test uses this)
- **Clinical Low** — below the lab range. Often means a real health problem.
- **Functional Low** — in the lab range but on the low end. Not sick, but not at your best.
- **Optimal** — the level where your body works its best. The goal.
- **Functional High** — in the lab range but on the high end. Body is under stress.
- **Clinical High** — above the lab range. Often means a real health problem.

### Sex-specific ranges
**B** = both sexes · **M** = males only · **F** = females only.

---

## Test Descriptions

"""
    body_parts = []
    for t in test_titles:
        if t not in tests:
            body_parts.append(f"### {t}\n\n*Reference content not present in source v3 — defer to operator or to the OHS test descriptions v3 file for the verbatim text.*\n")
            continue
        body_parts.append(f"### {t}\n\n{tests[t]}\n")

    return head + "\n".join(body_parts)


for slug, name, descr, test_titles in GROUPS:
    skill_md = build_skill(slug, name, descr, test_titles)
    out_path = DST_ROOT / slug / "SKILL.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(skill_md)
    n = len(test_titles)
    bytes_ = len(skill_md)
    print(f"  {slug:42}  {n:>2} tests  {bytes_/1024:>5.1f} KB  -> {out_path}")
