#!/usr/bin/env bash
# skill 数が threshold を超えたら Inbox に警告 (catch-up: 月-水 まで)

set -euo pipefail

THRESHOLD=110
LOG=/tmp/skill-count-alert.log
INBOX="$HOME/Documents/Obsidian Vault/00-Inbox"
TODAY="$(date +%Y%m%d)"
DOW="$(date +%u)"
ALERT="$INBOX/skill-count-alert-${TODAY}.md"

# Idempotent: その日の alert あれば skip
[ -f "$ALERT" ] && exit 0
# Catch-up window: Mon-Wed
[ "$DOW" -gt 3 ] && exit 0
# 今週の alert が既にあれば skip
if find "$INBOX" -name 'skill-count-alert-*.md' -mtime -7 2>/dev/null | grep -q .; then
  echo "[$(date -Iseconds)] this week's alert exists, skip" >> "$LOG"
  exit 0
fi

COUNT=$(find -L "$HOME/.claude/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')

if [ "$COUNT" -gt "$THRESHOLD" ]; then
  mkdir -p "$INBOX" 2>/dev/null
  if [ -d "$INBOX" ]; then
    {
      echo "# Skill Count Alert"
      echo
      echo "Date: $(date -Iseconds)"
      echo "Count: **$COUNT** (threshold: $THRESHOLD)"
      echo
      echo "Pruning が必要です。\`/skill-audit\` または skill-usage-weekly レポートを確認してください。"
    } > "$ALERT"
  fi
  echo "[$(date -Iseconds)] ALERT count=$COUNT threshold=$THRESHOLD" >> "$LOG"
else
  echo "[$(date -Iseconds)] OK count=$COUNT threshold=$THRESHOLD (DOW=$DOW)" >> "$LOG"
fi
