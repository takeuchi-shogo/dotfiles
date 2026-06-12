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

# アクティブ skill 数 = ディレクトリ実数 - skillOverrides "off" 抑制分。
# 退役は skillOverrides 抑制 (可逆、SKILL.md 不編集) で行いディレクトリは残るため、
# 実数を数えると退役済み skill が永遠に ALERT を出し続ける。
# jq は cron PATH (/usr/bin:/bin) に不在のため /usr/bin/python3 を使う
COUNT=$(/usr/bin/python3 - <<'PYEOF'
import glob
import json
import os

home = os.path.expanduser("~")
dirs = [d for d in glob.glob(f"{home}/.claude/skills/*") if os.path.isdir(d)]
try:
    with open(f"{home}/.claude/settings.json") as f:
        overrides = json.load(f).get("skillOverrides", {})
except (OSError, json.JSONDecodeError):
    overrides = {}
off = {k for k, v in overrides.items() if v == "off"}
print(sum(1 for d in dirs if os.path.basename(d) not in off))
PYEOF
) || { echo "[$(date -Iseconds)] python3 count failed, skip" >> "$LOG"; exit 0; }
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
