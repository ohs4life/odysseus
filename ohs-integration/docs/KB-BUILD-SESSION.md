# Building the OHS Knowledge Base — Session Playbook

> **For the next Claude session.** The user wants to build a shared
> knowledge base (KB) on the Odysseus deployment so all employees can
> ask the AI about OHS products, lab testing, custom recommendations,
> quality, customer support, and compliance. This document tells you
> how to do it.

**Status as of session 7:** The KB is built — **181 published, shared
skills** across 6 categories (`ohs-company`, `ohs-quality`,
`ohs-customer-support`, `ohs-lab-testing`, `ohs-products`,
`ohs-compliance`). The source material lives in
`ohs-integration/knowledgebase/`. A runtime snapshot of the built
skills (for disaster recovery) lives in `ohs-integration/runtime/skills/`.
The canonical source for ongoing KB changes is the
`ohs4life/odysseus` fork. See `docs/HANDOFF.md` session 7 for the
full state.

---

## 0. Before you start — read these (5 min total)

1. **`docs/OHSS-CONTEXT.md`** — what OHS actually does (supplement
   company, not clinical practice). Critical for not building the wrong KB.
2. **`docs/HANDOFF.md`** — current live state of the deployment (what
   works, what's broken, what's open). Read the most recent session update.
3. **One of the existing shared skills** —
   `cat ~/odysseus/data/skills/<category>/<skill>/SKILL.md` — to see
   the SKILL.md format and frontmatter. Start with
   `ohs-lab-testing/nutrients-rx-customer-journey/SKILL.md` — it has the
   most "Critical distinction" tables and is a good template for high-quality skills.
4. **The no-fabrication rule** — `ohs-compliance/no-fabrication/SKILL.md`
   AND the corresponding base-rule block in `src/agent_loop.py:_API_AGENT_RULES`.
   Any new skills you write will be used through this rule, so make sure
   you understand the workflow: (1) match the question to a skill, (2) LOAD
   the skill, (3) answer from the loaded body, (4) only say "I don't know"
   if the loaded body doesn't have it.

That's enough context. Don't read the wargame doc, the onboarding doc,
or anything else — they're not relevant to this task.

---

## 1. Goal

Replace the 3 placeholder shared skills in
`~/odysseus/data/skills/ohs-shared/` (which describe a clinical practice)
with a real OHS-focused KB that all 25 employees can use.

The mechanism is already in place: any SKILL.md with
`shared: true, status: published` in frontmatter is visible to all 25
users and surfaced in the agent's prompt in agent mode. See
`docs/HANDOFF.md` § "Shared KB mechanism" if you need a refresher.

---

## 2. Where to put files

**Base path:** `~/odysseus/data/skills/`

**Per-skill layout:**
```
~/odysseus/data/skills/<top-category>/<skill-name>/SKILL.md
```

**Recommended categories** (final list may vary based on what the user
shares — see § 3):

| Top-category | Example skill names |
|---|---|
| `ohs-company/` | `about-ohs`, `team`, `contact-info` |
| `ohs-products/` | one folder per product line (e.g., `ohs-products/energy-core/SKILL.md`) |
| `ohs-lab-testing/` | `blood-panel`, `urine-panel`, `dna-panel`, `how-to-order` |
| `ohs-recommendations/` | `how-recs-work`, `sample-recommendation` |
| `ohs-quality/` | `sourcing-philosophy`, `manufacturing-standards` |
| `ohs-customer-support/` | `ordering`, `shipping`, `returns`, `faq` |
| `ohs-compliance/` | `disclaimers`, `what-we-cant-say`, `privacy-gina` |

---

## 3. Information to gather from the user

Ask the user to paste content for each category. Don't try to write the
KB from your own knowledge — OHS-specific facts need to come from the
user. Suggested order:

1. **Company basics** (mission, founder, location, year, team size, tagline)
2. **Products** (one paragraph per supplement line)
3. **Lab testing** (one paragraph per panel: what's measured, turnaround,
   how to order, cost)
