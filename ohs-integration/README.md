# OHS Integration Layer

This directory contains everything OHS-specific that lives **on top of** the
upstream Odysseus product. It's namespaced under `ohs-integration/` to keep
our customizations clearly separate from upstream code, which makes
merging upstream changes straightforward.

## What's in here

| Path | What |
|---|---|
| `docs/` | OHS documentation — handoff, KB build playbook, employee onboarding, Cloudflare Access setup, credentials, wargame, company context |
| `knowledgebase/` | Source material for the OHS shared knowledge base (about-ohs, policies, products, labs) — used by the KB regenerator scripts |
| `scripts/` | OHS-specific operational scripts (backup, log rotation, battletest, KB regenerators) |
| `services/healthz/` | The healthz monitoring service (Python) that checks Odysseus, MiniMax, and llama.cpp |
| `launchd/` | Reference copies of the launchd plists that run the OHS services (the live copies are in `~/Library/LaunchAgents/`) |
| `env/` | Environment-variable snippets (e.g., `parity.env.append` — config templates) |

## What's NOT in here

- **Upstream Odysseus code** — that's in the parent directories. Don't
  add upstream-style code (Python services, React UI, etc.) into
  `ohs-integration/` — it should be a top-level change in the right
  upstream convention, or stay in `ohs-integration/` only as a thin
  glue layer.
- **User data** — chat history, uploaded files, etc. live in
  `~/odysseus/data/` (the upstream data dir). The nightly backup at
  `~/backups/odysseus/` captures them.
- **Real secrets** — never commit API keys, real passwords, or tokens.
  The `odysseus-credentials.md` here has placeholder passwords only
  (all end in `-Changeme` and are flagged for rotation before going
  live). For real credentials, use environment variables or a secret
  manager.

## How to re-deploy after a fresh clone

1. **Set up the Python venv** (the healthz service has its own):
   ```bash
   cd ~/odysseus
   source .venv/bin/activate  # upstream Odysseus venv
   pip install -r ohs-integration/services/healthz/requirements.txt  # if separated
   ```

2. **Install the launchd plist** for the healthz service:
   ```bash
   cp ohs-integration/launchd/com.ohs.ai.healthz.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.ohs.ai.healthz.plist
   ```

3. **Set up the nightly backup + log rotation** (add to cron or launchd):
   ```bash
   crontab -e
   # 02:30 nightly backup
   30 2 * * * /Users/ai/odysseus/ohs-integration/scripts/backup-odysseus.sh
   # 03:15 nightly log rotation
   15 3 * * * /Users/ai/odysseus/ohs-integration/scripts/rotate-logs-ohs.sh
   ```

4. **Re-generate the KB** after adding new source material:
   ```bash
   cd ~/odysseus/ohs-integration
   python3 scripts/kb/build_lab_skills.py      # from knowledgebase/labs/ohs_lab_test_descriptions_v3.md
   python3 scripts/kb/build_product_skills.py  # from knowledgebase/products/products_export_*.csv
   # Output goes to ~/odysseus/data/skills/ (gitignored, runtime data)
   ```

## How to upstream a change

1. Branch off `dev`: `git checkout -b ohs/<feature> fork/dev`
2. Make the change in the right place:
   - Generic Odysseus improvement → change the upstream-style code at the top level
   - OHS-specific glue → add to `ohs-integration/`
3. Commit, push, open a PR upstream
4. If it's truly OHS-specific, keep it on the fork's `dev` branch and don't PR

See `docs/HANDOFF.md` for the full workflow history and decision rationale.
