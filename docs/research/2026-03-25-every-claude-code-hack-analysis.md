---
source: "Every Claude Code Hack I Know (March 2026) by Matt Van Horn"
date: 2026-03-25
status: integrated
---

## Source Summary

**主張**: IDEは不要。plan.md + 音声入力だけで開発する。計画80%/コーディング20%の比率反転が生産性の鍵。

**手法** (11個):
1. Plan-first workflow（アイデア→即 `/ce:plan` で並列リサーチ→構造化プラン生成）
2. Voice input（Monologue/WhisperFlow → Claude Code 直接入力）
3. 4-6 parallel sessions（Ghostty 複数ウィンドウで並列タスク実行）
4. dangerously-skip-permissions（全ツール許可で自律実行）
5. Stop hook sound notification（完了時サウンド通知）
6. Autosave 500ms（エディタの即時反映で Google Docs 的体験）
7. Research before plan（`/last30days` で最新コミュニティ情報→プランに反映）
8. Meeting transcript → plan.md（Granola MCP でミーティング→プラン変換）
9. Plan files for non-code（戦略文書・記事も同じワークフロー）
10. Mac Mini remote（Telegram + tmux でリモートセッション維持）
11. Claude + Codex 併用（プランは Claude、重い実装は Codex でトークン分散）

**根拠**: 著者の実績（70 plan files, 263 commits/30days, 複数 OSS コントリビュート）

**前提条件**: Claude Max $200/月 + Codex $200/月, Mac, Ghostty + Zed, Compound Engineering プラグイン

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 2 | Voice input (Monologue/WhisperFlow) | N/A | OS/ハードウェアレベル。Claude Code 設定の対象外 |
| 4 | dangerously-skip-permissions | N/A | `disableBypassPermissionsMode: "disable"` + 精密 allow/deny + policy hooks で意図的にセキュリティ優先 |
| 6 | Autosave 500ms (Zed) | N/A | エディタ設定。Claude Code 設定の対象外 |
| 7 | Community pulse research (`/last30days` 的検索) | Partial | `/search-first` + `/research` は存在。Reddit/X/YouTube/HN コミュニティ動向特化のパターンなし |
| 8 | Meeting transcript → proposal | Partial | `/meeting-minutes` は議事録→GitHub Issues 抽出のみ。コードベース+過去文書照合→提案書生成は未実装 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|---------------|--------|
| 1 | `/spec`, `/spike`, `/epd`, `/rpi`, plan-lifecycle hooks | 「1行変更以外は全て plan.md」 | 強化不要 — リスク分析・plan gating 含め記事より高度 |
| 3 | cmux エコシステム、worktree 分離、`/autonomous` | 4-6 Ghostty ウィンドウ手動管理 | 強化不要 — cmux Conductor/Worker 分離が構造的に優位 |
| 5 | `afplay Blow.aiff` + `cmux-notify` on Stop | 同一の `afplay Blow.aiff` | 強化不要 — 完全一致 + cmux-notify 追加済み |
| 9 | `/spec`, `/timekeeper`, `/obsidian-content` | 戦略文書も plan.md ワークフロー | 強化不要 — Obsidian 連携含め非コード用途カバー済み |
| 10 | cmux-remote, Discord MCP, `/schedule` | Telegram + tmux でリモート | 強化不要 — Discord MCP + cmux-remote + scheduled triggers で同等以上 |
| 11 | `codex` skill, codex-reviewer, codex-risk-reviewer | Claude→Codex トークン節約切り替え | **強化可能** — トークン残量に応じた自動委譲パターンなし |

## Integration Decisions

- **#7 取り込み**: `search-first/references/strategies.md` にコミュニティパルス検索戦略を追加
- **#8 取り込み**: `/meeting-minutes` に Proposal Mode を追加（コードベース+過去文書照合→提案書生成）
- **#11 取り込み**: `rules/codex-delegation.md` にトークン予算切り替えセクションを追加

## Plan

| # | タスク | ファイル | 規模 |
|---|--------|---------|------|
| 1 | Community pulse 検索戦略を追加 | `skills/search-first/references/strategies.md` | S |
| 2 | Meeting → Proposal モードを追加 | `skills/meeting-minutes/SKILL.md` | S |
| 3 | Codex トークン予算切り替えルール追加 | `rules/codex-delegation.md` | S |
