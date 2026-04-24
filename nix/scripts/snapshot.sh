#!/usr/bin/env bash
# Phase 0+A Step 2/3: Nix pre/post install snapshot.
# Usage:
#   ./nix/scripts/snapshot.sh pre
#   ./nix/scripts/snapshot.sh post
set -euo pipefail

PHASE="${1:-pre}"
case "$PHASE" in
  pre|post) ;;
  *) echo "usage: $0 {pre|post}" >&2; exit 2 ;;
esac

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$REPO_ROOT/docs/plans/active/2026-04-24-phase-0a-${PHASE}-install-snapshot.txt"

{
  echo "# Phase 0+A ${PHASE}-install snapshot ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
  echo

  echo "## /etc/* shell profile files"
  for f in /etc/zshenv /etc/zshrc /etc/bashrc /etc/zprofile /etc/zsh/zshrc /etc/zsh/zshenv /etc/synthetic.conf; do
    echo "--- $f ---"
    sudo cat "$f" 2>/dev/null || echo "(not present)"
  done
  echo

  echo "## /etc/profile.d/"
  ls -la /etc/profile.d/ 2>/dev/null || echo "(not present)"
  echo

  echo "## PATH"
  echo "$PATH" | tr ':' '\n'
  echo

  echo "## home symlinks"
  for l in ~/.zshrc ~/.zshenv ~/.zprofile ~/.bashrc; do
    if [ -L "$l" ]; then
      printf '%s -> %s\n' "$l" "$(readlink "$l")"
    elif [ -e "$l" ]; then
      printf '%s (regular file)\n' "$l"
    else
      printf '%s (missing)\n' "$l"
    fi
  done
  echo

  echo "## macOS"
  sw_vers -productVersion
  echo

  echo "## Xcode CLT"
  xcode-select -p 2>&1 || true
  xcrun --show-sdk-path 2>&1 || true
  echo

  echo "## APFS volumes (nix-related)"
  diskutil apfs list 2>/dev/null | grep -i nix || echo "NO_NIX_VOLUME"
  echo

  echo "## Nix binary"
  command -v nix 2>&1 || echo "(not installed)"
  nix --version 2>&1 || true
} > "$OUT" 2>&1

echo "wrote: $OUT"
