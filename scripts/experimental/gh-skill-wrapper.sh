#!/usr/bin/env bash
# Experimental thin wrapper around `gh skill` (GitHub CLI v2.90+).
#
# Status: WAIT-AND-SEE. This wrapper exists to let us kick the tires on the
# upstream `gh skill` UX without fully swapping out our skills-lock.json +
# symlink pipeline. Promote to first-class only after real usage confirms
# stability and that install paths interop with our provenance / hash checks.
#
# Usage:
#   scripts/experimental/gh-skill-wrapper.sh install <repo> [<name>[@version]] [gh flags...]
#   scripts/experimental/gh-skill-wrapper.sh search  <keyword> [gh flags...]
#   scripts/experimental/gh-skill-wrapper.sh update  [--all] [<name>...]
#   scripts/experimental/gh-skill-wrapper.sh doctor              # env/version sanity check
#
# Taskfile integration:
#   task skills:install-gh -- <repo> [<name>]
#   task skills:search-gh  -- <keyword>
set -euo pipefail

REQUIRED_MAJOR=2
REQUIRED_MINOR=90

usage() {
  sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# //; s/^#//'
  exit "${1:-0}"
}

check_gh_version() {
  if ! command -v gh >/dev/null 2>&1; then
    echo "[error] GitHub CLI (gh) not installed" >&2
    exit 2
  fi
  local version
  version=$(gh --version 2>/dev/null | head -1 | awk '{print $3}')
  local major minor
  IFS=. read -r major minor _ <<<"$version"
  if [ "${major:-0}" -lt "$REQUIRED_MAJOR" ] || {
    [ "${major:-0}" -eq "$REQUIRED_MAJOR" ] && [ "${minor:-0}" -lt "$REQUIRED_MINOR" ]
  }; then
    echo "[error] gh CLI v${REQUIRED_MAJOR}.${REQUIRED_MINOR}+ required, found v${version}" >&2
    echo "        upgrade with: brew upgrade gh" >&2
    exit 2
  fi
  # even on newer gh, `skill` subcommand may not exist if the feature flag
  # is disabled. Detect that up front.
  if ! gh skill --help >/dev/null 2>&1; then
    echo "[error] gh CLI v${version} does not expose the 'skill' subcommand" >&2
    echo "        (confirm GitHub announcement: 2026-04-16 changelog)" >&2
    exit 2
  fi
}

doctor() {
  echo "experimental: gh skill wrapper"
  echo "gh version:   $(gh --version 2>/dev/null | head -1)"
  if gh skill --help >/dev/null 2>&1; then
    echo "gh skill:     available"
  else
    echo "gh skill:     NOT available (feature-gated or too old)"
  fi
  echo "wrapper:      ${BASH_SOURCE[0]}"
  echo "note:         experimental — not integrated with skills-lock.json"
}

main() {
  case "${1:-}" in
    ""|-h|--help) usage 0 ;;
    doctor) shift; doctor ;;
    install|search|update|publish)
      local sub="$1"; shift
      check_gh_version
      exec gh skill "$sub" "$@"
      ;;
    *)
      echo "[error] unknown subcommand: $1" >&2
      usage 1
      ;;
  esac
}

main "$@"
