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

# CMUX CLI resolver (CWE-426/427). Inline exempt: lib/ にアクセス不可な path 構造のため
# scripts/lib/cmux_resolver.sh と同期して inline 維持。変更時は両方更新すること。
# 失敗時は CMUX_CLI="" で osascript fallback に流す。
_resolve_cmux_cli() {
    if [[ -n "${CMUX_CLI:-}" ]]; then
        if [[ "$CMUX_CLI" = /* ]] \
           && [[ -x "$CMUX_CLI" ]] \
           && [[ ! -d "$CMUX_CLI" ]] \
           && [[ ! -L "$CMUX_CLI" ]]; then
            printf '%s\n' "$CMUX_CLI"
            return 0
        fi
        return 1
    fi
    local c
    for c in \
        "/Applications/cmux.app/Contents/Resources/bin/cmux" \
        "/opt/homebrew/bin/cmux" \
        "/usr/local/bin/cmux"; do
        if [[ -x "$c" ]] && [[ ! -d "$c" ]] && [[ ! -L "$c" ]]; then
            printf '%s\n' "$c"
            return 0
        fi
    done
    return 1
}
CMUX_CLI="$(_resolve_cmux_cli 2>/dev/null)" || CMUX_CLI=""

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
