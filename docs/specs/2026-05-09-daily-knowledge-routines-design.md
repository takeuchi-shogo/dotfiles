# Daily Knowledge Routines — Design Spec

> **Date**: 2026-05-09
> **Status**: Design (brainstorming → spec、plan 待ち)
> **Author**: takeuchishougo
> **Scope**: M-L (新規 6 ファイル + 既存 1 改修、検証期間 30 日)
> **Related**: [docs/guides/2026-05-09-claude-cowork-equivalents.md](../guides/2026-05-09-claude-cowork-equivalents.md)

## Background

Khairallah の "Claude Cowork" 記事 (マーケ系) が主張する 3 セッション (Morning Briefing / Midday Production / End-of-Day Wrap-up) + Knowledge Pipeline ワークフローを、本環境の既存 Anthropic 公式機能 (Skills + `/schedule` + MCP) で実装する。

「Claude Cowork」という Anthropic 公式製品は **存在しない**。ブランディング上の用語にすぎない。本 spec は記事の主張する用途 (情報収集 / 知見の蓄え / 改善ループ) のうち、本環境で **未実装** の 4 項目を埋める。

### 200-Session 集計データ (実証根拠)

`docs/research/2026-05-09-skill-usage-tally.md` 参照:

- `/absorb` 93 回 (80% セッションで使用) — Knowledge Pipeline は既に動作中
- `/commit` 94 回、`/rpi` 22 回 — 改善ループ既に運用中
- `auto-morning-briefing.sh` cron 08:30 — Morning Briefing 既に動作中
- `daily_enforcer.lua` 18:00 通知 — End-of-Day リマインド既に動作中

つまり 80% は既に動いている。本 spec は残り 20% (Email tier 分類 / End-of-Day 自動レポート / RSS 監視 / `/schedule` 活用) を埋めるもの。

## Goals

1. **情報収集の自動化**: Zenn / dev.to / blog の RSS を 30 分間隔で fetch、`knowledge_queue.jsonl` に dedup 追加。朝の Daily Note で消化候補を提示。
2. **Email Tier 分類**: Gmail MCP で取得した未読メールを T1 (今すぐ) / T2 (今日) / T3 (今週) / T4 (informational) に分類。
3. **End-of-Day 自動レポート**: 17:00 に `/schedule` 経由で Claude routine 起動、git activity / calendar / morning priorities 進捗 / queue 消化を Daily Note の `## End-of-Day` セクションに追記。
4. **`/schedule` の活用**: 1 routine (End-of-Day) で `/schedule` skill の運用パターンを確立。
5. **Pruning-First の維持**: 新規 skill 追加ゼロ、既存 skill (`/absorb` / `/digest` / `/timekeeper`) の運用を補強する形に留める。

## Non-Goals

- ❌ **Production Block タスクテンプレート skill 化**: 200 session 集計で「PR 要約 1 回 / PDF 抽出 0 回 / リサーチ集約 0 回 / 影響範囲 0 回 / Issue triage 0 回」と判明、speculative skill 量産は token tax 悪化のため棄却。
- ❌ **Full automation (人介在なし)**: Claude が自動推論で Q7-Q8 信念変化を埋めると質低下 (Sycophancy バイアス) のため棄却。
- ❌ **新規 Cloud Agent 利用**: Claude Code subscription 内 (`claude -p`) で完結、ANTHROPIC_API_KEY 不要。
- ❌ **マーケ記事の主張 (5-15 時間/週節約) の検証**: 影響者ブランディングは無視、本環境固有の用途のみ追求。

## Architecture

3 層構造 (機械的処理 / 賢い判断 / 起動ハーネス)。

