---
date: 2026-05-25
source: docs/research/2026-05-25-khairallah-50-prompts-absorb-analysis.md
status: pending
parent_absorb: 2026-05-25-khairallah-50-prompts
size: M × 5
adopted_from: Khairallah "50 Claude Prompts" Pass 2 verbatim verification by Codex (gpt-5.5)
---

# Khairallah 50 Prompts — M 規模統合プラン (5 tasks)

S 規模 4 件は同セッションで実装済み (P1 mizchi-blog-style, P22 code-reviewer, P3 rewrite, P35 paper-analysis)。本プランは別セッションで `/rpi` 実行用。

## Context

前回 /absorb で「0 件採用」と判定 → user の「手抜きでは？」指摘 → Codex (gpt-5.5) Pass 2 verbatim 検証で **14/16 件が adopt 候補** と判明。S 規模即実装 + M 規模 plan 保存の戦略を user 承認。

詳細経緯: [absorb analysis](../../research/2026-05-25-khairallah-50-prompts-absorb-analysis.md)

## Task T1: research に market / trend report preset

**目的**: Khairallah P31 (Market Research) + P32 (Trend Spotter) を `/research` の preset として吸収

**該当 prompt**:
- P31 verbatim: "market size / players / 5 emerging trends / segments / barriers / tech shifts / 3 opportunities. Exec summary 3 sentences"
- P32 verbatim: "5 accelerating / 3 peaking / 2 emerging. For each: what/evidence/who benefits/who disrupted/timeline. Contrarian insights, not consensus"

**変更ファイル**:
1. `.config/claude/skills/research/SKILL.md:89` — `--template=market` / `--template=trend` の preset selector を追加
2. `.config/claude/skills/research/templates/research-report-template.md` (既存確認) — market template / trend template の 2 種を追加
3. (新規) `.config/claude/skills/research/templates/market-report.md`:
   - sections: Market size + growth rate / Key players + share / 5 emerging trends / Customer segments / Barriers to entry / Tech shifts / 3 opportunities for new entrant
   - Exec summary: 3 sentences cap
4. (新規) `.config/claude/skills/research/templates/trend-report.md`:
   - sections: 5 accelerating / 3 peaking / 2 emerging (12 total)
   - each entry: what(1 sentence) / evidence / who benefits / who disrupted / timeline
   - default framing: contrarian (default to "what the crowd is missing")

**Size**: M (2 SKILL.md edits + 2 new template files)

## Task T2: weekly-review に business report + 7-Q reflection

**目的**: Khairallah P16 (Weekly Business Report) + P49 (Weekly Review 7-question) を `weekly-review` skill に統合

**該当 prompt**:
- P16 verbatim: "Top-line summary (3 sentences) / metrics table (this/last/change%) / 3 wins / 3 concerns / action items. <2 min read"
- P49 verbatim: "7 questions one-at-a-time (3 wins / didn't finish / took longer / should delegate / most important next week / obstacles / what to say no to). Then prioritized action plan (max 5)"

**変更ファイル**:
1. `.config/claude/skills/weekly-review/SKILL.md:53` (レビューフロー) と `:55` の後ろに 7-question reflection mode を追加
2. `.config/claude/skills/weekly-review/templates/weekly-report.md`:
   - `:3` 付近に `## Top-line (3 sentences max)` を追加
   - `:33` の metrics table に `Change %` 列を追加
   - `## Wins (3) / ## Concerns (3) / ## Action Items` セクションを追加
3. `.config/claude/skills/weekly-review/SKILL.md` Phase 6 に「next week action plan max 5」制限を明文化

**Size**: M (1 SKILL.md edit + 1 template restructure)

## Task T3: think/decision に score 1-10 + alternative + regret asymmetry

**目的**: Khairallah P36 (Decision Matrix) + P50 (Life Decision Framework) を `/think decision` mode に統合

**該当 prompt**:
- P36 verbatim: "options × weighted criteria (1-5) × scores (1-10) = totals. Recommended + biggest risk + when would a different option be better"
- P50 verbatim: "top 5 factors / score each option (1-10) / which failure would I regret more / 3 questions I haven't considered / recommendation + circumstances to change"

**変更ファイル**:
1. `.config/claude/skills/think/SKILL.md:148-160` 付近の decision matrix セクション:
   - scores の表記を `{スコア}/10` に明文化
   - 重み (1-5) × scores (1-10) の例を追加
2. `.config/claude/skills/think/SKILL.md:170` 付近 (問うべきだが問っていない質問):
   - 「どちらの失敗をより後悔するか？」を default question として追加
