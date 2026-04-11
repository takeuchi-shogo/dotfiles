---
source: https://zenn.dev/nakakiiro/articles/kaggle_claude_code_boilerplate
date: 2026-03-25
status: skipped
---

## Source Summary

Kaggle上位勢3名（mst, すぐー, ごうや）の `.claude/` 設定を比較分析した記事。

- **主張**: 異なる設計哲学が存在し、「なぜそう書くのか」を理解することが重要
- **手法**:
  - mst: 6フェーズ実験ワークフロー（Understand→Plan→Create→Implement→Train→Record）、W&B統合、Vertex AI GPU訓練
  - すぐー: 安定型+爆発型の2戦略提示ルール、出力分析→最適化の順序、AI/人間の実験命名分離、SESSION_NOTES.md、kaggle-researcher/data-analyst/code-reviewer エージェント
  - ごうや: .steering/ による設計強制（requirements.md + design.md + tasklist.md 必須）、4種カスタムエージェント、/review-exp スキル
- **共通成功要因**: コード品質の自動担保 + セッション跨ぎコンテキスト管理
- **前提条件**: Kaggle MLコンペティション、複数セッション実験管理

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 6フェーズ実験ワークフロー (mst) | N/A | Kaggle ML固有。/spike→/epd が汎用版 |
| 2 | 安定型+爆発型の2戦略提示 (すぐー) | Partial | /debate と brainstorming が存在するが構造化2案提示は未ルール化 |
| 3 | W&B統合・GPU訓練サポート (mst) | N/A | Kaggle ML固有 |
| 4 | AI/人間の実験命名分離 (すぐー) | N/A | git Co-authored-by で追跡可能 |
| 5 | /survey-papers 論文検索 (すぐー) | Already | /research がマルチモデル並列リサーチ提供 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事の知見 | 判定 |
|---|-------------|-----------|------|
| A | /checkpoint + session-protocol.md | SESSION_NOTES.md（実験単位コンテキスト管理） | 強化不要 |
| B | /daily-report | daily_reports/YYYYMMDD.md | 強化不要 |
| C | /spec + plan-lifecycle.py | .steering/ 設計強制 | 強化不要 |
| D | /review + 自動レビューアー選択 | /review-exp 実験レビュー | 強化不要 |
| E | 20+ 専門エージェント | ドメイン特化エージェント群 | 強化不要 |
| F | brainstorming スキル | 常に保守的+挑戦的の2案提示 | 強化可能（インパクト小） |
| G | verification-before-completion | 出力20件分析→最適化の順序 | 強化不要 |

## Integration Decisions

全項目スキップ。Kaggle ML固有の手法が大半で、唯一の候補（2戦略提示ルール）もインパクトが小さいと判断。
