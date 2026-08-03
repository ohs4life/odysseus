#!/usr/bin/env bash
# restore.sh — restore the OHS KB + settings from this directory.
#
# Use case: the Mac died. The OHS Odysseus deployment is rebuilt from
# scratch (re-cloned from this fork, deps installed, etc.). Before
# starting the agent, you want the 180 SKILL.md files and the KB-relevant
# settings back in place so the agent has the OHS knowledge base.
#
# Usage: ./restore.sh
#
# What it does:
#   1. Copies runtime/skills/ to ~/odysseus/data/skills/ (overwriting any
#      stale placeholders or archived skills)
#   2. Patches the KB-relevant fields into ~/odysseus/data/settings.json
#      (leaves all other settings untouched — model choices, API keys,
#      etc. are NOT in the repo and must be reconfigured by the operator)
#   3. Restarts the Odysseus launchd job so the new files are picked up
#
# This does NOT restore:
#   - User credentials (auth.json) — re-create users via the admin UI
#   - Chat history (app.db) — restore from the latest backup at
#     ~/backups/odysseus/<timestamp>/data/app.db
#   - Uploaded files, personal docs, vector memory, etc. — restore from
#     the same backup directory
#   - API keys, model credentials (data/settings.json non-KB fields) —
#     reconfigure manually or restore from a secret manager
#
# Run from this repo's ohs-integration/runtime/ directory, OR pass the
# path to the runtime/ dir as the first argument.

set -euo pipefail

RUNTIME_DIR="${1:-$(cd "$(dirname "$0")" && pwd)}"
SKILLS_SRC="$RUNTIME_DIR/skills"
SETTINGS_FILE="$RUNTIME_DIR/data-settings-kb-only.json"

ODYSSEUS_DIR="${ODYSSEUS_DIR:-$HOME/odysseus}"
SKILLS_DST="$ODYSSEUS_DIR/data/skills"
SETTINGS_DST="$ODYSSEUS_DIR/data/settings.json"

echo "==> restore.sh"
echo "    runtime dir:     $RUNTIME_DIR"
echo "    skills source:   $SKILLS_SRC  ($(find "$SKILLS_SRC" -name SKILL.md | wc -l | tr -d ' ') skills)"
echo "    skills dest:     $SKILLS_DST"
echo "    odysseus dir:    $ODYSSEUS_DIR"
echo

if [ ! -d "$SKILLS_SRC" ]; then
  echo "ERROR: $SKILLS_SRC not found. Run from ohs-integration/runtime/ or pass the path as the first argument." >&2
  exit 1
fi

if [ ! -d "$ODYSSEUS_DIR" ]; then
  echo "ERROR: $ODYSSEUS_DIR not found. Set ODYSSEUS_DIR env var if Odysseus is installed elsewhere." >&2
  exit 1
fi

# --- 1. Restore the skills ---
echo "==> Restoring skills..."
mkdir -p "$SKILLS_DST"
# rsync would be nicer, but cp -R works on every unix and is fine here
# since this is a one-shot restore (not a recurring sync).
cp -R "$SKILLS_SRC"/* "$SKILLS_DST"/
echo "    Copied $(find "$SKILLS_DST" -name SKILL.md | wc -l | tr -d ' ') SKILL.md files."

# --- 2. Patch the KB-relevant fields into settings.json ---
if [ -f "$SETTINGS_FILE" ]; then
  echo "==> Patching KB-relevant settings into $SETTINGS_DST..."
  if [ ! -f "$SETTINGS_DST" ]; then
    echo "    $SETTINGS_DST doesn't exist yet — copying the KB-only file as a starter."
    cp "$SETTINGS_FILE" "$SETTINGS_DST"
  else
    # Use python to merge (jq may not be installed, python is always there)
    python3 - <<PY
import json, sys
with open("$SETTINGS_DST") as f:
    cur = json.load(f)
with open("$SETTINGS_FILE") as f:
    kb = json.load(f)
# Apply the KB keys (the whitelisted ones)
for k, v in kb.items():
    cur[k] = v
with open("$SETTINGS_DST", 'w') as f:
    json.dump(cur, f, indent=2)
    f.write('\n')
print("    Applied KB keys: " + ", ".join(sorted(kb.keys())))
PY
  fi
else
  echo "==> Skipping settings patch (no $SETTINGS_FILE found)"
fi

# --- 3. Restart Odysseus so the new skills + settings are picked up ---
echo
echo "==> Restarting Odysseus via launchd..."
if command -v launchctl >/dev/null 2>&1; then
  launchctl kickstart -k "gui/$(id -u)/com.odysseus.ohs-ai" 2>/dev/null \
    || launchctl stop com.odysseus.ohs-ai && launchctl start com.odysseus.ohs-ai
  echo "    Restarted. Give it ~10s, then check:"
  echo "      curl -sS http://127.0.0.1:7860/api/auth/me"
  echo "      curl -sS http://127.0.0.1:7870/healthz"
else
  echo "    launchctl not found — restart Odysseus manually."
fi

echo
echo "==> Done. To verify the KB loaded:"
echo "      curl -sS -c /tmp/j -X POST http://127.0.0.1:7860/api/auth/login \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"username\":\"ohs-admin\",\"password\":\"YOUR_PASSWORD\"}' -o /dev/null"
echo "      curl -sS -b /tmp/j http://127.0.0.1:7860/api/skills | python3 -m json.tool | head -20"
echo "    Expect: 'count': 180"
