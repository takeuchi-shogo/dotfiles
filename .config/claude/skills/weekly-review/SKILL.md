---
name: weekly-review
description: GTD式の週次レビュー。全 Issue の棚卸し、滞留タスク検出、inbox 処理、優先度見直しを対話形式で実施。週末や週明けに使用。
---

## Skill Assets

- `templates/weekly-report.md` — Weekly report template (achievements, in-progress, blockers, next week plan, metrics)
disable-model-invocation: true
allowed-tools: Bash(gh *), Read, Grep, Glob
metadata:
  pattern: generator
---

# Weekly Review

GTD 式の週次レビューを対話形式で実施する。

## 設定確認

!`cat .claude/dev-ops.local.json 2>/dev/null || echo "NOT_CONFIGURED"`

上記が `NOT_CONFIGURED` の場合:
「開発オペレーション設定がまだありません。`/dev-ops-setup` を実行してセットアップしてください。」と案内して終了。

## 情報収集（並列実行）

以下を `gh` CLI で一括取得:

```bash
# 1. 全オープン Issue（自分担当 + チームラベル）
gh issue list --assignee {my_username} --state open --json number,title,labels,milestone,updatedAt,createdAt --limit 100

# 2. inbox ラベルの未処理 Issue
gh issue list --label {capture_label} --state open --json number,title,body,createdAt --limit 50

# 3. 今週クローズした Issue
gh issue list --assignee {my_username} --state closed --json number,title,closedAt --limit 30

# 4. 今週マージした PR
gh pr list --author {my_username} --state merged --json number,title,mergedAt --limit 20

# 5. レビュー待ちの PR
gh pr list --search "review-requested:{my_username}" --state open --json number,title,author,createdAt --limit 10

# 6. カンバン状態（Projects がある場合）
gh project item-list {project_number} --owner {owner} --format json --limit 100
```

## レビューフロー（対話形式）

### Phase 1: 今週の振り返り

```
## 今週の成果

### 完了したタスク (N件)
- #15 ペットの体重記録グラフ表示 ✅
- #18 ログイン画面リファクタ ✅

### マージした PR (N件)
- PR #32 体重記録グラフ
- PR #35 ログインUI改善

### 数値サマリー
- 完了: N件 / オープン: M件
- PR マージ: X件 / レビュー: Y件
```

感想や気づきがあるか質問する。

### Phase 2: Inbox 処理

inbox ラベルのある Issue を1件ずつ確認:

```
## Inbox 処理 (N件)

### #30 「APIレスポンスが遅い件を調査」
  作成: 3日前 / キャプチャ元テキスト: "..."

  → どうしますか？
  1. Next Action（着手可能 → Ready に移動）
  2. Project（分解が必要 → 子 Issue 作成を提案）
  3. Waiting（他者待ち → waiting ラベル）
  4. Someday（いつかやる → someday ラベル）
  5. Reference（参考情報 → コメント追記してクローズ）
  6. Delete（不要 → クローズ）
```

各 Issue について判断を求め、選択に応じてラベル変更・ステータス更新を実行。

### Phase 3: 進行中タスクの確認

In Progress のタスクを確認:

```
## 進行中タスクの棚卸し

### #20 写真アップロード機能 [In Progress / 5日間]
  最終コミット: 2日前
  → 続行 / ブロック中 / 保留 / 完了間近？
```

5日以上 In Progress のタスクは「滞留警告」を表示。

### Phase 4: Ready タスクの優先度見直し

```
## Ready タスクの優先度

現在の Ready タスク (N件):
1. #21 多頭飼い対応 [P2/M] — 3週間前に Ready
2. #25 通知設定画面 [P3/S] — 1週間前に Ready

→ 優先度の変更はありますか？
→ Someday に移動すべきものはありますか？
```

### Phase 5: レビュー待ち PR

```
## 未レビューの PR

- PR #40 by @tanaka "検索機能追加" — 2日前に依頼
  → 来週レビューする / リマインド送る / 別の人に依頼
```

### Phase 6: 来週の計画

```
## 来週の重点タスク（提案）

1. #20 写真アップロード機能 — 継続、今週中に完了目標
2. #21 多頭飼い対応 — 新規着手
3. PR #40 のレビュー — 月曜午前中

来週の重点を調整しますか？
```

## 実行サマリー

全フェーズ完了後、変更のサマリーを表示:

```
## 週次レビュー完了

### 変更内容
- Inbox 処理: 5件 → Ready: 2, Someday: 1, Closed: 2
- 滞留タスク: 1件を保留に変更
- 優先度変更: #25 P3→P2
- 来週の重点: 3タスク設定

### 来週の /morning で反映されます
```

## レビューの原則

- **対話形式**: 一方的にリストを出すのではなく、各項目で判断を求める
- **無理のないペース**: 全件一度に処理せず、フェーズごとに区切る
- **データに基づく提案**: 滞留日数、更新頻度、優先度から推奨を出す
- **承認ベース**: Issue の変更は必ず確認後に実行
