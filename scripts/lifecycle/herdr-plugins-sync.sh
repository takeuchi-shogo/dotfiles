#!/usr/bin/env bash
# scripts/lifecycle/herdr-plugins-sync.sh
#
# Materialize the declarative herdr plugin list (.config/herdr/plugins.txt,
# one <owner>/<repo> per line) onto this machine via `herdr plugin install`.
# Idempotent: safe to re-run.
#
# Why this exists: plugin payloads are fetched + built from GitHub into
# ~/.config/herdr/plugins/, which is machine-local and NOT vendored by nix
# (config.toml alone is symlinked — see nix/home/default.nix block 6). A
# fresh machine needs this step to materialize plugins declared here.
#
# Usage:
#   herdr-plugins-sync.sh install   # install declared plugins missing locally (default)
#   herdr-plugins-sync.sh check     # read-only: report declared-but-missing plugins (exit 1 if any)
#
# Source of truth: .config/herdr/plugins.txt (owner/repo, # comments and blank lines ignored)
set -uo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MANIFEST="$DOTFILES_DIR/.config/herdr/plugins.txt"
MODE="${1:-install}"

c_green=$'\033[0;32m'; c_yellow=$'\033[1;33m'; c_red=$'\033[0;31m'; c_reset=$'\033[0m'
log()  { echo "${c_green}[herdr-plugins]${c_reset} $*"; }
warn() { echo "${c_yellow}[herdr-plugins] WARN:${c_reset} $*" >&2; }
err()  { echo "${c_red}[herdr-plugins] ERROR:${c_reset} $*" >&2; }

command -v jq >/dev/null 2>&1 || { err "jq required"; exit 2; }
if [ ! -f "$MANIFEST" ]; then
  err "manifest not found: $MANIFEST"
  exit 2
fi

mapfile -t DECLARED < <(grep -vE '^\s*(#|$)' "$MANIFEST")

if [ "${#DECLARED[@]}" -eq 0 ]; then
  warn "no plugins declared in $MANIFEST — nothing to do"
  exit 0
fi

if ! command -v herdr >/dev/null 2>&1; then
  warn "herdr CLI not installed — skipping"
  exit 0
fi

# owner/repo of currently installed plugins (empty if server isn't running yet —
# install still proceeds per-entry below, tolerant of a fresh, never-launched machine).
declare -A installed=()
while IFS= read -r pair; do
  [ -n "$pair" ] && installed["$pair"]=1
done < <(herdr plugin list --json 2>/dev/null | jq -r '.result.plugins[]? | "\(.source.owner)/\(.source.repo)"' 2>/dev/null)

if [ "$MODE" = "check" ]; then
  missing=0
  for entry in "${DECLARED[@]}"; do
    if [ -n "${installed[$entry]:-}" ]; then
      echo "ok      $entry"
    else
      echo "MISSING $entry"
      missing=$((missing + 1))
    fi
  done
  echo ""
  echo "[summary] declared=${#DECLARED[@]}, missing=$missing"
  [ "$missing" -eq 0 ]
  exit $?
fi

# install mode
installed_ok=0; skipped=0; failed=0
for entry in "${DECLARED[@]}"; do
  if [ -n "${installed[$entry]:-}" ]; then
    skipped=$((skipped + 1))
    continue
  fi
  log "install: $entry"
  if herdr plugin install "$entry" --yes >/dev/null 2>&1; then
    installed_ok=$((installed_ok + 1))
  else
    warn "  failed to install $entry (herdr server not running? see: herdr status server)"
    failed=$((failed + 1))
  fi
done

echo ""
log "done — installed=$installed_ok, already-present=$skipped, failed=$failed"
exit 0
