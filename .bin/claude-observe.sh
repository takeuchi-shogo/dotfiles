#!/bin/bash
set -euo pipefail
# claude-observe: Claude Code + session-observer を全層観測モードで起動
# Usage: claude-observe.sh [--replay] [claude args...]
# Logs: ~/.claude/agent-memory/logs/observe/{yyyy-mm-dd}/

DATE="$(date +%Y-%m-%d)"
OBSERVE_DIR="$HOME/.claude/agent-memory/logs/observe/$DATE"
DEBUG_LOG="$OBSERVE_DIR/debug-raw.log"
OBSERVER_LOG="$OBSERVE_DIR/observer.log"
SCRIPT_DIR="$HOME/.claude/scripts/runtime"

mkdir -p "$OBSERVE_DIR"

if [[ "${1:-}" == "--replay" ]]; then
    shift
    echo "📼 Replaying latest session → $OBSERVE_DIR"
    python3 "$SCRIPT_DIR/session-observer.py" --latest --replay --compact \
        > "$OBSERVER_LOG" 2>&1
    echo "✅ Done. Logs:"
    # shellcheck disable=SC2012
    ls -lh "$OBSERVE_DIR"/*.jsonl 2>/dev/null | awk '{print "  " $NF " (" $5 ")"}'
    exit 0
fi

OBSERVER_PID=""
cleanup() {
    if [[ -n "$OBSERVER_PID" ]]; then
        kill "$OBSERVER_PID" 2>/dev/null || true
        wait "$OBSERVER_PID" 2>/dev/null || true
    fi
    echo ""
    echo "📊 Observation logs: $OBSERVE_DIR"
    if ls "$OBSERVE_DIR"/*.jsonl >/dev/null 2>&1; then
        # shellcheck disable=SC2012
        ls -lh "$OBSERVE_DIR"/*.jsonl | awk '{print "  " $NF " (" $5 ")"}'
    else
        echo "  (no JSONL logs yet)"
    fi
}
trap cleanup EXIT

# --- start observer (delayed background) ---
# 3秒待ってからセッション transcript を検出し tail 開始
(
    sleep 3
    exec python3 "$SCRIPT_DIR/session-observer.py" \
        --latest --debug-log "$DEBUG_LOG" --compact
) > "$OBSERVER_LOG" 2>&1 &
OBSERVER_PID=$!

# --- start claude with full debug logging ---
echo "🔍 Full observability mode: $OBSERVE_DIR"
echo "   debug-file: $DEBUG_LOG"
echo ""
claude --debug-file "$DEBUG_LOG" "$@"
