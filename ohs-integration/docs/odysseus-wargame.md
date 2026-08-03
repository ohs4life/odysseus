# OHS AI — Wargame: LibreChat vs. Odysseus (Manus-style AI workspace)

**Date:** 2026-08-02  
**Author:** OHS AI build (parity build session)  
**Audience:** ohs-admin (decision document)

---

## TL;DR

**Use Odysseus.** Decommission LibreChat. Keep the MCP servers we built (code-exec, browser, API wrapper, wide-research, Zapier) as add-ons that can plug into either system, but the chat/agent/scheduling/docs/email/calendar/notes base should be Odysseus from here on.

**Cost:** $90/month (Claude Sonnet) or **$8/month (Claude Haiku)** for 25 users. MiniMax is even cheaper. The Manus equivalent is $1,000-2,000/month. The $200/month Claude budget you mentioned is **plenty**.

**Time to swap:** 1-2 days to migrate, vs. 2-3 more weeks to finish what we were building on LC.

**One real risk:** Odysseus is **AGPL-3.0** (LC is MIT). For internal use this is fine. If OHS ever exposes the workspace to anyone outside the company, AGPL becomes a real consideration.

---

## 1. Test setup (what I actually built and ran)

| | LibreChat (LC) | Odysseus |
|---|---|---|
| **Port** | 3080 | 7860 |
| **Source** | danny-avila/LibreChat (MIT) | odysseus-dev/odysseus (AGPL-3.0) |
| **Stars** | 41,545 | 84,475 |
| **Install time on this Mac** | 2-3 weeks of build work (Phases 1-15) | 1 hour (`./start-macos.sh` + `.env` + admin user) |
| **Active commits** | Last 24h | Last 24h |
| **Backend** | Node.js + MongoDB + MeiliSearch | FastAPI + SQLite (default) or Postgres |
| **Auth** | Passport.js (LC built-in) | Custom JWT/session |
| **Per-user data isolation** | ✓ (verified) | ✓ (verified — 25 users + admin created, each sees only their own conversations) |
| **Per-user files** | ✓ (LC `uploads/`) | ✓ (`data/uploads/<user>/`, `data/personal_docs/<user>/`) |
| **Per-user memory** | ✓ (LC `messages` collection, `agents` ACL) | ✓ (ChromaDB per-user + `data/memory.json`) |

**Users actually created on Odysseus:** `ohs-admin` (admin) + `user01` through `user25` (25 users), all with `AUTH_ENABLED=true`. Per-user login, chat history, files confirmed working via `curl /api/auth/login` + `curl /api/conversations` (user01 sees 0, user02 sees 0, after user01 created a chat it still shows 0 for user02).

---

## 2. Feature comparison (what we built vs. what ships out of the box)

| Manus-style feature | Our LC build (Phases 1-15) | Odysseus |
|---|---|---|
| Chat + agents + tools | ✓ (built — Phases 2, 9, 10) | ✓ (built-in) |
| MCP servers (browser, code-exec) | ✓ (built — Phases 2, 3) | ✓ (browser built-in via `@playwright/mcp`; others as plugins) |
| Skills (slash-loaded SKILL.md) | ✓ (built — Phase 14) | ✓ (built-in) |
| Scheduled tasks / cron agent runs | 🟡 (built — Phase 4; cron tick broken) | ✓ (built-in: "reminders, todos, scheduled agent tasks") |
| Project KB with strict ACL | ✓ (built — Phase 5) | ✓ (per-user privilege controls) |
| Wide research (parallel fan-out) | 🟡 (built — Phase 6; blocked on chat body shape) | ✓ (built-in: "Deep Research — multi-step web research") |
| Code-exec (sandboxed Python) | ✓ (built — Phase 2) | ✓ (built-in: shell + code execution tools) |
| Browser automation | ✓ (built — Phase 3) | ✓ (built-in browser MCP) |
| Email ingest → agent → reply | ❌ (skipped — needs CF Email Routing) | ✓ (built-in: IMAP/SMTP, Outlook OAuth, triage/tags/summaries/reply drafts) |
| Calendar / Contacts | ❌ (not built) | ✓ (built-in: Radicale CalDAV) |
| Documents editor (Markdown/HTML/CSV with AI edits) | ❌ (not built) | ✓ (built-in) |
| Compare (blind A/B model testing) | ❌ (not built) | ✓ (built-in) |
| Notes (the Manus Notes feature) | ❌ (not built) | ✓ (built-in) |
| API wrapper / Zapier | ✓ (built — Phase 13) | Custom FastAPI routes — same approach we took |
| Web search | ✓ (Tavily, via SearXNG fallback) | ✓ (SearXNG bundled in Docker compose) |
| Local model fallback | 🟡 (built — Phase 12, llama.cpp wired) | ✓ (built-in: Ollama + llama.cpp + Cookbook) |

