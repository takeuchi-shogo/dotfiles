---
date: 2026-06-20
source:
  - https://x.com/mvanhorn/status/2063865685558903149 (Matt Van Horn "WTF Is a Loop?" — LinkedIn Pulse mirror で原文回収)
  - https://addyosmani.com/blog/loop-engineering/ (Addy Osmani "Loop Engineering")
family: loop-engineering / multi-agent-orchestration
saturation_gate: SATURATED-pure-rehash (delta=0、19/19 全手法 rehash)
phase_2_outcome: adopt=0 (Source 2 は同日 6 時間前に absorb 完了済 essay と同一記事)
phase_2_5: skipped (codex bash-unreachable + gemini sunset の dual-degraded、adopt=0 で議論余地なし)
status: light-phase2-only
adopted: 0
validation_only_followups: 0
related:
  - docs/research/2026-06-20-loop-engineering-essay-absorb-analysis.md (twin、6時間前 absorb 完了の Addy Osmani 系 essay)
  - docs/research/2026-06-17-loops-with-claude-absorb-analysis.md (kumai_yu/Qiita 二次紹介、3日前 adopt=0)
  - docs/research/2026-06-14-opik-self-repairing-harness-absorb-analysis.md (Karpathy loop engineering tweet、6日前 adopt=0)
  - references/comprehension-debt-policy.md (Osmani 一次源、出典明記で 2026-04-23 から live absorb)
---

## Source Summary

2 ソース同時提示:

1. **Source 1**: Matt Van Horn (@mvanhorn) "WTF Is a Loop? Peter Steinberger vs. Boris Cherny" — Boris Cherny の WorkOS Acquired Unplugged event 発言と Steinberger tweet (2.2M views) を結節点に loop の 5-stage lineage を整理した meta-synthesis。X tweet は image-only のため LinkedIn Pulse mirror から原文回収。
2. **Source 2**: Addy Osmani "Loop Engineering" blog — Codex と Claude Code が 5 primitives + memory を揃えたという product feature 確認と 1 つの canonical morning loop の説明。**今日 (2026-06-20) 6 時間前に既 absorb 済み記事と同一**。

両ソースは同一 family の同時期 (2026-06 上旬) 派生で、Cherny/Steinberger 引用を共通骨格とする。

## Per-Method 照合台帳 (全 19 手法 → prior 名指し)

### Source 1 (Matt Van Horn) — 9 手法

| current 手法 | verdict | matched_prior |
|---|---|---|
| Loop の 5-stage lineage (ReAct→AutoGPT→ralph→/goal→orchestration) | rehash | `2026-06-20-loop-engineering-essay` "Five-loop terminology progression" / 進化系譜同型 |
| Boris Cherny の loop 定義 (subroutine/altitude shift) | rehash | `2026-06-20-loop-engineering-essay` + `2026-06-17-loops-with-claude` Cherny "I write loops" 共通引用元 |
| /loop starter (babysit PRs) | rehash | `2026-06-20-loop-engineering-essay` "PR babysitter pattern" 同名 example + `references/scheduling-decision-table.md:22` live |
| Cherny 5 tips (auto/dynamic/goal/cloud/self-verify) | rehash | `2026-06-20-loop-engineering-essay` "Cherny 5-step unattended" 全要素照合済 (Workflow tool は deliberate non-adopt 維持) |
| Yegge Gas Town (Mayor + patrol + git-backed) | rehash | `2026-06-20-loop-engineering-essay` "crabfleet (board/durable/child-spawn)" + `references/cmux-ecosystem.md` 同型 |
| roborev (background commit review, Dan Kornas) | rehash | Codex Review Gate (codex-reviewer + code-reviewer 並列) + `2026-05-31-hermes-eval-loop` weak-verifier |
| Three hard stops (max-iter/no-progress/budget) | rehash | `references/resource-bounds.md` Doom-Loop + `2026-06-17-loops-with-claude` "Hard stop (Ralph Wiggum)" + `governance-map.md` |
| Skill-first thesis (loop=plumbing, skill=asset, intent debt) | rehash | `2026-04-12-tan-thin-harness-fat-skills` 完全同概念 (Parameterized Skill 却下と共に codify 済) |
| Cron との差分は middle decision-maker | rehash | `references/managed-agents-scheduling.md` + ReAct→AutoGPT 系譜で既説明 |

### Source 2 (Addy Osmani) — 10 手法

