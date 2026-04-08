---
name: checkpoint
description: >
  現在の作業状態を手動で checkpoint として保存し、HANDOFF.md を生成する。
  brief で Running Brief (RUNNING_BRIEF.md) を継続更新。
  長時間タスクの中断前やセッション切り替え時に使用。
  Triggers: 'checkpoint', '作業保存', 'セーブ', 'save state', '中断前に', 'handoff', 'running brief', 'ブリーフ更新'.
  Do NOT use for: git commit（use /commit）、日報作成（use /daily-report）、自動チェックポイント（hook が処理）。
allowed-tools: Bash, Read, Write, Edit, Glob
metadata:
  pattern: executor
---

現在の作業状態を手動で checkpoint として保存してください。

以下の手順で実行:

1. `~/.claude/session-state/edit-counter.json` から現在の編集カウントを取得
2. checkpoint を保存
3. 保存結果をユーザーに報告

実行コマンド:

```bash
python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts')
from checkpoint_manager import save_checkpoint, _read_counter
counter = _read_counter()
path = save_checkpoint(trigger='manual', edit_count=counter.get('count', 0))
print(f'Checkpoint saved: {path}')
"
```

4. checkpoint 保存後、以下のテンプレートに従い HANDOFF.md を生成する

**配置先の決定:**
- worktree 内の場合: worktree ルートに `HANDOFF.md`
- 通常の場合: `tmp/HANDOFF.md`（リポジトリルートの tmp/）

**HANDOFF.md テンプレート:**

変更されたファイル一覧は `git diff --name-only HEAD` と `git status --porcelain` から取得する。

```markdown
# HANDOFF

> Generated: {現在のISO日時}

## Goal

{現在のタスクの目的を1-2文で}

## Progress

- [x] {完了した作業項目}
- [ ] {未完了の作業項目}

## What Worked

- {うまくいったアプローチ・判断}

## What Didn't Work

- {試して失敗したこと・避けるべきこと}（なければ「特になし」）

## Next Steps

1. {次にやるべきこと}
2. {その次にやるべきこと}

## Context Files

{`git diff --name-only HEAD` と `git status --porcelain` の結果から関連ファイルをリスト}
```

5. 生成結果をユーザーに報告（ファイルパスと内容サマリ）

6. `feature_list.json` が存在する場合、`progress.log` にもエントリが追記されたことを確認・報告する
   - フォーマット: `[YYYY-MM-DD HH:MM] session_id | 作業内容 | 変更ファイル数 | git SHA`
   - checkpoint_manager.py が自動で追記するが、手動 checkpoint の場合も追記される

---

## Brief モード

プロジェクトの Running Brief を継続更新する。HANDOFF.md がセッション単位のスナップショットなのに対し、Running Brief はプロジェクト全体の進捗を累積的に記録する。

### 引数

- `/checkpoint brief` → Running Brief のみ更新（checkpoint は保存しない）
- `/checkpoint`（引数なし） → 通常の checkpoint + Running Brief にも自動追記

### 配置先

`RUNNING_BRIEF.md`（プロジェクトルート）

### テンプレート

```markdown
# Running Brief

> Last updated: {現在のISO日時}

## Goal

{プロジェクトの最終目標。初回作成時に設定、以降は変更があれば更新}

## Decisions Made

| 日付 | 決定事項 | 理由 | 影響範囲 |
|------|---------|------|---------|
| {YYYY-MM-DD} | {何を決めたか} | {なぜ} | {どこに影響するか} |

## Open Questions

- [ ] {未解決の問い} — {コンテキスト}

## Assumptions Not Yet Tested

- [ ] {検証されていない仮定} — {検証方法}

## Progress Log

| 日付 | セッション | 主な成果 |
|------|-----------|---------|
| {YYYY-MM-DD} | {session概要} | {何が進んだか} |
```

### 更新ロジック

1. `RUNNING_BRIEF.md` が存在するか確認
   - **存在しない場合**: テンプレートから新規作成。Goal を `AskUserQuestion` で聞く
   - **存在する場合**: Read で読み込み

2. 現在のセッション情報を収集:
   - `git log --oneline -10` で直近のコミット
   - `git diff --stat` で未コミットの変更
   - 現在のタスク進捗（TaskList があれば参照）

3. 以下のセクションを更新:
   - **Decisions Made**: 新しい決定があれば行を追加
   - **Open Questions**: 解決済みの問いにチェックを付け、新しい問いを追加
   - **Assumptions Not Yet Tested**: 検証済みの仮定にチェックを付け、新しい仮定を追加
   - **Progress Log**: 現在のセッションのエントリを追加
   - **Last updated**: 現在時刻に更新

4. Edit で `RUNNING_BRIEF.md` を更新し、変更内容をユーザーに報告

### HANDOFF.md との棲み分け

| | HANDOFF.md | RUNNING_BRIEF.md |
|---|-----------|-----------------|
| スコープ | 1セッション | プロジェクト全体 |
| 更新タイミング | セッション終了時 | 各セッションで累積 |
| 目的 | 次のセッションへの引き継ぎ | プロジェクトの意思決定記録 |
| 配置 | tmp/ or worktree root | プロジェクトルート |
