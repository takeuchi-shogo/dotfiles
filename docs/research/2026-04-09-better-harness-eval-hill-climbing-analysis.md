# Better Harness: Eval-Driven Hill-Climbing 分析レポート

> Source: "Better Harness: A Recipe for Harness Hill-Climbing with Evals" (LangChain/Z.ai, 2026)
> Date: 2026-04-09

## 記事の主張

Evals はハーネスエンジニアリングの「訓練データ」。Eval を hill-climbing signal として使い、ハーネスを自律的に改善できる。複合システム: data sourcing → experiment design → optimization → review & acceptance。

Claude Sonnet 4.6 と GLM-5 で検証、Holdout セットへのほぼ完全な汎化を確認。

## 手法一覧（11手法）

1. Eval-as-training-data パラダイム
2. Multi-source eval sourcing（手書き + production traces + external datasets）
3. Behavioral tagging（行動カテゴリタグ付け）
4. Train/Holdout split（過学習防止）
5. Baseline-first optimization
6. Single-change-at-a-time optimization
7. Regression protection（回帰テスト化）
8. Human review gate（過学習チェック）
9. Trace-driven flywheel（トレース→eval→改善ループ）
10. Model-harness fitting（モデル別チューニング）
11. Eval spring cleaning（定期退役）

## ギャップ分析

### Gap / Partial

| # | 手法 | 判定 | 現状 | 優先度 |
|---|------|------|------|--------|
| 7 | Regression protection（実行型） | Partial | regression-gate.py は構造検査のみ。regression-suite.json 未生成、実行回帰テストなし | 最優先 |
| 4 | Train/Holdout split | Gap | Rule 43 で将来方向と記述。実装なし | 中 |
| 11 | Eval spring cleaning | Partial | eval tuple の退役プロセスなし | 低 |

### Already (強化可能)

| # | 既存の仕組み | 強化案 |
|---|-------------|--------|
| 2 | trace→eval フライホイール | external dataset import 経路を eval-generator.py に追加 |
| 5 | baseline-eval.json + aggregate_benchmark.py | /improve Step 0 に明示的 baseline run 組み込み |
| 9 | trace フライホイール完備 | harness version 間のトレース比較機能追加 |
| 1 | AutoEvolve パイプライン | compound system パイプライン図を improve-policy.md に明示 |

### Already (強化不要)

- 3: Behavioral tagging（FM-001〜017 + severity + reviewer 3軸タグ完備）
- 6: Single-change（Rule 20 完備）
- 8: Human review gate（Rule 34 + harness_review_flag.py + completion-gate.py 完備）

### N/A

- 10: Model-harness fitting — 個人プロジェクトでは費用対効果が低い。Rule 32 cross-model smoke test で十分

## セカンドオピニオン

### Codex 批評

- #7 を Already (強化不要) と判定するのは危険 → Partial に修正
- #5 は baseline-eval.json + aggregate_benchmark.py が存在 → Already (強化可能) に昇格
- #10 は個人プロジェクトでは N/A 寄り
- 優先度: #7 実行型 regression > #2 external dataset > #4 holdout

### Gemini 周辺知識

- Distribution shift: Holdout split でも本番との分布ズレリスク
- 計算コスト: 大規模モデル × 多数 eval = コスト爆発。個人では特に制約
- Semantic Drift Detection: eval 劣化の早期発見 → spring cleaning 強化版
- 代替手法: Bandit 最適化、PBT、Multi-Objective Optimization

## 統合プラン

docs/plans/2026-04-09-better-harness-integration.md を参照。

## Triage 結果

Gap/Partial: 全部取り込み（#7→#4→#11）
Already 強化: 全部取り込み（#2, #5, #9, #1）
