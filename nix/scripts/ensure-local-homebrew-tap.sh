#!/usr/bin/env bash
# Ensure nix/homebrew is a git repository so `brew tap ... clone_target` can clone it.
# Parent repo tracks Casks/*.rb; nested .git is gitignored and recreated here.
set -euo pipefail

TAP_DIR="${TAP_DIR:-$HOME/dotfiles/nix/homebrew}"

if [[ ! -d "$TAP_DIR/Casks" ]]; then
  echo "ensure-local-homebrew-tap: missing $TAP_DIR/Casks" >&2
  exit 1
fi

if [[ ! -d "$TAP_DIR/.git" ]]; then
  git -C "$TAP_DIR" init
  git -C "$TAP_DIR" -c user.email=dotfiles@local -c user.name=dotfiles add -A
  git -C "$TAP_DIR" -c user.email=dotfiles@local -c user.name=dotfiles \
    commit -m "local homebrew tap" >/dev/null
  echo "ensure-local-homebrew-tap: initialized $TAP_DIR"
  exit 0
fi

git -C "$TAP_DIR" -c user.email=dotfiles@local -c user.name=dotfiles add -A
if ! git -C "$TAP_DIR" diff --cached --quiet; then
  git -C "$TAP_DIR" -c user.email=dotfiles@local -c user.name=dotfiles \
    commit -m "update local homebrew tap" >/dev/null
  echo "ensure-local-homebrew-tap: committed updates in $TAP_DIR"
else
  echo "ensure-local-homebrew-tap: up to date ($TAP_DIR)"
fi
