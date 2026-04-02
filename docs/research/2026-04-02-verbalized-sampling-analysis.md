---
source: https://arxiv.org/abs/2510.01171
date: 2026-04-02
status: integrated
---

## Source Summary

**論文**: "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity"
**著者**: Zhang, Yu, Shi (Northeastern), Chong, Tomz, Manning (Stanford), Sicilia (WVU)

**主張**: LLM の mode collapse は RLHF の typicality bias（典型的回答を好むバイアス）が根本原因。プロンプトのみで多様性を回復できる。

**手法**: Verbalized Sampling (VS) — 3バリアント (Standard/CoT/Multi)。モデルに回答の分布を言語化させる。

**根拠**: 5モデル×4データセットで typicality bias を統計的に確認 (α ≈ 0.57-0.65, p < 10⁻¹⁴)。創作 1.6-2.1x 多様性向上、合成データ 37.5% ベンチマーク改善。安全性維持 (>97% 拒否率)。

**前提条件**: 多様性が必要なタスク（創作、対話シミュレーション、合成データ生成）。事実確認タスクには不要。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | VS プロンプト技法 | Gap | best-of-n は並列実行で多様性を得るが、単一セッション内でプロンプトにより多様性を引き出す手法はなかった |
| 2 | Typicality Bias の認知 | Partial | cross-model-insights に Sycophancy・Shared Blind Spots はあるが typicality bias は未記載 |
| 3 | 合成データ生成での活用 | N/A | 現在のハーネスに合成データ生成パイプラインなし |

### Already 項目の強化分析

| # | 既存の仕組み | 強化案 |
|---|-------------|--------|
| A1 | best-of-n-guide.md | VS との併用セクション追加 |
| A2 | review-consensus-policy.md | 強化不要（Shared Blind Spots が既にカバー） |
| A3 | cross-model-insights.md | Typicality Bias セクション追記 |

## Integration Decisions

- #1 Gap: 採用 → `references/verbalized-sampling-guide.md` 新設
- #2 Partial: 採用 → `cross-model-insights.md` に Typicality Bias 追記
- #3 N/A: スキップ
- A1: 採用 → `best-of-n-guide.md` に VS 併用セクション追加
- A2: スキップ（強化不要）
- A3: 採用 → #2 と統合

## Plan

| # | タスク | ファイル | 規模 |
|---|--------|---------|------|
| T1 | VS リファレンス新設 | `references/verbalized-sampling-guide.md` | S |
| T2 | best-of-n ガイド強化 | `references/best-of-n-guide.md` | S |
| T3 | Typicality Bias 追記 | `references/cross-model-insights.md` | S |
| T4 | 分析レポート保存 | `docs/research/2026-04-02-verbalized-sampling-analysis.md` | S |
