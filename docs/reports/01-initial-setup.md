# 初期セットアップ手順

## 概要

新しい Mac に dotfiles を展開してツールチェーンを構築する手順。

## 前提

```bash
git clone git@github.com:takeuchi-shogo/dotfiles.git ~/dotfiles
```

## 1. init-install.sh の実行

```bash
bash ~/dotfiles/.bin/init-install.sh
```

このスクリプトが順に実行する内容:

| ステップ | 内容 |
|---------|------|
| Xcode CLI Tools | `xcode-select --install`（未インストール時） |
| Homebrew | インストールまたは `brew update` |
| Brewfile | `brew bundle` でパッケージ一括インストール |
| Sketchybar Font | GitHub から ttf をダウンロード |
| Symlinks | `symlink.sh` で dotfiles → HOME にリンク |
| Sheldon | `sheldon lock` で zsh プラグインインストール |
| Starship | インストール確認 |
| Claude Code Plugins | marketplace 追加 + プラグインインストール |
| Services | sketchybar, AeroSpace の起動 |

## 2. よくある問題と対処

### Brewfile の一部パッケージが失敗する

`sketchybar`, `borders`, `aerospace` はサードパーティ tap が必要。
Brewfile に tap が定義されているが、ネットワーク等で失敗した場合は手動で:

```bash
brew tap FelixKratz/formulae
brew tap nikitabobko/tap
brew install sketchybar borders
brew install --cask nikitabobko/tap/aerospace
```

### 既存ファイルが symlink を妨げる

`symlink.sh` は既存の実ファイルをスキップする（Warning 表示）。
手動で削除してから再実行:

```bash
rm ~/.zshrc  # 例
bash ~/dotfiles/.bin/symlink.sh
```

### sheldon / starship が入らない

Brewfile 失敗の影響。個別にインストール:

```bash
brew install fzf sheldon starship neovim lua ripgrep fd tree-sitter-cli
```

インストール後に sheldon lock:

```bash
sheldon lock
```
