#!/usr/bin/env python3
"""Build product SKILL.md files from products_export_08-02-2026.csv.

One SKILL.md per product line (handle) for active retail products.
"""
import csv
import re
import html
from pathlib import Path
from collections import defaultdict

SRC = Path("/Users/ai/ohs-ai-build/knowledgebase/products/products_export_08-02-2026.csv")
DST_ROOT = Path("/Users/ai/odysseus/data/skills/ohs-products")
CREATED = "2026-08-02T18:30:00Z"

# Product type -> friendly name
TYPE_LABEL = {
    "Shelf Pak": "Shelf Pak (pre-built daily nutrient pak)",
    "Custom Pak": "Custom Health Pak (built from your lab results — see Nutrients Rx)",
    "Whole Food Powder": "Whole-Food Powder",
    "Bundle": "Bundle",
    "Nutrients Rx": "Nutrients Rx Program",
}

# Titles/handles to EXCLUDE — these are clearly not retail supplements
# (vendor packages, gift cards, branded merch, seminars, services, etc.)
EXCLUDE_TITLE_PATTERNS = [
    "vendor package", "vendor registration", "booth",
    "seminar recording", "seminar ticket", "seminar 20", "formulas and marketing",
    "gift card",
    "shaker", "sticker", "hat ", "hat", "tarp", "cable", "stainless",
    "magazine", "flyer", "pdf download", "card",
    "dexa scan", "blood pressure cuff", "body fat caliper", "massage gun",
    "test kit", "lab work", "patient labs",
    "declaration", "great american food fraud", "healthy habits tracker",
    "literature", "supplement funnel",
    "hydrogen water bottle",
    "brimhall",
    "membership", "coaching",
    "starter package", "success kit",
    "access ", "guide", "workout", "21-day", "blitz",
    "tickets",
    "free offer", "discounted",
    "free pdf", "free-",
    "baked chips",
    "dr. harris", "dr harris", "vials",
    "early bird",
    "salt",
    "test ",
    "upsell", "gift",
]
# Handles that are clearly non-retail
EXCLUDE_HANDLES = {
    "g-a-f-f-declaration", "declaration-of-optimal-health-for-public",
    "ohs-gift-card", "ohs-hat", "ohs-sticker", "ohs-shaker-bottle",
    "ohs-stainless-shaker", "ohs-capsule-pouch",
    "every-patient-every-day-flyer", "tarp-stickers", "iron-man-magazine",
    "magnesium-card", "supplement-funnel", "baked-chips-gluten-free",
    "hydrogen-water-bottle",
    "free-offer-upsell-mvp-stack-gift-card",
    "great-american-food-fraud", "healthy-habits-tracker", "literature",
    "health-portal-access",
    "meal-ticket-ss25", "famm2025-recordings",
    "virtual-seminar-2026-tickets",
    "virtual-formulas-and-marketing-mastery-seminar-early-bird-2027-copy",
    "stress-relief-virtual-seminar-recording-access",
    "beginner-s-at-home-workout-guide-21-day-challenge-nutrition-guide-top-5-immune-hacks-guide-glute-circle",
    "brimhall-homecoming-vendor-registration",  # was silver-super-seminar-vendor-package-10x20-copy
    "silver-super-seminar-vendor-package-10x20",
    "gold-super-seminar-vendor-package-10x30",
    "platinum-super-seminar-vendor-package-10x30",
    "bronze-super-seminar-vendor-package-10x10",
    "optimal-clinic-starter-package",
    "hp-success-kit",
    "vendor-booth-electricity",
    "declaration-of-optimal-health-for-public",
    "g-a-f-f-declaration",
    "test",  # the literal handle "test" with a $100 placeholder
}
# Price floor — products under this are unlikely to be main retail supplements
# (cards, stickers, sample pouches, etc.)
MIN_PRICE = 15.0

