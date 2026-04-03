---
title: メタ進化
topics: [ml-rl]
sources: [2026-03-18-evox-meta-evolution-analysis.md, 2026-03-26-hyperagents-analysis.md, 2026-03-29-hyperagents-dgmh-analysis.md]
updated: 2026-04-04
---

# メタ進化

## 概要

メタ進化とは、解候補だけでなく「探索戦略自体」も進化させる二重ループ構造であり、固定戦略の停滞を突破する手法を指す。EvoXは二重ループ共進化（内側：解の進化、外側：戦略の進化）を提案し、HyperagentsはTask AgentとMeta Agentを単一の編集可能プログラムに統合した「メタ認知的自己修正」（改善プロセス自体が編集対象）を実現した。メタレベルの改善はドメイン間で60-80%が転移し、一設定での改善が別設定での継続改善と複合する「複利的自己改善」が確認されている。

## 主要な知見

- **二重ループ共進化**: 内側ループ（解の進化）と外側ループ（戦略の進化）を分離して共進化させる
- **停滞検知 → 戦略切替**: 閾値τ・スライディングウィンドウWで停滞を検知し、demand-drivenで戦略を切り替える
- **Population State Descriptor**: スコア統計・フロンティア構造・進捗指標・直近ウィンドウ統計を統合した状態記述子
- **戦略データベースH**: 過去戦略の（戦略・状態・パフォーマンス）を記録し、次回の条件付き推論に活用する
- **メタ認知的自己修正**: 改善 → 改善方法の改善 → ... という再帰的自己改善を実現する
- **クロスドメイン転移**: メタレベル改善（メモリ導入・トラッキング）がドメイン横断で60-80%転移する
- **永続メモリの自発的出現**: 因果仮説・合成的洞察・前方計画・過修正診断を蓄積する仕組みが自律的に発生
- **複利的自己改善**: 論文レビュー+ロボティクスで学んだ改善戦略が数学採点でも有効（0.0→0.710への向上）
- **バリデーション閾値**: デプロイ前に新戦略を検証し、閾値超の修正のみを採用する安全機構
- **reward tampering対策**: 改善目標の動的自己調整は意図的に禁止し、改善速度の急加速を警告する

## 実践的な適用

このリポジトリのAutoEvolve 4層ループ（Session→Daily→BG→/improve）がメタ進化の実装に最も近い。`stagnation-detector.py`がEvoXの停滞検知を実装し、`scripts/policy/`内のerror-to-codex.pyがエラー反応型の戦略切替を担う。`learnings/*.jsonl`が戦略有効性の記録（what-happenedレベル）を保持し、`improve-policy.md`の26ルールがバリデーション閾値と改善速度の安全制約を定義する。`experiment_tracker`にtransfer_domainフィールドを追加することで転移効率の定量追跡が可能になる。

## 関連概念

- [self-improving-agents](self-improving-agents.md) — 自己改善エージェントの設計原則
- [rlhf-alignment](rlhf-alignment.md) — 強化学習による整合性調整
- [trajectory-learning](trajectory-learning.md) — 軌跡データからの学習手法

## ソース

- [EvoX Meta-Evolution](../../research/2026-03-18-evox-meta-evolution-analysis.md) — 解と探索戦略の二重ループ共進化で~200タスクの数学・アルゴリズム最適化を上回る性能を実証
- [Hyperagents Analysis](../../research/2026-03-26-hyperagents-analysis.md) — Task Agent + Meta Agentの統合とメタ認知的自己修正によるドメイン横断転移の実証
- [Hyperagents DGM-H Analysis](../../research/2026-03-29-hyperagents-dgmh-analysis.md) — DGM-Hのアーカイブベース探索・永続メモリ・複利的自己改善の詳細分析
