---
source: "30 Claude Code Sub-Agents I Actually Use in 2026 (anonymous, Medium 系)"
date: 2026-05-02
status: integrated
tags:
  - absorb
  - subagent
  - harness
  - meta-principle
  - pruning-first
  - self-rejection-rule
  - subagent-count-ceiling
---

# 30 Claude Code Sub-Agents 2026 absorb analysis

## ソース

- **著者**: anonymous (Medium 系記事と推定)
- **タイトル**: 30 Claude Code Sub-Agents I Actually Use in 2026
- **カテゴリ**: subagent カタログ + meta principles
- **受領日**: 2026-05-02

## Source Summary

### 主張

- Claude Code を「OS として使う」前提で、100+ subagent を試した上で残った 30 best を提示
- 3 大原則として **Single-purpose** / **Difficulty path (Beginner→Intermediate→Advanced で haiku/sonnet/opus を使い分け)** / **Description-driven auto-delegation** を提唱
- 各 subagent は `.claude/agents/<name>.md` に YAML frontmatter (`name`, `description`, `model`) を伴う形式

### 30 agents (9 カテゴリ)

| カテゴリ | # | agents |
|---|---|---|
| Engineering | 1-3 | code-reviewer / bug-hunter / git-bisect |
| DevOps | 4-6 | migration-validator / secret-scanner / cost-spike |
| Product | 7-9 | spec-writer / edge-cases / ab-test-planner |
| Sales | 10-12 | lead-researcher / cold-email / renewal-risk |
| Marketing | 13-15 | hook-writer / seo-cluster / content-audit |
| Customer Support | 16-18 | ticket-triage / bug-reproducer / knowledge-gap |
| Operations | 19-21 | inbox-hawk / meeting-notes / okr-health |
| Finance | 22-24 | burn-rate / cap-table / variance |
| Research | 25-27 | source-verifier / counterargument / methodology-critic |
| Personal Productivity | 28-30 | daily-plan / resurrector / decision-log |

### 根拠

- 著者の経験談 (100+ subagent をテスト → 30 best)
- 独立検証なし。匿名 Medium 系記事

### 前提条件

- 著者は agent fleet を business team サイズで運用するソロ起業家系の使い方を想定
- 個人 dotfiles で subagent 数を増やすコストには言及していない (router 劣化リスクは扱われていない)

## Phase 1 + 2: Gap Analysis

集計: **exists 7 / partial 5 / not_found 3 / out_of_scope 15**

### 主要項目テーブル

| # | agent | 判定 | 詳細 |
|---|------|------|------|
| 1 | code-reviewer | Already (強化不要) | 既存 reviewer/code-reviewer は COMPLETION CONTRACT + 5 次元スコア + Critic Evasion 耐性 + Dynamic Rubric Generation を装備、記事の単純 review より深い |
| 2 | bug-hunter | Already (強化不要) | systematic-debugging skill + edge-case-analysis でカバー |
| 3 | git-bisect | Partial | git CLI を直接呼ぶ既存パターンで足りる、新規 subagent 不要 |
| 4 | migration-validator | Already (強化可能) | `migration-guard` 既存だが forward+reverse BLOCK rule + Postgres-specific hard blockers が薄い |
| 5 | secret-scanner | Already (強化不要) | secretlint + lefthook + AgentShield/security-scan で多層防御済み |
| 6 | cost-spike | Out of scope | dotfiles に SaaS 課金がない |
| 7 | spec-writer | Already (強化不要) | `/spec` Phase 0 6 項目 + Prompt-as-PRD 哲学が記事より深い、vanity reject は哲学衝突 |
| 8 | edge-cases | Already (強化可能) | `edge-case-analysis` SKILL.md が存在するが Step 4 の 15 軸チェックリスト補足が薄い |
| 9 | ab-test-planner | Out of scope | dotfiles に A/B 実験基盤なし |
| 10-12 | Sales (lead/email/renewal) | Out of scope | ソロ dotfiles に Sales pipeline なし |
| 13-15 | Marketing (hook/seo/content-audit) | Out of scope | dotfiles に marketing pipeline なし |
| 16-18 | Customer Support | Out of scope | dotfiles に CS pipeline なし |
| 19-21 | Operations (inbox/notes/okr) | Out of scope | timekeeper / weekly-review / decision で代替 |
| 22-24 | Finance (burn/cap/variance) | Out of scope | dotfiles に財務 pipeline なし |
| 25 | source-verifier | Already (強化不要) | absorb skill Phase 2.5 の Codex+Gemini fact-check で機能 |
| 26 | counterargument | Already (強化不要) | `/debate` は multi-model orchestration で設計思想が完全に異なる、新規追加 NG |
| 27 | methodology-critic | Already (強化不要) | paper-analysis skill + Gemini critic でカバー |
| 28 | daily-plan | Already (強化不要) | `/timekeeper` の対話型コーチング (Q1-Q7 + 深掘り) と structured 4-task は設計思想衝突 |
| 29 | resurrector | Already (強化不要) | `/checkpoint` + HANDOFF.md + Running Brief で代替 |
| 30 | decision-log | Already (強化不要) | `/decision` の 5 項目に「撤回条件」既存、record-condition を完全カバー |

