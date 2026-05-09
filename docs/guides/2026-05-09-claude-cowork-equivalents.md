# Claude Cowork 相当機能の使い方ガイド (本環境版)

> **Status**: 2026-05-09 作成 / Claude Code v2.1.119 / Anthropic Max plan
> **目的**: Khairallah の "Claude Cowork" 記事 (マーケ系) が主張する用途 (情報収集 / 知見の蓄え / 改善ループ) を、本環境の **既存** Anthropic 公式機能で実現する方法をまとめる。
> **前提**: 「Claude Cowork」は Anthropic 公式製品としては **存在しない**。ブランディング上の用語にすぎない。

## 1. 「Claude Cowork」は存在しない (誤解の整理)

| 記事の用語 | 実体 |
|---|---|
| "Cowork タスク" | Claude Code セッション (`claude` CLI、`claude -p` 非対話モード含む) |
| "Connector" | MCP servers (Model Context Protocol) |
| "/schedule" | Claude Code 公式 skill (Routines = cron-based 自動セッション、**実在**) |
| "タスクテンプレート" | Skills (本環境に 100+ 登録済み) |
| "Cloud Agents" | Claude.ai web 側の機能、Claude Code とは別経路 |

つまり「Cowork という製品」を覚える必要はなく、**Skills + /schedule + MCP の 3 つの公式機能** を使いこなせば記事の主張する用途は満たせる。

## 2. 公式機能の使い方マップ

### 2.1 Skills

- **何か**: 特定タスク用の指示書 (markdown + frontmatter)。`Skill` tool または `/<name>` で起動。
- **本環境の状態**: 100+ skill 登録済み。`.config/claude/skills/<name>/SKILL.md` または plugin (`~/.claude/plugins/`) 由来。
- **発見**: Claude Code セッション内で skill 名が conversation に注入される (system reminder)。
- **公式 docs**: <https://docs.claude.com/en/docs/claude-code/skills>

### 2.2 /schedule (Routines)

- **何か**: Claude Code セッションを cron 的に定期起動。一回限りの予約も可。
- **本環境の状態**: skill としては利用可能だが、現状 `/schedule list` で確認できる active routine は (要確認)。
- **使い所**: 「毎朝 X を実行」「金曜 17 時にレポート」など。
- **コスト**: Max plan 内の使用量を消費 (subscription 内、追加課金なし)。
- **公式 docs**: <https://docs.claude.com/en/docs/claude-code/routines>

### 2.3 MCP Connectors

- **何か**: Claude Code が外部サービス (Gmail, Calendar, Drive, GitHub, Slack 等) と接続するためのプロトコル。
- **本環境の状態**: **`settings.json` の `mcpServers` は現在空**。skill list に見える `mcp__claude_ai_Gmail__*` 等は plugin 由来で、**まだ認証していない**。
- **追加方法**: `settings.json` または個別 plugin で `mcpServers` を設定 → `authenticate` skill で認証。
- **公式 docs**: <https://docs.claude.com/en/docs/claude-code/mcp>

## 3. Knowledge Pipeline (情報収集) 運用

本環境では `/absorb` skill が **200 session 中 80% で使用、計 93 回呼び出し** という主軸スキル。Claude Cowork 記事が言う Knowledge Pipeline は既に動いている。

### 3.1 標準フロー

```
URL (Zenn / dev.to / blog / 論文)
  ↓
[Step 1] obsidian:defuddle (推奨) または WebFetch
       ※ WebFetch は Haiku 要約混入リスクあり (feedback_webfetch_haiku_summary)
  ↓
[Step 2] /digest  → Obsidian 02-Literature/ に Literature Note (構造化要約) を生成
  ↓
[Step 3] /absorb  → 既存セットアップとのギャップ分析、採用/棄却を Codex+Gemini 並列批評
       ※ Pruning-First: 採用ハードル高め
  ↓
[Step 4] docs/research/YYYY-MM-DD-<slug>-analysis.md に保存
  ↓
[Step 5] MEMORY.md と docs/research/_index.md に 1 行追記
```

### 3.2 各 skill の使い分け

| skill | 用途 | 本環境での使用回数 (200 session) |
|---|---|---|
| `/absorb` | 記事 1 本 → 採用/棄却判断、現状ギャップ分析 | **93 回** |
| `/digest` | 記事 1 本 → Literature Note 生成 (要約・メタデータ) | 2 回 (auto) |
| `/research` | 1 トピック → 複数ソース並列リサーチ → 統合 | 0 回 |
| `/paper-analysis` | 学術論文 → 構造的分析 | 0 回 |
| `/deep-read` | 1 記事 → 対話式理解度チェック | 0 回 |

