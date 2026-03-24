---
source: ユーザー構想 — Claude Code + Codex 協調開発サイクル
date: 2026-03-25
status: integrated
---

## Source Summary

Issue 起点の Claude Code + Codex 協調開発サイクル。6ステップで品質を担保しつつ人間介入を最小化する。

**手法**:
1. Claude Code で要件→Issue 作成
2. Codex で Issue をねっとりレビュー（抜け漏れ防止）
3. Claude Code で実装→Push→PR
4. Codex で PR にレビューコメント投稿
5. ユーザーが Codex の漏れを補完コメント
6. AI (Claude/Codex) が修正→ユーザー確認→マージ

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Claude で Issue 作成 | Partial | `/interviewing-issues` は既存 Issue 明確化。ゼロからの Issue 生成フローなし |
| 2 | Codex Issue レビュー | Gap | Codex はコードレビュー専用。Issue/仕様レビューパスなし |
| 3 | Claude Code 実装→Push | Already | `/rpi`, `/create-pr-wait` で対応済み |
| 4 | Codex PR コメント投稿 | Partial | `/codex-review` でレビュー可能だが GitHub 投稿統合なし |
| 5 | ユーザー補完コメント | N/A | 人間のステップ |
| 6 | 修正振り分け | Partial | `/github-pr` にコメント対応あるが振り分けロジックなし |

### Already 項目の強化分析

| # | 既存の仕組み | 弱点 | 強化案 |
|---|-------------|------|--------|
| 3 | `/create-pr-wait` | Issue レビュー未完了で着手するリスク | Issue レビュー完了を前提条件に |

## Integration Decisions

- 全 Gap/Partial を取り込み
- 3つの実行モード (auto / manual / semi) を全て作成
- dotfiles で試験、他リポジトリに展開

## Plan

`docs/plans/2026-03-25-dev-cycle-integration.md` 参照
