#!/bin/bash
# backup-odysseus.sh — nightly backup of ~/odysseus/data/ + .env
# Runs via cron at 2:30 AM. Keeps last 14 days. Writes to ~/backups/odysseus/.
set -euo pipefail

SRC=~/odysseus
DEST=~/backups/odysseus
TS=$(date +%Y%m%d-%H%M)
LOG="$DEST/logs/backup-$TS.log"

log() { printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$LOG"; }

# Sanity: source exists and has data
[ -d "$SRC/data" ] || { log "FATAL: $SRC/data not found"; exit 1; }
[ -f "$SRC/.env" ] || { log "FATAL: $SRC/.env not found"; exit 1; }

OUT="$DEST/$TS"
mkdir -p "$OUT"
log "starting backup -> $OUT"

# 1. data/ (SQLite + ChromaDB + uploads + memory) — this is the data.
#    -exclude chroma keeps the snapshot small (Chroma can be regenerated).
rsync -a --delete \
  --exclude='data/huggingface' \
  --exclude='data/odysseus_models' \
  --exclude='data/chroma' \
  "$SRC/data/" "$OUT/data/" 2>>"$LOG"

# 2. .env (DB url, admin password hash is in auth.json, model keys, OAuth secrets)
cp -p "$SRC/.env" "$OUT/.env"

# 3. auth.json (admin password hashes — DO NOT skip)
cp -p "$SRC/data/auth.json" "$OUT/auth.json"

# 4. The Odysseus version pin (for reproducible restores)
if [ -d "$SRC/.git" ]; then
  (cd "$SRC" && git rev-parse HEAD) > "$OUT/odysseus-git-rev.txt" 2>/dev/null || true
fi

# 5. Manifest
{
  echo "odysseus backup $TS"
  echo "src=$SRC"
  echo "size: $(du -sh "$OUT" | cut -f1)"
  echo "files: $(find "$OUT" -type f | wc -l | tr -d ' ')"
  echo "users: $(python3 -c "import json; d=json.load(open('$SRC/data/auth.json')); print(len(d.get('users', {})))")"
  echo "models_endpoints: $(python3 -c "import sqlite3; c=sqlite3.connect('$SRC/data/app.db'); print(c.execute('SELECT COUNT(*) FROM model_endpoints').fetchone()[0])" 2>/dev/null || echo '?')"
  echo "sessions: $(python3 -c "import sqlite3; c=sqlite3.connect('$SRC/data/app.db'); print(c.execute('SELECT COUNT(*) FROM sessions').fetchone()[0])" 2>/dev/null || echo '?')"
  echo "messages: $(python3 -c "import sqlite3; c=sqlite3.connect('$SRC/data/app.db'); print(c.execute('SELECT COUNT(*) FROM messages').fetchone()[0])" 2>/dev/null || echo '?')"
} > "$OUT/MANIFEST.txt"

log "done: $(du -sh "$OUT" | cut -f1) in $(find "$OUT" -type f | wc -l | tr -d ' ') files"

# 6. Prune: keep last 14 days
find "$DEST" -maxdepth 1 -mindepth 1 -type d -mtime +14 -exec rm -rf {} +
log "pruned old backups; remaining: $(ls -1 "$DEST" | grep -c '^[0-9]' || echo 0)"

# 7. Mirror to a second location if BACKUP_MIRROR is set
if [ -n "${BACKUP_MIRROR:-}" ] && [ -d "${BACKUP_MIRROR}" ]; then
  mkdir -p "${BACKUP_MIRROR}"
  rsync -a --delete "$DEST/" "${BACKUP_MIRROR}/" 2>>"$LOG"
  log "mirrored to ${BACKUP_MIRROR}"
fi

log "OK"
