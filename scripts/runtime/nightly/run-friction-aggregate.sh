#!/usr/bin/env bash
# run-friction-aggregate.sh — 前日 friction events の集計
# cron: 20 23 * * *  (DAILY gate)
#
# Codex Gate 反映:
#   Q1 (C5): .friction_class 主キー、fallback .type
#   M4: FRICTION_LOG_OVERRIDE env で dry-run 安全化 (mv で実 log を退避する必要なし)
#   Q10 (C1): preflight + TIMEOUT_BIN は本タスクでは不要 (claude -p 使わず)
#   M3: report は mktemp + atomic mv
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="friction-aggregate"

_cleanup() {
    local ec=$?
    if [[ -n "${_NIGHTLY_CURRENT_TASK:-}" ]]; then
        status_end fail "trapped exit_code=$ec"
    fi
}
trap _cleanup EXIT

# Prereq guards
if [[ -z "${OBSIDIAN_VAULT_PATH:-}" ]]; then
    status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"
    exit 0
fi
for cmd in jq; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found in PATH"
        exit 0
    fi
done

# M4: FRICTION_LOG_OVERRIDE で dry-run 安全化
FRICTION_LOG="${FRICTION_LOG_OVERRIDE:-$HOME/.claude/agent-memory/learnings/friction-events.jsonl}"
if [[ ! -f "$FRICTION_LOG" ]]; then
    status_begin "$TASK"; status_end fail "friction log not found: $FRICTION_LOG"
    exit 0
fi

should_run_today "$TASK" DAILY "" 0 || exit 0
status_begin "$TASK"

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-friction.md"
REPORT_TMP=$(mktemp -t "nightly-friction-${NIGHTLY_DATE}.XXXXXX")
trap 'rm -f "$REPORT_TMP"; _cleanup' EXIT

# 前日範囲: 24h 以内
SINCE_TS="$(date -v-1d -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -d 'yesterday' -u +%Y-%m-%dT%H:%M:%SZ)"

# Q1/C5: .friction_class 主キー、.type fallback
# H5 反映: jq -R 'fromjson?' で tolerant parse
CLASS_COUNTS=$(jq -R 'fromjson? | select(.timestamp >= "'"$SINCE_TS"'") | (.friction_class // .type // "unknown")' \
    "$FRICTION_LOG" 2>/dev/null | sort | uniq -c | sort -rn || true)

# Top 10 issues with full context (action_surface + target_hint + evidence)
TOP_ISSUES=$(jq -R --arg since "$SINCE_TS" '
    fromjson? | select(.timestamp >= $since) |
    "- [\(.friction_class // .type // "?")] surface=\(.action_surface // "?") target=\(.target_hint // "-") — \(.evidence // .description // .msg // "(no detail)")"
' "$FRICTION_LOG" 2>/dev/null | head -10 || true)

# Total count
TOTAL_COUNT=$(jq -R --arg since "$SINCE_TS" 'fromjson? | select(.timestamp >= $since) | 1' \
    "$FRICTION_LOG" 2>/dev/null | wc -l | tr -d ' ' || echo 0)
TOTAL_COUNT="${TOTAL_COUNT:-0}"

{
    echo "# Friction Events ${NIGHTLY_DATE} (前日集計)"
    echo ""
    echo "Generated: $(date -Iseconds 2>/dev/null || date)"
    echo "Source: \`${FRICTION_LOG/#$HOME/~}\`"
    echo "Window: 直近 24 時間 (since ${SINCE_TS})"
    echo ""
    echo "## Summary"
    echo "- Total events: ${TOTAL_COUNT}"
    echo ""
    echo "## Friction class breakdown"
    echo '```'
    echo "${CLASS_COUNTS:-(なし)}"
    echo '```'
    echo ""
    echo "## Top 10 issues"
    echo "${TOP_ISSUES:-(なし)}"
} > "$REPORT_TMP"

mv "$REPORT_TMP" "$REPORT_PATH"

status_end ok "total=$TOTAL_COUNT" \
    "report=06-Nightly/${NIGHTLY_DATE}-friction.md" \
    "metric.total=$TOTAL_COUNT"