4. **Recommendation methodology** (how lab results become custom recs,
   who creates them, what a typical rec includes)
5. **Customer support basics** (ordering process, shipping, returns,
   top 5-10 FAQs)
6. **Compliance / disclaimers** — only if they have existing language.
   If not, write a standard supplement-industry disclaimer covering
   DSHEA / FTC structure-function rules, "not medical advice", and GINA
   for DNA.

**Pacing:** if the user is pasting in chunks, ack each one and say
"more coming" or "that's the lot" so they know where you are. Don't
rush them into a single giant paste.

**You can scrape URLs** — if they give you URLs to OHS's own pages
(about, products, FAQ), fetch them with `curl` and extract the
relevant text. See "Web scraping" below.

---

## 4. SKILL.md format

```markdown
---
name: kebab-case-slug             # required, used as ID
description: One-line summary     # shown in agent picker — be specific
version: 1.0.0
category: ohs-<top-category>      # e.g., ohs-products, ohs-lab-testing
status: published                 # MUST be published (not draft)
shared: true                      # MUST be true to reach all 25 users
owner: ohs-admin
confidence: 0.8
source: user                      # "user" for human-authored, "learned" for AI-authored
---

# Title (freeform heading)

## When to Use
When the user asks about... (2-3 lines describing the trigger — helps
the agent decide whether to load this skill).

## Procedure
1. First step the agent should follow
2. Second step
3. Third step

## Pitfalls
- Common mistake or edge case the agent must not get wrong
- e.g., "Do NOT recommend a product to treat a medical condition"

## Verification
- How the agent can check its answer is correct
- e.g., "Confirm the policy is in /shared-drive/Policies/ before quoting"

## Anything else
Free-form additional context — FAQs, examples, related skills.
```

**Frontmatter notes:**

- `name`: kebab-case, unique, used as the skill's ID
- `description`: the agent's first impression — make it specific
  - ❌ "OHS information"
  - ✅ "OHS Energy Core supplement: whole-food B-complex + adaptogens for people with mid-afternoon fatigue"
- `status`: MUST be `published` (drafts are invisible to the agent)
- `shared`: MUST be `true` (otherwise only admin sees it)
- `owner`: `ohs-admin` for all OHS-authored skills
- `confidence`: 0.7-0.9 for established content
- `source`: `user` for content the user wrote; `learned` for content
  the AI inferred (rarely used in this case)

---

## 5. Write the skills

After gathering content, structure it into SKILL.md files. **One skill
per topic — don't combine unrelated things.**

Examples of what makes a good single skill:

- ✅ `ohs-products/energy-core` — the Energy Core supplement line
- ✅ `ohs-lab-testing/blood-panel-overview` — what's on the blood panel
- ✅ `ohs-recommendations/how-recs-work` — the methodology
- ❌ `ohs-products/all` — too broad; agent can't pick the right one

Each skill should be **small enough to load quickly** (a few hundred to
~2000 words). If a topic is bigger than that, split it.

---

## 6. Apply frontmatter correctly

For every SKILL.md you create:

```yaml
status: published
shared: true
owner: ohs-admin
```

