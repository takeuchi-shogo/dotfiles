#!/usr/bin/env bash
# session-stats.sh — SessionEnd で累積統計を記録する
# Stop hook から呼び出される。失敗しても hook チェーンを止めない
set -uo pipefail

STATS_FILE="$HOME/.claude/session-stats.json"
START_FILE="/tmp/claude-session-start.txt"

# セッション時間の計算
DURATION=0
if [[ -f "$START_FILE" ]]; then
  START=$(cat "$START_FILE" 2>/dev/null || echo 0)
  # 数値でなければ 0 にフォールバック
  [[ "$START" =~ ^[0-9]+$ ]] || START=0
  NOW=$(date +%s)
  DURATION=$((NOW - START))
fi

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# 整合性チェック
CLAUDE_MD_OK=false
SETTINGS_OK=false
[[ -f "$HOME/.claude/CLAUDE.md" ]] && CLAUDE_MD_OK=true
[[ -f "$HOME/.claude/settings.json" ]] && SETTINGS_OK=true

# 既存ファイルの読み込みまたは初期化
TOTAL=0
if [[ -f "$STATS_FILE" ]]; then
  TOTAL=$(jq -r '.total_sessions // 0' "$STATS_FILE" 2>/dev/null || echo 0)
fi
[[ "$TOTAL" =~ ^[0-9]+$ ]] || TOTAL=0

TOTAL=$((TOTAL + 1))

# アトミック書き込み (temp → mv)
TMP_FILE="${STATS_FILE}.tmp"
if jq -n \
  --argjson total "$TOTAL" \
  --argjson duration "$DURATION" \
  --arg ts "$TIMESTAMP" \
  --argjson claude_md "$CLAUDE_MD_OK" \
  --argjson settings "$SETTINGS_OK" \
  '{
    total_sessions: $total,
    last_session_duration_sec: $duration,
    last_session_at: $ts,
    integrity: { claude_md: $claude_md, settings_json: $settings }
  }' > "$TMP_FILE" 2>/dev/null; then
  mv "$TMP_FILE" "$STATS_FILE"
else
  rm -f "$TMP_FILE"
fi
