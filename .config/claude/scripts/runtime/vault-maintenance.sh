#!/usr/bin/env bash
# vault-maintenance.sh — Obsidian Vault 定期メンテナンス
#
# Vault のノート品質を自動チェックする:
#   - 孤立ノート検出 (04-Galaxy/, 05-Literature/ 内でどこからも参照されていないノート)
#   - リンク切れ検出 ([[wikilink]] が存在しないファイルを参照している)
#   - Stale Seed 検出 (#status/seed タグ + 更新日30日以上前)
#   - 重複候補検出 (04-Galaxy/ 内でファイル名の単語重複率が高いペア)
#
# Usage: vault-maintenance.sh [--dry-run]
# Env:   OBSIDIAN_VAULT_PATH (required)
#
# cron example: 0 9 * * 1 /path/to/vault-maintenance.sh >> /tmp/vault-maintenance.log 2>&1

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# --- Config ---
VAULT_PATH="${OBSIDIAN_VAULT_PATH:-}"
STALE_DAYS=30
TODAY="$(date +%Y-%m-%d)"

# --- Validation ---
if [[ -z "$VAULT_PATH" ]]; then
    echo "[vault-maintenance] OBSIDIAN_VAULT_PATH not set, skipping" >&2
    exit 0
fi

if [[ ! -d "$VAULT_PATH" ]]; then
    echo "[vault-maintenance] Vault not found: $VAULT_PATH" >&2
    exit 1
fi

# --- Result accumulators ---
orphan_notes=()
broken_links=()    # "file.md -> [[target]]" format
stale_seeds=()
duplicate_pairs=() # "noteA.md <-> noteB.md (score)" format

# ---------------------------------------------------------------------------
# check_orphan_notes
#   04-Galaxy/ と 05-Literature/ 内で、他のどのノートからも [[wikilink]] で
#   参照されていないノートを検出する
# ---------------------------------------------------------------------------
check_orphan_notes() {
    echo "[vault-maintenance] Checking orphan notes..."

    local target_dirs=("$VAULT_PATH/04-Galaxy" "$VAULT_PATH/05-Literature")

    for dir in "${target_dirs[@]}"; do
        [[ -d "$dir" ]] || continue

        while IFS= read -r -d '' note_path; do
            local note_filename
            note_filename="$(basename "$note_path" .md)"

            # Search for [[note_filename]] references across the entire vault
            local match_count
            match_count=$(grep -rl "\[\[${note_filename}" "$VAULT_PATH" \
                --include="*.md" 2>/dev/null \
                | grep -v "^${note_path}$" \
                | wc -l || true)

            if [[ "$match_count" -eq 0 ]]; then
                orphan_notes+=("${note_path#"$VAULT_PATH/"}")
            fi
        done < <(find "$dir" -maxdepth 2 -name "*.md" -print0 2>/dev/null)
    done

    echo "[vault-maintenance] Orphan notes found: ${#orphan_notes[@]}"
}

# ---------------------------------------------------------------------------
# check_broken_links
#   全ノート内の [[wikilink]] を抽出し、対応するファイルが Vault 内に
#   存在しないものを検出する
# ---------------------------------------------------------------------------
check_broken_links() {
    echo "[vault-maintenance] Checking broken links..."

    while IFS= read -r -d '' note_path; do
        local relative_path="${note_path#"$VAULT_PATH/"}"

        # Extract all [[...]] wikilinks from the file
        while IFS= read -r link_target; do
            [[ -z "$link_target" ]] && continue

            # Strip heading anchors (#section) and aliases (|alias)
            local clean_target
            clean_target="${link_target%%#*}"
            clean_target="${clean_target%%|*}"
            clean_target="$(echo "$clean_target" | xargs)"  # trim whitespace
            [[ -z "$clean_target" ]] && continue

            # Search for matching file anywhere in vault
            local found
            found=$(find "$VAULT_PATH" -name "${clean_target}.md" \
                -not -path "*/.*" 2>/dev/null | head -1 || true)

            if [[ -z "$found" ]]; then
                broken_links+=("${relative_path} -> [[${clean_target}]]")
            fi
        done < <(grep -o '\[\[[^]]*\]\]' "$note_path" 2>/dev/null \
            | sed 's/\[\[//g; s/\]\]//g' || true)

    done < <(find "$VAULT_PATH" -name "*.md" \
        -not -path "*/.git/*" -not -path "*/.*" -print0 2>/dev/null)

    echo "[vault-maintenance] Broken links found: ${#broken_links[@]}"
}

