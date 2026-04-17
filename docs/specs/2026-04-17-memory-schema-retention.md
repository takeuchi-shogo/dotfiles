---
date: 2026-04-17
task: Hermes absorb Plan B1 (Memory schema / retention)
status: draft
scope: ~/.claude/agent-memory/{learnings,metrics,traces}/**/*.jsonl
references:
  - docs/research/2026-04-17-hermes-fleet-shared-memory-analysis.md
  - docs/plans/2026-04-17-hermes-absorb-plan.md
---

# Memory Schema & Retention Spec

## 目的

`~/.claude/agent-memory/` 配下の JSONL に一貫した型・保持期間・識別情報を付与し、
以下を可能にする:

1. **Retention 自動化**: 型ごとに期限が決まり、TTL 超過分を安全に pruning
2. **Semantic search 基盤**: `id` と `source` で entry を一意特定 → 将来 Qdrant 等で indexable
3. **mem0 互換**: 将来 mem0 abstraction を導入する場合も差し替え可能な interface

## 必須フィールド

すべての JSONL エントリに以下を含める:

```json
{
  "type": "event | learning | proposal | summary",
  "timestamp": "ISO8601 UTC (例: 2026-04-17T10:00:00.000000+00:00)",
  "source": "<module>/<file>  例: learner/session-learner.py",
  "id": "<uuid4 or sha256:16>  dedup / cross-ref 用",
  "retention_days": 0,
  // --- type 固有フィールドは自由 ---
}
```

- `type`: 下記 4 区分のいずれか (必須、空禁止)
- `timestamp`: UTC ISO8601 (既存 `_now_iso()` 互換)
- `source`: 生成した module 名 (path ではなくロジック上の責務)
- `id`: uuid4 または `sha256(timestamp|type|message)[:16]` で dedup
- `retention_days`: `0` = 永続。数値 = その日数経過後に pruning 対象

## Type 区分

| type | 保持期間 (retention_days) | 説明 | 用途 |
|------|--------------------------|------|------|
| `event` | 30 | セッション内の個別イベント。エラー、品質、テレメトリ等 | 直近パターン分析 |
| `learning` | 0 (永続) | 抽出済みパターン・原則・慣用ルール | 長期的な挙動改善 |
| `proposal` | 7 | AutoEvolve 改善提案 (未採用の候補含む) | 採否判断後は破棄 |
| `summary` | 0 (永続) | セッションサマリ・週次/月次まとめ | 履歴ダッシュボード |

### 判定基準

- **event**: 「その場の観測記録」。再集約可能な fact。→ 30日で破棄してよい
- **learning**: 「抽出した汎化知識」。失うと再学習コストが大きい。→ 永続
- **proposal**: 「採否判断待ち」。判断後は結果のみ learning/summary に昇格。→ 7日
- **summary**: 「集約・アーカイブ」。長期トレンド用。→ 永続

## カテゴリマッピング (既存ファイルの分類)

| ファイル | type | retention_days | 備考 |
|----------|------|----------------|------|
| `current-session.jsonl` | event | -1 (flush 時削除) | 特殊: session 内だけ |
| `traces/*.jsonl` | event | 30 | 既存 90日 → 30日へ短縮 |
| `learnings/errors.jsonl` | event | 30 | エラー発生事実 |
| `learnings/patterns.jsonl` | learning | 0 | 抽出済みパターン |
| `learnings/quality.jsonl` | event | 30 | 品質違反の発生事実 |
| `learnings/telemetry.jsonl` | event | 30 | 計測値 |
| `learnings/friction-events.jsonl` | event | 30 | 摩擦イベント |
| `learnings/review-findings.jsonl` | learning | 0 | レビュー知見 |
| `learnings/review-feedback.jsonl` | learning | 0 | レビューア有効性 |
| `learnings/skill-executions.jsonl` | event | 30 | 実行履歴 |
| `learnings/skill-credit.jsonl` | learning | 0 | スキル貢献度 |
| `learnings/skill-benchmarks.jsonl` | summary | 0 | ベンチマーク結果 |
| `learnings/strategy-outcomes.jsonl` | learning | 0 | 戦略効果 |
| `learnings/agent-invocations.jsonl` | event | 30 | 呼出履歴 |
| `learnings/patterns.jsonl` | learning | 0 | |
| `metrics/session-metrics.jsonl` | summary | 0 | セッション集約 |
| `metrics/improve-history.jsonl` | summary | 0 | 改善サイクル履歴 |
| `metrics/skill-tier-shadow.jsonl` | learning | 0 | スキル tier 推移 |
| `runs/*/proposals.yaml` | proposal | 7 | AutoEvolve 生成 |

