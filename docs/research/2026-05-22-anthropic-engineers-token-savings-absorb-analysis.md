---
source: "How Anthropic Engineers Actually Save Tokens / I Saved 300 Million Tokens This Week"
date: 2026-05-22
status: integrated
size: S+M (S 部分実装済、M は plans/active/)
author: 不明 (community blog)
citation: Thariq Shihipar (Anthropic) X投稿 https://x.com/trq212/status/2024574133011673516
fetch_route: user-paste
trusted: false
---

## Source Summary

**主張**: Claude Code の prompt cache 機構を理解・活用することで token コストを大幅削減できる。Anthropic エンジニアが実践するキャッシュ戦略（TTL/層/破壊要因の理解）が中心。

**手法 (9)**:

| # | 手法 | 概要 |
|---|------|------|
| T1 | Cache hit rate 監視 | token-dashboard 等でキャッシュ比率を可視化 |
| T2 | TTL=1h pause 回避 | subscription = 1h、API default = 5min の差を認識し中断を避ける |
| T3 | Handoff skill + /clear | /compact より高速なセッション継続手法 |
| T4 | Model switch 破壊回避 | モデル切替で cache 全消去される点を意識 |
| T5 | Sub-agents TTL=5min 対策 | Task tool は常時 5min TTL、subscription でも例外なし |
| T6 | CLAUDE.md edit safe | mid-session 編集は restart まで反映されず → live cache 安全 |
| T7 | claude.ai Projects 活用 | Web UI の Projects でキャッシュ最大化 |
| T8 | 3-layer cache | system / project / conversation の prefix-match 3 層 |
| T9 | token-dashboard 可視化 | https://github.com/nateherkai/token-dashboard |

**根拠**: Thariq Shihipar (Anthropic) の X 投稿。公式 docs: https://code.claude.com/docs/en/prompt-caching

**前提条件**: Claude Code CLI + API subscription 利用者。claude.ai Web UI 向け T7 は CLI スコープ外。

## Phase 1.5 Saturation Gate

同 family 過去記事: HTML Effectiveness (2026-05-09)、Claude Code Large Codebase (2026-05-20) は別ドメイン。**cache mechanism は新分野 → PASS**（saturation 棄却なし）。

## Gap Analysis

### Pass 1: 判定表

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| T1 | Cache hit rate 監視 | Partial | session_observer に cache_read/cache_create 抽出済 (session_observer_parse.py:121-122)。比率算出・閾値警告は未実装 |
| T2 | TTL=1h pause 回避 | Already (強化必須) | references/ に 2h state TTL 記載あり。1h prompt cache TTL との混同回避の明示なし → 誤読リスク大 |
| T3 | Handoff skill + /clear | Already (強化不要) | session-protocol.md の既存 handoff + /clear フローで十分 |
| T4 | Model switch 破壊 | Gap | model-routing.md に cache invalidation boundary の記載なし |
| T5 | Sub-agents TTL=5min | Gap | subagent-delegation-guide.md に subscription vs API のキャッシュ差異の記載なし |
| T6 | CLAUDE.md edit safe | Partial | restart timing（いつ反映されるか）が明示されていない |
| T7 | claude.ai Projects | N/A | CLI スコープ外 |
| T8 | 3-layer cache | Partial | cc-7-layer-memory-model.md に 7 層モデルあり。prompt cache 3 層との対応注記なし |
| T9 | token-dashboard | Partial | session_observer で raw 値取得済。比率レポート・比較警告未実装 |
| NEW1 | MCP/tool deny/upgrade → cache 破壊 | Gap | 記事の欠落。MCP 接続切断・bare tool deny・CC upgrade も system prompt 層を変え cache 無効化 |
| NEW2 | /rewind は cache-safe 代替 | Gap | 記事の欠落。/rewind は /compact より cache を維持しやすい代替として未統合 |

### Pass 2: Already 強化分析

| # | 既存の仕組み | 弱点 | 判定 |
|---|---|---|---|
| T2 | references/ の 2h state TTL 記載 | 1h prompt cache TTL との区別が曖昧 → 誤読で余計な中断が発生 | 強化必須 |
| T3 | session-protocol.md handoff | 弱点なし | 強化不要 |

## Phase 2.5 Refine

### Codex review 統合 (task-mpg0cxic-z5lvrk, 2026-05-21)

