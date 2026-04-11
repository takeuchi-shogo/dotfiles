#!/usr/bin/env bash
# weekly-downloads-cleanup.sh — ~/Downloads の自動整理
#
# claude -p でファイルをタイプ別にサブフォルダに分類する。
# 削除は一切行わない（移動のみ）。
#
# Usage: weekly-downloads-cleanup.sh
# cron example: 0 10 * * 0 /path/to/weekly-downloads-cleanup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NOTIFY="$SCRIPT_DIR/cmux-notify.sh"
DOWNLOADS="$HOME/Downloads"

# --- Preflight ---
if ! command -v claude &>/dev/null; then
    echo "[downloads-cleanup] claude CLI not found, skipping" >&2
    exit 1
fi

if [[ ! -d "$DOWNLOADS" ]]; then
    echo "[downloads-cleanup] $DOWNLOADS not found" >&2
    exit 1
fi

# Count files (excluding hidden and subdirectories)
file_count=$(find "$DOWNLOADS" -maxdepth 1 -type f -not -name '.*' | wc -l | tr -d ' ')

if [[ "$file_count" -lt 5 ]]; then
    echo "[downloads-cleanup] Only $file_count files, skipping (threshold: 5)"
    exit 0
fi

# --- Cleanup via claude -p ---
prompt="Look at all files in $DOWNLOADS (top-level only, not subdirectories).
Organize them into subfolders within $DOWNLOADS by type:
- PDFs → $DOWNLOADS/PDFs/
- Images (png, jpg, jpeg, gif, svg, webp) → $DOWNLOADS/Images/
- Videos (mp4, mov, avi, mkv) → $DOWNLOADS/Videos/
- Archives (zip, tar, gz, dmg, pkg) → $DOWNLOADS/Archives/
- Documents (doc, docx, xls, xlsx, ppt, pptx, csv, txt) → $DOWNLOADS/Documents/
- Code (js, ts, py, go, rs, sh, json, yaml, yml, toml) → $DOWNLOADS/Code/
- Other → leave in place (do NOT move unknown types)

Rules:
- Create folders that don't exist.
- Don't delete anything. Move only.
- Skip any file modified in the last 24 hours (it might be in use).
- Print a summary: how many files moved and where."

result=$(claude -p "$prompt" --allowedTools Bash --output-format text 2>/dev/null) || {
    echo "[downloads-cleanup] claude -p failed" >&2
    exit 1
}

# --- Notify ---
if [[ -x "$NOTIFY" ]]; then
    "$NOTIFY" "Downloads Cleanup" "Organized $file_count files" hero
fi

echo "$result"
