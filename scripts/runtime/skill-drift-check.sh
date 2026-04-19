#!/usr/bin/env bash
# Detect drift between locked provenance and upstream HEAD for external skills.
#
# Reports entries in skills-lock.json whose provenance.commit_sha no longer
# matches `gh api repos/<source>/commits/<ref>` output.
#
# Usage:
#   scripts/runtime/skill-drift-check.sh             # all github entries
#   scripts/runtime/skill-drift-check.sh <name>...   # specific skills only
#
# Exit codes:
#   0  no drift
#   1  drift detected
#   2  lockfile or dependency error
set -euo pipefail

DOTFILES_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCKFILE="$DOTFILES_ROOT/skills-lock.json"

if ! command -v gh >/dev/null 2>&1; then
  echo "[error] gh CLI required" >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "[error] jq required" >&2
  exit 2
fi
if [ ! -f "$LOCKFILE" ]; then
  echo "[error] lockfile not found: $LOCKFILE" >&2
  exit 2
fi

filter_names=("$@")
should_check() {
  [ ${#filter_names[@]} -eq 0 ] && return 0
  local name="$1"
  for n in "${filter_names[@]}"; do
    [ "$n" = "$name" ] && return 0
  done
  return 1
}

drift_count=0
checked=0

# iterate over each skill with github sourceType
while IFS=$'\t' read -r name source ref locked_sha; do
  should_check "$name" || continue
  [ "$source" = "null" ] && continue
  [ "$locked_sha" = "null" ] && locked_sha=""
  checked=$((checked + 1))

  upstream_sha=$(gh api "repos/$source/commits/${ref:-HEAD}" --jq '.sha' 2>/dev/null || true)
  if [ -z "$upstream_sha" ]; then
    echo "warn  $name — could not resolve upstream (source=$source ref=$ref)"
    continue
  fi

  if [ "$upstream_sha" = "$locked_sha" ]; then
    echo "ok    $name — pinned to ${locked_sha:0:12}"
  else
    drift_count=$((drift_count + 1))
    echo "drift $name"
    echo "      locked:   ${locked_sha:0:12}"
    echo "      upstream: ${upstream_sha:0:12}"
    echo "      source:   $source@${ref:-HEAD}"
  fi
done < <(
  jq -r '
    .skills
    | to_entries[]
    | select(.value.sourceType == "github")
    | [
        .key,
        (.value.source // "null"),
        (.value.provenance.ref // "HEAD"),
        (.value.provenance.commit_sha // "null")
      ]
    | @tsv
  ' "$LOCKFILE"
)

echo ""
echo "[summary] checked=$checked, drift=$drift_count"
[ "$drift_count" -eq 0 ]
