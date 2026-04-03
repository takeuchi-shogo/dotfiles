---
title: マルチエージェントアーキテクチャ
topics: [agent]
sources: [2026-03-12-subagent-patterns-analysis.md, 2026-03-23-multi-agent-scaling-analysis.md, 2026-03-26-hierarchical-mas-theory-analysis.md, 2026-04-02-self-organizing-llm-agents-analysis.md]
updated: 2026-04-04
---

# マルチエージェントアーキテクチャ

## 概要

マルチエージェントシステムの設計は「増やせば賢くなる」という単純な話ではなく、タスクの特性（並列可能か逐次推論か）によって効果が大きく異なる。階層化された構造では制御スパンを O(log W) に圧縮することでエラーの連鎖増幅を抑制でき、フラットな線形チェーンが引き起こす指数的失敗拡大を回避できる。また大規模実験（25,000+ タスク）では、プロトコル選択が品質差異の 44% を説明し、モデル選択は約 14% にとどまることが示されており、協調設計こそが最重要変数である。

## 主要な知見

- **Sync / Async / Scheduled の3パターン**: サブエージェント委譲はブロッキング（結果待ち）、ファイア＆フォーゲット（長時間非同期）、定期スケジュールの3形式に分類できる
- **並列化の両刃**: 独立並列構成ではエラーが 17.2 倍に増幅するが、中央集権型では 4.4 倍に抑制される。並列化は慎重なトポロジ設計が前提
- **Depth-1 原則**: サブエージェントはサブエージェントを生まない（深さ 1 制限）。再帰的委譲は制御とデバッグを困難にする
- **Sequential プロトコルが最優秀**: 4〜256 エージェントへのスケーリングで品質低下なし（p=0.61）。Shared メモリ方式との差は +44%（Cohen's d=1.86）
- **能力閾値が分岐点**: 強力なモデルでは自律性で +3.5% 改善、弱いモデルでは自律性が -9.6% の悪化を招く
- **3層構造分離（HMASTheory）**: トポロジ圧縮・スコープ分離・検証ゲートの3メカニズムを組み合わせると失敗指数が Θ(W) から O(log W) に低減する
- **異種レビューアーの優位性**: 均質な8エージェントより異種2エージェントの方が AUROC が高い（84.2 vs 81.4）。エラーモードの直交性が重要
- **コンテキスト圧縮が本質的 ROI**: 並列性よりも、サブエージェントへの委譲によるコンテキスト分割・圧縮が実際の価値源泉
- **Generic > Specialized**: 特化エージェントを増やすより、汎用エージェントにチェックリストを注入する段階的特化の方がルーティング複雑度を抑えられる

## 実践的な適用

dotfiles リポジトリでは3種のサブエージェントパターンが実装済みである。Sync は `/review` での 2〜4 エージェント並列起動・結果統合、Async は `claude -p` 子プロセス（`/research`, `/autonomous`）、Scheduled は `autoevolve-runner.sh` cron ジョブ（毎日 3:00）が対応する。Depth-1 原則はエージェント設計で厳守しており、サブエージェントは Agent ツールを持たない。マルチモデル統合（Claude + Codex + Gemini）は能力特性に基づくルーティング（`agent-router.py`）で実現されており、Codex はレビュー・設計相談、Gemini は 1M コンテキスト分析に役割分担している。Sequential プロトコルへの移行は現在 Gap として認識されており、Implicit Coordinator パターンからの昇格が課題である。

## 関連概念

- [harness-engineering](harness-engineering.md) — ハーネス設計とエージェント協調のインフラ基盤
- [context-management](context-management.md) — エージェント間コンテキスト分離と圧縮
- [long-running-agents](long-running-agents.md) — 長時間自律タスクの管理と安全機構

## ソース

- [Three Sub-Agent Patterns Analysis](../../research/2026-03-12-subagent-patterns-analysis.md) — Sync/Async/Scheduled の3パターン分類とコンテキスト圧縮が真のROI
- [Multi-Agent Scaling Analysis](../../research/2026-03-23-multi-agent-scaling-analysis.md) — Google/Anthropic/Cognition の3視点からスケーリング特性を検証。エラー増幅率の定量データあり
- [Hierarchical MAS Theory Analysis](../../research/2026-03-26-hierarchical-mas-theory-analysis.md) — トポロジ圧縮・スコープ分離・検証ゲートによる失敗指数削減の数理理論
- [Self-Organizing LLM Agents Analysis](../../research/2026-04-02-self-organizing-llm-agents-analysis.md) — 25,000+ タスクの大規模実験。Sequential プロトコルの優位性と能力閾値効果
