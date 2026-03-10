---
name: autonomous
description: >
  複雑なタスクをセッション跨ぎで自律実行する。タスク分解→並列/逐次実行→進捗管理。
  claude -p ヘッドレスモードで子セッションを生成し、task_list.md で進捗を追跡。
  長時間のリファクタリング、マイグレーション、大規模実装に使用。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
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

実行中/完了後に以下で進捗を確認:

```bash
# 進捗確認
cat .autonomous/{task-name}/task_list.md
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

## Anti-Patterns

- ユーザー承認なしに自動実行を開始する
- 単純なタスクに /autonomous を使う（→ 直接実行で十分）
- ロックファイルを無視して並列実行する
- セッション出力を確認せずに次に進む
