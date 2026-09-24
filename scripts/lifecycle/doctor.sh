#!/usr/bin/env bash
# scripts/lifecycle/doctor.sh — dotfiles setup health check
#
# Usage: doctor.sh [binary|nix|hook|settings|brew|all]
# Output: [CATEGORY] SEVERITY: message (hint)
# Exit:   0 if no FAIL, 1 if any FAIL
#
# Spec:         docs/specs/2026-05-13-setup-doctor.md
# Requirements: .config/claude/references/setup-requirements.md
#
# Design: read-only. Hook checks do NOT execute hook commands (would mutate state).
# All external calls wrapped in `timeout 5s` to prevent stdin-hang.

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REQ_FILE="${SETUP_DOCTOR_REQ_FILE:-$ROOT_DIR/.config/claude/references/setup-requirements.md}"
SETTINGS_FILE="${SETUP_DOCTOR_SETTINGS:-$HOME/.claude/settings.json}"
NIX_FILE="${SETUP_DOCTOR_NIX_FILE:-$ROOT_DIR/nix/darwin/default.nix}"
HOSTNAME_OVERRIDE="${SETUP_DOCTOR_HOSTNAME:-}"

FAIL_COUNT=0
WARN_COUNT=0
OK_COUNT=0

# Portable timeout: GNU coreutils `timeout` is not on stock macOS, and
# `gtimeout` only exists if `brew install coreutils` was run. Fall back
# to running the command without a timeout — better than swallowing the
# probe via `|| true` and silently degrading FAILs to WARNs.
if command -v timeout >/dev/null 2>&1; then
  _to() { timeout "$@"; }
elif command -v gtimeout >/dev/null 2>&1; then
  _to() { gtimeout "$@"; }
else
  _to() { shift; "$@"; }   # drop the duration arg, run directly
fi

emit() {
  local cat="$1" sev="$2" msg="$3" hint="${4:-}"
  if [[ -n "$hint" ]]; then
    printf "[%-7s] %s: %s (%s)\n" "$cat" "$sev" "$msg" "$hint"
  else
    printf "[%-7s] %s: %s\n" "$cat" "$sev" "$msg"
  fi
  case "$sev" in
    FAIL) FAIL_COUNT=$((FAIL_COUNT + 1)) ;;
    WARN) WARN_COUNT=$((WARN_COUNT + 1)) ;;
    OK|SKIP) OK_COUNT=$((OK_COUNT + 1)) ;;
  esac
}

# version_lt A B → exit 0 if A < B (semver), 1 otherwise
version_lt() {
  [[ "$1" = "$2" ]] && return 1
  local lo
  lo=$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -1)
  [[ "$lo" = "$1" ]]
}

# Read fenced ```setup-requirements block from REQ_FILE, strip comments/blanks.
read_requirements() {
  awk '/^```setup-requirements$/{f=1; next} /^```/{f=0} f' "$REQ_FILE" \
    | grep -vE '^(#|$)'
}

check_binary() {
  while IFS=' ' read -r tier name min probe rest; do
    [[ -z "${tier:-}" ]] && continue
    # probe may contain spaces; rejoin
    [[ -n "$rest" ]] && probe="$probe $rest"
    local bin_path
    bin_path=$(command -v "$name" 2>/dev/null || true)
    if [[ -z "$bin_path" ]]; then
      case "$tier" in
        required)        emit binary FAIL "$name not found in PATH" "install: brew install $name" ;;
        recommended)     emit binary WARN "$name not installed (recommended)" "install: brew install $name" ;;
        bootstrap_gated) emit binary SKIP "$name unavailable (bootstrap-gated, run task nix:bootstrap)" ;;
      esac
      continue
    fi
    if [[ "$min" = "-" || -z "$probe" || "$probe" = "-" ]]; then
      emit binary OK "$name found at $bin_path"
      continue
    fi
    local cmd="${probe//\{bin\}/$name}"
    local ver
    ver=$(_to 5 bash -c "$cmd"</dev/null 2>/dev/null || true)
    if [[ -z "$ver" ]]; then
      emit binary WARN "$name version probe failed" "cmd: $cmd"
      continue
    fi
    if version_lt "$ver" "$min"; then
      emit binary FAIL "$name $ver found, requires >= $min" "run: brew upgrade $name"
    else
      emit binary OK "$name $ver (>= $min)"
    fi
  done < <(read_requirements)
}

