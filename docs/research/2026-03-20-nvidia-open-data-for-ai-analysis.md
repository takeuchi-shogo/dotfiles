---
source: https://huggingface.co/blog/nvidia/open-data-for-ai
date: 2026-03-20
status: integrated
---

## Source Summary

**Title**: How NVIDIA Builds Open Data for AI (2026-03-10)

**Main thesis**: AI progress depends on data quality, not just model capability. NVIDIA addresses the AI-data bottleneck by releasing permissively licensed datasets (2+ PB, 180+ datasets, 650+ models) alongside training recipes and evaluation frameworks.

**Key techniques**:
- Extreme Co-Design: Data + Method + Eval をセットで公開し、コミュニティフィードバックで反復改善
- Synthetic persona generation: 人口統計分布に基づく合成ペルソナ（日本6M, 米国6M, インド21M等）
- CLIMB algorithm: embedding クラスタリング + 反復精製でデータミックス最適化（H100計算時間33%削減）
- Agentic safety labeling: ツール使用ワークフローの11Kラベル付きテレメトリトレース
- Domain-specific post-training: structured conversation / math proofs / agentic / SWE の4カテゴリ

**Evidence**:
- CrowdStrike: NL->CQL 精度 50.7% -> 90.4%
- NTT Data: 法律QA 15.3% -> 79.3%
- APTO: 攻撃成功率 7% -> 0%
- ClimbMix: Time-to-GPT-2 leaderboard で最大改善

**Prerequisites**: モデル学習基盤を持つ組織向け。本ハーネスへの適用はパターン・設計思想レベル。

## Gap Analysis

| # | Topic | Status | Current State | Gap |
|---|-------|--------|---------------|-----|
| 1 | Synthetic data / personas | N/A | Scope outside | - |
| 2 | Data quality / curation | Partial | `setup_health.py`, `retroactive_scorer.py` | No cleaning/normalization pipeline |
| 3 | Agentic safety datasets | Partial | `agency-safety-framework.md`, `gaming-detector.py` | No tool-use safety taxonomy |
| 4 | RL data / training | Already | `rl-optimization-guide.md`, `rl_advantage.py` | - |
| 5 | Retrieval / RAG | Partial | MCP context server | No embedding fine-tuning |
| 6 | Benchmark / evaluation | Already | 6-dimension benchmark, TPR/TNR | - |
| 7 | Protein / biology | N/A | Scope outside | - |
| 8 | Robotics / driving | N/A | Scope outside | - |
| 9 | Open data strategy | Partial | OSS survey exists | No formal strategy |
| 10 | Speculative decoding | N/A | Claude API handles inference | - |
| 11 | Pre-training mixing / CLIMB | N/A | No pre-training | - |
| 12 | Multi-step planning | Already | `/spec`, `/spike`, `/epd`, blueprint DAG | - |
| 13 | SWE instruction tuning | Partial | SWE-CI survey, language rules | No systematic data collection |

## Integration Decisions

All 4 items selected for integration:

1. **[Partial -> Integrated] Agentic safety taxonomy** - Add tool-use safety patterns to `agency-safety-framework.md`
2. **[Partial -> Integrated] Data domain classification** - Add `_classify_data_domain()` to `session-learner.py`
3. **[Gap -> Integrated] Co-Design cycle pattern** - Create `references/co-design-cycle.md`
4. **[Partial -> Integrated] SWE data collection** - Covered by domain classification in item 2

## Plan

| Task | File | Size | Dependency |
|------|------|------|------------|
| 1 | This report | S | - |
| 2 | `references/agency-safety-framework.md` | S | - |
| 3 | `scripts/learner/session-learner.py` | S | - |
| 4 | `references/co-design-cycle.md` | S | - |
| 5 | MEMORY.md pointer | S | 1 |

Overall size: **M** (4 files modified/created)