**所感**: `/absorb` 一強。他は使われていない (3 回未満) ため、必要になったときに使う運用で十分。

### 3.3 WebFetch vs defuddle

| 観点 | WebFetch | obsidian:defuddle |
|---|---|---|
| Haiku 要約混入 | あり (feedback 既知) | なし (生 markdown 取得) |
| 引用 faithfulness | 低下リスク | 高い |
| トークン効率 | 要約済みで少なめ | フル取得で多め |
| 推奨用途 | 概要把握のみ | `/absorb` 等の正式取り込み |

**ルール**: 正式取り込みは `defuddle` 経由。`/absorb` の Phase 1 で hook により WebFetch 由来は警告 (`webfetch_truncation_suspect` event)。

## 4. 改善ループ (改善を回す) 運用

### 4.1 既存の改善 skill

| skill | 用途 | 200 session 使用 |
|---|---|---|
| `/improve` | skill / docs / code を並列点検、整理 | 7 回 |
| `/audit` | コードベース監査、QUESTIONS.md 生成 | 4 回 |
| `/check-health` | doc 鮮度・コード乖離・参照整合性 | 0 回 (M/L Plan で自動) |
| `/skill-audit` | skill A/B benchmark, health audit | 0 回 |
| `retrospective-codify` | 失敗→成果物化 (ast-grep / skill / CLAUDE.md rule) | 0 回 (auto trigger) |

### 4.2 本環境固有の改善ループ (AutoEvolve)

