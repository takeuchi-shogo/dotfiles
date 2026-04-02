---
source: https://github.com/wquguru/harness-books
date: 2026-04-02
status: integrated
---

## Source Summary

### 概要

wquguru/harness-books は2冊の中国語書籍からなるリポジトリ（326 stars、2026-04-01 作成）。
Claude Code と Codex のソースコードを行番号レベルで引用しながら、ハーネスエンジニアリングの設計哲学を分析する。

### Book 1: Harness Engineering — Claude Code 設計指南

- **主張**: ハーネスエンジニアリングは Prompt Engineering の拡大版ではない。不安定なモデルを持続的なエンジニアリング秩序に収束させる制御構造の設計論
- **構造**: 7層（制御面→Query Loop→ツール権限→コンテキスト→エラー回復→マルチエージェント→チーム制度）→ 10原則に圧縮
- **手法**: Claude Code ソースコード（`src/query.ts`, `src/constants/prompts.ts` 等）の具体的な行番号引用に基づく構造分析
- **ソース**: instructkr/claude-code（リーク版）の TypeScript ソース

### Book 2: Claude Code と Codex のハーネス設計哲学

- **主張**: 両システムは「秩序がどの層に配置されるか」で分岐する。機能比較表は無意味
- **核心比喩**: Claude Code = 「運行時共和制」（runtime heartbeat 中心）、Codex = 「控制面立憲制」（structured fragments 中心）
- **手法**: Claude Code（TypeScript）と Codex（Rust）のソースコードを対照分析
- **ソース**: Claude Code + openai/codex のオープンソース

### 10原則（Book 1 Ch9）

1. モデルは不安定部品。同僚ではない
2. Prompt は制御面の一部
3. Query Loop が代理システムの心拍
4. 工具は受管理実行インターフェース
5. コンテキストは作業メモリ（治理可能であるべき）
6. エラーパスは主パス
7. 回復の目標は作業継続
8. マルチエージェントの意義は不確実性の分区
9. 検証は独立すべき（自己採点禁止）
10. チーム制度は個人技巧より重要

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 「運行時共和制 vs 控制面立憲制」ハーネス政体比較フレームワーク | Gap | CC vs Codex の統一比較視座が不在 |
| 2 | 10原則チェックリスト | Partial | 個別原則は CLAUDE.md core_principles に散在、統合チェックリスト未整備 |
| 3 | Codex instruction fragment パターン | Gap | fragment.rs 設計哲学の分析が不足 |

### Already 項目の強化分析

| # | 既存の仕組み | 強化案 |
|---|-------------|--------|
| 1 | CC内部アーキテクチャ分析 (04-01) | 強化不要 — 同等以上の深さ |
| 2 | Scaffolding > Model 原則 | 強化可能 — 政体比喩を委譲ガイドに追記 |
| 3 | Harness Engineering 包括的調査 (03-28~29) | 強化不要 |
| 4 | エラーは主パス概念 | 強化不要 |
| 5 | マルチエージェント検証 | 強化不要 |

## Integration Decisions

- **#1 政体比較フレームワーク**: 取り込み → `references/harness-polity-comparison.md`
- **#2 10原則チェックリスト**: 取り込み → `references/harness-10-principles-checklist.md`
- **#3 Codex fragment パターン**: 取り込み → `rules/codex-delegation.md` に設計哲学セクション追加
- **Already #2 政体比喩追記**: 取り込み → `references/subagent-delegation-guide.md` に追記

## Plan

| # | タスク | 成果物 | 規模 |
|---|--------|--------|------|
| T1 | 分析レポート保存 | この文書 | S |
| T2 | 政体比較フレームワーク | `references/harness-polity-comparison.md` | S |
| T3 | 10原則チェックリスト | `references/harness-10-principles-checklist.md` | S |
| T4 | Codex fragment パターン追記 | `rules/codex-delegation.md` | S |
| T5 | 委譲ガイドに政体比喩追記 | `references/subagent-delegation-guide.md` | S |
