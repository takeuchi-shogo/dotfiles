#!/usr/bin/env bash
# scripts/lifecycle/claude-settings-sync-permissions.sh
#
# Replace the `permissions` block of the live ~/.claude/settings.json with the
# repo copy, leaving every other key (hooks injected by Superset/Orca, model,
# autoMode, ...) untouched.
#
# Why this exists: live settings.json is a real file, not a symlink (see
# doctor.sh check_settings), so repo permission edits never reach it on their
# own. `task doctor:settings` detects the drift; this script closes it.
#
# Usage:
#   claude-settings-sync-permissions.sh          # show drift, ask y/N on a terminal
#   claude-settings-sync-permissions.sh --yes    # show drift, apply without asking
#
# Without --yes and without a terminal it refuses: a permissions rewrite
# widens or narrows what the agent may run, so it must not happen unattended.
#
# Env: CLAUDE_SETTINGS_LIVE (default ~/.claude/settings.json)
#      CLAUDE_SETTINGS_REPO (default <repo>/.config/claude/settings.json)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIVE="${CLAUDE_SETTINGS_LIVE:-$HOME/.claude/settings.json}"
REPO="${CLAUDE_SETTINGS_REPO:-$ROOT_DIR/.config/claude/settings.json}"

assume_yes=0
case "${1:-}" in
  --yes) assume_yes=1 ;;
  "") ;;
  *) echo "usage: $0 [--yes]" >&2; exit 2 ;;
esac

command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }
for f in "$REPO" "$LIVE"; do
  [[ -f "$f" ]] || { echo "$f not found" >&2; exit 1; }
  jq empty "$f" || { echo "$f is not valid JSON" >&2; exit 1; }
done
jq -e '.permissions | type == "object" and
    all(to_entries[]; (.key | IN("allow", "ask", "deny", "additionalDirectories") | not)
                      or (.value | type == "array"))' "$REPO" >/dev/null \
  || { echo "$REPO permissions is missing or malformed; refusing to push it live" >&2; exit 1; }

drift=$(SETUP_DOCTOR_REPO_SETTINGS="$REPO" SETUP_DOCTOR_SETTINGS="$LIVE" \
  bash "$ROOT_DIR/scripts/lifecycle/doctor.sh" settings 2>&1 | grep 'FAIL: .*permissions' || true)
if [[ -z "$drift" ]] && jq -e 'has("permissions")' "$LIVE" >/dev/null; then
  echo "permissions already in sync: $LIVE"
  exit 0
fi

echo "permissions drift in $LIVE:"
if [[ -n "$drift" ]]; then printf '%s\n' "$drift"; else echo "  (live has no permissions block)"; fi

if [[ $assume_yes -eq 0 ]]; then
  if [[ ! -t 0 ]]; then
    echo "refusing without a terminal; re-run with --yes to apply" >&2
    exit 1
  fi
  read -r -p "replace live permissions with repo? [y/N] " answer
  [[ "$answer" == [yY] ]] || { echo "aborted; live unchanged"; exit 1; }
fi

# Superset/Orca and Claude Code itself write this file while sessions run.
# Build the result from one snapshot and refuse to install it if live moved
# on in the meantime; otherwise their writes would be silently reverted.
# A write landing between the final cksum and mv is still lost: no lock is
# shared with those writers. The per-run backup is the recovery path.
backup="$(mktemp "$LIVE.bak-$(date +%Y%m%d%H%M%S)-XXXXXX")"
cp -p "$LIVE" "$backup"
before="$(cksum < "$backup")"
tmp="$(mktemp "$(dirname "$LIVE")/.settings.json.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
cp -p "$backup" "$tmp"
jq --slurpfile r "$REPO" '.permissions = $r[0].permissions' "$backup" > "$tmp"
if [[ "$(cksum < "$LIVE")" != "$before" ]]; then
  echo "live settings changed during sync; nothing written, re-run" >&2
  exit 1
fi
mv "$tmp" "$LIVE"
trap - EXIT

echo "synced permissions (backup: $backup)"
