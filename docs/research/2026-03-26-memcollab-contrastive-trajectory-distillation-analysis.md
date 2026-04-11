---
source: "MemCollab: Cross-Agent Memory Collaboration via Contrastive Trajectory Distillation (arXiv:2603.23234)"
date: 2026-03-26
status: integrated
---

## Source Summary

**Title:** MemCollab: Cross-Agent Memory Collaboration via Contrastive Trajectory Distillation
**Authors:** Yurui Chang, Yiran Wu, Qingyun Wu, Lu Lin (Penn State / AG2AI)
**Date:** 2026-03-25

### Main Claims

異種 LLM エージェント間でメモリを直接転送すると性能が低下する（エージェント固有バイアスが混入するため）。同じタスクに対する成功/失敗の推論軌跡を**対比的に蒸留**し、エージェント非依存の**規範的制約**（enforce X; avoid Y）として共有メモリを構築すれば、弱いモデルも強いモデルも一貫して改善する。

### Key Techniques

1. **Contrastive Trajectory Distillation** — 同一タスクに対する 2 エージェントの軌跡を対比し、violation patterns（失敗パターン）と reasoning invariants（推論不変条件）を抽出
2. **Normative Constraint Format** — `mk = (enforce ik; avoid vk)` の対形式。抽象的な推論原則であり、生のソリューションではない
3. **Task-Category-Aware Retrieval** — タスクをカテゴリ/サブカテゴリに分類し、同カテゴリのメモリのみを検索。p=3 が最適（非単調: p>threshold で性能低下）
4. **Agent-Agnostic Memory** — モデル固有バイアスを除去した共有メモリバンク。全エージェントが再利用可能
5. **Cross-Architecture Contrast** — 異アーキテクチャ間の対比が同族対比を上回るケースあり（Qwen32B+LLaMA8B: 95.2% vs Qwen32B+Qwen7B: 93.6%）
6. **Spatial Pruning Effect** — エラーパターンが探索空間を刈り込み、推論ターン数を削減（MATH500: 2.7→2.2 turns）

### Evidence

| Backbone | Baseline | MemCollab | Delta |
|----------|----------|-----------|-------|
| Qwen-2.5-7B (MATH500) | 52.2% | 67.0% | +14.8pt |
| Qwen-2.5-32B (MATH500) | 63.8% | 73.8% | +10.0pt |
| Llama-3-8B (MATH500, cross-family) | 27.4% | 42.4% | +15.0pt |
| Qwen-2.5-7B (MBPP) | 47.9% | 57.6% | +9.7pt |

- 直接転送 (w/ Memory(32B)→7B) は baseline 以下になるケースあり（MATH500: 50.6% vs 52.2%）
- Self-Contrast Memory は MemCollab に劣後（クロスエージェント対比の優位性）
- 推論ターン数削減: 全ベンチマークで vanilla より少ないターンで高い精度

### Prerequisites

- 2 つ以上の異種エージェントが同一タスクに取り組む環境
- 正解判定機能（indicator model）
- 蒸留を行う backbone model

---

## Gap Analysis

### Gap / Partial / N/A

| # | Technique | Verdict | Current State |
|---|-----------|---------|---------------|
| 1 | Contrastive Trajectory Distillation pipeline | **Gap** | No mechanism to contrast success/failure trajectories across agents |
| 2 | "Enforce X; Avoid Y" paired normative constraints | **Partial** | `failure-taxonomy.md` has Avoid patterns (FM-001~020). No corresponding Enforce (reasoning invariants) |
| 3 | Task-category-aware memory retrieval | **Partial** | MEMORY.md manually organized by topic. No automatic task classification → category-conditioned retrieval |
| 4 | Normative constraint distillation from review disagreements | **Gap** | Disagreements escalated to user. No process to extract transferable constraints from them |

### Already Items Strengthening Analysis

| # | Existing Mechanism | Paper's Insight | Strengthening |
|---|-------------------|-----------------|---------------|
| A1 | `cross-model-insights.md` per-model insights | Per-model memory degrades when transferred (Fig 1) | Add "Shared Normative Constraints" section |
| A2 | `failure-taxonomy.md` FM-001~020 | One-sided "avoid" format. Missing paired "enforce" invariants | Add Reasoning Invariant field to each FM |
| A3 | `review-consensus-policy.md` §1 Heterogeneous Signal Priority | Cross-architecture contrast > same-family (95.2% vs 93.6%) | Add empirical evidence from MemCollab |
| A4 | `cross-model-insights.md` Shared Blind Spots | Fig 1: naive cross-model transfer degrades performance | Add "Agent-Specific Bias Entanglement" pattern |
| A5 | Memory retrieval guidance | p=3 optimal, non-monotonic degradation | Add retrieval budget guidance to workflow-guide.md |

---

## Integration Decisions

All items selected for integration (user chose "all" for both Gap/Partial and Already strengthening).

### Phase 1: Document Updates (same session)

- T1: `failure-taxonomy.md` — Add Reasoning Invariant field to each FM (merges #2 + A2)
- T2: `cross-model-insights.md` — Add "Shared Normative Constraints" section + "Agent-Specific Bias Entanglement" pattern (A1 + A4)
- T3: `review-consensus-policy.md` — Add cross-architecture contrast empirical data (A3)
- T4: `workflow-guide.md` — Add memory retrieval budget guidance (A5)

### Phase 2: Mechanism Changes (future session)

- T5: Contrastive distillation from review disagreements (#1 + #4) — `/review` or `/analyze-tacit-knowledge` に対比蒸留ステップを追加
- T6: Task-category-aware memory retrieval (#3) — `session-load.js` or memory system enhancement
