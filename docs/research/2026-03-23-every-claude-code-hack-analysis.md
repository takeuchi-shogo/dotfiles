---
source: "Every Claude Code Hack I Know (March 2026) by @mvanhorn"
date: 2026-03-23
status: integrated
---

## Source Summary

**主張**: Claude Code の最大の生産性レバーは「plan-first development」。コーディング前に構造化プランを作り、複数セッションを並列実行し、音声入力で思考速度を維持することで、従来の80%コーディング/20%計画を反転させる。

**手法**:
1. Plan-first development — アイデア→即 `/ce:plan`（Compound Engineering プラグイン）。複数リサーチエージェント並列→構造化 plan.md→ `/ce:work` で実行
2. Voice input — Monologue/WhisperFlow で音声→Claude Code
3. 4-6 並列セッション — Ghostty 窓×4-6、各セッションが独立タスク実行
4. Bypass permissions — `defaultMode: bypassPermissions` + `skipDangerousModePermissionPrompt`
5. 完了サウンド通知 — Stop hook で `afplay` 実行
6. Zed autosave 500ms — ファイル変更即同期、Google Docs 風協調編集体験
7. Research-before-plan — `/last30days` で最新 SNS/コミュニティ情報収集→plan に反映
8. Meeting→plan.md — Granola transcript + codebase context → 提案書生成
9. Mac Mini リモート — Telegram 連携 + tmux で場所を問わず作業
10. Codex 併用 — Claude 計画 + Codex 実装、トークン節約

**根拠**: 著者は 70 plan files / 263 commits in 30 days。Compound Engineering #3 contributor。複数 OSS プロジェクトにマージ実績。

**前提条件**: Compound Engineering プラグイン依存、Mac 環境、$200/月×2 プラン（Claude Max + Codex）、Ghostty + Zed 環境

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Plan-first development | Already | `/spec`, `/spike`, `/epd`, `/rpi` スキル + CLAUDE.md に plan-first ワークフロー明示 |
| 2 | Voice input | N/A | ツール選択はユーザーの環境設定。Claude Code 側の設定変更不要 |
| 3 | 4-6 並列セッション | Already | cmux エコシステム + worktree 分離 + サブエージェント並列実行 |
| 4 | Bypass permissions | 意図的不採用 | harness 設計思想により粒度の高い allow-list + hook ガードを採用。bypass はセキュリティリスク |
| 5 | 完了サウンド通知 | Partial→Integrated | cmux-notify 既存。Stop hook に `afplay` を追加 |
| 6 | Zed autosave 500ms | Gap→Integrated | `on_focus_change` → `after_delay: 500ms` に変更 |
| 7 | Research-before-plan | Partial | `/research` スキル（マルチモデル並列）は存在。SNS 横断の `/last30days` 相当はなし |
| 8 | Meeting→plan.md | Already | `meeting-minutes` スキルが存在 |
| 9 | Mac Mini リモート | Partial | cmux-remote + Discord MCP で部分カバー |
| 10 | Codex 併用 | Partial | codex-reviewer/risk-reviewer/debugger 実装済み。クレジット自動切替はなし |

## Integration Decisions

- **Integrated**: Zed autosave 500ms、Stop hook サウンド通知
- **Skipped (Already)**: Plan-first, 並列セッション, Meeting→plan
- **Skipped (意図的不採用)**: Bypass permissions — harness 設計と相反
- **Skipped (N/A)**: Voice input — 環境設定の範疇
- **Skipped (Partial, 現状十分)**: Research-before-plan, Mac Mini remote, Codex credit management — 既存の仕組みで十分カバーされている

## Changes Made

1. `.config/zed/settings.json`: `autosave` を `"on_focus_change"` → `{"after_delay": {"milliseconds": 500}}` に変更
2. `.config/claude/settings.json`: Stop hook に `afplay /System/Library/Sounds/Blow.aiff` を追加
