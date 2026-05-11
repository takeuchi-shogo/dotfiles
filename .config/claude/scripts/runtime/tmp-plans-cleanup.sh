#!/usr/bin/env bash
# tmp/plans の random codename ephemeral plan を 30 日 stale で削除
# 命名 pattern X-Y-Z[(-agent-HASH)?] のみ対象、名前付き (date prefix / descriptive) は保護
# Idempotent: 削除済みファイルは無害

set -euo pipefail

PLANS_DIR="$HOME/dotfiles/tmp/plans"
LOG=/tmp/tmp-plans-cleanup.log
TODAY="$(date +%Y%m%d)"
DOW="$(date +%u)"

# Mon-Wed のみ catch-up window で実行
[ "$DOW" -gt 3 ] && exit 0
[ -d "$PLANS_DIR" ] || { echo "[$(date -Iseconds)] $PLANS_DIR missing" >> "$LOG"; exit 0; }

deleted=0
find "$PLANS_DIR" -maxdepth 1 -type f -mtime +30 -name "*.md" 2>/dev/null | while read -r f; do
  bn=$(basename "$f" .md)
  if echo "$bn" | grep -qE '^[a-z]+-[a-z]+-[a-z]+(-agent-[a-f0-9]+)?$'; then
    /bin/rm -f "$f"
    deleted=$((deleted + 1))
    echo "[$(date -Iseconds)] removed: $bn" >> "$LOG"
  fi
done
echo "[$(date -Iseconds)] cleanup done (DOW=$DOW)" >> "$LOG"
