#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Validate TOML and JSON"
python3 - <<'PY'
import json
import pathlib
import tomllib

toml_files = [
    ".codex/config.toml",
    ".config/aerospace/aerospace.toml",
    ".config/sheldon/plugins.toml",
    ".config/starship.toml",
]

json_files = [
    ".config/claude/settings.json",
    ".config/karabiner/karabiner.json",
    ".config/nvim/lazyvim.json",
]

for path_str in toml_files:
    path = pathlib.Path(path_str)
    tomllib.loads(path.read_text())
    print(f"ok  {path_str}")

for path_str in json_files:
    path = pathlib.Path(path_str)
    json.loads(path.read_text())
    print(f"ok  {path_str}")
PY

echo "==> Validate shell scripts"
while IFS= read -r file; do
  bash -n "$file"
  echo "ok  $file"
done < <(find .bin -type f -name '*.sh' | sort)

bash -n .config/claude/statusline.sh
echo "ok  .config/claude/statusline.sh"

for file in .config/sketchybar/icon_map.sh .config/sketchybar/icon_updater.sh; do
  bash -n "$file"
  echo "ok  $file"
done

echo "==> Validate zsh files"
while IFS= read -r file; do
  zsh -n "$file"
  echo "ok  $file"
done < <(find .config/zsh -type f -name '*.zsh' | sort)

echo "==> Validate Lua syntax"
while IFS= read -r file; do
  luac -p "$file"
  echo "ok  $file"
done < <(find .config/nvim .config/sketchybar .config/wezterm -type f -name '*.lua' | sort)

echo "==> Validate WezTerm config load"
wezterm --config-file .config/wezterm/wezterm.lua show-keys >/dev/null
echo "ok  .config/wezterm/wezterm.lua"
