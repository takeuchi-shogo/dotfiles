---
source: https://arxiv.org/abs/2604.02145
date: 2026-04-06
status: integrated
---

# MTI: A Behavior-Based Temperament Profiling System for AI Agents

## Source Summary

**著者**: Jihoon 'JJ' Jeong, MD, MPH, PhD (DGIST) — Model Medicine シリーズ第3弾
**主張**: AI モデルの行動的気質（temperament）は能力ベンチマークとは独立した次元であり、4軸で標準化測定できる

### 4軸フレームワーク

| 軸 | 測定対象 | High Pole | Low Pole |
|---|---|---|---|
| Reactivity | 環境変化に対する出力変動 | Fluid (F) | Anchored (A) |
| Compliance | 指示と行動の整合性（圧力下） | Guided (G) | Independent (I) |
| Sociality | 関係性リソースの配分 | Connected (C) | Solitary (S) |
| Resilience | ストレス下での性能維持 | Tough (T) | Brittle (B) |

### 手法
- 行動ベース測定（自己申告ではなく実出力を観察）
- 2段階プロトコル（能力確認 → 性向分離）
- 温度=0 の決定的設定、完全自動採点
- 9 instruction-tuned SLM (1.7B-9B) + 1 base model、約1,930実験

### 根拠
- 軸間独立性: 全 cross-axis 相関 |r| < 0.42
- ファセット解離: Compliance の Formal/Stance facet 相関 r = 0.002
- サイズ非依存性: 1.7B-9B で気質とモデル規模に系統的関係なし

### 前提条件
- SLM (1.7B-9B) で検証、フロンティアモデル未検証
- 単一 Shell 設定のみ（Core × Shell factorial は Future Work）
- RLHF 分析は llama3.1 instruct/base 1ペアのみ

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 多軸独立測定（能力 ≠ 気質） | Gap | model-expertise-map は能力スコアのみ |
| 2 | Compliance-Resilience パラドックス | Gap | Shell 透過性の方向依存概念が未記録 |
| 3 | RLHF の軸別選択的影響 | Partial | Typicality Bias は記載済、軸別知見は未記録 |
| 4 | 2段階プロトコル | N/A | SLM 向け測定、API フロンティアモデルには不適 |
| 5 | 具体的な測定バッテリー | N/A | Quick MTI は論文の Future Work |

### Already 項目の強化分析

| # | 既存の仕組み | 判定 |
|---|-------------|------|
| A1 | Core-Shell モデル (agency-safety-framework 3本柱) | Already (強化可能) |
| A2 | 行動ベース vs 自己申告 (Verbalized Confidence Inflation) | Already (強化不要) |
| A3 | Sycophancy 対策 (agency-safety-framework) | Already (強化可能) |

## Integration Decisions

**取り込み (全5項目)**:
1. [Gap] 多軸独立測定の知見 → model-expertise-map.md に気質次元の参照注記
2. [Gap] C-R パラドックス知見 → cross-model-insights.md に新セクション
3. [Partial] RLHF 軸別影響 → cross-model-insights.md に追記
4. [強化] Core-Shell 変動 → cross-model-insights.md に追記
5. [強化] Sycophancy 2ファセット → agency-safety-framework.md の追従バイアス項を拡充

**スキップ**:
- 2段階プロトコル / 測定バッテリー — フロンティアモデル向け未確立 (N/A)

## Plan

| # | ファイル | 変更内容 |
|---|---------|---------|
| T1 | `references/cross-model-insights.md` | 「MTI Temperament Insights」セクション追加（C-R パラドックス、RLHF 軸別影響、Core-Shell 変動） |
| T2 | `references/model-expertise-map.md` | 「Temperament ≠ Capability」参照注記セクション追加 |
| T3 | `references/agency-safety-framework.md` | 追従バイアス項に 2ファセット構造 + チャネル別評価を追記 |
| T4 | `docs/research/2026-04-06-mti-temperament-profiling-analysis.md` | 本ファイル（分析レポート） |
