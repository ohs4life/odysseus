---
name: trushield-certified
description: "OHS TruShield Certified products are tested by a WADA-experienced laboratory for 400+ banned substances. For athletes, coaches, NCAA / Olympic / pro teams, and any customer subject to anti-doping rules. Use this when a customer or sales rep asks 'is this product safe for drug-tested athletes?'"
version: 1.0.0
category: ohs-quality
status: published
shared: true
owner: ohs-admin
confidence: 0.9
source: user
created: "2026-08-02T18:30:00Z"
---

# OHS TruShield Certified — Anti-Doping / Banned-Substance Tested

## When to Use
When the user asks any variant of:
- "Are your products safe for athletes?"
- "Are your products WADA-compliant / drug-tested?"
- "I'm a college athlete / pro / Olympic hopeful — can I take this?"
- "Will this trigger a positive on a drug test?"
- "What is TruShield?"
- "Which products are TruShield?"
- Coach, trainer, or team-purchaser asking about a roster of athletes.

## Procedure
1. Identify the product family: **TruShield Certified** products.
2. State who tests them: a **WADA-experienced laboratory** (i.e., a lab with World Anti-Doping Agency protocol experience).
3. State what they test for: **400+ banned substances**, using "advanced anti-doping methods."
4. State who it's for: **athletes, coaches, and teams at every level** — high school, NCAA, professional, Olympic.
5. State the two things the certification supports: **clean performance** and **protection of eligibility**.
6. If the user names a specific product, check the Shopify tag `TruShield` to confirm that product is in the program. If unsure, defer to the operator or `ohs-products/<handle>` skill for the specific SKU.

## Pitfalls
- **Not every OHS product is TruShield.** Only products tagged `TruShield` in the Shopify catalog carry the certification. Do not imply blanket coverage.
- **"WADA-experienced" ≠ "WADA-certified" or "WADA-approved."** TruShield uses a WADA-experienced lab and advanced anti-doping methods. Do not use language that implies WADA itself has endorsed or certified the products.
- **Do not promise an outcome** ("you will pass any drug test"). State the testing scope and let the customer / their athletic organization make the eligibility decision.
- **Do not use medical / disease language** — see `ohs-compliance/disclaimers`. TruShield is a quality / contamination claim, not a health claim.
- **The TruShield tag applies to a subset of products.** A "yes, this is TruShield" claim requires a tag check; a "no" or "I don't know" claim is safer than a wrong yes.

## Verification
- The verbatim one-paragraph blurb is in `knowledgebase/about-ohs/trushield-certified.md`.
- Confirm membership by checking the `Tags` column in `knowledgebase/products/products_export_08-02-2026.csv` for the value `TruShield`.
- For underlying quality / facility standards, see `ohs-quality/gmp-certification`.

## Anything else

### The verbatim claim (OHS-authored)
> "When your career or eligibility is on the line, your supplements need to be bulletproof. Our TruShield Certified products are tested by a WADA-experienced laboratory using advanced anti-doping methods and screened against 400+ banned substances. Built for athletes, coaches, and teams at every level—from high school and NCAA programs to professional and Olympic-level competition—this certification supports clean performance and protects eligibility."

### Anti-doping context
Anti-doping programs (NCAA, USADA, WADA, professional leagues) hold athletes strictly liable for what's in their body. A contaminated supplement can trigger a positive test and end a career. TruShield exists to reduce that risk for OHS customers who are subject to drug testing.

### Related skills
- `ohs-quality/gmp-certification` — the FDA cGMP baseline
- `ohs-products/*` — check the specific product's `Tags` for `TruShield`
- `ohs-compliance/disclaimers` — required framing language
