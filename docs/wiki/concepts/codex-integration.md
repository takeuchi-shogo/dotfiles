---
title: Codex統合
topics: [tooling, claude-code]
sources: [2026-03-29-claude-codex-collaboration-guide-analysis.md, 2026-03-31-codex-plugin-cc-analysis.md, 2026-03-31-codex-plugins-architecture-analysis.md]
updated: 2026-04-04
---

# Codex統合

## 概要

CodexはOpenAIのコーディング特化CLIエージェントで、Claude Codeと補完的な役割分担を持つ。Claude（設計・レビュー・判断）とCodex（実装・テスト生成・高速推論）の分業により、同一タスクでClaudeの3〜4倍のトークン消費効率を実現できる。dotfilesではClaude Code内から`/codex`スキルおよびCodex Plugin（`codex-plugin-cc`）経由で統合し、Codex Review Gate・リスク分析・レスキュー委譲を実現している。

## 主要な知見

- **トークン差の定量データ** — Figmaプラグイン4.2倍、スケジューラ3.2倍、API統合3.6倍のトークン消費差。Rate Limit節約の根拠
- **ベンチマーク適性の違い** — SWE-bench: Claude 80.8% > Codex（設計判断）。Terminal-Bench: Codex 77.3% > Claude 65.4%（実装実行）
- **推論速度差** — Codex 1,000+ tok/s vs Claude ~200 tok/s。テスト生成・ボイラープレート生成に有利
- **4層スタック（Codex側）** — Skills（ワークフローロジック）→ MCP（ツール/コンテキスト）→ Apps（認証統合）→ Plugins（パッケージ化）
- **Steerable Adversarial Review** — `/codex:adversarial-review`でフォーカステキスト付きの挑戦的レビューが可能
- **Rescueパターン** — `/codex:rescue`でセッション継続付き委譲（`--resume`/`--fresh`）。詰まった実装のエスカレーション先
- **バックグラウンドジョブ管理** — `status/result/cancel`でCodexジョブを非同期追跡
- **フォールバックルール** — レビュー2回失敗時のClaude直接実装への自動切替

## 実践的な適用

dotfilesでの分業テーブル：

| ユースケース | 推奨手段 |
|------------|---------|
| `/review`ワークフロー内の自動レビュー | 既存`codex-reviewer`エージェント |
| 手動でブランチ比較レビュー | `/codex:review --base main` |
| 実装前リスク分析 | `codex-risk-reviewer`エージェント |
| 実装後のadversarialレビュー | `/codex:adversarial-review` |
| Codexへのインライン実行（100行超/テスト生成） | `/codex`スキル |
| 詰まった実装の委譲 | `/codex:rescue` |

`codex-delegation.md`に実装オフロード閾値（100行超・テスト生成）とコスト根拠を記載。`/codex`スキルにはreasoning effort自動推定テーブルを追加済みで、タスク性質から`low/medium/high`を自動選択しユーザーがオーバーライド可能。

## 関連概念

- [Claude Codeアーキテクチャ](claude-code-architecture.md) — Claude Code内部でのCodex連携の実装位置
- [ワークフロー最適化](workflow-optimization.md) — Codex分業によるRate Limit最適化フロー
- [マルチエージェントアーキテクチャ](multi-agent-architecture.md) — Claude-Codex間の協調プロトコル設計

## ソース

- [Claude Code × Codex連携ガイド](../../research/2026-03-29-claude-codex-collaboration-guide-analysis.md) — タスク適性分業・トークンコスト定量データ・フォールバックルール
- [Codex Plugin for Claude Code](../../research/2026-03-31-codex-plugin-cc-analysis.md) — `/codex:review`/`adversarial-review`/`rescue`の機能詳細とdotfilesへの統合決定
- [Codex Plugins Architecture](../../research/2026-03-31-codex-plugins-architecture-analysis.md) — 4層スタック解説とプラグイン構造のGap分析
