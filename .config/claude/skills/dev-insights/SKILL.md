---
name: dev-insights
description: "Use when analyzing development patterns data-driven — commit frequency, issue completion rate, day-of-week performance, stale task trends. Visualizes metrics and suggests improvements. Triggers: '開発分析', 'コミット頻度', 'パフォーマンス分析', '滞留タスク', 'dev metrics'. Do NOT use for: daily status (use daily-report), weekly task review (use weekly-review)."
disable-model-invocation: true
allowed-tools: Bash(gh *), Read, Grep, Glob
argument-hint: "[weekly | monthly | custom-range]"
metadata:
  pattern: reviewer
---

# Development Insights

開発データを分析し、パターンと改善ポイントを可視化する。

## 設定確認

!`cat .claude/dev-ops.local.json 2>/dev/null || echo "NOT_CONFIGURED"`

上記が `NOT_CONFIGURED` の場合:
「開発オペレーション設定がまだありません。`/dev-ops-setup` を実行してセットアップしてください。」と案内して終了。

## 分析期間

`$ARGUMENTS` に応じて期間を設定:
- `weekly`（デフォルト）: 過去7日間
- `monthly`: 過去30日間
- `YYYY-MM-DD..YYYY-MM-DD`: カスタム範囲

## データ収集（並列実行）

```bash
# 1. コミット履歴
git log --oneline --since="{start_date}" --author="{my_username}" --no-merges \
  --format="%H|%ad|%s" --date=format:"%Y-%m-%d %H:%M %a" | head -200

# 2. クローズした Issue
gh issue list --assignee {my_username} --state closed \
  --json number,title,labels,createdAt,closedAt --limit 100 \
  | jq '[.[] | select(.closedAt >= "{start_date}")]'

# 3. マージした PR
gh pr list --author {my_username} --state merged \
  --json number,title,additions,deletions,mergedAt,createdAt --limit 50 \
  | jq '[.[] | select(.mergedAt >= "{start_date}")]'

# 4. 現在オープンな Issue（滞留分析用）
gh issue list --assignee {my_username} --state open \
  --json number,title,labels,createdAt,updatedAt --limit 100

# 5. レビューした PR
gh pr list --search "reviewed-by:{my_username}" --state merged \
  --json number,title,mergedAt --limit 30 \
  | jq '[.[] | select(.mergedAt >= "{start_date}")]'
```

## 分析項目

### 1. アクティビティサマリー

```
## 開発アクティビティ ({period})

| 指標 | 値 | 前期比 |
|------|-----|-------|
| コミット数 | 45 | +12% |
| Issue 完了 | 8 | -2 |
| PR マージ | 6 | +1 |
| PR レビュー | 4 | +2 |
| コード追加行 | 1,200 | — |
| コード削除行 | 800 | — |
```

### 2. 曜日別パフォーマンス

コミットを曜日別に集計し、パターンを分析:

```
## 曜日別コミット数

Mon ████████████ 12
Tue ██████████████ 14
Wed █████████ 9
Thu ███████████ 11
Fri ████ 4
Sat ██ 2
Sun  0

💡 金曜のコミットが少なめ — 週末前の整理に時間を使っている可能性
```

### 3. 時間帯別アクティビティ

```
## 時間帯別コミット数

06-09 ████ 4
09-12 ██████████████ 14
12-15 ████████ 8
15-18 ████████████ 12
18-21 ████████ 8
21-24 ██ 2

💡 午前中が最も生産的 — 集中タスクは午前に配置推奨
```

### 4. タスク完了リードタイム

Issue の作成→クローズまでの日数を分析:

```
## タスク完了リードタイム

| サイズ | 平均日数 | 中央値 | 最大 |
|--------|---------|--------|------|
| S | 2.1 | 1 | 5 |
| M | 5.3 | 4 | 12 |
| L | 12.7 | 10 | 25 |

💡 M サイズのタスクのばらつきが大きい — 見積もり精度に改善余地
```

### 5. 滞留タスク分析

```
## 滞留タスク（14日以上オープン）

- #12 「検索の全文対応」 [P2/L] — 28日間オープン
  最終更新: 15日前 / ブロッカー？
- #19 「パフォーマンス改善」 [P3/M] — 21日間オープン
  最終更新: 21日前 / Someday 候補？

💡 2件が2週間以上滞留 — /weekly-review で棚卸しを推奨
```

### 6. 繰り越し常連ランキング

```
## よく繰り越されるタスク

1. #12 検索の全文対応 — 4週連続 Ready のまま
2. #19 パフォーマンス改善 — 3週連続

💡 着手しないなら Someday に移動、または分解を検討
```

## 改善提案

分析結果から具体的な改善アクションを3つまで提案:

```
## 改善提案

1. **金曜の生産性**: 金曜午前に小タスク（S/P3）を集中させ、午後はレビュー・整理に充てる
2. **Mサイズの見積もり**: 5日超えたら分解を検討するルールを追加
3. **滞留タスク対策**: 2週間 Ready のままのタスクは自動で Someday ラベルを検討
```

## AutoEvolve 連携

分析結果を AutoEvolve learnings に emit（既存の `session_events.py` を活用）:
- カテゴリ: `dev-insights`
- データ: 主要指標のスナップショット
- 用途: `/improve` での長期トレンド分析に活用
