---
source: https://arxiv.org/abs/2604.01457v1
date: 2026-04-04
status: integrated
---

## Source Summary

**論文**: "Wired for Overconfidence: A Mechanistic Perspective on Inflated Verbalized Confidence in LLMs" (Zhao, He, Zheng, Zhang, Chen, 2026-04-01)

**主張**: LLM の過剰自信（"confidently wrong"）は、中〜後段レイヤーの Confidence Mover Circuits (CMC) に起因する。この回路は事実性検索回路と構造的に分離しており、推論時介入で大幅なキャリブレーション改善が可能。

**手法**:
- TSLD (Target-Set Logit Difference): 高/低信頼度トークンのロジット差を微分可能な内部指標化
- Truth-Injection 反事実設計: 不正解→正解の置換で clean/corrupt ペアを構成
- EAP-IG (Edge Attribution Patching with Integrated Gradients): 回路発見
- ΔTSLD データ層化: 勾配キャンセル防止のためバケット分割
- Activation Steering (α=0.5-0.6): 推論時の過剰自信方向ベクトル減算
- 信頼度回路 vs 事実性回路の構造的不一致分析

**根拠**:
- 2モデル (Qwen2.5-3B, Llama-3.2-3B) × 3データセット (PopQA, MMLU, NQOpen)
- CMC の cross-dataset 共通性 ≥80%
- ECE 最大 96.9% 改善 (Llama/PopQA)
- 上位 3,000 エッジ（全体の <0.6%）で忠実度 85%+

**前提条件**: 3B 規模 instruction-tuned LLM。信頼度言語化タスク。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | CMC 特定・Activation Steering | N/A | モデル内部の回路操作。プロンプト/ハーネスレベルでは介入不可 |
| 2 | TSLD 内部指標・EAP-IG 回路発見 | N/A | 研究手法。ハーネスに直接適用する対象では��い |
| 3 | 信頼度 ≠ 事実性の構造的不一致をハーネス前提にする | Gap | レビューア評価系が信頼度をおおむね信頼できる信号として扱っていた |
| 4 | cross-dataset 安定性をモデル不変量として記録 | Partial | cross-model-insights.md にバイアス傾向あり。構造的膨張は未記載 |
| 5 | RLHF による過剰自信増幅の因果経路 | Partial | rlhf-alignment.md に mode collapse 言及あり。過剰自信増幅は未記載 |

### Already 項目の強化分析

| # | 既存の仕組み | 論文が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| A1 | Evaluator Calibration Guide | 信頼度言語化は事実性回路と構造的に分離 → 体系的膨張 | Verbalized Confidence Discount 原則を追記 |
| A2 | Review Consensus Policy | 複数レビューアー全員が過剰自信 → 偽の確信 | Confidence Inflation Alert 条件を追加 |
| A3 | Emotion Concepts 統合 | CMC は desperation とは独立した failure mode | CMC 独立性を Wave 3 として併記 |
| A4 | Verbalized Sampling Guide | VS は多様性の問題。過剰自信は直交する calibration の問題 | 強化不要 |
| A5 | 「壊れたら即STOP」原則 | desperation 因果経路は既に記載済み | 強化不要 |

## Integration Decisions

全 Gap/Partial (#3, #4, #5) + Already 強化 (A1, A2, A3) を統合。

## Plan (実行済み)

| # | タスク | 対象ファイル | 状態 |
|---|--------|-------------|------|
| T1 | #3+#4: 信頼度膨張を構造的不変量として追記 | `references/cross-model-insights.md` | Done |
| T2 | A1: Verbalized Confidence Discount 原則 | `references/evaluator-calibration-guide.md` | Done |
| T3 | A2: Confidence Inflation Alert 条件 | `references/review-consensus-policy.md` | Done |
| T4 | #5: RLHF 過剰自信増幅の因果経路 | `docs/wiki/concepts/rlhf-alignment.md` | Done |
| T5 | A3: CMC と desperation の独立性を併記 | `docs/research/2026-04-04-emotion-concepts-llm-analysis.md` | Done |
| T6 | 分析レポート保存 | `docs/research/2026-04-04-overconfidence-circuits-analysis.md` | Done |
