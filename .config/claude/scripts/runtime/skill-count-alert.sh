#!/usr/bin/env bash
# skill 数が threshold を超えたら Inbox に警告 (catch-up: 月-水 まで)

set -euo pipefail

THRESHOLD=110
LOG=/tmp/skill-count-alert.log
INBOX="$HOME/Documents/Obsidian Vault/00-Inbox"
TODAY="$(date +%Y%m%d)"
DOW="$(date +%u)"
ALERT="$INBOX/skill-count-alert-${TODAY}.md"
STATE_DIR="$HOME/.cache/skill-health"
STATE_FILE="$STATE_DIR/last-count-alert.txt"
THIS_WEEK="$(date +%G-W%V)"

# 週次ゲートは状態ファイルで判定する。Inbox の出力ファイル存在で判定すると、
# ユーザーが Inbox を処理 (移動/削除) した翌日に catch-up が再発火し毎日 ALERT になる
if [ "$(cat "$STATE_FILE" 2>/dev/null)" = "$THIS_WEEK" ]; then
  exit 0
fi
# Catch-up window: Mon-Wed
[ "$DOW" -gt 3 ] && exit 0

COUNT=$(find -L "$HOME/.claude/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
mkdir -p "$STATE_DIR" || { echo "[$(date -Iseconds)] mkdir STATE_DIR failed, skip" >> "$LOG"; exit 0; }
echo "$THIS_WEEK" > "$STATE_FILE"

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
