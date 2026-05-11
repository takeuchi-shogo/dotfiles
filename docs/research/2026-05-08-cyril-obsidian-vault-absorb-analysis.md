---
source: "How to Build an Obsidian Knowledge Vault That Gets Smarter Every Day (@cyrilXBT)"
date: 2026-05-08
status: analyzed
classification: reference-only
adopted_tasks: 3
rejected_main_claims: 8
---

## Source Summary

**主張**: Obsidian Vault は archive ではなく feedback loop を持つ thinking partner にすべき。3 fail mode (capture friction / no connection / no return) を Capture (Readwise/Airr/Whisper/Telegram + N8N) / Pipeline / Obsidian (5-folder) / Claude (intelligence) の 4-layer で解決する。

**手法**:
1. Auto-capture pipeline (Readwise/Airr/Whisper/Telegram bot via N8N、capture friction を 10 秒以下に)
2. 5-folder Vault structure (Inbox/Notes/Ideas/Projects + CLAUDE.md root)
3. Vault root CLAUDE.md template (Who I Am / Current Projects / How This Vault Works / What I Want From You / What I Am Reading)
4. Daily Brief automation (N8N で 6am 自動実行、CONNECTIONS/PATTERN/QUESTION 3 出力)
5. Weekly Synthesis (15min Monday、EMERGING THESIS/CONTRADICTIONS/KNOWLEDGE GAPS/ONE ACTION)
6. Weekly CLAUDE.md refresh (Current Projects + Reading 月曜 5min 更新)
7. Start small onboarding (5 notes から開始)

**根拠**: 経験論ベース、定量データなし。「1month/3month/6month の compound effect」物語のみ。著者は newsletter プロモ目的。

**前提条件**: 個人 PKM 用途 / N8N 環境 / Readwise (有料 SaaS) / Telegram bot / 日常的な情報摂取量。dotfiles の engineering harness scope とミスマッチ。

## Gap Analysis (Pass 1: 存在チェック → Pass 2: Opus 強化)

| # | 手法 | Sonnet Pass 1 | Opus Pass 2 | Codex Phase 2.5 | 最終判定 | 詳細 |
|---|------|---------------|-------------|-----------------|----------|------|
| 1 | SaaS auto-capture pipeline | partial | N/A | 維持 | **N/A** | ベンダーロックイン、scope 外、/digest /absorb /note で代替 |
| 2 | 5-folder Vault structure | exists (8-folder IPARAG) | Already 強化不要 | 維持 | **Already 強化不要** | 8-folder IPARAG > 5-folder simple |
| 3 | Vault CLAUDE.md template | partial | Already 強化可能 | **棄却** | **Already 強化不要** | Codex: CLAUDE.md root 肥大化リスク、別場所 (thinking-context-template) に移行 |
| 4 | auto-morning-briefing CONNECTIONS/PATTERN/QUESTION | partial | Already 強化可能 | **強化不要 + 別問題発覚** | **Already 強化不要** | Codex Critical: Daily Note path 不整合 (`07-Daily` vs `01-Projects/Daily`) を先に解決 |
| 5 | weekly-review 4-frame Synthesis | partial | Already 強化可能 | 強化不要 (項目 A に集約) | **Already 強化不要** | weekly-review 肥大化リスク、contradiction detection 1点に集約 |
| 6 | /profile-drip Vault CLAUDE.md refresh | not_found | Already 強化可能 | **棄却** | **N/A** | 責務違い、profile-drip は memory/user_*.md gap 用 |
| 7 | N8N scheduling | partial (CronCreate/ScheduleWakeup) | Already 強化不要 | 維持 | **Already 強化不要** | 内部 scheduler 十分 |
| 8 | Telegram bot capture | not_found | N/A | 維持 | **N/A** | mobile PKM scope 外、/note skill 代替 |
| 9 | Readwise integration | not_found | N/A | 維持 | **N/A** | 有料 SaaS、設計思想と非整合 |
| 10 | Whisper transcription | not_found | N/A | 維持 | **N/A** | scope 外、OS dictation 代替 |
| 11 | "Start small 5-note" onboarding | partial | Already 強化不要 | 維持 | **Already 強化不要** | obsidian-vault-setup 1-5 インタビューで代替 |
| 12 | Cross-vault auto-link discovery | partial | Already 強化可能 | **棄却** | **Already 強化不要** | 承認付き Link Discovery を自動化はノイズ・誤リンク増 |
| **A (NEW)** | **Contradiction detection (保存済み信念との照合)** | (Codex 発掘) | (Codex 発掘) | **過小評価指摘** | **Partial → 採用** | `/think` は反論・盲点はあるが、過去保存仮説との矛盾照合なし。記事の唯一の実質的差分 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

**5 件中 3 件棄却、2 件強化不要、1 件 (Codex 発掘の) 別案件 (項目 B)**

| # | 旧判定 | Codex 修正 | 理由 |
|---|--------|------------|------|
| 3 | 強化可能 | **棄却** | CLAUDE.md root 肥大化、Codex 推奨の thinking-context-template 移行 (項目 C) で部分採用 |
| 4 | 強化可能 | **強化不要** | --vault-mode は新 mode 追加で Pruning-First 違反、別問題 (path 不整合) を項目 B で対応 |
| 5 | 強化可能 | **強化不要** | weekly-review 肥大化、項目 A に集約 |
| 6 | 強化可能 | **棄却** | 責務違い |
| 12 | 強化可能 | **棄却** | 自動化はノイズ・誤リンク増 |

