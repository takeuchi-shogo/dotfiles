#!/usr/bin/env bash
# scripts/lifecycle/claude-settings-sync.sh
#
# Push repo-owned keys of .config/claude/settings.json into the live
# ~/.claude/settings.json, leaving every other key (hooks injected by
# Superset/Orca, model, autoMode, ...) untouched.
#
#   permissions  replaced wholesale (runtime never writes it)
#   MERGE_KEYS   repo entries merged in, repo wins per entry; live-only entries
#                are kept because `claude plugin install` writes them too.
#                Removing an entry from the repo does NOT remove it from live:
#                disable a plugin with `false`, drop a marketplace by hand.
#
# Why this exists: live settings.json is a real file, not a symlink (see
# doctor.sh check_settings), so repo edits never reach it on their own.
# `task doctor:settings` detects the drift; this script closes it.
#
# Usage:
#   claude-settings-sync.sh          # show drift, ask y/N on a terminal
#   claude-settings-sync.sh --yes    # show drift, apply without asking
#
# Without --yes and without a terminal it refuses: a permissions rewrite
# widens or narrows what the agent may run, so it must not happen unattended.
#
# Env: CLAUDE_SETTINGS_LIVE (default ~/.claude/settings.json)
#      CLAUDE_SETTINGS_REPO (default <repo>/.config/claude/settings.json)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# Keep in sync with check_settings_merge_keys in doctor.sh.
MERGE_KEYS='["enabledPlugins", "extraKnownMarketplaces", "skillOverrides"]'
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
# A merge key must be an object or absent on both sides. jq's `//` would turn
# null/false into {} and `+` errors on anything else, so refuse instead.
refuse_bad_merge_keys() {
  local f="$1" bad
  bad=$(jq -r --argjson ks "$MERGE_KEYS" '
    if type != "object" then "root is \(type)" else
      $ks[] as $k | select(has($k) and (.[$k] | type) != "object") | "\($k) is \(.[$k] | type)"
    end' "$f")
  [[ -z "$bad" ]] || { echo "$f: $bad; refusing to sync" >&2; exit 1; }
}
refuse_bad_merge_keys "$REPO"
refuse_bad_merge_keys "$LIVE"

# Repo entries win; live-only entries survive. A repo key with no entries
# still creates an empty key in live, matching doctor's presence check.
# shellcheck disable=SC2016  # jq program, not shell expansion
MERGE='reduce ($ks[] | select(. as $k | $r[0] | has($k))) as $k (.; .[$k] = ((.[$k] // {}) + $r[0][$k]))'

# Decide "in sync" with jq, not by grepping doctor: doctor reports a missing
# key on a different line than per-entry drift, and a grep miss reads as sync.
# permissions keeps doctor's order-insensitive comparison.
doctor_out=$(SETUP_DOCTOR_REPO_SETTINGS="$REPO" SETUP_DOCTOR_SETTINGS="$LIVE" \
  bash "$ROOT_DIR/scripts/lifecycle/doctor.sh" settings 2>&1 || true)
perm_drift=$(grep 'FAIL: .*permissions' <<< "$doctor_out" || true)
merge_in_sync=$(jq --slurpfile r "$REPO" --argjson ks "$MERGE_KEYS" ". == ($MERGE)" "$LIVE")
drift=$(grep -E 'FAIL: .*(permissions|enabledPlugins|extraKnownMarketplaces|skillOverrides)' <<< "$doctor_out" || true)
if [[ -z "$perm_drift" && "$merge_in_sync" == true ]] && jq -e 'has("permissions")' "$LIVE" >/dev/null; then
  echo "settings already in sync: $LIVE"
  exit 0
fi

echo "settings drift in $LIVE:"
if [[ -n "$drift" ]]; then printf '%s\n' "$drift"; else echo "  (live has no permissions block)"; fi

if [[ $assume_yes -eq 0 ]]; then
  if [[ ! -t 0 ]]; then
    echo "refusing without a terminal; re-run with --yes to apply" >&2
    exit 1
  fi
  read -r -p "apply repo settings to live? [y/N] " answer
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
# live may have changed since the check above; validate what we transform.
refuse_bad_merge_keys "$backup"
tmp="$(mktemp "$(dirname "$LIVE")/.settings.json.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
cp -p "$backup" "$tmp"
jq --slurpfile r "$REPO" --argjson ks "$MERGE_KEYS" ".permissions = \$r[0].permissions | $MERGE" "$backup" > "$tmp"
if [[ "$(cksum < "$LIVE")" != "$before" ]]; then
  echo "live settings changed during sync; nothing written, re-run" >&2
  exit 1
fi
mv "$tmp" "$LIVE"
trap - EXIT

echo "synced settings (backup: $backup)"
if grep -qE 'FAIL: (enabledPlugins|extraKnownMarketplaces)' <<< "$drift"; then
  echo "plugins changed; install them with: task claude:plugins"
fi
