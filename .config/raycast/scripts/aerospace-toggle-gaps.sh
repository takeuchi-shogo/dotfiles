#!/usr/bin/env bash
set -euo pipefail

# @raycast.schemaVersion 1
# @raycast.title AeroSpace Toggle Gaps
# @raycast.mode silent
# @raycast.packageName AeroSpace
# @raycast.icon 🪟
# @raycast.description ウィンドウ間の余白を 3px と 0 で切り替える (aerospace.toml を書き換える)
# @raycast.author takeuchi-shogo

# Raycast は login shell を通さないので aerospace / zed のある Homebrew の bin を足す。
export PATH="/opt/homebrew/bin:$PATH"

config="$HOME/dotfiles/.config/aerospace/aerospace.toml"
gaps_on=3 # aerospace.toml の [gaps] の既定値

# AeroSpace には実行時に gaps を変えるコマンドが無いので、toml の [gaps] を書き換えて reload する。
current=$(awk '/^\[gaps\]/ {in_gaps=1; next} /^\[/ {in_gaps=0} in_gaps && $1 == "inner.horizontal" {print $3; exit}' "$config")
if [[ -z "$current" ]]; then
  echo "aerospace.toml の [gaps] に inner.horizontal が見つからない" >&2
  exit 1
fi
next=$([[ "$current" == 0 ]] && echo "$gaps_on" || echo 0)

perl -i -pe 's/=(\s*)\d+\s*$/=${1}'"$next"'\n/ if (/^\[gaps\]/ ... /^\[/) && !/^\s*#/' "$config"
aerospace reload-config
echo "gaps: ${current} → ${next} (dotfiles の aerospace.toml に差分が出る)"
