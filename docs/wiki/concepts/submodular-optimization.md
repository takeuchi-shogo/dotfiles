---
title: サブモジュラー最適化
topics: [ml-rl]
sources: [2026-04-10-submodular-diverse-query-generation-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 1
confidence: emerging
---

# サブモジュラー最適化

## 概要

サブモジュラー最適化（Submodular Optimization）は、部分集合関数の「収穫逓減」性質を利用して、大きな候補集合から最大カバレッジを持つ部分集合を効率的に選択する手法である。Facility Location 関数と貪欲法の組み合わせにより、関連性と多様性を同時に最大化できる。文書要約・推薦システムで10年以上の実績があり、LLM エージェントの生成後選択レイヤーへの応用が進んでいる。

## 主要な知見

- **LLM 生成クエリの高重複問題** — コサイン類似度 0.4-0.8 の高重複が発生。プロンプト工夫だけでは不十分
- **Facility Location 関数** — 各候補が「施設」として他の候補をカバーする範囲を最大化する目的関数
- **貪欲法の近似率保証** — (1 - 1/e) ≈ 0.63 の近似率が数学的に証明されており、最悪ケースでも最適解の 63% 以上を保証
- **λ パラメータ** — 関連性（スコア）と多様性（カバレッジ）のトレードオフを連続制御。λ=0 で純粋な多様性最大化、λ=1 で純粋なスコア最大化
- **計算コストの分離** — submodular 選択自体はミリ秒レベル。実質ボトルネックは候補生成の LLM コスト
- **Lazy Greedy（Stochastic Greedy）** — 優先度キューやランダムサブサンプリングで劣モジュラ関数の評価回数を削減し、候補数が多い場合でも高速に近似解へ到達する手法（Mirzasoleiman et al. 2015: Lazier Than Lazy Greedy）[EXTRACTED, conf=80]
- **ATCG（Adaptive Threshold-Driven Continuous Greedy）** — 貪欲法の選択閾値を適応的に調整する連続緩和ベースの新手法（2026）。候補集合が大きい場面での精度・速度トレードオフ改善を狙う [EXTRACTED, conf=60]
- **λ自動チューニングは未解決課題** — 現状は経験的な固定値設定が主流（dotfiles では 0.5 から開始し実測データで調整する運用）。データセットごとに最適な λ を自動決定する手法は研究途上 [EXTRACTED, conf=70]
- **文書要約分野での実績** — Lin & Bilmes (2011, ACL) が facility location 系の劣モジュラ関数を文書要約に適用した先行研究で、10年以上前から実運用されてきた理論的系譜 [EXTRACTED, conf=75]

## 実践的な適用

dotfiles ハーネスでは /research スキルの多様性保証に応用予定。3段階で統合する。

| 段階 | 内容 | 実装 |
|------|------|------|
| Wave 1 | 症状計測 | `diversity_metrics.py`（TF-IDF + cosine）でクエリ重複を定量化 |
| Wave 2 | 選択層追加 | `submodular_selection.py` + /research Aggregate 強化 |
| Wave 3 | 2段階パイプライン | Verbalized Sampling + submodular の組み合わせ |

## 「生成前多様化」との補完関係

既存手法（Verbalized Sampling、マルチモデル並列）は **生成前多様化** アプローチである。submodular optimization は **生成後選択** として異なるレイヤーで動作し、2段階パイプラインとして組み合わせられる。

```
[候補生成] Verbalized Sampling / multi-model → [候補集合] → [submodular 選択] → [最終クエリ]
```

## 関連概念

- [diversity-selection](diversity-selection.md) — 生成後の多様性選択層（直接の適用先）
- [RLHFアライメント](rlhf-alignment.md) — Verbalized Sampling（生成前多様化）との補完関係
- [ナレッジパイプライン](knowledge-pipeline.md) — 知識変換パイプラインへの統合点

## ソース

- [Jina AI: Submodular Optimization for Diverse Query Generation in DeepResearch](../../research/2026-04-10-submodular-diverse-query-generation-analysis.md) — Lazy Greedy・ATCG・λ自動チューニング課題・文書要約実績を含む全項目採用の統合分析