**The two most common mistakes are forgetting `status: published` (the
agent can't see drafts) or forgetting `shared: true` (only admin sees it).
Always double-check these two.**

---

## 7. Replace the placeholder skills

The 3 existing shared skills in `~/odysseus/data/skills/ohs-shared/`
describe a clinical practice and are misleading:

```
mv ~/odysseus/data/skills/ohs-shared \
   ~/odysseus/data/skills/.placeholder-backup-$(date +%Y%m%d)
```

Then create your new `ohs-company/`, `ohs-products/`, etc. directories.

---

## 8. Verify

After writing the skills:

```bash
# 1. As admin, /api/skills shows all new skills
J=$(mktemp)
curl -sS -c "$J" -X POST 'http://127.0.0.1:7860/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"ohs-admin","password":"OHS-Admin-Pass-2026-Changeme"}' \
  -o /dev/null
curl -sS -b "$J" http://127.0.0.1:7860/api/skills | python3 -m json.tool | head -50

# 2. As a regular user, /api/skills shows them too (shared: true)
# (Use any real username + password; for the live deployment, see
# /Users/ai/odysseus/data/auth.json for the current user list.)
curl -sS -c "$J" -X POST 'http://127.0.0.1:7860/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"REPLACE-ME","password":"REPLACE-ME"}' \
  -o /dev/null
curl -sS -b "$J" http://127.0.0.1:7860/api/skills | python3 -m json.tool | head -50

# 3. /api/skills/index (agent prompt view) shows them
curl -sS -b "$J" http://127.0.0.1:7860/api/skills/index | python3 -m json.tool

# 4. End-to-end: ask the agent in agent mode about something that should hit a skill
SID=$(curl -sS -b "$J" -X POST 'http://127.0.0.1:7860/api/session' \
  --data-urlencode "name=kb-verify" \
  --data-urlencode "endpoint_url=https://api.minimax.io/v1" \
  --data-urlencode "model=MiniMax-M3" \
  --data-urlencode "endpoint_id=4aded1be" \
  --data-urlencode "rag=false" --data-urlencode "skip_validation=true" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
curl -sS -b "$J" -X POST 'http://127.0.0.1:7860/api/chat_stream' \
  -F "mode=agent" \
  -F "message=What's in the Energy Core supplement?" \
  -F "session=$SID" -F "model=MiniMax-M3" -m 120 \
  | grep -E 'data: \{"(delta|type|tool)":' | tail -30
rm -f "$J"
```

If the agent sees the skill in step 3 and either loads it directly or
offers to via `ask_user`, you're good.

---

## 9. Web scraping (if user gives URLs)

```bash
# Fetch a static HTML page and extract text
curl -sSL "https://ohs.example/about" -o /tmp/page.html
python3 -c "
from html.parser import HTMLParser
import re, sys

class Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','nav','footer','header'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script','style','nav','footer','header'):
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data.strip())

s = Stripper()
with open('/tmp/page.html') as f:
    s.feed(f.read())
print('\n'.join(line for line in '\n'.join(s.text).split('\n') if line.strip()))
"
```

For JS-heavy sites, install Playwright once and use it headless:

```bash
pip install playwright
python3 -m playwright install chromium
# then use playwright to fetch + dump
```

Be polite: `sleep 1-2` between requests, respect `robots.txt`. For
OHS's own content, copyright is a non-issue (it's their data); for
third-party content, paraphrase rather than copy.

---

## 10. Common pitfalls

- **Forgetting `status: published`** — agent can't see it. Always set it.
- **Forgetting `shared: true`** — only admin sees it. Always set it.
- **Writing one giant skill instead of several small ones** — the agent
  has to load the whole skill to use it. Small focused skills load fast
  and are easier to maintain.
- **Vague descriptions** — the agent picks skills by description. Make
  them specific.
- **No "When to Use" section** — without it, the agent can't tell when
  the skill applies.
- **No "Pitfalls" section** — the agent then confidently gives wrong
  answers on edge cases (especially regulatory ones).
- **Omitting disclaimers on compliance-relevant skills** — supplements
  have strict FDA/FTC rules about what you can and can't claim.

---

## 11. Order of work (suggested)

1. Read `docs/OHSS-CONTEXT.md` and `docs/HANDOFF.md`
2. Ask the user the questions in § 3 (one category at a time)
3. Move the placeholder skills out of the way (§ 7)
4. Write the company, products, and lab-testing skills first (most
   user-facing)
5. Write the compliance skill **before** the recommendation skill —
   so you can reference the disclaimers when writing recommendations
6. Write the recommendation, quality, and customer-support skills
7. Verify (§ 8)
8. Hand back to the user with a summary of what was added

---

## 12. Where to ask the user for more info

The user said "Let's go with option B. I'll paste content." — they're
ready to paste. If they pause or ask "what do you want next?", prompt
them with the next category from § 3.

If they ask about the previous session's work, point them at
`docs/HANDOFF.md` § "Open issues / things to do next".