```
[起動層]                      [処理層]                              [出力層]
  cron 06:30  ──> rss_watcher.py ──> knowledge_queue.jsonl
                  (Zenn/dev.to RSS, dedup, append-only)

  cron 07:00  ──> auto-morning-briefing.sh ──> Daily Note (07-Daily/YYYY-MM-DD.md)
                  (既存拡張 + queue 集計)            "## Morning Briefing"
                  │
                  ├─> Gmail MCP → unread emails
                  ├─> tier_classifier.py (rule-based, keyword)
                  │     └─ ambiguous fallback → claude -p (1 call/day max)
                  ├─> read knowledge_queue.jsonl (status=pending, top 10)
                  └─> read carry_forward.jsonl (date=yesterday)

  cron 16:55  ──> eod_collector.py ──> /tmp/eod_context_YYYY-MM-DD.json
                  (git / calendar / priorities / queue diff 集計)

  /schedule 17:00 ──> Claude routine ──> Daily Note 追記
                       (集計済み JSON を context として渡す)        "## End-of-Day"
                       └─> append carry_forward.jsonl

  Hammerspoon 18:00 ──> daily_enforcer.lua (既存: リマインダー、文言更新のみ)
                                                          │
                                                          ▼
  人間 (manual)   ──> /timekeeper review or /digest <url>  Daily Note 仕上げ
```

### 設計原則の対応

- **契約層 strict / 実装層 regenerable**: JSONL schema 固定、shell/Python は再生成可能
- **Static-checkable は mechanism**: RSS dedup / git diff 集計はコード、tier 分類は claude -p (機械化困難な判断のみ)
- **Build to Delete**: 各層独立、不要になれば 1 ファイル削除で消せる
- **`Humans steer, agents execute`**: 賢い判断を人と claude -p に分担、機械的処理は shell/Python

## Components

### 1. `scripts/runtime/rss_watcher.py` (新規)

- **責務**: 設定された RSS feed を fetch → dedup → queue 追記
- **入力**: `references/knowledge-sources.yaml` (新規、feed URL リスト)
- **出力**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/knowledge_queue.jsonl` (append-only)
- **依存**: Python stdlib (`urllib.request`, `xml.etree`) を第一候補。stdlib で Atom/RSS 2.0 両対応が困難な場合のみ Plan 段階の spike で `feedparser` 採用判定。
- **起動**: cron `*/30 6-22 * * *` (営業時間帯の 30 分間隔、夜間は静止)
- **dedup key**: URL の SHA-256 を `seen_urls.txt` に保持
- **rotation**: queue が 10MB 超 + status=digested の 30 日経過行を `<file>.archive` に移動
- **dry-run**: `--dry-run` で stdout 出力、queue 書き込みなし

### 2. `scripts/runtime/auto-morning-briefing.sh` (改修)

- **既存責務**: Daily Note 生成 (Cyril absorb 由来)
- **追加責務**: 以下 3 セクションを Daily Note に挿入
  - `### Email Tier (T1-T4)` — Gmail MCP で取得 → tier_classifier.py で分類
  - `### Knowledge Queue` — `knowledge_queue.jsonl` の status=pending を **fetched_at 降順** で上位 10 件をタイトル+URL で表示 (新着優先)
  - `### Carry Forward (from yesterday)` — 前日の `carry_forward.jsonl` を表示
- **起動**: cron 07:00 (既存 08:30 から変更、End-of-Day と分離)
- **fail-soft**: Gmail MCP 認証切れでも他セクションは出力、警告表示

### 3. `scripts/runtime/tier_classifier.py` (新規)

- **責務**: Email subject + sender + snippet を入力に T1-T4 分類
- **入力**: `[{subject, sender, snippet}, ...]` (JSON、stdin)
- **出力**: `{T1: [...], T2: [...], T3: [...], T4: [...]}` (JSON、stdout)
- **方式**:
  - Step 1: rule-based (keyword matching、`URGENT`/`ACTION REQUIRED`/`reminder` 等)
  - Step 2: ambiguous な件 (rule で判定不能) のみ → `claude -p` で fallback (1 call/day max)
- **設定**: `references/email-tier-rules.yaml` (新規、keyword リスト)

### 4. `scripts/runtime/eod_collector.py` (新規)

- **責務**: End-of-Day routine が読む context を集計
- **出力**: `/tmp/eod_context_YYYY-MM-DD.json`
  - `git_activity`: { commits: [...], files_changed: [...], branch }
  - `calendar_events`: 当日 occurred (gcalcli or Calendar MCP)
  - `priorities_status`: Daily Note の Top 3 Priorities を grep → done/pending 判定
  - `queue_diff`: `digested_today: int`, `pending_yesterday: int`, `pending_now: int`