3. `.config/claude/skills/think/SKILL.md:193` 付近 (推奨セクション):
   - 「Recommendation が変わる条件 (under what circumstances)」を必須項目に追加
   - 「別選択肢が上回る条件」を追加
4. `.config/claude/skills/decision/SKILL.md` も同等の rubric を decision-journal entry に組み込む

**Size**: M (think/SKILL.md 3 箇所 edit + decision/SKILL.md 同期)

## Task T4: feature-tracker + spec に 90-day roadmap + priority + bold bet

**目的**: Khairallah P19 (Product Roadmap Builder) を feature-tracker + spec に吸収

**該当 prompt**:
- P19 verbatim: "90-day by month (theme + features S/M/L) / P0/P1/P2 + Impact High/Med/Low / one bold bet feature"

**変更ファイル**:
1. `.config/claude/skills/feature-tracker/SKILL.md:30` 付近の JSON schema:
   - `roadmap_90_day` field 追加 (month1/month2/month3 with theme + features)
   - 各 feature に `priority: P0|P1|P2`, `impact: High|Med|Low`, `effort: S|M|L`, `bold_bet: boolean` を追加
2. `.config/claude/skills/spec/SKILL.md:86` (Product Spec section) に optional `## 90-day Roadmap` セクションを定義 (L 規模 spec のみ)
3. `feature_list.json` schema (もし存在すれば) を migrate

**Size**: M (schema 拡張 + spec template 更新)

## Task T5: document-factory + playbooks に SOP / Runbook type

**目的**: Khairallah P45 (SOP Writer) を document-factory の新 document type として追加

**該当 prompt**:
- P45 verbatim: "Purpose / Scope / Prerequisites / Step-by-step / Decision points / Common mistakes / Quality check. Write for someone doing this for the first time. Assume nothing."

**変更ファイル**:
1. `.config/claude/agents/document-factory.md:141` 付近の document type 一覧に `SOP / Runbook` を追加
2. SOP template を明文化:
   - `## Purpose` (なぜ存在するか)
   - `## Scope` (covers / does not cover)
   - `## Prerequisites` (実行前条件)
   - `## Step-by-step Procedure` (新人が質問なしで follow できる詳細さ)
   - `## Decision Points` (判断が必要な箇所 + ガイドライン)
   - `## Common Mistakes` (典型的な失敗 + 回避策)
   - `## Quality Check` (完了 verification)
3. `docs/playbooks/` 既存 playbook (codex-rules-operations.md / symlink-management.md) を新 template に合わせて軽く修正

**Size**: M (agent 定義拡張 + playbook 同期)

## Execution Order Recommendation

1. **T3 (think/decision)** — 既存 decision matrix が最も近く、verbatim 強化が低リスク
2. **T1 (research preset)** — 新 template 追加で副作用なし
3. **T2 (weekly-review)** — template restructure、既存ユーザーへの影響注意
4. **T4 (feature-tracker schema)** — JSON schema 変更で migration 必要
5. **T5 (document-factory SOP)** — playbook 同期で広範な影響

## Verification

各 T*_完了時:
- `task validate-configs` (harness 設定 lint)
- `task validate-symlinks` (symlink 健全性)
- 既存 skill の trigger word 衝突なし確認

## References

- Source absorb analysis: [docs/research/2026-05-25-khairallah-50-prompts-absorb-analysis.md](../../research/2026-05-25-khairallah-50-prompts-absorb-analysis.md)
- Codex Pass 2 verbatim verification (gpt-5.5, xhigh reasoning): /tmp/codex-absorb-pass2-result.md
- S 規模即実装 commit (本セッション): code-reviewer.md, mizchi-blog-style/SKILL.md, rewrite/SKILL.md, paper-analysis/SKILL.md
- P7 (SEO) + P20 (Meeting Agenda) は **N/A 確定** — 本プラン scope 外

## Meta-finding (this absorb session)

`/absorb` skill の改善トリガー:
- Phase 1.5 で「skip 推奨」framing が **Effort-Avoidance bias** を生む可能性 → `references/topic-family-saturation.md` の Step 4 提示文を再設計対象
- light-phase2 mode の Pass 2 verbatim 照合は **Codex 委譲必須** (Opus 単独だと self-preference bias)
- "Sonnet imagination" anti-pattern を Pass 2 段階だけでなく Phase 1.5 saturation gate でも踏む可能性 (今回 Codex Q1 で Partial 候補 15 件が一括 N/A 化されていた)
