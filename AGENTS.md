# Dotfiles Codex Guide

## Scope
- このリポジトリは macOS 用 dotfiles。`~/.config`、`~/.claude`、`~/.codex` に symlink される設定の実体を管理する。
- `~/.claude/` の実体は `.config/claude/`、`~/.codex/` の実体は `.codex/`。

## Workflow
- スコープが曖昧、または複数ステップの変更は、実装前に plan を作る。
- 依存追加・新規 script・新規 utility・新規抽象化の前に、まず既存の設定・script・skill・MCP を探す。
- 変更後は、変更範囲に最も近い validation を実行してから完了を宣言する。
- diff が自明でない場合は `codex review --uncommitted` を使ってから報告する。

## Working Rules
- 日本語で応答する。コード・コマンド・技術用語は英語のままでよい。
- 変更は最小限にとどめ、既存の命名規則とファイル構成に従う。
- 不要なコメントやドキュメントは追加しない。
- パッケージマネージャや実行コマンドは、各プロジェクトですでに使われているものに合わせる。
- フォーマッタ・リンター・テストがある場合は、変更範囲に応じて実行して確認する。
- テキスト検索は `rg`、ファイル一覧は `rg --files` を優先する。

## Where To Look
- 全体構成と基本コマンド: `README.md`, `Taskfile.yml`
- Claude Code 設定: `.config/claude/`
- Codex 設定: `.codex/`
- MCP 定義: `.mcp.json`
- ツール別の補足:
  - WezTerm: `.config/wezterm/README.md`
  - AeroSpace: `.config/aerospace/README.md`
  - Karabiner: `.config/karabiner/README.md`
  - zsh: `.config/zsh/README.md`

## Codex Skills
- project-local skills は `.agents/skills/` に置く。
- まず使う候補:
  - `$codex-search-first`: 実装前の既存資産調査
  - `$codex-verification-before-completion`: 完了前の実コマンド検証
  - `$dotfiles-config-validation`: dotfiles 向け validation コマンド選定
- Claude 向け skill を参照する場合は、Claude 固有の `Agent`、`AskUserQuestion`、slash command、plugin 前提の記述をそのまま実行せず、文書として必要部分だけ採用する。

## Useful Commands
- `task symlink`: symlink を再作成
- `task install`: 初回セットアップ
- `task brew`: Brewfile からパッケージを導入
- `task restart-wm`: window manager 関連を再起動
- `task validate`: dotfiles の主要 validation をまとめて実行
- `task validate-configs`: config/script の構文チェック
- `task validate-readmes`: README のローカルリンク検証
- `task validate-symlinks`: managed symlink の検証
- `task update`: Homebrew とパッケージを更新

## Change Validation
- 変更した設定に対応する README やスクリプトを先に確認してから編集する。
- 検証は変更対象に最も近いコマンドだけを実行し、無関係な全体変更は避ける。
- `.codex/` や symlink 管理を変えたら `task validate-symlinks` を含める。
