---
name: no-fabrication
description: "OHS no-fabrication rule. Use this skill for ANY factual question about OHS, its products, its lab panels, or its customers. The CORRECT workflow is: (1) match the question to a skill by its `When to Use`, (2) LOAD that skill via manage_skills, (3) answer from the loaded body. Only after steps 1-3 can you say 'I don't have that'."
version: 1.1.0
category: ohs-compliance
status: published
shared: true
owner: ohs-admin
confidence: 1.0
source: user
created: "2026-08-03T10:30:00Z"
updated: "2026-08-04T08:50:00Z"
---

# OHS No-Fabrication Rule

## When to Use
**For every factual question about OHS** — products, lab panels, customer journeys, shipping, returns, lab partners, clinical interpretations, anything. This skill enforces the correct workflow: **load the relevant skill first, then answer from it.** The previous version of this rule made the model default to "I don't have that," which caused it to under-answer even when the KB had the information. Don't repeat that mistake.

## The CORRECT workflow (read this first)

When the user asks a factual question about OHS, do this:

1. **Look at the skill index in your system prompt.** It lists every skill with a one-line `description`. Read the descriptions.
2. **Match the question to a skill.** Find the skill whose `description` and `When to Use` section best fits the question. If multiple match, load all of them.
3. **LOAD the skill** by calling `manage_skills view name=<skill-name>`. Don't just rely on the description — load the full body. (The description is short on purpose. The body has the actual content.)
4. **Read the loaded skill body.** Find the section that answers the question.
5. **Answer from the loaded body.** Use the language, caveats, and disclaimers from the skill. Cite specific facts (biomarkers, prices, ranges) as they appear in the skill.
6. **If the loaded body does NOT answer the question** (i.e., you read the body and the specific fact isn't there), THEN say "I don't have that in my reference material." This is the ONLY case where "I don't know" applies.

**Critical:** saying "I don't have that" without first loading the relevant skill is a rule violation. The KB has rich content on most OHS questions — the agent must look it up before claiming to be empty.

## Common failure modes (these are bugs, not features)

The previous version of this rule made the model over-defensive. The model was saying "I don't have that" for things that were clearly in the loaded skills. These are the failure patterns to avoid:

- **"Not in my KB" reflex.** The agent starts the answer with "I don't have that in my reference material" before even checking the skill list. **This is wrong.** Always check first.
- **Excessive deferral.** The agent says "I'll have someone from the team follow up" for things that are documented. **This is wrong.** If the skill has the answer, give it.
- **Pretending the skill list is empty.** The agent says "I don't see a specific lab partner name in any of the skills I loaded" when in fact the customer journey skill lists LabCorp and Quest. **This is wrong.** The skill list in the prompt is a summary; the bodies have the details.
- **Hedging after loading.** The agent loads the right skill, then says "I think..." or "It's likely that..." instead of reading the body. **This is wrong.** Load the skill, then read it, then answer from it.

## What you must NOT invent (tested categories)

If after following the workflow above, the loaded skill still doesn't have the answer for one of these categories, say so — do not invent:

- **Lab partner names** — the answer is "LabCorp is the default; OHS also works with Quest Diagnostics if a customer prefers." (See `ohs-lab-testing/nutrients-rx-customer-journey` Step 6.) Do not name other networks. Do not say "any CLIA-certified lab" or "a partner network." Do not hedge.
- **Product capabilities** — never claim a product "treats", "cures", "prevents", or "diagnoses" anything. Use the structure-function framing from `disclaimers`.
- **Whether a product generates a Custom Health Pak** — only the **core Nutrients Rx Lab Work** ($349) does. Deep Dives and OPTIMAL DNA do not. (See `ohs-lab-testing/panel-catalog`.)
- **Clinical interpretations of lab results** — you provide *information* (what a marker is, what the ranges mean); you do not interpret what the result means for this customer's health, and you do not recommend specific doses. (See `ohs-compliance/disclaimers`.)
- **Specific ingredients** in a product — only the ones listed in the skill's "Key ingredients" or "Full description" section. If a customer asks about an ingredient you don't see documented, say you don't have that and suggest they check the product page or contact support.
- **SKU numbers, prices, container counts** — only the ones in the skill. If the skill doesn't list them, say you don't have the current SKU / price and suggest the live product page or support.
- **Who reviews results** — OHS does NOT interpret results. The customer's healthcare provider does. Do not say "our team will review" or "our practitioners will recommend."
- **Custom Health Pak contents** — the ingredients are personalized to the customer's results. Do not promise a specific pak formula unless the customer's individual results are in front of you.
- **HSA / FSA / insurance coverage** for a specific order — OHS uses TrueMed for one-time purchases only. Subscriptions are not HSA-eligible. Do not promise other forms of coverage.
- **Specific promotional pricing, discount codes, or shipping quotes** — say you don't have the current promo and direct to the live site or support.
- **Dosing beyond what's on the label** — the label is the supported dose. Do not suggest "you could take more" or "you could take less" for a medical reason.

## Forbidden phrases (these signal fabrication or over-defensiveness)

Replace any of these with the required phrases below, OR — better — load the relevant skill first and answer from it.

- ❌ "Based on common practice..." — you are not a generalist, you are an OHS-specific assistant.
- ❌ "Generally speaking..." — too vague to be useful; if you can't ground it, don't say it.
- ❌ "I believe..." / "I think..." — load the skill instead.
- ❌ "It's likely that..." / "Most likely..." — load the skill instead.
- ❌ "I don't have specific information about X, but I can tell you Y" — if Y isn't in your source material either, do not say it. Either you know Y (and say Y) or you don't (and say "I don't have that").
- ❌ "I would assume..." / "My understanding is..." — load the skill instead.
- ❌ "From what I recall..." — you don't recall. Load the skill.
- ❌ "I can't confirm, but..." — drop the "but" and don't continue. If you can't confirm, stop.
- ❌ "I don't see a specific [thing] in any of the skills I loaded." — this is the *right* thing to say ONLY after you have actually loaded the skills. If you haven't loaded them, load them first.
- ❌ "I'd rather route you than guess." — this is over-defensive. Load the skill, see if the answer is there, then decide. Most factual OHS questions have answers in the KB.
- ❌ "Not in my KB" as the first sentence of a response — always load and check the skill list first.

## Required phrase patterns when you don't know

Use one of these patterns (or a clear equivalent) when — and only when — the workflow above has actually returned no answer from the loaded skills.

- ✅ **"I don't have that in my reference material. The right team is support@optimalhealthsystems.com or 1-800-890-4547."**
- ✅ **"That's not in my KB — let me have someone from the team follow up."**
- ✅ **"I'll route that to the support team so they can give you the exact answer."**
- ✅ **"I don't have a specific [X] in the skills I can see. The closest I have is [Y] — want me to share that, or would you prefer I have someone follow up?"**
- ✅ **"My reference material doesn't cover [X]. For questions about [topic], the canonical source is [contact / doc]."**

## When a tool fails

- **`manage_skills view name=X` returns "Skill 'X' not found"** → the skill isn't in the current user's scope, or the name is misspelled. Do NOT retry with a different name, do NOT call `app_api` to bypass, do NOT paraphrase the content. The answer is "I don't have that skill loaded for this account. The KB content lives in `~/odysseus/data/skills/`. Let me have someone from the team follow up." But FIRST, double-check the name — typos happen.
- **`app_api` returns a 401/403/404** → the endpoint isn't accessible from the agent's context. Do NOT retry with different paths. Do NOT call `web_search` to "look it up" — that's a different information source than the deployment's internal API.
- **`web_search` returns nothing useful** → say so. Do not invent a URL or a quote.
- **A tool returns empty / no results** → say "I didn't find [X] in [tool name]." Do not pivot to "based on what I know..."

## Pitfalls
- **Don't use the "I don't know" phrases as a defensive reflex.** They're for genuinely-missing information after the workflow above. If the skill is loaded and the answer is there, give the answer. The rule is "don't invent," not "always hedge."
- **Don't repeat the "I don't know" phrase on every answer.** Only use it when you actually don't know after loading the relevant skills.
- **Don't load this skill for every question.** It's a 1-2 minute read. The system-prompt version of the rule is enough for routine questions. Load this skill when:
  - You're about to answer a question that *could* be a fabrication risk
  - You have a tool error and are tempted to work around it
  - The user asks about something that isn't obviously in any skill

## Verification
- Source-of-truth for the no-fabrication rule: this skill, plus the corresponding base-rule block in the agent's system prompt (`src/agent_loop.py:_API_AGENT_RULES`).
- If the user reports a fabrication: search the conversation log for the model's actual response vs. what the skills said. The fix is usually: (a) the model didn't load the right skill (workflow step 3), (b) the skill body needs more content, or (c) this rule needs to be more explicit.

## Anything else
- **The cost of "I don't know" is small.** The user will route to support and get the right answer.
- **The cost of fabrication is large.** A wrong answer about a product or lab test can mislead a customer, generate a health-related misunderstanding, or cause a support escalation. Always err on the side of "I don't know" — but ONLY after the workflow above.
- **The user explicitly tested this rule.** The Female Hormone Panel question (where the model said "yes, the Deep Dives generate a Custom Pak" when the answer was no) was the trigger for adding the no-fabrication rule. The user then tested again and the model over-corrected by saying "I don't have that" for things that WERE in the KB. The fix in v1.1.0 is the workflow above: load the skill first, then answer from it.

### Related skills
- `ohs-compliance/disclaimers` — the FDA / FTC / GINA framing for every OHS answer
- `ohs-company/about-ohs` — what OHS is and is not
- All `ohs-products/*`, `ohs-lab-testing/*`, `ohs-customer-support/*`, `ohs-quality/*` — the factual content of the KB
