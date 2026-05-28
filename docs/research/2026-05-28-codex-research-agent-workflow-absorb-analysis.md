---
source: "中国語記事「从0开始，十分钟搭建一个帮你筛选优质信息的Codex Research Agent工作流」"
date: 2026-05-28
status: integrated
family: morning-briefing/personal-research-agent
adoption: 3 件採用 (T1+T2+T3) — annotation 欄 + negative filter + 週次 diff 提案
---

## Source Summary

**主張**: 毎朝 Codex CLI が Twitter/HN/競合等の情報源を scan、CODEX.md (私は誰/関心/見たくないもの/信頼ソース) で過濾し、構造化 brief を Obsidian に書き出す。n8n cron で起動。core insight は「毎日のブリーフ末尾に手動 annotation を残し、週次で Codex が一週間分を読んで CODEX.md を更新する feedback loop」。

**手法** (11 件抽出):
1. n8n self-host で cron スケジュール ($5/月 DigitalOcean)
2. Brave Search MCP でリアルタイム外部検索 (無料 2000 query/月)
3. Filesystem MCP で Obsidian Vault 書き込み
4. Codex CLI が core executor (terminal native)
5. CODEX.md = research-agent 専用 context file (私は誰/関心/既知/現プロジェクト/信頼ソース/見たくないもの)
6. **"見たくないもの" Negative Filter section**
7. Research prompt 4-step (主要トピック検索 → シグナル/ノイズ過濾 → 競合情報 → 構造化統合出力)
8. **毎日のブリーフ末尾に手動 annotation (useful / noise / missing)**
9. **週次 feedback loop: Codex が 7 日分の annotation を読み CODEX.md を自動更新**
10. 拡張: deeper research キュー / 4h ごと競合監視 / 週報生成
11. Telegram 通知

**根拠**: 著者個人の 2 ヶ月運用。「3 ヶ月目には brief 精度が劇的に向上する」と主張するが数値根拠は薄い。

**前提条件**: Codex CLI 利用可、Obsidian Vault 運用、OpenAI/Brave API key、n8n self-host する意欲、外部 Twitter ユーザー (中国語圏)。

## Phase 1.5: Saturation Gate

- **Family**: `morning-briefing / personal-research-agent`
- **過去 absorb 件数**: 1 件 (Hermes personal analyst 2026-04-14, 採用あり → `auto-morning-briefing.sh` + `morning-briefing` skill として実装済み)
- **判定**: PASS (warning) — N=1 で飽和未達。ただし Hermes と内容近接で「既存実装との詳細比較」が中心になる

## Gap Analysis (Pass 1 + Pass 2)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | n8n cron | Already | `scripts/runtime/auto-morning-briefing.sh` + cron で実装済み (n8n は overkill) |
| 2 | Brave Search MCP | Partial | Hermes で HN/arXiv/RSS 検討済だが、現実装 source は GH/git/memory のみ。外部 web リアルタイム検索は未統合 |
| 3 | Filesystem MCP で Obsidian | Already | `OBSIDIAN_VAULT_PATH/00-Inbox/YYYY-MM-DD.md` に append 済み |
| 4 | Codex CLI 駆動 | N/A | `claude -p` 使用中、cmux Worker 経由で Codex 切替可。model 選択の好み |
| 5 | CODEX.md 分離 context file | Partial | CLAUDE.md/MEMORY.md に統合済だが、briefing 用「見たい/見たくない」spec は分離されていない |
| 6 | "見たくないもの" Negative Filter | **Gap** | briefing prompt に noise filter 基準が暗黙的 → **T2 で採用** |
| 7 | Research prompt 4-step | Already (強化可能) | 現 prompt は Issues/Activity/Memory/Focus 4 セクションだが、過濾基準が暗黙 |
| 8 | Brief 末尾 annotation | **Gap** | feedback signal 収集 mechanism なし → **T1 で採用** (最優先) |
| 9 | 週次 Codex 自動 context tuning | **Partial** | context auto-tuning loop なし。**T3 で採用 (差分"提案"止まり、auto-update せず)** |
| 10 | deeper research / 4h 競合 / 週報 | N/A | YAGNI、過剰拡張 |
| 11 | Telegram 通知 | Already | Discord (MORNING_WEBHOOK_URL) で代替済 |

## Phase 2.5: Refine (Codex + Gemini)

### Codex 批評 (xhigh reasoning)

