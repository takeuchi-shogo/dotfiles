---
status: reference
last_reviewed: 2026-04-23
---

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
| `metadata` | object | No | 任意拡張点。`parent_id`（親タスク id）、`query`、`token_usage`、`duration_ms` 等を格納。register/update_status の両方で受理 |

## 例

```jsonl
{"id":"tr-2026-03-12-0001","pattern":"async","source_skill":"research","task_description":"競合プライシング調査","status":"completed","created_at":"2026-03-12T10:00:00Z","completed_at":"2026-03-12T10:15:00Z","output_path":"docs/research/2026-03-12-competitor-pricing.md"}
{"id":"tr-2026-03-12-0002","pattern":"scheduled","source_skill":"manual","task_description":"デプロイメトリクス分析","status":"pending","created_at":"2026-03-12T14:00:00Z","cron_id":"cron-abc123"}
```

## 運用ルール

- 90日以上前の completed/cancelled エントリは自動アーカイブ対象
- レジストリは追記のみ（更新は同じ id で新しい行を追記、最新が有効）
- 機密情報は task_description に含めない

## agent-invocations.jsonl との棲み分け

dotfiles には **2 つの異なる Agent 観測ファイル** が併存している。混同を避けるために役割を明示する。

| ファイル | 目的 | 書き手 | 1 行あたりの粒度 | 寿命 |
|---|---|---|---|---|
| `~/.claude/agent-memory/task-registry.jsonl` | **明示的 lifecycle 追跡**（pending → running → completed） | 起動側スクリプト（例: `skills/autonomous/scripts/run-session.sh`）が `scripts/lib/task_registry.py` の `register()` / `update_status()` を**意図的に**呼ぶ | 1 タスク = 複数行（状態遷移ごとに append） | 90 日（自動アーカイブ） |
| `~/.claude/agent-memory/agent-invocations.jsonl` | **観測ログ**（全 Agent 呼び出しの記録） | `scripts/runtime/agent-invocation-logger.py` が PostToolUse:Agent hook で**全 Agent 呼び出しを自動記録** | 1 Agent 呼び出し = 1 行 | 別途 `scripts/runtime/error-rate-monitor.py` 等が消費 |

### どちらに書くべきか

```
タスクのライフサイクルを追跡したい (pending/running/completed の状態遷移)
  → task-registry.jsonl
  → scripts/lib/task_registry.py の register() / update_status() を呼ぶ
  → 例: /autonomous の各セッション、CronCreate で予約した scheduled タスク

Agent 呼び出し自体の観測（誰がどの subagent を呼んだか・モデル・所要時間）
  → agent-invocations.jsonl
  → 何もしなくていい（PostToolUse:Agent hook が自動記録）
  → 例: skill-audit の Dominant tier 検出、cascade 分析、AutoEvolve 集計
```

### 重複させない原則

- **task-registry.jsonl は全 Agent 呼び出しを記録しない**。短寿命の Sync subagent は registry に書かない（観測なら agent-invocations.jsonl で十分）
- **agent-invocations.jsonl は lifecycle を持たない**。1 行 = 1 イベントの append-only 観測ログであり、status の遷移を表現しない
- **新規 PostToolUse:Agent hook を追加して task-registry に書くのはアンチパターン** — agent-invocations.jsonl と完全に同じ入力（PostToolUse:Agent payload）を扱うことになり重複する。register が必要な async/scheduled タスクは**起動側スクリプトから明示的に register()** を呼ぶこと

### 現在の write 経路

| 経路 | 書き先 | トリガー |
|---|---|---|
| `skills/autonomous/scripts/run-session.sh` | task-registry.jsonl | autonomous セッションの開始/完了 |
| `skills/research/SKILL.md` workflow | task-registry.jsonl | `/research` 起動時に `register()`、subagent dispatch 時は `metadata={"parent_id": ...}` で紐付け |
| `skills/loop/SKILL.md` workflow | task-registry.jsonl | `/loop` 起動時に `register()`、各 iteration 完了時に `update_status()` の metadata 更新 |
| `scripts/runtime/agent-invocation-logger.py` | agent-invocations.jsonl | PostToolUse:Agent hook（全 Agent 呼び出し） |

> **Empirical state (2026-04-12 時点)**: `~/.claude/agent-memory/task-registry.jsonl` の実ファイルは未生成の場合がある。これは「実装空白」ではなく、autonomous セッションが未起動である状態を指す。`task_registry.register()` 自体は `skills/autonomous/scripts/run-session.sh` から呼び出される実装が完成しており、autonomous 起動時に生成される。`/research`, `/loop` 等の他 async ランナーから register したい場合は、各ランナーの起動時点で `task_registry.register()` を**明示的に呼ぶ**実装追加が必要（PostToolUse hook で代替してはいけない — 上記「重複させない原則」参照）。

### 関連ドキュメント

- `references/subagent-delegation-guide.md § タスクレジストリ` — task_registry.py の API リファレンス
- `references/multi-agent-coordination-patterns.md § Pattern 3 Agent Teams` — 5-Pattern View での位置づけ
