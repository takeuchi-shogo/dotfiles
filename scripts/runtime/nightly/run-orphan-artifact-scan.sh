#!/usr/bin/env bash
# run-orphan-artifact-scan.sh — stale worktree / merged・gone ブランチの inventory scan
# cadence: 週次・火曜 (DOW 2 gate, catch-up 6d)
# read-only。候補件数を metric として status JSONL に記録するのみで、削除は
# 人間がレビュー後に手動で行う (詳細は scripts/lifecycle/orphan-artifact-scan.sh を直接実行)。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="orphan-artifact-scan"
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
for cmd in git; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found in PATH"
        exit 0
    fi
done

# === Gate ===
should_run_today "$TASK" DOW 2 6 || exit 0

status_begin "$TASK"

cd "$REPO"

# gone 判定は remote-tracking ref の prune 後にしか立たないため best effort で prune。
# launchd 環境では credential 不在で失敗しうる — 失敗しても scan は age/merged で継続。
git fetch --prune --quiet origin 2>/dev/null || true

OUT=$(bash scripts/lifecycle/orphan-artifact-scan.sh 2>&1) || {
    status_end fail "scan exit non-zero: ${OUT}"
    exit 0
}

# scanner の最終行 "candidates: N" から件数を抽出 (metric 用)
COUNT=$(printf '%s' "$OUT" | sed -nE 's/^candidates: ([0-9]+)$/\1/p')
COUNT="${COUNT:-0}"

status_end ok "scan complete" "metric.candidates=${COUNT}"
