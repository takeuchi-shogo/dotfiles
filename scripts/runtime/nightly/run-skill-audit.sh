#!/usr/bin/env bash
# run-skill-audit.sh — skill health audit (静的)
# cron: 45 23 * * *  (DOW=4 木曜、catch-up 6 days)
#
# 2026-06-14: claude -p "/skill-audit" → codex 移行。
# /skill-audit skill は Claude 専用機構で codex からは呼べないため、skill が行う
# 静的 health audit (5D 品質スキャン / trigger 衝突検出 / usage tier / Keep-Improve-Retire 分類)
# を codex プロンプトとして再実装する。A/B runtime benchmark (Claude eval 実行が必要) は
# codex では実行不能なため意図的に対象外 (レポート冒頭にその旨を明記させる)。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="skill-audit"
DOTFILES_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SKILLS_DIR="${DOTFILES_DIR}/.config/claude/skills"
SKILL_EXEC_LOG="${HOME}/.claude/agent-memory/learnings/skill-executions.jsonl"

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
for cmd in jq codex; do
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

# skill health audit プロンプト (codex 再実装: /skill-audit の静的部分)
PROMPT="あなたは Claude Code の skill 定義を監査する health auditor です。
read-only でファイルを読み、Markdown レポートを 1 つ生成してください (ファイル編集は禁止)。

## 対象
- skill 定義: ${SKILLS_DIR}/*/SKILL.md (各 skill の frontmatter description と本文)
- 使用ログ: ${SKILL_EXEC_LOG} (JSON-lines。過去30日の skill 実行回数集計に使う。
  存在しない/データ不足なら usage 判定はスキップし、静的スキャンのみで判定する)

## スコープ (重要)
A/B runtime benchmark (Claude eval 実行) は codex では実行不能なため**対象外**です。
本監査は静的 health audit のみ。レポート冒頭にこの旨を 1 行明記してください。

## 監査項目
1. **5D 品質スキャン**: 各 skill を Safety / Completeness / Executability / Maintainability /
   Cost-awareness の 5 次元で Good/Average/Poor 判定。いずれか Poor なら Improve 分類。
2. **trigger 衝突検出**: description の Triggers が重複・曖昧で誤起動を招く skill ペアを検出。
   検出した各ペアは行頭に必ず 「[CONFLICT]」マーカーを付ける。
3. **usage tier**: 使用ログから Dominant(40%以上) / Weekly(4回+) / Monthly(1-3回) / Unused(0回) に分類。
   Unused の skill は Retire Candidates に列挙し、各行頭に必ず 「[DORMANT]」マーカーを付ける。
4. **Keep / Improve / Retire** に各 skill を分類。

## 出力フォーマット (Markdown)
重要: [CONFLICT] / [DORMANT] マーカーは該当する finding 行頭にのみ付け、見出しや Summary には付けない
(スクリプトがマーカー数で件数を集計するため)。

# Skill Audit Report (${NIGHTLY_DATE})

> 注記: A/B runtime benchmark は対象外 (codex 静的監査)。

## Summary
- 監査 skill 数: N
- Keep: X / Improve: Y / Retire candidates: Z
- trigger conflict pairs: C

## Conflicts
- [CONFLICT] <skillA> vs <skillB> — <理由>

## Retire Candidates
- [DORMANT] <skill>: 未使用 (0回) — <根拠>

## Improve
- <skill>: <Poor 次元と改善方向>

## Keep
- <skill> ...

衝突 0 件・retire 候補 0 件なら各セクションに 'なし' と記載してください
(マーカー行は出さない)。"

# codex exec (read-only 分析 → -o で REPORT_TMP に最終メッセージのみ書き出す)
if ! run_codex_report 900 "$REPORT_TMP" "$PROMPT"; then
    status_end fail "codex failed/timeout: $CODEX_ERR_HEAD"
    exit 0
fi

mv "$REPORT_TMP" "$REPORT_PATH"

# マーカー数で集計 (見出し/Summary の語句を誤カウントしない)
DORMANT=$(grep -cF '[DORMANT]' "$REPORT_PATH" 2>/dev/null || true)
CONFLICTS=$(grep -cF '[CONFLICT]' "$REPORT_PATH" 2>/dev/null || true)
DORMANT="${DORMANT:-0}"
CONFLICTS="${CONFLICTS:-0}"

# Discord 詳細: dormant / conflicts 該当行 top 5
DETAIL="dormant=$DORMANT conflicts=$CONFLICTS"
TOP_FINDINGS=$(grep -F -e '[DORMANT]' -e '[CONFLICT]' "$REPORT_PATH" 2>/dev/null | head -5 || true)
[[ -n "$TOP_FINDINGS" ]] && DETAIL+=$'\n\nTop findings:\n'"$TOP_FINDINGS"

status_end ok "dormant=$DORMANT conflicts=$CONFLICTS" \
    "report=06-Nightly/${NIGHTLY_DATE}-skill.md" \
    "metric.dormant=$DORMANT" "metric.conflicts=$CONFLICTS" \
    "detail=$DETAIL"
