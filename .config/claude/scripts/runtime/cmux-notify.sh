#!/usr/bin/env bash
# cmux-notify.sh — Claude Code 通知を cmux ネイティブ通知に統合
# cmux 外では macOS 通知にフォールバック
#
# Usage: cmux-notify.sh <title> <body> [sound]
# sound: hero (完了), glass (入力待ち), default (その他)

set -euo pipefail

TITLE="${1:-Claude Code}"
BODY="${2:-}"
SOUND="${3:-default}"

# CMUX CLI resolver — allow-list 優先で PATH hijacking リスク軽減 (CWE-426)
# 優先順: $CMUX_CLI env → 絶対パス allow-list → command -v fallback
_resolve_cmux_cli() {
    if [[ -n "${CMUX_CLI:-}" ]]; then
        printf '%s\n' "$CMUX_CLI"
        return 0
    fi
    local c
    for c in \
        "/Applications/cmux.app/Contents/Resources/bin/cmux" \
        "/opt/homebrew/bin/cmux" \
        "/usr/local/bin/cmux"; do
        [[ -x "$c" ]] && { printf '%s\n' "$c"; return 0; }
    done
    command -v cmux 2>/dev/null || printf '%s\n' "/Applications/cmux.app/Contents/Resources/bin/cmux"
}
CMUX_CLI="$(_resolve_cmux_cli)"

# cmux 内で実行中かどうかを判定
if [[ -n "${CMUX_WORKSPACE_ID:-}" ]] && "$CMUX_CLI" ping &>/dev/null; then
    # cmux ネイティブ通知
    "$CMUX_CLI" notify --title "$TITLE" --body "$BODY" 2>/dev/null || true

    # claude-hook notification で sidebar にも反映
    "$CMUX_CLI" claude-hook notification 2>/dev/null || true
else
    # cmux 外: macOS 通知にフォールバック
    osascript -e "display notification \"$BODY\" with title \"$TITLE\"" 2>/dev/null || true
fi

# サウンド再生 (共通)
case "$SOUND" in
    hero)  afplay /System/Library/Sounds/Hero.aiff & ;;
    glass) afplay /System/Library/Sounds/Glass.aiff & ;;
    *)     ;;
esac
