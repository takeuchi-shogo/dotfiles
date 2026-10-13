#!/usr/bin/env bash
# run-security-scan.sh — AgentShield エージェント設定セキュリティ監査 (静的)
# cron: 45 23 * * *  (DOW=3 水曜、catch-up 6 days)
# Scope: ~/.claude/ のエージェント設定 (CLAUDE.md / hooks / skills / settings.json)。
#
# Logos / Horos 型のステージ形状（Cybozu Inside Out 概要編・ハーネス編で読めた範囲）:
#   1. product context     — 対象は agent config（製品アプリ SAST/DAST ではない）
#   2. split scans         — AgentShield のファイル走査 + 本スクリプトは週次1ジョブ
#   3. dedup / FP filter   — agentshield-filter.py（誤検出除去 + fingerprint dedup）
#   4. reproduction check  — critical/high/medium に半自動再現チェックリストを付与
#   5. feedback loop       — suppressed/deduped/reproductionPending をレポートに残す
#
# Caveat: Horos の PSIRT triage / DAST PoC 実行は移植していない。
#         本ジョブは AgentShield 静的スキャン + フィルタ/ステージメタデータの範囲。
#         旧 skill `/security-scan` の非対話版（skill 本体は 2026-09-24 退役、commands は残存）。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="security-scan"
DOTFILES_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
FILTER="${DOTFILES_DIR}/.config/claude/scripts/policy/agentshield-filter.py"
SCAN_TARGET="${SECURITY_SCAN_PATH:-$HOME/.claude}"

_cleanup() {
    local ec=$?
    if [[ -n "${_NIGHTLY_CURRENT_TASK:-}" ]]; then
        status_end fail "trapped exit_code=$ec"
    fi
}
trap _cleanup EXIT

if [[ -z "${OBSIDIAN_VAULT_PATH:-}" ]]; then
    status_begin "$TASK"; status_end fail "missing OBSIDIAN_VAULT_PATH"
    exit 0
fi
for cmd in jq python3 npx; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found"
        exit 0
    fi
done
if [[ ! -f "$FILTER" ]]; then
    status_begin "$TASK"; status_end fail "preflight: filter not found ($FILTER)"
    exit 0
fi

should_run_today "$TASK" DOW 3 6 || exit 0
status_begin "$TASK"

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-security.md"
JSON_TMP=$(mktemp -t "nightly-security-${NIGHTLY_DATE}.XXXXXX")
ERR_TMP="${JSON_TMP}.err"
trap 'rm -f "$JSON_TMP" "$ERR_TMP"; _cleanup' EXIT

# Stage 1–2: product context + scan (filter が AgentShield を起動)
# Stage 3–5: FP/dedup + reproduction staging + feedback fields in JSON
# agentshield-filter.py exit code: 0=clean / 1=critical findings あり (正常動作) / 2=実行・parse エラー
# → exit 1 を fail 扱いしない (critical 件数はレポート + metric に出す)。
SCAN_EC=0
python3 "$FILTER" --path "$SCAN_TARGET" --format json >"$JSON_TMP" 2>"$ERR_TMP" || SCAN_EC=$?
if [[ "$SCAN_EC" -ge 2 ]]; then
    status_end fail "agentshield error (ec=$SCAN_EC): $(head -c 200 "$ERR_TMP" 2>/dev/null | tr '\n' ' ')"
    exit 0
fi

# 出力検証 (silent failure 回避: grade が取れなければ異常として fail し握り潰さない)
GRADE=$(jq -re '.score.grade' "$JSON_TMP" 2>/dev/null) || {
    status_end fail "agentshield output has no .score.grade (ec=$SCAN_EC)"
    exit 0
}
SCORE=$(jq -r '.score.numericScore' "$JSON_TMP")
TOTAL=$(jq -r '.summary.totalFindings' "$JSON_TMP")
CRIT=$(jq -r '.summary.critical' "$JSON_TMP")
HIGH=$(jq -r '.summary.high' "$JSON_TMP")
SUPPRESSED=$(jq -r '.suppressed // 0' "$JSON_TMP")
DEDUPED=$(jq -r '.deduped // 0' "$JSON_TMP")
REPRO_PENDING=$(jq -r '.reproductionPending // 0' "$JSON_TMP")
FILES=$(jq -r '.summary.filesScanned' "$JSON_TMP")

