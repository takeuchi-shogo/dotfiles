# Memory Schema (short reference)

`~/.claude/agent-memory/**/*.jsonl` の型・保持期間。詳細: [`docs/specs/2026-04-17-memory-schema-retention.md`](../../../docs/specs/2026-04-17-memory-schema-retention.md)。AutoEvolve 固有 artifact は [`autoevolve-artifacts.md`](./autoevolve-artifacts.md) 参照。

## 必須フィールド

```json
{
  "type": "event | learning | proposal | summary",
  "timestamp": "ISO8601 UTC",
  "source": "<module>/<file>",
  "id": "uuid4 or sha256:16",
  "retention_days": 0
}
```

## Type → 保持期間

| type | retention_days | 用途 |
|------|----------------|------|
| `event` | 30 | 個別イベント (エラー、品質、telemetry) |
| `learning` | 0 (永続) | 抽出済みパターン・原則 |
| `proposal` | 7 | AutoEvolve 改善提案 |
| `summary` | 0 (永続) | セッション/週次まとめ |

## 判定ルール

- **event**: 再集約可能な fact。30日で破棄してよい
- **learning**: 失うと再学習コスト大。永続
- **proposal**: 採否後は learning/summary に昇格、原本は破棄
- **summary**: 長期トレンド用、永続

## 既存カテゴリ簡易マッピング

- `traces/*.jsonl`, `learnings/{errors,quality,telemetry,friction-events,skill-executions,agent-invocations}.jsonl` → **event (30日)**
- `learnings/{patterns,review-findings,review-feedback,skill-credit,strategy-outcomes,hypotheses}.jsonl`, `metrics/skill-tier-shadow.jsonl` → **learning (永続)**
- `metrics/{session-metrics,improve-history}.jsonl`, `learnings/skill-benchmarks.jsonl` → **summary (永続)**
  - `skill-benchmarks.jsonl` 追加フィールド (T4 Autogenesis): `task_category: retrieval|generation|gate` (default: `generation`), `model_tier: weak|strong` (default: `strong`)。ceiling detection (baseline >= 0.9, delta < 0.03) で使用
- `runs/*/proposals*.yaml` → **proposal (7日)**

## Retention 実施

| Owner | 対象 |
|-------|------|
| `learner/session-trace-store.py` | `traces/*.jsonl` (30日, 既存) |
| `lifecycle/memory-prune.py` (予定) | `learnings/*.jsonl` (event のみ), `runs/*/proposals*.yaml` |
| `lifecycle/memory-archive.py` (既存) | MEMORY.md (180行超過) |

## 後方互換

既存 JSONL は必須フィールド欠落しうる。Reader は graceful degradation
(カテゴリマップから推定)。Writer は新規書き込みから段階的に付与。
