# AutoEvolve Artifacts (short reference)

AutoEvolve ループが生成・消費する artifact 一覧。詳細 schema は各ファイルの出典を参照。

## 一覧

| Artifact | 生成 | 消費 | Retention |
|----------|------|------|-----------|
| `runs/YYYY-MM-DD/proposals.jsonl` | Phase 2.5 | Phase 4 (outcome 更新), /improve 次ラン | proposal (7日) |
| `runs/YYYY-MM-DD/candidates.md` | Phase 2.0 | backlog 参照 | 7日 |
| `runs/YYYY-MM-DD/debate-log.md` | Phase 2.0 | 人間レビュー | 7日 |
| `runs/YYYY-MM-DD/winning-direction.md` | Phase 2.0 | 次ラン Phase 1.0 | 永続 |
| `runs/YYYY-MM-DD/cycle-time.json` | Phase 1.0 | run-summary.json | 永続 |
| `runs/YYYY-MM-DD/cycle-cost.json` | Phase 1.0 〜 Phase 2 末尾 | cost-gate.py, run-summary.json | 永続 |
| `agent-memory/proposal-pool.jsonl` | Phase 3 末尾 | Phase 2.0 (サンプリング) | LRU 50 件 |
| `agent-memory/improvement-backlog.md` | Phase 2.5 | 次ラン Phase 1.0 | 永続 |
| **`agent-memory/learnings/hypotheses.jsonl`** | Phase 1 (meta-analyzer) | Phase 2.0 (候補生成), Phase 2.5 (falsification 確認) | learning (永続) |

## hypotheses.jsonl

Tracer → Hypothesis registry。Reflect フェーズで観測された「なぜ失敗/成功したか」の仮説を
永続化し、Select/Evaluate 両フェーズで参照可能にする。

### 目的

- evidence_chain が「提案側」の根拠なのに対し、hypotheses は「観測側」の仮説
- Phase 2.5 Codex gate で falsification_criteria と照合し、提案が仮説を偽証できるかを判定
- 採否後に status を confirmed/refuted に更新 → 次ラン Phase 1 の学習データに

### Schema

```jsonc
{
  "type": "learning",
  "id": "HYP-YYYY-MM-DD-NNN",
  "trace_id": "session-xxx:line42 | friction-event-id | null",
  "hypothesis": "観測データから導かれた仮説 (1-2 文)",
  "falsification_criteria": "どうなれば仮説が偽証されるか (検証可能な形式)",
  "metric": "仮説を検証するメトリクス名 (例: error-fix-guides 追加後の同エラー再発率)",
  "status": "pending | confirmed | refuted | stale",
  "evidence_chain": {
    "data_points": 3,
    "confidence": 0.7,
    "specific_refs": ["..."]
  },
  "timestamp": "ISO8601 UTC",
  "resolved_at": "ISO8601 UTC | null",
  "resolved_by": "IMP-YYYY-MM-DD-NNN | null",
  "retention_days": 0
}
```

### ライフサイクル

1. **生成**: Phase 1 (meta-analyzer) が Reflect の出力として生成。既知パターン → 仮説化
   (「既知」をそのままコピペしない — 失敗モード 1 対策)
2. **消費 (Select)**: Phase 2.0 candidate 生成時、pending hypotheses を参考材料として注入
3. **消費 (Evaluate)**: Phase 2.5 Codex gate が falsification_criteria を提案と照合
4. **更新**: Phase 4 Feedback Loop で merge/revert を受けて status を更新
   - merged + metric 改善 → `confirmed` + `resolved_by` に IMP-id 記録
   - reverted or metric 悪化 → `refuted`
   - 60 日 pending のまま → `stale` にして archive

### 失敗モード 1 対策

Reflect で session-learner の出力をコピペするだけにならないよう、
meta-analyzer は以下を必須とする:

- `hypothesis` フィールドは「観測」ではなく「なぜそうなったかの推測」
- `falsification_criteria` を必ず含める (検証可能性の担保)
- 同一 trace_id に対する重複仮説は BM25 類似度で除外 (> 0.85)

## evidence_chain との関係

| 側面 | evidence_chain | hypotheses |
|------|----------------|-----------|
| 所属 | proposals.jsonl 内 | 独立 jsonl |
| 視点 | 提案側 (why this change) | 観測側 (why this pattern exists) |
| 粒度 | 1 提案 = 1 evidence_chain | 1 観測 = 1 hypothesis (多対多) |
| タイミング | Phase 2 Propose | Phase 1 Reflect |
| 役割 | 提案の根拠 | 提案の falsifier (Phase 2.5 で照合) |

提案の evidence_chain が hypothesis を引用する場合は
`evidence_chain.hypothesis_refs: ["HYP-..."]` で相互参照する。