{
    echo "# Security Scan (AgentShield) ${NIGHTLY_DATE}"
    echo ""
    echo "Scope: ${SCAN_TARGET/#$HOME/~} (CLAUDE.md / hooks / skills / settings.json)"
    echo ""
    echo "## Pipeline stages (Logos-shaped)"
    echo ""
    echo "1. product context — agent config only"
    echo "2. split/scan — AgentShield walk"
    echo "3. dedup + false-positive filter — suppressed=${SUPPRESSED}, deduped=${DEDUPED}"
    echo "4. reproduction check (semi-automated) — pending=${REPRO_PENDING}"
    echo "5. feedback — see Feedback section below"
    echo ""
    echo "- Grade: **${GRADE}** (${SCORE}/100)"
    echo "- Findings: ${TOTAL} (critical=${CRIT} high=${HIGH})"
    echo "- Suppressed false positives: ${SUPPRESSED}"
    echo "- Deduped duplicates: ${DEDUPED}"
    echo "- Reproduction pending: ${REPRO_PENDING}"
    echo "- Files scanned: ${FILES}"
    echo ""
    echo "## Findings"
    jq -r '(.findings // []) | if length == 0 then "なし" else (.[] | "- [\(.severity | ascii_upcase)] \(.title) — \(.file)\(if .line then ":\(.line | tostring)" else "" end)\(if (.reproduction.status // "") == "pending" then " _(repro pending)_" else "" end)") end' "$JSON_TMP"
    echo ""
    echo "## Reproduction checklist (semi-automated)"
    jq -r '
      (.findings // [])
      | map(select((.reproduction.status // "") == "pending"))
      | if length == 0 then "なし（pending なし）"
        else .[] |
          "### \(.title) (\(.severity)) — \(.file)\n" +
          ((.reproduction.checklist // []) | map("- [ ] \(.)") | join("\n"))
        end
    ' "$JSON_TMP"
    echo ""
    echo "## Feedback"
    echo ""
    echo "- Use suppressed/deduped counts next week to tune FP rules in agentshield-filter.py"
    echo "- Mark reproduction checklist items when human/agent verifies; keep proof one-liners in vault notes"
    jq -r '
      if .feedback then
        "- suppressedReasons: \(.feedback.suppressedReasons | tostring)\n- dedupedCount: \(.feedback.dedupedCount)\n- reproductionChecklistRemaining: \(.feedback.reproductionChecklistRemaining)"
      else empty end
    ' "$JSON_TMP"
} > "$REPORT_PATH"

DETAIL="grade=$GRADE score=$SCORE critical=$CRIT high=$HIGH suppressed=$SUPPRESSED deduped=$DEDUPED repro_pending=$REPRO_PENDING"
TOP=$(jq -r '(.findings // []) | map(select(.severity == "critical" or .severity == "high")) | .[0:5][] | "[\(.severity | ascii_upcase)] \(.title) — \(.file)"' "$JSON_TMP" 2>/dev/null || true)
[[ -n "$TOP" ]] && DETAIL+=$'\n\nTop findings:\n'"$TOP"

status_end ok "grade=$GRADE score=$SCORE critical=$CRIT high=$HIGH" \
    "report=06-Nightly/${NIGHTLY_DATE}-security.md" \
    "metric.score=$SCORE" "metric.critical=$CRIT" "metric.high=$HIGH" \
    "metric.deduped=$DEDUPED" "metric.repro_pending=$REPRO_PENDING" \
    "detail=$DETAIL"