# ---------------------------------------------------------------------------
# check_stale_seeds
#   #status/seed タグを持ち、ファイル更新日が STALE_DAYS 日以上前のノートを検出
# ---------------------------------------------------------------------------
check_stale_seeds() {
    echo "[vault-maintenance] Checking stale seeds (older than ${STALE_DAYS} days)..."

    while IFS= read -r note_path; do
        [[ -f "$note_path" ]] || continue

        # Check modification time: find files older than STALE_DAYS
        local is_stale
        is_stale=$(find "$note_path" -not -newermt "-${STALE_DAYS} days" \
            2>/dev/null | head -1 || true)

        if [[ -n "$is_stale" ]]; then
            stale_seeds+=("${note_path#"$VAULT_PATH/"}")
        fi
    done < <(grep -rl '#status/seed' "$VAULT_PATH" --include="*.md" 2>/dev/null || true)

    echo "[vault-maintenance] Stale seeds found: ${#stale_seeds[@]}"
}

# ---------------------------------------------------------------------------
# check_duplicates
#   04-Galaxy/ 内で、ファイル名（タイムスタンプ除去後）の単語重複率が
#   高いペアを検出する（簡易実装: 共通単語数 / 最大単語数）
# ---------------------------------------------------------------------------
check_duplicates() {
    echo "[vault-maintenance] Checking duplicate candidates in 04-Galaxy/..."

    [[ -d "$VAULT_PATH/04-Galaxy" ]] || return 0

    # Collect all note filenames, stripping timestamps (YYYYMMDDHHMMSS or YYYY-MM-DD)
    local -a notes=()
    while IFS= read -r note_path; do
        notes+=("$note_path")
    done < <(find "$VAULT_PATH/04-Galaxy" -maxdepth 2 -name "*.md" 2>/dev/null | sort)

    local note_count="${#notes[@]}"
    if [[ "$note_count" -lt 2 ]]; then
        echo "[vault-maintenance] Duplicate check skipped (fewer than 2 notes)"
        return 0
    fi

    # Compare each pair
    for ((i = 0; i < note_count - 1; i++)); do
        local name_a
        name_a="$(basename "${notes[$i]}" .md)"
        # Remove leading timestamps: 14-digit, 8-digit, or YYYY-MM-DD
        name_a="$(echo "$name_a" | sed 's/^[0-9]\{14\}[[:space:]_-]*//; s/^[0-9]\{8\}[[:space:]_-]*//; s/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}[[:space:]_-]*//')"
        # Normalize: lowercase, replace separators with spaces
        local words_a
        words_a="$(echo "$name_a" | tr '[:upper:]' '[:lower:]' | tr '-_ ' '\n' | grep -v '^$' || true)"

        for ((j = i + 1; j < note_count; j++)); do
            local name_b
            name_b="$(basename "${notes[$j]}" .md)"
            name_b="$(echo "$name_b" | sed 's/^[0-9]\{14\}[[:space:]_-]*//; s/^[0-9]\{8\}[[:space:]_-]*//; s/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}[[:space:]_-]*//')"
            local words_b
            words_b="$(echo "$name_b" | tr '[:upper:]' '[:lower:]' | tr '-_ ' '\n' | grep -v '^$' || true)"

            # Count common words
            local common_count total_a total_b max_count score
            common_count=$(comm -12 \
                <(echo "$words_a" | sort -u) \
                <(echo "$words_b" | sort -u) \
                2>/dev/null | wc -l || echo 0)
            total_a=$(echo "$words_a" | grep -c '.' 2>/dev/null || echo 0)
            total_b=$(echo "$words_b" | grep -c '.' 2>/dev/null || echo 0)

            if [[ "$total_a" -gt "$total_b" ]]; then
                max_count="$total_a"
            else
                max_count="$total_b"
            fi

            # Avoid division by zero; threshold: common >= 2 AND ratio >= 0.5
            if [[ "$max_count" -gt 0 && "$common_count" -ge 2 ]]; then
                # Integer arithmetic: score = common * 100 / max
                score=$(( common_count * 100 / max_count ))
                if [[ "$score" -ge 50 ]]; then
                    local rel_a rel_b
                    rel_a="${notes[$i]#"$VAULT_PATH/"}"
                    rel_b="${notes[$j]#"$VAULT_PATH/"}"
                    duplicate_pairs+=("${rel_a} <-> ${rel_b} (score: ${score}%)")
                fi
            fi
        done
    done

    echo "[vault-maintenance] Duplicate candidates found: ${#duplicate_pairs[@]}"
}

