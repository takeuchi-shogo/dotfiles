---
name: autonomous
description: >
  複雑なタスクをセッション跨ぎで自律実行する。タスク分解→並列/逐次実行→進捗管理。
  claude -p ヘッドレスモードで子セッションを生成し、task_list.md で進捗を追跡。
  並列タスクは worktree で隔離し、共有状態の破損を防止。
  長時間のリファクタリング、マイグレーション、大規模実装に使用。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
metadata:
  pattern: pipeline
---

# Autonomous — Multi-Session Task Automation

## Trigger

`/autonomous {task description}` で起動。

## Workflow

1. **Analyze** — タスクを分析、サブタスクに分解
2. **Plan** — task_list.md を作成、ユーザー承認
3. **Execute** — claude -p でヘッドレス実行（セッションループ）
4. **Monitor** — 進捗を表示、必要に応じて介入

## Step 1: Analyze

タスクの複雑さを評価し、実行戦略を決定:

| 戦略            | 条件           | 説明                                         |
| --------------- | -------------- | -------------------------------------------- |
| **Structured**  | 3+ サブタスク  | フル分解 → task_list.md → セッションループ   |
| **Lightweight** | 1-2 サブタスク | 同一プロンプトを繰り返し実行（TDD ループ等） |

## Step 2: Plan

`.autonomous/{task-name}/` ディレクトリを作成:

```
.autonomous/{task-name}/
├── task_list.md          # タスクリスト（チェックボックス形式）
├── executor-prompt.md    # Executor への指示
├── progress.md           # 進捗ログ
├── sessions/             # 各セッションの出力
└── run.lock              # 排他制御用ロック
```

### タスクリストのフォーマット選択

| フォーマット | 用途 | ファイル |
|---|---|---|
| **Markdown** (default) | シンプルなタスク (1-5個) | `task_list.md` |
| **JSON** | 検証ステップ付き大規模タスク (6+個) | `task_list.json` |

JSON フォーマットは以下の場合に使用する:
- タスクが6個以上
- 各タスクに明確な検証ステップがある（E2E テスト等）
- `passes` フィールドで「完了」と「検証済み」を区別する必要がある

スキーマ: `templates/task-list.schema.json`

**重要**: JSON の `passes` フィールドは、検証ステップを全て実行し成功した場合のみ `true` に更新する。コードを書いただけでは `true` にしない。テストの削除・変更は禁止。

### Worktree 隔離（並列実行時）

並列タスクを実行する場合、各タスクを git worktree で隔離する:

```bash
# タスクごとに worktree を作成
git worktree add .autonomous/{task-name}/worktrees/task-{n} -b autonomous/{task-name}/task-{n}
```

**隔離ルール**（"The Self-Driving Codebase" Isolated Compute 原則）:
- 並列タスク間で同じファイルを変更しない
- 各 worktree は独立したブランチで作業
- 完了後にメインブランチへマージ → worktree を削除
- コンフリクト発生時は停止して報告

**隔離が不要なケース**:
- 逐次実行（1タスクずつ順番に実行）
- 同一ファイルに触らないことが明らかな場合

task_list.md を作成し、**ユーザーの承認を得てから** Step 3 に進む。

## Step 3: Execute

### ヘッドレスモード（推奨）

```bash
bash ~/.claude/skills/autonomous/scripts/run-session.sh \
  .autonomous/{task-name} \
  {max_sessions} \
  {budget_per_session}
```

デフォルト: max_sessions=10, budget=$5.00/session

### インタラクティブモード

Agent ツールで1タスクずつ実行し、各タスク完了後にレビュー:

```
for each unchecked task in task_list.md:
  1. Agent で実行
  2. task_list.md を更新 ([ ] → [x])
  3. progress.md にログ追記
  4. 次のタスクへ
```

## Step 4: Monitor

### 構造化された進捗レポート

`run-session.sh` は各セッション完了時に `progress.md` へ構造化エントリを記録する:

```markdown
### Session 3 — 2026-03-12T14:30:00Z

- **Status**: completed
- **Tasks completed this session**: 2
- **Total progress**: 5/8
- **Output**: session-3.md
- **Newly completed**:
  - [x] データベースマイグレーション作成
  - [x] API エンドポイント実装
```

### 進捗確認コマンド

```bash
# 構造化された進捗レポート
cat .autonomous/{task-name}/progress.md
# 残りタスク数
grep -c '^\- \[ \]' .autonomous/{task-name}/task_list.md
# 最新セッション出力
cat .autonomous/{task-name}/sessions/session-*.md | tail -50
```

## Safety

- **Lock ファイル**: 同時実行を防止（`run.lock`）
- **Budget cap**: セッション毎の最大コスト（デフォルト $5.00）
- **Max sessions**: 無限ループ防止（デフォルト 10回）
- **Progress persistence**: 途中で停止しても task_list.md で再開可能
- **Worktree 隔離**: 並列実行時は git worktree で各タスクを分離（共有状態の破損防止）

## Anti-Patterns

- ユーザー承認なしに自動実行を開始する
- 単純なタスクに /autonomous を使う（→ 直接実行で十分）
- ロックファイルを無視して並列実行する
- セッション出力を確認せずに次に進む
- 並列タスクで同じファイルを複数エージェントが同時に変更する（→ worktree で隔離）

## Gotchas

- **run.lock 残存**: セッション異常終了時に `.autonomous/{name}/run.lock` が残り、再実行がブロックされる。手動で `rm` が必要
- **worktree のクリーンアップ**: 並列タスク完了後に `git worktree remove` を忘れると、ディスクを圧迫し、ブランチが残る
- **claude -p のコンテキスト制限**: ヘッドレスセッションは会話コンテキストが短い。executor-prompt.md に必要な情報を全て含めること
- **共有状態の書き込み競合**: 並列タスクが同じファイルを編集すると、マージコンフリクトが発生する。worktree 隔離を徹底
- **セッション数の爆発**: MAX_SESSIONS を設定しないと、分解したタスク数だけセッションが生まれる。推奨: 5以下
