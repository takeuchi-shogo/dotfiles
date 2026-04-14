---
source: "3 Things I learnt after 3 weeks of using Hermes as a personal analyst"
date: 2026-04-14
status: completed-partial
author: PE/VC/IB 出身者 (匿名)
source_type: 個人体験ブログ
original_date: 2026-03-23 前後（正確な日付不明）
---

## Source Summary

**主張**: Hermes (Nous Research) のようなセッション跨ぎメモリ付きエージェントは、正しいセットアップ ($5-10/月) で研究・投資・営業の個人アナリストになる。Setup > Model の思想が全て。3 週間の個人運用体験ベース。

**手法**:
1. Session-Spanning Memory with Hindsight Reflection
2. Daily Briefing Automation (マクロ/ポートフォリオ/X bookmarks 毎朝レポート)
3. Model-Task Routing (Kimi k2.5 / GLM 5.1 / MiniMax 2.7 の使い分け)
4. Multi-Source Information Ingestion (Last30days: Reddit/X/YouTube/GitHub)
5. MCP/API Integration → Auto Skill Creation
6. Browser Use Built-in (YouTube transcript + form filling)
7. Discord as UI Layer (結果受取 + feedback loop)
8. Setup-First Philosophy (Setup > Model)
9. Operator-Aware Continuous Learning
10. Cost-Optimized Multi-Agent System ($5-10/月)

**根拠**: 著者自身の 3 週間の個人運用体験。PE/VC/IB バックグラウンドからのリサーチ・投資ユースケース中心。

**前提条件**: 個人ユーザーが月$5-10 程度のコストで AI アナリストを構築したいケース。Hermes エージェント (hermes-agent.nousresearch.com) を使用。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Session-Spanning Memory with Hindsight Reflection | Already | analyze-tacit-knowledge + recall + continuous-learning + AutoEvolve 03:00 cron で完備 |
| 2 | Daily Briefing Automation | Already (強化可能) | auto-morning-briefing.sh が cron + claude -p + Obsidian + cmux notify で既に稼働。情報源拡張が強化余地 |
| 3 | Model-Task Routing | Already | Sonnet/Haiku/Opus/Codex/Gemini/Cursor/Managed Agents の6系統完備 |
| 4 | Multi-Source Information Ingestion | N/A | research + absorb + morning-briefing で on-demand 十分 |
| 5 | MCP → Auto Skill Creation | Gap (小) | skill-creator は手動。新規 MCP 接続時の自動トリガーなし |
| 6 | Browser Use Built-in | Already | webapp-testing + playwright + defuddle + digest で対応済み |
| 7 | Discord as UI Layer | N/A | cmux notify で十分。Discord bot は不要 |
| 8 | Setup-First Philosophy | Already | CLAUDE.md に "Scaffolding > Model: 44% vs 14%" として完全一致。Scaffolding over Scaling 論文で academic 裏付け |
| 9 | Operator-Aware Continuous Learning | Already | AutoEvolve 4 層 + profile-drip 完備 |
| 10 | Cost-Optimized Multi-Agent System | Already (強化可能・小) | Codex 3-4x 削減 + ハード予算キャップ完備。月次ダッシュボードが未整備 |

