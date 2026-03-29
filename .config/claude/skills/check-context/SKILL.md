---
allowed-tools: Bash(wc *), Bash(cat *), Bash(ls *)
description: Check current context window usage and session state
---

# Check Context

コンテキストウィンドウの使用状況とセッション状態を確認する。

## Session State

!`cat ~/.claude/session-state/last-session.json 2>/dev/null || echo '{"status": "no saved session"}'`

## Edit Counter

!`cat ~/.claude/session-state/edit-counter.json 2>/dev/null || echo '{"count": 0, "note": "no counter"}'`

## Action Guidelines

コンテキストの状況に応じて以下を提案:

| 状況 | 推奨アクション |
|------|-------------|
| Edit数 < 20 | 通常運用。問題なし |
| Edit数 20-30 | 大きな調査はサブエージェントに委譲を検討 |
| Edit数 30-50 | コンテキスト圧縮を推奨 |
| Edit数 > 50 | 新しいセッションでの作業を強く推奨 |

上記の情報を簡潔にまとめて報告すること。
