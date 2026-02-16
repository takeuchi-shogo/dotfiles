# Sheldon による Zsh プラグイン管理

## 概要

Sheldon は Zsh プラグインマネージャ。
設定ファイルは `~/.config/sheldon/plugins.toml`（dotfiles で symlink 管理）。

## セットアップ

```bash
brew install sheldon
sheldon lock
exec zsh
```

## インストールされるプラグイン

| プラグイン | 用途 |
|-----------|------|
| zsh-defer | プラグインの遅延読み込み |
| zsh-history-substring-search | 履歴のサブストリング検索 |
| zsh-autopair | 括弧・クォートの自動ペア |
| zeno.zsh | SQLite ベースの履歴サブシステム |
| zsh-autosuggestions | コマンド入力の自動補完候補 |
| fast-syntax-highlighting | シンタックスハイライト |
| zsh-completions | 追加の補完定義 |
| fzf-tab | fzf によるタブ補完の拡張 |

## トラブルシューティング

### sheldon lock が失敗する

ネットワーク接続を確認。GitHub からの clone が必要。

### プラグインが反映されない

```bash
sheldon lock   # lock ファイルを再生成
exec zsh       # シェルを再起動
```

### fzf-tab が動かない

fzf 本体が必要:

```bash
brew install fzf
```
