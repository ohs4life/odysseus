# OHS — Company Context

> **Read this first in any new session.** OHS is **not** what the
> placeholder skill content in `~/odysseus/data/skills/ohs-shared/` says it
> is. That content was drafted for a generic clinical-practice deployment
> and was never replaced with real OHS information.

## What OHS actually does

**Optimal Health Systems (OHS)** makes **whole-food nutritional supplements**.

- **Mission**: help people have more energy, feel better, be healthier —
  with the ultimate goal of helping people achieve optimal health and
  *stay* healthy.
- **Products**: whole-food-based nutritional supplement lines (multiple SKUs).
- **Lab testing**: blood, urine, and DNA panels offered to customers.
- **Custom recommendations**: based on lab results, OHS makes customized
  nutrient recommendations tailored to each customer's biology and goals.

## What OHS is NOT

- **Not a healthcare practice.** The 3 placeholder SKILL.md files in
  `~/odysseus/data/skills/ohs-shared/` describe a clinical practice with
  patients, providers, scheduling, EHR, SOAP notes, prescription refills,
  HIPAA breach reporting, etc. **None of that applies to OHS.** Treat the
  placeholder content as wrong; replace it.
- **Not a pharmacy.** No prescription dispensing.
- **Not a medical-device manufacturer.** No diagnostic claims.
- **Not subject to HIPAA.** OHS is not a "covered entity" or "business
  associate" — it doesn't bill insurance or provide clinical care. Customer
  data is regulated by FTC, state privacy laws, and **GINA** for the DNA
  side specifically.

## Regulatory frame (FYI, not legal advice)

| Domain | Regulator | Key concern |
|---|---|---|
| Supplement labeling & claims | **FDA** (DSHEA, 1994) | Can't claim to "diagnose, treat, cure, or prevent" any disease. Structure-function claims allowed with the standard disclaimer. |
| Advertising claims | **FTC** | Must be truthful, substantiated, not deceptive. Health claims need competent and reliable scientific evidence. |
| DNA / genetic data | **GINA** (federal) + state laws (e.g., California GIPS) | Can't discriminate based on genetic data. Disclosure to third parties is restricted in many states. |
| General privacy | State laws (CCPA in CA, etc.) | Customer lab data and DNA results are sensitive personal data. |

The KB **must** include a compliance skill that trains the agent to:

- Never claim a product diagnoses, treats, cures, or prevents any disease
- Use the FDA structure-function disclaimer where appropriate
- Recommend consulting a doctor for medical questions
- Handle DNA / lab questions with appropriate privacy framing
- Not give specific dosing or "treatments" — recommend consulting the
  customer's healthcare provider for any medical interpretation

## Recommended KB structure for OHS

| Category | Why |
|---|---|
| `ohs-company/` | Mission, story, who's on the team, where based |
| `ohs-products/` | Each supplement line — what it's for, key ingredients, who it's for |
| `ohs-lab-testing/` | Blood / urine / DNA panels — what's measured, turnaround, how to order |
| `ohs-recommendations/` | How custom nutrient recs work — methodology, who creates them, disclaimers |
| `ohs-quality/` | Whole-food sourcing philosophy, manufacturing standards, certifications |
| `ohs-customer-support/` | Ordering, shipping, returns, account help, FAQ |
| `ohs-compliance/` | FDA / FTC / GINA framing, standard disclaimers, what the agent must NOT say |

See `docs/KB-BUILD-SESSION.md` for the step-by-step build process.

## Things the user (operator) still needs to provide

The user shared high-level context but the KB will need:

1. **Founder / leadership names** (or "anonymous")
2. **Where based** (city, state)
3. **Year founded**
4. **Team size / roles** (e.g., "4 people: 2 formulators, 1 RD, 1 ops")
5. **Product names + 1-line descriptions** (one per supplement line)
6. **Lab panel names + 1-line descriptions** (one per panel)
7. **Sample turnaround times** for each panel
8. **Customer support basics** — ordering, shipping, returns, FAQ
9. **Existing disclaimers** if they have standard language

The next session should ask for these in a structured way. See
`docs/KB-BUILD-SESSION.md` § "Information to gather from the user".