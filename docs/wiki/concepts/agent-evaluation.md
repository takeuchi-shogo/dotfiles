---
title: エージェント評価
topics: [evaluation]
sources: [2026-03-12-ai-evals-framework.md, 2026-03-19-evals-skills-analysis.md, 2026-03-17-swe-ci-deep-survey.md, 2026-03-30-slopcodebench-iterative-degradation-analysis.md]
updated: 2026-04-04
---

# エージェント評価

## 概要

エージェント評価とは、AIコーディングエージェントの品質・能力・劣化傾向を定量的に測定するフレームワークを指す。従来の「スナップショット型」（1回の修正で評価）ベンチマークは長期的なコード品質劣化を検出できず、CIループを回しながら連続的にコードを進化させる「evolution-based」評価が必要であるとSWE-CIが示す。SlopCodeBenchの分析では11モデル×20問題で完全解決がゼロであり、プロンプト介入は初期品質（intercept）を改善するが反復ごとの劣化速度（slope）は変わらないという根本的な課題が明らかになっている。

## 主要な知見

- **二層評価アーキテクチャ**: Code-Based（決定論的・高速・安価）とLLM-as-Judge（意味的分析）を組み合わせる
- **ボトムアップ帰納**: カテゴリを事前ブレストせず、~100トレースの観察から失敗モードを帰納する
- **TPR/TNR分離計測**: 合否率だけでなく真陽性率・真陰性率を個別に計測し、Rogan-Gladen補正を適用する
- **zero-regression rate**: 18モデル中Claude Opus系の2モデルのみが0.5超。大半は0.25未満という衝撃的な結果
- **Slope vs Intercept分離**: プロンプト改善は初期品質を上げるが劣化速度は変わらない。構造的対策が必要
- **Structural Erosion**: 高CC(>10)関数への複雑性集中度を`mass(f) = CC(f) × √SLOC(f)`で定量化する
- **テストスイートの限界**: 機能的正確性（pass/fail）が維持されたまま構造的劣化が進む。ErrorとRegressionテストで崩壊
- **God Function化パターン**: 反復的編集の主要失敗モード。新ロジックが既存関数にパッチされ肥大化する
- **初期アーキテクチャ決定の複利効果**: C1でのハードコード判断がC2, C5で連鎖的書き直しを引き起こす
- **グラフ構造メトリクス**: タスク正解率だけでなくnode count・depth・width・communication volume・structural varianceも報告すべき

## 実践的な適用

このリポジトリでは`golden-check.py`・`protect-linter-config.py`・`completion-gate.py`がCode-Based評価層を構成し、`code-reviewer`・`security-reviewer`・`product-reviewer`・`design-reviewer`がLLM-as-Judge層を担う。`error-to-codex.py`がregex検出→fix guide注入→codex-debugger提案のハイブリッドパイプラインを実現する。`/review`スキルがdiff内容シグナルで専門レビュアーを自動起動し、confidence 80未満を自動除外する。AutoEvolveの4層ループ（Session→Daily→Cron→On-demand）が「You can never stop looking at data」の思想を体現している。

## 関連概念

- [quality-gates](quality-gates.md) — 評価結果をゲートとして組み込む仕組み
- [automated-code-review](automated-code-review.md) — 自動コードレビューの設計パターン
- [adversarial-evaluation](adversarial-evaluation.md) — 対抗的評価による品質保証

## ソース

- [AI Evals Framework](../../research/2026-03-12-ai-evals-framework.md) — Error Analysis→失敗モード→アプリ固有メトリクスの二層評価アーキテクチャを分析
- [Evals Skills Analysis](../../research/2026-03-19-evals-skills-analysis.md) — TPR/TNR分離計測・Rogan-Gladen補正・ボトムアップ帰納のベストプラクティス
- [SWE-CI Deep Survey](../../research/2026-03-17-swe-ci-deep-survey.md) — evolution-based評価でzero-regression rateを初めて体系的に測定
- [SlopCodeBench](../../research/2026-03-30-slopcodebench-iterative-degradation-analysis.md) — Slope vs Intercept分離・Structural Erosion定量化・テストスイート限界の実証
- [MTI Temperament Profiling](../../research/2026-04-06-mti-temperament-profiling-analysis.md) — 能力とは直交する行動的気質4軸（Reactivity, Compliance, Sociality, Resilience）の独立測定。Compliance-Resilience パラドックス
