---
title: Codex統合
topics: [tooling, claude-code]
sources: [2026-03-29-claude-codex-collaboration-guide-analysis.md, 2026-03-31-codex-plugin-cc-analysis.md, 2026-03-31-codex-plugins-architecture-analysis.md, 2026-04-27-codex-claude-parity-absorb-analysis.md, 2026-04-29-codex-vs-claudecode-role-split-absorb-analysis.md, 2026-05-16-anthropic-agent-sdk-credit-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 6
confidence: established
---

# Codex統合

> **重要 (2026-05-23 更新)**: `/codex:rescue` および `codex-rescue` agent (Skill/subagent_type 両経路) は **廃止**。Permission Storm + Silent Stall + 6-hop chain (観察不能) のため。代替は cmux Worker (`scripts/runtime/launch-worker.sh --model codex --task "..."`) または `codex exec` 直接呼び出し。詳細: memory `feedback_codex_casual_use.md` / `rules/codex-delegation.md`。

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
- **Codex hooks framework の安定化** — Codex CLI v0.124.0 で hooks が stable 化。`.codex/config.toml` の `[hooks]` で `apply_patch` 後の lint 実行等が設定できる
- **Claude↔Codex間のagent/skill/command drift** — Claude 33 agents vs Codex 7、Claude 32 slash commands vs Codex 0、MCP設定も双方向に欠落がある。定期的な同期タスクとして扱う必要がある
- **Codexの「安全設計」を鵜呑みにしない** — Codexのdeny-by-default哲学は理想だが、dotfilesはtrusted profile運用が前提。実際の安全境界は `.codex/config.toml` のprofile設定・lefthook pre-commit・`protect-linter-config` hookの3層で構成される
- **Agent SDK credit billing分離 (2026-06-15〜)** — `claude -p`・Claude Agent SDK・GitHub Actions・third-party SDK appsの利用は新しいcreditプールを消費するが、interactive Claude Code (TUI)とAPI key (Developer Platform) は対象外。credit枯渇時はCodex/Gemini委譲 → extra usage → TUI切替の順にフォールバックする

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

`codex-delegation.md`に実装オフロード閾値（100行超・テスト生成）とコスト根拠を記載。`/codex`スキルにはreasoning effort自動推定テーブルを追加済みで、タスク性質から`low/medium/high`を自動選択しユーザーがオーバーライド可能。Codexの安全設計を鵜呑みにしない注記も`codex-delegation.md`に追記済み。Agent SDK creditの影響範囲は`references/agent-sdk-credit.md`に、フォールバック順序は`references/model-routing.md`のCost-aware Fallback節に実装されている。

## 関連概念

- [Claude Codeアーキテクチャ](claude-code-architecture.md) — Claude Code内部でのCodex連携の実装位置
- [ワークフロー最適化](workflow-optimization.md) — Codex分業によるRate Limit最適化フロー
- [マルチエージェントアーキテクチャ](multi-agent-architecture.md) — Claude-Codex間の協調プロトコル設計

## ソース

- [Claude Code × Codex連携ガイド](../../research/2026-03-29-claude-codex-collaboration-guide-analysis.md) — タスク適性分業・トークンコスト定量データ・フォールバックルール
- [Codex Plugin for Claude Code](../../research/2026-03-31-codex-plugin-cc-analysis.md) — `/codex:review`/`adversarial-review`/`rescue`の機能詳細とdotfilesへの統合決定
- [Codex Plugins Architecture](../../research/2026-03-31-codex-plugins-architecture-analysis.md) — 4層スタック解説とプラグイン構造のGap分析
- [Codex CLI を Claude Code 並みに最適化](../../research/2026-04-27-codex-claude-parity-absorb-analysis.md) — Codex最適化4項目を分析、agents/MCP同期等6件採用
- [Codex vs Claude Code 役割分担](../../research/2026-04-29-codex-vs-claudecode-role-split-absorb-analysis.md) — Codex/Claude Code役割分担記事を分析、注記1件のみ採用
- [Anthropic Agent SDK Credit billing split](../../research/2026-05-16-anthropic-agent-sdk-credit-absorb-analysis.md) — Agent SDK課金分離を検証し6件のreference更新を実装
