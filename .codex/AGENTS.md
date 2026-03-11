# Personal Codex Defaults

## Core Workflow
- 日本語で応答する。リポジトリ固有の指示があればそちらを優先する。
- 実装前に `rg` / `rg --files` で既存コード・設定・ドキュメントを確認する。
- 曖昧、または複数ステップのタスクは plan を作ってから編集する。
- 完了を宣言する前に、変更範囲に最も近い build/test/lint/validation を実行する。
- diff が自明でない場合は `codex review --uncommitted` を使って追加確認する。

## Runtime Defaults
- `personality` は persistent default として最小限に保つ。文体、長さ、出力形式、表現トーンはそのタスクの依頼か skill で上書きする。
- 同じゴールを継続する間は、completion criteria を勝手に変えない。変更できるのはユーザーが要件を変えたときだけ。
- 進捗共有と最終回答を混同しない。途中報告では進行中の作業と未検証項目を明示し、最終回答では完了・検証済みの内容を中心に述べる。
- 長時間タスクでは、goal、completion criteria、pending validation を常に明示できる状態を保つ。

## Session Management
- 同じ問題を継続するなら同じ thread / transcript を優先する。`/fork` 相当は、解法を分岐させたいときだけ使う。
- context が長くなったら、先に checkpoint を残してから compact / resume する。
- compact / resume 後も、元の goal と completion criteria は維持する。checkpoint は一時的な authoritative summary として扱い、必要に応じて `git status` や対象ファイルで再検証する。
- handoff 前、中断前、milestone 完了時は `$codex-checkpoint-resume` を使って filesystem に state を残す。

## Project Instructions
- 最も近い `AGENTS.md` を常に優先する。
- repo に `.agents/skills/` がある場合は、project-local skill を先に使う。
- `CLAUDE.md` や Claude 向け skill を参照する場合は、Claude 固有の `Agent`、`AskUserQuestion`、slash command、plugin 前提をそのまま実行しない。

## Editing Defaults
- 変更は既存の命名規則・構成・formatter に従う。無関係な差分を広げない。
- パッケージ追加や新規 utility の前に、既存の task、script、skill、MCP を確認する。
- 同じ運用を 2 回以上繰り返したら、skill 化や AGENTS 追加を検討する。

## Harness Rules
- リンター設定ファイル (`.eslintrc*`, `biome.json`, `.prettierrc*`, `.golangci.yml` 等) は変更禁止。lint 違反はコードで修正する。
- `git commit --no-verify` 禁止。pre-commit フックをバイパスしない。
- タスク完了前にテスト・lint を実行して通過を確認する。
- repo 共通 contract は `docs/agent-harness-contract.md` を参照する。
- 長時間タスク、中断前、handoff 前、milestone 完了時は `$codex-checkpoint-resume` を使う。
- 繰り返し発生した repo 固有ルールや failure は `$codex-memory-capture` で `~/.codex/memories` に記録する。
- session 開始時は、対象 repo や task に関連する `~/.codex/memories/*-memory.md` があれば必要なものだけ確認する。
