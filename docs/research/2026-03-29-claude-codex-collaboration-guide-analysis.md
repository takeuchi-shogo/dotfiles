---
source: Claude Code × Codex 連携ガイド（記事テキスト直貼り）
date: 2026-03-29
status: integrated
---

## Source Summary

**主張**: 実装作業をCodex CLIにオフロードし、Claudeを判断・レビューに集中させることでRate Limit消費を削減できる。同一タスクでClaudeはCodexの3〜4倍のトークンを消費する。

**手法**:
1. MCP経由のCodex連携 (`claude mcp add codex codex mcp-server`)
2. タスク適性による分業（Claude=設計/レビュー、Codex=実装/テスト生成）
3. 三層セキュリティ防御（設定+hooks+ルール注入）
4. 2段階レビュー+フォールバック（2回失敗→Claude直接実装）
5. 段階的移行（単体最適化→並列化→Codex連携→Skills最適化）
6. Claudeを「プロンプト変換器」として活用

**根拠データ**:
- トークン消費: Figmaプラグイン 4.2倍、スケジューラ 3.2倍、API統合 3.6倍
- SWE-bench: Claude 80.8% > Codex、Terminal-Bench: Codex 77.3% > Claude 65.4%
- 推論速度: Codex 1,000+ tok/s vs Claude ~200 tok/s

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | MCP経由のCodex連携 | N/A | 既に `codex exec` CLI直接呼び出しで連携済み。MCP経由は不要 |
| 2 | タスク適性による分業 | Already (強化可能) | `codex-delegation.md` に振り分けルールあり。実装オフロードの閾値が曖昧 |
| 3 | 三層セキュリティ防御 | Already (強化不要) | settings.json + policy hooks + sandbox で既に三層 |
| 4 | 2段階レビュー+フォールバック | Partial | レビューは実装済み。実装失敗時の自動フォールバックルールなし |
| 5 | 段階的移行 | Already (強化不要) | Phase 1-3完了、Skills化も済み |
| 6 | プロンプト変換器 | Already (強化可能) | `/codex` スキルで確立済み。reasoning effort の手動選択が摩擦 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| 2 | codex-delegation.md の実装委譲セクション | 3-4倍のトークン差の具体的データ | 100行超/テスト生成の閾値とコスト根拠を追記 |
| 6 | /codex スキルの手動reasoning選択 | タスク性質で自動推定が可能 | 自動推定テーブルを追加、ユーザーはオーバーライド可能に |

## Integration Decisions

- [x] #4 Partial → codex-delegation.md にフォールバックルール追加
- [x] #2 強化 → 実装オフロード閾値の具体化（100行超、テスト生成）
- [x] #6 強化 → /codex スキルに reasoning effort 自動推定テーブル追加
- [skip] #1 MCP連携 → N/A（既存CLI直接呼び出しで十分）
- [skip] #3 セキュリティ → Already（強化不要）
- [skip] #5 段階的移行 → Already（完了済み）

## Plan (実行済み)

| # | タスク | ファイル | 規模 |
|---|--------|---------|------|
| 1 | Codex実装失敗フォールバックルール追加 | `rules/codex-delegation.md` | S |
| 2 | 実装オフロード閾値の具体化 | `rules/codex-delegation.md` | S |
| 3 | reasoning effort 自動推定テーブル | `skills/codex/SKILL.md` | S |
