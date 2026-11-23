#!/usr/bin/env bash
set -euo pipefail

# @raycast.schemaVersion 1
# @raycast.title AeroSpace Restart
# @raycast.mode silent
# @raycast.packageName AeroSpace
# @raycast.icon 🪟
# @raycast.description AeroSpace を終了して起動し直す
# @raycast.author takeuchi-shogo

# Raycast は login shell を通さないので aerospace / zed のある Homebrew の bin を足す。
export PATH="/opt/homebrew/bin:$PATH"

# 応答しないときにも効くよう quit ではなく kill する。起動していなければ pkill は 1 を返すだけなので無視する。
pkill -x AeroSpace || true
for _ in {1..20}; do
  pgrep -x AeroSpace >/dev/null || break
  sleep 0.1
done
open -a AeroSpace
echo "AeroSpace を再起動した"