If they ask about login, credentials, or admin tasks, point them at
`docs/odysseus-credentials.md` (full user list with passwords).

---

## 13. Post-build fix — make vague questions actually trigger skills (2026-08-02)

After the 57 skills were built, end-to-end testing revealed that **vague employee questions didn't reliably trigger the right skill.** The agent would either answer from the index description (sometimes right, sometimes wrong) or truthfully report "I don't have `manage_skills` in my available tools list" and ask the user to choose how to proceed. This is a deal-breaker for adoption because employees won't write prompts like "use manage_skills to load the X skill" — they'll write "what about the brain pak?" and expect a useful answer.

### Root cause

`src/tool_index.py:ALWAYS_AVAILABLE` only contains `manage_memory`, `ask_user`, and `update_plan`. The system uses RAG-based tool selection (`get_tools_for_query`) to pick the top 8 semantically relevant tools per message and send only those to the model. For vague questions like "what's the return policy?", the semantic search picked email/document tools (because "policy" + "return" are semantically closer to those than to a "skill management" tool) and `manage_skills` got dropped from the tool list. The agent then couldn't call it even though the skill was indexed.

### The fix (3 changes)

1. **`src/tool_index.py`** — add `"manage_skills"` to `ALWAYS_AVAILABLE` so it's always sent to the model, regardless of RAG selection. The comment should explain why (vague questions whose embedding doesn't match a tool name were losing `manage_skills`).

2. **`src/agent_loop.py`** (relevant-skills injection block, around line 2450) — three tweaks:
   - Bump default `_skill_max_injected` from 3 → 12 (and update `data/settings.json` from 3 → 12 to match).
   - Lower the relevance `threshold` from 0.25 → 0.2.
   - Include the skill's `body_extra` (the "Anything else" content where the real detail lives) in the injected block, capped at 6 KB per skill, plus add a stronger system instruction ("Do NOT ask the user to paste skill text or for a URL; you already have the full content.").

3. **No new tools / no schema changes** — this is purely a presentation + gating fix. Existing `manage_skills` action set is unchanged (`view`, `view_ref`, `list`, `search`, `add`, `edit`, `patch`, `publish`, `delete`).

### Test pattern

After the fix, six vague questions all routed correctly without explicit "load the X skill" prompting. See `docs/HANDOFF.md` session 4 update for the full table. Sample test from a real chat:

```
USER: "What is OHS's return policy for opened products?"
AGENT:
  [calls manage_skills {"action": "view", "name": "return-policy"}]
  [loads full SKILL.md body — 6,399 bytes]
  "**OHS return policy for opened products: 30 days** ... full detail ..."
```

To verify the fix is in place after an Odysseus upgrade:

```bash
# 1. manage_skills should be in ALWAYS_AVAILABLE
grep -A 1 "manage_skills" /Users/ai/odysseus/src/tool_index.py | head -3
# expect: a comment + '"manage_skills",' in the ALWAYS_AVAILABLE frozenset

# 2. body_extra should be injected
grep "Full body:" /Users/ai/odysseus/src/agent_loop.py
# expect: lines.append("Full body:\n" + body_extra)

# 3. settings.json should be at 12
python3 -c "import json; print(json.load(open('/Users/ai/odysseus/data/settings.json'))['skill_max_injected'])"
# expect: 12
```

If any of those three are missing, the agent will fall back to the pre-fix behavior (vague questions fail).

### Caveat

The `ohs-lab-testing/test-reference-*` skills are 7–53 KB each. With `max_injected=12` and a 6 KB per-skill cap on `body_extra`, only the most relevant test reference will be inlined for any single question. For specific test-value questions, the agent will call `manage_skills view` to load the full body. This is the right tradeoff — we don't want to blow up context with 53 KB of CBC values when the question is about a single marker.

---

## 14. The no-fabrication rule (added session 7)

The user has been clear: the agent must not invent answers. Two failure modes have been observed and need to be defended against:

