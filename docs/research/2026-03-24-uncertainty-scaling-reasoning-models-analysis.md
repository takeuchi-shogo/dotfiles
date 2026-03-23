---
source: https://arxiv.org/abs/2603.19118
date: 2026-03-24
status: integrated
---

# How Uncertainty Estimation Scales with Sampling in Reasoning Models

Del et al., 2026. arXiv:2603.19118

## Source Summary

### 主張

推論モデル（CoT）の不確実性推定では、Verbalized Confidence (VC) と Self-Consistency (SC) を 2 サンプルで組み合わせた SCVC が最もコスト効率が良く、各信号を 8 サンプルまで個別スケールした場合を上回る。

### 手法

- **VC**: モデルが明示的に報告する confidence 値（0-100）を majority-vote 回答に対して平均
- **SC**: K サンプル中の majority-vote 一致率
- **SCVC**: `λ·SC + (1-λ)·VC_avg`（λ=0.5 で十分ロバスト）
- **評価**: AUROC（識別能力、校正不要）、Bootstrap 評価プロトコル（R=10, B=多数）

### 根拠

- 3 モデル（gpt-oss-20B, Qwen3-30B-A3B, DeepSeek-R1-8B）× 17 タスク（数学4, STEM8, 人文5）
- SCVC K=2 → 数学 84.2 AUROC（VC K=1 比 +12.9）、STEM 80.2（+6.4）、人文 74.9（+6.4）
- SCVC K=2 は VC K=8 (81.4) / SC K=8 (79.6) を上回る
- λ 感度分析: 0 < λ < 1 の広範囲で AUROC ほぼ一定

### 前提条件

- temperature > 0 のサンプリングが可能なブラックボックスアクセス
- 推論モデル（extended chain-of-thought）が対象。標準 LLM では異なる挙動の可能性

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | SCVC 線形結合公式 | Partial | review-consensus-policy.md は agreement_rate と confidence を別々に扱う |
| 2 | ドメイン別信号信頼度 | Gap | reviewer-capability-scores.md にドメイン別 VC/SC 重み調整なし |
| 3 | Bootstrap 評価プロトコル | N/A | 論文固有の統計手法 |
| 4 | 6種 VC バリエーション比較 | N/A | レビューアーは各自専門化済み |

### Already 項目の強化分析

| # | 既存の仕組み | 論文が示す知見 | 判定 |
|---|-------------|---------------|------|
| A1 | Reviewer Scaling Upper Bound | SCVC K=2 > 単独 K=8。異種シグナル 2 体 > 同種 8 体 | 強化可能 |
| A2 | Shared Blind Spots | レビューアー数増加→信号収束→盲点検出力は上がらない | 強化可能 |
| A3 | Best-of-N プランニング | K=2→K=8 の追加ゲインは逓減 | 強化可能（ただし今回はスキップ） |
| A4 | overconfidence-prevention.md | 行動規範であり統計的識別力とは別関心 | 強化不要 |
| A5 | Convergence Stall Detection | 異種間不一致=相補的情報 vs 同種間不一致=真の矛盾 | 強化可能 |

## Integration Decisions

全 Gap/Partial + A1, A2, A5 を統合。A3 は今回スキップ（Best-of-N は既に十分な記載あり）。A4 は強化不要。

### 変更ファイル

1. `references/review-consensus-policy.md` — §1 異種優先原則, §3 異種/同種分類, 新§ SCVC Hybrid Signal
2. `references/cross-model-insights.md` — Shared Blind Spots に収束リスク追記
3. `references/reviewer-capability-scores.md` — Domain Signal Trust セクション追加
