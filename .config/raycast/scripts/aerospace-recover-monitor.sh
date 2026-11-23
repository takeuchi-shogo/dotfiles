#!/usr/bin/env bash
set -euo pipefail

# @raycast.schemaVersion 1
# @raycast.title AeroSpace Recover Monitor
# @raycast.mode silent
# @raycast.packageName AeroSpace
# @raycast.icon 🪟
# @raycast.description モニタを外した後、画面外に残ったウィンドウを描き直す (モニタ 1 枚のときだけ動く)
# @raycast.author takeuchi-shogo

# Raycast は login shell を通さないので aerospace / zed のある Homebrew の bin を足す。
export PATH="/opt/homebrew/bin:$PATH"

# on-focused-monitor-changed に登録した flatten-on-single-monitor.sh を手動で走らせる。
aerospace run-callback on-focused-monitor-changed
echo "モニタ復旧を実行した (ログ: ~/Library/Logs/aerospace-monitor-change.log)"
