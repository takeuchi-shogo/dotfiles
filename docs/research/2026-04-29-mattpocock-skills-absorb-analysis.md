---
source: "AlphaSignal: Skills For Real Engineering (mattpocock/skills, 28K stars 2026-04-27)"
date: 2026-04-29
status: integrated
---

## Source Summary

**主張**: Anthropic Skills spec (2025-12-18) の上で、5-skill daily chain (`grill-me` / `to-prd` / `to-issues` / `tdd` / `improve-codebase-architecture`) を中心に「process encoding (HOW to think) を narrow scope SKILL.md に閉じ込める」 discipline で kitchen-sink CLAUDE.md より travel する。28K stars in 4 days。

**手法**:
- **Process encoding, not knowledge dumping**: skill は walk tree / one-question / recommend / explore-code の手順を encode
- **Narrow scope per skill**: grill-me 11 行、最長 github-triage 170 行、1 skill 1 workflow
- **Intentional auto-invocation control**: `disable-model-invocation: true` で agent 自律 vs user 手動を構造的に分離
- **grill-me**: 設計決定木を 1 質問ずつ walk、AI 推奨回答を添え、コードから derive できる質問は探索
- **to-prd**: 会話履歴を Problem/Solution/User Stories/Implementation/Testing/Out-of-Scope に synthesize し `gh issue create`
- **to-issues**: PRD を vertical-slice tracer-bullet に分解、HITL/AFK マーカー、依存関係順
- **tdd**: vertical-slice red-green-refactor、horizontal anti-pattern (bulk test → bulk code) 明示禁止
- **improve-codebase-architecture**: deepening opportunities + LANGUAGE.md (Module/Interface/Implementation/Depth/Seam/Adapter/Leverage/Locality 固定、component/service/API/boundary 禁止)
- **Personal artifact philosophy**: 個人 `~/.claude/skills/` をそのまま export、汎用化抑制

**根拠**: 28K stars in 4 days、application code zero。AlphaSignal Take: 「taste and narrow scope > feature breadth」。

**前提条件**: Claude Code + GitHub Issues backlog 前提。Auto Mode OFF (Opus 4.7 で grill 中の pause skip 実例 2026-04-26)。Linear/Jira/Beads 利用は fork 必要。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| K1 | Process encoding (HOW to think) | Already | `skill-creator/references/skill-writing-principles.md` 12 原則 (§1 指示を書け、知恵を書くな + Invert Test) |
| K2 | Narrow scope (1 skill 1 workflow, 11-170 lines) | Already | 同 §3 ビルドタスクスコープ + §3.5 5ステップ×2回閾値 + skill-audit |
| K3 | `disable-model-invocation: true` | Already | grill-interview / morning / capture など ~10 skill で実装済 |
| K4 | grill-me (design tree walking) | Already | `grill-interview/SKILL.md` に mattpocock origin タグ付き、削除テスト相当 + Step 3 逐次質問 |
| K5 | to-prd (会話 → PRD → GitHub) | Already | `spec/SKILL.md` Phase 0 interview + Deep Interview Protocol (13 カテゴリ) |
| K6 | to-issues (vertical-slice tracer-bullet) | Already (強化可能) | `prd-to-issues/SKILL.md` (mattpocock + takeuchi adaptation) — Tracer Bullet 原則あり、HITL/AFK マーカーは未実装 |
| K7 | tdd vertical-slice (red-green-refactor) | Gap | CLAUDE.md "Goal-Driven Execution" は TDD 専用でない、fix-issue / ast-grep-practice / gleam-practice に分散 |
| K8 | improve-codebase-architecture (deep modules) | Already | `improve-codebase-architecture/{SKILL,LANGUAGE,DEEPENING,INTERFACE-DESIGN}.md` フル移植済 (mattpocock@2026-04-26) |
| K9 | LANGUAGE.md / closed vocabulary | Already | improve-codebase-architecture/LANGUAGE.md + ubiquitous-language skill + docs/glossary.md |
| K10 | Personal artifact / Build to Delete | Already | ADR-0006 hook-philosophy + harness-debt-register + Build to Delete 原則 |
| K11 | Auto Mode override risk | Already (強化可能) | ADR-0006 Human Judgment 分類でカバー、ただし grill-interview に Auto Mode 警告未記載 |
| K12 | Skill-level evals | Already | empirical-prompt-tuning + skill-audit (description 衝突検証) |
| K13 | Backlog abstraction (Linear/Jira) | N/A | GitHub Issues 運用前提、移行予定なし |
| K14 | Progressive disclosure | Already | ADR-0002 + skill-writing-principles §7 (1階層まで, 500行以下) |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | grill-interview SKILL.md (`disable-model-invocation: true` 済) | Pocock 2026-04-26 で Opus 4.7 Auto Mode が pause を skip する実例。grill-interview に警告無し | Step 3 冒頭に「Auto Mode を OFF にする」起動条件を 1 行追記 (Codex 推奨「Known Limitations 章ではなく起動条件に短く」) | 強化可能 → 採用 |
| S2 | prd-to-issues SKILL.md (Tracer Bullet + blocking 関係) | HITL / AFK マーカー無い。実行モードが暗黙 | Step 3 分解ルール末尾に Mode 付与 + Issue テンプレに `## Execution Mode` + Step 4 確認画面に `[HITL]/[AFK]` バッジ + Step 5 サマリ表に Mode 列 | 強化可能 → 採用 |
| S3 | skill-writing-principles.md 12 原則 | `disable-model-invocation` の使い方ガイダンス無し | §13 Invocation Control Discipline 追加 | 強化可能 → **保留** (Codex 「実害が出るまで分類追加は不要」) |