- **起動**: cron 16:55 (routine 起動 5 分前)
- **dry-run**: `--dry-run` で stdout

### 5. `references/eod-routine-prompt.md` (新規)

- `/schedule` で 17:00 に起動する Claude routine の system prompt
- 入力: `/tmp/eod_context_YYYY-MM-DD.json`
- 出力:
  - Daily Note `## End-of-Day` セクションに追記 (機械集計 + 軽い文章化)
  - `carry_forward.jsonl` に未完了項目を append
- **idempotent**: 既存 `## End-of-Day` ヘッダーを検出したら `## End-of-Day (re-run HH:MM)` で append
- **短時間完了**: 1 routine ≒ 30 秒、claude -p 1 call 程度

### 6. JSONL Schemas

```jsonl
# memory/knowledge_queue.jsonl (append-only)
{"id":"sha256-of-url","url":"https://zenn.dev/...","title":"...","source":"zenn:claude","fetched_at":"2026-05-09T07:30:00Z","status":"pending","digested_at":null}
{"id":"sha256-of-url","url":"...","title":"...","source":"...","fetched_at":"...","status":"digested","digested_at":"2026-05-09T08:15:00Z"}

# memory/carry_forward.jsonl (append-only)
{"date":"2026-05-09","item":"X を実装","reason":"Codex review pending","priority":"P1","carried_from":"2026-05-08"}
```

### 7. Hammerspoon (変更最小)

- 既存 `daily_enforcer.lua` 18:00 リマインダーは維持
- 通知文言だけ更新: 「End-of-Day 自動レポート挿入済み、`/timekeeper review` で仕上げて」

## Data Flow

`Architecture` 図参照。時系列:

- **06:30** — `rss_watcher.py` cron
- **07:00** — `auto-morning-briefing.sh` cron → Daily Note `## Morning Briefing`
- **07:30 user** — Daily Note 確認、`/digest <url>` で queue 消化
- **08-17 通常作業** — `/absorb` `/commit` `/rpi` 等の手動運用
- **16:55** — `eod_collector.py` cron → `/tmp/eod_context_*.json`
- **17:00** — `/schedule` routine → Daily Note `## End-of-Day`
- **18:00** — `daily_enforcer.lua` Hammerspoon 通知
- **18:30 user** — `/timekeeper review` で対話的仕上げ

## Error Handling

| 失敗箇所 | 検出 | 対処 |
|---|---|---|
| RSS fetch 失敗 | try/except、log WARN | skip、3 連続で notify |
| Gmail MCP 認証切れ | HTTP 401 | Daily Note に警告、briefing は他セクション出力 |
| `claude -p` 失敗 | exit code !=0 | rule-based fallback、未分類は明示 |
| `/schedule` routine 失敗 | 完了通知なし | 18:00 通知文言を「未挿入、手動 /timekeeper」に変更 |
| `eod_collector.py` 失敗 | 各 collector 独立 | 部分的レポート、欠損明示 |
| Daily Note 二重起動 | section header 存在チェック | re-run 用 append |
| JSONL 破損 | 各行 try/parse | 不正行を `<file>.broken` に隔離 |
| queue 肥大化 (>10MB) | サイズ監視 | 30 日経過 + digested を archive 移動 |

### 防御原則

- **Idempotent**: 全スクリプトは複数回起動しても二重作用しない
- **Fail-soft**: 1 コンポーネント失敗で全体停止しない
- **Observability**: 全 cron / routine の log を `~/.claude/logs/cowork-*.log` に集約
- **Silent failure 禁止**: Daily Note に必ず痕跡を残す (本環境の `silent-failure-hunter` 原則)

## Test Strategy

### 単体テスト (pytest)

- `rss_watcher.py` dedup
- `tier_classifier.py` rule-based
- `eod_collector.py` git activity (git fixture)
- JSONL schema validation

### 統合テスト (manual dry-run)

```bash
python3 scripts/runtime/rss_watcher.py --dry-run
DRY_RUN=1 scripts/runtime/auto-morning-briefing.sh
python3 scripts/runtime/eod_collector.py --dry-run
# /schedule run <eod-routine-id>
```

### Acceptance Criteria

