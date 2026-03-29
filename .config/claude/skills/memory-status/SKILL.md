---
allowed-tools: Bash(wc *), Bash(ls *), Bash(cat *)
description: Show memory system status and usage summary
---

# Memory Status

メモリシステムの状態を確認し、整理が必要かどうかを判断する。

## MEMORY.md

!`wc -l ~/.claude/projects/*/memory/MEMORY.md 2>/dev/null || echo "0 (no MEMORY.md found)"`

!`cat ~/.claude/projects/*/memory/MEMORY.md 2>/dev/null | head -50`

## Memory Detail Files

!`ls -la ~/.claude/projects/*/memory/*.md 2>/dev/null || echo "No detail files"`

## Agent Memory

!`ls -la ~/.claude/agent-memory/*.md 2>/dev/null || echo "No agent memory files"`

## Health Check

以下の基準で評価:

| チェック項目 | 基準 | ステータス |
|------------|------|----------|
| MEMORY.md 行数 | < 200行 | 200行超なら整理必要 |
| 重複エントリ | 0件 | あれば統合 |
| 古い情報 | なし | あれば更新/削除 |
| 機密情報 | なし | あれば即削除 |
| 詳細ファイル分離 | 適切 | 長いセクションは分離推奨 |

上記の情報を確認し、以下を報告すること:
1. MEMORY.md の現在の行数と上限（200行）までの余裕
2. 記録されているパターンの概要
3. 整理が必要な場合は具体的な提案
