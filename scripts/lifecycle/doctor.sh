#!/usr/bin/env bash
# scripts/lifecycle/doctor.sh — dotfiles setup health check
#
# Usage: doctor.sh [binary|nix|hook|brew|all]
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

CATEGORY: binary | nix | hook | brew | all (default)

Read-only setup health check. Exits 1 if any FAIL is reported.
Spec: docs/specs/2026-05-13-setup-doctor.md
EOF
}

main() {
  case "${1:-all}" in
    binary)    check_binary ;;
    nix)       check_nix ;;
    hook)      check_hook ;;
    brew)      check_brew ;;
    all)       check_binary; check_nix; check_hook; check_brew ;;
    -h|--help) usage; exit 0 ;;
    *)         usage; exit 2 ;;
  esac
  echo
  echo "Summary: FAIL=$FAIL_COUNT WARN=$WARN_COUNT OK=$OK_COUNT"
  [[ $FAIL_COUNT -gt 0 ]] && exit 1
  exit 0
}

main "$@"
