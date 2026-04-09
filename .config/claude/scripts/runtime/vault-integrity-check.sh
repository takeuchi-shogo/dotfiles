#!/usr/bin/env bash
# vault-integrity-check.sh — Vault ↔ dotfiles memory bidirectional integrity check
#
# dotfiles の memory ファイルと Obsidian Vault の 08-Agent-Memory/ を比較し、
# 不整合（Vault-only, Vault-newer, dotfiles-only）を検知・修正する。
#
# Usage: vault-integrity-check.sh [--fix | --dry-run]
#   --dry-run  チェックのみ（デフォルト）
#   --fix      不整合を自動修正（Vault → dotfiles の逆同期）
# Env:   OBSIDIAN_VAULT_PATH (required)
#
# cron example: 0 * * * * /path/to/vault-integrity-check.sh

set -euo pipefail

FIX=false
DRY_RUN=true
for arg in "${@}"; do
    case "$arg" in
        --fix)     FIX=true; DRY_RUN=false ;;
        --dry-run) DRY_RUN=true ;;
    esac
done

# --- Config ---
VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
DEST_DIR="08-Agent-Memory"
MEMORY_SOURCES=("$HOME/.claude/projects"/*/memory)

# --- Validation ---
if [[ -z "$VAULT_PATH" ]]; then
    echo "[integrity] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

if [[ ! -d "$VAULT_PATH" ]]; then
    echo "[integrity] Vault not found: $VAULT_PATH" >&2
    exit 1
fi

VAULT_TARGET="$VAULT_PATH/$DEST_DIR"

if [[ ! -d "$VAULT_TARGET" ]]; then
    echo "[integrity] Vault memory dir not found: $VAULT_TARGET" >&2
    echo "[integrity] Run sync-memory-to-vault.sh first" >&2
    exit 0
fi

echo "[integrity] Checking vault ↔ dotfiles consistency..."

# --- Helper: strip Obsidian-specific frontmatter fields ---
# Removes obsidian_tags and synced_at from within the frontmatter block (--- ... ---)
# Preserves all other fields (name, description, type, etc.)
strip_obsidian_frontmatter() {
    local src_file="$1"
    local dest_file="$2"

    awk '
        BEGIN { fence=0; in_fm=0 }
        /^---$/ {
            fence++
            if (fence == 1) { in_fm=1; print; next }
            if (fence == 2) { in_fm=0; print; next }
        }
        in_fm && /^obsidian_tags:/ { next }
        in_fm && /^synced_at:/ { next }
        { print }
    ' "$src_file" > "$dest_file"
}

# --- Collect dotfiles memory files into an associative map ---
declare -A dotfiles_map  # filename -> path

for src_dir in "${MEMORY_SOURCES[@]}"; do
    [[ -d "$src_dir" ]] || continue
    for src_file in "$src_dir"/*.md; do
        [[ -f "$src_file" ]] || continue
        filename="$(basename "$src_file")"
        [[ "$filename" == "MEMORY.md" ]] && continue
        dotfiles_map["$filename"]="$src_file"
    done
done

# --- Check categories ---
vault_only=()
vault_newer=()
vault_newer_dates=()   # parallel array: "vault_date dotfiles_date"
dotfiles_only=()

# 1. Iterate Vault files → find Vault-only and Vault-newer
for vault_file in "$VAULT_TARGET"/*.md; do
    [[ -f "$vault_file" ]] || continue
    filename="$(basename "$vault_file")"
    [[ "$filename" == "MEMORY.md" ]] && continue

    if [[ -z "${dotfiles_map[$filename]+_}" ]]; then
        # Vault-only
        vault_only+=("$filename")
    else
        dotfiles_file="${dotfiles_map[$filename]}"
        if [[ "$vault_file" -nt "$dotfiles_file" ]]; then
            # Vault is newer
            vault_newer+=("$filename")
            vault_date="$(date -r "$vault_file" +%Y-%m-%d 2>/dev/null || stat -f '%Sm' -t '%Y-%m-%d' "$vault_file" 2>/dev/null || echo 'unknown')"
            df_date="$(date -r "$dotfiles_file" +%Y-%m-%d 2>/dev/null || stat -f '%Sm' -t '%Y-%m-%d' "$dotfiles_file" 2>/dev/null || echo 'unknown')"
            vault_newer_dates+=("$vault_date $df_date")
        fi
    fi
done

# 2. Iterate dotfiles files → find dotfiles-only
for filename in "${!dotfiles_map[@]}"; do
    vault_file="$VAULT_TARGET/$filename"
    if [[ ! -f "$vault_file" ]]; then
        dotfiles_only+=("$filename")
    fi
done

# --- Report ---
echo "[integrity] Vault-only: ${#vault_only[@]} files"
for f in "${vault_only[@]}"; do
    echo "  - $f (recommend: reverse-sync)"
done

echo "[integrity] Vault-newer: ${#vault_newer[@]} file(s)"
for i in "${!vault_newer[@]}"; do
    f="${vault_newer[$i]}"
    dates="${vault_newer_dates[$i]}"
    vd="${dates%% *}"
    dd="${dates##* }"
    echo "  - $f (vault: $vd, dotfiles: $dd)"
done

echo "[integrity] dotfiles-only: ${#dotfiles_only[@]} files"
for f in "${dotfiles_only[@]}"; do
    echo "  - $f (recommend: run sync-memory-to-vault.sh)"
done

total=$(( ${#vault_only[@]} + ${#vault_newer[@]} + ${#dotfiles_only[@]} ))
echo "[integrity] Summary: $total inconsistencies found"

[[ $total -eq 0 ]] && exit 0

# --- Fix mode ---
if $DRY_RUN && ! $FIX; then
    echo "[integrity] Run with --fix to apply reverse-sync" >&2
    exit 0
fi

if $FIX; then
    echo "[integrity] Fixing $total inconsistencies..."
    fixed=0

    # Fix Vault-only: reverse-sync Vault → dotfiles
    for filename in "${vault_only[@]}"; do
        vault_file="$VAULT_TARGET/$filename"

        # Determine which memory dir to place the file in (use first available)
        dest_dir=""
        for src_dir in "${MEMORY_SOURCES[@]}"; do
            [[ -d "$src_dir" ]] || continue
            dest_dir="$src_dir"
            break
        done

        if [[ -z "$dest_dir" ]]; then
            echo "[integrity] Warning: no memory directory found, skipping $filename" >&2
            continue
        fi

        dest_file="$dest_dir/$filename"
        strip_obsidian_frontmatter "$vault_file" "$dest_file"
        echo "[integrity] Reverse-synced: $filename → $dest_dir/"
        fixed=$((fixed + 1))
    done

    # Fix Vault-newer: update dotfiles from Vault
    for i in "${!vault_newer[@]}"; do
        filename="${vault_newer[$i]}"
        vault_file="$VAULT_TARGET/$filename"
        dotfiles_file="${dotfiles_map[$filename]}"
        dest_dir="$(dirname "$dotfiles_file")"

        strip_obsidian_frontmatter "$vault_file" "$dotfiles_file"
        echo "[integrity] Updated: $filename (stripped obsidian_tags, synced_at)"
        fixed=$((fixed + 1))
    done

    # dotfiles-only: just report (user should run sync-memory-to-vault.sh)
    for filename in "${dotfiles_only[@]}"; do
        echo "[integrity] Skipped (dotfiles-only): $filename — run sync-memory-to-vault.sh to push to Vault"
    done

    echo "[integrity] Done. $fixed file(s) fixed."
fi