## Phase 2.5: deep-dive で発見した novel pattern

ユーザーから「徹底検証して、手抜きないか」の指摘を受けて Phase 2.5 を表面 Already/N/A 判定で終わらせず、**meta-principle 層**まで掘り下げた結果、以下 2 件の Gap が発見された。

### Gap-A: Self-Rejection Rule pattern (新規発見)

著者が「100+ → 30 に絞った」プロセスは "agent を増やすほど性能が落ちる" 経験則を示している。これは個別 agent コピーよりも価値の高いメタ原則で、dotfiles の `agent-design-lessons.md` に未収録。

- **要点**: subagent 候補は「既存 agent/skill の責務拡張で吸収できないか」を **追加前** にチェックする self-rejection ルール
- **既存 mechanism との関係**: skill-audit / skill-writing-principles は skill 側、agent 側に同等の絞り込み原則が欠けていた

### Gap-B: Subagent Count Ceiling (新規発見)

Gemini 補完で「50+ subagent fleet で 9/10→5/10 に劣化」の独立観察が得られた。dotfiles 側に明示的な **subagent 個数の警戒ライン** が文書化されていない。

- **現在数**: 33 個 (Gemini 警戒ライン 50 まで残り 17)
- **要点**: Count Ceiling を 40-50 と置き、超過時は新規追加禁止 + 既存 agent 統合・廃止を必須化

### 採用候補 (Phase 2.5 + deep-dive 後)

| ID | 内容 | 判定 | 採否 |
|----|------|------|------|
| T2 | `migration-guard.md` に forward+reverse BLOCK rule + Postgres hard blockers 追記 | Already (強化可能) | 採用 |
| T3 | `edge-case-analysis` SKILL.md Step 4 に 15 軸補足例 | Already (強化可能) | 採用 |
| T5 | `agent-design-lessons.md` に Self-Rejection Rule pattern セクション | Gap (deep-dive で発見) | 採用 |
| メタ | `agent-design-lessons.md` に Subagent Count Ceiling セクション | Gap (deep-dive で発見) | 採用 |

### 棄却 (主要)

