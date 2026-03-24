---
source: https://www.anthropic.com/engineering/harness-design-long-running-apps
date: 2026-03-25
status: integrated
author: Prithvi Rajasekaran (Anthropic Labs)
---

## Source Summary

Anthropic Labs による長時間アプリケーション開発のためのハーネス設計記事。Generator-Evaluator 分離アーキテクチャ（GAN インスパイア）、コンテキスト管理（リセット vs コンパクション）、主観的品質の評価基準設計など 12 の手法を、レトロゲームメーカー・DAW・美術館サイトの 3 ケーススタディで実証。

**核心主張**: "every component in a harness encodes an assumption about what the model can't do on its own, and those assumptions are worth stress testing."

**主要手法**:
1. Generator-Evaluator 分離（生成と評価の分離）
2. Context Reset vs Compaction（コンテキスト管理）
3. タスク分解 & 逐次フィーチャー実装
4. 主観的品質の 4 次元評価基準（Design Quality / Originality / Craft / Functionality）
5. 構造化アーティファクトハンドオフ
6. Sprint Contract（実装前スコープ合意）
7. Self-evaluation bias 軽減
8. Context Anxiety 対策
9. QA エージェントの反復チューニング
10. Feature Stubbing 検出
11. Load-bearing Component 特定（仮定のストレステスト）
12. モデル改善に伴うハーネス進化

**ケーススタディ**:
- レトロゲームメーカー: Solo($9/20min) vs Full Harness($200/6hr) — 品質差大
- DAW: 3ラウンド Build-QA で $124.70/3hr50min
- 美術館サイト: 10 イテレーションで美的ピボット（CSS 3D 空間体験）

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Feature Stubbing 検出 | Partial | FM-011 (Plan Adherence) は「ステップ省略」を検出するが「ステップ完了に見えるが実は stub」は対象外 |
| 2 | Assumption Stress-test | Partial | Scaffolding vs Harness 概念はあるが定期的な除去テスト方法論がない |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点/知見 | 強化案 |
|---|-------------|-------------------|--------|
| A | Generator-Evaluator 分離 | 反復 Build-QA ループの自動化 | workflow-guide.md に反復パターン追記 |
| B | Context Reset vs Compaction | モデル別 Context Anxiety 感受性差 | cross-model-insights.md にエントリ追加 |
| C | 主観的品質の評価基準 | 4 次元 + AI slop ペナルティ | design-reviewer.md に評価次元追加 |
| D | Self-evaluation bias | QA の rationalization パターン | failure-taxonomy.md に FM-018 追加 |
| E | ハーネス進化 | 仮定のストレステスト方法論 | improve-policy.md にフェーズ追加 |

## Integration Decisions

全 7 項目を統合（Gap/Partial 2 + Already 強化 5）。

## Changes Made

| ファイル | 変更内容 |
|---------|---------|
| `references/failure-taxonomy.md` | FM-017: Feature Stubbing + FM-018: Evaluator Rationalization 追加 |
| `references/cross-model-insights.md` | Claude Insights にモデル別 Context Anxiety 感受性エントリ追加 |
| `agents/design-reviewer.md` | Subjective Quality 4 次元 + AI Slop 検出パターン追加 |
| `references/improve-policy.md` | 仮定ストレステスト（Assumption Stress-test）フェーズ追加 |
| `references/workflow-guide.md` | 反復 Build-QA パターン（長時間タスク向け）追加 |