- **4 層ループ**: セッション内 → 日次 → BG (background) → `/improve`
- **詳細**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/autoevolve_details.md`
- **安全機構**: master 直変禁止、1 サイクル最大 3 ファイル
- **AutoEvolve は記事の "weekly refinement" を自動化したもの**。手動で `/improve` 起動も可。

### 4.3 friction-events.jsonl

- セッション中の摩擦 (frustration, stuck) を JSONL に記録 → AutoEvolve Phase 1 で改善候補に変換
- 詳細: `memory/project_friction_detection_loop.md`

## 5. 定期実行 (Routines) の使い方

### 5.1 /schedule の基本

```
/schedule create "毎朝 7:30 に Daily Brief 生成" cron="30 7 * * 1-5" prompt="..."
/schedule list
/schedule delete <id>
```

### 5.2 既存の cron との使い分け

本環境には Claude routine と OS cron が並存:

| 機構 | 既存例 | 適している用途 |
|---|---|---|
| OS cron + shell | `auto-morning-briefing.sh` (`crontab -l`) | 機械的処理 (git log / file 集計 / RSS fetch) |
| Hammerspoon | `daily_enforcer.lua` 18:00 リマインド | OS 通知、UI トリガー |
| `/schedule` (Claude routine) | (現状未活用) | **賢い判断** が必要な定期タスク (priority 分類、carry-forward 推論) |

### 5.3 推奨: 機械的処理は cron、判断は /schedule

```
[06:30] OS cron      ──> rss_watcher.py (記事 fetch + dedup)
[07:00] OS cron      ──> auto-morning-briefing.sh (Daily Note 自動生成)
[17:00] /schedule    ──> Claude routine (End-of-Day 要約、carry-forward 抽出)
[18:00] Hammerspoon  ──> daily_enforcer.lua (リマインダー通知)
```

### 5.4 注意: scheduling-decision-table

`/schedule` を増やすと Daily Brief の subagent と衝突する可能性。詳細は `references/scheduling-decision-table.md`。

## 6. MCP Connectors の追加方法

### 6.1 現状確認

```bash
python3 -c "import json; print(json.load(open('.config/claude/settings.json')).get('mcpServers', {}))"
```

→ 現在 `{}` (空)。skill list に見える `mcp__claude_ai_Gmail__*` 等は plugin 由来で、**未認証**。

### 6.2 Gmail を追加する例

1. `.config/claude/settings.json` の `mcpServers` に追加:
   ```json
   {
     "mcpServers": {
       "gmail": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-gmail"]
       }
     }
   }
   ```
2. Claude Code 再起動
3. `/mcp__claude_ai_Gmail__authenticate` で OAuth フロー
4. `/mcp__claude_ai_Gmail__complete_authentication` でトークン保存

### 6.3 推奨 MCP (本環境のワークフローと相性が良いもの)

| MCP | 用途 |
|---|---|
| Gmail | Morning Briefing で email tier 分類、urgent 抽出 |
| Google Calendar | 当日のミーティング prep brief 生成 |
| Google Drive | 共有ドキュメント参照、`/digest` 入力 |
| Obsidian | 既に `obsidian:*` skill 経由で利用中 |

### 6.4 セキュリティ

- MCP 認証情報は `~/.claude/mcp-credentials/` に保存される (要保護)
- `agentic_security_insights.md` (OWASP MCP Top 10) を参照
- 不要な MCP は無効化 (アタックサーフェス最小化)

## 7. 公式 docs への参照リンク

- Claude Code overview: <https://docs.claude.com/en/docs/claude-code>
- Skills: <https://docs.claude.com/en/docs/claude-code/skills>
- Routines (`/schedule`): <https://docs.claude.com/en/docs/claude-code/routines>
- MCP Protocol: <https://docs.claude.com/en/docs/claude-code/mcp>
- Settings (settings.json): <https://docs.claude.com/en/docs/claude-code/settings>
- Hooks: <https://docs.claude.com/en/docs/claude-code/hooks>

## 8. 本環境ですでに動いている仕組み (確認チェックリスト)

`Claude Cowork 記事` で言及されているもののうち、本環境では既に動作中:

- [x] **Morning Briefing** — `auto-morning-briefing.sh` が cron 08:30 で Daily Note 生成 (`07-Daily/` に保存)
- [x] **Knowledge Pipeline** — `/absorb` 主軸 (200 session で 93 回使用、80% セッションで利用)
- [x] **Improvement Loop** — AutoEvolve 4 層ループ + `/improve` (7 回手動起動)
- [x] **End-of-Day Reminder** — `daily_enforcer.lua` 18:00 通知 + 15 分間隔再通知
- [x] **Knowledge Repository** — Obsidian Vault `02-Literature/`, `04-Resources/`
- [x] **MEMORY.md** — auto-memory に 60+ 記事の absorb index
- [x] **Decision Journal** — `/decision` skill + `references/decision-journal.md`

未実装 (記事が言うが本環境にない):

- [ ] **Email Tier 分類 (T1-T4)** — Gmail MCP 未認証のため不可
- [ ] **End-of-Day 自動レポート** — `daily_enforcer.lua` は通知のみ、レポート生成なし
- [ ] **RSS 監視** — Zenn/dev.to の自動 fetch + queue 化なし
- [ ] **`/schedule` の活用** — skill 利用可だが現状 active routine なし

## 9. 「使いこなす」ためのアクション 3 段階

### Step 1: 既存を確認 (今日)

```bash
# 過去 30 日の skill 利用集計
python3 /tmp/skill_usage_tally.py  # docs/research/2026-05-09-skill-usage-tally.md 参照

# active routine 確認
# (Claude Code 内で) /schedule list

# crontab 確認
crontab -l | grep -E "claude|briefing|vault"
```

### Step 2: 不足を特定 (今週)

- 上記 Section 8 の未実装項目で、自分が本当に必要なもの 1-2 個に絞る
- 残りは「いつか必要になったら」として保留

### Step 3: 実装または運用変更 (必要なときだけ)

- 「実装が必要」と確信できたら、`brainstorming` skill から spec → plan → implement
- 「運用で解決」できるなら、既存 skill の使い方を磨く (例: `/absorb` の Phase 1 gate を毎回通す)

---

## 関連 references

- [knowledge-pyramid.md](../../.config/claude/references/knowledge-pyramid.md)
- [unattended-pipeline.md](../../.config/claude/references/unattended-pipeline.md)
- [scheduling-decision-table.md](../../.config/claude/references/scheduling-decision-table.md)
- [web-fetch-policy.md](../../.config/claude/references/web-fetch-policy.md)
- [memory-schema.md](../../.config/claude/references/memory-schema.md)

## 関連 docs

- [docs/research/2026-05-09-skill-usage-tally.md](../research/2026-05-09-skill-usage-tally.md) — 200 session 集計
- [docs/research/2026-04-21-obsidian-claudecode-absorb-analysis.md](../research/2026-04-21-obsidian-claudecode-absorb-analysis.md) — Obsidian × Claude Code 35 コマンド体系