1. RSS watcher: 任意 feed で 5 件以上が queue に append、再実行で重複ゼロ
2. Morning Briefing: Daily Note に `### Email Tier`, `### Knowledge Queue`, `### Carry Forward` 3 セクション含有
3. End-of-Day: 17:00 routine 後、Daily Note に `## End-of-Day` 追記、`carry_forward.jsonl` 更新
4. Failure mode: Gmail 未認証でも briefing 他セクション出力、警告表示 (silent failure せず)
5. Idempotent: 全 cron 2 回連続実行で破壊なし

### 検証期間

- Day 1-3: 個別 dry-run
- Day 4-7: 全コンポーネント有効化、毎朝目視確認
- Day 8: 1 週間後の振り返り、不具合 + 運用感を `friction-events.jsonl` に記録
- Day 30: `harness-stability` retire 評価対象

### Codex Review Gate

L 規模変更のため実装後に Codex Review Gate (codex-reviewer + code-reviewer 並列) を通す。

## Risks & Reversibility

### Risks

| リスク | 影響 | 緩和 |
|---|---|---|
| Gmail MCP 認証フローが複雑 | Email tier 機能が動かない | 認証手順を guide 化、認証切れでも fail-soft |
| `/schedule` routine がコスト想定以上 | Max plan 圧迫 | 1 routine/day に制限、Day 8 で実測確認 |
| RSS feed が壊れた構造 | watcher が落ちる | feed 別に try/except、parser 例外で skip |
| queue 肥大化で Daily Note 重い | 朝の briefing 遅延 | 30 日 rotation、top 10 制限 |
| 30 日後に「使ってない」と判明 | 過剰実装 | retire 評価で全削除可能 (Build to Delete) |

### Reversible Decisions (撤退条件)

- **Day 8 評価**: 1 週間で knowledge_queue 消化率 < 20% なら RSS watcher 停止 (cron 削除のみ)
- **Day 14 評価**: End-of-Day routine の利用感が悪ければ `/schedule` 解除 (集計スクリプトは残す)
- **Day 30 評価**: 全 4 機能のうち利用率最下位を retire 候補に

詳細: `references/reversible-decisions.md`

### Pre-mortem (失敗モード予測)

- **想定失敗 1**: 朝の Email tier 分類が雑で T1 を見逃す → 段階的に rule 改善、`feedback_xxx.md` に記録
- **想定失敗 2**: RSS queue が「読まない記事の墓場」になる → top 10 制限 + 7 日経過 pending を auto-skip
- **想定失敗 3**: End-of-Day routine が朝の routine と context 衝突 → log 分離、別 routine ID

詳細: `references/pre-mortem-checklist.md`

## References

- [docs/guides/2026-05-09-claude-cowork-equivalents.md](../guides/2026-05-09-claude-cowork-equivalents.md) — 公式機能の使い方ガイド
- [docs/research/2026-05-09-skill-usage-tally.md](../research/2026-05-09-skill-usage-tally.md) — 200-session 集計
- [docs/research/2026-04-21-obsidian-claudecode-absorb-analysis.md](../research/2026-04-21-obsidian-claudecode-absorb-analysis.md) — Obsidian × Claude Code 35 コマンド体系
- [.config/claude/references/scheduling-decision-table.md](../../.config/claude/references/scheduling-decision-table.md)
- [.config/claude/references/web-fetch-policy.md](../../.config/claude/references/web-fetch-policy.md)
- [.config/claude/references/memory-schema.md](../../.config/claude/references/memory-schema.md)
- [.config/claude/references/reversible-decisions.md](../../.config/claude/references/reversible-decisions.md)
- [.config/claude/references/pre-mortem-checklist.md](../../.config/claude/references/pre-mortem-checklist.md)

## Out of Scope (本 spec で扱わない)

- Slack / Discord MCP 連携 (本環境で使われていない)
- Production Block タスクテンプレート skill 量産 (data-driven に棄却)
- Full automation (人介在なし) / 自動 Q7-Q8 推論 (Sycophancy リスクで棄却)
- Cloud Agent / web 経路の活用 (本環境は Claude Code CLI 中心)
- 元記事 (Khairallah) の 5-15 時間/週節約主張の検証 (マーケ煽り、本環境の ROI とは無関係)
