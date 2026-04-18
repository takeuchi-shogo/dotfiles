---
name: check-context
allowed-tools: Bash(wc *), Bash(cat *), Bash(ls *)
description: >
  Check current context window usage and session state.
  Triggers: 'check-context', 'コンテキスト確認', 'context usage', '残りコンテキスト', 'how much context'.
  Do NOT use for: メモリ状態確認（use /memory-status）、セッション分析（use /analyze-tacit-knowledge）。
origin: self
disable-model-invocation: true
---

# Check Context

コンテキストウィンドウの使用状況とセッション状態を確認する。

## Context Pressure（実使用率、主指標）

!`cat ~/.claude/session-state/context-pressure.json 2>/dev/null || echo '{"used_pct": 0, "note": "no pressure data — statusline hook not yet run"}'`

> `used_pct` は `context-monitor.py` が Claude Code から直接取得した実使用率。1M context 基準。

## Session State

!`cat ~/.claude/session-state/last-session.json 2>/dev/null || echo '{"status": "no saved session"}'`

## Edit Counter（補助指標）

!`cat ~/.claude/session-state/edit-counter.json 2>/dev/null || echo '{"count": 0, "note": "no counter"}'`

## Compaction Counter

!`cat ~/.claude/session-state/compaction-counter.json 2>/dev/null || echo '{"count": 0}'`

## Action Guidelines（タスク複雑度を考慮）

> 出典: Anthropic "Session Management & 1M Context" (2026-04) + NVIDIA RULER。
> 有効帯域はタスク依存。単純抽出は ~1M、multi-hop 推論は ~300-400k で劣化。

### 主指標: `used_pct`（実使用率）

| used_pct | Multi-hop タスク（debug, refactor, 設計判断） | 単純タスク（抽出, 要約） |
|----------|----------------------------------------------|--------------------------|
| < 30% | 通常運用 | 通常運用 |
| 30-40% | 複雑判断は継続可だが large Read/Grep を避ける | 通常運用 |
| **40-50%**（≈ 300-400k）| **劣化ゾーン突入** — Subagent 委譲で隔離、`/compact {focus}` を検討 | 継続可、ただし並列起動は抑制 |
| 50-70% | multi-hop なら新セッション推奨、`/clear` + brief | `/compact` で軽量化 |
| 70-85% | **Danger**: 新規並列停止、`/checkpoint` + 新セッション | Subagent 委譲必須 |
| > 85% | **Hard Stop**: 即 `/clear` or `/checkpoint` → 新セッション | 即圧縮 |

### 補助指標: Edit 数 / Compaction 回数

`used_pct` が取得できない場合の fallback。

| Edit 数 | 備考 |
|---------|------|
| < 20 | 通常運用 |
| 20-30 | 大きな調査は Subagent 委譲 |
| 30-50 | `/compact {focus}` 推奨 |
| > 50 | 新セッション強く推奨 |

| Compaction 回数 | 備考 |
|-----------------|------|
| 0-2 | 通常（各回で品質劣化を観察） |
| 3+ | **Reset > Compaction** 原則。即 `/clear` |

### 判断の流れ

1. **現タスクは multi-hop か？** (デバッグ、設計判断、横断 refactor なら Yes)
2. Yes かつ `used_pct ≥ 40%` → **劣化ゾーン**。次ターン前に `/compact {focus}` または `/clear` を検討
3. 判断フローの詳細: `references/workflow-guide.md § Every Turn Is a Branching Point`
4. Compact vs Clear の選択: `references/session-protocol.md § Compact vs Clear Decision Matrix`

上記の情報を簡潔にまとめて報告すること。`used_pct` が取れていれば主指標として使い、Edit 数は補助としてのみ言及する。
