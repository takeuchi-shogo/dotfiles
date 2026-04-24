# Taps
tap "FelixKratz/formulae"    # borders
tap "k1LoW/tap"
tap "nikitabobko/tap"

# CLI tools
# Phase B1 Tier 1 (fzf, lua, ripgrep, bat, eza, zoxide, git-delta, dust, yazi, fd,
# tree-sitter-cli, grep, gh, neovim) は nix/home/default.nix に移動済み。
# 残存分は brew-retain (tap-only) / bootstrap (後続) / tier2-tooling。
brew "git"        # tier2-tooling (gitconfig symlink 要注意、B1 後期で移植)
brew "sheldon"    # bootstrap (Phase B1 最後に移植)
brew "starship"   # bootstrap (同上)
brew "mise"       # bootstrap — binary は nix へ移植予定 (D5: runtime 管理は mise 維持)
brew "borders"    # brew-retain (FelixKratz/formulae tap-only、nix-darwin.homebrew.brews で宣言)
brew "direnv"     # bootstrap
brew "k1LoW/tap/mo" # brew-retain (k1LoW tap-only)

# GUI apps
cask "wezterm"            # GPU アクセラレーテッドターミナル
cask "ghostty"            # GPU アクセラレーテッドターミナル (代替)
cask "aerospace"          # タイル型ウィンドウマネージャ
cask "hammerspoon"        # wake / unlock hooks とローカル自動化
cask "karabiner-elements" # キーボードカスタマイズ
cask "sf-symbols"         # Apple SF Symbols ブラウザ
cask "macskk"             # SKK 日本語入力メソッド
cask "jordanbaird-ice"    # メニューバーマネージャ (SketchyBar 後継)
cask "raycast"            # ランチャー (Spotlight 代替)

# Fonts
cask "font-hackgen-nerd"  # HackGen Nerd Font (日本語対応)
cask "font-hack-nerd-font" # Hack Nerd Font
