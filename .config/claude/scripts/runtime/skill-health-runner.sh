#!/usr/bin/env bash
# LaunchAgent から呼ばれるラッパー。各 script は内部で idempotent gate を持つ。
# ログイン毎に発火、cron との二重起動でもレポートは 1 日 1 つしか作られない。

set -uo pipefail

# One-shot migration (idempotent): Inbox/ → 00-Inbox/
INBOX_OLD="$HOME/Documents/Obsidian Vault/Inbox"
INBOX_NEW="$HOME/Documents/Obsidian Vault/00-Inbox"
if [ -d "$INBOX_OLD" ]; then
  mkdir -p "$INBOX_NEW"
  find "$INBOX_OLD" -mindepth 1 -maxdepth 1 -exec mv {} "$INBOX_NEW"/ \; 2>/dev/null
  rmdir "$INBOX_OLD" 2>/dev/null || true
fi

bash "$HOME/.claude/scripts/runtime/probation-30day.sh" || true
bash "$HOME/.claude/scripts/runtime/skill-usage-weekly.sh" || true
bash "$HOME/.claude/scripts/runtime/skill-count-alert.sh" || true
bash "$HOME/.claude/scripts/runtime/tmp-plans-cleanup.sh" || true
