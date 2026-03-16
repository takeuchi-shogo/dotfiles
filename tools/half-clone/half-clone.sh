#!/usr/bin/env bash
set -euo pipefail

# half-clone.sh — Back up the latter 50% of the current Claude conversation
# before auto-compact discards context. Keeps 3 generations of backups.

BACKUP_DIR="${HOME}/dotfiles/tmp"
BACKUP_FILE="${BACKUP_DIR}/half-clone-backup.jsonl"
CLAUDE_DIR="${HOME}/.claude"

# ── Find the most recent .jsonl conversation file ────────────────
latest_jsonl=""
if [[ -d "${CLAUDE_DIR}" ]]; then
  latest_jsonl=$(find "${CLAUDE_DIR}" -maxdepth 3 -name '*.jsonl' -type f \
    -newer "${CLAUDE_DIR}" -o -name '*.jsonl' -type f 2>/dev/null \
    | xargs ls -t 2>/dev/null | head -1 || true)
fi

# Fallback: broader search
if [[ -z "${latest_jsonl}" ]]; then
  latest_jsonl=$(find "${CLAUDE_DIR}" -maxdepth 3 -name '*.jsonl' -type f 2>/dev/null \
    | xargs ls -t 2>/dev/null | head -1 || true)
fi

if [[ -z "${latest_jsonl}" ]]; then
  # No conversation file found — graceful exit
  exit 0
fi

# ── Check minimum line count ─────────────────────────────────────
total_lines=$(wc -l < "${latest_jsonl}" | tr -d ' ')
if (( total_lines < 4 )); then
  # Too few lines to be worth backing up
  exit 0
fi

# ── Rotate backups (3 generations) ───────────────────────────────
mkdir -p "${BACKUP_DIR}"

if [[ -f "${BACKUP_FILE}.2" ]]; then
  mv -f "${BACKUP_FILE}.2" "${BACKUP_FILE}.3"
fi
if [[ -f "${BACKUP_FILE}.1" ]]; then
  mv -f "${BACKUP_FILE}.1" "${BACKUP_FILE}.2"
fi
if [[ -f "${BACKUP_FILE}" ]]; then
  mv -f "${BACKUP_FILE}" "${BACKUP_FILE}.1"
fi

# ── Extract latter 50% ──────────────────────────────────────────
half=$(( total_lines / 2 ))
start_line=$(( total_lines - half + 1 ))

tail -n +"${start_line}" "${latest_jsonl}" > "${BACKUP_FILE}"

exit 0
