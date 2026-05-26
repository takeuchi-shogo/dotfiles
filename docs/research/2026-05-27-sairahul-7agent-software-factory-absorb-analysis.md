---
name: sairahul-7agent-software-factory-absorb-analysis
description: Sai Rahul "7-agent Software Factory" listicle の light-phase2 absorb 分析 (adopt 0 件)
type: research
date: 2026-05-27
status: light-phase2-only
family: multi-agent-orchestration (informal)
saturation: by-spirit (registered family taxonomy には未一致だが、同分野 absorb 30+ 件で functional saturation)
adopt_count: 0
---

# Sai Rahul "7-agent Software Factory" Absorb 分析

## Source Summary

- **Title**: "How to Build a Software Factory with Claude Code That Ships Features While You Sleep"
- **Author**: @sairahul1 (creator-monetization framing: 「Follow @sairahul1」「Bookmark this」「save months」hype)
- **Date received**: 2026-05-27 (URL なし、ユーザーがテキスト貼付)
- **Genre**: Multi-agent orchestration / role-split listicle (popularization-style)

### 主張 (Phase 1 抽出)

1 セッションで全役割を兼ねる "vibe coding" にはハードシーリングがある。
7 つの specialized agent + 3 human checkpoints で「software factory」化すれば
1 developer が backend/frontend/test/validation の vertical slice を ship できる。

### 手法 (10 項目)

1. 7-agent chain: Researcher → Story Writer → Spec Writer → Backend Builder → Frontend Builder → Test Verifier → Validator
2. Read-only roles for research/spec/validation agents
3. Backend/Frontend folder scoping (tool 権限を directory レベルで制限)
4. 3 human checkpoints (story approval / brief approval / PR approval)
5. Backend Builder summary as API contract for Frontend (明示的 handoff document)
6. Acceptance tests against user story (not unit tests)
7. Validator with Critical/Important/Minor severity grouping + no-fix policy
8. CLAUDE.md 100-300 行 persistent memory
9. Context drift fix: throw conversation away for wrong architectural assumption (not patch)
10. Pre-commit hook blocking .env/.key/.pem/secrets

## Phase 1.5: Saturation Gate

- **Family taxonomy 厳密 hit**: なし (claude-code-tips にも `8-step setup` `N tricks` 様の listicle 形式しか hit せず閾値未達)
- **Functional saturation**: 同分野 (subagent role-split / orchestration) で過去 30+ 件 absorb 済 (`docs/research/2026-03-12-subagent-patterns-analysis.md` 以降)
- **直近 baseline**:
  - 2026-05-02 30-subagents-2026: 採用 4 件 (Self-Rejection Rule / Subagent Count Ceiling / edge-case 15 軸)
  - 2026-05-04 Distribution vs Escalation: Bundle A+B1+B2 採用
  - 2026-04-11 Multi-Agent Coordination Patterns: 5-pattern 統合ビュー新設
- **判定**: 形式 PASS だが saturation-by-spirit。ユーザーに 3 択提示 → **light-phase2** 選択

### Step 3.7: 手法 delta 計算

prior_methods (recent absorb から):
- Self-Rejection Rule / Subagent Count Ceiling / 5-pattern coordination view / wrapper-vs-raw-boundary / Subagents vs Advisors split / Minimum Routing Granularity / acceptance-test family / severity grouping (code-reviewer の MUST/CONSIDER/NIT)

current_methods のうち prior と完全重複 8 件: #1, #2, #4, #6, #7, #8, #9, #10
novel 候補 2 件: #3 (Backend/Frontend folder scoping)、#5 (Backend Builder API summary handoff)

**delta = 2** → SATURATED-but-novel → light-phase2 強制提示 → ユーザー選択

## Phase 2 (light): 2 件の novel 候補に絞り込み

### Pass 1 (Sonnet Explore)

| N | 項目 | Sonnet 判定 | 関連ファイル |
|---|------|-------------|-------------|
| N1 | Backend/Frontend folder scoping | **not_found** | `agents/backend-architect.md:1-10`、`settings.json:350-382` の PreToolUse hook に path filter なし、`tools/claude-hooks/src/pre_tool.rs:40-88` の BLOCKED_FILES は linter config 全体保護のみ |
| N2 | Backend Builder API summary handoff | **partial** | `agents/backend-architect.md:44-51` で「API endpoint definitions with example requests/responses」出力 spec あり、`agents/cross-file-reviewer.md:111-115` で API contract 不整合検出あり。ただし backend→frontend explicit handoff flow なし |

