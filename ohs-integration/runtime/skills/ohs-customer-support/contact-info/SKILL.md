---
name: contact-info
description: "How to reach Optimal Health Systems — email, phone, hours, mailing address, store / pickup location, and which channel to use for which kind of question. Use this whenever a customer or employee asks 'how do I contact OHS?' or needs to be routed to a specific team."
version: 1.0.0
category: ohs-customer-support
status: published
shared: true
owner: ohs-admin
confidence: 0.95
source: user
created: "2026-08-02T18:30:00Z"
---

# How to Contact Optimal Health Systems

## When to Use
Whenever the user (employee or customer) needs to reach OHS — for support, returns, sales, or in-person. Use this skill to pick the right channel and to give the customer / colleague the right address / hours / phone number.

## Procedure

### The one-screen reference

| Channel | Details |
|---|---|
| **Email** | `support@optimalhealthsystems.com` |
| **Phone** | `1-800-890-4547` (or `800.890.4547`) |
| **Hours** | Mon–Thu 8am–5pm Arizona time, Fri 8am–4:30pm Arizona time |
| **Mailing / returns address** | Optimal Health Systems LLC, 265 E Hwy 70, Pima, Arizona 85543 |
| **Store / in-person pickup** | OHS Headquarters, Pima, AZ (Graham County) — local pickup available for Graham County residents |
| **Website** | `optimalhealthsystems.com` |
| **Nutrients Rx portal** | `nutrientsrx.com` (separate site, 2FA login) |

### What to use for what
- **Returns & refunds:** start with email (`support@optimalhealthsystems.com`) or phone (`1-800-890-4547`). Include name + email + order number.
- **Damaged / wrong / missing items:** contact **immediately** by email or phone — same contacts.
- **HSA / TrueMed questions:** see `ohs-customer-support/hsa-payments`; for an order issue, contact `support@optimalhealthsystems.com`.
- **Product questions (which one is right for me, dosing, ingredients):** use the product-specific skill under `ohs-products/*`; if not sure, route to `support@optimalhealthsystems.com`.
- **Lab / DNA result questions:** see `ohs-lab-testing/*` skills. **Do not interpret results** — refer the customer to share with their provider (per `ohs-compliance/disclaimers`).
- **Privacy / data questions:** see the OHS Privacy Policy (linked from the website). For DNA / GINA questions, use the framing in `ohs-compliance/disclaimers`.
- **Local pickup (Graham County only):** see `ohs-customer-support/shipping-policy` (local pickup section).
- **Subscription / autoship changes:** route to `support@optimalhealthsystems.com` — the agent should not change subscription state directly.

## Pitfalls
- **Do not give a physical address for a customer to walk in for general questions** unless the customer is in Graham County. The Pima, AZ location is a warehouse + pickup point, not a general retail storefront for browsing.
- **Do not promise 24/7 phone support.** Hours are Mon–Thu 8am–5pm, Fri 8am–4:30pm Arizona time. Outside hours, the customer should email.
- **Do not invent email aliases** (e.g., `returns@`, `billing@`) — there's only one support inbox at `support@optimalhealthsystems.com`.
- **Do not invent a customer-service rep's direct line / email.** Route everything through the shared inbox and phone.

## Verification
- `support@optimalhealthsystems.com` and `1-800-890-4547` are the canonical support contacts across all OHS policy documents (shipping, returns, HSA, FAQ).
- The Pima, AZ address appears as the return address in the return policy and as the local-pickup location in the shipping policy — same place, two functions.
- Source-of-truth: distributed across `knowledgebase/policies/*.md`. All OHS-authored documents agree on the same contacts.

## Anything else

### Time-zone note
All OHS-published times are **Arizona time**. Arizona does **not** observe daylight saving time, so during DST the rest of the U.S. is offset by 1 hour less (e.g., when it's 9am PT in summer, it's 9am AZ, not 10am).

### Related skills
- `ohs-customer-support/shipping-policy` — for shipping / tracking / pickup / insurance
- `ohs-customer-support/return-policy` — for returns / refunds / damages
- `ohs-customer-support/hsa-payments` — for HSA / FSA / TrueMed
- `ohs-customer-support/support-faq` — for general site / account / product-dating questions
- `ohs-compliance/disclaimers` — for any product / lab / DNA question framing
