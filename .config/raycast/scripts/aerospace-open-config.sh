#!/usr/bin/env bash
set -euo pipefail

# @raycast.schemaVersion 1
# @raycast.title AeroSpace Open Config
# @raycast.mode silent
# @raycast.packageName AeroSpace
# @raycast.icon 🪟
# @raycast.description aerospace.toml を Zed で開く
# @raycast.author takeuchi-shogo

# Raycast は login shell を通さないので aerospace / zed のある Homebrew の bin を足す。
export PATH="/opt/homebrew/bin:$PATH"

zed "$HOME/dotfiles/.config/aerospace/aerospace.toml"
