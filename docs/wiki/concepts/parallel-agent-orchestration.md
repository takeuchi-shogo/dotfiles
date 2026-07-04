---
title: 並列エージェントオーケストレーション
topics: [agent, harness]
sources: [2026-04-05-parallel-agent-worktrees-orchestration-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 9
confidence: established
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
- **Progressive Trust**: Orchestrator が Subagent への権限を Visibility → Trust → Autonomy の順で段階的に拡大する運用原則。Micro-Loop 規律（小さい単位で実行・確認を繰り返す）と対になり、いきなり広い権限を渡さない
- **フレッシュ視点レビューと router drift の可観測性**: ソロ環境では Orchestrator 自身によるコミット前検証（フレッシュ視点レビュー）が最も過小評価されやすいパターンで、Subagent 数が増えるほど「どの Subagent にルーティングされたか」のログが drift 検出の基盤になる
- **判断のゲート化と失敗の durable artifact 化**: レビューや検証は suggestion ではなく pass/block のゲートとして扱い、失敗は "try harder" ではなく capability gap として文書に変換する。この 2 原則が Orchestrator の品質保証を支える
- **Instruction Budget が Orchestrator のボトルネック**: 常時露出する指示・description・hook 注入・MCP tool 定義を合算した総量が一定を超えると、Subagent への指示遵守率が下がる（2000 トークン超で 20-30% 低下という研究結果あり）。並列数を増やす前に Instruction Budget を計測する価値がある
- **Forked Subagent の意図的不採用**: `CLAUDE_CODE_FORK_SUBAGENT=1`（親 context の全継承）は prompt cache 再利用で fork children 以降の input tokens を大幅に安くできるが、context isolation の利点を消すため既定では採用しない。Return Contract（役割別の返却サイズ上限）と Re-Flooding 防止ルールで、Subagent から Orchestrator への情報逆流を防ぐ方が優先される
- **Cost-Arbitrage パターン**: 生成コストが低く deterministic な verifier が存在し失敗確率が低いタスクに限り、安価な worker を N≥3 並列実行させ、高価な verifier は refute/select のみに専念させるとコスト効率が良い。主観評価や高単価生成には通常の階層 routing を使う

## 実践的な適用

このリポジトリでは `superpowers:dispatching-parallel-agents` と `/dispatch` が並列エージェント起動の基盤を提供する。`/autonomous` スキルが Orchestrator 役を担い、個別の Agent ツール呼び出しが Subagent に対応する。Awareness Summary プロトコルは `references/subagent-delegation-guide.md` に定義されており、fork_context=false 時の最小入力セット（タスク・パス・Awareness Summary）も同ファイルに明記されている。Pre-Merge Conflict Detection は `/autonomous` の Step 4.3 として実装され、全 worktree 完了後にファイル重複を検出する。Narrow Context Principle は既存の `fork_context` ポリシーと合致しており、追加の実装は不要。`CLAUDE_CODE_FORK_SUBAGENT=1` によるコンテキスト全継承は `references/subagent-delegation-guide.md` で意図的不採用として明記されている。

## 関連概念

- [multi-agent-architecture](multi-agent-architecture.md) — オーケストレーションのトポロジー設計とエラー増幅率の理論的基盤
- [context-management](context-management.md) — Narrow Context Principle の基盤となるコンテキスト圧縮・分離の体系
- [long-running-agents](long-running-agents.md) — 長時間並列タスクの安定化とチェックポイント戦略
- [harness-engineering](harness-engineering.md) — worktree 隔離を支えるハーネス設計の原則

## ソース

- [Parallel Agent Worktrees Orchestration Analysis](../../research/2026-04-05-parallel-agent-worktrees-orchestration-analysis.md) — Orchestrator+Subagent 2層構造・Awareness Summary・Pre-Merge Conflict Detection・Narrow Context Principle の実践的解説
- [Claude Code Harness Blueprint (leaked CC internals)](../../research/2026-04-08-cc-harness-blueprint-analysis.md) — CC内部4層設計を分析、7項目をharnessに統合済み
- [Subagents in Claude Code (Anthropic公式ブログ)](../../research/2026-04-08-subagents-claude-code-analysis.md) — 公式サブエージェント指南を分析、レビュー強制と可観測性を追加
- [CREAO AI-First戦略記事 (CREAO CTO) 分析](../../research/2026-04-14-creao-ai-first-analysis.md) — CREAO記事のharness engineering手法を分析、4原理のみ抽出し採用
- [Harnesses are everything (Baseten blog)](../../research/2026-04-19-harness-everything-absorb-analysis.md) — ハーネス設計記事を分析、instruction budget計測等6項目全採用
- [google/skills + ADK 2.0 Multi-Agent Orchestration Patterns](../../research/2026-04-24-google-skills-adk2-absorb-analysis.md) — google/skills 13個全採択、ADK 2.0パターンは強化不要と判定
- [Subagent Context Fork absorb分析 (aitmpl系記事)](../../research/2026-04-27-subagent-context-fork-absorb-analysis.md) — Subagent context fork記事を分析、fork機能非採用・観測3件採用
- [Distribution vs Escalation: Subagents or Advisors absorb分析](../../research/2026-05-04-distribution-vs-escalation-absorb-analysis.md) — Subagent/Advisor使い分け記事を分析、決定表等5件統合
- [The Self-Improving Loop: 300-agent swarm on Kimi K2.6](../../research/2026-06-18-kimi-k26-self-improving-swarm-loop-absorb-analysis.md) — Kimi swarm記事はほぼrehash、Cost-Arbitrageのみbest-of-nガイドに採用
