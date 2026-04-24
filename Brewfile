# Phase B1 Step 5+6 以降、GUI cask / tap-only formula は nix/darwin/default.nix の
# homebrew module で宣言的に管理。この Brewfile に残るのは:
#   - Phase B1 Step 7 で移植予定の bootstrap 系
#   - Phase C 以降で扱う Font
# Phase B1 が完全に完了すれば task brew は不要になり、nix-darwin 経由の
# `task nix:switch` だけで全環境が揃う。

# Bootstrap (Phase B1 Step 7 で nix 移植予定)
brew "git"        # tier2-tooling (gitconfig symlink 検証付き)
brew "sheldon"    # zsh プラグインマネージャ
brew "starship"   # クロスシェルプロンプト
brew "mise"       # ランタイムバージョンマネージャ (binary のみ nix 予定、D5)
brew "direnv"     # ディレクトリ別環境変数マネージャ

# Fonts (Phase B1 対象外、Phase C 以降で検討)
cask "font-hackgen-nerd"  # HackGen Nerd Font (日本語対応)
cask "font-hack-nerd-font" # Hack Nerd Font
