#!/usr/bin/env bash
# sync-daily-report.sh — ~/daily-reports/*.md → Obsidian Vault 07-Daily/
set -euo pipefail

VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
if [[ -z "$VAULT_PATH" ]]; then
    echo "[sync-daily] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

SOURCE_DIR="$HOME/daily-reports"
TARGET="$VAULT_PATH/07-Daily"

[[ -d "$SOURCE_DIR" ]] || { echo "[sync-daily] No daily-reports dir, skipping" >&2; exit 0; }
mkdir -p "$TARGET"

synced=0

for src_file in "$SOURCE_DIR"/*.md; do
    [[ -f "$src_file" ]] || continue
    filename="$(basename "$src_file")"
    dest_file="$TARGET/$filename"

    # Skip if already synced and source hasn't changed
    if [[ -f "$dest_file" ]] && [[ ! "$src_file" -nt "$dest_file" ]]; then
        continue
    fi

    synced_at="$(TZ=Asia/Tokyo date +%Y-%m-%dT%H:%M:%S+09:00)"

    # Check if source has frontmatter
    if head -1 "$src_file" | grep -q "^---"; then
        awk -v ts="$synced_at" '
            BEGIN { fence=0 }
            /^---$/ { fence++
                if (fence == 2) {
                    print "obsidian_tags: [agent/daily-report]"
                    print "synced_at: " ts
                }
            }
            { print }
        ' "$src_file" > "$dest_file"
    else
        {
            echo "---"
            echo "obsidian_tags: [agent/daily-report]"
            echo "synced_at: $synced_at"
            echo "---"
            echo ""
            cat "$src_file"
        } > "$dest_file"
    fi

    synced=$((synced + 1))
done

if [[ $synced -gt 0 ]]; then
    echo "[sync-daily] Synced $synced file(s) to $TARGET"
fi
