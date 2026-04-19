#!/usr/bin/env bash
# Verify installed external skills match the computedHash in skills-lock.json.
#
# Detects tampered or corrupted skill payloads. Intended to run after the
# skill install step in .bin/init-install.sh (setup_claude_plugins) and as
# `task skills:verify` on demand.
#
# Hash method: sha256 of concatenated SKILL.md content + sorted file list.
# This mirrors the convention used when populating `computedHash` in the
# lockfile (see scripts/security/ for any generator). If `computedHash` is
# null or empty, the entry is skipped with a warning.
#
# Exit codes:
#   0  all checked entries match
#   1  mismatch detected
#   2  dependency/io error
set -euo pipefail

DOTFILES_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCKFILE="$DOTFILES_ROOT/skills-lock.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "[error] jq required" >&2
  exit 2
fi
if [ ! -f "$LOCKFILE" ]; then
  echo "[error] lockfile not found: $LOCKFILE" >&2
  exit 2
fi

# Candidate install roots. An external skill may be under any of these.
SKILL_ROOTS=(
  "$HOME/.claude/skills"
  "$HOME/.claude/plugins"
  "$HOME/.codex/skills"
  "$HOME/.agents/skills"
)

find_skill_dir() {
  local name="$1"
  for root in "${SKILL_ROOTS[@]}"; do
    [ -d "$root/$name" ] && { echo "$root/$name"; return 0; }
  done
  return 1
}

# Compute a stable content hash over a skill directory.
compute_hash() {
  local dir="$1"
  (cd "$dir" && find . -type f \! -name '.DS_Store' -print0 | sort -z | xargs -0 shasum -a 256) \
    | shasum -a 256 \
    | awk '{print $1}'
}

mismatch=0
checked=0
skipped=0

while IFS=$'\t' read -r name locked_hash; do
  if [ -z "$locked_hash" ] || [ "$locked_hash" = "null" ]; then
    echo "skip  $name (no computedHash)"
    skipped=$((skipped + 1))
    continue
  fi
  skill_dir=$(find_skill_dir "$name" || true)
  if [ -z "$skill_dir" ]; then
    echo "skip  $name (not installed)"
    skipped=$((skipped + 1))
    continue
  fi
  actual=$(compute_hash "$skill_dir")
  checked=$((checked + 1))
  if [ "$actual" = "$locked_hash" ]; then
    echo "ok    $name"
  else
    mismatch=$((mismatch + 1))
    echo "FAIL  $name"
    echo "      locked: ${locked_hash:0:16}"
    echo "      actual: ${actual:0:16}"
    echo "      path:   $skill_dir"
  fi
done < <(
  jq -r '.skills | to_entries[] | [.key, (.value.computedHash // "null")] | @tsv' "$LOCKFILE"
)

echo ""
echo "[summary] checked=$checked, skipped=$skipped, mismatch=$mismatch"
[ "$mismatch" -eq 0 ]
