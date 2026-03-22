---
source: https://arxiv.org/abs/2603.18507
title: "Expert Personas Improve LLM Alignment but Damage Accuracy: Bootstrapping Intent-Based Persona Routing with PRISM"
authors: Zizhao Hu, Mohammad Rostami, Jesse Thomason
date: 2026-03-23
status: integrated
---

## Source Summary

### 主張

エキスパートペルソナは LLM のアライメント（安全性・文体）を改善するが、知識依存タスク（MMLU等）の精度を低下させる。
PRISM（Persona Routing via Intent-based Self-Modeling）は意図ベースのゲーティングでこのトレードオフを解消する。

### 手法

- 5段階パイプライン: Query生成 → ペルソナ有/無回答 → 位置入替Self-verification → ゲート訓練 → LoRA蒸留
- ゲート: layer 0 の hidden state に sigmoid。閾値 0.5 でペルソナ適用/非適用を判定
- Self-verification: verbosity bias 回避のため、ペアワイズ比較を位置入替で2回実行。両方で勝った場合のみ正例
- 外部データ・モデル不要

### 根拠（定量結果）

| モデル | 手法 | MT-Bench | MMLU | Overall |
|--------|------|----------|------|---------|
| Qwen2.5-7B | Base | 7.56 | 71.7% | 71.8 |
| | PRISM | 7.76 | 71.7% | 73.5 |
| Mistral-7B | Base | 8.74 | 59.8% | — |
| | PRISM | 8.99 | 59.8% | — |
| Llama-3.1-8B | Base | 7.23 | 68.4% | 67.5 |
| | PRISM | 7.76 | 68.4% | 70.3 |

- MMLU: ペルソナなし 71.6% → ペルソナあり 68.0%（-3.6pt）
- JailbreakBench: +17.7%（53.2% → 70.9%）
- ゲートルーティング率と実効果の相関: Pearson r=0.65, Spearman rho=0.75

### 前提条件

- 7-8B パラメータのオープンモデルで検証。70B+ は未検証
- LoRA ゲート方式は標準 LoRA マージと非互換
- 推論蒸留モデル（R1系）ではペルソナ効果がほぼゼロ（97-99%がベースにルーティング）

## Gap Analysis

| # | 手法 | 判定 | 現状と差分 |
|---|------|------|-----------|
| 1 | タスク依存ペルソナ効果 | N/A | 論文は7-8Bモデル。当環境はClaude Opus/Sonnet（数百B規模）で効果の方向・サイズが異なる可能性が高い |
| 2 | Intent-based routing | Partial | `agent-router.py` がキーワードベースで Codex/Gemini 委譲を提案。概念的に類似だがペルソナゲーティングではない |
| 3 | Self-verification（位置入替） | Gap | レビュー合成時の verbosity bias 対策が未実装 |
| 4 | ペルソナ粒度最適化 | Gap | agent 定義の長さに設計指針がない |
| 5 | LoRA ゲート + Self-distillation | N/A | API ベース利用では適用不可 |
| 6 | 推論蒸留モデルにはペルソナ不要 | N/A | 蒸留モデルを直接使用していない |

## Integration Decisions

- **#3 採用**: `review-consensus-policy.md` に Section 5 "Verbosity Bias Mitigation" を追加。Convergence Stall / Outlier 判定時に位置入替ペアワイズ比較を適用
- **#4 採用**: `compact-instructions.md` に "Agent 定義の粒度指針" セクションを追加。タスク特性別の推奨トークン数を記載
- #1, #5, #6: モデル規模・利用形態の差異により除外
- #2: 既存の agent-router.py で部分的にカバー済み。追加実装なし
