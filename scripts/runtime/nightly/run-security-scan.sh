#!/usr/bin/env bash
# run-security-scan.sh — AgentShield エージェント設定セキュリティ監査 (静的)
# cron: 45 23 * * *  (DOW=3 水曜、catch-up 6 days)
# Scope: ~/.claude/ のエージェント設定 (CLAUDE.md / hooks / skills / settings.json)。
# agentshield-filter.py が `npx ecc-agentshield scan` を実行し、deny ルール等の
# false positive を除去して再採点する (skill `/security-scan` の非対話版)。
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

# agentshield-filter.py の exit code: 0=clean / 1=critical findings あり (正常動作) / 2=実行・parse エラー
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
SUPPRESSED=$(jq -r '.suppressed' "$JSON_TMP")
FILES=$(jq -r '.summary.filesScanned' "$JSON_TMP")

{
    echo "# Security Scan (AgentShield) ${NIGHTLY_DATE}"
    echo ""
    echo "Scope: ${SCAN_TARGET/#$HOME/~} (CLAUDE.md / hooks / skills / settings.json)"
    echo ""
    echo "- Grade: **${GRADE}** (${SCORE}/100)"
    echo "- Findings: ${TOTAL} (critical=${CRIT} high=${HIGH})"
    echo "- Suppressed false positives: ${SUPPRESSED}"
    echo "- Files scanned: ${FILES}"
    echo ""
    echo "## Findings"
    jq -r '(.findings // []) | if length == 0 then "なし" else (.[] | "- [\(.severity | ascii_upcase)] \(.title) — \(.file)\(if .line then ":\(.line | tostring)" else "" end)") end' "$JSON_TMP"
} > "$REPORT_PATH"

DETAIL="grade=$GRADE score=$SCORE critical=$CRIT high=$HIGH suppressed=$SUPPRESSED"
TOP=$(jq -r '(.findings // []) | map(select(.severity == "critical" or .severity == "high")) | .[0:5][] | "[\(.severity | ascii_upcase)] \(.title) — \(.file)"' "$JSON_TMP" 2>/dev/null || true)
[[ -n "$TOP" ]] && DETAIL+=$'\n\nTop findings:\n'"$TOP"

status_end ok "grade=$GRADE score=$SCORE critical=$CRIT high=$HIGH" \
    "report=06-Nightly/${NIGHTLY_DATE}-security.md" \
    "metric.score=$SCORE" "metric.critical=$CRIT" "metric.high=$HIGH" \
    "detail=$DETAIL"