- **見落とし**: DailyNote と weekly-review の責務境界の議論欠落
- **過大評価**: n8n 置換 / HN/arXiv/RSS (Hermes で既出)
- **過小評価**: negative filter の明文化 (#6)
- **前提の誤り**: n8n/Twitter 前提は個人 cron 環境には過剰
- **最優先**: #8 annotation 欄
- ⚠️ **重要 safety 指摘**: #9 は「自動更新」ではなく **「差分提案止まり」** にすべき

### Gemini grounding

- annotation loop の典型的失敗パターン: **手動負担増による更新停止**
- CODEX.md 分離は context 肥大化防止に有効 (静的指示 vs 動的知見)
- cron は軽量・安定、n8n は外部連携には強いが管理コスト増
- Brave 2000 query/月は morning brief には十分。Tavily/Jina は目的別併用が理想

### 修正点

| # | 元判定 | 修正後 | 理由 |
|---|-------|-------|------|
| #9 | Gap | **Partial (差分提案止まり)** | Codex safety: auto-update は危険 |
| #8 | Gap | **Gap (最優先)** | Codex/Gemini 両者同意 |
| #6 | Gap | **Gap** | Codex が過小評価と確認 |

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| T1 | Brief 末尾に `## Notes` annotation 欄 (S) | **採用** | 最優先。摩擦最小設計 (3 行記入) |
| T2 | auto-morning-briefing.sh の prompt に negative filter (S) | **採用** | Codex 指摘で過小評価訂正 |
| T3 | weekly-review に annotation 集計 + diff 提案 (M) | **採用** | Codex safety 指摘を反映し auto-update 禁止、user 承認制 |
| 他 8 件 | Already / N/A / 過剰 | 不採用 | Hermes 系で既存対応 or YAGNI |

## Plan & Implementation

### T1 (S): `morning-briefing/templates/briefing.md` に annotation 欄
- 追加: `## 📝 Notes (読了後 30 秒で記入 — /weekly-review で集計)`
- フォーマット: `useful / noise / missing` の 3 行 (全空欄 OK)
- 既存 SKILL.md の Anti-Patterns に「AI が自動生成で埋めない」を追記

### T2 (S): `scripts/runtime/auto-morning-briefing.sh` PROMPT に negative filter
- 追加: 「48h 前と同内容の重複 / Bump 系単一コミット / 進行に影響しないリファクタ逐一列挙 / 14 日以上 stale な backlog Issue」を除外
- シグナルなし時は「該当なし」を明記 (フェイク項目防止)
- SKILL.md Anti-Patterns に「シグナルなしで焦点を捻り出さない」を追記

### T3 (M): `weekly-review/SKILL.md` に Phase 2.7 追加
- 過去 7 日の `~/daily-reports/morning/YYYY-MM-DD.md` から `## Notes` を grep
- 3 日未満記入 → サンプル不足、来週まで継続記入を促す
- 頻出 noise (≥3 回) / 頻出 missing (≥2 回) を抽出
- **diff "提案" のみ**。auto-update せず user 承認制 (Codex safety 指摘反映)
- 集計結果は `~/.claude/skill-data/weekly-review/annotation-history.jsonl` に蓄積

## メタ学習

- **same-family quick adoption**: Hermes (4-14) で既に同分野 absorb 済みのため、Phase 1.5 で saturation 警告を受けつつも「既存実装との詳細差分」に集中できた (delta novelty 3 件)
- **Codex safety 指摘の価値**: 「auto-update 危険、差分提案止まり」は Opus の Phase 2 では拾えなかった重要な guardrail。Phase 2.5 並列批評の存在価値を再確認
- **Gemini feedback loop 失敗パターン**: 「手動負担増で更新停止」は典型的失敗。T1 で 3 行記入の摩擦最小設計を採用したのは正解
- **記事の novelty 評価の難しさ**: 表面的には generic tutorial だが、annotation → 週次 context update の loop は dotfiles に欠けていた具体パターン。「内容は近接、しかし運用 mechanism が違う」記事は Phase 2 詳細比較が必要

## 参照

- 関連: [Hermes Personal Analyst (2026-04-14)](2026-04-14-hermes-personal-analyst-analysis.md) — morning-briefing 系 foundational
- 関連: [Cyril Obsidian Vault Smarter (2026-05-08)](2026-05-08-cyril-obsidian-vault-absorb-analysis.md) — auto-morning-briefing.sh パス統一
- 実装: `~/.claude/skills/morning-briefing/templates/briefing.md`, `~/.claude/skills/morning-briefing/SKILL.md`, `~/dotfiles/scripts/runtime/auto-morning-briefing.sh`, `~/.claude/skills/weekly-review/SKILL.md`
