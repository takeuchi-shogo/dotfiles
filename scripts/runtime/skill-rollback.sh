#!/usr/bin/env bash
# Snapshot + rollback tool for skills-lock.json.
#
# Usage:
#   scripts/runtime/skill-rollback.sh snapshot            # save current as skills-lock-history/YYYYMMDD-HHMMSS.json
#   scripts/runtime/skill-rollback.sh list                # list available snapshots (newest first)
#   scripts/runtime/skill-rollback.sh --to=<timestamp>    # restore to specified snapshot
#   scripts/runtime/skill-rollback.sh --to=latest         # restore to most recent snapshot
#
# Snapshot rotation: the snapshot subcommand keeps at most 5 snapshots;
# older ones are pruned.
set -euo pipefail

DOTFILES_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCKFILE="$DOTFILES_ROOT/skills-lock.json"
HISTORY_DIR="$DOTFILES_ROOT/skills-lock-history"
MAX_SNAPSHOTS=5

usage() {
  sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# //; s/^#//'
  exit "${1:-0}"
}

snapshot() {
  [ -f "$LOCKFILE" ] || { echo "[error] lockfile not found: $LOCKFILE" >&2; exit 2; }
  mkdir -p "$HISTORY_DIR"
  local stamp
  stamp=$(date -u +'%Y%m%d-%H%M%S')
  local target="$HISTORY_DIR/$stamp.json"
  cp -p "$LOCKFILE" "$target"
  echo "saved: $target"
  # prune oldest beyond MAX_SNAPSHOTS
  mapfile -t files < <(ls -1t "$HISTORY_DIR"/*.json 2>/dev/null || true)
  if [ "${#files[@]}" -gt "$MAX_SNAPSHOTS" ]; then
    for ((i = MAX_SNAPSHOTS; i < ${#files[@]}; i++)); do
      rm -f "${files[i]}"
      echo "pruned: ${files[i]}"
    done
  fi
}

list_snapshots() {
  [ -d "$HISTORY_DIR" ] || { echo "(no snapshots yet)"; return 0; }
  ls -1t "$HISTORY_DIR"/*.json 2>/dev/null | while read -r f; do
    echo "$(basename "$f" .json)  $(stat -f '%z' "$f" 2>/dev/null || stat -c '%s' "$f") bytes"
  done
}

resolve_snapshot() {
  local ts="$1"
  if [ "$ts" = "latest" ]; then
    ls -1t "$HISTORY_DIR"/*.json 2>/dev/null | head -n1
    return
  fi
  local candidate="$HISTORY_DIR/$ts.json"
  [ -f "$candidate" ] && echo "$candidate"
}

rollback() {
  local ts="$1"
  [ -d "$HISTORY_DIR" ] || { echo "[error] no snapshots available" >&2; exit 2; }
  local src
  src=$(resolve_snapshot "$ts")
  if [ -z "$src" ]; then
    echo "[error] snapshot not found: $ts" >&2
    list_snapshots
    exit 2
  fi
  # snapshot current before overwriting, so a rollback can be rolled back
  snapshot >/dev/null
  cp -p "$src" "$LOCKFILE"
  echo "restored: $LOCKFILE <- $(basename "$src")"
}

case "${1:-}" in
  snapshot) snapshot ;;
  list)     list_snapshots ;;
  --to=*)   rollback "${1#--to=}" ;;
  ""|-h|--help) usage 0 ;;
  *)        echo "[error] unknown arg: $1" >&2; usage 1 ;;
esac