## Retention 実施責務

| Owner | ファイル範囲 | 頻度 |
|-------|-------------|------|
| `learner/session-trace-store.py` | `traces/*.jsonl` | Stop hook ごと (既存、90 → 30 日へ変更) |
| `lifecycle/memory-prune.py` (**新規**) | `learnings/*.jsonl` (event のみ), `runs/*/proposals.yaml` | 日次 or `/improve` 内 |
| `lifecycle/memory-archive.py` (既存) | MEMORY.md のみ | 180行超過時 |

新規 `memory-prune.py` は type/retention_days を JSONL ヘッダーまたは
カテゴリマッピング表から読み取り、期限超過エントリのみ削除する。
event type のみ対象、learning/summary/proposal は per-file の扱い差異あり。

## mem0 互換 interface (保留)

将来 mem0 abstraction を導入する場合に備え、以下の操作を interface として明記:

| 操作 | 現在の実装 | mem0 互換シグネチャ |
|------|-----------|---------------------|
| `add(type, source, content, metadata)` | `emit_event(category, data)` 他 | `memory.add(messages, user_id=source, metadata={...})` |
| `search(query, filters)` | 未実装 (grep) | `memory.search(query, user_id=source, filters={type: ...})` |
| `get(id)` | 未実装 | `memory.get(memory_id)` |
| `update(id, content)` | 未実装 | `memory.update(memory_id, data)` |
| `delete(id)` | 手動 `.unlink()` | `memory.delete(memory_id)` |

現時点では file-based 実装を継続。mem0 への移行判断は B2 実験結果次第。

## Redactor Scope (A2 連携)

A2 で実装した `.config/claude/scripts/lib/redactor.py` の適用範囲は本 spec で
カバーする JSONL の **Python hook 経由 write path のみ**:

- `lib/session_events.py` (emit_event / append_to_learnings / append_to_metrics /
  emit_skill_event)
- `learner/session-trace-store.py` (_store_trace / _generate_fleet_summary)

**Out of scope** (本 redactor では保護不能):

- `~/.claude/projects/*.jsonl` — Claude Code 本体が writer、Python hook を経由しない
  - A1 audit の真陽性 3 件はこの経路由来。再発防止には **post-hoc sanitizer**
    (定期 scan → in-place redact) が必要。別タスク化 (B3 候補)
- shell redirect / `tee` 等で書かれる任意の `.jsonl`
- base64 / hex encoded secret (encoded 状態では pattern match 不能、decode 層が必要)

本 scope 境界を誤解しないこと: redactor は「hook が書いた JSONL に secret が
混入することを防ぐ」ための防御層であり、**既存 transcript の sanitize は行わない**。

## 後方互換性

- 既存 JSONL は `type`/`source`/`id`/`retention_days` が欠落しうる
- Reader 側で不在を許容し、カテゴリマッピング表から推定する (graceful degradation)
- Writer は新規書き込みから必須フィールドを付与 (漸進的)

## 実装ステップ (本 spec の外、別 PR)

1. `session_events.py` 等 writer に 4 必須フィールドを追加 (default で `type` は category から推論)
2. `lifecycle/memory-prune.py` を追加 (日次 cron or `/improve` hook で起動)
3. `traces/` の MAX_AGE_DAYS を 90 → 30 に統一
4. `learnings/*.jsonl` に対する pruning を有効化 (dry-run → 実運用)

## 撤退条件

- 必須フィールド追加で既存 reader が壊れた場合 → graceful degradation 強化 or schema バージョニング導入
- Pruning が learning type を誤って削除 → 型推論ロジック強化 + バックアップ

## 関連

- A1 audit: `docs/security/2026-04-17-jsonl-secret-audit.md`
- A2 redactor: `.config/claude/scripts/lib/redactor.py`
- Reference (short): `.config/claude/references/memory-schema.md`
