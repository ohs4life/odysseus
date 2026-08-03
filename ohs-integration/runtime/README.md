# OHS Runtime Snapshot — KB and Settings

This directory is a **disaster-recovery snapshot** of the OHS Odysseus
deployment's knowledge base and the KB-relevant settings. If the Mac
dies and you need to rebuild from scratch, this is what you reach for.

## What's here

| Path | What | Size |
|---|---|---|
| `skills/` | A snapshot of all 180 SKILL.md files that the agent reads at runtime, organized as `data/skills/<category>/<name>/SKILL.md` | 1.8 MB |
| `data-settings-kb-only.json` | Just the KB-relevant fields from `data/settings.json` (5 keys: `default_model`, `default_endpoint_id`, `share_defaults_with_users`, `skill_max_injected`, `skill_autosave_min_confidence`) | <1 KB |
| `restore.sh` | One-shot script: copies the skills into `~/odysseus/data/skills/`, patches the settings, restarts Odysseus | 4 KB |

## What's NOT here (and why)

| Thing | Where it lives | Why not in the repo |
|---|---|---|
| Chat history (`app.db`) | `~/odysseus/data/app.db` | User conversations, may contain sensitive data |
| Uploaded files | `~/odysseus/data/uploads/<user>/` | User-uploaded content, may be sensitive |
| Vector memory | `~/odysseus/data/chroma/` | Can be rebuilt from chat history |
| User credentials (`auth.json`) | `~/odysseus/data/auth.json` | **Has bcrypt password hashes — never commit, even to a private repo** |
| API keys, model credentials | `~/odysseus/.env` and the secret-bearing fields of `data/settings.json` | These are operator-managed secrets |
| Skill usage counters | `~/odysseus/data/skills/_usage.json` | Regenerated on first use after restore |

For the items in the first four rows, the existing nightly backup at
`~/backups/odysseus/<timestamp>/` already captures them. Don't change
your backup strategy — this `runtime/` directory is **not** a substitute.

## How to use this on a fresh Mac

```bash
# 1. Clone the fork
git clone https://github.com/ohs4life/odysseus.git ~/odysseus
cd ~/odysseus

# 2. Install Odysseus and start it (see upstream docs/quickstart)
./start-macos.sh   # or however the install works on a fresh box

# 3. Run the restore script
cd ohs-integration/runtime
./restore.sh
#    Skills copied to ~/odysseus/data/skills/
#    Settings patched into ~/odysseus/data/settings.json
#    Odysseus restarted via launchd

# 4. Verify
curl -sS http://127.0.0.1:7870/healthz | python3 -m json.tool
#    Expect: ok: true
```

## When to re-snapshot

This snapshot gets stale every time the KB regenerator scripts run
(`scripts/kb/build_lab_skills.py` and `scripts/kb/build_product_skills.py`),
or whenever a new skill is added manually via `manage_skills add`.

**Re-snapshot procedure** (run on the live Mac, then commit + push):

```bash
# 1. Regenerate the KB from the latest source
cd ~/odysseus/ohs-integration
python3 scripts/kb/build_lab_skills.py
python3 scripts/kb/build_product_skills.py

# 2. Re-snapshot the runtime state
cd ~/odysseus
rm -rf ohs-integration/runtime/skills
cp -R ~/odysseus/data/skills ohs-integration/runtime/

# 3. Refresh the settings file (in case other KB-relevant keys changed)
python3 -c "
import json
with open('~/odysseus/data/settings.json'.replace('~', '/Users/ai')) as f:
    s = json.load(f)
keys = ['default_model', 'default_endpoint_id', 'share_defaults_with_users',
        'skill_max_injected', 'skill_autosave_min_confidence']
with open('ohs-integration/runtime/data-settings-kb-only.json', 'w') as f:
    json.dump({k: s[k] for k in keys}, f, indent=2)
"

# 4. Commit and push
git add ohs-integration/runtime/
git commit -m "chore: refresh KB snapshot ($(date +%Y-%m-%d), $(find ohs-integration/runtime/skills -name SKILL.md | wc -l) skills)"
git push fork dev
```

Or, to automate this, add a `scripts/kb/snapshot.sh` that does steps
1-3, and run it after every KB rebuild. (Not yet written; current
workflow is manual as of this snapshot.)

## How big is the snapshot vs. what it replaces?

- `ohs-integration/runtime/skills/`: 1.8 MB on disk (180 SKILL.md files)
- The upstream `data/skills/` on a fresh Odysseus install: empty (0 bytes)
- Net cost: +1.8 MB to the fork, in exchange for instant-recovery of the
  full OHS shared knowledge base.

## Why this lives in the fork and not a separate backup repo

The fork already has the *source* material (knowledgebase/) and the
*regenerator scripts* (scripts/kb/). Adding the *built artifacts*
(runtime/skills/) makes the fork the single source of truth for
"everything OHS needs to run Odysseus." No more "where do I look?"
hesitation. The cost — 1.8 MB in the repo — is small relative to the
benefit.