- **T9 を Gap → Partial に修正**: session_observer_parse.py:121-122 / session_observer_fmt.py:99-100 に `cache_read` / `cache_create` 抽出済。比率算出と閾値警告が未実装な点が残差
- **T2 を「強化可能」→「強化必須」に格上げ**: 2h state TTL と 1h prompt cache TTL の混同が誤読を生む。明示的な三層 TTL 表が必要
- **NEW1 追加**: MCP 接続/切断、bare tool deny、Claude Code upgrade も system prompt 層を変え cache invalidation を引き起こす — 記事の欠落として識別
- **NEW2 追加**: /rewind は /compact より cache を維持しやすい代替として未統合
- **opusplan bias 指摘**: token cost だけで opusplan を禁止するのは bias。Opus の設計品質メリットを無視している

### Gemini fact-check 結果

| 主張 | 判定 |
|------|------|
| subscription cache TTL = 1h | VERIFIED |
| API default TTL = 5min | VERIFIED |
| cache read cost = 通常 input の 10% | VERIFIED |
| 3-layer cache (system/project/conversation) | VERIFIED |
| model switch で cache 全消去 | VERIFIED |
| CLAUDE.md mid-session edit → cache safe | VERIFIED |
| token-dashboard repo 存在 | VERIFIED |
| sub-agent 5min (subscription でも例外なし) | PARTIALLY VERIFIED (公式に明記あり) |

**Hallucination 注意**: Gemini が出した model ID `claude-3-opus-20240229` は古い (2024 年)。現行は `claude-opus-4-x` 系。

## Integration Decisions

### 採用 (S 規模、実装済)

| # | 項目 | 採用先 | 規模 |
|---|------|--------|------|
| T2 + T6 | TTL 三層表 + CacheSafeParams 注記 | `references/resource-bounds.md` 新規セクション / `cc-7-layer-memory-model.md` 既存行 enhance | S |
| T4 + NEW1 | Model Switch / Cache Invalidation Boundary | `references/model-routing.md` 新セクション | S |
| T5 + NEW2 | Subagent Prompt Cache TTL 注記 + /rewind 追加 | `references/subagent-delegation-guide.md` / `references/session-protocol.md` | S |

### 採用 (M 規模、計画ファイルに保存)

| # | 項目 | 採用先 | 規模 |
|---|------|--------|------|
| T9 | session_observer 拡張 — cache 比率レポート + 閾値警告 | `docs/plans/active/2026-05-22-token-cache-observer-extension.md` | M |

### スキップ

| # | 項目 | 理由 |
|---|------|------|
| T7 | claude.ai Projects | CLI スコープ外 |
| T3 | handoff skill | 既存 session-protocol で十分、強化不要 |
| T1 | Cache hit rate 監視 (独立タスク化) | T9 の M 規模計画に統合済 |

## Implementation Summary

**S 規模 変更ファイル (5)**:

| ファイル | 変更内容 |
|----------|----------|
| `references/resource-bounds.md` | TTL 三層表セクション追加 (subscription 1h / API 5min / subagent 5min) |
| `references/cc-7-layer-memory-model.md` | CacheSafeParams 注記追加 (CLAUDE.md mid-session edit はキャッシュに影響しない) |
| `references/model-routing.md` | Model Switch / Cache Invalidation Boundary セクション追加 |
| `references/subagent-delegation-guide.md` | Subagent Prompt Cache TTL 注記追加 |
| `references/session-protocol.md` | /rewind を cache-safe 代替として追記 |

**M 規模 続行プラン**: `docs/plans/active/2026-05-22-token-cache-observer-extension.md`

## Bias Warnings

- 著者の「opusplan 禁止」スタンスは **token cost bias**。Opus plan の設計品質メリット（複雑タスクでの構造化能力）を無視している。Codex review で指摘済
- Gemini grounding に **古い model ID (claude-3-opus-20240229, 2024年)** の hallucination あり。現行モデル ID で上書き必要
- 記事は引用元 URL なし。Thariq X post (`https://x.com/trq212/status/2024574133011673516`) のみが verifiable な一次ソース
- community blog 著者不明 → `trusted: false` で処理

## References

| リソース | URL / パス |
|----------|-----------|
| 公式 prompt caching docs | https://code.claude.com/docs/en/prompt-caching |
| Thariq X post (一次ソース) | https://x.com/trq212/status/2024574133011673516 |
| token-dashboard | https://github.com/nateherkai/token-dashboard |
| cc-7-layer-memory-model.md | `references/cc-7-layer-memory-model.md` |
| model-routing.md | `references/model-routing.md` |
| session-protocol.md | `references/session-protocol.md` |
| subagent-delegation-guide.md | `references/subagent-delegation-guide.md` |
| resource-bounds.md | `references/resource-bounds.md` |
| session_observer_parse.py | `scripts/runtime/session_observer_parse.py` |
