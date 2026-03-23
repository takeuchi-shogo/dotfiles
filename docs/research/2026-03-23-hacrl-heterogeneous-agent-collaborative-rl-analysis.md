---
source: https://arxiv.org/abs/2603.02604
date: 2026-03-23
status: analyzed
---

## Source Summary

**Title**: Heterogeneous Agent Collaborative Reinforcement Learning (HACRL)
**Authors**: Zhang et al. (10 authors), arXiv 2603.02604, 2026-03-04

### Main Claim

Heterogeneous LLM agents (different checkpoints, sizes, architectures) can share rollouts during training to mutually improve, while operating independently at inference time. The proposed HACPO algorithm achieves +3.3% average improvement over GSPO while using only half the rollout cost.

### Key Techniques

1. **Agent-Capability-Aware Advantage Estimation**: Capability ratio omega^(k,j) = P_hat^(k) / P_hat^(j) weights the mixed baseline by relative agent strength. Without this, AIME2025 performance drops -44%.
2. **Model Capabilities Discrepancy Coefficient**: Same omega used for gradient modulation — amplify learning signal from stronger agents, attenuate from weaker.
3. **Exponential Importance Sampling**: s_tilde = s * (sg[s])^alpha for cross-agent rollouts. Prioritizes learning from agents whose output distribution is closer. Alpha controls conservatism.
4. **Stepwise Clipping**: clip(s, 1-delta+k*delta_step, 1.0) — progressively tightens clipping bounds within mini-batch updates to prevent policy drift accumulation.

### Evidence

- 3 heterogeneity types (state, size, model) x 7 math benchmarks
- Outperforms GSPO x2 (double compute baseline) with half rollout cost
- Ablation: removing capability-aware advantage = -5.7% avg, -44% on AIME2025
- Theoretical guarantees: unbiased advantage estimation (Theorem 4.1), gradient consistency (Theorem 4.3)

### Preconditions

- Multiple heterogeneous LLMs training on shared tasks
- Verifiable rewards (math reasoning evaluated)
- Only 2-agent settings tested; n>2 scaling unverified

## Gap Analysis

| # | HACRL Technique | Status | Current State |
|---|----------------|--------|---------------|
| 1 | Heterogeneous agent collaborative training | N/A | Training paradigm; dotfiles is inference-time harness |
| 2 | GRPO / advantage estimation | Already | `rl_advantage.py`: `grpo_advantage()`, `rloo_advantage()` |
| 3 | Importance sampling (version drift) | Already | `rl_advantage.py`: `importance_weight()` |
| 4 | PPO-style clipping | Already | `rl_advantage.py`: `clip_ratio()` |
| 5 | Capability ratio for review weighting | **Gap** | `/review` treats all reviewers equally in consensus synthesis |
| 6 | Cross-agent knowledge transfer | **Partial** | Multi-model delegation exists, but no feedback loop between models |
| 7 | Stepwise clipping for AutoEvolve | **Partial** | Static reject limits exist, no progressive tightening within iteration |
| 8 | Expertise proximity weighting in debate | **Gap** | `/debate` collects opinions without domain-relevance weighting |
| 9 | Theoretical guarantees | N/A | Academic proofs, not actionable for harness |

## Integration Decisions

All 4 Gap/Partial items selected for integration:
- #5: Capability ratio for review weighting
- #6: Cross-agent knowledge transfer
- #7: Stepwise clipping for AutoEvolve
- #8: Expertise proximity weighting

## Plan

See `docs/plans/2026-03-23-hacrl-integration.md`
