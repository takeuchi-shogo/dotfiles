#!/usr/bin/env bash
# Phase B1 Step 1: Brewfile 各エントリの nixpkgs 在庫確認。
# 標準出力に markdown table を出す。stderr に進捗。
set -euo pipefail

cd "$(dirname "$0")/../.."

# brew name | nixpkgs attribute のマッピング (brew名と nixpkgs attribute が違うものは明示)
declare -a CLI_ENTRIES=(
  # "brew-name|nixpkgs-attr|note"
  "git|git|"
  "neovim|neovim|"
  "sheldon|sheldon|"
  "starship|starship|"
  "fzf|fzf|"
  "lua|lua|lua5_4 or lua5_1 variant があるので要確認"
  "ripgrep|ripgrep|"
  "bat|bat|"
  "eza|eza|"
  "zoxide|zoxide|"
  "atuin|atuin|"
  "git-delta|delta|name 差分"
  "dust|du-dust|name 差分"
  "yazi|yazi|"
  "fd|fd|"
  "tree-sitter-cli|tree-sitter|name 差分の可能性"
  "grep|gnugrep|name 差分"
  "gh|gh|"
  "mise|mise|"
  "uv|uv|"
  "borders|_NO_|FelixKratz/formulae tap-only"
  "nb|nb|"
  "direnv|direnv|"
  "k1LoW/tap/mo|_NO_|k1LoW tap-only"
)

declare -a CASK_ENTRIES=(
  "wezterm|wezterm|CLI もあるが GUI app は cask"
  "ghostty|ghostty|newer, nixpkgs に入った可能性あり"
  "aerospace|_NO_|nikitabobko/tap"
  "hammerspoon|_NO_|macOS GUI / no nixpkgs"
  "karabiner-elements|_NO_|macOS GUI / no nixpkgs"
  "sf-symbols|_NO_|Apple font browser / no nixpkgs"
  "macskk|_NO_|sandbox 制約 / brew 固定"
  "jordanbaird-ice|_NO_|macOS GUI / no nixpkgs"
  "raycast|_NO_|macOS GUI / no nixpkgs"
)

check_nixpkgs() {
  local attr="$1"
  if [ "$attr" = "_NO_" ]; then
    echo "N/A|N/A"
    return
  fi
  local desc
  desc=$(/nix/var/nix/profiles/default/bin/nix eval --raw "nixpkgs#${attr}.meta.description" 2>/dev/null | head -c 60 || true)
  if [ -z "$desc" ]; then
    echo "NOT_FOUND|NOT_FOUND"
  else
    local name
    name=$(/nix/var/nix/profiles/default/bin/nix eval --raw "nixpkgs#${attr}.name" 2>/dev/null || echo "unknown")
    echo "${name}|${desc}"
  fi
}

echo "# Phase B1 Brewfile Inventory ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
echo
echo "自動生成: \`nix/scripts/brewfile-inventory.sh\`"
echo

echo "## CLI (\`brew \"<name>\"\`)"
echo
echo "| brew name | nixpkgs attr | nixpkgs name | description | classification |"
echo "|---|---|---|---|---|"

for entry in "${CLI_ENTRIES[@]}"; do
  IFS='|' read -r brew_name attr note <<< "$entry"
  echo "  checking $brew_name..." >&2
  read -r pkg_name pkg_desc <<< "$(check_nixpkgs "$attr" | tr '|' ' ')"
  if [ "$attr" = "_NO_" ]; then
    class="brew-retain (tap-only)"
  elif [ "$pkg_name" = "NOT_FOUND" ]; then
    class="NOT_FOUND — brew-retain or needs manual search"
  else
    # tier assignment heuristic
    case "$brew_name" in
      ripgrep|bat|eza|fd|dust|git-delta|yazi|fzf|zoxide|tree-sitter-cli|gh|grep|neovim|lua) class="tier1-cli" ;;
      atuin|uv|nb|k1LoW/tap/mo) class="tier2-tooling" ;;
      git) class="tier2-tooling (gitconfig symlink 要注意)" ;;
      sheldon|starship|mise|direnv) class="bootstrap (最後に移植)" ;;
      *) class="tier2-tooling" ;;
    esac
  fi
  echo "| \`$brew_name\` | \`$attr\` | $pkg_name | $pkg_desc | $class |"
done

echo
echo "## Cask (\`cask \"<name>\"\`)"
echo
echo "| cask name | nixpkgs attr | description | classification |"
echo "|---|---|---|---|"

for entry in "${CASK_ENTRIES[@]}"; do
  IFS='|' read -r cask_name attr note <<< "$entry"
  echo "  checking cask $cask_name..." >&2
  if [ "$attr" = "_NO_" ]; then
    echo "| \`$cask_name\` | N/A | $note | tier3-cask (brew retain, nix-darwin.homebrew.casks で宣言) |"
  else
    read -r pkg_name pkg_desc <<< "$(check_nixpkgs "$attr" | tr '|' ' ')"
    if [ "$pkg_name" = "NOT_FOUND" ]; then
      echo "| \`$cask_name\` | \`$attr\` | (nixpkgs NOT_FOUND) | tier3-cask |"
    else
      echo "| \`$cask_name\` | \`$attr\` | $pkg_desc | tier3-cask (cask 維持 / $note) |"
    fi
  fi
done

echo
echo "## Taps"
echo
echo "- \`FelixKratz/formulae\` → borders (tap-only)"
echo "- \`k1LoW/tap\` → mo (tap-only)"
echo "- \`nikitabobko/tap\` → aerospace (tap-only cask)"
echo
echo "→ nix-darwin.homebrew.taps に宣言: \`[ \"FelixKratz/formulae\" \"k1LoW/tap\" \"nikitabobko/tap\" ]\`"

echo
echo "## Fonts"
echo
echo "- \`font-hackgen-nerd\` / \`font-hack-nerd-font\` → **Phase B1 対象外** (Phase C 以降、macOS font cache の罠回避)"
