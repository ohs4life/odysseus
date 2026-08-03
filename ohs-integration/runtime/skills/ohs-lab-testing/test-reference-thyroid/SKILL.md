---
name: test-reference-thyroid
description: "Standard TSH plus the deep-dive thyroid markers: T3 Free, T4 Free, Reverse T3, Thyroglobulin Antibody, and TPO Antibody."
version: 1.0.0
category: ohs-lab-testing
status: published
shared: true
owner: ohs-admin
confidence: 0.9
source: user
created: "2026-08-02T18:30:00Z"
---

# Thyroid Panel — Test Reference

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

### TSH (Thyroid-Stimulating Hormone)

**What is this test?** TSH is a hormone made by your pituitary gland (a small gland at the base of your brain). It tells your thyroid gland (in your neck) to make thyroid hormones (T4 and T3). Thyroid hormones control your energy, metabolism, body temperature, and many other body functions.

**Why does it matter?** TSH is the best single screening test for thyroid problems. High TSH usually means an underactive thyroid (hypothyroidism). Low TSH usually means an overactive thyroid (hyperthyroidism). Many people have symptoms even within the lab range, so functional medicine uses tighter ranges.

**Reference ranges (mIU/L, both sexes):**

- Clinical Low: 0–0.4  
- Functional Low: 0.41–0.99  
- **Optimal: 1.0–3.5**  
- Functional High: 3.51–4.5  
- Clinical High: 4.51 and above

**Clinical Low (below 0.41 mIU/L):** Very low TSH means hyperthyroidism (overactive thyroid). It can cause anxiety, fast heart rate, weight loss, feeling hot, shaking, insomnia, diarrhea, and bulging eyes (in Graves disease, an autoimmune thyroid disorder). Causes: Graves disease, toxic multinodular goiter (an enlarged thyroid with hot nodules), toxic adenoma (a single hot nodule), thyroiditis (inflammation of the thyroid, early phase), too much thyroid medicine, too much iodine, or rarely pituitary tumors. To address: work with a provider. Treatment may include antithyroid drugs (methimazole, PTU), radioactive iodine, or surgery. Cut back on iodine and stimulants. Manage stress. Add calming nutrients (magnesium, selenium, L-theanine).

**Functional Low (0.41–0.99 mIU/L):** This is in the lab range but on the low side. It can be subclinical hyperthyroidism (low TSH with normal thyroid hormones) or early hyperthyroidism. Symptoms: anxiety, insomnia, heart palpitations, and weight loss. Causes: early Graves disease, too much thyroid medicine, too much iodine or selenium, and chronic stress. To optimize: work with a provider. Cut back on iodine and stimulants. Manage stress. Support your HPA axis (the system that manages stress hormones). A provider can check free T3, free T4, thyroid antibodies, and reverse T3.

**Optimal (1.0–3.5 mIU/L):** This is the goal. It means your thyroid is working well. To stay here: make sure you get enough iodine (seaweed, seafood, iodized salt), selenium (Brazil nuts, fish), zinc, iron, vitamin D, and tyrosine (an amino acid your body uses to make thyroid hormones). Manage stress. Sleep 7–9 hours. Avoid endocrine disruptors. A functional medicine provider can also check free T3, free T4, reverse T3, and thyroid antibodies for a fuller picture.

**Functional High (3.51–4.5 mIU/L):** This is in the lab range but on the high side. It can mean subclinical hypothyroidism (high TSH with normal thyroid hormones). Symptoms: fatigue, weight gain, brain fog, feeling cold, constipation, and mild sadness. Common causes: Hashimoto's thyroiditis (an autoimmune disease that attacks the thyroid — the most common cause), iodine deficiency, low selenium, low iron, chronic stress, poor T4-to-T3 conversion, and certain medicines. To optimize: address the cause. Get enough iodine, selenium, zinc, iron, and vitamin D. Manage stress. Sleep well. Eat an anti-inflammatory diet. A provider can check free T3, free T4, thyroid antibodies, and reverse T3.

**Clinical High (4.51 mIU/L and above):** High TSH means hypothyroidism (underactive thyroid). It can be subclinical (high TSH, normal T4) or overt (high TSH, low T4). Symptoms: fatigue, weight gain, feeling cold, constipation, brain fog, sadness, hair loss, dry skin, and irregular periods. Causes: Hashimoto's thyroiditis (most common in iodine-sufficient areas), iodine deficiency, thyroid surgery, radioactive iodine, certain medicines (lithium, amiodarone), or rarely pituitary problems. To address: work with a provider. Treatment may include thyroid hormone replacement (levothyroxine, liothyronine, or natural desiccated thyroid). Lifestyle: get enough iodine, selenium, zinc, iron, and vitamin D. Manage stress. Sleep well. Eat an anti-inflammatory diet. A functional medicine provider can check the full thyroid panel, antibodies, and gut health.

---
