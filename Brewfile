# Phase B1 完了後、この Brewfile は最小限に縮退。
# CLI / GUI cask / tap-only formula の大半は nix/darwin/default.nix と nix/home/default.nix
# で宣言的に管理される。Font は macOS font cache の罠を避けるため Phase C 以降で扱う。
# direnv は nix build 時 checkPhase が Determinate + sudo 環境で hang するため brew に残置。

# direnv (nix build の hang 回避、別途対応予定)
brew "direnv"

# Fonts (Phase B1 対象外)
cask "font-hackgen-nerd"  # HackGen Nerd Font (日本語対応)
cask "font-hack-nerd-font" # Hack Nerd Font
