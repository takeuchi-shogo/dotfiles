---
source: "https://claude.com/blog/using-claude-code-session-management-and-1m-context"
date: 2026-04-17
status: analyzed
tags:
  - ingest
  - topic/session-management
  - topic/context-management
  - source/anthropic-blog
---

# Using Claude Code: Session Management & 1M Context 分析レポート

**日付**: 2026-04-17
**ソース**: "Using Claude Code: Session Management & 1M Context" — Anthropic Applied AI team
**URL**: https://claude.com/blog/using-claude-code-session-management-and-1m-context
**分析対象**: 個人 Claude Code dotfiles ハーネス (/Users/takeuchishougo/dotfiles)
**フェーズ**: Extract → Analyze (Sonnet Explore) → Refine (Codex + Gemini 並列批評) → Triage → Plan

---

## Executive Summary

Anthropic 公式ブログが 1M context window 時代のセッション管理プラクティスを体系化した記事。核心は「1M context は autonomous 操作を延長できるが、context pollution（300-400k 付近で劣化）に対して能動的に管理しなければならない」という点。Every turn is a branching point として Continue / /rewind / /clear / /compact / Subagent の5択を毎ターン意識することが主な処方箋。

dotfiles 現状との照合では、compaction/checkpoint の基盤は既存だが、Rewind プラクティスと毎ターンの branching 意識儀式が完全に欠落していることが主要 Gap。既存 Already 項目も concrete heuristic の明文化が不足している。

取り込み決定: Gap 全3件 + Already 強化 全4件 = 計 6 ファイル変更 (M 規模)。

---

## Phase 1: 記事要点 (Extract)

### 中核主張

1M context window は autonomous 操作を長くできるが、context pollution リスクがある。Context rot は ~300-400k tokens、タスク依存。Every turn is a branching point として Continue / /rewind / /clear / /compact / Subagent の5択を意識することが重要。Rule of thumb: new task = new session。

### 6 手法

| # | 手法 | 概要 |
|---|------|------|
| 1 | Context Rot Management | 300-400k でパフォーマンス劣化、task-dependent |
| 2 | Rewinding Instead of Correcting | `/rewind` で clean point から再プロンプト |
| 3 | Proactive Compaction with Steering | `/compact {focus-instruction}` 早期発動 |
| 4 | Clear Session Strategy | `/clear` で明示的 distilled brief |
| 5 | Task-Scoped Sessions | new task = new session (rule of thumb、grey area 含む) |
| 6 | Subagent Delegation for Output Reduction | mental test: "will I need this output again, or just the conclusion?" |

### 根拠

- Context rot 300-400k (task-dependent)
- Autocompact は model intelligence low point で発動
- Rewind は iterative correction より clean
- Subagent は intermediate output を隔離

### 前提条件

1M context window 環境、session management コマンド (/rewind, /compact, /clear) の理解

---

## Phase 2: ギャップ分析 (修正後)

### Gap / Partial 項目

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 2 | Rewinding Instead of Correcting | **Gap** | /rewind 活用プラクティス不在。HANDOFF.md Dead Ends は次セッション用で、今セッションの汚染コンテキスト除去とは効用が違う |
| 5 | Task-Scoped Sessions (grey area) | **Partial** | 「1セッション1機能」は L 限定で妥当。欠けているのは grey area（実装→ドキュメント等）の判定例 |
| 7 | Every Turn Is a Branching Point | **Gap (Codex 追加)** | workflow-guide.md に Continue/Spawn 判断はあるが、毎ターンに /rewind /clear /compact Subagent を含む5択選択儀式が無い |

### Already 項目 (強化候補)

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Context Rot Management | **Already (強化可能)** | check-context (Edit数) + context-constitution.md 存在。「300-400k 目安、タスク複雑度依存」の具体数値が未記載 |
| 3 | Proactive Compaction with Steering | **Already (強化可能)** | pre-compact-save.js + compact-instructions.md 存在。Steering 方向付け例が不足 |
| 4 | Clear Session Strategy | **Already (強化可能)** | /checkpoint + HANDOFF.md / RUNNING_BRIEF.md 存在。Compact vs Clear の判断マトリクスが無い |
| 6 | Subagent Delegation for Output Reduction | **Already (強化可能)** | subagent-delegation-guide.md + output-offload.py 存在。"output again or conclusion?" heuristic が明文化されていない |

---

## Phase 2.5: Refine (Codex + Gemini 批評)

### Codex の指摘サマリ

1. **見落とし**: 「毎ターン branching point」のメタ思考が workflow-guide.md に無い → Gap #7 追加
2. **Gap #2 は妥当**: HANDOFF.md Dead Ends と Rewind は効用が違う。Dead Ends は「次セッションへの引き継ぎ」、Rewind は「今セッション内の汚染除去」
3. **過小評価**: 手法 6 は "output again or conclusion?" heuristic が明文化不足 → Already 強化に格上げ
4. **M/S への拡張は過剰制約**: grey area の判定例追加で十分（Task-Scoped Sessions の Partial は維持）
5. **優先度トップ**: Rewind を session decision table に追加、Subagent 1行 heuristic 追加

### Gemini 周辺知識サマリ

