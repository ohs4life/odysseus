#!/bin/bash
# rotate-logs-ohs.sh — daily rotation for any *:7860-area logs.
# Compresses anything > 1 day old, deletes anything > 14 days.
set -euo pipefail
LOG_DIRS=(
  "$HOME/ohs-ai-build/logs"
  "$HOME/odyssey/logs"
  "$HOME/.cloudflared"
)
for d in "${LOG_DIRS[@]}"; do
  [ -d "$d" ] || continue
  # Compress anything .log older than 1 day that is not already .gz
  find "$d" -type f -name '*.log' -mtime +1 ! -name '*.gz' 2>/dev/null \
    | while read -r f; do
      gzip -- "$f" 2>/dev/null || true
    done
  # Delete .log.gz older than 14 days
  find "$d" -type f -name '*.log.gz' -mtime +14 -delete 2>/dev/null || true
done
