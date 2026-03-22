#!/usr/bin/env bash
# sync-tacit-knowledge.sh — agent-memory/learnings/*.jsonl → Obsidian 04-Galaxy/
set -euo pipefail

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
if [[ -z "$VAULT_PATH" ]]; then
    echo "[sync-tacit] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

LEARNINGS_DIR="$HOME/.claude/agent-memory/learnings"
TARGET="$VAULT_PATH/04-Galaxy"
mkdir -p "$TARGET"

TODAY="$(TZ=Asia/Tokyo date +%Y-%m-%d)"
synced=0

for jsonl_file in "$LEARNINGS_DIR"/*.jsonl; do
    [[ -f "$jsonl_file" ]] || continue
    source_name="$(basename "$jsonl_file" .jsonl)"

    # Extract entries (--all: all entries, default: today only)
    date_filter="$TODAY"
    [[ "${1:-}" == "--all" ]] && date_filter=""
    while IFS= read -r entry; do
        [[ -z "$entry" ]] && continue

        # Generate hash for dedup
        hash=$(echo "$entry" | md5 -q 2>/dev/null || echo "$entry" | md5sum | cut -d' ' -f1)
        short_hash="${hash:0:8}"
        timestamp=$(echo "$entry" | jq -r '.timestamp // empty' 2>/dev/null)
        ts_prefix="${timestamp//[:-]/}"
        ts_prefix="${ts_prefix:0:14}"
        [[ -z "$ts_prefix" ]] && ts_prefix="$(date +%Y%m%d%H%M%S)"

        dest_file="$TARGET/${ts_prefix}-learning-${short_hash}.md"

        # Skip if already exists
        [[ -f "$dest_file" ]] && continue

        # Extract fields
        msg=$(echo "$entry" | jq -r '.message // .rule // .pattern // "no description"' 2>/dev/null)
        category=$(echo "$entry" | jq -r '.category // .type // "unknown"' 2>/dev/null)

        synced_at="$(TZ=Asia/Tokyo date +%Y-%m-%dT%H:%M:%S+09:00)"

        {
            echo "---"
            echo "created: \"$TODAY\""
            echo "tags:"
            echo "  - type/permanent"
            echo "  - agent/tacit-knowledge"
            echo "  - status/seed"
            echo "  - \"source/$source_name\""
            echo "source: \"$source_name\""
            echo "synced_at: $synced_at"
            echo "---"
            echo ""
            echo "# Learning: $category"
            echo ""
            echo "## 主張"
            echo ""
            echo "$msg"
            echo ""
            echo "## 詳細"
            echo ""
            echo '<!-- 自動抽出。必要に応じて編集 -->'
            echo ""
            echo "\`\`\`json"
            echo "$entry" | jq '.' 2>/dev/null || echo "$entry"
            echo "\`\`\`"
            echo ""
            echo "## 関連ノート"
            echo ""
            echo "- [[]] — 関連の理由"
        } > "$dest_file"

        synced=$((synced + 1))
    done < <(if [[ -n "$date_filter" ]]; then jq -c --arg date "$date_filter" 'select(.timestamp // "" | startswith($date))' "$jsonl_file" 2>/dev/null; else jq -c '.' "$jsonl_file" 2>/dev/null; fi)
done

if [[ $synced -gt 0 ]]; then
    echo "[sync-tacit] Synced $synced learning(s) to $TARGET"
fi
