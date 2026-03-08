# Dotfiles Codex Guide

## Scope
- このリポジトリは macOS 用 dotfiles。`~/.config`、`~/.claude`、`~/.codex` に symlink される設定の実体を管理する。
- `~/.claude/` の実体は `.config/claude/`、`~/.codex/` の実体は `.codex/`。

## Working Rules
- 日本語で応答する。コード・コマンド・技術用語は英語のままでよい。
- 変更は最小限にとどめ、既存の命名規則とファイル構成に従う。
- 不要なコメントやドキュメントは追加しない。
- パッケージマネージャや実行コマンドは、各プロジェクトですでに使われているものに合わせる。
- フォーマッタ・リンター・テストがある場合は、変更範囲に応じて実行して確認する。
- テキスト検索は `rg`、ファイル一覧は `rg --files` を優先する。

## Where To Look
- 全体構成と基本コマンド: `README.md`
- Claude Code 設定: `.config/claude/`
- Codex 設定: `.codex/`
- ツール別の補足:
  - WezTerm: `.config/wezterm/README.md`
  - AeroSpace: `.config/aerospace/README.md`
  - Karabiner: `.config/karabiner/README.md`
  - zsh: `.config/zsh/README.md`

## Reusable Skills
- Claude Code 向けの一部 skill は `~/.codex/skills/` に symlink して再利用してよい。
- そのまま流用しやすいのは `frontend-design`、`react-best-practices`、`senior-architect`、`senior-backend`、`senior-frontend`。
- `@.config/claude/skills/<skill>/SKILL.md` の形で参照してよい。
- `SKILL.md` が `references/` を参照している場合は、必要なファイルだけ追加で `@` 参照する。
- Claude 固有の `Agent`、`AskUserQuestion`、slash command、plugin 前提の記述は Codex ではそのまま使えないため、文書として解釈して必要部分だけ採用する。

## Useful Commands
- `task symlink`: symlink を再作成
- `task install`: 初回セットアップ
- `task brew`: Brewfile からパッケージを導入
- `task restart-wm`: window manager 関連を再起動
- `task update`: Homebrew とパッケージを更新

## Change Validation
- 変更した設定に対応する README やスクリプトを先に確認してから編集する。
- 検証は変更対象に最も近いコマンドだけを実行し、無関係な全体変更は避ける。