### Pass 2 (Opus 判定)

| N | 判定 | 理由 |
|---|------|------|
| N1 | **N/A** | dotfiles は 23 agent を「機能で分離」運用 (backend-architect / frontend-developer は別 session で起動)。並列 builder が同時に path 競合するシナリオが定型化されておらず、path-based hook 強制は YAGNI。2026-05-02 30-subagents absorb 時にも同じ判断で path scope を不採用 |
| N2 | **N/A** | `backend-architect.md:44-51` で既に「API endpoint definitions with example requests/responses」を出力 spec 化済。cross-file-reviewer が事後整合性検出を担当 (`agents/cross-file-reviewer.md:111-115`)。dotfiles の single-session-sequential 開発スタイルでは explicit handoff document 化の必要性が低い。dotfiles 主想定は solo engineer の single-session、Backend agent 別 session → Frontend agent 別 session の二段 handoff シナリオ自体が稀 |

**adopt 0 件確定**。Phase 2.5 省略 (light flag、Gap 0 件のため自動昇格不要)。

## Already (詳細を残さない、参考までに)

記事 10 手法のうち 8 件は既存実装で完全カバー:

| # | 記事手法 | dotfiles 既存 |
|---|---------|--------------|
| 1 | 7-agent chain | `/epd` (Spec → Spike → Validate → Build → Review) + `/rpi` (Research → Plan → Implement) + 23 specialized agents |
| 2 | Read-only research/spec/validation | code-reviewer / codex-reviewer / security-reviewer / product-reviewer 等は全て report-only (no fix) |
| 4 | 3 human checkpoints | `/epd` の Approve gates (spec / spike / pr) |
| 6 | Acceptance tests vs unit tests | test-engineer.md (test 作成) + test-analyzer.md (網羅性検証) の分離 + `superpowers:test-driven-development` skill |
| 7 | Validator severity (Critical/Important/Minor) | code-reviewer の MUST/CONSIDER/NIT/ASK/FYI 5-tier + cross-file-reviewer / silent-failure-hunter / type-design-analyzer 各 severity 別出力 |
| 8 | CLAUDE.md 100-300 lines | user CLAUDE.md ~130 行 + project CLAUDE.md ~70 行、IFScale 知見で「指示数が重要」確認済 |
| 9 | Throw conversation away on wrong assumption | `/checkpoint`, `/recall`, search-first workflow、core principle「壊れたら即STOP・ごまかし禁止」 |
| 10 | Pre-commit hook blocking secrets | lefthook pre-commit + secretlint + prek 統合 |

## Decisions (light-phase2 結論)

- **Adopted**: 0 件
- **Rejected (N/A)**: N1 (folder scoping) / N2 (API summary handoff) — 両者とも dotfiles の運用前提とミスマッチ + 既存仕組みで実害なし
- **Already**: 8 件 (上記表)

## Meta-findings

1. **Family taxonomy gap**: 「multi-agent orchestration / role-split」が registered family taxonomy (`references/topic-family-saturation.md`) に未登録。同分野 30+ 件 absorb 済で**新規 family 追加候補**。閾値判断のためには追加 evidence 収集 (各 absorb の adopt 率トレンド) が必要。
2. **Creator-monetization listicle 系の即時 reject 判定** が機能した: Phase 1.5 で saturation-by-spirit を user 提示 → light-phase2 で 13 分以内に adopt 0 結論。フル workflow なら 20-30 分浪費していた。
3. **30-subagents (2026-05-02)** とほぼ同テーマで baseline 確立済。3 週間以内に同種 listicle が再投入されることを示す popularization velocity の高さ。

## Validation-only Follow-up

なし。記事の framing が dotfiles 内の stale fact / drift を露出させる箇所はなかった (既存仕組みが記事主張をフルカバー)。

## 関連

- `docs/research/2026-05-02-30-subagents-2026-absorb-analysis.md` — 直近同分野 baseline (採用 4)
- `docs/research/2026-04-11-multi-agent-coordination-patterns-analysis.md` — 5-pattern view 確立
- `docs/research/2026-05-04-distribution-vs-escalation-absorb-analysis.md` — Subagents vs Advisors
- `references/topic-family-saturation.md` — Phase 1.5 saturation 判定基準