1. **Fabrication (under-answering the wrong way).** The model invents specific facts (lab partner names, product capabilities, "yes the Deep Dives generate a Custom Pak", etc.) that aren't in the KB. Triggered by the model's tendency to fill gaps with plausible guesses.
2. **Over-defensiveness (under-answering the other wrong way).** The model says "I don't have that in my reference material" or "I'd rather route you than guess" for things that ARE in the loaded skills, because it never actually loaded the skills. Triggered by a "no fabrication" rule that's too strict and makes the model default to deferral.

### The fix (in `src/agent_loop.py` and `ohs-compliance/no-fabrication/SKILL.md`)

The CORRECT workflow the model is told to follow:

1. Look at the skill index in the system prompt. Match the question to a skill by its `When to Use` section.
2. **LOAD the skill** by calling `manage_skills view name=<skill-name>`. Don't just rely on the description.
3. Read the loaded skill body and find the answer.
4. Answer from the loaded body with the right framing.
5. Only if the loaded body does NOT have the answer → say "I don't have that in my reference material."

This is in two places:
- `src/agent_loop.py:_API_AGENT_RULES` — the `## No-fabrication rule (HARD — applies to every answer)` block. Always on, every turn.
- `ohs-compliance/no-fabrication/SKILL.md` v1.1.0 — the full skill with the tested categories (what NOT to invent), the forbidden phrases, and the required phrase patterns.

### What to put in every skill you write

To make the model find and load your skill reliably:

- **Description** in the frontmatter: be specific about what questions the skill answers. The model uses the description to match the question to the skill. ❌ "OHS information" ✅ "OHS shipping policy — processing times, expedited methods, P.O. Box rules, international shipping, customer responsibility for address accuracy, local pickup, and shipping insurance."
- **`## When to Use` section** in the body: list the question variants the skill matches. The model uses this to decide whether to load the skill.
- **`## Pitfalls` section**: list the things the model might get wrong, with ✅/❌ examples. This is critical for preventing fabrication in the specific topic.
- **A "Critical distinction" or "What X is and isn't" table at the top** if there are common confusions. The "Deep Dives don't generate Custom Pak" rule is the canonical example of a confusion that needs a high-priority table at the top of the relevant skills.
- **Specific facts, not paraphrases**: bullet-pointed facts (prices, SKUs, biomarkers, container counts) so the model can quote them. Avoid prose paragraphs of facts.

### How to test a new skill

After adding or updating a skill:

1. Verify it's loaded: `curl -sS -b $J http://127.0.0.1:7860/api/skills/<name> | python3 -m json.tool` (where `$J` is the admin session cookie jar).
2. Verify it's in the index: `curl -sS -b $J http://127.0.0.1:7860/api/skills/index | grep <name>`.
3. In the UI, ask a question whose answer is in the skill. Verify the agent loads the skill (look for the `manage_skills` tool call in the response trace) and answers correctly.
4. In the UI, ask a question whose answer is NOT in the skill. Verify the agent says "I don't have that in my reference material" and routes to support, rather than inventing.

### If the agent still fabricates

- Add the specific failure pattern to the skill's `## Pitfalls` section with a ❌/✅ example. This makes the model more likely to remember next time.
- Check whether the skill's `description` is specific enough to be matched. If the description is too generic, the model may not load the skill.
- Check whether the model itself is too weak to follow the no-fabrication rule. The default model is `MiniMax-M3`; for OHS-specific questions, a stronger model (e.g., `gemma-4-12b` local or a different cloud model) may follow the rule more reliably. The settings.json can override the default model for specific sessions.

### If the agent is over-defensive

- Check whether the model is actually loading the skills. If the agent is saying "I don't have that" for things that ARE in the skills, it's probably not loading them.
- Add explicit hints in the relevant skills: "If the user asks about [X], this skill has the answer. Load via `manage_skills view name=...` before responding."
- Verify the skill's `description` mentions the specific topics the model is being asked about. The description is the primary matching signal.

---

**Good luck. The KB is the highest-impact thing you can build right now
— it directly affects what all 25 employees get from the AI every day.**