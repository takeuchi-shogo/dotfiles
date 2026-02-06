# Zsh 設定

モジュール構成で管理。`~/.zshrc` から `~/.config/zsh/.zshrc` を読み込み、各サブディレクトリの `.zsh` ファイルを順に source する。

## ディレクトリ構成

```
zsh/
├── .zshrc           # エントリポイント（core → tools → functions → aliases → plugins の順に読込）
├── core/            # 環境変数、PATH、zsh オプション
├── tools/           # mise, pyenv, rbenv, docker 等のツール初期化
├── functions/       # カスタム関数（chpwd 等）
├── aliases/         # エイリアス定義
└── plugins/         # sheldon, fzf, starship の初期化
```

## エイリアス

### Git

| エイリアス | コマンド |
|-----------|---------|
| `g` | `git` |
| `gs` | `git status` |
| `gd` | `git diff` |
| `gds` | `git diff --staged` |
| `ga` | `git add` |
| `gc` | `git commit` |
| `gp` | `git push` |
| `gl` | `git log --oneline --graph --decorate` |
| `gco` | `git checkout` |
| `gb` | `git branch` |
| `gpl` | `git pull` |

### General

| エイリアス | コマンド |
|-----------|---------|
| `ll` | `ls -la` |
| `la` | `ls -a` |
| `..` | `cd ..` |
| `...` | `cd ../..` |
| `....` | `cd ../../..` |
| `mkdir` | `mkdir -p` |
| `cp` | `cp -i`（上書き確認） |
| `mv` | `mv -i`（上書き確認） |
| `rm` | `rm -i`（削除確認） |

## プラグイン（sheldon）

| プラグイン | 説明 |
|-----------|------|
| zsh-defer | 遅延読み込み |
| zsh-autosuggestions | コマンド補完提案 |
| zsh-completions | 追加補完定義 |
| zeno | 補完強化 |
| fast-syntax-highlighting | シンタックスハイライト |
| zsh-history-substring-search | 履歴部分一致検索（↑↓キー） |
| zsh-autopair | 括弧・クォートの自動補完 |
| fzf-tab | タブ補完を fzf で強化 |

## キーバインド（プラグイン提供）

| キー | 動作 | 提供元 |
|------|------|--------|
| `Ctrl+R` | 履歴検索（fzf） | fzf |
| `Ctrl+T` | ファイル検索（fzf） | fzf |
| `Alt+C` | ディレクトリジャンプ（fzf） | fzf |
| `↑` / `↓` | 履歴部分一致検索 | zsh-history-substring-search |
