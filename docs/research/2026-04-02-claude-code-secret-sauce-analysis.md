---
source: "Claude Code's Real Secret Sauce (Probably) Isn't the Model (blog post, 2026-04-02)"
date: 2026-04-02
status: skipped
---

## Source Summary

**主張**: Claude Code の性能はモデルではなくソフトウェアハーネス（プロンプトキャッシュ、専用ツール、コンテキスト管理、サブエージェント）に起因する。

**手法** (6つ):
1. Live Repo Context — git branch/commits/CLAUDE.md をセッション開始時にロード
2. Prompt Cache Reuse — 静的/動的コンテンツの境界マーカーでキャッシュ再利用
3. Dedicated Tools — Grep/Glob/LSP 専用ツール（bash経由より優秀）
4. Context Bloat Minimization — ファイル読み取り重複排除、大結果のディスク退避、autocompaction
5. Structured Session Memory — セッション状態をセクション分けした構造化 markdown で保持
6. Fork & Subagents — 親キャッシュ再利用 + mutable state 認識の並列エージェント

**根拠**: リークされたソースコード観察。定量データなし。

## Gap Analysis

全6項目が Already (強化不要)。

| # | 手法 | 判定 | 既存の仕組み |
|---|------|------|-------------|
| 1 | Live Repo Context | Already | `env-bootstrap.py` (SessionStart) |
| 2 | Prompt Cache Reuse | Already | `compact-instructions.md` キャッシュ安定性ルール |
| 3 | Dedicated Tools | Already | CLAUDE.md + system prompt 指示 |
| 4 | Context Bloat Minimization | Already | `output-offload.py` + `suggest-compact.js` + `pre-compact-save.js` |
| 5 | Structured Session Memory | Already | `session-trace-store.py` + MEMORY.md + 圧縮時保持優先度 |
| 6 | Fork & Subagents | Already | `subagent-delegation-guide.md` + worktree 隔離 + Sequential プロトコル |

## Integration Decisions

スキップ。本記事は 2026-04-01 の内部アーキテクチャ分析（実ソースコードベース）のライト版サマリーであり、
新規の手法・知見・定量データを含まない。「Scaffolding > Model」原則は CLAUDE.md に定量根拠付きで既に明記済み。
