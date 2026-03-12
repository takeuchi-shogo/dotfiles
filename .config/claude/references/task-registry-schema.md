# タスクレジストリ スキーマ

Async/Scheduled サブエージェントの成果物を追跡する軽量レジストリ。

## 保存先

`~/.claude/agent-memory/task-registry.jsonl`

## スキーマ

各行は1つの JSON オブジェクト:

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string | Yes | 一意識別子（`tr-YYYY-MM-DD-NNNN`） |
| `pattern` | string | Yes | `sync` / `async` / `scheduled` |
| `source_skill` | string | Yes | 起動元スキル（`review`, `research`, `autonomous`, `manual`） |
| `task_description` | string | Yes | タスクの概要（1行） |
| `status` | string | Yes | `pending` / `running` / `completed` / `failed` / `cancelled` |
| `created_at` | string | Yes | ISO 8601 タイムスタンプ |
| `completed_at` | string | No | ISO 8601 タイムスタンプ |
| `output_path` | string | No | 成果物のファイルパス |
| `agent_id` | string | No | Agent ツールの agent ID（resume 用） |
| `cron_id` | string | No | CronCreate の ID（Scheduled 用） |
| `error` | string | No | 失敗時のエラーメッセージ |

## 例

```jsonl
{"id":"tr-2026-03-12-0001","pattern":"async","source_skill":"research","task_description":"競合プライシング調査","status":"completed","created_at":"2026-03-12T10:00:00Z","completed_at":"2026-03-12T10:15:00Z","output_path":"docs/research/2026-03-12-competitor-pricing.md"}
{"id":"tr-2026-03-12-0002","pattern":"scheduled","source_skill":"manual","task_description":"デプロイメトリクス分析","status":"pending","created_at":"2026-03-12T14:00:00Z","cron_id":"cron-abc123"}
```

## 運用ルール

- 90日以上前の completed/cancelled エントリは自動アーカイブ対象
- レジストリは追記のみ（更新は同じ id で新しい行を追記、最新が有効）
- 機密情報は task_description に含めない
