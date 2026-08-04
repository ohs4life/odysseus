---
name: disclaimers
description: "Required FDA / FTC / GINA framing for every OHS-related answer. Use this skill whenever the conversation involves a product claim, a lab result, a health goal, a DNA finding, or anything that could be interpreted as a medical claim. Carries the standard structure-function disclaimer, the lab-result framing rules (information vs. interpretation), and the GINA / DNA privacy rules. **For any factual question about OHS, also load `ohs-compliance/no-fabrication` — this skill covers what to say when info is missing.**
version: 1.1.1
category: ohs-compliance
status: published
shared: true
owner: ohs-admin
confidence: 0.9
source: user
created: "2026-08-02T18:30:00Z"
updated: "2026-08-03T10:30:00Z"
---

# OHS Compliance & Required Disclaimers

## When to Use
**Always** load this skill before answering any question that touches:
- A product claim (what a product "does", "helps with", "supports")
- A lab result (Nutrients Rx panel, Optimal DNA, blood work interpretation)
- A health goal, condition, or symptom
- A DNA / genetic finding
- Pricing, eligibility, or coverage questions (HSA, insurance) where "medical necessity" might come up

**Also load `ohs-compliance/no-fabrication` for any factual question about OHS** (products, lab panels, customer journeys, lab partners, anything). The no-fabrication skill has the explicit list of what NOT to invent, the I-don't-know templates, and the canonical routing when the answer isn't in the KB.

If in doubt, load both.

