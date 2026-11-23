#!/usr/bin/env bash
set -euo pipefail

# @raycast.schemaVersion 1
# @raycast.title AeroSpace Reload Config
# @raycast.mode silent
# @raycast.packageName AeroSpace
# @raycast.icon 🪟
# @raycast.description aerospace.toml を再読み込みする
# @raycast.author takeuchi-shogo

# Raycast は login shell を通さないので aerospace / zed のある Homebrew の bin を足す。
export PATH="/opt/homebrew/bin:$PATH"

aerospace reload-config
echo "設定を再読み込みした"
