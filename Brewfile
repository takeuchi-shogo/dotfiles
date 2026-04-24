# Phase B1 partial-complete 時点での Brewfile:
#   - CLI: Tier 1 (14) + Tier 2 (3) は nix/home/default.nix に移動済み
#   - Cask 9 + tap 3 + brews 2 (borders, mo) は nix/darwin/default.nix の homebrew module 経由
#   - Bootstrap 5 は Phase B1.5 で再挑戦 (direnv checkPhase hang / overrideAttrs cache miss)
#   - Font は Phase C 以降

# Bootstrap (Phase B1.5 で nix 移植再挑戦予定)
brew "git"        # tier2-tooling (gitconfig symlink 要注意)
brew "sheldon"    # zsh プラグインマネージャ
brew "starship"   # クロスシェルプロンプト
brew "mise"       # ランタイムバージョンマネージャ (binary のみ nix 予定、D5)
brew "direnv"     # nix build で checkPhase hang (Phase B1.5 で別 strategy 模索)

# Fonts (Phase B1 対象外)
cask "font-hackgen-nerd"  # HackGen Nerd Font (日本語対応)
cask "font-hack-nerd-font" # Hack Nerd Font