| 項目 | 理由 |
|---|---|
| code-reviewer (#1) | 既存 reviewer は COMPLETION CONTRACT + 5 次元スコア + Critic Evasion 耐性 + Dynamic Rubric Generation で記事より深い |
| spec-writer (#7) | `/spec` Phase 0 6 項目 + 思考ツール哲学で実質カバー、vanity reject は哲学衝突 |
| counterargument (#26) | `/debate` は multi-model orchestration で設計思想が完全に異なる、新規追加 NG |
| daily-plan (#28) | `/timekeeper` の対話型コーチング (Q1-Q7 + 深掘り) と structured 4-task は設計思想衝突 |
| decision-log (#30) | `/decision` の 5 項目に「撤回条件」既存、record-condition を完全カバー |
| 残り 25 個 | out_of_scope (business team) または既存 skill/subagent で実質カバー |

## Phase 2.5: Codex + Gemini 批評サマリ

### Codex (`codex-rescue` subagent) 結論

- **最終推奨採用件数: 1 件 (T3 のみ)**
- 「新規 subagent 追加は router 劣化リスク」「既存 agent/skill 追記以外は不可」
- ROI: T3 (15 axes 汎用) > T2 (code-reviewer 限定強化) > その他
- 採用 0 件も妥当と判定 (Pruning-First の極端側)
- 重要な指摘: 「個別 agent コピーは router decision space を汚染、メタ原則 codify が ROI 高い」

### Gemini (Google Search grounding) 結論

- **#1 CONFIRMED**: Anthropic 公式が single-purpose subagent を **context isolation + accuracy** 目的で推奨
- **#2 UNFOUND**: solo engineer が business team subagent fleet (Sales/Marketing/CS/Finance) を維持して ROI 出した独立検証は **見つからず**
- **#3 CONFIRMED**: 50+ subagent で品質 9/10→5/10 に劣化 + token cost spike (独立コミュニティ観察)

### 統合判定

- Codex 推奨 (T3 のみ) と Gemini 警告 (50+ degradation) が独立に **Pruning-First** を支持
- ユーザー指摘で deep-dive 実行 → meta-principle 層で Gap-A (Self-Rejection Rule) と Gap-B (Count Ceiling) が高価値 Gap として発見
- Codex の「採用 1 件」推奨を超えて 4 件採択するのは、deep-dive で発見した novel pattern が Codex 表面評価のスコープ外だったため

## Phase 3: 採用最終 4 件

### Task 1: T2 - `migration-guard.md` 強化

- **Files**: `.claude/agents/migration-guard.md`
- **Changes**: forward+reverse BLOCK rule + Postgres-specific hard blockers (例: `DROP COLUMN`, `ALTER TYPE`, non-concurrent `CREATE INDEX`) を ~10 行追記
- **Size**: S
- **Rationale**: 記事 #4 migration-validator の「両方向 BLOCK」が既存 migration-guard に欠けていた

### Task 2: T3 - `edge-case-analysis` SKILL.md Step 4 強化

- **Files**: `.claude/skills/edge-case-analysis/SKILL.md`
- **Changes**: 15 軸チェックリスト補足 (boundary / nil / concurrency / clock / encoding / locale / numeric overflow / empty input / very-large input / partial failure / retry idempotency / network partition / disk full / permission / ordering) を ~10 行追記
- **Size**: S
- **Rationale**: Codex も「ROI 最高」と判定。15 軸は既存 Step 4 を汎用的に強化

### Task 3: T5 - `agent-design-lessons.md` に Self-Rejection Rule

- **Files**: `.claude/references/agent-design-lessons.md`
- **Changes**: 新規セクション「Self-Rejection Rule Pattern」(~25 行)
  - 候補 agent は追加前に「既存 agent/skill の責務拡張で吸収できないか」を必ずチェック
  - 100+ → 30 のような絞り込み事例を引用
  - skill-audit と直交する **agent 側** の絞り込みルールとして明示
- **Size**: S
- **Rationale**: deep-dive で発見した novel pattern。個別 agent コピーより ROI 高い

### Task 4: メタ - `agent-design-lessons.md` に Subagent Count Ceiling

- **Files**: `.claude/references/agent-design-lessons.md`
- **Changes**: 新規セクション「Subagent Count Ceiling」(~30 行)
  - 警戒ライン: 40-50 個 (Gemini 観察 50+ で 9/10→5/10 劣化を引用)
  - 現在数: 33 個 (残り 17)
  - 超過時の運用: 新規追加禁止 + 既存 agent 統合・廃止必須
  - skill-audit / harness-debt-register との連携
- **Size**: S
- **Rationale**: 個数管理の警戒ラインを明示しないと自然増で router 劣化に至る

合計: **4 ファイル変更、~75 行追加、S 規模**

## Phase 4 → 5: 即実行 (S 規模、その場で完了)

実装は同セッションで完了済み (4 Edit 成功)。

| Task | File | Status |
|---|---|---|
| T2 | `.claude/agents/migration-guard.md` | Edit 成功 |
| T3 | `.claude/skills/edge-case-analysis/SKILL.md` | Edit 成功 |
| T5 | `.claude/references/agent-design-lessons.md` (Self-Rejection) | Edit 成功 |
| メタ | `.claude/references/agent-design-lessons.md` (Count Ceiling) | Edit 成功 |

## メタ発見

- dotfiles 既存 subagent: **33 個** (Gemini 警戒ライン 50 まで残り 17 個)
- 記事「30 agents 全採用」を実行すると **63 agent → 性能崩壊確実**
- 新規 subagent 追加は今後 **既存 33 個との責務重複チェック** + **既存拡張優先** で運用 (Self-Rejection Rule に codify 済)

## 教訓 (次回 absorb 用)

1. **「徹底検証」の効用**
   ユーザーの「手抜きない？」指摘で deep-dive を実行 → メタ原則レベルで Self-Rejection Rule (高価値) と Count Ceiling を発見。表面 Already/N/A 判定では見逃していた。**Phase 2.5 で「meta-principle 層に Gap が残っていないか」を 1 ステップ追加すべき**。

2. **Pruning-First の継続効果**
   30 個ある記事から累積 1-2 件採用 (今回 4 件は novel pattern 発見で増加) は 40+ absorb 平均と一致。**「全部採用」「半分採用」は記事の見栄えに引きずられた誤り**。

3. **個別 agent vs メタ原則の ROI 差**
   個別 subagent コピーは router decision space 劣化リスクで不可。メタ原則 (Self-Rejection / Difficulty path / Single-purpose) は references にまとめて codify する方が ROI 高い。**「コピー可能なものから採用候補に挙げない」を Phase 2 で先に切る**。

4. **既存 subagent 数の自覚**
   dotfiles 33 個は警戒ラインに近い。今後の subagent 追加は厳禁、既存拡張で対応。**Count Ceiling を文書化したことで自動的にこの警戒が走る**。

5. **Codex + Gemini 並列の価値 (再確認)**
   Codex (採用 1 件推奨) と Gemini (50+ degradation 警告) は独立だが結論一致 = bias mitigation 機能した。匿名 Medium 系記事は **特に独立検証なしの主張が混在** するため、grounded fact-check が必須。

## 関連参照

- [agent-design-lessons.md](../../.config/claude/references/agent-design-lessons.md) — 本 absorb で 2 セクション追加
- [edge-case-analysis SKILL.md](../../.config/claude/skills/edge-case-analysis/SKILL.md) — 15 軸補足
- [migration-guard.md](../../.config/claude/agents/migration-guard.md) — forward+reverse BLOCK rule 追加
- [feedback_absorb_already_deepdive.md](../../.claude/projects/-Users-takeuchishougo-dotfiles/memory/feedback_absorb_already_deepdive.md) — Already 判定で deep-dive 怠ると見逃すパターン (本セッションで再現)
- 関連 absorb:
  - [Top 67 Claude Skills absorb](2026-04-19-top67-claude-skills-analysis.md) — 64 却下 (Pruning-First) の先例
  - [Karpathy Skills absorb](2026-04-20-karpathy-skills-absorb-analysis.md) — メタ原則 codify が個別 skill コピーより ROI 高い
  - [Subagent Context Fork absorb](2026-04-27-subagent-context-fork-absorb-analysis.md) — fork デフォルト棄却の先例
