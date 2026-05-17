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

CMUX_CLI="${CMUX_CLI:-$(command -v cmux 2>/dev/null || echo /Applications/cmux.app/Contents/Resources/bin/cmux)}"

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
