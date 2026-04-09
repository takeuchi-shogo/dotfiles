# 多様性選択手法ガイド

LLM 出力の多様性を定量的に改善する3手法の比較と使い分け。

## 手法比較

| 手法 | 原理 | 計算量 | 近似保証 | 適用場面 |
|------|------|--------|---------|---------|
| **Submodular (Facility Location)** | f(S) = sum_i max_{j in S} sim(i,j) を貪欲最大化 | O(n²k) | (1-1/e) ~ 0.63 | 汎用。候補 10-100 で最適 |
| **DPP (Determinantal Point Process)** | 行列式で多様性を確率的にモデル化 | O(n^3) | 確率的 | 厳密な多様性保証が必要な場合 |
| **MMR (Maximal Marginal Relevance)** | 関連性と既選択との距離の線形結合 | O(nk) | なし | 検索結果のリランキング |

## 使い分けフローチャート

```
候補数 < 5 → 手動確認で十分。選択アルゴリズム不要
候補数 5-50 → Submodular greedy（推奨デフォルト）
候補数 50+ → Submodular greedy + Lazy Greedy 最適化
厳密な多様性保証 → DPP（計算コスト高）
リランキングのみ → MMR
```

## lambda パラメータ

`scripts/lib/submodular_selection.py` の `--lambda` で調整:

| lambda | 挙動 |
|--------|------|
| 0.0 | 純粋なカバレッジ最大化（多様性ペナルティなし） |
| 0.3 | 関連性重視。類似アイテムも許容 |
| **0.5** | **デフォルト。カバレッジと多様性のバランス** |
| 0.7 | 多様性重視。類似アイテムを積極排除 |
| 1.0 | 強い多様性制約。カバレッジ犠牲の可能性 |

## ツール

### diversity_metrics.py — 類似度計測

```bash
python3 scripts/lib/diversity_metrics.py --input texts.jsonl
```

- TF-IDF + cosine similarity ベース（stdlib-only）
- 出力: 平均/最大/最小ペアワイズ類似度、カバレッジスコア
- cosine > 0.7 のペアを自動フラグ

### submodular_selection.py — 最適部分集合選択

```bash
python3 scripts/lib/submodular_selection.py \
  --candidates cands.jsonl --k 5 --lambda 0.5
```

- Facility Location + lambda-weighted greedy
- `--duplicates` で重複ペアも報告

## 2段階多様化パイプライン

詳細は `references/verbalized-sampling-guide.md` の「2段階多様化パイプライン」を参照。

- Stage 1（生成前）: VS / マルチモデルで多様な候補を生成
- Stage 2（生成後）: submodular selection で最適 k 個を選択

## 参考文献

- Lin & Bilmes (ACL 2011): Submodular functions for document summarization
- Jina AI (2026): Submodular optimization for diverse query generation
- Carbonell & Goldstein (SIGIR 1998): MMR for document re-ranking
- Kulesza & Taskar (2012): DPPs for machine learning
