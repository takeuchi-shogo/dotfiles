#!/usr/bin/env bash
# scripts/lifecycle/doctor-stale.sh — stale-state inventory (read-only)
#
# Usage: doctor-stale.sh
# Output: category summary + path list (count, age, size). Never deletes.
# Exit:   always 0 — stale state is informational, NOT a setup failure.
#
# Sibling to doctor.sh but a distinct concern: doctor.sh reports setup
# HEALTH (OK/WARN/FAIL + exit code); this reports an INVENTORY of state
# that has accumulated and may be safe to remove MANUALLY. It deliberately
# performs no deletion (claude-code-harness `doctor --migration-report`
# pattern: inventory, don't mutate).

set -uo pipefail

STALE_DAYS="${DOCTOR_STALE_DAYS:-30}"
NOW="$(date +%s)"
THRESHOLD=$((STALE_DAYS * 86400))

CODEX_STATE_DIR="${DOCTOR_STALE_CODEX_DIR:-$HOME/.claude/plugins/data/codex-openai-codex/state}"
CLAUDE_DIR="${DOCTOR_STALE_CLAUDE_DIR:-$HOME/.claude}"

orphaned_count=0
backup_count=0

# newest mtime (epoch) among all files under a dir; 0 if none/unreadable.
newest_mtime() {
  local dir="$1" newest=0 m
  while IFS= read -r f; do
    if m=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null); then
      [[ "$m" -gt "$newest" ]] && newest="$m"
    fi
  done < <(find "$dir" -type f 2>/dev/null)
  echo "$newest"
}

echo "=== stale-state inventory (read-only, threshold: ${STALE_DAYS}d) ==="
echo ""

# --- 1) orphaned codex job state ---
echo "[codex job state] $CODEX_STATE_DIR"
if [[ -d "$CODEX_STATE_DIR" ]]; then
  for d in "$CODEX_STATE_DIR"/*/; do
    [[ -d "$d" ]] || continue
    mtime=$(newest_mtime "$d")
    if [[ "$mtime" -eq 0 ]]; then
      continue
    fi
    age_days=$(((NOW - mtime) / 86400))
    if [[ "$age_days" -gt "$STALE_DAYS" ]]; then
      size=$(du -sh "$d" 2>/dev/null | cut -f1)
      printf "  orphaned: %s (%dd idle, %s)\n" "${d%/}" "$age_days" "${size:-?}"
      orphaned_count=$((orphaned_count + 1))
    fi
  done
  [[ "$orphaned_count" -eq 0 ]] && echo "  orphaned: none"
else
  echo "  (state dir not present — skipped)"
fi
echo ""

# --- 2) backup residue under ~/.claude ---
echo "[backup residue] $CLAUDE_DIR (*.bak / *.orig, depth<=3)"
if [[ -d "$CLAUDE_DIR" ]]; then
  while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    printf "  residue: %s\n" "$f"
    backup_count=$((backup_count + 1))
  done < <(find "$CLAUDE_DIR" -maxdepth 3 \( -name '*.bak' -o -name '*.orig' \) -type f 2>/dev/null)
  [[ "$backup_count" -eq 0 ]] && echo "  residue: none"
else
  echo "  (dir not present — skipped)"
fi
echo ""

# --- summary ---
echo "=== summary ==="
echo "  orphaned codex state dirs: $orphaned_count"
echo "  backup residue files:      $backup_count"
if [[ "$orphaned_count" -gt 0 || "$backup_count" -gt 0 ]]; then
  echo ""
  echo "  NOTE: nothing was deleted. Remove manually after review if appropriate."
fi

exit 0
