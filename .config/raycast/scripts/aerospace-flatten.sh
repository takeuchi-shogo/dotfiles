#!/usr/bin/env bash
set -euo pipefail

# @raycast.schemaVersion 1
# @raycast.title AeroSpace Flatten Workspace
# @raycast.mode silent
# @raycast.packageName AeroSpace
# @raycast.icon 🪟
# @raycast.description フォーカス中のワークスペースの入れ子を崩し、サイズを均等にする
# @raycast.author takeuchi-shogo

# Raycast は login shell を通さないので aerospace / zed のある Homebrew の bin を足す。
export PATH="/opt/homebrew/bin:$PATH"

aerospace flatten-workspace-tree
aerospace balance-sizes
echo "レイアウトを平らにした"
