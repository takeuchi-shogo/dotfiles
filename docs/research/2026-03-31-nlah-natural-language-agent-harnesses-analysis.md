---
source: "Natural-Language Agent Harnesses" (Pan et al., arXiv:2603.25723)
date: 2026-03-31
status: integrated
---

## Source Summary

**主張**: ハーネスの design-pattern layer を自然言語で書かれたポータブルな実行可能アーティファクト (NLAH) として外部化し、共有ランタイム (IHR) で実行できる。

**手法**:
1. NLAH 6要素の形式化 (Contracts, Roles, Stages, Adapters, State semantics, Failure taxonomy)
2. IHR 3層分離 (in-loop LLM + backend + runtime charter)
3. File-backed state の3性質 (externalized, path-addressable, compaction-stable)
4. Self-evolution モジュール (retry loop + 失敗反省 + attempt間再設計) — **RQ2で最高ROI (75.2→80.0)**
5. Evidence-backed answering (最終回答前に standalone evidence artifact)
6. Verifier separation (独立検証者が candidate を inspect)
7. Multi-candidate search (K=5, diversity, pruning, escalation)
8. Dynamic orchestration (最小適切トポロジー優先)
9. Runtime charter / harness logic の明示的分離
10. fork_context semantics (子エージェントのコンテキスト継承制御)

**根拠**: SWE-bench Verified 125件 + OSWorld 36件。Codex CLI 0.114.0, GPT-5.4, reasoning xhigh。

**核心の知見**:
- Self-evolution が最もコスト効率の高いモジュール（スコア上昇、コスト右シフトなし）
- 「構造追加 ≠ 性能向上」— モジュールは solved-set replacer として機能し、ローカル検証成功がベンチマーク受理と乖離するリスクがある
- 90%のリソースは子エージェントが消費
- Code-to-text 移行で信頼性メカニズムが GUI修復ループから file-backed state + artifact-backed closure に再配置される

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 3 | File-backed state 3性質 | Partial | plans/checkpoints で外部化あるが3性質は未明文化 |
| 5 | Evidence-backed answering | Partial | verification-before-completion はあるが standalone artifact 生成なし |
| 10 | fork_context semantics | Gap | worktree でFS分離するが会話コンテキスト継承の設計指針なし |
| 11 | "More structure ≠ better" 原則 | Gap | KISS/YAGNI はあるがハーネスモジュール追加の判断基準なし |

### Already 項目の強化分析

| # | 既存の仕組み | 強化判定 | 強化案 |
|---|-------------|---------|--------|
| 1 | NLAH 6要素 | 強化不要 | — |
| 2 | IHR 3層 / Runtime charter分離 | 強化可能 | agent-harness-contract.md に境界定義追記 |
| 4 | Self-evolution (AutoEvolve) | 強化可能 | タスクレベルの explicit attempt loop を workflow-guide に追加 |
| 6 | Verifier separation | 強化不要 | 多観点並列レビューで十分 |
| 7 | Multi-candidate search (best-of-n) | 強化可能 | diversity/pruning/escalation + 高コスト注意書き |
| 8 | Dynamic orchestration | 強化不要 | — |
| 9 | Runtime charter / harness logic | → #2 と統合 | — |

## Integration Decisions

全7項目を取り込み:
- T1: タスクレベル self-evolution → workflow-guide.md
- T2: "More structure ≠ better" → workflow-guide.md
- T3: fork_context semantics → subagent-delegation-guide.md
- T4: Runtime charter vs harness logic → agent-harness-contract.md
- T5: File-backed state 3性質 → agent-harness-contract.md
- T6: best-of-n-guide 強化 → best-of-n-guide.md
- T7: Evidence-backed answering → workflow-guide.md

## Plan

規模M（5ファイル修正）。同一セッションで実行。
