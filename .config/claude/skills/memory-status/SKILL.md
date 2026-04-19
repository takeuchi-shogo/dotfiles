---
name: memory-status
allowed-tools: Bash(wc *), Bash(ls *), Bash(cat *)
description: >
  Show memory system status and usage summary. メモリファイル数、サイズ、MEMORY.md の行数を表示。
  Triggers: 'memory-status', 'メモリ状態', 'memory usage', 'メモリ確認', 'how much memory'.
  Do NOT use for: コンテキスト使用量（use /check-context）、メモリ内容の検索（直接 Read で十分）。
origin: self
disable-model-invocation: true
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

## Capacity Check

!`echo "=== MEMORY.md Capacity ===" && wc -c ~/.claude/projects/*/memory/MEMORY.md 2>/dev/null | awk '{print "  bytes: "$1" / 25000 (hard limit)"}' && wc -l ~/.claude/projects/*/memory/MEMORY.md 2>/dev/null | awk '{print "  lines: "$1" / 200 (hard limit)"}'`

## Stale Memory Files (30+ days since last update)

!`find ~/.claude/projects/*/memory -name "*.md" ! -name "MEMORY.md" -mtime +30 2>/dev/null | while read f; do echo "  STALE: $(basename "$f") ($(stat -f '%Sm' -t '%Y-%m-%d' "$f" 2>/dev/null || stat -c '%y' "$f" 2>/dev/null | cut -d' ' -f1))"; done || echo "  None"`

## Health Check

以下の基準で評価:

| チェック項目 | 基準 | ステータス |
|------------|------|----------|
| MEMORY.md 行数 | < 180行 (アーカイブ閾値) | 180行超で自動アーカイブ発動 |
| MEMORY.md バイト | < 23KB (25KB上限の92%) | 25KB超でサイレント切り捨て |
| 重複エントリ | 0件 | あれば統合 |
| 古い情報 | なし | あれば更新/削除 |
| 30日以上未更新ファイル | 確認 | 陳腐化の兆候、検証 or 削除 |
| 機密情報 | なし | あれば即削除 |
| 詳細ファイル分離 | 適切 | 長いセクションは分離推奨 |

## Dashboard Statistics

!`echo "=== Memory Type Distribution ===" && for type in user feedback project reference; do count=$(grep -l "type: $type" ~/.claude/projects/*/memory/*.md 2>/dev/null | wc -l | tr -d ' '); echo "  $type: $count files"; done`

!`echo "=== Knowledge Pyramid Coverage ===" && echo "  Lessons Learned:" && wc -l ~/.claude/../.config/claude/references/lessons-learned.md 2>/dev/null | awk '{print "    "$1" lines"}' || echo "    not found" && echo "  Decision Journal:" && grep -c "^### \[" ~/.claude/../.config/claude/references/decision-journal.md 2>/dev/null | awk '{print "    "$1" decisions"}' || echo "    0 decisions"`

上記の情報を確認し、以下を報告すること:
1. **Capacity**: MEMORY.md の行数 (/ 200) とバイト数 (/ 25KB)。180行 or 23KB 超で警告
2. **Staleness**: 30日以上未更新のメモリファイルがあれば一覧と対処提案
3. **Dashboard**: type 別メモリ件数、lessons-learned 行数、decision-journal エントリ数
4. **カバレッジ**: 知見が薄い領域（type 件数が 0-1 の分類）
5. **ノイズ検出**: Operational (Tier 1) レベルの内容が混入していないか spot check
6. 整理が必要な場合は具体的な提案
