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
- 非自明な変更では root の `PLANS.md` に従い、永続化したい plan は `docs/plans/` に残す。
- 並列で別 task を進めるときは worktree を使って branch と filesystem を分離する。

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

## Security Analysis
- セキュリティ深掘り調査には `profiles.security`（xhigh + read-only）を使用する: `codex exec --skip-git-repo-check -m gpt-5.4 -p security "..."`
- 対象: 認証・認可ロジック、暗号化・トークン管理、外部入力処理、依存関係の変更
- 攻撃ベクトルのマッピング、権限昇格パス、暗号の弱点、レースコンディション、サプライチェーンリスクを分析する
- findings list や scanner 出力を起点にしすぎず、まず trust boundary、sensitive path、decode/parse/normalize をまたぐ invariant を確認する
- 「チェックがあるか」より「最終的に解釈される値まで constraint が保たれるか」を優先して見る
- 可能なら再現コマンド、exit code、log など validation evidence を残し、推測だけで確定判定しない
- Claude 側の `security-reviewer` エージェントの表面チェックを補完する深い推論として位置づける

## Mandatory Skill Usage
- 調査開始時は `$codex-search-first`
- dotfiles の validation 選定は `$dotfiles-config-validation`
- 長時間タスク、resume、compact、handoff は `$codex-checkpoint-resume`
- thread 継続 / fork / resume 判断が絡むときは `$codex-session-hygiene`
- repo 固有 learnings の保存は `$codex-memory-capture`

## Subagent Usage

### Configured Custom Agents

| Agent | Model | 用途 | Sandbox |
|---|---|---|---|
| `pr_explorer` | `gpt-5.3-codex-spark` | diff の影響範囲・依存関係マッピング | `read-only` |
| `reviewer` | `gpt-5.4` | correctness / security / test gap レビュー | `read-only` |
| `docs_researcher` | `gpt-5.3-codex-spark` | ドキュメント・config の整合確認 | `read-only` |
| `validation_explorer` | `gpt-5.3-codex-spark` | dotfiles 変更に対する最小 validation 選定 | `read-only` |

### 使い方

- subagent は親 agent に明示的に依頼して起動する
- 並列委譲で独立した観点を調査させ、親 agent が統合する
- 全 custom agent は read-only。ファイル編集は親 agent が行う
- 詳細な framing とテンプレートは `docs/playbooks/codex-subagent-usage.md` を参照する

### Branch Review パターン

```text
Review this branch with parallel subagents.
Use pr_explorer for code path mapping, reviewer for correctness/security/test gaps, and docs_researcher for documentation/config consistency.
Wait for all three, then return a prioritized summary with file references.
```

### Repo Exploration パターン

```text
Explore this repo with parallel subagents.
Use pr_explorer on the target directory structure, docs_researcher on documentation and config files.
Return consolidated findings without proposing edits.
```

### Validation Selection パターン

```text
Choose the smallest sufficient validation commands for this change.
Use validation_explorer on Taskfile.yml, validate scripts, change surface matrix, and nearby README guidance.
Return recommended commands in priority order with rationale, and do not run commands.
```

### Runtime 制御

- `max_threads = 4`: 同時 subagent 数。token 消費を見て調整
- `max_depth = 1`: subagent の subagent は禁止
- subagent は親の sandbox を継承するが、custom agent 側で `read-only` に上書き済み

### 注意事項

- `codex --version` と `codex features list` で runtime 状態を確認すること
- 2026-03-17 時点のローカル確認では `codex-cli 0.115.0`、`multi_agent stable true`
- `child_agents_md` は未有効のため、agent 固有の運用ガイドは引き続き `.codex/AGENTS.md` と playbook で管理する
- custom agent 定義は current CLI が受け付ける最小項目に寄せ、追加フィールドを入れたら local parser か `codex review --uncommitted` で確認する
- custom agent 名解決や UI 表示の挙動は CLI 更新時に再確認する
- write-capable subagent は Phase 2 で検討。現時点では read-only のみ

## Change Surface Matrix
- `.codex/` を変えたら `docs/agent-harness-contract.md`, `PLANS.md`, `.agents/skills/` を確認する
- `.agents/skills/` を変えたら `.bin/symlink.sh` と `.bin/validate_symlinks.sh` を確認する
- symlink 管理を変えたら `task symlink` と `task validate-symlinks` を必ず実行する
- Claude 側 harness を読むときは `.config/claude/references/workflow-guide.md` を参照し、Claude 固有 hook を Codex へ持ち込まない
- selected project skill は `~/.codex/skills/` と `~/.agents/skills/` の両方へ公開する
