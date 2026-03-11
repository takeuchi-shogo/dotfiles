---
name: kanban
description: GitHub Projects カンバンの操作と進捗確認。ステータス変更、進捗一覧表示、Issue の開始/完了処理を自動化。「次は何したらいい？」にも応答。
disable-model-invocation: true
allowed-tools: Bash(gh *), Read
argument-hint: "[status | start #N | done #N | view]"
---

# Kanban Operations

GitHub Projects カンバンの操作と進捗確認を行う。

## 設定確認

!`cat .claude/dev-ops.local.json 2>/dev/null || echo "NOT_CONFIGURED"`

上記が `NOT_CONFIGURED` の場合:
「開発オペレーション設定がまだありません。`/dev-ops-setup` を実行してセットアップしてください。」と案内して終了。

## コマンド

`$ARGUMENTS` に応じて以下を実行:

### `/kanban` または `/kanban view` — カンバン一覧表示

```bash
gh project item-list {project_number} --owner {owner} --format json --limit 100
```

結果をステータス別にグループ化して表示:

```
## カンバン: {team_name} ({date})

### In Progress (2)
- #15 ペットの体重記録グラフ表示 [P1/M] @takeuchishougo
- #18 ログイン画面リファクタ [P2/S] @teammate

### In Review (1)
- #16 フード管理画面UI [P1/S] → PR #32

### Ready (3)
- #20 写真アップロード機能 [P1/L]
- #21 多頭飼い対応 [P2/M]
- #25 通知設定画面 [P3/S]

### Backlog (5)
- ...（省略、件数のみ表示）
```

チームラベルが設定されている場合、そのラベルを持つアイテムのみ表示。

### `/kanban start #N` — タスク開始

1. Issue #{N} のステータスを「In Progress」に変更
2. 自分をアサイン（未アサインの場合）

```bash
# ステータス変更
gh project item-edit --project-id {project_id} --id {item_id} \
  --field-id {status_field_id} --single-select-option-id {in_progress_option_id}

# アサイン
gh issue edit {N} --add-assignee {my_username}
```

確認メッセージ: `#N を In Progress に変更しました。`

### `/kanban done #N` — タスク完了

1. Issue #{N} のステータスを「Done」に変更
2. Issue をクローズ

```bash
gh project item-edit --project-id {project_id} --id {item_id} \
  --field-id {status_field_id} --single-select-option-id {done_option_id}
gh issue close {N}
```

確認メッセージ: `#N を Done に変更し、クローズしました。`

### `/kanban review #N` — レビューへ移動

1. Issue #{N} のステータスを「In Review」に変更

### `/kanban status` — 自分の担当状況

自分にアサインされたアイテムのみフィルタして表示。

### `/kanban next` — 次のタスク提案

Ready ステータスのアイテムから、優先度・サイズ・依存関係を考慮して次に着手すべきタスクを提案。

## GitHub Projects がない場合

`project` 設定が `null` の場合、GitHub Issues のラベルとアサインで代替:

- `start`: `in-progress` ラベル追加 + アサイン
- `done`: Issue クローズ
- `view`: オープンな Issue をラベル別に一覧
- `review`: `in-review` ラベル追加

## 安全規則

- **ステータス変更前に現在のステータスを表示**し、意図通りか確認
- **Done への変更は Issue クローズを伴う**ため、必ず確認を取る
- **他人にアサインされた Issue の操作**は警告を表示
