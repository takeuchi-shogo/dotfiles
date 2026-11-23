#!/usr/bin/env bash
set -euo pipefail

# @raycast.schemaVersion 1
# @raycast.title AeroSpace Toggle Enable
# @raycast.mode silent
# @raycast.packageName AeroSpace
# @raycast.icon 🪟
# @raycast.description タイリングを一時的に止める / 再開する
# @raycast.author takeuchi-shogo

# Raycast は login shell を通さないので aerospace / zed のある Homebrew の bin を足す。
export PATH="/opt/homebrew/bin:$PATH"

aerospace enable toggle
echo "AeroSpace の有効/無効を切り替えた"