| current 手法 | verdict | matched_prior |
|---|---|---|
| Five pieces + memory (6 要素) | rehash | `2026-06-20-loop-engineering-essay` "Six parts (trigger/isolation/context/tool-reach/verifier/state)" 同一構造 |
| Automations = heartbeat (Codex Automations tab + Triage inbox) | rehash | `2026-06-20-loop-engineering-essay` + `references/managed-agents-scheduling.md` + `auto-triage` skill |
| /goal: stop condition + separate validator (4 要素契約) | rehash | `references/scheduling-decision-table.md:23` `/goal` pilot 行 + `2026-06-12-fable5-14steps` T3 採用済 |
| Worktrees で collision 回避 (--worktree / isolation: worktree) | rehash | `CLAUDE.md` L45 worktree 隔離 + `cross-file-fix-workflow.md` + `autonomous/SKILL.md` |
| Skills (SKILL.md / `$name` invocation / tight boring description) | rehash | `2026-04-12-tan-thin-harness-fat-skills` + `skills/skill-creator/description-optimization.md` |
| Plugins/Connectors = real tools (PR open/Linear ticket) | rehash | `references/mcp-toolshed.md` + `references/claude-code-threats.md` + `.mcp.json` |
| Sub-agents: maker-checker 分離 (`.codex/agents` / `.claude/agents`) | rehash | `references/multi-agent-coordination-patterns.md` Generator-Verifier + Codex Review Gate parallel + `stage-transition-rules.md` |
| One canonical morning automation loop | rehash | `auto-morning-briefing.sh` (251 行 live) + `2026-04-14-hermes-personal-analyst` |
| Three sharper problems (verification / comprehension debt / cognitive surrender) | rehash | `references/comprehension-debt-policy.md` (Osmani 出典明記、last_reviewed 2026-04-23) + `silent-failure-hunter` agent |
| Codex vs Claude Code primitive mapping | rehash | `2026-06-20-loop-engineering-essay` "Codex vs Claude Code mapping" + `2026-04-29-codex-vs-claudecode-role-split-absorb-analysis` |

**delta = 0** (19/19 全手法に matched_prior 3 点セット完備、名指しできない手法ゼロ)。

## Why /absorb proceeded past saturation gate

Phase 1.5 で SATURATED-pure-rehash (delta=0) + Source 2 が 6 時間前既 absorb 完了済と提示したが、user 判断 `continue` で Phase 2 へ進行。検証目的は (a) per-method 照合台帳の妥当性確認 (b) Pass 1 が prior 台帳に未網羅の novel 機構を発見しないか (c) 6/20 essay absorb の adopt=0 が holding か。

Pass 1 結果は全 19 手法 exists/partial、Pass 1 が挙げた "novel 3 件" (nightly status JSONL prepend / Thin Harness 10 原則 codify / Heterogeneous Signal Priority) はいずれも記事言及外の dotfiles 既存資産で、記事から強化案を引き出す対象ではない (Sonnet imagination ガード)。台帳の妥当性 holding 確認。

## Phase 2.5 Skip 理由

- adopt=0 確定 (議論対象なし)
- Codex bash-unreachable (`memory/feedback_codex_bash_tool_unreachable.md`)
- Gemini CLI sunset (`memory/feedback_gemini_cli_sunset.md`)
- light-phase2 protocol で Phase 2.5 は省略可
- 6 時間前の twin absorb (`2026-06-20-loop-engineering-essay`) で同条件 Phase 2.5 skipped 前例

cmux Worker での Codex 起動は対費用効果なしと判定 (大方針判断 = multi-agent-orchestration family の deliberate non-adopt 維持 + loop-engineering family の per-method 台帳 holding に修正を要する点なし)。

## Adopted Decisions

なし (adopt=0)。

## Rejected Decisions

全 19 手法 (matched_prior 3 点セット名指し完了)。

## Validation-only Follow-up

なし。

- stale-plan audit は 6/20 essay absorb (twin) で完了済 (PR review plan `2026-05-19-pr-review-agent-plan` kept-by 2026-06-20)
- crontab PAUSED memo も 6/20 essay absorb で `docs/wiki/log.md` 追記済 (4 日経過、意図的)

## Family Lessons (追記候補なし)

loop-engineering family の `_index.md` family lesson は 6/17 absorb 時点で確立済:

> 一次ソース (Osmani) は `references/comprehension-debt-policy.md` に出典明記で既 absorb 済み。二次紹介・派生記事は構造的に adopt=0 になる。

本 absorb は family lesson を強化せず、**「同一一次源を 6 時間以内に再提示されても skip すべきだった」事例**として記録に留める。次回同 family は Phase 1 の取得直後 (Phase 1.5 進入前) に「直近 24h 以内の同 family absorb がないか」を Bash 1 行で確認する short-circuit を検討するが、現状の per-method 照合台帳が 6 ステップで結論到達できるため、新 mechanism 追加は YAGNI。

## 教訓 (このセッション固有)

- ユーザーが「2 ソース同時提示」した場合、Phase 1 取得後に**最初に**「同日付の twin absorb 報告がないか」を確認する。今回は 6 時間前 (`2026-06-20-loop-engineering-essay`) で adopt=0 確定済を Phase 2 開始後に検出した
- continue 選択は「台帳の妥当性に疑いを持つ」シグナルとして読み、Pass 1 で *prior 台帳に未網羅の novel 機構* を別フィールドで追跡する angle が機能 (今回は novel 検出 0 で台帳 holding)

## 参照

- 一次源頭: Addy Osmani "AI-assisted coding loops" (`references/comprehension-debt-policy.md` 内出典)
- 直近 twin (6 時間前): `docs/research/2026-06-20-loop-engineering-essay-absorb-analysis.md`
- 直近 triplet (3 日前): `docs/research/2026-06-17-loops-with-claude-absorb-analysis.md`
- 関連 family: `docs/research/_index.md` "multi-agent-orchestration / loop-engineering" 節