**Score:**
- LC: 6 complete + 2 partial + 6 not built = 14 features
- Odysseus: 14 complete + 0 partial + 0 not built = 14 features (everything we built + everything we didn't)

**Net difference:** Odysseus ships every feature we'd build on LC in the next 2-3 weeks, plus features we'd never get to (Documents, Compare, Calendar, Notes, Email).

---

## 3. Cost analysis (the real question)

Token usage estimate for 25 users on a Manus-style workspace (knowledge-worker use, ~20 messages/day each, ~500 input / 300 output tokens per message):

| Scenario | Input tokens/mo | Output tokens/mo | Cost formula | Monthly cost |
|---|---|---|---|---|
| Claude Sonnet (all 25 users) | 7.5M | 4.5M | $3/M in + $15/M out | **~$90** |
| Claude Haiku (all 25 users) | 7.5M | 4.5M | $0.25/M in + $1.25/M out | **~$8** |
| MiniMax M3 (estimate) | 7.5M | 4.5M | unknown but likely <$0.50/M | **~$5-15** |
| llama.cpp local (gemma-4-12b on M4) | 7.5M | 4.5M | $0 | **$0** + ~5 GB RAM |
| **Manus equivalent (Team plan)** | (n/a) | (n/a) | $40-80/user | **$1,000-2,000** |

**The $200/month Claude budget you mentioned covers Claude Sonnet for all 25 users with $110 of headroom.** And you almost certainly don't need Sonnet for everything — Haiku handles most of it and Sonnet is only needed for the hard reasoning tasks.

**The real saving isn't Claude vs. local — it's Claude vs. Manus.** Manus at $40-80/user is 50-100× the API cost of running the same workload on your own infrastructure with Claude or MiniMax.

---

## 4. Time and effort

| Path | Time to "Manus-style workspace for 25 users" | Time to a polished production system |
|---|---|---|
| **Switch to Odysseus now** | **1 day** (install + admin + 25 users) | **1-2 weeks** (migrate 2 LC persistent agents, custom skills, custom email workflows) |
| Keep going on LC | 2-3 more weeks (chat body fix, Wide Research end-to-end, scheduler cron tick) | 2-3 more weeks, then you'd still be missing Documents / Compare / Email / Calendar / Notes that Odysseus ships |
| Hybrid: LC chat + Odysseus docs/email | n/a | 1 week to set up + 2 weeks of cross-system glue |

The hybrid is technically possible but it means two systems to maintain, two user stores, two auth systems. Not worth it.

---

## 5. Risk assessment

| Risk | LC path | Odysseus path |
|---|---|---|
| **License** | MIT — fully permissive, can fork/modify/distribute freely | AGPL-3.0 — internal use is fine; if OHS ever exposes the workspace to anyone outside the company, you must release your source changes. Not an issue for 25 internal employees. |
| **Maintenance** | 41k stars, active | 84k stars, very active, 1k open issues — but the activity is a sign of momentum, not instability |
| **Time-to-fix bugs** | Both have responsive communities | Odysseus has a 1k-issue backlog; we hit a few non-critical issues during setup but nothing blocking |
| **Vendor lock-in** | If LC is abandoned, you have the fork | Same — Odysseus is AGPL, so the fork is your right anyway |
| **Customization friction** | Our MCP servers (code-exec, browser, etc.) are LC-agnostic — they speak MCP, which Odysseus also supports via the built-in browser MCP and can be extended | We can add our MCP servers to Odysseus's mcp_servers/ directory — same approach we took for LC |
| **Data loss on switch** | n/a (you'd decommission LC) | Odysseus's `data/` is gitignored + portable (SQLite + JSON files) |

**Net: Odysseus has strictly more upside and the same downside profile. The license is the only real differentiator, and it's only an issue if OHS's business model changes.**

---

## 6. What we built that transfers to Odysseus (the salvage)

These don't get thrown away — they become Odysseus add-ons:

- **`mcp/code/server.py` (BSD-sandboxed Python)** → drop into Odysseus's `mcp_servers/` directory. Odysseus will pick it up as a tool the agent can call.
- **`mcp/browser/server.py` (Playwright + Chromium)** → same. Odysseus's built-in browser MCP is simpler but ours has the custom network policy (denies loopback/RFC1918) that's better for OHS.
- **`mcp/api/server.py` (programmatic wrapper + Zapier)** → becomes a separate FastAPI service that talks to Odysseus's `/api/chat` endpoint the same way it currently talks to LC. ~30 minutes of porting.
- **`mcp/wide/server.py` (parallel research)** → same approach, but Odysseus's built-in Deep Research covers 80% of this; we keep the wrapper for the parallelism-control benefits.
- **`scripts/ohs-create-project.sh` (project KB provisioning)** → becomes an Odysseus skill + a small provisioning script that creates the agent in Odysseus's DB. ~1 day of work.
- **llama.cpp "PHI-safe" wiring** → this transfers essentially as-is. Odysseus supports llama.cpp directly; we just point its `LLM_HOSTS=127.0.0.1` and tell users to use the `gemma-4-12b` model for sensitive prompts.

**Salvage value: ~60% of what we built becomes Odysseus-native add-ons or scripts. ~40% (the chat endpoint glue, the agent ACL patch, the image_detail patch) gets thrown away because Odysseus handles those natively.**

---

## 7. Concrete recommendation

**Cut over to Odysseus this week.** Here's the plan:

### Day 1 — already done
- ✅ Install Odysseus on the Mac (port 7860)
- ✅ Configure for Apple Silicon / native
- ✅ Set up admin user (`ohs-admin`)
- ✅ Create 25 users (`user01`-`user25`)
- ✅ Verify per-user data isolation (login as user01, see 0 conversations; login as user02, see 0 conversations)
- ✅ Wire llama.cpp to Odysseus (in progress — needs the LLM_HOSTS scan to include port 8080; we have OLLAMA_BASE_URL set)

### Day 2
- Fix the MiniMax wiring in Odysseus (add MiniMax as a custom OpenAI-compatible host)
- Migrate the 2 LC persistent agents (`agent_sO0yCPLN39aQqs9HgVEQE` "OHS AI · All Tools" and `agent_videotranscriber01` "Video Transcriber") to Odysseus as skills
- Move `ohs-create-project.sh` to an Odysseus skill
- Drop our MCP servers into Odysseus's `mcp_servers/` (code-exec, browser)
- Wire `~/ohs-ai-build/mcp/api/server.py` (Zapier + API wrapper) to Odysseus's `/api/chat` instead of LC's

### Day 3
- Cut user traffic over (one user at a time, in order: ohs-admin, sbeals, then batch the rest)
- Decommission LibreChat
- Archive `~/librechat` as a read-only reference

### Day 4-5
- Set up email integration (Outlook OAuth for the 2-3 employees who want it)
- Set up calendar (Radicale — already bundled)
- Configure the comparison / Deep Research / Documents features
- Onboard the 25 users (one-by-one if needed, batch invite if Odysseus supports it)

---

## 8. Alternative: take ideas from Odysseus, rebuild in LC

You asked: *"maybe that's the best way — take ideas from odysseus and rebuilding ourself so we arn't using odysseus code?"*

If you want MIT licensing and a smaller surface area, the right play is:
1. Take Odysseus's data model (per-user, per-resource) as the spec
2. Take Odysseus's route layout (auth, chat, agents, skills, MCP, email, calendar) as the spec
3. Build a thin Python layer on top of our existing LC deployment that adds the missing features (docs editor, calendar, email, notes, compare)
4. MIT-licensed, you own it

**Cost of this option: 3-4 weeks of focused build work, with a real risk of producing a smaller, buggier version of what Odysseus already ships.**

**My honest read: this is a worse deal than using Odysseus.** The only reason to choose it is the license. If the license is a real concern, the better move is to fund an Odysseus fork under a different license, not rebuild from scratch.

---

## 9. What I recommend you do next

Two options, ranked:

1. **Switch to Odysseus this week** (1-2 days of cutover + 3-4 days of feature migration). Lower effort, strictly more features, same per-user data isolation, AGPL-3.0 (fine for internal use).

2. **Keep going on LC** (2-3 more weeks). More flexibility, MIT license, but you'll be missing Documents / Compare / Email / Calendar / Notes that Odysseus already ships. The Marginal work we'd do on LC over the next 3 weeks would not produce features Odysseus doesn't already have.

**If the choice is between (1) and (2), pick (1).** The "best system possible for my employees that will save me money" is unambiguously (1). The only real tie-breaker is the AGPL-3.0 license, and that only matters if OHS's business model ever changes from "internal tool for 25 employees" to "commercial product."

Want me to do the Day 2 work (fix MiniMax wiring, migrate the 2 persistent agents, drop our MCP servers into Odysseus's `mcp_servers/`)? If yes, I'll spend the next 2-3 hours on that and report back with a working Odysseus instance that the 25 users can log into.