# ---------------------------------------------------------------------------
# print_results
#   各チェック結果を整形して stdout に出力する
# ---------------------------------------------------------------------------
print_results() {
    echo ""
    echo "====================================================="
    echo "  Vault Maintenance Report — ${TODAY}"
    echo "====================================================="
    echo ""

    # Orphan notes
    echo "## 孤立ノート (${#orphan_notes[@]} 件)"
    if [[ "${#orphan_notes[@]}" -gt 0 ]]; then
        for note in "${orphan_notes[@]}"; do
            echo "  - $note"
        done
    else
        echo "  (なし)"
    fi
    echo ""

    # Broken links
    echo "## リンク切れ (${#broken_links[@]} 件)"
    if [[ "${#broken_links[@]}" -gt 0 ]]; then
        for link in "${broken_links[@]}"; do
            echo "  - $link"
        done
    else
        echo "  (なし)"
    fi
    echo ""

    # Stale seeds
    echo "## Stale Seed (${#stale_seeds[@]} 件, ${STALE_DAYS}日以上未更新)"
    if [[ "${#stale_seeds[@]}" -gt 0 ]]; then
        for seed in "${stale_seeds[@]}"; do
            echo "  - $seed"
        done
    else
        echo "  (なし)"
    fi
    echo ""

    # Duplicate candidates
    echo "## 重複候補 (${#duplicate_pairs[@]} 件)"
    if [[ "${#duplicate_pairs[@]}" -gt 0 ]]; then
        for pair in "${duplicate_pairs[@]}"; do
            echo "  - $pair"
        done
    else
        echo "  (なし)"
    fi
    echo ""
}

# ---------------------------------------------------------------------------
# save_report
#   結果サマリーを Vault の 00-Inbox/ に Markdown ファイルとして保存する
#   問題が1件もなければ保存しない
# ---------------------------------------------------------------------------
save_report() {
    local total_issues=$(( ${#orphan_notes[@]} + ${#broken_links[@]} + ${#stale_seeds[@]} + ${#duplicate_pairs[@]} ))

    if [[ "$total_issues" -eq 0 ]]; then
        echo "[vault-maintenance] No issues found, skipping report creation"
        return 0
    fi

    local inbox_dir="$VAULT_PATH/00-Inbox"
    mkdir -p "$inbox_dir"

    local report_path="$inbox_dir/vault-maintenance-report-${TODAY}.md"

    {
        echo "---"
        echo "created: \"${TODAY}\""
        echo "tags:"
        echo "  - type/maintenance-report"
        echo "  - status/needs-action"
        echo "---"
        echo ""
        echo "# Vault Maintenance Report — ${TODAY}"
        echo ""
        echo "## サマリー"
        echo ""
        echo "| チェック項目 | 件数 |"
        echo "| --- | --- |"
        echo "| 孤立ノート | ${#orphan_notes[@]} |"
        echo "| リンク切れ | ${#broken_links[@]} |"
        echo "| Stale Seed | ${#stale_seeds[@]} |"
        echo "| 重複候補 | ${#duplicate_pairs[@]} |"
        echo ""

        if [[ "${#orphan_notes[@]}" -gt 0 ]]; then
            echo "## 孤立ノート"
            echo ""
            for note in "${orphan_notes[@]}"; do
                local note_name
                note_name="$(basename "$note" .md)"
                echo "- [[${note_name}]]"
            done
            echo ""
        fi

        if [[ "${#broken_links[@]}" -gt 0 ]]; then
            echo "## リンク切れ"
            echo ""
            for link in "${broken_links[@]}"; do
                echo "- $link"
            done
            echo ""
        fi

        if [[ "${#stale_seeds[@]}" -gt 0 ]]; then
            echo "## Stale Seed (${STALE_DAYS}日以上未更新)"
            echo ""
            for seed in "${stale_seeds[@]}"; do
                local seed_name
                seed_name="$(basename "$seed" .md)"
                echo "- [[${seed_name}]]"
            done
            echo ""
        fi

        if [[ "${#duplicate_pairs[@]}" -gt 0 ]]; then
            echo "## 重複候補"
            echo ""
            for pair in "${duplicate_pairs[@]}"; do
                echo "- $pair"
            done
            echo ""
        fi
    } > "$report_path"

    echo "[vault-maintenance] Report saved: $report_path"
}

# --- Main ---
echo "[vault-maintenance] Starting maintenance for: $VAULT_PATH"
$DRY_RUN && echo "[vault-maintenance] DRY RUN mode — report will not be saved"

check_orphan_notes
check_broken_links
check_stale_seeds
check_duplicates

print_results

if ! $DRY_RUN; then
    save_report
fi

echo "[vault-maintenance] Done"
