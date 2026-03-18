#!/bin/sh
# Track planning accuracy: planned vs actual tasks
# Usage: accuracy-tracker.sh [YYYY-MM-DD]
set -e
DATE="${1:-$(date +%Y-%m-%d)}"
VAULT="$HOME/Documents/Obsidian Vault/07-Daily"
FILE="$VAULT/$DATE.md"
if [ ! -f "$FILE" ]; then echo "No daily note for $DATE"; exit 0; fi
PLANNED=$(grep -c '^\- \[.\]' "$FILE" 2>/dev/null || echo 0)
DONE=$(grep -c '^\- \[x\]' "$FILE" 2>/dev/null || echo 0)
if [ "$PLANNED" -gt 0 ]; then
  RATE=$((DONE * 100 / PLANNED))
  echo "{\"date\":\"$DATE\",\"planned\":$PLANNED,\"done\":$DONE,\"rate\":$RATE}"
else
  echo "{\"date\":\"$DATE\",\"planned\":0,\"done\":0,\"rate\":0}"
fi
