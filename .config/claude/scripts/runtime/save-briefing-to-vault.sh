#!/usr/bin/env bash
set -euo pipefail

# save-briefing-to-vault.sh
# PostToolUse hook for Skill: /morning 実行時にブリーフィングを Vault に保存
# stdin: PostToolUse JSON payload

VAULT="${OBSIDIAN_VAULT_PATH:-}"
[[ -z "$VAULT" ]] && exit 0

# skill 名を確認
SKILL=$(jq -r '.tool_input.skill // empty' 2>/dev/null)
[[ "$SKILL" != "morning" ]] && exit 0

# auto-morning-briefing.sh をバックグラウンドで実行
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OBSIDIAN_VAULT_PATH="$VAULT" "$SCRIPT_DIR/auto-morning-briefing.sh" >> /tmp/morning-briefing.log 2>&1 &

echo '{"suppressOutput":true}'
