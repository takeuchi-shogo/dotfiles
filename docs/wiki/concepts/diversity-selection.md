---
title: 多様性選択
topics: [ml-rl]
sources: [2026-04-10-submodular-diverse-query-generation-analysis.md, 2026-04-11-moe-article-analysis.md, 2026-04-14-karpathy-second-brain-modified-analysis.md, 2026-06-02-hermes-60-days-6-lessons-absorb-analysis.md, 2026-06-04-ai-tech-researcher-self-evolving-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 5
confidence: established
---

# 多様性選択

## 概要

多様性選択（Diversity Selection）は、LLM が大量生成した候補集合から、関連性を保ちつつ互いに重複しない多様な部分集合を選ぶ後処理ステップである。Verbalized Sampling（生成前多様化）や複数モデル並列実行とは独立したレイヤーで動作し、補完関係にある。

## 主要な知見

- **生成後処理の必要性** — 生成前多様化（温度調整、VS プロンプト）だけでは類似クエリの重複を十分に除去できない
- **生成前 vs 生成後** — 生成前：確率的サンプリングで多様化。生成後：決定論的選択で最大カバレッジを保証
- **計測基盤が前提** — 重複症状を定量化（TF-IDF + cosine similarity）してから選択ロジックを導入するデータ駆動アプローチが重要
- **DPP（Determinantal Point Process）** — submodular 系の同族手法として 2026 年に活発化中。embedding 品質がボトルネック
- **重複の実測データ** — LLM 生成クエリはコサイン類似度 0.4-0.8 の高重複域に集中する（Wang et al. 2025, Abe et al. 2025）。多様性選択を導入する前に、この閾値を基準として自システムの重複度をまず定量計測すべき [EXTRACTED, conf=85]
- **Lazy Greedy による高速化** — 優先度キューで不要な候補評価をスキップし貪欲選択を高速化する手法。候補数が数十件規模では効果が限定的なため、候補数増加時に導入すれば十分（YAGNI） [EXTRACTED, conf=75]
- **先行研究の系譜** — 文書要約（Lin & Bilmes, ACL 2011）、YouTube 推薦（DPP, CIKM 2018）で 10 年以上の実績がある手法群であり、LLM エージェントへの適用は Jina AI らが先行している [EXTRACTED, conf=80]
- **MoE の Load Balancing との類推（粒度崩壊ガードレール）** — MoE の Load balancing loss（特定 Expert への集中 = Expert collapse を防ぐ）は多様性選択の目的と同型だが、選択の粒度をトークン単位まで細かくすると論理的一貫性が崩壊する（Contextual Fragmentation）。多様性選択は「候補・レスポンス単位」で運用し、より細かい粒度への安易な転用は避けるべき [INFERRED, conf=70]
- **昇格ループにおける echo chamber 問題** — フィードバックループ型の自己改善システム（learned 昇格ループ等）では、出力が既存の優勢な傾向に収束する echo chamber / self-reinforcing loop が未解決課題として指摘されている。多様性選択の部品（`submodular_selection.py`, `diversity-selection-guide.md`）が存在しても、昇格ゲート自体に配線されていなければ機能しない [EXTRACTED, conf=80]
- **Watch 条件による段階導入** — 多様性強制機構を稼働前にフル実装するのは YAGNI。同一 scope の learned が複数バッチ連続で昇格を占有する、または矛盾 learned が恒常的に reject される、といった具体的な兆候を観測してから昇格ゲートへの統合を検討する段階的アプローチが有効 [EXTRACTED, conf=75]
- **情報源選定への一般化** — 採用実績ベースで情報源を自己進化させる仕組みでは、採用実績を主指標にすると LLM が要約しやすい/クリックベイト的なソースに偏る評価指標ゲーミングを招く。対策として MMR（本記事の適用パターンの一つ）や Multi-armed Bandit 探索が挙げられており、多様性選択は生成クエリに限らず情報源ランキングのような他の選択問題にも一般化する [EXTRACTED, conf=75]

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
- 昇格ループ（`/promote-learnings`）: echo chamber 対策として多様性チェック heuristic を Step 3 に追加済み。watch 条件（同一 scope の learned が 3 連続バッチ占有 / 矛盾 learned の恒常 reject）を満たしたら `submodular_selection.py` の本配線を検討

## 関連概念

- [サブモジュラー最適化](submodular-optimization.md) — 多様性選択の主要アルゴリズム
- [RLHFアライメント](rlhf-alignment.md) — Verbalized Sampling（生成前多様化・補完関係）
- [ワークフロー最適化](workflow-optimization.md) — /research スキルのパイプライン設計

## ソース

- [Jina AI: Submodular Optimization for Diverse Query Generation in DeepResearch](../../research/2026-04-10-submodular-diverse-query-generation-analysis.md)
- [Mixture of Experts Explained — 分析レポート](../../research/2026-04-11-moe-article-analysis.md) — MoE の Load balancing/Expert collapse 回避と MoA の粒度崩壊事例をハーネス設計に類推
- [My Second Brain Setup: A Modified Karpathy Method](../../research/2026-04-14-karpathy-second-brain-modified-analysis.md) — 個人 wiki の agent/human 執筆分離と draft graduation 機構の分析
- [6 Workflows, 6 Lessons, 60 Days with Hermes Analyst](../../research/2026-06-02-hermes-60-days-6-lessons-absorb-analysis.md) — 60日運用の教訓、echo chamber / self-reinforcing loop が昇格ループの未解決課題として判明
- [AI Tech Researcher: 自己進化する情報収集システム](../../research/2026-06-04-ai-tech-researcher-self-evolving-absorb-analysis.md) — 情報源の採用実績ベース自己進化、評価指標ゲーミングと MMR による多様性強制対策
