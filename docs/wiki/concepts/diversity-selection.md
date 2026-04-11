---
title: 多様性選択
topics: [ml-rl]
sources: [2026-04-10-jina-submodular-diverse-query-generation-analysis.md]
updated: 2026-04-10
---

# 多様性選択

## 概要

多様性選択（Diversity Selection）は、LLM が大量生成した候補集合から、関連性を保ちつつ互いに重複しない多様な部分集合を選ぶ後処理ステップである。Verbalized Sampling（生成前多様化）や複数モデル並列実行とは独立したレイヤーで動作し、補完関係にある。

## 主要な知見

- **生成後処理の必要性** — 生成前多様化（温度調整、VS プロンプト）だけでは類似クエリの重複を十分に除去できない
- **生成前 vs 生成後** — 生成前：確率的サンプリングで多様化。生成後：決定論的選択で最大カバレッジを保証
- **計測基盤が前提** — 重複症状を定量化（TF-IDF + cosine similarity）してから選択ロジックを導入するデータ駆動アプローチが重要
- **DPP（Determinantal Point Process）** — submodular 系の同族手法として 2026 年に活発化中。embedding 品質がボトルネック

## 適用パターン

| パターン | 手法 | 特徴 |
|---------|------|------|
| 貪欲選択 | Submodular + Facility Location | 近似率保証あり（≥63%）。実装シンプル |
| 確率的選択 | DPP（Determinantal Point Process） | 理論的に最適だが embedding 品質依存 |
| ルールベース | MMR（Maximal Marginal Relevance） | クエリ拡張の古典手法。実装が最も簡単 |

## 2段階パイプライン

生成前多様化と組み合わせることで多様性の「二重保証」が得られる。

```
Step 1 [生成前]: Verbalized Sampling プロンプトで候補を多様に生成
         ↓
Step 2 [生成後]: Submodular / DPP で最大カバレッジの部分集合を選択
         ↓
最終クエリセット（重複なし・関連性維持）
```

## 実践的な適用

dotfiles ハーネスでは /research スキルの Aggregate フェーズに組み込み予定。

- Wave 1: `diversity_metrics.py` で重複率の基準値を計測
- Wave 2: `submodular_selection.py` を Aggregate に統合、λ パラメータで関連性-多様性を調整
- Wave 3: VS + submodular の2段階パイプラインを /research Step 1 に統合

## 関連概念

- [サブモジュラー最適化](submodular-optimization.md) — 多様性選択の主要アルゴリズム
- [RLHFアライメント](rlhf-alignment.md) — Verbalized Sampling（生成前多様化・補完関係）
- [ワークフロー最適化](workflow-optimization.md) — /research スキルのパイプライン設計

## ソース

- [Jina AI: Submodular Optimization for Diverse Query Generation in DeepResearch](../../research/2026-04-10-jina-submodular-diverse-query-generation-analysis.md)