### Phase 2.5 セカンドオピニオン統合 (Codex)

1. **判定致命的修正**: Phase 2 Pass 2 は "helpful" 寄り。新規 Partial 1 件発見: `/think` の保存済み信念との照合は未実装。記事唯一の実質的差分。
2. **Already 強化可能 5 件中 3 件棄却推奨**: #3, #6, #12 は責務違い・自動化リスク・root 肥大化。
3. **#4 別問題発覚**: Daily Note path 不整合 (`auto-morning-briefing.sh` → `01-Projects/Daily` vs `timekeeper` → `07-Daily`)。記事と無関係だが critical issue。
4. **最終推奨 top 3 (すべて S 規模)**:
   - rank 1: `/think` contradiction check
   - rank 2: Daily Note path contract 検証
   - rank 3: thinking-context-template に読書欄

### Phase 2.5 セカンドオピニオン統合 (Gemini)

- 記事は initial introduction quality、absorb 対象ではなく **reference only** 推奨
- Compound effect 主張は未検証 (Ahrens 2017 ケーススタディのみ、数値研究なし)
- Vault ~1000 ノートで Claude 200K context full embed 不可能 → rolling window / vector top-K pre-filter 必須
- 既に user は Hermes Fleet (Qdrant+Ollama+mem0) 取り込み済み
- 5-folder vs IPARAG 比較研究なし (2025-26)、context dependent

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A | `/think` contradiction check | **採用** | Codex 推奨 rank 1、唯一の実質差分 |
| 1, 8, 9, 10 | SaaS capture layer | **N/A** | dotfiles scope 外 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 3 | Vault CLAUDE.md 2 セクション追加 | **棄却** (Codex) | CLAUDE.md root 肥大化、項目 C で部分採用 |
| 4 | --vault-mode 追加 | **棄却** (Codex) | 別問題 (path 不整合) を項目 B で対応 |
| 5 | 4-frame Synthesis 追加 | **棄却** (Codex) | weekly-review 肥大化、A に集約 |
| 6 | profile-drip variant | **棄却** (Codex) | 責務違い |
| 12 | auto-seeding | **棄却** (Codex) | 自動化はノイズ・誤リンク増 |

### 副次発見 (記事と無関係、Codex 発掘)

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| B | Daily Note path contract 不整合 | **採用** | auto-morning-briefing.sh と timekeeper で Daily 保存先が分散、Vault template 整合性問題 |
| C | thinking-context-template に Reading 欄 | **採用** | CLAUDE.md root ではなく thinking-context に閉じる、月次手動運用 |

## Plan

### Task A: /think skill に contradiction check step 追加 [S]

- **Files**: `~/dotfiles/.config/claude/skills/think/SKILL.md`
- **Changes**: Step 1 (Context Load) または Step 4 (Synthesis) に「thinking-context.md の hypotheses (信じていること) 欄と現在発言の矛盾候補 1 件抽出」step 追加
- **制約 (Codex 注記)**: Vault 全文スキャンではなく `thinking-context.md` の仮説欄だけ対象
- **Size**: S (1 ファイル)
- **検証**: /think を 1 回走らせて矛盾候補が surface するか目視

### Task B: Daily Note path contract 検証 [S]

- **Files**:
  - `~/dotfiles/.config/claude/scripts/runtime/auto-morning-briefing.sh` (現 `01-Projects/Daily`)
  - `~/dotfiles/.config/claude/skills/timekeeper/SKILL.md` (現 `07-Daily`)
- **Changes**: Vault template の正規 path (`07-Daily`) に統一
- **Migration**: 既存 Daily Note の場所が分散している場合は user 判断
- **Size**: S (1-2 ファイル)
- **検証**: 両 skill が同じ Daily Note を append するか

### Task C: thinking-context-template に Reading section 追加 [S]

- **Files**: `~/dotfiles/.config/claude/skills/think/templates/thinking-context-template.md`
- **Changes**: 末尾に `## 5. Currently Reading / Thinking About` section 追加 (3-5 entries 想定、月次手動更新)
- **CLAUDE.md root には追加しない** (Codex 指摘)
- **Size**: S (1 ファイル)

---

## 棄却項目 (記事の主要主張)

- SaaS capture layer (Readwise / Telegram / Whisper / N8N) — ベンダーロックイン
- 5-folder structure 移行 — 8-folder IPARAG > 5-folder
- Daily Brief CONNECTIONS/PATTERN/QUESTION mode — Pruning-First 違反
- Weekly Synthesis 4-frame 丸ごと — weekly-review 肥大化
- /profile-drip Vault refresh variant — 責務違い
- obsidian-knowledge daily auto-seeding — ノイズ増
- "Start with 5 notes" guidance — obsidian-vault-setup で代替済み
- "compound effect" narrative — 数値根拠なし

## Triage 結果

User 選択: A + B + C すべて採用 (3 タスク、すべて S 規模)。

## Notes

- 記事自体は absorb 対象ではなく **reference only** と分類
- 採用 3 タスクは「記事から得た 1 + 副次発見 2」の混合
- 主要主張 (SaaS pipeline / 5-folder / 4-frame Synthesis 等) は dotfiles 用途と非整合のため棄却