**集計**: Already 強化不要 5 / Already 強化可能 2 / Gap 小 1 / N/A 2

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 (#2) | auto-morning-briefing.sh (cron + claude -p + Obsidian + cmux notify) | 情報源が固定 (マクロ/ポートフォリオ中心)。Hacker News / arXiv 等の技術情報源が未収録 | Hacker News Top 10 (無認証 API) + arXiv cs.AI 新着 + Optional RSS (OBSIDIAN_RSS_FEEDS env) を追加。既存 context 変数への append で非干渉 | 採用 |
| S2 (#10) | Codex 3-4x コスト削減 + ハード予算キャップ | 月次トレンドが可視化されていない。CLI usage log が不在 | 月次コスト tracking ダッシュボード。feasibility spike のみ実施 | 採用 (spike のみ) |

## Phase 2.5 補正メモ

- **#2 の N/A → Already 強化可能 への補正**: Codex search 中に `.config/claude/scripts/runtime/auto-morning-briefing.sh` を発見 (cron + claude -p + Obsidian + cmux notify で既に稼働)。構造的に記事のユースケースと同型。これが採用判定の決定打
- **#8 の追加裏付け**: Gemini が "Scaffolding over Scaling" 論文 (2025末発表) で「ハーネス効果 25%+ vs モデル性能向上 3-5%」を検証。CLAUDE.md の "44% vs 14%" 主張を academic に補強
- **Codex サブエージェントの状態**: タイムアウト (Stream idle)、最終 assistant message 未書き出し。ただし search footprint から auto-morning-briefing.sh を発見し、これが #2 判定補正の決定打となった。部分的貢献は価値があった

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | MCP → Auto Skill Creation (#5) | 採用 | 自動生成はしない (skill 品質担保)。新規 MCP server 検知時に stderr でヒント通知する軽量フックで実現 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | morning-briefing 情報源拡張 (#2) | 採用 | HN/arXiv/RSS 追加で技術情報カバレッジが向上。既存スクリプト非干渉で低リスク |
| S2 | 月次コストダッシュボード (#10) | 採用 (spike のみ) | CLI usage log 不在。計測対象の洗い出しと料金テーブル管理方針を spike で確認。本格実装は別 plan |

## Plan

### Task 1: morning-briefing 情報源拡張【S】
- **Files**: `.config/claude/scripts/runtime/auto-morning-briefing.sh`
- **Changes**: Hacker News Top 10 (無認証 HN API `https://hacker-news.firebaseio.com/v0/topstories.json`) + arXiv cs.AI 最新5件 + Optional RSS (OBSIDIAN_RSS_FEEDS 環境変数) を既存の context 変数に append
- **Size**: S

### Task 2: 月次コスト tracking【feasibility spike のみ】
- **Files**: 新規 `docs/plans/cost-tracking-spike.md`
- **Changes**: 計測対象の洗い出し (Claude API usage, Codex token log, Gemini API log)、料金テーブル管理方針、集約方針の文書化
- **Size**: L → このセッションは spike ドキュメントのみ
- **Note**: `~/.codex/usage*` なし、`~/.gemini/` に log なし、`~/.claude/statsig/` はキャッシュのみ、と確認済み。本格実装は `/spike` or `/epd` で別途

### Task 3: MCP → Skill ヒント通知【S】
- **Files**: 新規 `.config/claude/scripts/hooks/mcp-skill-hint.py`、`settings.json` (hooks セクション)
- **Changes**: PostToolUse hook で `.claude.json` 編集を検知。新規 MCP server があれば stderr に skill-creator 起動提案を出力。自動生成はしない (skill 品質担保)
- **Size**: S

## 周辺知識 (Gemini 補完)

- **Hermes Agent**: Nous Research の実製品 (hermes-agent.nousresearch.com)。Hindsight は "self-reflection + ベクトル DB 要約保存 + 動的注入" の仕組み
- **エージェント memory 層 SOTA**: Letta (旧 MemGPT) が企業導入で先行。mem0 / Cognee / LangChain Memory が追従。Anthropic Memory Tool v2 + Letta ADR-Memory がハイブリッド方向
- **Scaffolding over Scaling 論文** (2025末): ハーネス効果 25%+ vs モデル性能向上 3-5%。CLAUDE.md の "44% vs 14%" 主張を academic に補強
- **Kimi k2.5**: 長文処理は LMSYS で検証済み。**MiniMax 2.7**: 公式ベンチマーク乏しく裏付け薄い

## Handoff

同一セッションで Task 1 (#2 情報源拡張) + Task 3 (#5 MCP ヒント通知) + Task 2 spike を実行。

## Implementation Summary (2026-04-14 セッション内実行)

Task #1 と #3 をこのセッションで実装、Task #2 は spike のみ実行:

### Task #1: auto-morning-briefing.sh 情報源拡張 ✅ 完了
- ファイル: `.config/claude/scripts/runtime/auto-morning-briefing.sh`
- 追加内容:
  - Hacker News Top 5 取得 (`https://hacker-news.firebaseio.com/v0/topstories.json`)
  - arXiv cs.AI 新着 5件 (`http://export.arxiv.org/api/query?search_query=cat:cs.AI`)
  - Optional RSS (`MORNING_BRIEFING_RSS_FEEDS` env var、改行区切り URL)
- 各ソースは network 失敗時もブリーフィング全体を止めない設計 (`--max-time` + `|| true` + 条件付き append)
- Syntax check: PASS
- 既存機能への影響: なし（context 変数への append パターン、既存ロジック非干渉）

### Task #3: MCP → Skill Hint Hook ✅ 完了
- 新規ファイル: `.config/claude/scripts/policy/mcp-skill-hint.py`
- 新規登録: `.config/claude/settings.json` PostToolUse (`Edit|Write` matcher) に追加
- 動作: `.claude.json` / `.mcp.json` / `mcp.json` 編集時、追加内容に `mcpServers` または `"command"` キーワードが含まれる場合 `/skill-creator` 起動を提案するヒントを additionalContext で出力
- 自動生成はしない（skill 品質担保）
- Smoke test: positive case (mcpServers + command)、negative case (非MCP file、関連キーワードなし) 両方 PASS
- Ruff lint: PASS

### Task #2: 月次コストダッシュボード Spike ⚠️ Feasible but deferred

**Spike 調査結果 (2026-04-14)**:

| Source | Data Location | Fields | 可否 |
|--------|--------------|--------|------|
| Claude Code | `~/.claude/projects/*/*.jsonl` の `message.usage` per-message | `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `service_tier`, `cache_creation.ephemeral_1h_input_tokens`, `iterations[]` | ✅ 詳細 |
| Codex CLI | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` の `event_msg.payload.type = "token_count"` | `total_token_usage.{input,cached_input,output,reasoning_output,total}_tokens`, `rate_limits.{primary,secondary}.{used_percent,resets_at}`, `credits.has_credits` | ✅ 詳細（レート制限まで） |
| Gemini CLI | `~/.gemini/state.json`, `~/.gemini/history/` | `tipsShown` のみ、history は project root markers | ❌ **blind** (手動入力 or 別途 wrapper が必要) |

**Feasibility Verdict**: Claude + Codex は完全に可能（価値ベースで約90%のコンピュートをカバー）。Gemini は CLI 側で usage 永続化されていないため、手動入力または wrapper script が別途必要。

**実装スコープ（別セッションで /spec or /epd 推奨）**:
1. `references/pricing-table.yaml` — model × token type → USD 単価、`effective_from` 付き
2. `scripts/runtime/aggregate-daily-cost.py` — Claude/Codex JSONL を指定日で集計し `~/.claude/cost-daily/YYYY-MM-DD.json` に書き出し
3. `scripts/runtime/monthly-cost-report.py` — 日次データを月次にロールアップ → markdown レポート生成
4. `scripts/runtime/com.claude.monthly-cost.plist` — launchd trigger（月初 1 日 08:00 等）
5. Optional: Gemini wrapper or 月末手動入力プロンプト

**推定実装コスト**: 2-3日（pricing table の運用方針決定を含む）

**Gotchas**:
1. 価格改定による drift → dated pricing table
2. Max プランのユーザーは「on-demand equivalent cost」として推定値を出す
3. cache read savings は別メトリクスとして報告価値高い
4. subagent 呼び出しは別 sessionId → 集計に含める
5. 料金テーブルは半年-1年毎に監査が必要

## 後続アクション

- **Task #2** の本格実装は `/spec` で要件を固めてから `/epd` で進めることを推奨
- `MORNING_BRIEFING_RSS_FEEDS` env var の実際の使い方例を `references/` に追加するか、cron 起動スクリプトのドキュメントに記載することを検討
- mcp-skill-hint の false positive 率は運用で様子見（初期は控えめに発火するはず）
