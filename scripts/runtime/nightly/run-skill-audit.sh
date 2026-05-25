#!/usr/bin/env bash
# run-skill-audit.sh — skill A/B benchmark + health audit
# cron: 45 23 * * *  (DOW=4 木曜、catch-up 6 days)
# 既存 /skill-audit skill を claude -p で呼び出す (Q2 反映: exact invocation)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="skill-audit"

_cleanup() {
    local ec=$?
    if [[ -n "${_NIGHTLY_CURRENT_TASK:-}" ]]; then
        status_end fail "trapped exit_code=$ec"
    fi
    release_claude_lock
}
trap _cleanup EXIT

if [[ -z "${OBSIDIAN_VAULT_PATH:-}" ]]; then
    status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"
    exit 0
fi
for cmd in jq claude; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found"
        exit 0
    fi
done
TIMEOUT_BIN=$(command -v timeout 2>/dev/null || command -v gtimeout 2>/dev/null || true)
if [[ -z "$TIMEOUT_BIN" ]]; then
    status_begin "$TASK"; status_end fail "preflight: timeout/gtimeout not found"
    exit 0
fi

should_run_today "$TASK" DOW 4 6 || exit 0
status_begin "$TASK"

if ! acquire_claude_lock; then
    status_end fail "claude lock timeout"
    exit 0
fi

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-skill.md"
REPORT_TMP=$(mktemp -t "nightly-skill-${NIGHTLY_DATE}.XXXXXX")
trap 'rm -f "$REPORT_TMP"; _cleanup' EXIT

# Q2 反映: exact "/skill-audit" invocation
STDERR_LOG=$(mktemp -t "nightly-skill-stderr.XXXXXX")
if ! "$TIMEOUT_BIN" 900s claude -p "/skill-audit" > "$REPORT_TMP" 2> "$STDERR_LOG"; then
    err_head=$(head -c 200 "$STDERR_LOG" 2>/dev/null || echo "")
    rm -f "$STDERR_LOG"
    status_end fail "claude -p /skill-audit failed/timeout, stderr: $err_head"
    exit 0
fi
rm -f "$STDERR_LOG"

mv "$REPORT_TMP" "$REPORT_PATH"

DORMANT=$(grep -cE 'dormant|未使用|0 calls' "$REPORT_PATH" 2>/dev/null || true)
CONFLICTS=$(grep -cE '衝突|conflict' "$REPORT_PATH" 2>/dev/null || true)
DORMANT="${DORMANT:-0}"
CONFLICTS="${CONFLICTS:-0}"

status_end ok "dormant=$DORMANT conflicts=$CONFLICTS" \
    "report=06-Nightly/${NIGHTLY_DATE}-skill.md" \
    "metric.dormant=$DORMANT" "metric.conflicts=$CONFLICTS"
