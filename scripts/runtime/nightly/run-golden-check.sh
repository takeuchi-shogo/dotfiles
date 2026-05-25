#!/usr/bin/env bash
# run-golden-check.sh — 夜間 golden principles 違反一覧生成
# cron: 15 23 * * * (内部 gate で DAILY 判定)
# Vault output: 06-Nightly/${DATE}-golden.md
#
# Template-establishing task: Task 6-10 の run-*.sh はこの形を踏襲する。
# Codex Gate 反映:
#   Q10 (C1): preflight (command -v jq curl claude) + TIMEOUT_BIN 解決
#   Q12 (FM-7): acquire/release claude_lock で 23:45 同時実行を回避
#   M3: report は mktemp に書いて成功時のみ atomic mv (partial write 防止)
#   H2: grep -c は `|| true` でラップ (no-match で `0\n0` 防止)
#   Q9: status_end が内部で mark_run_today を呼ぶ (fail でも mark、lib 側)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="golden-check"

# === Cleanup trap (lock release + status_end on unexpected exit) ===
_cleanup() {
    local ec=$?
    # status_end が既に呼ばれていれば _NIGHTLY_CURRENT_TASK は空
    if [[ -n "${_NIGHTLY_CURRENT_TASK:-}" ]]; then
        status_end fail "trapped exit_code=$ec"
    fi
    release_claude_lock
}
trap _cleanup EXIT

# === Prereq guards (Q10 / C1) ===
if [[ -z "${OBSIDIAN_VAULT_PATH:-}" ]]; then
    status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"
    exit 0
fi
for cmd in jq curl claude; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found in PATH"
        exit 0
    fi
done
TIMEOUT_BIN=$(command -v timeout 2>/dev/null || command -v gtimeout 2>/dev/null || true)
if [[ -z "$TIMEOUT_BIN" ]]; then
    status_begin "$TASK"; status_end fail "preflight: timeout/gtimeout not found (install coreutils)"
    exit 0
fi

# === Gate ===
should_run_today "$TASK" DAILY "" 0 || exit 0

status_begin "$TASK"

# === Acquire claude -p lock (Q12 / FM-7) ===
if ! acquire_claude_lock; then
    status_end fail "claude lock timeout (held by another nightly task)"
    exit 0
fi

# === Body ===
REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-golden.md"
# M3: atomic mv パターン — partial write 防止
REPORT_TMP=$(mktemp -t "nightly-golden-${NIGHTLY_DATE}.XXXXXX")
trap 'rm -f "$REPORT_TMP"; _cleanup' EXIT

PROMPT="$(cat <<'PROMPT_EOF'
あなたは golden principles 監査エージェントです。
dotfiles リポ (~/dotfiles) の以下のディレクトリを横断スキャンしてください:
  - .config/claude/agents/
  - .config/claude/skills/
  - .config/claude/hooks/
  - scripts/runtime/

検出対象 (golden principles):
  - "暗黙フォールバック" の残置 (silent skip / silent fallback / モック残置)
  - "silent failure" (catch して握り潰し、ログ無し)
  - NO-OP 実装 (空関数 + return success、コメントに「後で実装する」旨の注記がある等)
  - 既存パターン違反 (例: ハードコード path で symlink 機構を無視)

出力フォーマット (Markdown):
# Golden Check Report (YYYY-MM-DD)

## Summary
- 違反検出数: N 件
- 重要度内訳: critical=X, warning=Y, info=Z

## Findings
### F-1: <タイトル>
- 重要度: critical | warning | info
- ファイル: `path/to/file.sh:LINE`
- 内容: <violation の説明>
- 推奨対応: <fix の方向>

(以下 F-N まで)

## 違反 0 件なら "クリーン状態" と記載してください。
PROMPT_EOF
)"

STDERR_LOG=$(mktemp -t "nightly-golden-stderr.XXXXXX")
if ! "$TIMEOUT_BIN" 600s claude -p "$PROMPT" > "$REPORT_TMP" 2> "$STDERR_LOG"; then
    local_stderr_head=$(head -c 200 "$STDERR_LOG" 2>/dev/null || echo "")
    rm -f "$STDERR_LOG"
    status_end fail "claude -p failed or timeout, stderr: $local_stderr_head"
    exit 0
fi
rm -f "$STDERR_LOG"

# M3: 成功時のみ atomic mv
mv "$REPORT_TMP" "$REPORT_PATH"

# === Metric 抽出 (H2: grep -c は || true でラップ) ===
VIOLATIONS=$(grep -cE '^### F-' "$REPORT_PATH" 2>/dev/null || true)
VIOLATIONS="${VIOLATIONS:-0}"

status_end ok "violations=$VIOLATIONS" \
    "report=06-Nightly/${NIGHTLY_DATE}-golden.md" \
    "metric.violations=$VIOLATIONS"
