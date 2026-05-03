#!/usr/bin/env bash
# skill 数が threshold を超えたら Inbox に警告

set -euo pipefail

THRESHOLD=110
LOG=/tmp/skill-count-alert.log
INBOX="$HOME/Documents/Obsidian Vault/Inbox"
TODAY="$(date +%Y%m%d)"

COUNT=$(find -L "$HOME/.claude/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')

if [ "$COUNT" -gt "$THRESHOLD" ]; then
  ALERT="$INBOX/skill-count-alert-${TODAY}.md"
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
  echo "[$(date -Iseconds)] OK count=$COUNT threshold=$THRESHOLD" >> "$LOG"
fi
