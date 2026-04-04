---
name: autonomous
description: >
  複雑なタスクをセッション跨ぎで自律実行する。タスク分解→並列/逐次実行→進捗管理。
  claude -p ヘッドレスモードで子セッションを生成し、task_list.md で進捗を追跡。
  並列タスクは worktree で隔離し、共有状態の破損を防止。
  長時間のリファクタリング、マイグレーション、大規模実装に使用。
  Triggers: '自律実行', 'autonomous', 'セッション跨ぎ', 'バックグラウンドで', '並列実行', 'long-running task'.
  Do NOT use for: 単一セッションで完了する作業（直接実行で十分）、単純な並列タスク（use Agent tool directly）。
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

### タスク分解のガイドライン

- **1タスクあたり 100行以下** を目安に分解する。エージェントは RL プロセスで複雑タスクの失敗ペナルティを学習しており、大きなタスクを回避する傾向がある（Complexity Fear）。小さいタスクに分解することで activation energy をゼロに近づけ、stub や "out of scope" 宣言を防ぐ
- 500個の小タスクを連結する方が、5個の大タスクよりも品質が高くなる
- 各タスクは独立してテスト可能な単位にする

> Ref: OpenForage "Complexity Fear" — "break a complex problem into many different sub-tasks where every task is a sub-hundred-line task"

### タスクリストのフォーマット選択

| フォーマット | 用途 | ファイル |
|---|---|---|
| **Markdown** (default) | シンプルなタスク (1-5個) | `task_list.md` |
| **JSON** | 検証ステップ付き大規模タスク (6+個) | `task_list.json` |

JSON フォーマットは以下の場合に使用する:
- タスクが6個以上
- 各タスクに明確な検証ステップがある（E2E テスト等）
- `passes` フィールドで「完了」と「検証済み」を区別する必要がある
- **フィーチャーリスト**: 項目数に関わらず常に JSON（Markdown はエージェントが勝手に完了マークを付ける傾向がある）

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
- **マージ前コンフリクト検出**: 全 worktree 完了後、マージ前に変更ファイルの重複を検出する（Step 4.3 参照）

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

## Step 4.5: QA Phase（Build-QA 自動ループ）

> Anthropic Harness Design v2: Generator→Evaluator→Generator ループ。
> 「嘘をつけない検証者」（Layer 0）+ 異種モデル評価（Layer 2）の組み合わせ。

**起動条件**: 変更が 30 行以上（`git diff --stat` で判定）。S 規模はスキップ。

**Dual-Model QA**（並列起動）:

1. **Opus Evaluator**: Agent ツールで code-reviewer を懐疑的ペルソナで起動
   - プロンプト: 「`adversarial-evaluation-criteria.md` の基準で採点せよ。be skeptical, probe edge cases, don't approve easily」
   - 成果物を `adversarial-evaluation-criteria.md` の Code/API/Doc 基準で評価

2. **Codex Evaluator**: `/codex-review` スキル経由（reasoning effort: xhigh）
   - 独立した視点からの deep reasoning レビュー
   - Opus と異なるモデルによる盲点補完

**反復ルール**:
- Build→QA を最大 3 ラウンド反復
- 各ラウンドで QA の指摘を元に修正 → 再 QA
- 修正は指摘箇所のみ（スコープ拡大禁止）

**終了条件**:
| 条件 | アクション |
|------|----------|
| 両モデル PASS | Deliver フェーズへ進行 |
| 片方 PASS + 片方 NEEDS_FIX (3R後) | Graduated Completion (Partial) + handback report |
| 両モデル NEEDS_FIX (3R後) | Graduated Completion (Partial) + handback report |
| UI 変更あり | Playwright MCP でスクリーンショット取得 → Opus Evaluator に視覚評価を追加 |

## Step 4.3: Pre-Merge Conflict Detection（並列実行時のみ）

全 worktree の実行が完了した後、マージ前に変更ファイルの重複を検出する。

**手順**:

```bash
# 各 worktree の変更ファイルを収集
for wt in .autonomous/{task-name}/worktrees/task-*; do
  branch=$(git -C "$wt" rev-parse --abbrev-ref HEAD)
  echo "=== $branch ==="
  git -C "$wt" diff --name-only main..HEAD
done
```

**判定**:

| 状態 | アクション |
|------|-----------|
| 重複なし | そのままマージへ進む |
| 重複あり | `⚠️ Merge warning: {branch-A} and {branch-B} both modified {file}` を出力 |

**重複発見時のフロー**:
1. 重複ファイルと対応ブランチを一覧で報告
2. マージ順序を推奨（変更行数が少ないブランチを先にマージ）
3. **自動マージしない** — ユーザーに判断を委ねる

> 出典: Mex Emini "Parallel Agent Orchestrator" — "Detection occurs before merge conflicts manifest, allowing developers to plan merge order."

## Step 5: Deliver (Stripe Minions Pattern)

セッションループ完了後、自動的に PR を作成しハンドバックする。

### PR 作成条件

| 状態 | アクション |
|------|-----------|
| 全タスク完了 (Full) | PR 作成 + 通知 |
| 一部完了 (Partial, COMPLETION_MODE=graduated) | `[WIP]` PR + ハンドバックレポート + 通知 |
| 着手不能 (Blocked) | PR なし、エラーレポート + 通知 |

### 手動実行

```bash
# run-session.sh が自動実行するが、手動でも可能
COMPLETION_MODE=graduated bash ~/.claude/skills/autonomous/scripts/run-session.sh \
  .autonomous/{task-name} \
  {max_sessions} \
  {budget_per_session}
```

### Blueprint 連携

タスク分析時に `references/blueprints/` から最適な blueprint を推薦する:

1. バグ修正系 → `bug-fix.yaml`
2. 新機能系 → `feature.yaml`
3. リファクタリング系 → `refactor.yaml`

Blueprint の `tools` フィールドを executor-prompt.md の指示に反映し、
不要なツールの使用を抑制する。

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
