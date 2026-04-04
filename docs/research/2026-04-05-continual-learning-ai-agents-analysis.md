---
source: Harrison Chase, "Continual learning for AI agents" (LangChain blog)
date: 2026-04-05
status: integrated
---

# Continual Learning for AI Agents

## Source Summary

**著者**: Harrison Chase (LangChain)
**主張**: AI エージェントの継続的学習は Model（重み更新）/ Harness（コード+常時付随する指示・ツール）/ Context（設定可能な指示・スキル・メモリ）の3層で起きる。多くの人はモデル層のみに注目するが、ハーネス層・コンテキスト層の学習が実用上より重要であり、すべての学習フローはトレースを共通基盤とする。

### 手法

- **3層分類フレームワーク**: Model（SFT/RL で重み更新、catastrophic forgetting が課題）、Harness（Meta-Harness 等でコード自動最適化）、Context（メモリ・スキル・指示の更新）
- **コンテキスト学習の粒度**: agent-level（SOUL.md 等）/ tenant-level（user, org, team）/ 混合
- **コンテキスト更新の2タイミング**: offline "dreaming"（バッチでトレースを分析）vs hot-path（実行中にリアルタイム更新）
- **明示性の軸**: ユーザー主導（"remember this"）vs エージェント自律（ハーネス指示に基づく自動記憶）
- **Meta-Harness パターン**: タスク実行→評価→トレースFS保存→コーディングエージェントがハーネス改善提案
- **トレース中心アーキテクチャ**: 全学習フロー（model/harness/context）の共通入力としてトレースを位置づけ

### 根拠

- Claude Code / OpenClaw の実装例
- Meta-Harness 論文（TerminalBench-2 で SoTA）
- LangSmith + Deep Agents の本番運用

### 前提条件

- ループ実行可能なエージェントシステム
- トレース収集・保存基盤の存在
- 評価可能なタスクセット

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | コンテキスト学習の粒度（agent / tenant / user / org） | **Partial** | user-level（MEMORY.md）と agent-level（`.claude/agent-memory/`）は存在。tenant/org 粒度は個人 dotfiles のため不要 |
| 2 | トレース中心アーキテクチャ（全学習フローの統一基盤） | **Partial** | `session-trace-store.py` → `session-learner.py` → `findings-to-autoevolve.py` のパイプラインが実質的にトレース中心の学習を実現。概念的な統一ドキュメントはないが実装は対応済み |
| 3 | 3層分類フレームワーク | **N/A** | 分類概念の紹介。当セットアップは既にこの3層を実装済みで、分類自体を追加する実益なし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|--------------|--------|
| 1 | Meta-Harness パターン — 分析済み・AutoEvolve に統合 | 記事は harness-level learning の代表例として引用。新情報なし | Already (強化不要) |
| 2 | コンテキスト更新の2タイミング — offline: AutoEvolve、hot-path: session-learner + eureka | 記事は "dreaming" と "hot-path" を区別。OpenClaw dreaming ≈ AutoEvolve bg loop | Already (強化不要) |
| 3 | 明示性の軸 — user-prompted: /improve, /eureka。autonomous: hooks | 記事は explicit vs implicit を軸として提示。両方カバー済み | Already (強化不要) |

## Integration Decisions

- **#1 Partial（粒度）**: 個人 dotfiles のため tenant/org 粒度は不要。スキップ
- **#2 Partial（トレース中心）**: wiki `trajectory-learning.md` に Chase の3層フレームワークを追記し、トレースが全層の学習を駆動する統一概念であることを明記

## Plan

| # | タスク | 規模 | ファイル |
|---|--------|------|---------|
| 1 | wiki `trajectory-learning.md` に Chase の3層継続学習フレームワークを追記 | S | `docs/wiki/concepts/trajectory-learning.md` |
| 2 | 分析レポート保存 | S | `docs/research/2026-04-05-continual-learning-ai-agents-analysis.md` |
