#!/usr/bin/env bash
# run-audit.sh — コードベース横断品質監査 (sec/arch/perf/quality)
# cron: 45 23 * * *  (DOW=1 月曜、catch-up 6 days)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="audit"

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

should_run_today "$TASK" DOW 1 6 || exit 0
status_begin "$TASK"

if ! acquire_claude_lock; then
    status_end fail "claude lock timeout"
    exit 0
fi

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-audit.md"
REPORT_TMP=$(mktemp -t "nightly-audit-${NIGHTLY_DATE}.XXXXXX")
trap 'rm -f "$REPORT_TMP"; _cleanup' EXIT

PROMPT="$(cat <<'PROMPT_EOF'
あなたは /audit skill 相当のコードベース品質監査エージェントです。

監査対象: ~/dotfiles リポ (excluding .worktrees, .git, node_modules)
監査軸:
  1. Security: secret hardcode / unsafe eval / shell injection
  2. Architecture: 関心分離違反 / 循環依存 / God script (>500行)
  3. Performance: 不要な O(N²) / 同期 I/O ループ
  4. Test coverage: 重要 logic に test なし
  5. Code quality: 重複コード / dead code / 命名規約違反

出力フォーマット (優先度付き Markdown):
# Audit Report (YYYY-MM-DD)

## Executive Summary
- Total issues: N
- Critical: X, High: Y, Medium: Z, Low: W

## Critical Issues
### A-1: <タイトル>
- ファイル: `path:line`
- 軸: security/architecture/performance/test/quality
- 内容: <詳細>
- 推奨対応: <具体的 fix>

(以下 High, Medium, Low の順に羅列)

## QUESTIONS (Answer 欄付き、人手で埋める)
### Q-1: <非自明な設計判断について>
- 背景: ...
- 選択肢: ...
- Answer: (未回答)
PROMPT_EOF
)"

STDERR_LOG=$(mktemp -t "nightly-audit-stderr.XXXXXX")
if ! "$TIMEOUT_BIN" 1200s claude -p "$PROMPT" --model "${NIGHTLY_CLAUDE_MODEL:-claude-sonnet-4-6}" > "$REPORT_TMP" 2> "$STDERR_LOG"; then
    err_head=$(head -c 200 "$STDERR_LOG" 2>/dev/null || echo "")
    rm -f "$STDERR_LOG"
    status_end fail "claude -p failed/timeout, stderr: $err_head"
    exit 0
fi
rm -f "$STDERR_LOG"

mv "$REPORT_TMP" "$REPORT_PATH"

TOTAL=$(grep -cE '^### A-[0-9]+' "$REPORT_PATH" 2>/dev/null || true)
QUESTIONS=$(grep -cE '^### Q-[0-9]+' "$REPORT_PATH" 2>/dev/null || true)
TOTAL="${TOTAL:-0}"
QUESTIONS="${QUESTIONS:-0}"

# Discord 詳細: issue タイトル top 5
DETAIL="total=$TOTAL questions=$QUESTIONS"
TOP_ISSUES=$(grep -E '^### A-[0-9]+' "$REPORT_PATH" 2>/dev/null | head -5 || true)
[[ -n "$TOP_ISSUES" ]] && DETAIL+=$'\n\nTop issues:\n'"$TOP_ISSUES"

status_end ok "total=$TOTAL q=$QUESTIONS" \
    "report=06-Nightly/${NIGHTLY_DATE}-audit.md" \
    "metric.total=$TOTAL" "metric.questions=$QUESTIONS" \
    "detail=$DETAIL"
