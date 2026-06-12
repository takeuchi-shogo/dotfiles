---
status: active
last_reviewed: 2026-04-23
---

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

## verification_status (任意フィールド)

> 出典: Fable 5 14-steps absorb (2026-06-12) — 5段階メモリ進行の「Verify=検証済み事実化 / Consult=再導出せず参照」を薄い軸として翻訳。新規ループは作らない。

`learning` / `summary` に任意で付与する信頼度ラベル。「仕組みの記録」と「検証済みの事実」を区別し、未検証仮説を事実として consult する事故を防ぐ。

```json
{ "verification_status": "verified | hypothesis | stale | retracted" }
```

| 値 | 意味 | consult 時の扱い |
|----|------|----------------|
| `verified` | 実行・観測・公式 docs で裏取り済み (裏取り方法を detail に残す) | 再導出せず参照してよい |
| `hypothesis` | もっともらしいが未検証 (session summary 由来は原則これ) | 採用前に裏取りする |
| `stale` | 検証済みだったが前提が変わった疑い (バージョン更新等) | 再検証してから使う |
| `retracted` | 誤りと判明。反証を detail に残して保持 (再学習防止) | 参照しない (反証の根拠としてのみ) |

運用ルール:
- **欠落 = `hypothesis` 扱い** (reader 側 graceful degradation、既存 JSONL の後方互換)
- 昇格 (`hypothesis` → `verified`) には裏取りの根拠 1 行を必須にする — 「似た記述を見た」は裏取りではない
- Markdown メモリ (memory/*.md, HANDOFF) では frontmatter ではなく本文に「検証済み:」「仮説:」の接頭辞で表現してよい (薄い軸を重いスキーマにしない)

## 既存カテゴリ簡易マッピング

- `traces/*.jsonl`, `learnings/{errors,quality,telemetry,friction-events,skill-executions,agent-invocations}.jsonl` → **event (30日)**
  - `friction-events.jsonl` の `friction_class` 値例: `environment_blocker`, `validation_ping_pong`, `webfetch_truncation_observation` (manual sampling), `webfetch_truncation_suspect` (auto via `runtime/webfetch-truncation-detector.py`)
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
