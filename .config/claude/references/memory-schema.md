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

## Session-Independent Durable State

session memory (会話 context) と長期 state の境界。複数セッション跨ぎで参照される state は session memory に置かず、外部 store に逃がす。

| 種別 | 置き場 | 寿命 | 例 |
|------|--------|------|-----|
| **session memory** | LLM context window | 揮発 (Compact/Clear で消失) | 現在の作業内容、TaskList、直近の Read 結果 |
| **session-bound persistent** | `~/.claude/agent-memory/**/*.jsonl` | 上表の retention に従う | event/learning/proposal/summary |
| **session-independent durable** | MCP state, 外部 DB, git-tracked files | 永続 | resume anchor (HANDOFF/Plan), プロジェクト spec, ADR |

### MCP state vs session memory の判断基準

state を session memory に置いてよい条件:
- 現在のセッション内でのみ参照される
- 中断・compact で失っても再構築コストが低い
- ユーザー対話で都度確認可能

外部 store (MCP / ファイル) に逃がすべき条件:
- 複数セッション・複数 agent 跨ぎで参照される
- 失うと再収集コストが大きい (= learning や spec)
- 機械的 (hook/gate/CI) に参照される必要がある

**判断ヒント**: 「次のセッションがこの state を必要とするか？」を問う。Yes なら必ず外部 store。

### 由来

「How I got banned from GitHub due to my harness pipeline」(2026-04) — session-independent state を session memory に置いて compact で失った事例の翻訳。AutoEvolve learnings はこの原則で永続化されている。