- **300-400k 根拠**: NVIDIA RULER (arxiv.org/abs/2404.06654) で multi-hop 推論は 300-500k で指数的劣化、NIAH は 1M まで対応
- **Rewind の隠れコスト**: prompt cache 全無効化、tool 副作用との乖離（副作用がある操作後の rewind はリスクあり）
- **/compact セマンティックドリフト**: arxiv.org/abs/2406.01544 — compact 後に重要コンテキストが失われうる実証
- **新潮流**: Letta/MemGPT 階層型メモリ、Voyager skill library、マルチエージェント分離
- **他ツール比較**: Cursor (.cursorrules + RAG)、Aider (Repo-map)、Cline (MCP checkpoint) — いずれも context management を仕組みで解決

---

## Phase 3: ユーザー選択 (Triage)

### 取り込み決定

- **Gap 全件取り込み**: #2 Rewind + #5 grey area + #7 Turn Decision Table
- **Already 強化 全件取り込み**: #1 (context-constitution) + #3 (compact-instructions) + #4 (session-protocol) + #6 (subagent-delegation-guide)

### スキップ

- N/A なし（全手法が1M context window 環境の dotfiles に適用可能）

---

## Phase 4: 統合プラン (M 規模、6 ファイル)

| # | ファイル | 変更種別 | 変更内容 |
|---|---------|---------|---------|
| T1 | `.config/claude/references/workflow-guide.md` | 追記 | **Turn Decision Table** 追加。毎ターンに考慮する5択（Continue / /rewind / /clear / /compact w/ steering / Subagent）+ Rewind 使用条件・隠れコスト（cache 無効化、副作用乖離）を併記 |
| T2 | `.config/claude/references/workflow-guide.md` | 追記 | **Grey Area 判定例** 追加。実装→docs（同タスク = Continue）、実装→test（同タスク = Continue）、debug→関連 warning（境界 = /compact で圧縮後 Continue）、debug→別機能 bug（別タスク = new session）の4例 |
| T3 | `.config/claude/references/session-protocol.md` | 追記 | **Compact vs Clear Decision Matrix** 追加。方向継続 + context 膨張 → `/compact w/ steering`、方向転換 or context rot 検出 → `/clear` + distilled brief、完全 clean start → new session |
| T4 | `.config/claude/references/compact-instructions.md` | 追記 | **Steering Compact セクション** 追加。`/compact {focus-instruction}` の書式例（例: `/compact Focus on the authentication refactor. Drop unrelated debug output.`）+ 方向転換時に必須という heuristic |
| T5 | `.config/claude/references/subagent-delegation-guide.md` | 先頭追記 | **Mental Test Heuristic** 1行を冒頭に追加: `"Will I need this output again, or just the conclusion? → just the conclusion = delegate to subagent"` |
| T6 | `.config/claude/references/context-constitution.md` | 追記 | **300-400k Threshold** を P8 付近に追記。「RULER 実証: multi-hop 推論は 300-500k で指数的劣化、NIAH は 1M 対応。simple retrieval は上限まで使用可、multi-hop reasoning は 300k を目安に compaction 検討」 |

**依存関係**: T1-T6 独立、並列実行可能

**実装予定の具体例**:

T1 Turn Decision Table イメージ:
```markdown
## Every Turn: Branching Point Checklist

各ターンに5択から判断する:
| 状況 | アクション |
|------|-----------|
| タスク継続、context 健全 | Continue |
| 直前の応答が方向を誤った | /rewind（注意: prompt cache 無効化、tool 副作用との乖離に注意） |
| 300-400k 超過、方向転換 | /clear + distilled brief |
| 300-400k 超過、方向継続 | /compact {focus-instruction} |
| 中間出力が大量、結論だけ必要 | Subagent に委譲 |
```

T6 context-constitution.md 追記イメージ:
```markdown
### P8: Context Size Threshold (実証値)

- NIAH (Needle-in-a-Haystack): 1M tokens まで対応（単純検索）
- Multi-hop 推論: 300-500k で指数的劣化 (NVIDIA RULER, arxiv.org/abs/2404.06654)
- 目安: 300-400k を超えたら task complexity に応じて /compact または /clear を検討
```

---

## 関連項目 (_index.md への追記候補)

```markdown
| 2026-04-17 | Using Claude Code: Session Management & 1M Context | https://claude.com/blog/using-claude-code-session-management-and-1m-context | integrated | session-mgmt, context-rot, rewind, compact, subagent | T1-T6 workflow-guide/session-protocol/compact-instructions/subagent-delegation-guide/context-constitution に統合 |
```

---

## 参考文献

- NVIDIA RULER benchmark: arxiv.org/abs/2404.06654 (multi-hop 推論の context 長依存性)
- Compact セマンティックドリフト: arxiv.org/abs/2406.01544
- 関連既存ファイル:
  - `.config/claude/references/workflow-guide.md`
  - `.config/claude/references/session-protocol.md`
  - `.config/claude/references/compact-instructions.md`
  - `.config/claude/references/subagent-delegation-guide.md`
  - `.config/claude/references/context-constitution.md`
  - `scripts/lifecycle/pre-compact-save.js`
  - `scripts/policy/output-offload.py`
