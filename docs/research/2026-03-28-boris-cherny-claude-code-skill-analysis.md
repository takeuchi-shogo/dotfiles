---
source: "The Complete Boris Cherny Claude Code Skill Changes How You Build Software (X/Twitter thread)"
date: 2026-03-28
status: integrated
---

## Source Summary

Boris Cherny (@bcherny) の42の Claude Code ティップスを5層のレイヤードアーキテクチャとして解説した記事。
各層が次の層を解放する積み上げ式設計で、順番に実装することで Claude Code を「AIエンジニアリングチーム」として機能させるという主張。

**主張**: 42のティップスは単なるリストではなく、Foundation → Team → Customization → Isolation → Orchestration の5層アーキテクチャ。

**手法**: 10手法（並列セッション、Plan+Auto-accept、CLAUDE.md更新、チーム共有、hooks/agents、出力スタイル、カスタムエージェント、Worktree並列、/simplify、/batch）

**根拠**: 実務経験。レビューサイクルが日→時間に短縮。

**前提条件**: Claude Code CLI を日常的に使う開発者・チーム。

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 現状 | 差分 |
|---|------|------|------|------|
| 2 | Plan→Auto-accept | Partial | Plan段階・plansDirectory あり | Auto-accept criteria（リスクレベル別自動承認）未実装 |
| 6 | 出力スタイル切替（Explanatory/Learning/Minimal） | Gap | persona（口調切替）のみ | 認知モード（冗長度・推論深さ）の切替なし |

### Already 項目の強化分析

| # | 手法 | 既存 | 記事パターン | 強化案 |
|---|------|------|-------------|--------|
| 1 | 並列セッション | Agent+worktrees+autonomous | Session pool management | Session Pool Registry で active session 数を track |
| 3 | CLAUDE.md 継続更新 | doc-garden-check + claude-md-management | セッション終了時 tacit knowledge 自動逆流 | Already（強化不要）— analyze-tacit-knowledge で既カバー |
| 4 | チーム共有 CLAUDE.md | AGENT_TEAMS=1 + worktree 内 CLAUDE.md | チーム全員が同一 CLAUDE.md 参照 | N/A — 個人 dotfiles 環境 |
| 5 | チーム hooks/agents | 32 agents + hooks 4層 | 新メンバー加入時の標準 agent 割当 | N/A — 同上 |
| 7 | カスタムエージェント | 32 agents | migration-guard（breaking change 検出） | migration-guard agent 新規定義 |
| 8 | Worktree 並列化 | autonomous + EnterWorktree + isolation: "worktree" | 各エージェント自動 worktree | Already（強化不要）— Agent tool の isolation で対応済み |
| 9 | /simplify | code-simplifier plugin + /review 内並列レビュー | 独立スキルとして detection rules 設定化 | /simplify スキル独自化 |
| 10 | /batch | autonomous + dev-cycle + epd | 対話的計画→多数エージェント→並列PR | Already（強化不要）— /autonomous が同等機能 |

## Integration Decisions

取り込み対象（全5項目）:
1. **[Gap] #6 出力スタイル切替** — 認知モード（Explanatory/Learning/Minimal）の実装
2. **[Partial] #2 Auto-accept criteria** — Plan 承認後の低リスク変更自動実行フレームワーク
3. **[強化] #1 Session Pool Registry** — active session 数の追跡・自動調整
4. **[強化] #7 migration-guard agent** — Breaking change 検出専門エージェント新規定義
5. **[強化] #9 /simplify スキル独自化** — plugin 依存から独自スキル化、detection rules 設定ファイル化

スキップ: #3(強化不要), #4/#5(N/A:個人環境), #8(強化不要), #10(強化不要)

## Plan

→ `docs/plans/2026-03-28-boris-cherny-integration.md` 参照
