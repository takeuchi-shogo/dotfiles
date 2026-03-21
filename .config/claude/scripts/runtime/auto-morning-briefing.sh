#!/usr/bin/env bash
# auto-morning-briefing.sh — 朝の自動ブリーフィング生成
#
# cron + claude -p で朝のブリーフィングを自動生成し、
# Obsidian Daily Note に書き込み + cmux notify で通知する。
#
# Usage: auto-morning-briefing.sh
# Env:
#   OBSIDIAN_VAULT_PATH (optional) — 設定時は Daily Note に書き込み
#   GITHUB_USERNAME      (optional) — gh CLI のデフォルトユーザー
#
# cron example: 30 8 * * 1-5 /path/to/auto-morning-briefing.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NOTIFY="$SCRIPT_DIR/cmux-notify.sh"
DATE="$(date +%Y-%m-%d)"
VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
DAILY_NOTE_DIR="01-Projects/Daily"

# --- Preflight ---
if ! command -v claude &>/dev/null; then
    echo "[morning-briefing] claude CLI not found, skipping" >&2
    exit 1
fi

if ! command -v gh &>/dev/null; then
    echo "[morning-briefing] gh CLI not found, skipping" >&2
    exit 1
fi

# --- Gather context (lightweight, no claude call yet) ---
context=""

# GitHub Issues assigned to me
issues=$(gh issue list --assignee "@me" --state open \
    --json number,title,labels --limit 15 2>/dev/null || echo "[]")
context+="## Assigned Issues
$issues

"

# Open PRs by me
my_prs=$(gh pr list --author "@me" --state open \
    --json number,title,reviewDecision --limit 10 2>/dev/null || echo "[]")
context+="## My Open PRs
$my_prs

"

# Review requests for me
review_prs=$(gh pr list --search "review-requested:@me" --state open \
    --json number,title,author,createdAt --limit 10 2>/dev/null || echo "[]")
context+="## Review Requests
$review_prs

"

# Recent commits (yesterday)
recent_commits=$(git -C "$HOME/dotfiles" log --oneline --since="yesterday" \
    --no-merges 2>/dev/null | head -10 || echo "(none)")
context+="## Yesterday's Commits
$recent_commits
"

# --- Generate briefing via claude -p ---
prompt="You are a morning briefing assistant. Based on the following GitHub data, generate a concise Japanese morning briefing for today ($DATE).

Rules:
- Prioritize: In-progress tasks > Review requests > New tasks
- Limit new task suggestions to 2-3
- Flag any CI failures or approaching deadlines
- Format as clean Markdown with checkboxes
- Keep it under 30 lines
- Output in Japanese

Data:
$context"

briefing=$(claude -p "$prompt" --output-format text 2>/dev/null) || {
    echo "[morning-briefing] claude -p failed" >&2
    exit 1
}

# --- Output to Daily Note (if Vault exists) ---
if [[ -n "$VAULT_PATH" ]] && [[ -d "$VAULT_PATH" ]]; then
    daily_dir="$VAULT_PATH/$DAILY_NOTE_DIR"
    mkdir -p "$daily_dir"
    daily_note="$daily_dir/$DATE.md"

    if [[ -f "$daily_note" ]]; then
        # Append to existing daily note
        {
            echo ""
            echo "---"
            echo "## Morning Briefing (auto-generated)"
            echo ""
            echo "$briefing"
        } >> "$daily_note"
    else
        # Create new daily note
        {
            echo "---"
            echo "date: $DATE"
            echo "tags: [daily]"
            echo "---"
            echo ""
            echo "# $DATE"
            echo ""
            echo "## Morning Briefing (auto-generated)"
            echo ""
            echo "$briefing"
        } > "$daily_note"
    fi
    echo "[morning-briefing] Written to $daily_note"
fi

# --- Notify via cmux ---
if [[ -x "$NOTIFY" ]]; then
    "$NOTIFY" "Morning Briefing" "Today's plan is ready" hero
fi

# --- Also print to stdout (for cron mail / logs) ---
echo "$briefing"
