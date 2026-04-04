---
title: 並列エージェントオーケストレーション
topics: [agent, harness]
sources: [2026-04-05-parallel-agent-worktrees-orchestration-analysis.md]
updated: 2026-04-05
---

# 並列エージェントオーケストレーション

## 概要

並列エージェントオーケストレーションとは、複数の AI エージェントを Git worktree で隔離しながら同時並行でタスクを実行させ、オーケストレーターが結果を統合する設計パターンである。Docker Compose がサービスを並列化するのと同じ発想で、worktree がブランチを並列化する。キーとなる洞察は「ブランチは順次切り替えるものではなく、並列実行する環境」であり、コンテキストスイッチを完全に排除することにある。Orchestrator + Subagent の2層構造を基本とし、Awareness Summary・Pre-Merge Conflict Detection・Narrow Context Principle の3つが品質の鍵を握る。

## 主要な知見

- **Orchestrator + Subagent 2層構造**: Orchestrator が全体把握・ワーカー起動・結果収集を担い、Subagent は狭いコンテキストで自律実行（実装→テスト→コミット）する。merge/push は Orchestrator のみが行う
- **Awareness Summary**: 各 Subagent に「他のエージェントが何をしているか」を 1-2 行で伝える相互認識プロトコル。目的は衝突回避であり、過剰な情報共有ではなく「最小限の相互認識」で十分
- **最小入力セット**: `fork_context=false` 時、Subagent に渡す入力はタスク説明・対象パス・Awareness Summary の3つのみ。それ以上は Narrow Context Principle に反する
- **Worktree = ランタイム環境**: worktree はファイルの隔離だけでなく、サーバー・プロセス・ドメインを含むランタイム環境全体の隔離を意味する。ファイルシステム視点での理解は不十分
- **Narrow Context Principle**: コンテキストが狭いほどエージェントの出力品質が上がる。過剰なコンテキストはエージェントの self-doubt（second-guessing）を誘発し、意思決定の質を低下させる
- **Pre-Merge Conflict Detection**: 全 worktree の作業完了後、マージ前に複数エージェントが同一ファイルを変更した箇所を検出・警告する事前チェック。発生後の解決より発生前の検出が安全
- **コンテキストスイッチの完全排除**: 各 worktree が独立した環境を持つため、エージェント（および人間）のコンテキストスイッチが「reduced ではなく gone」になる
- **番号付きタスクリスト UX**: 並列実行タスクを番号付きリスト形式で Orchestrator に渡すことで、進行状況の追跡と結果統合が容易になる

## 実践的な適用

このリポジトリでは `superpowers:dispatching-parallel-agents` と `/dispatch` が並列エージェント起動の基盤を提供する。`/autonomous` スキルが Orchestrator 役を担い、個別の Agent ツール呼び出しが Subagent に対応する。Awareness Summary プロトコルは `references/subagent-delegation-guide.md` に定義されており、fork_context=false 時の最小入力セット（タスク・パス・Awareness Summary）も同ファイルに明記されている。Pre-Merge Conflict Detection は `/autonomous` の Step 4.3 として実装され、全 worktree 完了後にファイル重複を検出する。Narrow Context Principle は既存の `fork_context` ポリシーと合致しており、追加の実装は不要。

## 関連概念

- [multi-agent-architecture](multi-agent-architecture.md) — オーケストレーションのトポロジー設計とエラー増幅率の理論的基盤
- [context-management](context-management.md) — Narrow Context Principle の基盤となるコンテキスト圧縮・分離の体系
- [long-running-agents](long-running-agents.md) — 長時間並列タスクの安定化とチェックポイント戦略
- [harness-engineering](harness-engineering.md) — worktree 隔離を支えるハーネス設計の原則

## ソース

- [Parallel Agent Worktrees Orchestration Analysis](../../research/2026-04-05-parallel-agent-worktrees-orchestration-analysis.md) — Orchestrator+Subagent 2層構造・Awareness Summary・Pre-Merge Conflict Detection・Narrow Context Principle の実践的解説