# Body-text mentions to require for "supplement with no Type" — at least one
# of these keywords should appear in the product's bullets / health goals /
# body / tags. This is what tells us it's a real supplement, not an event
# or service.
SUPPLEMENT_KEYWORDS = [
    "supplement", "vitamin", "mineral", "probiotic", "enzyme", "antioxidant",
    "nutrient", "whole food", "herbal", "botanical", "digest", "immune",
    "energy", "joint", "bone", "heart", "brain", "liver", "kidney", "thyroid",
    "hormone", "protein", "amino", "omega", "fatty acid", "magnesium",
    "zinc", "iron", "b-12", "b12", "vitamin c", "vitamin d", "vitamin k",
    "gluta", "coq10", "ubiquinol", "mitochondri", "microbiome", "flora",
    "reflux", "bloat", "gas, bloat",
    "adrenal", "sleep", "calm", "stress", "mood", "focus", "memory",
    "fitness", "muscle", "strength", "recovery", "endurance", "performance",
    "weight", "metabol", "sugar", "fat", "cholesterol", "cardio",
    "skin", "hair", "nail", "anti-aging", "longevity", "wellness",
    "detox", "cleanse", "toxin", "liver", "kidney", "lymph",
    "inflammation", "joint", "pain",
    "essential", "optimal", "opti-",
    "capsule", "tablet", "powder", "liquid", "drops", "gummy", "spray",
    "whey", "plant-based", "grass-fed",
    "testosterone", "estrogen", "progesterone", "cortisol", "dhea",
    "methylat", "mthfr", "folate", "folic",
    "natural", "organic", "non-gmo",
    "blood", "cell", "cellular", "tissue", "organ", "system",
    "health", "support", "promote", "boost", "enhance", "improve",
    "pH", "alkalin", "acid", "acidity",
    "fiber", "prebiotic",
    "peptide", "amino acid", "creatine", "bcaa", "glutamine", "carnitine",
    "electrolyte", "mineral", "trace",
    "antiviral", "antibacterial", "antifungal", "parasit", "candid",
    "oxygen", "nitric",
    "pH", "leaky gut", "ibs", "gerd", "ibs", "ibd", "celiac", "gluten",
]

# These are the handles we want to write skills for (already created dirs)
ALLOWED_HANDLES = None  # will be filtered by directory existence


