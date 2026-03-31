---
source: https://github.com/openai/codex-plugin-cc
date: 2026-03-31
status: integrated
---

## Source Summary

Codex Plugin for Claude Code。Claude Code 内から Codex をプラグインとして呼び出し、3つの機能を提供:
- `/codex:review` — 標準 read-only レビュー（`--base`, `--background` 対応）
- `/codex:adversarial-review` — ステアリング可能な挑戦レビュー（カスタムフォーカステキスト付き）
- `/codex:rescue` — Codex へのタスク委譲（`--resume`/`--fresh` でセッション継続、`--background` 対応）
- ジョブ管理: `/codex:status`, `/codex:result`, `/codex:cancel`
- オプション: review gate（Stop hook で Codex レビューを強制。リミット消費リスク高）

Codex app server 経由で動作。ローカルの auth/config/MCP をそのまま利用。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | バックグラウンドジョブ管理 (status/result/cancel) | Gap | `codex exec` インライン実行のみ |
| 2 | Steerable adversarial review | Partial | `codex-risk-reviewer` は実装前特化。実装後の adversarial コードレビューなし |
| 3 | Rescue（セッション継続付き委譲） | Partial | `/codex` スキルあるが resume/thread 追跡なし |
| 4 | Plugin marketplace install | N/A | インストール手段であり手法ではない |

### Already 項目の強化分析

| # | 既存の仕組み | プラグインの利点 | 判定 |
|---|-------------|-----------------|------|
| 1 | `/codex-review` + `codex-reviewer` | `--base`, `--background` ネイティブ対応 | 強化可能（共存で解決） |
| 2 | `completion-gate.py` | Review gate（Codex レビュー自動トリガー） | 強化不要（リミット消費リスク高） |

## Integration Decisions

- **採用**: プラグインをそのままインストール。既存スキル・エージェントと共存
- **スキップ**: review gate（記事自体がリスク注意喚起。completion-gate.py で十分）
- **スキップ**: 使い分けガイド追記（プラグインのコマンドは直感的で、既存との混乱リスク低い）

## 既存統合との使い分け

| ユースケース | 推奨 |
|-------------|------|
| `/review` ワークフロー内の自動レビュー | 既存 `codex-reviewer` エージェント |
| 手動でブランチ比較レビュー | `/codex:review --base main` |
| 実装前リスク分析 | 既存 `codex-risk-reviewer` エージェント |
| 実装後の adversarial レビュー | `/codex:adversarial-review` |
| Codex への inline 実行 | 既存 `/codex` スキル |
| バックグラウンドタスク委譲 | `/codex:rescue --background` |
