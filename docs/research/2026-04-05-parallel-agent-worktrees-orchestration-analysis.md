---
source: https://dev.to/mexiter/claude-code-parallel-agent-driven-worktrees-orchestration-5bf0
date: 2026-04-05
status: integrated
---

## Source Summary

**Title**: "I Built a Parallel Agent Orchestrator. Here is the Architecture."
**Author**: Mex Emini
**Date**: 2026-04-01

### 主張
ブランチは順次切り替えるものではなく、並列実行する環境であるべき。Git worktree + エージェント並列実行でコンテキストスイッチを完全排除する。Docker Compose がサービスを並列化するように、worktree がブランチを並列化する。

### 手法
1. **`/worktree` スキル** — ブランチごとに隔離ディレクトリ + 固有ドメイン + サーバー自動起動（~150行のマークダウン）
2. **`/parallel` エージェント** — 番号付きタスクリストで複数タスクを同時に worktree で並列実行（~180行のマークダウン）
3. **Orchestrator + Subagent 2層アーキテクチャ** — Orchestrator が全体把握・ワーカー起動・結果収集。Subagent は狭いコンテキストで自律実行（実装→テスト→コミット）、merge/push は禁止
4. **Awareness Summary** — 各 Subagent に「他のエージェントが何をしているか」を 1-2 行で伝える。目的は衝突回避
5. **Pre-Merge Conflict Detection** — 全 worktree 完了後、マージ前に複数エージェントが同一ファイルを変更した箇所を検出・警告
6. **狭いコンテキスト原則** — コンテキストが狭いほどエージェントの出力品質が上がる。過剰なコンテキストはエージェントの self-doubt を誘発

### 根拠
- 著者の実体験: コンテキストスイッチが「reduced ではなく gone」
- Docker Compose とのアナロジー: サービス並列化 → ブランチ並列化
- 狭いコンテキストの実践知: 過剰コンテキストのエージェントは「second-guess themselves」

### 前提条件
- PHP/Laravel スタック（Herd/Valet によるローカルドメインサーバー）
- Claude Code のカスタムコマンド対応環境
- Git worktree の基本理解

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | `/worktree` スキル（隔離ディレクトリ + 固有ドメイン + サーバー自動起動） | **Partial** | `Agent(isolation: "worktree")` と `/autonomous` が worktree 隔離を提供。固有ドメイン + サーバー自動起動は未実装（dotfiles では不要） |
| 2 | `/parallel` エージェント（番号付きタスクリストで並列実行） | **Partial** | `superpowers:dispatching-parallel-agents` + `/dispatch` + `/autonomous` が存在。記事の「番号付きリストで全自動」UX はなかった |
| 3 | Awareness Summary（Subagent 間の相互認識） | **Gap** | `subagent-delegation-guide.md` にコンテキスト境界の原則はあるが、Awareness Summary プロトコルは未定義 |
| 4 | Pre-Merge Conflict Detection | **Gap** | `/autonomous` に「コンフリクト発生時は停止」とあるが、事前検出の仕組みはなかった |
| 5 | 狭いコンテキスト原則 | **Already** | `fork_context` ポリシー + `Context Inheritance Policy` |
| 6 | Orchestrator + Subagent 2層アーキテクチャ | **Already** | CLAUDE.md の `agent_delegation` + `/dispatch` + `/autonomous` |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| 5 | `fork_context` ポリシー: true/false で継承制御 | 各 Subagent に exactly 3 inputs（タスク、パス、awareness summary） | **強化可能→実施**: `fork_context=false` 時の最小入力セットを `subagent-delegation-guide.md` に明文化 |
| 6 | `agent_delegation` + `/dispatch` + `/autonomous` | Subagent は merge/push 禁止 | **強化不要**: 既存の委譲ポリシーが同等以上の制御を提供 |

## Integration Decisions

全 Gap/Partial 項目 + Already 強化 #5 を取り込み:

1. ✅ **Awareness Summary プロトコル** → `subagent-delegation-guide.md` に追加
2. ✅ **fork_context=false 最小入力セット** → `subagent-delegation-guide.md` に追加
3. ✅ **Pre-Merge Conflict Detection** → `autonomous/SKILL.md` に Step 4.3 として追加
4. ✅ **並列タスクリスト UX** → `dispatch/SKILL.md` に番号付きリスト形式を追加
5. ✅ **Worktree = ランタイム環境の原則** → `subagent-delegation-guide.md` に追加

## Plan

| # | タスク | 対象ファイル | 規模 |
|---|--------|-------------|------|
| T1 | Awareness Summary + 最小入力セット | `references/subagent-delegation-guide.md` | S |
| T2 | Pre-Merge Conflict Detection (Step 4.3) | `skills/autonomous/SKILL.md` | S |
| T3 | 並列タスクリスト UX | `skills/dispatch/SKILL.md` | S |
| T4 | Worktree = ランタイム環境の原則 | `references/subagent-delegation-guide.md` | S |
| T5 | 分析レポート保存 | `docs/research/` | S |
