#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

echo "==> Validate TOML and JSON"
python3 - <<'PY'
import json
import pathlib
import tomllib

toml_files = [
    ".codex/config.toml",
    ".config/aerospace/aerospace.toml",
    ".config/rtk/config.toml",
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

echo "==> Validate gate counts (deny-rules-catalog drift)"
python3 - <<'PY'
import json, re, pathlib, sys

perm = json.loads(pathlib.Path(".config/claude/settings.json").read_text())["permissions"]
live = {k: len(perm.get(k, [])) for k in ("deny", "allow", "ask")}

cat = pathlib.Path(".config/claude/references/deny-rules-catalog.md").read_text()
def declared(tier):
    m = re.search(rf"^## {tier} \((\d+)\)", cat, re.M)
    return int(m.group(1)) if m else None

errors = []
for tier, key in (("DENY", "deny"), ("ALLOW", "allow")):
    d = declared(tier)
    if d is None:
        errors.append(f"deny-rules-catalog.md に '## {tier} (N)' ヘッダがない")
    elif d != live[key]:
        errors.append(f"{tier}: 台帳宣言={d} / settings.json 実数={live[key]} (drift)")
if live["ask"] != 0:
    errors.append(f"ask tier が {live['ask']} 件出現。deny-rules-catalog.md に ASK セクションを追加して同期せよ")

if errors:
    print("NG  gate count drift:")
    for e in errors:
        print("    - " + e)
    print("    fix: deny-rules-catalog.md のヘッダ・合計・カテゴリ件数を settings.json に一致させる")
    sys.exit(1)
print(f"ok  deny-rules-catalog.md (deny={live['deny']} allow={live['allow']} ask={live['ask']})")
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
if have_cmd zsh; then
  while IFS= read -r file; do
    zsh -n "$file"
    echo "ok  $file"
  done < <(find .config/zsh -type f -name '*.zsh' | sort)
else
  echo "skip  zsh validation (zsh not found)"
fi

echo "==> Validate Lua syntax"
if have_cmd luac; then
  while IFS= read -r file; do
    luac -p "$file"
    echo "ok  $file"
  done < <(find .config/nvim .config/sketchybar .config/wezterm .hammerspoon -type f -name '*.lua' | sort)
else
  echo "skip  Lua validation (luac not found)"
fi

echo "==> Validate WezTerm config load"
if have_cmd wezterm; then
  wezterm --config-file .config/wezterm/wezterm.lua show-keys >/dev/null
  echo "ok  .config/wezterm/wezterm.lua"
else
  echo "skip  .config/wezterm/wezterm.lua (wezterm not found)"
fi
