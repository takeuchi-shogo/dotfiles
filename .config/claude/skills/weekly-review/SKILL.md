---
name: weekly-review
description: >
  GTD式の週次レビュー。GitHub Issue + Obsidian 00-Inbox/ + vault-maintenance report の棚卸し、滞留タスク検出、優先度見直しを対話形式で実施。週末や週明けに使用。
  Triggers: '週次レビュー', 'weekly-review', '棚卸し', '今週の振り返り', 'weekly review'.
  Do NOT use for: 朝の計画（use /morning）、日報（use /daily-report）、夕方の振り返り（use /timekeeper review）。
origin: self
disable-model-invocation: true
allowed-tools: Bash(gh *), Bash(ls *), Bash(cat *), Read, Grep, Glob
metadata:
  pattern: generator
---

## Skill Assets

- `templates/weekly-report.md` — Weekly report template (achievements, in-progress, blockers, next week plan, metrics)

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

### Phase 2.5: Obsidian Inbox + vault-maintenance report 処理

GitHub Issue inbox とは別に、Obsidian Vault 側の Inbox と保守レポートも決定ループに吸い上げる。Codex 2026-04-21 批評「report が誰の inbox に入り、いつ裁かれるか」指摘を反映。

#### 2.5.1 Vault `00-Inbox/` の triage

```bash
# Vault パス検出 (環境変数 or 既定パス)
VAULT_PATH="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# 未処理 Inbox ノート一覧
ls -lt "$VAULT_PATH/00-Inbox/" 2>/dev/null | head -20
```

各ノートを 1 件ずつ確認:

```
## Obsidian Inbox 処理 (N件)

### 00-Inbox/2026-04-18-idea-xxx.md
  作成: 3日前 / 最初の行: "..."

  → どうしますか？
  1. Literature Note 化（05-Literature/ に移動）
  2. Permanent Note 化（02-Permanent/ に昇格）
  3. 次のアクションに変換（GitHub Issue 化 or TODO 追加）
  4. Someday（Inbox 内で `tag: someday` 付与）
  5. 削除
```

選択に応じて移動 or アーカイブを提案（実行はユーザー承認後）。

#### 2.5.2 vault-maintenance report の吸収

```bash
# 直近の vault-maintenance.sh report を確認
ls -lt "$VAULT_PATH/00-Inbox/vault-maintenance-"*.md 2>/dev/null | head -3
```

最新 report を読み、以下の 4 項目それぞれを決定ループへ:

```
## Vault 保守 report (YYYY-MM-DD)

### 孤立ノート (N件)
  → リンク追加 / アーカイブ / 削除 を判断

### リンク切れ (N件)
  → 修正 / 削除 を判断

### Stale Seed (N件)
  → 展開 / アーカイブ を判断

### 重複候補 (N件)
  → マージ / 個別化 を判断
```

**重要 (Codex 指摘)**: report を読んで終わりにせず、各項目を Horizon 1 decisions（来週の具体アクション）に変換する。変換できない項目は「Someday」か「削除候補」に分類。

#### 2.5.3 統合後の分類

Phase 2.5 の結果は Phase 6「来週の計画」で Horizon 1 タスクとして組み込む。

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

### Phase 5.5: Horizon 5 — Life Review (軽量, 2-3問のみ)

Career/Product/Tech の外側を**週次で軽く**点検する。心理カウンセリングではなく、TELOS の Horizon 5 (長期目的) に接続する事実確認のみ。**各質問 1 行で答えて OK、詳細を求めない。スキップ自由**。

```
## Horizon 5 — 今週の生活点検

Q1: 今週の最重要 Non-negotiables (/timekeeper plan で設定した3つ) の達成率はどれくらい？ ざっくり%で。
Q2: Career/Product 以外の領域（健康/関係/休養/学習）で、無視できない信号はあったか？ 1行で。
Q3: 来週、どれか1つだけ継続強化するとしたら何？
```

- 「特になし」も有効な回答。深掘りしない
- **Anti-Pattern**: 9ドメイン全部を毎週聞かない (performative audit trap)。3問で終わる
- この記録は `~/.claude/skill-data/weekly-review/horizon5.jsonl` に append-only で蓄積し、四半期に一度 TELOS Goals の見直しに使う

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

## Anti-Patterns

| NG | 理由 |
|----|------|
| 全 Issue を一度にクローズ判断する | 疲労で誤判断が増える。フェーズごとに区切る |
| 滞留タスクを放置して新規だけ見る | 技術的負債が蓄積する。棚卸しが週次レビューの核 |
| 週次レビューを2週以上スキップする | inbox が溢れて GTD が崩壊する。最低隔週で実施 |
