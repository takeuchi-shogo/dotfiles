#!/usr/bin/env bash
# sync-session-insights.sh — セッション JSONL → Obsidian Vault 00-Inbox/
set -euo pipefail

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
if [[ -z "$VAULT_PATH" ]]; then
    echo "[sync-insights] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

TARGET="$VAULT_PATH/00-Inbox"
mkdir -p "$TARGET"

TODAY="$(TZ=Asia/Tokyo date +%Y-%m-%d)"
DEST_FILE="$TARGET/insight-${TODAY}.md"

# Idempotent: skip if already generated today
if [[ -f "$DEST_FILE" ]]; then
    exit 0
fi

# Collect today's sessions from all projects
sessions=""
for index_file in "$HOME"/.claude/projects/*/sessions-index.json; do
    [[ -f "$index_file" ]] || continue
    result=$(jq -c --arg date "$TODAY" '
        .entries[]
        | select(
            (.created // "" | startswith($date)) or
            (.modified // "" | startswith($date))
        )
        | {sessionId, firstPrompt, summary, projectPath, fullPath}
    ' "$index_file" 2>/dev/null) || continue
    [[ -n "$result" ]] && sessions+="$result"$'\n'
done

# No sessions today
if [[ -z "${sessions:-}" ]]; then
    exit 0
fi

synced_at="$(TZ=Asia/Tokyo date +%Y-%m-%dT%H:%M:%S+09:00)"

# Build the insight note
{
    echo "---"
    echo "tags: [agent/session-insight, status/seed]"
    echo "created: $TODAY"
    echo "synced_at: $synced_at"
    echo "---"
    echo ""
    echo "# Session Insights - $TODAY"
    echo ""

    # Process each session
    echo "$sessions" | jq -rs '
        group_by(.projectPath)[]
        | "## " + (.[0].projectPath | split("/") | last) + "\n" +
          ([.[] | "- **" + (.firstPrompt // "no prompt" | .[0:100]) + "**\n  " + (.summary // "no summary" | .[0:200])] | join("\n"))
    ' 2>/dev/null || echo "(sessions could not be parsed)"

} > "$DEST_FILE"

echo "[sync-insights] Generated $DEST_FILE"