check_nix() {
  local drb=/run/current-system/sw/bin/darwin-rebuild
  if [[ ! -x "$drb" ]]; then
    emit nix SKIP "$drb not found" "run: task nix:bootstrap"
    return
  fi
  emit nix OK "darwin-rebuild present at $drb"
  local host="${HOSTNAME_OVERRIDE:-$(hostname -s 2>/dev/null || hostname)}"
  case "$host" in
    MacBookPro|MacBookPro.local)        emit nix OK   "hostname=$host matches profile=private" ;;
    MacBookPro-work|MacBookPro-work.*)  emit nix OK   "hostname=$host matches profile=work" ;;
    *)                                  emit nix WARN "hostname=$host does not match private/work" "verify task nix:switch PROFILE=<...>" ;;
  esac
}

check_hook() {
  if [[ ! -f "$SETTINGS_FILE" ]]; then
    emit hook FAIL "$SETTINGS_FILE missing" "run: task validate-symlinks"
    return
  fi
  if ! command -v jq >/dev/null 2>&1; then
    emit hook SKIP "jq not installed (required to parse settings.json)"
    return
  fi
  # Resolve hook commands without execution. For each command we walk tokens
  # (whitespace-split) and pick the FIRST one that resolves to an existing path or
  # PATH entry — skipping env-assignments, quoted-string fragments, and shell
  # metacharacter prefixes. Bash word-split doesn't handle quoted spaces; that's
  # why we skip noisy tokens (`*"*`, `*}*`) and keep walking until something
  # resolves (e.g., `bash`, `python3`, an absolute path).
  # Verify settings.json parses before iterating; otherwise silent OK hides
  # the case where Claude itself cannot load the hook config.
  local jq_err
  jq_err=$(jq empty "$SETTINGS_FILE" 2>&1) || {
    emit hook FAIL "settings.json is not valid JSON" "${jq_err%%$'\n'*}"
    return
  }
  local unresolved=0 total=0
  while IFS= read -r cmd; do
    [[ -z "$cmd" ]] && continue
    total=$((total + 1))
    local resolved="" t
    for t in $cmd; do
      case "$t" in
        ""|*=*|*\"*|*\'*|*\}*|*\{*|\&\&|\|\|) continue ;;
      esac
      t="${t#\(}"; t="${t#\)}"; t="${t#\&}"
      [[ -z "$t" ]] && continue
      t="${t/#\~/$HOME}"
      t="${t//\$HOME/$HOME}"
      if [[ "$t" == */* ]]; then
        [[ -x "$t" || -f "$t" ]] && { resolved="$t"; break; }
      else
        command -v "$t" >/dev/null 2>&1 && { resolved="$t"; break; }
      fi
    done
    if [[ -z "$resolved" ]]; then
      emit hook FAIL "no resolvable executable in hook" "cmd: ${cmd:0:60}..."
      unresolved=$((unresolved + 1))
    fi
  done < <(jq -r '..|.command? // empty' "$SETTINGS_FILE" 2>/dev/null | sort -u)
  [[ $unresolved -eq 0 && $total -gt 0 ]] && emit hook OK "all $total hook commands resolve"
  # rtk hook claude subcommand recognition (read-only)
  if command -v rtk >/dev/null 2>&1; then
    if _to 5 rtk hook --help </dev/null 2>/dev/null | grep -qE '^[[:space:]]+claude([[:space:]]|$)'; then
      emit hook OK "rtk hook claude subcommand recognized"
    else
      emit hook FAIL "rtk hook claude subcommand missing" "run: brew upgrade rtk"
    fi
  fi
}

check_settings() {
  local repo_settings="${SETUP_DOCTOR_REPO_SETTINGS:-$ROOT_DIR/.config/claude/settings.json}"
  if [[ ! -f "$repo_settings" ]]; then
    emit settings SKIP "$repo_settings not found"
    return
  fi
  if [[ ! -f "$SETTINGS_FILE" ]]; then
    emit settings FAIL "$SETTINGS_FILE missing" "merge keys from $repo_settings"
    return
  fi
  if ! command -v jq >/dev/null 2>&1; then
    emit settings SKIP "jq not installed (required to parse settings.json)"
    return
  fi
  local f jq_err
  for f in "$repo_settings" "$SETTINGS_FILE"; do
    jq_err=$(jq empty "$f" 2>&1) || {
      emit settings FAIL "$f is not valid JSON" "${jq_err%%$'\n'*}"
      return
    }
  done
  # settings.json is deliberately outside home-manager (nix/home/default.nix):
  # Superset/Orca inject hooks into the live file at runtime, and symlinking it
  # would drop both the injection and `/model` changes. The cost of that choice
  # is that nothing keeps live and repo in sync, so the repo copy can go fully
  # inert without any visible symptom — skills and CLAUDE.md keep working via
  # their own symlinks while permissions, hooks and plugins silently vanish.
  #
  # Compare key PRESENCE only, never values: `/model`, `/config` toggles and
  # runtime injection all rewrite values legitimately, so a value diff is noise.
  #
  # Presence alone is not enough either — the live file has two owners. Claude
  # Code deletes keys as well as rewriting them (picking the default in `/model`
  # drops `model` entirely), so a plain "missing from live" rule fires on
  # ordinary use. Only the repo-owned keys below carry harness enforcement, and
  # runtime never writes them; those are the ones worth failing on. Anything
  # else missing is reported as WARN so it stays visible without crying wolf.
  local -r REPO_OWNED="permissions hooks env enabledPlugins extraKnownMarketplaces skillOverrides statusLine"
  local repo_keys live_keys missing extra
  repo_keys=$(jq -r 'keys[]' "$repo_settings" | sort)
  live_keys=$(jq -r 'keys[]' "$SETTINGS_FILE" | sort)
  missing=$(comm -23 <(printf '%s\n' "$repo_keys") <(printf '%s\n' "$live_keys"))
  extra=$(comm -13 <(printf '%s\n' "$repo_keys") <(printf '%s\n' "$live_keys"))
  if [[ -n "$missing" ]]; then
    local k soft=""
    while IFS= read -r k; do
      [[ -z "$k" ]] && continue
      if [[ " $REPO_OWNED " == *" $k "* ]]; then
        emit settings FAIL "repo-owned key '$k' absent from live settings" \
          "merge repo keys into $SETTINGS_FILE (nix-unmanaged by design)"
      else
        soft="$soft $k"
      fi
    done <<< "$missing"
    # One line for the soft set: a wholesale replacement drops ~16 of these at
    # once, and 16 identical WARNs bury the FAILs that actually matter.
    [[ -n "${soft// }" ]] && emit settings WARN "repo keys absent from live:${soft}" \
      "runtime may own these (/model, /config); harmless unless set deliberately"
  else
    emit settings OK "all $(printf '%s\n' "$repo_keys" | grep -c .) repo top-level keys present in live"
  fi
  if [[ -n "$extra" ]]; then
    emit settings OK "live-only keys (runtime-injected, expected): $(tr '\n' ' ' <<< "$extra")"
  fi
  check_settings_permissions "$repo_settings"
}

# permissions is the one repo-owned key whose VALUES are safe to compare:
# runtime never writes it ("don't ask again" lands in the per-repo
# settings.local.json), and Superset/Orca inject hooks only. So any value
# difference is an unsynced edit — e.g. live missing ask rules that fence an
# allow like `pnpm *`, which lets `pnpm add` run unprompted.
check_settings_permissions() {
  local repo_settings="$1"
  if ! jq -e 'has("permissions")' "$repo_settings" >/dev/null 2>&1; then
    emit settings FAIL "repo settings has no permissions block" "$repo_settings"
    return
  fi
  jq -e 'has("permissions")' "$SETTINGS_FILE" >/dev/null 2>&1 || return
  local f side ptype
  for side in repo live; do
    f="$repo_settings"; [[ $side == live ]] && f="$SETTINGS_FILE"
    ptype=$(jq -r '.permissions | type' "$f")
    if [[ "$ptype" != "object" ]]; then
      emit settings FAIL "permissions is not an object in $side settings ($ptype)" \
        "task claude:settings:sync-permissions"
      return
    fi
  done
  # Validate rule tiers per side, not by comparison: two identical malformed
  # values (ask: null on both) would otherwise compare equal and pass.
  local bad tier ttype malformed=0
  for side in repo live; do
    f="$repo_settings"; [[ $side == live ]] && f="$SETTINGS_FILE"
    bad=$(jq -r '.permissions | to_entries[]
      | select(.key | IN("allow", "ask", "deny", "additionalDirectories"))
      | select(.value | type != "array") | "\(.key)\t\(.value | type)"' "$f")
    while IFS=$'\t' read -r tier ttype; do
      [[ -z "$tier" ]] && continue
      emit settings FAIL "permissions.$tier is not an array in $side settings ($ttype)" \
        "task claude:settings:sync-permissions"
      malformed=1
    done <<< "$bad"
  done
  [[ $malformed -eq 1 ]] && return
  # An absent key and an empty array mean the same rule set (explicit null does
  # not: Claude Code may reject it); any other type
  # difference (string vs array) is reported as-is rather than fed to `-`,
  # which would error and leave $drift empty — i.e. a false "match".
  local drift jq_err key repo_side live_side
  if ! drift=$(jq -rn --slurpfile r "$repo_settings" --slurpfile l "$SETTINGS_FILE" '
    ($r[0].permissions) as $rp | ($l[0].permissions) as $lp
    | ([$rp, $lp] | map(keys) | add | unique)[] as $k
    | ($rp | has($k)) as $ha | ($lp | has($k)) as $hb
    | $rp[$k] as $a | $lp[$k] as $b
    | (if ($ha | not) and ($b | type) == "array" then [] else $a end) as $a
    | (if ($hb | not) and ($a | type) == "array" then [] else $b end) as $b
    | if $ha != $hb and ($a | type) != "array" and ($b | type) != "array" then
        [$k, "repo: \(if $ha then $a | tojson else "absent" end)",
             "live: \(if $hb then $b | tojson else "absent" end)"] | join("\t")
      elif ($a | type) != ($b | type) and (($a | type) == "array" or ($b | type) == "array") then
        [$k, "repo: \($a | type)", "live: \($b | type)"] | join("\t")
      elif ($a | type) == "array" then
        ($a - $b) as $miss | ($b - $a) as $more
        | select(($miss | length) > 0 or ($more | length) > 0)
        | [$k, "repo-only: \(if ($miss | length) > 0 then $miss | map(tostring) | join(", ") else "-" end)",
               "live-only: \(if ($more | length) > 0 then $more | map(tostring) | join(", ") else "-" end)"]
          | join("\t")
      elif $a != $b then [$k, "repo: \($a | tojson)", "live: \($b | tojson)"] | join("\t")
      else empty end' 2>&1); then
    emit settings FAIL "permissions could not be compared" "${drift%%$'\n'*}"
    return
  fi
  if [[ -z "$drift" ]]; then
    emit settings OK "permissions match repo ($(jq -r '.permissions | "allow=\(.allow // [] | length) ask=\(.ask // [] | length) deny=\(.deny // [] | length)"' "$repo_settings"))"
    return
  fi
  while IFS=$'\t' read -r key repo_side live_side; do
    emit settings FAIL "permissions.$key drifted from repo ($repo_side; $live_side)" \
      "task claude:settings:sync-permissions"
  done <<< "$drift"
}

check_brew() {
  if [[ ! -f "$NIX_FILE" ]]; then
    emit brew SKIP "$NIX_FILE not found"
    return
  fi
  if ! command -v brew >/dev/null 2>&1; then
    emit brew SKIP "brew not in PATH"
    return
  fi
  # Extract brews and taps from nix file. Both `"name"` (string) and
  # `{ name = "name"; args = [...]; }` (attrset) forms are supported for brews.
  # Taps are always plain strings in `homebrew.taps`.
  _nix_list() {
    local key="$1"
    awk -v key="$key" '
      $0 ~ "(^|[^a-zA-Z_])" key "[[:space:]]*=[[:space:]]*\\["{in_b=1; next}
      in_b && /\]/{in_b=0}
      in_b && /name[[:space:]]*=[[:space:]]*"[^"]+"/{
        s=$0; sub(/.*name[[:space:]]*=[[:space:]]*"/, "", s); sub(/".*/, "", s); print s; next
      }
      in_b && /^[[:space:]]*"[^"]+"/{
        s=$0; sub(/^[[:space:]]*"/, "", s); sub(/".*/, "", s); print s
      }
    ' "$NIX_FILE" | sort -u
  }
  local brews taps
  brews=$(_nix_list "brews")
  taps=$(_nix_list "taps")
  if [[ -z "$brews" && -z "$taps" ]]; then
    emit brew WARN "no brews or taps declared in $NIX_FILE"
    return
  fi
  local installed installed_taps missing_b="" missing_t=""
  installed=$(_to 10 brew list --formula 2>/dev/null | sort -u || true)
  installed_taps=$(_to 10 brew tap 2>/dev/null | sort -u || true)
  while IFS= read -r b; do
    [[ -z "$b" ]] && continue
    grep -qx "$b" <<< "$installed" || missing_b="$missing_b $b"
  done <<< "$brews"
  while IFS= read -r t; do
    [[ -z "$t" ]] && continue
    grep -qix "$t" <<< "$installed_taps" || missing_t="$missing_t $t"
  done <<< "$taps"
  if [[ -z "${missing_b// }" && -z "${missing_t// }" ]]; then
    local nb nt
    nb=$(printf '%s\n' "$brews" | grep -c . || true)
    nt=$(printf '%s\n' "$taps"  | grep -c . || true)
    emit brew OK "all declared brews ($nb) and taps ($nt) installed"
  else
    for b in $missing_b; do
      emit brew FAIL "$b declared in nix.brews but not installed" "run: task nix:switch"
    done
    for t in $missing_t; do
      emit brew FAIL "$t declared in nix.taps but not tapped" "run: task nix:switch"
    done
  fi
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [CATEGORY]

CATEGORY: binary | nix | hook | settings | brew | all (default)

Read-only setup health check. Exits 1 if any FAIL is reported.
Spec: docs/specs/2026-05-13-setup-doctor.md
EOF
}

main() {
  case "${1:-all}" in
    binary)    check_binary ;;
    nix)       check_nix ;;
    hook)      check_hook ;;
    settings)  check_settings ;;
    brew)      check_brew ;;
    all)       check_binary; check_nix; check_hook; check_settings; check_brew ;;
    -h|--help) usage; exit 0 ;;
    *)         usage; exit 2 ;;
  esac
  echo
  echo "Summary: FAIL=$FAIL_COUNT WARN=$WARN_COUNT OK=$OK_COUNT"
  [[ $FAIL_COUNT -gt 0 ]] && exit 1
  exit 0
}

main "$@"
