---
status: active
last_reviewed: 2026-04-23
---

# Submodular Optimization for Diverse Query Generation in DeepResearch — 分析レポート

> Source: https://jina.ai/news/submodular-optimization-for-diverse-query-generation-in-deepresearch/
> Date: 2026-04-10
> Status: Plan generated, awaiting implementation

## 記事の主張

LLM の検索クエリ生成は支配的な見方に偏る。プロンプトエンジニアリングではなく、**部分加法最適化（submodular optimization）**で関連性と多様性を同時に最大化すべき。

### 手法

1. **Facility Location**（カバレッジベース） — 候補クエリ全体のカバレッジを最大化し暗黙的に多様性を確保
2. **λパラメータ制御** — 関連性と多様性の重み付けを連続パラメータで調整
3. **貪欲法（Greedy Algorithm）** — O(nk)で最適解の63%保証（1−1/e ≈ 0.63の近似率）
4. **Lazy Greedy** — 優先度キューで不要な計算を回避し高速化

### 根拠

- LLM生成クエリはコサイン類似度0.4-0.8の高重複
- 貪欲アルゴリズムに(1−1/e)≈0.63の近似率保証（数学的下限）
- Wang et al.(2025), Abe et al.(2025): LLMは支配的見方に偏る傾向を確認

### 前提条件

- 検索クエリの多様化が重要なリサーチシステム
- トークンコストが制約（k個の厳選クエリで無駄削減）
- 再現可能性と説明可能性が求められるシステム
- n個の候補クエリとスコア計算能力、候補間距離計測の仕組みが必要

## ギャップ分析

### Gap / Partial

| # | 手法 | 判定 | 現状 | 優先度 |
|---|------|------|------|--------|
| 1 | 候補間類似度の計測基盤 | Critical Gap | word_overlap_ratio のみ。embedding 距離なし | 最優先 — 他の全判定の土台 |
| 2 | 生成後の多様性選択層（submodular / DPP / MMR） | Gap | 候補集合からの最適部分集合選択なし | 高 — 10年の実績ある手法群 |
| 3 | 関連性-多様性トレードオフ制御 | Partial | Pareto frontier は存在。連続λ制御なし | 中 — #1, #2 完了後 |
| 4 | Lazy Greedy 高速化 | 低優先 | 候補数が数十レベルでは効果限定的 | 低 — Greedy 導入時に自然に入る |
| 5 | 現行システムの重複症状計測 | 新規 Gap | /research, /debate の出力重複度が未検証 | 最優先 — #1 と同時に実施 |

### Already 項目の強化分析

| # | 既存の仕組み | 強化余地 | 備考 |
|---|-------------|---------|------|
| A | VS（生成前プロンプト多様化） | submodular 選択と補完関係で2段階化 | VS 自体は 2-3倍改善実証済み |
| B | /research Step 4 Aggregate | 類似度スコアベースの重複排除 + coverage gap 定量化 | Aggregate の品質フィルタ強化 |

## セカンドオピニオン

### Codex 批評（主要指摘）

- #1と#2は二重計上 → 統合済み
- #5（症状確認）が最優先 — Gap認定の前にデータが必要
- #3のλはPareto frontierがあるので完全な空白ではない → Partial に修正
- Already C（diversity_bonus）は問題設定が異なる → 削除
- マルチモデルは記事の批判対象外 → Already A を VS+prompt 限定に修正

### Gemini 周辺知識

- **採用事例**: 文書要約(Lin & Bilmes 2011, ACL)、YouTube推薦(DPP, CIKM 2018)。LLMエージェントへは Jina AI が先行者
- **制約**: embedding品質がボトルネック、λ自動チューニング未解決、候補生成のLLMコストが支配的（submodular自体はミリ秒）
- **代替手法**: DPP for RAG(2026), Diversified Sampling(2025), MMR+FPS統合, Guided Generation(EMNLP 2025)
- **総合**: 問題認識は妥当。「プロンプトでは不十分」は過度に単純化の可能性。VS等との補完関係が正しい位置づけ

## 選別結果

全項目を取り込み。優先順位: #1+5 → #2 → #B → #A → #3

## 統合プラン

### Wave 1: 計測基盤 + 症状検証

| タスク | 成果物 | 依存 |
|--------|--------|------|
| 1-1: 多様性メトリクス・ユーティリティ作成 | `scripts/lib/diversity_metrics.py` — TF-IDF + cosine similarity ベース。embedding API プラグイン可 | なし |
| 1-2: /research, /debate の出力重複度を計測 | 計測スクリプト実行 + 結果レポート | 1-1 |

### Wave 2: 選択アルゴリズム + Aggregate 強化

| タスク | 成果物 | 依存 |
|--------|--------|------|
| 2-1: Submodular greedy selection ユーティリティ | `scripts/lib/submodular_selection.py` — Facility Location + λ制御 + greedy | 1-1 |
| 2-2: /research Aggregate に類似度ベース重複排除を統合 | `skills/research/SKILL.md` 修正 + `references/diversity-selection-guide.md` | 2-1 |

### Wave 3: パイプライン統合 + ドキュメント

| タスク | 成果物 | 依存 |
|--------|--------|------|
| 3-1: VS + submodular 2段階パイプライン設計 | `references/verbalized-sampling-guide.md` に追記 | 2-1 |
| 3-2: /research Step 1 にサブ目標多様化の統合ポイント追記 | `skills/research/SKILL.md` 修正 | 2-2, 3-1 |

### 設計判断

- embedding API 不要: TF-IDF + cosine をベース、Jina/OpenAI embedding は optional プラグイン
- Greedy のみ: Lazy Greedy は候補数増加時に追加（YAGNI）
- λデフォルト値: 0.5 から開始、Wave 1 のデータで調整
- スクリプト言語: Python（既存 scripts/lib/ と統一）

## 参考文献

- Jina AI: Submodular Optimization for Diverse Query Generation in DeepResearch
- Lin & Bilmes (ACL 2011): A Class of Submodular Functions for Document Summarization
- YouTube DPP (CIKM 2018): Practical Diversified Recommendations on YouTube
- Diversified Sampling (arXiv 2025): Diversified Sampling Improves Scaling LLM Inference
- DPP for RAG (arXiv 2026): Scaling DPPs for RAG: Density Meets Diversity
- Diversity Enhances RAG (arXiv 2025): Diversity Enhances an LLM's Performance in RAG
- Mirzasoleiman+ 2015: Lazier Than Lazy Greedy (Stochastic Greedy)
- ATCG (arXiv 2026): Adaptive Threshold-Driven Continuous Greedy Method
