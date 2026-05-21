#!/usr/bin/env bash
# inject-review-prompt.sh — cmux PR Review Agent の Setup pane から
# Claude pane に `@REVIEW_TASK.md` を自動投入する。
# Setup pane の command 末尾で `... &` バックグラウンド起動する。
# Claude REPL の準備完了を検出する手段がないため固定 sleep で待つ。

set -uo pipefail

readonly WAIT_SEC=5
readonly REPL_READY_SEC=3
readonly SURFACE_NAME="Claude Review"
readonly PROMPT='@REVIEW_TASK.md'
readonly LOG_DIR="${HOME}/Library/Logs/pr-reviewer"
readonly LOG_FILE="${LOG_DIR}/poll.log"

mkdir -p "$LOG_DIR"
log() { printf '%s [inject:%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$$" "$*" >> "$LOG_FILE"; }

sleep "$WAIT_SEC"

# cmux は UUID 形式の workspace handle を reject するため `cmux identify` で
# 自身が居る pane の workspace short ref (workspace:N) を取る
ws_ref=$(cmux identify 2>/dev/null | jq -r '.caller.workspace_ref // empty' 2>/dev/null)
if [[ -z "$ws_ref" ]]; then
  log "skip: cmux identify did not return workspace_ref"
  exit 0
fi

# Claude pane の surface 登録は state file 待ち等で遅延しうるため retry で待つ
# (selected surface 行は "* surface:N  Name  [selected]" で $1 が "*" になるので
#  grep -oE で行から surface:N を直接抽出)
surface_ref=""
for attempt in $(seq 1 10); do
  surface_ref=$(cmux list-pane-surfaces --workspace "$ws_ref" 2>/dev/null \
    | grep -F "$SURFACE_NAME" \
    | grep -oE 'surface:[0-9]+' \
    | head -1)
  [[ -n "$surface_ref" ]] && break
  sleep 1
done

if [[ -z "$surface_ref" ]]; then
  log "skip ws=$ws_ref: surface '$SURFACE_NAME' not found after $WAIT_SEC+10s"
  exit 0
fi

# surface 検出 ≠ claude REPL ready。REPL 起動 (token check + UI) を少し待つ
sleep "$REPL_READY_SEC"

if cmux send --surface "$surface_ref" "$PROMPT" 2>>"$LOG_FILE"; then
  log "sent prompt to $surface_ref"
  sleep 0.3
  cmux send --surface "$surface_ref" $'\r' 2>>"$LOG_FILE" \
    && log "sent Enter to $surface_ref" \
    || log "warn: Enter send failed for $surface_ref"
else
  log "ERROR: cmux send failed for $surface_ref"
fi
