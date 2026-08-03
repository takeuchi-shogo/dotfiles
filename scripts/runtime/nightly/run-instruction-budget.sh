#!/usr/bin/env bash
# run-instruction-budget.sh — 週次 instruction budget 計測 (measure-instruction-budget.py)
# cadence: 週次・金曜 (DOW 5 gate, catch-up 6d)
# read-only。measure-instruction-budget.py の閾値超過 (exit 1) は計測結果の warn であって
# runner の障害ではないため status_end ok として記録する。python 自体が起動できずに
# サマリ行を出力できなかった場合のみ status_end fail とする。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="instruction-budget"
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
for cmd in python3; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found in PATH"
        exit 0
    fi
done

# === Gate ===
should_run_today "$TASK" DOW 5 6 || exit 0

status_begin "$TASK"

cd "$REPO"

# measure-instruction-budget.py は閾値超過時に exit 1 を返す (これは計測結果の warn であって
# 起動失敗ではない)。python 自体が起動できずサマリ行 ("[instruction-budget] total=...") を
# 出力できなかった場合のみ runner の失敗として扱う。
OUT=$(python3 .config/claude/scripts/policy/measure-instruction-budget.py 2>&1) || true

TOTAL=$(printf '%s\n' "$OUT" | sed -nE 's/^\[instruction-budget\] total=([0-9]+) tokens, status=(ok|warn|degraded)$/\1/p')
STATUS=$(printf '%s\n' "$OUT" | sed -nE 's/^\[instruction-budget\] total=([0-9]+) tokens, status=(ok|warn|degraded)$/\2/p')

if [[ -z "$TOTAL" || -z "$STATUS" ]]; then
    status_end fail "python did not produce a summary line: ${OUT}"
    exit 0
fi

if [[ "$STATUS" == "degraded" ]]; then
    REASON=$(printf '%s\n' "$OUT" | sed -nE 's/^  degraded: (.+)$/\1/p')
    # degraded では未測定分が残るため、部分和が閾値を超えていなくても "超えていない" とは
    # 言えない。超過が証明できたときだけ true、それ以外は false ではなく unknown を記録する。
    THRESHOLD_EXCEEDED=unknown
    printf '%s\n' "$REASON" | grep -q "exceeds threshold" && THRESHOLD_EXCEEDED=true
    status_end fail "total=${TOTAL} tokens, status=degraded (${REASON})" \
        "metric.total_tokens=${TOTAL}" \
        "metric.status=${STATUS}" \
        "metric.threshold_exceeded=${THRESHOLD_EXCEEDED}"
    exit 0
fi

status_end ok "total=${TOTAL} tokens, status=${STATUS}" \
    "metric.total_tokens=${TOTAL}" \
    "metric.status=${STATUS}"