## Integration Decisions

### Gap

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| K7 | TDD 専用 reference / skill | スキップ | 新規 reference 追加は Pruning-First 違反。Codex「CLAUDE.md Goal-Driven + ast-grep-practice の近接運用で十分」 |
| K13 | Backlog abstraction | N/A | GitHub-only 運用継続、Linear 移行予定なし |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | grill-interview に Auto Mode 警告 | 採用 | Pocock 実例 (Opus 4.7) で friction 顕在化、起動条件として短く埋める |
| S2 | prd-to-issues に HITL/AFK markers | 採用 (Codex 最優先) | 実行モード誤認は実務 friction、テンプレ最小追記で実装 |
| S3 | skill-writing-principles §13 Invocation Control | 保留 | Codex「skill-writing-principles 重くしやすい / 誤用実例が出てから」 |

## Phase 2.5 Refine 結果

### Codex 批評の反映
- K7 を Gap → スキップ (新規 reference は Pruning-First 違反)
- S3 を採用候補 → 保留 (実害が出るまで分類追加は不要、`Known Limitations` 章は記事写しの friction)
- 優先順: S2 (HITL/AFK) > S1 (Auto Mode 警告) > S3 (保留)
- 本質指摘: Pocock から汲むべきは skill catalog ではなく「個人 artifact を過度に一般化しない / 狭い process encoding に閉じる / 更新できない skill は負債化」discipline。これらは既に dotfiles に内蔵済 (skill-writing-principles + ADR-0006 + harness-debt-register)

### Gemini 補完の反映
- Anthropic Skills Spec evolution (Tasks プリミティブ SEP-1686 / Portability) は watch のみ、早期対応不要
- Skill Explosion guard は既存 Pruning-First でカバー (66 skills)
- Auto Mode override は 2026-04-26〜28 にコミュニティでアクティブ議論 (具体日付/数字は未検証)
- 「skill_bloat_ratio メトリクス追加」「Portability frontmatter 拡張」は skill-audit / skill-creator 改修案として記録のみ (今回スコープ外)

## Plan

### Task 1: prd-to-issues に HITL/AFK markers
- **Files**: `.config/claude/skills/prd-to-issues/SKILL.md`
- **Changes**:
  - Step 3 「分解ルール」末尾にルール 5 (各 Issue に Execution Mode を付与) 追加
  - Step 3 「Issue テンプレート」に `## Execution Mode` セクション追加 (HITL / AFK 定義)
  - Step 4 「確認」画面の例に `[HITL]/[AFK]` バッジ追加
  - Step 5 「作成完了」表に Mode 列追加 + 並列着手可能 (AFK) 注釈
- **Size**: S (~15 行追加)
- **Status**: 完了

### Task 2: grill-interview に Auto Mode 警告
- **Files**: `.config/claude/skills/grill-interview/SKILL.md`
- **Changes**:
  - Step 3 「逐次質問」冒頭に 1 行追記 (Auto Mode 中は AskUserQuestion 短絡 → 起動前に OFF)
- **Size**: S (~2 行追加)
- **Status**: 完了

### Task 3: 分析レポート保存
- **Files**: `docs/research/2026-04-29-mattpocock-skills-absorb-analysis.md`
- **Status**: 完了 (本ファイル)

### Task 4: MEMORY.md ポインタ追記
- **Files**: `~/.claude/projects/.../memory/MEMORY.md`
- **Status**: 残

## メタ含意 (Codex 本質指摘)

mattpocock/skills の 5-chain は dotfiles に既に厚く統合済 (4/5 が origin タグ付きで存在)。記事から新規取り込みすべきは「skill catalog」ではなく「discipline」:

1. **個人 artifact を過度に一般化しない** — 既に dotfiles の運用方針
2. **狭い process encoding に閉じる** — skill-writing-principles で実装済
3. **更新できない skill は負債化** — harness-debt-register / Build to Delete で対応済

これらはすべて既存の harness 原則に内蔵されており、新規哲学追加は不要。今回採用したのは S1/S2 の **既存 skill への局所的強化** に留め、Pruning-First を貫いた。
