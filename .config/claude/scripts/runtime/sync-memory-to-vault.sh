#!/usr/bin/env bash
# sync-memory-to-vault.sh — Claude Code memory -> Obsidian Vault one-way sync
#
# Claude Code のメモリファイルを Obsidian Vault に同期する。
# frontmatter に Obsidian 互換タグを付与し、Vault 内で検索・リンク可能にする。
#
# Usage: sync-memory-to-vault.sh [--dry-run]
# Env:   OBSIDIAN_VAULT_PATH (required)
#
# cron example: */30 * * * * /path/to/sync-memory-to-vault.sh

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# --- Config ---
VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
DEST_DIR="07-Agent-Memory"
MEMORY_SOURCES=(
    "$HOME/.claude/projects/-Users-takeuchishougo-dotfiles/memory"
)

# --- Validation ---
if [[ -z "$VAULT_PATH" ]]; then
    echo "[sync-memory] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

if [[ ! -d "$VAULT_PATH" ]]; then
    echo "[sync-memory] Vault not found: $VAULT_PATH" >&2
    exit 1
fi

TARGET="$VAULT_PATH/$DEST_DIR"
mkdir -p "$TARGET"

synced=0

for src_dir in "${MEMORY_SOURCES[@]}"; do
    [[ -d "$src_dir" ]] || continue

    # MEMORY.md (index) is skipped - it's an index, not a note
    for src_file in "$src_dir"/*.md; do
        [[ -f "$src_file" ]] || continue
        filename="$(basename "$src_file")"
        [[ "$filename" == "MEMORY.md" ]] && continue

        dest_file="$TARGET/$filename"

        # Skip if source hasn't changed (compare mtime)
        if [[ -f "$dest_file" ]] && [[ ! "$src_file" -nt "$dest_file" ]]; then
            continue
        fi

        if $DRY_RUN; then
            echo "[dry-run] would sync: $filename"
            synced=$((synced + 1))
            continue
        fi

        # Read existing frontmatter type from source
        mem_type=""
        if head -1 "$src_file" | grep -q "^---"; then
            mem_type=$(awk '/^---$/{n++; next} n==1 && /^type:/{gsub(/^type: */, ""); print; exit}' "$src_file")
        fi

        # Build Obsidian-compatible tags
        tags="agent-memory"
        [[ -n "$mem_type" ]] && tags="$tags, $mem_type"

        synced_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

        # Check if source already has frontmatter
        if head -1 "$src_file" | grep -q "^---"; then
            # Insert obsidian_tags before closing --- of frontmatter
            awk -v tags="$tags" -v ts="$synced_at" '
                BEGIN { fence=0 }
                /^---$/ { fence++
                    if (fence == 2) {
                        print "obsidian_tags: [" tags "]"
                        print "synced_at: " ts
                    }
                }
                { print }
            ' "$src_file" > "$dest_file"
        else
            # Wrap with new frontmatter
            {
                echo "---"
                echo "obsidian_tags: [$tags]"
                echo "synced_at: $synced_at"
                echo "---"
                echo ""
                cat "$src_file"
            } > "$dest_file"
        fi

        synced=$((synced + 1))
    done
done

if [[ $synced -gt 0 ]]; then
    echo "[sync-memory] Synced $synced file(s) to $TARGET"
fi
