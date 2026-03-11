---
name: meeting-minutes
description: 会議の議事録やメモから決定事項・アクション項目を抽出し、GitHub Issues の更新を提案する。承認後に一括反映。定例会議後の処理を自動化。
disable-model-invocation: true
allowed-tools: Bash(gh *), Read
argument-hint: "<meeting notes or file path>"
---

# Meeting Minutes Processor

会議の議事録からアクション項目を抽出し、GitHub Issues を一括更新する。

## 設定確認

!`cat .claude/dev-ops.local.json 2>/dev/null || echo "NOT_CONFIGURED"`

上記が `NOT_CONFIGURED` の場合:
「開発オペレーション設定がまだありません。`/dev-ops-setup` を実行してセットアップしてください。」と案内して終了。

## 入力

`$ARGUMENTS` から議事録テキストを受け取る。

- テキスト直接入力: `/meeting-minutes 佐藤: 体重記録のグラフ表示がマージされました...`
- ファイルパス: `/meeting-minutes /path/to/minutes.md`（ファイルの場合は Read で読み込む）
- 引数なし: 「議事録のテキストを貼り付けてください」と質問

## 処理フロー

### Step 1: カンバン現状確認

```bash
gh project item-list {project_number} --owner {owner} --format json --limit 100
```

または GitHub Projects がない場合:
```bash
gh issue list --state open --json number,title,labels,assignees --limit 50
```

### Step 2: 議事録から情報抽出

以下のカテゴリで情報を抽出:

1. **決定事項**: 合意された方針・仕様変更
2. **アクション項目**: 誰が何をいつまでに
3. **進捗報告**: 完了・進行中の作業
4. **要件変更**: スコープや仕様の変更
5. **優先度変更**: タスクの優先度調整
6. **新規タスク**: 新しく発生したタスク

### Step 3: 更新計画を提案

抽出結果を構造化して表示し、**必ずユーザーの承認を待つ**:

```
## 議事録処理結果

### クローズ予定
- #15 ペットの体重記録グラフ表示 → Done

### 新規 Issue 作成
- 「ワクチン接種リマインダー機能」Priority: P1 / Size: M
  アサイン: @tanaka

### 優先度変更
- #20 写真アップロード機能: P1 → P2
  理由: リマインダー機能を優先

### コメント追加
- #16 に「デザインレビュー完了、再実装待ち」を追記
- #21 に「仕様確定: 最大5頭まで対応」を追記

### ステータス変更
- #18 Ready → In Progress（@suzuki が着手）

---
上記の変更を実行しますか？ (y/n/個別選択)
```

### Step 4: 承認後に実行

ユーザーが承認した項目のみ実行:

```bash
# Issue クローズ
gh issue close {N} --comment "議事録より: {reason}"

# 新規 Issue 作成
gh issue create --title "{title}" --body "{body}" --label "{labels}" --assignee "{assignee}"

# コメント追加
gh issue comment {N} --body "{comment}"

# ステータス変更
gh project item-edit --project-id {project_id} --id {item_id} \
  --field-id {status_field_id} --single-select-option-id {option_id}
```

### Step 5: 実行結果サマリー

```
## 実行完了

- クローズ: 1件 (#15)
- 新規作成: 1件 (#30 ワクチン接種リマインダー機能)
- コメント追加: 2件 (#16, #21)
- ステータス変更: 1件 (#18)
- スキップ: 0件
```

## 安全規則

- **承認なしに Issue の変更を実行しない**（最重要）
- 個別選択モードでは、各変更ごとに y/n を確認
- 大量の変更（10件超）の場合は特に慎重に確認を促す
- 実行前にドライランとして `gh` コマンドを表示する選択肢も提供
