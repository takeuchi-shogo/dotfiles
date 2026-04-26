# Dotfiles

macOS 向け開発環境の設定ファイル群。
シェル・エディタ・WM の設定に加え、Claude Code / Codex CLI / Cursor の AI エージェント基盤を統合管理する。

参考: [mozumasu/dotfiles](https://github.com/mozumasu/dotfiles)

## セットアップ

```bash
# 初回 (nix-darwin が未インストール)
task nix:bootstrap PROFILE=private

# 通常運用 (CLI / Brewfile / dotfiles symlink を一括反映)
task nix:switch PROFILE=private

# 個別操作
task brew               # Brewfile からパッケージインストール (legacy)
task restart-wm         # WM サービスの再起動
task update             # Homebrew パッケージの更新
task validate           # 全 dotfiles の検証 (config, README, symlink)
```

> Phase B2 (2026-04-26 完了) で symlink 管理は `home-manager` に移行。
> 詳細は [`nix/README.md`](nix/README.md)。

## 構成

### シェル・ターミナル

| ディレクトリ | 説明 | キーバインド |
|---|---|---|
| [.config/zsh/](.config/zsh/) | シェル設定・エイリアス | [README](.config/zsh/README.md) |
| [.config/wezterm/](.config/wezterm/) | WezTerm ターミナル | [README](.config/wezterm/README.md) |
| [.config/ghostty/](.config/ghostty/) | Ghostty ターミナル | |
| [.config/starship.toml](.config/starship.toml) | プロンプト (Starship) | |
| [.config/sheldon/](.config/sheldon/) | zsh プラグインマネージャ | |

### エディタ

| ディレクトリ | 説明 |
|---|---|
| [.config/nvim/](.config/nvim/) | Neovim (AstroNvim) |
| [.config/zed/](.config/zed/) | Zed エディタ |

### ウィンドウマネージャ・UI

| ディレクトリ | 説明 | キーバインド |
|---|---|---|
| [.config/aerospace/](.config/aerospace/) | AeroSpace (タイル型 WM) | [README](.config/aerospace/README.md) |
| [.hammerspoon/](.hammerspoon/) | wake / unlock 自動化 | [README](.hammerspoon/README.md) |
| [.config/karabiner/](.config/karabiner/) | キーリマッピング | [README](.config/karabiner/README.md) |
| [.config/sketchybar/](.config/sketchybar/) | ステータスバー | |
| [.config/borders/](.config/borders/) | ウィンドウボーダー | |

### Git・開発ツール

| ディレクトリ | 説明 |
|---|---|
| [.config/git/](.config/git/) | Git 設定 |
| [.config/gh/](.config/gh/) | GitHub CLI |
| [.config/lazygit/](.config/lazygit/) | lazygit TUI |

### AI エージェント

| ディレクトリ | 説明 | symlink 先 |
|---|---|---|
| [.config/claude/](.config/claude/) | Claude Code ハーネス | `~/.claude/` |
| [.codex/](.codex/) | Codex CLI (OpenAI) | `~/.codex/` |
| [.cursor/](.cursor/) | Cursor エディタ | `~/.cursor/` |

## AI エージェント基盤

この dotfiles の中核は 3 つの AI コーディングエージェントの統合基盤。

### Claude Code

最も重い構成。hooks・スキル・エージェント・ポリシーの 4 層ハーネスで動作を制御する。

```
.config/claude/
├── CLAUDE.md              # グローバル指示 (Progressive Disclosure)
├── settings.json          # hooks, permissions, env
├── agents/                # 31 専門エージェント (code-reviewer, debugger, etc.)
├── skills/                # 60+ スキル (review, commit, spec, epd, etc.)
├── commands/              # 27 スラッシュコマンド (/commit, /review, /spec, etc.)
├── scripts/
│   ├── policy/            # ガードレール hooks (golden-check, protect-linter-config, etc.)
│   ├── runtime/           # セッション管理 (checkpoint, output-offload, etc.)
│   ├── lifecycle/         # セッションライフサイクル
│   ├── learner/           # 自己学習 (session-learner, etc.)
│   └── lib/               # 共通ライブラリ
├── references/            # 50+ リファレンスドキュメント
├── rules/                 # 言語別ルール (config, proto, test)
└── templates/             # テンプレート
```

主な機能:

- **AutoEvolve**: セッションデータから自動で設定改善を提案
- **マルチモデル連携**: Claude ↔ Codex (gpt-5.4) ↔ Gemini (1M ctx) の自動委譲
- **Progressive Disclosure**: `CLAUDE.md` → `references/` → `rules/` の段階的情報開示
- **EPD ワークフロー**: Spec → Spike → Validate → Implement → Review

```bash
task upgrade-claude       # Claude Code アップグレード + パッチ適用
task patch-claude         # システムプロンプトパッチのみ適用
task restore-claude       # パッチをリストア (vanilla に戻す)
task build-hooks          # claude-hooks Rust バイナリのビルド
```

### Codex CLI

OpenAI Codex CLI の設定。Claude Code のサブエージェントとしても使用。

```
.codex/
├── AGENTS.md              # エージェント指示
├── config.toml            # 基本設定
├── agents/                # 専門エージェント (reviewer, debugger, etc.)
└── rules/                 # デフォルトルール
```

```bash
task codex-janitor        # Codex janitor ワークフロー実行
```

### Cursor

Cursor エディタの AI 設定。rules・skills・agents・hooks で構成。

```
.cursor/
├── rules/                 # 10 ルール (global, quality-guard, 言語別)
├── skills/                # 7 スキル (review, commit, create-pr, spec, etc.)
├── agents/                # 3 エージェント (verifier, reviewer, security-checker)
├── commands/              # コマンド定義
├── hooks.json             # hooks 設定
└── hooks/                 # hook スクリプト (quality-gate.sh)
```

## ツール

| ディレクトリ | 説明 |
|---|---|
| [tools/claude-hooks/](tools/claude-hooks/) | Claude Code hooks の Rust 実装 |
| [tools/system-prompt-patcher/](tools/system-prompt-patcher/) | Claude Code システムプロンプトパッチャー |
| [tools/codex-janitor/](tools/codex-janitor/) | Codex janitor ワークフローランナー |
| [tools/half-clone/](tools/half-clone/) | Half-Clone (軽量リポジトリクローン) |
| [tools/safeclaw/](tools/safeclaw/) | SafeClaw (安全なコマンド実行) |

## 運用ガイド

この repo は単なる設定置き場ではなく、設定の変更・検証・再開方法まで管理する運用 repo。

| ドキュメント | 内容 |
|---|---|
| [AGENTS.md](AGENTS.md) | エージェント向け contract |
| [PLANS.md](PLANS.md) | 長時間・複数ステップ作業の plan contract |
| [docs/agent-harness-contract.md](docs/agent-harness-contract.md) | Claude / Codex 共通ハーネス contract |
| [docs/guides/ai-workflow-audit.md](docs/guides/ai-workflow-audit.md) | AI workflow の監査と昇格基準 |
| [docs/playbooks/](docs/playbooks/) | 変更手順の playbook |
| [docs/adr/](docs/adr/) | Architecture Decision Records |

非自明な変更では、まず `PLANS.md` に従って `docs/plans/` へ plan を残し、
変更後は `task validate` を実行する。

## tmux キーバインド

Prefix: `Ctrl+Q`

| キー | 動作 |
|---|---|
| `Prefix` → `h/j/k/l` | ペイン移動 |
| `Prefix` → `r` | 設定リロード |
| `Alt+Arrow` | ペインサイズ調整 |
