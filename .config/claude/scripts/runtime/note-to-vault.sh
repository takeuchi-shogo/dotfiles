#!/usr/bin/env bash
# note-to-vault.sh — テキストを Obsidian Vault 00-Inbox/ に即時保存
set -euo pipefail

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
if [[ -z "$VAULT_PATH" ]]; then
    echo "[note] OBSIDIAN_VAULT_PATH not set" >&2
    exit 1
fi

TEXT="${1:-}"
if [[ -z "$TEXT" ]]; then
    echo "[note] Usage: note-to-vault.sh 'content'" >&2
    exit 1
fi

TARGET="$VAULT_PATH/00-Inbox"
mkdir -p "$TARGET"

TODAY="$(TZ=Asia/Tokyo date +%Y-%m-%d)"
TIMESTAMP="$(TZ=Asia/Tokyo date +%Y%m%d%H%M%S)"
DEST_FILE="$TARGET/note-${TIMESTAMP}.md"

{
    echo "---"
    echo "tags: [status/seed]"
    echo "created: \"$TODAY\""
    echo "---"
    echo ""
    echo "$TEXT"
} > "$DEST_FILE"

echo "$DEST_FILE"
