#!/usr/bin/env bash
# inject-review-prompt.sh — cmux PR Review Agent の Setup pane から
# Claude pane に `@REVIEW_TASK.md` を自動投入する。
# Setup pane の command 末尾で `... &` バックグラウンド起動する。
# Claude REPL の準備完了を検出する手段がないため固定 sleep で待つ。

set -uo pipefail

readonly WAIT_SEC=15
readonly SURFACE_NAME="Claude Review"
readonly PROMPT='@REVIEW_TASK.md'
readonly LOG_DIR="${HOME}/Library/Logs/pr-reviewer"
readonly LOG_FILE="${LOG_DIR}/poll.log"

mkdir -p "$LOG_DIR"
log() { printf '%s [inject:%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$$" "$*" >> "$LOG_FILE"; }

ws_id="${CMUX_WORKSPACE_ID:-}"
if [[ -z "$ws_id" ]]; then
  log "skip: CMUX_WORKSPACE_ID not set"
  exit 0
fi

sleep "$WAIT_SEC"

surface_ref=$(cmux list-pane-surfaces --workspace "workspace:${ws_id}" 2>/dev/null \
  | awk -v name="$SURFACE_NAME" '$0 ~ name {print $1; exit}')

if [[ -z "$surface_ref" ]]; then
  log "skip ws=$ws_id: surface '$SURFACE_NAME' not found"
  exit 0
fi

# list-pane-surfaces は selected surface に `*` プレフィックスを付ける
surface_ref="${surface_ref#\*}"

if cmux send --surface "$surface_ref" "$PROMPT" 2>>"$LOG_FILE"; then
  log "sent prompt to $surface_ref"
  sleep 0.3
  cmux send --surface "$surface_ref" $'\r' 2>>"$LOG_FILE" \
    && log "sent Enter to $surface_ref" \
    || log "warn: Enter send failed for $surface_ref"
else
  log "ERROR: cmux send failed for $surface_ref"
fi
