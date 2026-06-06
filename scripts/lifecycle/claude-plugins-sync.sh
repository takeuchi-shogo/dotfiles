#!/usr/bin/env bash
# scripts/lifecycle/claude-plugins-sync.sh
#
# Materialize the declarative Claude Code plugin/marketplace config from
# settings.json onto this machine. settings.json (`enabledPlugins` +
# `extraKnownMarketplaces`) is the single source of truth — this script only
# runs `claude plugin marketplace add` + `claude plugin install` to fetch the
# payloads that a fresh machine is missing. Idempotent: safe to re-run.
#
# Why this exists: skills are vendored into the repo (.config/claude/skills/,
# symlinked by nix), so they arrive with the clone. Plugins are NOT — their
# payloads live in ~/.claude/plugins/cache/ which is machine-local. Without
# this step a team member's clone enables plugins in settings.json that have
# no payload installed. See Taskfile `setup` / `claude:plugins`.
#
# Usage:
#   claude-plugins-sync.sh install   # add marketplaces + install enabled plugins (default)
#   claude-plugins-sync.sh check     # read-only: report declared-but-missing plugins (exit 1 if any)
#
# Source of truth: $CLAUDE_SETTINGS (default ~/.claude/settings.json)
#   - extraKnownMarketplaces.<name>.source → github repo | directory path
#   - enabledPlugins."<name>@<marketplace>" = true
#
# Built-in marketplaces (claude-plugins-official, claude-code-plugins) are not
# listed in extraKnownMarketplaces; they map to anthropics repos via the
# DEFAULT_MARKETPLACES table below. Plugins whose marketplace cannot be
# resolved (e.g. a stale entry pointing at an undefined marketplace) are
# warned and skipped — never fatal.
#
# Exit codes:
#   install: 0 always unless a hard dependency (jq) is missing → 2
#   check:   0 if nothing missing, 1 if declared plugins are not installed, 2 on dep error
set -uo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
INSTALLED="${CLAUDE_INSTALLED_PLUGINS:-$HOME/.claude/plugins/installed_plugins.json}"
MODE="${1:-install}"

# Built-in marketplaces not declared in extraKnownMarketplaces.
# name → github repo passed to `claude plugin marketplace add`.
declare -A DEFAULT_MARKETPLACES=(
  ["claude-plugins-official"]="anthropics/claude-plugins-official"
  ["claude-code-plugins"]="anthropics/claude-code"
)

c_green=$'\033[0;32m'; c_yellow=$'\033[1;33m'; c_red=$'\033[0;31m'; c_reset=$'\033[0m'
log()  { echo "${c_green}[plugins]${c_reset} $*"; }
warn() { echo "${c_yellow}[plugins] WARN:${c_reset} $*" >&2; }
err()  { echo "${c_red}[plugins] ERROR:${c_reset} $*" >&2; }

command -v jq >/dev/null 2>&1 || { err "jq required"; exit 2; }
if [ ! -f "$SETTINGS" ]; then
  err "settings.json not found: $SETTINGS"
  exit 2
fi

# Resolve a marketplace name to the <source> argument for `marketplace add`.
# Prints the source on success; prints nothing and returns 1 if unresolvable.
resolve_marketplace() {
  local name="$1" kind path repo
  kind=$(jq -r --arg n "$name" '.extraKnownMarketplaces[$n].source.source // empty' "$SETTINGS")
  case "$kind" in
    github)
      jq -r --arg n "$name" '.extraKnownMarketplaces[$n].source.repo' "$SETTINGS"
      return 0
      ;;
    directory)
      # The recorded path is absolute to the original machine. Rebase onto this
      # repo: directory marketplaces are vendored under .config/claude/marketplaces/.
      path="$DOTFILES_DIR/.config/claude/marketplaces/$name"
      if [ -d "$path" ]; then echo "$path"; return 0; fi
      return 1
      ;;
    "")
      repo="${DEFAULT_MARKETPLACES[$name]:-}"
      if [ -n "$repo" ]; then echo "$repo"; return 0; fi
      return 1
      ;;
  esac
  return 1
}

# Enabled plugins ("name@marketplace") where value is true.
mapfile -t ENABLED < <(
  jq -r '.enabledPlugins // {} | to_entries[] | select(.value == true) | .key' "$SETTINGS"
)

if [ "${#ENABLED[@]}" -eq 0 ]; then
  warn "no enabled plugins declared in $SETTINGS — nothing to do"
  exit 0
fi

# ----------------------------------------------------------------------------
# check mode: read-only diff of declared vs installed (by base plugin name, so
# a marketplace rename does not produce a false "missing").
# ----------------------------------------------------------------------------
if [ "$MODE" = "check" ]; then
  declare -A installed_base=()
  if [ -f "$INSTALLED" ]; then
    while IFS= read -r key; do
      installed_base["${key%@*}"]=1
    done < <(jq -r '.plugins // {} | keys[]' "$INSTALLED")
  fi
  missing=0
  for entry in "${ENABLED[@]}"; do
    base="${entry%@*}"; mp="${entry##*@}"
    if [ -n "${installed_base[$base]:-}" ]; then
      echo "ok      $entry"
    elif ! resolve_marketplace "$mp" >/dev/null; then
      echo "skip    $entry (marketplace '$mp' unresolvable — stale entry)"
    else
      echo "MISSING $entry"
      missing=$((missing + 1))
    fi
  done
  echo ""
  echo "[summary] declared=${#ENABLED[@]}, missing=$missing"
  [ "$missing" -eq 0 ]
  exit $?
fi

# ----------------------------------------------------------------------------
# install mode
# ----------------------------------------------------------------------------
if ! command -v claude >/dev/null 2>&1; then
  warn "Claude Code CLI not installed — skipping plugin install"
  exit 0
fi

# 1. Add every marketplace referenced by an enabled plugin (dedup, resolvable only).
declare -A seen_mp=()
for entry in "${ENABLED[@]}"; do
  mp="${entry##*@}"
  [ -n "${seen_mp[$mp]:-}" ] && continue
  seen_mp["$mp"]=1
  if ! source=$(resolve_marketplace "$mp"); then
    warn "marketplace '$mp' unresolvable — plugins from it will be skipped"
    continue
  fi
  log "marketplace add: $mp ($source)"
  if ! claude plugin marketplace add "$source" >/dev/null 2>&1; then
    log "  marketplace '$mp' already present (continuing)"
  fi
done

# 2. Install each enabled plugin (user scope is the CLI default).
installed_ok=0; skipped=0; failed=0
for entry in "${ENABLED[@]}"; do
  mp="${entry##*@}"
  if ! resolve_marketplace "$mp" >/dev/null; then
    skipped=$((skipped + 1))
    continue
  fi
  log "install: $entry"
  if claude plugin install "$entry" --scope user >/dev/null 2>&1; then
    installed_ok=$((installed_ok + 1))
  else
    warn "  failed to install $entry (already installed? see: claude plugin list)"
    failed=$((failed + 1))
  fi
done

echo ""
log "done — installed/ok=$installed_ok, skipped(unresolvable)=$skipped, failed=$failed"
exit 0
