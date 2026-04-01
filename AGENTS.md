# Dotfiles Codex Guide

## Scope
- このリポジトリは macOS 用 dotfiles。`~/.config`、`~/.claude`、`~/.codex` に symlink される設定の実体を管理する。
- `~/.claude/` の実体は `.config/claude/`、`~/.codex/` の実体は `.codex/`。

## Workflow
- スコープが曖昧、または複数ステップの変更は、実装前に plan を作る。
- 依存追加・新規 script・新規 utility・新規抽象化の前に、まず既存の設定・script・skill・MCP を探す。
- 変更後は、変更範囲に最も近い validation を実行してから完了を宣言する。
- diff が自明でない場合は `codex review --uncommitted` を使ってから報告する。

## Plan Contract
- 非自明な変更では root の `PLANS.md` に従う。
- 永続化する plan は `docs/plans/YYYY-MM-DD-<topic>-plan.md` に置く。
- Claude Code の一時 plan は `tmp/plans/` に置かれてもよいが、長時間タスクや handoff 対象は `docs/plans/` に昇格する。
- harness 変更、複数ディレクトリ変更、30 分以上の作業見込みでは plan を必須とする。
- 並列で別 task を進めるときは worktree を使って branch と filesystem を分離する。

## Working Rules
- 日本語で応答する。コード・コマンド・技術用語は英語のままでよい。
- 変更は最小限にとどめ、既存の命名規則とファイル構成に従う。
- 不要なコメントやドキュメントは追加しない。
- パッケージマネージャや実行コマンドは、各プロジェクトですでに使われているものに合わせる。
- フォーマッタ・リンター・テストがある場合は、変更範囲に応じて実行して確認する。
- テキスト検索は `rg`、ファイル一覧は `rg --files` を優先する。

## Where To Look
- 全体構成と基本コマンド: `README.md`, `Taskfile.yml`, `PLANS.md`
- Claude Code 設定: `.config/claude/`
- Codex 設定: `.codex/`
- MCP 定義: `.mcp.json`
- playbook: `docs/playbooks/`
- ツール別の補足:
  - WezTerm: `.config/wezterm/README.md`
  - AeroSpace: `.config/aerospace/README.md`
  - Karabiner: `.config/karabiner/README.md`
  - zsh: `.config/zsh/README.md`

## CLI Tools

このリポジトリに含まれる CLI ツール一覧。`--json` フラグでエージェント向け構造化出力に対応。

### osa (OpenTelemetry Session Analyzer)

Claude Code のセッションログを解析し、ツール呼び出し統計・トークン使用量・ボトルネックを表示する。

```shell
# セッション一覧を表示
osa list
osa list --project dotfiles
osa list --json                  # JSON output for agents

# 直近セッションの統計を表示
osa analyze
osa analyze --last 5 --json      # JSON output for agents

# OTLP エンドポイントにエクスポート
osa export <session-file> --otlp http://localhost:4318
```

### validate_*.sh (.bin/)

dotfiles の検証スクリプト。`task validate` から一括実行可能。

```shell
task validate-configs       # config/script の構文チェック
task validate-symlinks      # managed symlink の検証
task validate-readmes       # README のローカルリンク検証
```

## Codex Skills
- project-local skills は `.agents/skills/` に置く。
- selected skill は compatibility のため `~/.codex/skills/` と `~/.agents/skills/` の両方へ公開する。
- まず使う候補:
  - `$codex-search-first`: 実装前の既存資産調査
  - `$ai-workflow-audit`: harness 改善や repo 横断共有で、skill / memory / script の昇格先を決める
  - `$openai-frontend-prompt-workflow`: GPT-5.4 frontend prompt template の再利用、公式 guidance の運用化、不足情報の聞き返し
  - `$frontend-skill`: visually strong な landing page / app / dashboard を実装するときの art direction と hard rules
  - `$github-review-workflow`: PR comments と GitHub Actions CI の振り分けと処理
  - `$artifact-workflow`: doc / pdf / slides / screenshot の振り分けと成果物 workflow
  - `$codex-verification-before-completion`: 完了前の実コマンド検証
  - `$dotfiles-config-validation`: dotfiles 向け validation コマンド選定
  - `$codex-checkpoint-resume`: 長時間タスクの checkpoint と再開補助
  - `$codex-memory-capture`: repo 固有 learnings の durable 保存
  - `$codex-session-hygiene`: compact / resume / handoff を含む長時間タスクの整流
- Claude 向け skill を参照する場合は、Claude 固有の `Agent`、`AskUserQuestion`、slash command、plugin 前提の記述をそのまま実行せず、文書として必要部分だけ採用する。

## Mandatory Skill Usage
- 実装前の調査が必要なら `$codex-search-first`
- harness 改善、workflow 設計、他 repo への横展開判断は `$ai-workflow-audit`
- 完了前の検証コマンド選定は `$dotfiles-config-validation`
- 30 分以上、handoff、resume、compact が絡む作業は `$codex-checkpoint-resume`
- 同じ長時間タスクで thread 継続や再開判断が必要なら `$codex-session-hygiene`
- 繰り返し出た repo 固有ルールを残すときは `$codex-memory-capture`

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

## Change Surface Matrix
- `.codex/config.toml`, `.codex/AGENTS.md`, `.agents/skills/`
  - 併せて見る: `PLANS.md`, `docs/agent-harness-contract.md`, `docs/guides/codex-long-horizon-workflow.md`
  - 最低検証: `task validate-configs`, `task validate-symlinks`
- `.config/claude/CLAUDE.md`, `.config/claude/settings.json`, `.config/claude/scripts/`, `.config/claude/skills/`
  - 併せて見る: `.config/claude/references/workflow-guide.md`, `PLANS.md`, `docs/agent-harness-contract.md`
  - 最低検証: `task validate-configs`, `task validate-symlinks`
- `.bin/symlink.sh`, `.bin/validate_symlinks.sh`
  - 併せて見る: `Taskfile.yml`, `.codex/AGENTS.md`, `.config/claude/CLAUDE.md`
  - 最低検証: `task symlink`, `task validate-symlinks`
- `Taskfile.yml`, `.bin/validate_*.sh`
  - 併せて見る: `AGENTS.md`, tool 別 README
  - 最低検証: 変更した task/validator を直接実行
- `README.md`, `docs/`, tool 別 `README.md`
  - 併せて見る: 対応する実ファイルと task
  - 最低検証: `task validate-readmes`

## Harness Contract
- 共通 contract は `docs/agent-harness-contract.md` を参照する。
- repo 共通で信頼してよいのは `Taskfile.yml`、`validate_*.sh`、`.mcp.json`、`.agents/skills/`、`AGENTS.md`。
- Claude 固有の hook / middleware / completion gate は `.config/claude/` 配下の harness として扱う。
- Codex 固有の config / profile / local skill / memory は `.codex/` と `.agents/skills/` の harness として扱う。

## Playbooks
- `docs/playbooks/codex-config-changes.md`
- `docs/playbooks/claude-config-changes.md`
- `docs/playbooks/symlink-management.md`
- `docs/playbooks/worktree-based-tasking.md`
