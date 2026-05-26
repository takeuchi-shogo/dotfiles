#!/usr/bin/env bash
# run-daily-report.sh — 今日の活動サマリ (Claude sessions + Obsidian + git + friction)
# cron: 35 23 * * *  (DAILY gate)
# Sources:
#   - ~/.claude/projects/*/[uuid].jsonl (今日 modified)
#   - ${VAULT}/**/*.md (今日 modified、06-Nightly 除外)
#   - ${VAULT}/05-Literature/*.md (今日 新規 = 読んだ記事)
#   - git log --since=midnight (dotfiles)
#   - friction-events.jsonl 今日分
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="daily-report"

_cleanup() {
    local ec=$?
    if [[ -n "${_NIGHTLY_CURRENT_TASK:-}" ]]; then
        status_end fail "trapped exit_code=$ec"
    fi
    release_claude_lock
}
trap _cleanup EXIT

# Prereq
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
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-daily.md"
REPORT_TMP=$(mktemp -t "nightly-daily-${NIGHTLY_DATE}.XXXXXX")
trap 'rm -f "$REPORT_TMP"; _cleanup' EXIT

# === Source data 収集 ===

# Claude sessions today (今日 mtime)
SESSION_LIST=$(find "$HOME/.claude/projects" -name "*.jsonl" -mtime -1 2>/dev/null | head -20 || true)
SESSION_COUNT=$(echo "${SESSION_LIST}" | grep -cE '\.jsonl$' || true)
SESSION_COUNT="${SESSION_COUNT:-0}"

# セッション最初の user 発話 抽出 (最大 10 件 × 各 100 char)
SESSION_TOPICS=""
if [[ -n "$SESSION_LIST" ]]; then
    SESSION_TOPICS=$(echo "$SESSION_LIST" | head -10 | while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        topic=$(jq -r 'select(.type == "user") | (.message.content // "") | if type == "array" then .[0].text else . end | tostring | .[0:120]' "$f" 2>/dev/null | grep -v '^null$' | grep -v '^$' | head -1)
        [[ -n "$topic" ]] && echo "- $topic"
    done | head -10)
fi

# Vault 変更 (06-Nightly 除外)
VAULT_CHANGED=$(find "$OBSIDIAN_VAULT_PATH" -name "*.md" -mtime -1 \
    -not -path "*06-Nightly*" 2>/dev/null | head -30 || true)
VAULT_COUNT=$(echo "$VAULT_CHANGED" | grep -cE '\.md$' || true)
VAULT_COUNT="${VAULT_COUNT:-0}"

# Literature 新規 (読んだ記事)
LIT_NEW=$(find "$OBSIDIAN_VAULT_PATH/05-Literature" -name "*.md" -mtime -1 2>/dev/null | head -10 || true)
LIT_COUNT=$(echo "$LIT_NEW" | grep -cE '\.md$' || true)
LIT_COUNT="${LIT_COUNT:-0}"

# Git commits (dotfiles only for v1; multi-repo は v2)
GIT_COMMITS=$(cd "$HOME/dotfiles" && git log --since=midnight --oneline 2>/dev/null | head -20 || true)
GIT_COUNT=$(echo "$GIT_COMMITS" | grep -cE '^[0-9a-f]' || true)
GIT_COUNT="${GIT_COUNT:-0}"

# Friction events today
FRICTION_LOG="$HOME/.claude/agent-memory/learnings/friction-events.jsonl"
FRICTION_TODAY=""
if [[ -f "$FRICTION_LOG" ]]; then
    FRICTION_TODAY=$(jq -Rr "fromjson? | select(.timestamp >= \"${NIGHTLY_DATE}T00:00:00Z\") | .friction_class // .type // \"unknown\"" \
        "$FRICTION_LOG" 2>/dev/null | sort | uniq -c | sort -rn | head -5 || true)
fi

# === Prompt 構築 ===
PROMPT="$(cat <<PROMPT_EOF
あなたは今日 (${NIGHTLY_DATE}) の活動を要約する Daily Report エージェントです。

# 今日のデータ

## Claude Code セッション
- 件数: ${SESSION_COUNT}
- セッション最初の発話 (top 10):
\`\`\`
${SESSION_TOPICS:-(なし)}
\`\`\`

## Obsidian Vault 変更
- 変更ファイル数: ${VAULT_COUNT} (06-Nightly 除外)
- ファイル一覧 (top 30):
\`\`\`
${VAULT_CHANGED:-(なし)}
\`\`\`

## 新規 Literature (読んだ記事)
- 件数: ${LIT_COUNT}
- ファイル:
\`\`\`
${LIT_NEW:-(なし)}
\`\`\`

## Git コミット (dotfiles)
- 件数: ${GIT_COUNT}
- コミット:
\`\`\`
${GIT_COMMITS:-(なし)}
\`\`\`

## Friction events 今日分
\`\`\`
${FRICTION_TODAY:-(なし)}
\`\`\`

# 出力フォーマット (Markdown、20-40 行で簡潔に)

# Daily Report (${NIGHTLY_DATE})

## 主要トピック
- (sessions の話題 + git commits から 2-4 個推測)

## 取り組み
- **セッション**: ${SESSION_COUNT} 件 — (主な内容を要約)
- **Obsidian**: ${VAULT_COUNT} 件更新 — (カテゴリ分布)
- **読んだ記事**: ${LIT_COUNT} 件 — (タイトル抜粋)
- **コミット**: ${GIT_COUNT} 件 — (主な変更)

## 気づき / Friction
- (friction events と sessions から 1-3 個)

## 明日へ持ち越し
- (進行中の話題、未解決の問いから 1-3 個、なければ「特になし」)
PROMPT_EOF
)"

STDERR_LOG=$(mktemp -t "nightly-daily-stderr.XXXXXX")
if ! "$TIMEOUT_BIN" 600s claude -p "$PROMPT" > "$REPORT_TMP" 2> "$STDERR_LOG"; then
    err_head=$(head -c 200 "$STDERR_LOG" 2>/dev/null || echo "")
    rm -f "$STDERR_LOG"
    status_end fail "claude -p failed/timeout, stderr: $err_head"
    exit 0
fi
rm -f "$STDERR_LOG"

mv "$REPORT_TMP" "$REPORT_PATH"

# Discord 詳細: report の主要トピック+取り組み section (head 15 行)
DETAIL=$(head -15 "$REPORT_PATH" 2>/dev/null || echo "")

status_end ok "sessions=$SESSION_COUNT vault=$VAULT_COUNT lit=$LIT_COUNT git=$GIT_COUNT" \
    "report=06-Nightly/${NIGHTLY_DATE}-daily.md" \
    "metric.sessions=$SESSION_COUNT" "metric.vault=$VAULT_COUNT" "metric.lit=$LIT_COUNT" "metric.git=$GIT_COUNT" \
    "detail=$DETAIL"