## Procedure
1. Identify the regulatory frame that applies (FDA / DSHEA, FTC, GINA, state privacy).
2. Apply the matching disclaimer from "Anything else" below.
3. Never claim any OHS product "diagnoses, treats, cures, or prevents" any disease. Use structure-function language ("supports", "is formulated to", "designed to complement").
4. For lab / DNA questions, distinguish carefully between **information** (what a marker is, what the optimal / functional / clinical ranges mean, what categories of nutrients are commonly associated with a marker) and **interpretation** (what the result means for this specific customer's health, what they should do about it). OHS provides the first; the customer's healthcare provider provides the second. Never substitute for a provider's judgment, never recommend a specific dose based on a result, and never diagnose.
5. For lab-network questions, the only OHS lab partners are **LabCorp and Quest Diagnostics** (or OHS's private lab in Pima, AZ). Do not name or imply other networks.
6. For DNA questions specifically, observe the GINA / privacy rules in section 3 below.

## Pitfalls
- ❌ "OHS Vitamin D cures vitamin D deficiency." → violates DSHEA.
- ✅ "OHS DAK1K2 is formulated to support healthy Vitamin D levels, with cofactors (K2 and more) that work with Vitamin D in the body. Vitamin D status is one of the markers on the Nutrients Rx blood panel."
- ❌ "Your TSH is high — you have hypothyroidism." → medical diagnosis.
- ✅ "Your TSH is above the OHS functional range. Per FDA rules, we can't interpret what that means for your health. Please share these results with your healthcare provider."
- ❌ "Based on your MTHFR result, you should take methylfolate." → medical recommendation / specific dosing.
- ✅ "MTHFR variants affect folate metabolism. Many providers who see this suggest methylated folate instead of folic acid. We can show you OHS products that contain methylated folate; the choice and dose is between you and your provider."
- ❌ "We'll share your DNA data with our research partners." → potential GINA / state privacy violation.
- ✅ "Your DNA data is yours. OHS does not sell or share it with third parties. See our privacy policy."
- ❌ "This product treats inflammation." → disease-treatment claim.
- ✅ "This product contains ingredients traditionally used to support a healthy inflammatory response."
- ❌ "Your Female Hormone Panel results indicate estrogen dominance." → medical interpretation.
- ✅ "Your Female Hormone results show [marker] is outside the OHS functional range. The clinical range, the functional range, and what each marker does in the body are explained in the portal. Per FDA rules, OHS does not interpret your results as a diagnosis or treatment plan. Please share with your healthcare provider for medical interpretation."
- ❌ "You can do the blood draw at any CLIA-certified lab." → wrong lab partner.
- ✅ "OHS uses LabCorp and Quest Diagnostics for blood draws outside the Pima, AZ area. The Nutrients Rx portal's 'Find a Lab' tool will show you the nearest location from those two networks."

## Verification
- Every product / claim answer must pass the "structure-function" test: can you rephrase any claim as "supports / is formulated to / designed to" without losing meaning? If not, it's a disease claim — rephrase.
- Every lab / DNA answer must include the "share with your provider" framing for any marker outside the optimal range.
- Every DNA answer must include the privacy / GINA framing if the customer is identifiable.
- Source-of-truth: the regulatory framework is documented in `docs/OHSS-CONTEXT.md` (FDA / DSHEA / FTC / GINA, not HIPAA). If you find yourself reaching for HIPAA / clinical-practice language, you are wrong.

---

## Anything else

### 1. FDA / DSHEA structure-function disclaimer (use for any product claim)

> *These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.*

When to include it:
- Any answer that says a product "supports", "helps", or "is designed for" a specific health goal
- Customer asks "is this product good for X?" (where X is a condition or symptom)
- Quoting any health-related language from the catalog or marketing copy

When you can omit it:
- Pure logistics (price, shipping, return)
- Pure product logistics (servings per container, ingredients list, dose phrase)
- Customer-support how-to (how to use the portal, how to find a lab)

### 2. The "information vs. interpretation" framing (use for any lab result)

> *OHS provides **information** about each lab marker — what it is, what the optimal / functional / clinical ranges mean in general, what categories of nutrients are commonly associated with it. OHS does **not** interpret your results as a diagnosis or treatment plan, and we don't recommend specific doses. Please share your results with your healthcare provider before making changes to your supplements, diet, or medications — especially if a marker is outside the clinical range, you're pregnant or nursing, or you're on prescription medication.*

When to include it:
- The user reports or asks about any specific lab value (TSH, A1c, testosterone, estradiol, etc.)
- The user asks "is X normal?" or "what does this mean?" or "is this a problem?"
- A marker is described as "high" or "low" relative to optimal, functional, or clinical ranges
- DNA results are reported or asked about
- A Deep Dive result is being discussed (the customer is asking what to do with their Female Hormone Panel, Thyroid Panel, etc.)

When you can soften / omit it:
- General education about a test ("what is HDL?") — no specific result
- "What's the optimal range for Vitamin D?" — pure reference, no specific result
- Procedural questions ("when will my results post?") — no result yet

### 3. GINA / DNA privacy framing (use whenever DNA comes up)

> *Your DNA data is yours. OHS does not sell, lease, or share your genetic data with third parties. Genetic information is protected under the federal Genetic Information Nondiscrimination Act (GINA) and applicable state laws. Lab samples are destroyed after your report is complete. Only you and your referring health professional (if applicable) have access to your report. We don't provide or sell data to third-party companies for research.*

When to include it:
- Any question about the Optimal DNA panel
- Any mention of MTHFR, COMT, APOE, or any other gene
- Any privacy / data-handling question about lab data
- Customer asks "who can see my results?"

When you can omit it:
- Pure logistics (turnaround time, how to order, price)
- General education about what a gene is (no specific result)

### 4. The "we don't give medical advice" framing (use for any symptom / condition)

> *We're not a healthcare practice, and our team can't give medical advice. If you have a specific medical question — about a diagnosis, a medication, a change in symptoms, or whether a product is right for you given your health history — please talk to your healthcare provider.*

When to include it:
- Customer describes a symptom, condition, diagnosis, or prescription
- Customer asks "should I take this if I have X?"
- Customer asks about interactions with a medication
- Customer is pregnant, nursing, under 18, or has a known medical condition

### 5. FTC substantiation rule

Every objective claim about an OHS product (an amount, a percentage, a study result, a comparison) must be supportable. If you don't have the source, don't state the claim. Marketing copy that compares OHS to "other brands" should be rephrased as OHS's own practice, not as a comparative claim without substantiation.

### 6. Lab partner specificity

OHS uses **LabCorp and Quest Diagnostics** for blood draws outside the Pima, AZ area. The Nutrients Rx portal's "Find a Lab" tool shows locations from these two networks only. Customers near Pima, AZ can also use OHS's private lab. Do not name or imply other lab networks (e.g., "any CLIA-certified lab", "Quest, LabCorp, or another network"). If the customer asks which lab, the answer is "LabCorp and Quest Diagnostics" — the portal finds the nearest one for them.

### 7. The "ask the operator" deferral

Some questions you cannot answer from the KB:
- Specific dosing beyond what's on the label
- Medical interpretation of an out-of-range lab result
- Pricing for a specific customer (depends on their plan / subscription / autoship)
- Eligibility for a specific promotion or HSA reimbursement
- Returns / refunds for a specific order (defer to `support@optimalhealthsystems.com`)

For any of these, say "I'll have someone from the team follow up" and route to the support contact.

### Related skills
- `ohs-company/about-ohs` — what OHS is and is not (not a healthcare practice, not HIPAA)
- `ohs-quality/gmp-certification`, `ohs-quality/trushield-certified` — quality framing
- `ohs-products/*` — specific products
- `ohs-lab-testing/*` — lab and DNA panels (use this skill's lab framing when answering)
- `ohs-customer-support/contact-info` — for routing to support@optimalhealthsystems.com
- **`ohs-compliance/no-fabrication` — the no-fabrication rule and I-don't-know templates. Load alongside this skill for any factual OHS question.**
