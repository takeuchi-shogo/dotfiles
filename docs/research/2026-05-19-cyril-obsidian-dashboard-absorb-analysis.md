---
source: "How to Build an Obsidian Dashboard That Shows You Everything That Matters Today (@cyrilXBT)"
date: 2026-05-19
status: analyzed
classification: reference-only
adopted_tasks: 2
rejected_main_claims: 10
related: docs/research/2026-05-08-cyril-obsidian-vault-absorb-analysis.md
---

## Source Summary

**著者**: @cyrilXBT (Telegram newsletter funnel、content farm pattern 11 件目)
**前回**: 2026-05-08 absorb で reference-only 既分類 (同一著者)

**主張**: Obsidian Dashboard = Dataview ベース 6-section single note (Today's Priorities / Active Projects / Next 7 Days / Client Health / Open Loops / Revenue Pulse) + Claude MCP morning briefing + N8N 6AM Telegram。朝 45min → 10min に短縮できる。

**手法**: Dataview TABLE クエリ + YAML schema per type (project/task/client) + 番号付きフォルダ構造 + OPEN: prefix タスク管理 + N8N × Telegram 配信

**前提条件**: agency/solo consultancy 文脈 (client + MRR + revenue pulse)。solo dev には domain mismatch。定量根拠なし、newsletter CTA で着地。

**Bias signals**:
- domain mismatch (solo dev、CRM/revenue pulse 不要)
- "Filesystem MCP" 名称曖昧 (generic)
- 6-section 構成の効果検証なし
- 同一著者の繰り返し: Cyril 記事 2 本目、手法重複多数

---

## Gap Analysis (Pass 1 Sonnet → Pass 2 Opus → Phase 2.5 Codex+Gemini)

12 手法すべてに最終判定テーブル:

| # | 手法 | Sonnet Pass 1 | Opus Pass 2 | Phase 2.5 修正 | 最終判定 | 詳細 |
|---|------|---------------|-------------|----------------|----------|------|
| T1 | Read-Not-Store dashboard | partial | N/A (domain mismatch) | 維持 (Gemini: Agentic Synthesis 既備) | **N/A** | auto-morning-briefing.sh で Agentic Synthesis 実装済 |
| T2 | Dataview TABLE FROM query | partial | Partial | N/A (Gemini: Dataview 2026 legacy/Bases へ) | **N/A → 副次採用 (micro-dashboard)** | プラグイン推奨のみ、Bases caveat 付き |
| T3 | YAML schema per type | partial | Partial | T2 と統合 (Codex) | **Partial → micro schema** | client は不要、minimal schema 化 |
| T4 | Folder numbered | exists (8-folder) | Already 強化不要 | Codex: 実体は 9-folder (`08-Agent-Memory` まで) | **Already + doc 精度修正** | `templates/obsidian-vault/CLAUDE.md:14-24` |
| T5 | OPEN: prefix | partial | Partial 強化候補 | **Already 降格 (Codex)** | **Already** | `timekeeper/SKILL.md:76-79,204-205,224-245` で「明日に持ち越し」既存 |
| T6 | LIMIT 10 forcing | partial | Already 強化不要 | 維持 | **Already** | timekeeper Q1=1, Q2=3-5 で既に十分 |
| T7 | Client health | not_found | N/A | 維持 (Codex: solo dev 版 health は vault-maintenance.sh + weekly-review で吸収) | **N/A** | CRM 不要 |
| T8 | briefing rubric | partial | Already 強化候補 | **強化不要降格 (Codex)** | **Already** | `auto-morning-briefing.sh:166-185` で rubric 既備 |
| T9 | property auto-update | not_found | N/A | 維持 (Gemini: 型不整合/race/property hallucination/security 多数文書化) | **N/A** | failure mode 多数 |
| T10 | N8N + Telegram | partial | Already 代替 | 維持 | **Already** | Hammerspoon + launchd 代替済 |
| T11 | EoD review ritual | exists | Already 強化不要 | **Partial 降格 (Codex)** | **Partial → 採用** | `daily_enforcer.lua:214-227` の `## 日報` marker と `timekeeper SKILL.md:219-245` の `## Review` 不整合 |
| T12 | property typo lint hook | not_found | N/A | 維持 | **N/A** | YAGNI |

---

## Phase 2.5 セカンドオピニオン詳細

### Codex (gpt-5.5) の判定修正

1. **T5 OPEN: prefix を Partial → Already 降格** — `timekeeper/SKILL.md:76-79,204-205,224-245` で「明日に持ち越し」既存、翌朝 plan で前日読込、daily carryover はほぼカバー済
2. **T8 briefing rubric を強化候補 → 強化不要降格** — `auto-morning-briefing.sh:166-185` で既に priority/suggestion limit/CI/deadline/30行/untrusted boundary を持つ rubric 完備
3. **T11 EoD review を Already 強化不要 → Partial 降格** — `daily_enforcer.lua` と `timekeeper` review の責務不整合 (section format 不一致)。記事と無関係の実装ギャップだが実害が近い
4. **T4 folder precision** — 「8-folder」は古い、実体は `00-Inbox` から `08-Agent-Memory` まで 9 folder
5. **T2/T3 統合評価** — Dataview dashboard は schema が前提、別評価は雑、micro-dashboard としてまとめて評価すべき

**優先度提案 (Codex)**:
- Rank 1: T11 派生 EoD surface 整合 (dashboard 追加より実害が近い)
- Rank 2 (Dataview を実際に使う前提のみ): T2/T3 派生 micro-dashboard (3 セクション、minimal schema)

### Gemini (grounded) の補完

1. **Dataview は 2026 でメンテモード** — **Bases** (2025 公式) が新標準、**Datacore** (Dataview author 次世代) も存在。新規構築なら Bases を推奨
2. **"Filesystem MCP" は generic** — mcp-obsidian + obsidian-skills が canonical (File over App 思想)
3. **6-section business dashboard は marketing fabrication** — community は "Agentic Synthesis" へ移行、Dataview 依存の rigid dashboard は非推奨トレンド
4. **AI property auto-update failure modes documented**: 整合性崩壊 / Bases スキーマ型不整合 / race condition / property hallucination / security risk
5. **OPEN: prefix 規約の出典** (Karpathy LLM Wiki/Steph Ango 影響説) — 出典 URL なし → Gemini 幻覚の可能性大、独立検証不能、採用根拠にしない

---

## Integration Decisions

### 採用 (副次発見)

| # | 項目 | 規模 | 理由 |
|---|------|------|------|
| A | T11 派生: `daily_enforcer.lua` に `## Review` section detector 追加 | S (1-2 ファイル) | Codex Rank 1。記事と無関係の実装ギャップ、実害近い |
| B | T2/T3 派生: Dataview micro-dashboard template (3-section, minimal schema, Bases caveat 付き) | S (2 ファイル) | Codex Rank 2 (Dataview 採用前提)。ユーザー明示採択。Bases 移行 caveat 必須 |

### 棄却 (記事の主要主張すべて)

| # | 項目 | 理由 |
|---|------|------|
| T1 | Read-Not-Store 6-section dashboard | 6-section は marketing fabrication、Agentic Synthesis (auto-morning-briefing) で代替済 |
| T4 全面置換 | 4-folder (01-PROJECTS 等) 構造 | 9-folder IPARAG が既存、agency 文脈 (CLIENTS 等) 不要 |
| T5 | OPEN: prefix convention | timekeeper 「明日に持ち越し」で機能カバー済 |
| T6 | LIMIT 10 | Q1=1, Q2=3-5 で既に厳しい (solo dev には適切な粒度) |
| T7 | Client Health monitor | solo dev 文脈、CRM 不要、vault/project health は vault-maintenance.sh で吸収 |
| T8 | briefing prompt rubric 改善 | `auto-morning-briefing.sh:166-185` で rubric 既備 |
| T9 | DONE:/UPDATE: property auto-update | failure mode 多数文書化、daily-report append-only と原則対立 |
| T10 | N8N + Telegram | Hammerspoon + launchd で代替済 |
| T11 元主張 EoD ritual | timekeeper review で代替 (派生問題のみ採用) |
| T12 | property typo lint hook | YAGNI |

---

## Plan

### Task A: T11 派生 EoD surface 整合 [S]

**問題**: `daily_enforcer.lua:214-227` は `## 日報` HTML marker を検出するが、`timekeeper/SKILL.md:219-245` の `/timekeeper review` は `## Review` ヘッダー形式で日報を生成する。両者の section format が不整合で、review 完了を enforcer が認識できないケースがある。

**Files**:
- `/Users/takeuchishougo/.hammerspoon/daily_enforcer.lua` — `has_meaningful_review_content` 関数追加。`build_status()` で `## 日報` OR `## Review` の OR 判定

**Approach**:
1. `extract_section` を header-based に拡張、または別関数 `extract_review_section` を追加
2. `## Review` 以降 next `##` までを抽出し、中身が空でなければ `report_done = true` で OR 取る
3. HTML marker (`<!-- DAILY_REPORT_START -->`) 検出と header 検出の両方をカバー

**Verification**:
1. テスト用 daily note を作成し `## Review\n### やれたこと\n- foo` を含む状態に
2. Hammerspoon 再ロード後 `build_status()` が `report_done = true` を返すか目視
3. `/timekeeper review` を実走させて menu DAY 表示に変わるか確認

---

### Task B: Dataview micro-dashboard template [S]

**前提**: Dataview plugin 既導入 or 新規インストール予定の場合のみ有効。Bases 移行計画あり → schema は migration-friendly に。

**Files**:
- `/Users/takeuchishougo/dotfiles/templates/obsidian-vault/Dashboard.md` (新規) — 3-section template (Today/Carryover/Open Loops)、`07-Daily/` 連携、HTML marker 内に query 配置
- `/Users/takeuchishougo/dotfiles/.config/claude/skills/obsidian-vault-setup/references/dashboard-template.md` (新規) — usage notes + Bases migration caveat (Dataview 2026 maintenance mode 注記)
- `/Users/takeuchishougo/dotfiles/.config/claude/skills/obsidian-vault-setup/references/plugin-recommendations.md` — Dataview 行に Bases 移行注記追加

**制約 (Codex)**:
- Client / Revenue / Telegram / N8N / property auto-update は入れない
- project/task/daily schema は最小化 (`type`, `date`, `status` のみ)
- Bases 移行を見据えて schema は migration-friendly に (YAML frontmatter 標準準拠)

**Verification**:
1. Vault に `Dashboard.md` を配置し Dataview plugin 有効化
2. `07-Daily/` 配下の daily note 5 個に最小 frontmatter (`type: daily, date: YYYY-MM-DD`) を付与
3. Dashboard.md を開き 3 セクションが render されるか確認

---

## Notes

- 記事自体は **reference only** 分類 (前回 2026-05-08 absorb と同じ判定)
- 採用 2 タスクは「副次発見 1 (T11 派生) + Dataview 採用判断 1 (T2/T3 派生)」
- Dataview legacy 化に注意、Bases 移行時に micro-dashboard は再設計予定
- content farm pattern 11 件目を記録 (Boris/Three-Model Stack/Cyril×1/12-rule/zodchixquant/0xfene/Nav Toor/Khairallah/Dreaming/Agent Governance/Cyril×2)
- 同一著者 2 本目: 手法重複が多く、記事間でのデルタは小さい

---

## Triage 結果

**採択**: Task A + Task B 両方採用 (T11 派生 + T2/T3 派生)
