---
title: エージェント評価
topics: [evaluation]
sources: [2026-03-12-ai-evals-framework.md, 2026-03-19-evals-skills-analysis.md, 2026-03-17-swe-ci-deep-survey.md, 2026-03-30-slopcodebench-iterative-degradation-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 26
confidence: established
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
- **原子スキル分解と構成的汎化**: ソフトウェアエンジニアリングをCode Localization/Editing/Unit Test生成/Review/Issue再現の最小単位に分解しJoint RLで統合最適化すると、原子スキルの改善がOODの複合タスクに転移する。スキル設計は最小性・自己完結性・独立評価可能性の3原則に従う
- **Wrapper vs Raw の意識的境界**: エージェントに生のprimitiveをどこまで渡すか（Raw Primitive露出）とwrapperで抽象化するかは、安全性・再現性・認知負荷のトレードオフである。無制限のAPI parityはOWASP LLM08 Excessive Agencyのリスクを高めるため、Intentional Restrictionとして意識的に選択すべき
- **「動く」と「使える」の分離**: 仕様通りの機能検証（Evaluator）とユーザー体験の検証（UX Reviewer）は別軸であり、UXの劣化はiteration間のスクリーンショット差分比較で定量的に検出しないと見逃される
- **Reward Hacking対策付きtool_uses計測**: tool_uses count を評価指標に採用する際はPrecision of Tool Useを併用しないとreward hackingを招く。Self-preference Bias（同モデルファミリーの評価者は甘くなる）・Holdout Contamination（評価ケースの最適化ループ混入）・Evaluator Drift（評価器バージョンアップでの基準変動）も既知のリスク
- **5-testの機会費用フィルター**: 新手法の採用可否判断で「6ヶ月スキップした場合のコストはほぼゼロ」という機会費用の反転視点を使うと、FOMO駆動の乗り換えを防げる
- **Teach-back型の理解検証ゲート**: 作業完了後にAI自身が教師役となり、restate-first→3階層理解（problem/solution/broader-context）→クイズの順で人間の理解度を段階的に検証する。self-explanation effect・protégé effectの学習科学的裏付けがある
- **アーキテクチャ＞モデル能力の実証**: Computer Use Agent検証器では、非重複ルーブリック生成・プロセス/アウトカム報酬分離といった設計選択がモデルのバージョンアップより性能差に効き、Cohen's κ 0.64（人間アノテーター間一致率と同等）・偽陽性率0.01-0.08を達成した
- **評価指標自体の内部不整合バグ**: per-skillスコアリングでスキル名による絞り込みが漏れて全スキルに同一セッションスコアが記録される、スコアスケールが1-10と0.0-1.0で混在するなど、メトリクス追加より先に評価基盤自体の構造的バグを直す必要がある

## 実践的な適用

このリポジトリでは`golden-check.py`・`claude-hooks` pre-edit (protect-linter-config)・`completion-gate.py`がCode-Based評価層を構成し、`code-reviewer`・`security-reviewer`・`product-reviewer`・`design-reviewer`がLLM-as-Judge層を担う。`claude-hooks` (post-bash, error-to-codex 機能) がregex検出→fix guide注入→codex-debugger提案のハイブリッドパイプラインを実現する。`/review`スキルがdiff内容シグナルで専門レビュアーを自動起動し、confidence 80未満を自動除外する。AutoEvolveの4層ループ（Session→Daily→Cron→On-demand）が「You can never stop looking at data」の思想を体現している。`references/wrapper-vs-raw-boundary.md`がRaw/Wrapper判断マトリクスを、`skill-writing-guide.md`が独立評価可能性とOnboarding not manuals原則を、`/teachback`コマンドがセッション作業のteach-back検証を提供する。

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
- [Single-Agent vs Multi-Agent Thinking Budget](../../research/2026-04-08-sas-vs-mas-thinking-budget-analysis.md) — SAS対MAS論文を分析、委譲判断基準にDPI根拠明文化を提案
- [Skill Evaluation & Self-Improving Loop](../../research/2026-04-09-skill-eval-self-improving-loop-analysis.md) — スキル評価改善ループを分析、per-skillスコアリング修正等採用
- [Scaling Coding Agents via Atomic Skills](../../research/2026-04-10-atomic-skills-coding-agents-analysis.md) — 原子スキル分解論文を分析、独立評価可能性など4タスク採用
- [Submodular Optimization for Diverse Query Generation](../../research/2026-04-10-submodular-diverse-query-generation-analysis.md) — 部分加法最適化によるクエリ多様化を分析、全項目採用
- [The Art of Building Verifiers for Computer Use Agents](../../research/2026-04-10-universal-verifier-cua-analysis.md) — CUA検証器論文を分析、失敗帰属分離など全7項目採用
- [PostHog『The golden rules of agent-first product engineering』](../../research/2026-04-11-posthog-agent-first-rules-analysis.md) — PostHog記事、wrapper境界文書化とfriction→evalループを採用
- [「仕様通り動く」の先へ、Claude Codeで『使える』を検証する](../../research/2026-04-11-spec-driven-usable-validation-analysis.md) — UX検証記事、UX差分ゲートのみ採用、パイプライン全体は不要判定
- [Autogenesis: A Self-Evolving Agent Protocol](../../research/2026-04-19-autogenesis-absorb-analysis.md) — 自己進化エージェント論文を分析、一部の強化案のみ採用し統一リソース層は棄却
- [Empirical Prompt Tuning skill](../../research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md) — mizchiのプロンプト評価スキルを分析、tool_uses計測等を優先採用
- [How to build a Deep Researcher](../../research/2026-04-24-deep-researcher-absorb-analysis.md) — Deep Researcher記事分析、query3軸・LLM選別等をresearch skillに統合
- [The Self-Healing Agent Harness absorb分析](../../research/2026-04-29-self-healing-harness-absorb-analysis.md) — 自己修復ハーネス記事を分析、outcome-over-trajectory等3件採用
- [Claude Code Routines性能チューニング absorb分析](../../research/2026-04-29-yamadashy-routines-perf-tuning-absorb-analysis.md) — Routines性能チューニング記事を分析、AutoEvolveへ6タスク採用
- [Continually Improving Cursor's Agent Harness absorb分析](../../research/2026-04-30-cursor-harness-absorb-analysis.md) — Cursorハーネス改善記事を分析、11手法全て既存カバーで採用0件
- [What to Learn, Build, and Skip in AI Agents (2026) absorb分析](../../research/2026-04-30-learn-build-skip-2026-absorb-analysis.md) — AIエージェント要点記事を分析、機会費用フィルター1件のみ採用
- [14 Claude Code sub-agents, 4 survived](../../research/2026-05-30-14-subagents-4-survived-absorb-analysis.md) — 60日14サブエージェント実験記事、アンチパターン等軽微採用
- [You're Not Slow. You're Single-Threaded: 300 Agents](../../research/2026-05-30-single-threaded-300-agents-absorb-analysis.md) — Kimi300エージェント群記事、並列主張は全て既存確認済
- [How To Fix AI Slop (Using Hermes)](../../research/2026-05-31-hermes-ai-slop-eval-loop-absorb-analysis.md) — Hermesのeval loop提案を分析、既存基盤が上回り自動closeループ不採用
- [How To Fix AI Slop (Using Hermes) — full-workflow 再分析](../../research/2026-05-31-hermes-eval-loop-absorb-analysis.md) — 同種Hermes eval loop記事を再分析、全Already/意図的retireで採用0
- [Suzanne teach-back prompt](../../research/2026-06-02-suzanne-teachback-absorb-analysis.md) — Suzanne teach-backを分析、軽量/teachbackコマンド採用
- [How to Build Your First Team of AI Agents Using Claude](../../research/2026-06-20-khairallah-agent-team-intro-absorb-analysis.md) — エージェントチーム入門記事は既存30+件と完全rehash、採用0
- [Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering](../../research/2026-07-04-coding-benchmarks-misaligned-absorb-analysis.md) — ベンチマーク不整合position paperは既存哲学と一致、採用0だが引用価値あり
