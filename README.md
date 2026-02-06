# Dotfiles

macOS 向け開発環境の設定ファイル群。

参考: [mozumasu/dotfiles](https://github.com/mozumasu/dotfiles)

## セットアップ

```bash
task install      # 初回セットアップ
task symlink      # シンボリックリンクのみ再作成
task brew         # Brewfile からパッケージインストール
task restart-wm   # WM サービスの再起動
task update       # Homebrew パッケージの更新
```

## 構成

| ディレクトリ | 説明 | キーバインド |
|-------------|------|-------------|
| [.config/wezterm/](.config/wezterm/) | ターミナルエミュレータ | [README](.config/wezterm/README.md) |
| [.config/aerospace/](.config/aerospace/) | タイル型ウィンドウマネージャ | [README](.config/aerospace/README.md) |
| [.config/karabiner/](.config/karabiner/) | キーリマッピング | [README](.config/karabiner/README.md) |
| [.config/zsh/](.config/zsh/) | シェル設定・エイリアス | [README](.config/zsh/README.md) |
| [.config/nvim/](.config/nvim/) | Neovim (AstroNvim) | |
| [.config/zed/](.config/zed/) | Zed エディタ | |
| [.config/starship.toml](.config/starship.toml) | プロンプト | |
| [.config/sheldon/](.config/sheldon/) | zsh プラグインマネージャ | |
| [.config/sketchybar/](.config/sketchybar/) | ステータスバー | |
| [.config/claude/](.config/claude/) | Claude Code 設定 | |
| [.config/git/](.config/git/) | Git 設定 | |
| [.config/gh/](.config/gh/) | GitHub CLI | |

### tmux キーバインド

Prefix: `Ctrl+Q`

| キー | 動作 |
|------|------|
| `Prefix` → `h/j/k/l` | ペイン移動 |
| `Prefix` → `r` | 設定リロード |
| `Alt+Arrow` | ペインサイズ調整 |
