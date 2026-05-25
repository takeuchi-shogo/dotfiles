#!/usr/bin/env bash
# run-health-check.sh — docs 鮮度 + コード乖離検出
# cron: 25 23 * * *  (DAILY gate)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="health-check"

_cleanup() {
    local ec=$?
    if [[ -n "${_NIGHTLY_CURRENT_TASK:-}" ]]; then
        status_end fail "trapped exit_code=$ec"
    fi
    release_claude_lock
}
trap _cleanup EXIT

# Prereq (Q10/C1)
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

should_run_today "$TASK" DAILY "" 0 || exit 0
status_begin "$TASK"

if ! acquire_claude_lock; then
    status_end fail "claude lock timeout"
    exit 0
fi

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-health.md"
REPORT_TMP=$(mktemp -t "nightly-health-${NIGHTLY_DATE}.XXXXXX")
trap 'rm -f "$REPORT_TMP"; _cleanup' EXIT

# 30 日以上更新なし docs を抽出
STALE_DOCS=$(find "$HOME/dotfiles/docs" "$HOME/dotfiles/.config/claude/references" -name "*.md" -mtime +30 2>/dev/null | head -20 || true)
STALE_COUNT=$(echo "${STALE_DOCS}" | grep -cE '^[^[:space:]]' 2>/dev/null || true)
STALE_COUNT="${STALE_COUNT:-0}"

PROMPT="$(cat <<PROMPT_EOF
あなたは docs 健全性監査エージェントです。

以下の stale docs リスト (30 日以上未更新):
\`\`\`
${STALE_DOCS:-(なし)}
\`\`\`

各 doc について:
1. 内容が code/設定の現状と乖離していないかチェック (git log で参照 commit 履歴を確認)
2. broken reference (存在しないファイルへのパス) がないか確認
3. 削除候補か更新候補かを判定

出力フォーマット (Markdown):
# Health Check Report (${NIGHTLY_DATE})

## Summary
- 監査対象: N 件
- 削除候補: X 件
- 更新候補: Y 件
- 健全: Z 件

## Findings
### <doc path>
- 判定: 削除 | 更新 | 健全
- 理由: <理由>
- 推奨アクション: <具体的 action>
PROMPT_EOF
)"

STDERR_LOG=$(mktemp -t "nightly-health-stderr.XXXXXX")
if ! "$TIMEOUT_BIN" 600s claude -p "$PROMPT" > "$REPORT_TMP" 2> "$STDERR_LOG"; then
    err_head=$(head -c 200 "$STDERR_LOG" 2>/dev/null || echo "")
    rm -f "$STDERR_LOG"
    status_end fail "claude -p failed/timeout, stderr: $err_head"
    exit 0
fi
rm -f "$STDERR_LOG"

mv "$REPORT_TMP" "$REPORT_PATH"

# H2 反映
TO_DELETE=$(grep -c '^- 判定: 削除' "$REPORT_PATH" 2>/dev/null || true)
TO_UPDATE=$(grep -c '^- 判定: 更新' "$REPORT_PATH" 2>/dev/null || true)
TO_DELETE="${TO_DELETE:-0}"
TO_UPDATE="${TO_UPDATE:-0}"

status_end ok "stale=$STALE_COUNT to_delete=$TO_DELETE to_update=$TO_UPDATE" \
    "report=06-Nightly/${NIGHTLY_DATE}-health.md" \
    "metric.stale=$STALE_COUNT" "metric.to_delete=$TO_DELETE" "metric.to_update=$TO_UPDATE"