def strip_html(s: str) -> str:
    if not s:
        return ""
    # crude: replace br/p/li with newlines, strip tags
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</p\s*>", "\n\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<li[^>]*>", "• ", s, flags=re.IGNORECASE)
    s = re.sub(r"</li\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    # collapse whitespace
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def first_active_row(rows_by_handle: dict, handle: str):
    """Return the first active retail row for a handle (prefer rows with rich content)."""
    candidates = [r for r in rows_by_handle.get(handle, []) if r.get('Status') == 'active']
    if not candidates:
        return None
    # Prefer non-Wholesale rows, then rows with a body
    non_ws = [r for r in candidates if not r.get('Handle', '').startswith('ws-')]
    pool = non_ws or candidates
    pool.sort(key=lambda r: (
        not (r.get('Body (HTML)') or '').strip(),  # rows with body first
        not (r.get('Bullets (product.metafields.ohs.bullets)') or '').strip(),
    ))
    return pool[0]


def build_skill(handle: str, row: dict) -> str:
    title = row.get('Title', '').strip()
    ptype = row.get('Type', '').strip()
    ptype_label = TYPE_LABEL.get(ptype, ptype or "Product")
    price = row.get('Variant Price', '').strip()
    sku = row.get('Variant SKU', '').strip()
    tags = [t.strip() for t in (row.get('Tags', '') or '').split(',') if t.strip()]
    bullets = (row.get('Bullets (product.metafields.ohs.bullets)', '') or '').strip()
    health_goals = (row.get('Health Goals (product.metafields.ohs.health_goals)', '') or '').strip()
    ingredients = (row.get('Ingredients (product.metafields.ohs.ingredients)', '') or '').strip()
    faqs = (row.get('FAQs (product.metafields.ohs.faqs)', '') or '').strip()
    dose_phrase = (row.get('Dose Phrase (product.metafields.ohs.dose_phrase)', '') or '').strip()
    container_type = (row.get('Container Type (product.metafields.ohs.container_type)', '') or '').strip()
    container_qty = (row.get('Container Qty (product.metafields.ohs.container_qty)', '') or '').strip()
    container_servings = (row.get('Container Servings (product.metafields.ohs.container_servings)', '') or '').strip()
    fact_card = (row.get('Fact Card Product (product.metafields.ohs.fact_card_product)', '') or '').strip()
    body_html = (row.get('Body (HTML)', '') or '').strip()
    body_text = strip_html(body_html)

    # Description for the frontmatter: short, specific
    short_descr = f"OHS {title} — {ptype_label}"
    if bullets:
        # use the first bullet as a one-liner
        first_bullet = re.split(r"[\n\r]", bullets)[0].strip().rstrip('.')
        if first_bullet and len(first_bullet) < 130:
            short_descr = f"OHS {title} — {first_bullet}"
    short_descr = short_descr.replace('"', "'")
    # YAML escape: wrap in quotes, escape inner quotes
    descr_yaml = short_descr.replace('"', '\\"')

    # Build the body
    parts = []
    parts.append(f"""---
name: {handle}
description: "{descr_yaml}"
version: 1.0.0
category: ohs-products
status: published
shared: true
owner: ohs-admin
confidence: 0.85
source: user
created: "{CREATED}"
---

# {title}

## When to Use
When a customer, employee, or practitioner asks about **{title}** specifically — what it is, who it's for, what's in it, how to take it, or whether it ships in a particular program (e.g., TruShield, Custom Pak). For general OHS context, see `ohs-company/about-ohs`. For product-line comparisons, see the related-skills section at the bottom of this skill.

## Procedure
1. Confirm the customer is asking about the **right product** — there are many similarly named products. If unsure, ask for the SKU or the container description.
2. State the product's purpose using the bullets and the description below.
3. Surface the **ingredients / what's in it** if relevant. Do not invent ingredients.
4. Surface the **container / dose** information (e.g., "30 packets, 1 per day, AM and PM").
5. If the customer asks about TruShield / banned-substance testing, confirm the `TruShield` tag is present (it is in the tags list below). For drug-tested athletes, see `ohs-quality/trushield-certified`.
6. For health-condition questions, apply the framing from `ohs-compliance/disclaimers` (no disease claims, recommend the customer's provider).

## Pitfalls
- **Do not claim this product diagnoses, treats, cures, or prevents any disease.** Use the FDA / DSHEA structure-function language from `ohs-compliance/disclaimers`.
- **Do not recommend a dose different from the label** (the "Dose Phrase" below). The dose on the label is the supported dose.
- **Do not invent ingredients** beyond what's listed below. If a question requires an ingredient not in the list, defer to the operator.
- **Do not generalize from this product to other OHS products.** Each product has its own formulation. If the customer is asking about a different SKU, route to that product's skill.
- **Do not promise the product will produce a specific outcome** ("this will lower your cholesterol"). The product is a whole-food supplement, not a drug.
- **Custom Paks are built after the order is placed.** Don't promise same-day fulfillment for any Custom Pak SKU.
- **Subscriptions are not HSA-eligible.** If the customer wants to use HSA / FSA, direct them to `ohs-customer-support/hsa-payments` (TrueMed, one-time purchases only).

## Verification
- The OHS store URL for this product is `optimalhealthsystems.com/products/{handle}`.
- The Shopify `Variant SKU` below is the unique identifier. For questions about a specific order, the SKU + order number is the right lookup.
- Tags below are sourced from the OHS Shopify catalog and may include: `Bulk Discountable`, `Direct Script`, `Tier 1 - Retail`, `Tier 1 - Wholesale`, `TruShield`, `Visibility - All`, `HP Line Order`, `Wholesale`, `WS - Bulk Discountable`, `Exclude Recommended`, `Exclude Review`, `exclude_rebuy`, `Visibility - HP Only`, `Visibility - Admin Only`, etc.
- For the underlying whole-food philosophy, see `ohs-company/about-ohs` (the "Made Different" / Opti-Blend™ story).
- For facility quality (cGMP, FDA), see `ohs-quality/gmp-certification`.
- For the Nutrients Rx program (which produces Custom Health Paks from lab results), see `ohs-lab-testing/nutrients-rx-customer-journey`.

## Anything else
""")

    # Quick reference table
    parts.append("### Quick reference\n")
    parts.append(f"| | |\n|---|---|\n")
    parts.append(f"| **Product type** | {ptype_label} |\n")
    if price:
        parts.append(f"| **Price** | ${price} |\n")
    if sku:
        parts.append(f"| **Variant SKU** | `{sku}` |\n")
    if container_type or container_qty or container_servings:
        container = []
        if container_type: container.append(container_type)
        if container_qty: container.append(f"qty {container_qty}")
        if container_servings: container.append(f"{container_servings} servings")
        parts.append(f"| **Container** | {' · '.join(container)} |\n")
    if dose_phrase:
        parts.append(f"| **Dose** | {dose_phrase} |\n")
    if fact_card:
        parts.append(f"| **Fact card** | {fact_card} |\n")
    parts.append("\n")

    # Bullets / purpose
    if bullets:
        parts.append("### What it's for\n")
        for line in bullets.splitlines():
            line = line.strip()
            if line:
                parts.append(f"- {line}\n")
        parts.append("\n")

    # Health goals
    if health_goals:
        parts.append("### Health goals\n")
        parts.append(health_goals + "\n\n")

    # Body description (if any)
    if body_text:
        parts.append("### Full description\n")
        parts.append(body_text + "\n\n")

    # Ingredients
    if ingredients:
        parts.append("### Key ingredients (Shopify metafield)\n")
        # The metafield is semicolon-separated slugs like "pygeum-herb; eurycoma-longifolia-root"
        # Convert to readable form
        ing_list = [i.strip().replace('-', ' ').strip() for i in ingredients.split(';') if i.strip()]
        if ing_list:
            for ing in ing_list:
                parts.append(f"- {ing.title() if ing.islower() else ing}\n")
            parts.append("\n")

    # FAQs
    if faqs:
        parts.append("### FAQs (from the product page)\n")
        # FAQs are usually "Q: ... A: ..." or similar — try to detect
        # The metafield format in the export is varied; just emit as a block
        parts.append(strip_html(faqs) + "\n\n")

    # Tags
    if tags:
        parts.append("### Tags (Shopify)\n")
        parts.append(", ".join(f"`{t}`" for t in tags) + "\n\n")

    # TruShield callout
    if any(t.lower() == 'trushield' for t in tags):
        parts.append("> **TruShield Certified** — this product is tested by a WADA-experienced laboratory for 400+ banned substances. See `ohs-quality/trushield-certified` for details.\n\n")

    # Custom Pak callout
    if ptype == 'Custom Pak':
        parts.append("> **Custom Health Pak** — this is the output of the Nutrients Rx program. It is **created only after the customer places the order** (after lab results are posted). See `ohs-lab-testing/nutrients-rx-customer-journey` for the full customer journey.\n\n")

    # Nutrients Rx callout
    if ptype == 'Nutrients Rx':
        parts.append("> **Nutrients Rx program** — this is the entry-point SKU for the lab + custom-pak program. See `ohs-lab-testing/nutrients-rx-customer-journey` for the full customer journey.\n\n")

    # Standard FDA disclaimer
    parts.append("> *These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.*\n\n")

    # Related skills
    related = ["`ohs-company/about-ohs`", "`ohs-quality/gmp-certification`", "`ohs-quality/trushield-certified`", "`ohs-compliance/disclaimers`"]
    if ptype == 'Custom Pak' or ptype == 'Nutrients Rx':
        related.append("`ohs-lab-testing/nutrients-rx-customer-journey`")
        related.append("`ohs-lab-testing/panel-catalog`")
    if ptype in ('Shelf Pak', 'Whole Food Powder', 'Bundle'):
        related.append("`ohs-customer-support/shipping-policy`")
        related.append("`ohs-customer-support/return-policy`")
    parts.append(f"### Related skills\n" + ", ".join(related) + "\n")

    return "".join(parts)


# ---------------------------------------------------------------------------
# 1. Read source
# ---------------------------------------------------------------------------
with SRC.open() as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Group by handle
by_handle = defaultdict(list)
for r in rows:
    h = r.get('Handle', '').strip()
    if h:
        by_handle[h].append(r)

# Iterate over all handles, apply smart filter to decide which are retail supplements
def is_retail_supplement(handle: str, rows_for_handle: list) -> tuple[bool, str]:
    """Return (include, reason) for a handle.

    Include if:
      - Handle is NOT in EXCLUDE_HANDLES
      - Title doesn't match any EXCLUDE_TITLE_PATTERNS
      - Has at least one active retail row with price >= MIN_PRICE
      - Product has supplement-related content (bullets / health goals / body / tags)
        OR has one of the well-known supplement Type values
    """
    if handle in EXCLUDE_HANDLES:
        return False, "excluded handle"
    # Find the best row to use
    row = first_active_row(by_handle, handle)
    if not row:
        return False, "no active row"
    title = (row.get('Title', '') or '').lower()
    # Excluded title patterns
    for pat in EXCLUDE_TITLE_PATTERNS:
        if pat in title:
            return False, f"title matches '{pat}'"
    # Price check
    try:
        price = float(row.get('Variant Price', '0') or '0')
    except (TypeError, ValueError):
        price = 0.0
    if price < MIN_PRICE:
        return False, f"price ${price} < ${MIN_PRICE}"
    # Type-based inclusion (known retail types)
    ptype = (row.get('Type') or '').strip()
    if ptype in TYPE_LABEL:
        return True, f"type={ptype}"
    # Content-based inclusion (must have supplement-related keywords in bullets / health goals / body)
    text = ' '.join([
        row.get('Bullets (product.metafields.ohs.bullets)', '') or '',
        row.get('Health Goals (product.metafields.ohs.health_goals)', '') or '',
        row.get('Body (HTML)', '') or '',
        row.get('Tags', '') or '',
        title,
    ]).lower()
    if any(kw in text for kw in SUPPLEMENT_KEYWORDS):
        return True, "content match"
    return False, f"no supplement keywords (type={ptype!r})"


# Iterate over ALL active handles
all_handles = sorted(set(
    r.get('Handle', '').strip()
    for r in rows
    if r.get('Status') == 'active' and r.get('Handle', '').strip()
    and not r.get('Handle', '').strip().startswith(('ws-', 'pl-', 'sample-', 'mf-'))
))

written = 0
skipped = []
for handle in all_handles:
    include, reason = is_retail_supplement(handle, by_handle.get(handle, []))
    if not include:
        skipped.append((handle, reason))
        continue
    row = first_active_row(by_handle, handle)
    skill_md = build_skill(handle, row)
    out = DST_ROOT / handle / "SKILL.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(skill_md)
    written += 1
    title = row.get('Title', '?')
    ptype = row.get('Type', '?')
    print(f"  ✓ {handle:50} type={ptype:18} {title[:40]}")

print(f"\nWrote {written} product skills")
print(f"Skipped {len(skipped)} non-retail handles (sample reasons below):")
# Print a small sample of skipped reasons
from collections import Counter
reason_counts = Counter(s[1] for s in skipped)
for reason, count in reason_counts.most_common(10):
    print(f"  {count:>4}  {reason}")
