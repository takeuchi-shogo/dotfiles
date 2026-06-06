#!/usr/bin/env bash
# run-plan-close-scan.sh — docs/plans/active/ を走査し close 候補を Tier 別に検出
# cron: 50 0 * * *  (DAILY gate)
# dry-run のみ。auto-apply (--apply-tier1) は calibration milestone まで開放しない。
# output: docs/plan-close/<date>-close-report.md + candidates.jsonl (pending source of truth)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="plan-close-scan"
REPO="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# === Cleanup trap (status_end on unexpected exit) ===
_cleanup() {
    local ec=$?
    if [[ -n "${_NIGHTLY_CURRENT_TASK:-}" ]]; then
        status_end fail "trapped exit_code=$ec"
    fi
}
trap _cleanup EXIT

# === Prereq guards ===
for cmd in python3 git; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found in PATH"
        exit 0
    fi
done

# === Gate ===
should_run_today "$TASK" DAILY "" 0 || exit 0

status_begin "$TASK"

cd "$REPO"
OUT=$(python3 scripts/lifecycle/plan-close-detector.py 2>&1) || {
    status_end fail "detector exit non-zero: ${OUT}"
    exit 0
}

# detector の stdout "scanned: N candidates → ..." から件数を抽出 (metric 用)
COUNT=$(printf '%s' "$OUT" | sed -nE 's/^scanned: ([0-9]+) candidates.*/\1/p')
COUNT="${COUNT:-0}"

status_end ok "scan complete" "metric.candidates=${COUNT}" \
    "report=docs/plan-close/${NIGHTLY_DATE}-close-report.md"
