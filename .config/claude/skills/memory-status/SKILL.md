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

## Dashboard Statistics

!`echo "=== Memory Type Distribution ===" && for type in user feedback project reference; do count=$(grep -l "type: $type" ~/.claude/projects/*/memory/*.md 2>/dev/null | wc -l | tr -d ' '); echo "  $type: $count files"; done`

!`echo "=== Knowledge Pyramid Coverage ===" && echo "  Lessons Learned:" && wc -l ~/.claude/../.config/claude/references/lessons-learned.md 2>/dev/null | awk '{print "    "$1" lines"}' || echo "    not found" && echo "  Decision Journal:" && grep -c "^### \[" ~/.claude/../.config/claude/references/decision-journal.md 2>/dev/null | awk '{print "    "$1" decisions"}' || echo "    0 decisions"`

上記の情報を確認し、以下を報告すること:
1. MEMORY.md の現在の行数と上限（200行）までの余裕
2. **Dashboard**: type 別メモリ件数、lessons-learned 行数、decision-journal エントリ数
3. **カバレッジ**: 知見が薄い領域（type 件数が 0-1 の分類）
4. **ノイズ検出**: Operational (Tier 1) レベルの内容が混入していないか spot check
5. 整理が必要な場合は具体的な提案
