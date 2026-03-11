# Personal Codex Defaults

## Core Workflow
- 日本語で応答する。リポジトリ固有の指示があればそちらを優先する。
- 実装前に `rg` / `rg --files` で既存コード・設定・ドキュメントを確認する。
- 曖昧、または複数ステップのタスクは plan を作ってから編集する。
- 完了を宣言する前に、変更範囲に最も近い build/test/lint/validation を実行する。
- diff が自明でない場合は `codex review --uncommitted` を使って追加確認する。

## Project Instructions
- 最も近い `AGENTS.md` を常に優先する。
- repo に `.agents/skills/` がある場合は、project-local skill を先に使う。
- `CLAUDE.md` や Claude 向け skill を参照する場合は、Claude 固有の `Agent`、`AskUserQuestion`、slash command、plugin 前提をそのまま実行しない。

## Editing Defaults
- 変更は最小限にとどめ、既存の命名規則・構成・formatter に従う。
- パッケージ追加や新規 utility の前に、既存の task、script、skill、MCP を確認する。
- 同じ運用を 2 回以上繰り返したら、skill 化や AGENTS 追加を検討する。

## Harness Rules
- リンター設定ファイル (`.eslintrc*`, `biome.json`, `.prettierrc*`, `.golangci.yml` 等) は変更禁止。lint 違反はコードで修正する。
- `git commit --no-verify` 禁止。pre-commit フックをバイパスしない。
- タスク完了前にテスト・lint を実行して通過を確認する。
- repo 共通 contract は `docs/agent-harness-contract.md` を参照する。
- 長時間タスク、中断前、handoff 前は `$codex-checkpoint-resume` を使って filesystem に状態を残す。
- 繰り返し発生した repo 固有ルールや failure は `$codex-memory-capture` で `~/.codex/memories` に記録する。
- repo 開始時に `~/.codex/memories/dotfiles-memory.md` があれば確認する。
