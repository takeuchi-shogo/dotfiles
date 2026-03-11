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

## 運用ガイド

この repo は単なる設定置き場ではなく、`~/.config` / `~/.claude` / `~/.codex` に公開される
設定と、その変更・検証・再開方法まで管理する運用 repo として扱う。

- エージェント向け contract: [AGENTS.md](AGENTS.md)
- 長時間・複数ステップ作業の plan contract: [PLANS.md](PLANS.md)
- Claude / Codex 共通 harness contract: [docs/agent-harness-contract.md](docs/agent-harness-contract.md)
- AI workflow の監査と昇格基準: [docs/guides/ai-workflow-audit.md](docs/guides/ai-workflow-audit.md)
- 変更手順の playbook: [docs/playbooks/](docs/playbooks/)

非自明な変更では、まず `PLANS.md` に従って `docs/plans/` へ plan を残し、
変更後は `task validate` か最も近い `task validate-*` を実行する。

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
| [.config/claude/](.config/claude/) | Claude Code 設定 | [README](.config/claude/README.md) |
| [.codex/](.codex/) | Codex CLI 設定 | |
| [.config/git/](.config/git/) | Git 設定 | |
| [.config/gh/](.config/gh/) | GitHub CLI | |

### tmux キーバインド

Prefix: `Ctrl+Q`

| キー | 動作 |
|------|------|
| `Prefix` → `h/j/k/l` | ペイン移動 |
| `Prefix` → `r` | 設定リロード |
| `Alt+Arrow` | ペインサイズ調整 |
