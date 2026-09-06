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

PROJECT_DIR="${DOCTOR_STALE_PROJECT_DIR:-$PWD}"

orphaned_count=0
backup_count=0
anchor_count=0

# mtime (epoch) of one file; prints nothing and returns 1 if unreadable.
# Do NOT chain `stat -f %m || stat -c %Y`: on GNU coreutils `-f` means
# "filesystem status" and still writes to stdout, so the two outputs get
# concatenated into a non-numeric value that breaks arithmetic under `set -u`.
file_mtime() {
  local m
  if m=$(stat -f %m "$1" 2>/dev/null) && [[ "$m" =~ ^[0-9]+$ ]]; then
    echo "$m"
  elif m=$(stat -c %Y "$1" 2>/dev/null) && [[ "$m" =~ ^[0-9]+$ ]]; then
    echo "$m"
  else
    return 1
  fi
}

# newest mtime (epoch) among all files under a dir; 0 if none/unreadable.
newest_mtime() {
  local dir="$1" newest=0 m
  while IFS= read -r f; do
    if m=$(file_mtime "$f"); then
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

# --- 3) resume anchors past their contracted lifetime ---
# resume-anchor-contract.md gives each anchor a lifetime and an owner, but the
# owner is only a WRITE path. Plan is reported by plan-close-detector.py and
# HANDOFF.md is retired by session-load.js once it has been read at SessionStart;
# RUNNING_BRIEF.md had no detector at all and sat 104 days stale describing a
# finished project (2026-09-05).
echo "[resume anchors] $PROJECT_DIR (contract: references/resume-anchor-contract.md)"
while IFS= read -r f; do
  [[ -n "$f" && -f "$f" ]] || continue
  m=$(file_mtime "$f") || continue
  age_days=$(((NOW - m) / 86400))
  if [[ "$age_days" -gt "$STALE_DAYS" ]]; then
    printf "  stale(%dd): %s\n" "$age_days" "$f"
    anchor_count=$((anchor_count + 1))
  fi
done < <(
  printf '%s\n' "$PROJECT_DIR/RUNNING_BRIEF.md" "$PROJECT_DIR/HANDOFF.md" \
    "$PROJECT_DIR/tmp/HANDOFF.md"
)
[[ "$anchor_count" -eq 0 ]] && echo "  stale anchors: none"
echo "  (plans under docs/plans/active are owned by plan-close-detector.py — not rescanned here)"
echo ""

# --- summary ---
echo "=== summary ==="
echo "  orphaned codex state dirs: $orphaned_count"
echo "  backup residue files:      $backup_count"
echo "  stale resume anchors:      $anchor_count"
if [[ "$orphaned_count" -gt 0 || "$backup_count" -gt 0 || "$anchor_count" -gt 0 ]]; then
  echo ""
  echo "  NOTE: nothing was deleted. Remove manually after review if appropriate."
fi

exit 0
