#!/usr/bin/env bash
set -euo pipefail

# @raycast.schemaVersion 1
# @raycast.title AeroSpace Reassign Windows
# @raycast.mode silent
# @raycast.packageName AeroSpace
# @raycast.icon 🪟
# @raycast.description 全ウィンドウに on-window-detected のルールを再適用し、割り当て先のワークスペースへ戻す
# @raycast.author takeuchi-shogo

# Raycast は login shell を通さないので aerospace / zed のある Homebrew の bin を足す。
export PATH="/opt/homebrew/bin:$PATH"

aerospace run-callback --for-every-window on-window-detected
echo "全ウィンドウを定位置へ戻した"
