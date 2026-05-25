#!/usr/bin/env bash
# run-dep-audit.sh — 依存パッケージ脆弱性 + outdated 監査
# cron: 30 22 * * *  (Q11/C4 反映: dep-audit を前夜枠 22:30 に移動、morning-briefing は前日 JSONL を読むため)
# Scope: dotfiles root + tools サブディレクトリ (Q3/C2 反映: tools/claude-hooks/Cargo.toml + tools/otel-session-analyzer/go.mod 含む)
# Gate: DOM=1 月初、catch-up 7 days
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./lib/nightly-status.sh
source "${SCRIPT_DIR}/lib/nightly-status.sh"

TASK="dep-audit"

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
for cmd in jq; do
    if ! command -v "$cmd" &>/dev/null; then
        status_begin "$TASK"; status_end fail "preflight: $cmd CLI not found"
        exit 0
    fi
done

should_run_today "$TASK" DOM 1 7 || exit 0
status_begin "$TASK"

REPORT_DIR="${OBSIDIAN_VAULT_PATH}/06-Nightly"
mkdir -p "$REPORT_DIR"
REPORT_PATH="${REPORT_DIR}/${NIGHTLY_DATE}-dep.md"
REPORT_TMP=$(mktemp -t "nightly-dep-${NIGHTLY_DATE}.XXXXXX")
trap 'rm -f "$REPORT_TMP"; _cleanup' EXIT

DOTFILES_ROOT="${DOTFILES_ROOT_OVERRIDE:-$HOME/dotfiles}"

# Q3/C2: 動的検出 (root + tools/ サブディレクトリ)
# `find -maxdepth 3` で深すぎないように制限、node_modules / .git / worktrees は除外
MANIFESTS=$(find "$DOTFILES_ROOT" -maxdepth 3 \
    \( -name node_modules -o -name .git -o -name worktrees -o -name .worktrees \) -prune \
    -o \( -name "Cargo.toml" -o -name "go.mod" -o -name "package.json" -o -name "pyproject.toml" \) -print 2>/dev/null | sort -u)

{
    echo "# Dependency Audit ${NIGHTLY_DATE}"
    echo ""
    echo "Scope: ${DOTFILES_ROOT} (root + tools/ サブディレクトリ、動的検出)"
    echo ""
    echo "Detected manifests:"
    echo '```'
    echo "${MANIFESTS:-(none)}"
    echo '```'
    echo ""

    # Per-manifest audit
    while IFS= read -r manifest; do
        [[ -z "$manifest" ]] && continue
        local_dir=$(dirname "$manifest")
        local_basename=$(basename "$manifest")
        rel="${local_dir/#$HOME/~}"
        echo "## $local_basename @ $rel"
        echo '```'
        case "$local_basename" in
            package.json)
                if command -v npm &>/dev/null; then
                    (cd "$local_dir" && npm audit --json 2>/dev/null || true) | \
                        jq -r '"vulnerabilities: \(.metadata.vulnerabilities // {})"' 2>/dev/null || echo "(npm audit json parse failed)"
                    (cd "$local_dir" && npm outdated 2>/dev/null || true)
                else
                    echo "(npm CLI not found)"
                fi
                ;;
            pyproject.toml)
                if command -v pip-audit &>/dev/null; then
                    (cd "$local_dir" && pip-audit 2>&1 || true)
                else
                    echo "(pip-audit not installed)"
                fi
                ;;
            go.mod)
                if command -v govulncheck &>/dev/null; then
                    (cd "$local_dir" && govulncheck ./... 2>&1 || true)
                else
                    echo "(govulncheck not installed)"
                fi
                ;;
            Cargo.toml)
                if command -v cargo-audit &>/dev/null || cargo audit --version &>/dev/null 2>&1; then
                    (cd "$local_dir" && cargo audit 2>&1 || true)
                else
                    echo "(cargo-audit not installed)"
                fi
                ;;
        esac
        echo '```'
        echo ""
    done <<< "$MANIFESTS"
} > "$REPORT_TMP"

mv "$REPORT_TMP" "$REPORT_PATH"

# Metric: 脆弱性数の近似 (各 audit CLI の出力から抽出)
VULN_LINES=$(grep -ciE 'vulnerab|critical|high' "$REPORT_PATH" 2>/dev/null || true)
MANIFEST_COUNT=$(echo "$MANIFESTS" | grep -cE '^[^[:space:]]' 2>/dev/null || true)
VULN_LINES="${VULN_LINES:-0}"
MANIFEST_COUNT="${MANIFEST_COUNT:-0}"

status_end ok "manifests=$MANIFEST_COUNT vuln_lines=$VULN_LINES" \
    "report=06-Nightly/${NIGHTLY_DATE}-dep.md" \
    "metric.manifests=$MANIFEST_COUNT" "metric.vuln_lines=$VULN_LINES"
