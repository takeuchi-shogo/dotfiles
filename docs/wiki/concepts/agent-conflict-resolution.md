---
title: エージェント競合解決
topics: [agent]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 4
confidence: established
---

# エージェント競合解決

並列実行するエージェント間の矛盾を検出・調停するパターン。

## 概要

複数のエージェントが同一データや同一ファイルに対して操作する場合、矛盾する行動（相反する推奨、同一ファイルの矛盾編集、スケジュール競合）が発生しうる。コーディネーター層（Opus）が結果統合時に検証チェックリストを実行することで調停する。

## 核心パターン

| パターン | 対策 |
|---------|------|
| 同一ファイル矛盾編集 | worktree 隔離で物理的に回避 |
| 相反する推奨 | コーディネーターが根拠の強さで判断 |
| 前提の不整合 | ベースコミットを揃える |
| スコープ侵食 | agent 契約（ツール制限）で防止 |
| リソース競合 | MCP ツールの順次実行 |
| Shared State の同時書き込み競合 | CRDT は未導入。現状は非同期・単方向の共有ストア（agent-memory / Vault 同期）に限定してリアルタイム衝突を回避 |
| Verifier への偽装（Reward Hacking） | Verifier がパスすることだけを狙った偽出力を出すリスクがある。周期的な人間監査と Verifier 基準の定期更新で対処 |
| 責務重複による矛盾出力 | Orthogonality Check（出力種別 × ドメインの2軸）で重複するエージェントを検出し統合候補としてフラグする |
| Executor の判断の行き詰まり | Advisor の応答型（plan / correction / stop）による Stop Signal で、対立する判断を構造化してエスカレーションする |

## 適用

- `references/agent-conflict-patterns.md` にカタログとチェックリストを定義
- `/dispatch` 並列実行時にガードレール文言をプロンプトに注入
- `/review` の並列レビューア結果統合時にチェックリスト実行
- `references/subagent-delegation-guide.md` の Return Contract + Re-Flooding 防止ルールで、複数エージェントの返却が親を溢れさせて矛盾を増幅するのを防ぐ

## 関連

- [並列エージェントオーケストレーション](parallel-agent-orchestration.md)
- [マルチエージェント・アーキテクチャ](multi-agent-architecture.md)

## 出典

- Dorsey "World Intelligence" 実装体験記 (2026-04-05): エージェント間競合の実践的な失敗事例と対策
- [Mixture of Experts Explained (Amit Shekhar)](../../research/2026-04-11-moe-article-analysis.md) — MoEをハーネスに類推、Orthogonality Check等3件実装
- [Multi-Agent Coordination Patterns: Five Approaches (Anthropic Blog)](../../research/2026-04-11-multi-agent-coordination-patterns-analysis.md) — 5協調パターンを分析、Shared State制約明示・Reward Hacking検知ルールなど6タスク採用
- [Distribution vs Escalation: Subagents or Advisors absorb分析](../../research/2026-05-04-distribution-vs-escalation-absorb-analysis.md) — Subagent/Advisor使い分け記事を分析、Advisor Stop Signal・Return Contract等5件統合
