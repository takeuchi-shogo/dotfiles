---
date: 2026-06-20
source: text-pasted (Addy Osmani 系 essay "From Prompting Agents to Loop Engineering"、無署名版)
family: loop-engineering / multi-agent-orchestration
saturation_gate: SATURATED-pure-rehash (delta=0)
phase_2_outcome: adopt=0 (全 13 手法 Already 強化不要)
phase_2_5: skipped (codex bash-unreachable + gemini sunset の dual-degraded、adopt=0 で議論余地なし)
status: light-phase2-only
adopted: 0
validation_only_followups: 1
---

## Source Summary

Addy Osmani 系の loop-engineering essay。Steinberger と Cherny の引用を骨格に「prompt engineering → loop engineering」のレベル遷移を主張する教科書的解説。crabfleet (Steinberger の OpenClaw project) を orchestration-as-product の具体例として紹介。

著者は無署名 (記事冒頭 "written with the help of Claude" のみ)。記事末尾 "Other Useful References" で Addy Osmani / Matt Van Horn / Peter Steinberger / Boris Cherny を列挙し、本文がこれらの再パッケージであることを自認。

## Why /absorb proceeded past saturation gate

Phase 1.5 で SATURATED-pure-rehash (delta=0) と判定したが user 判断 `continue` で Phase 2 へ進行。検証目的は (a) per-method 照合台帳の妥当性確認 (b) 6/17 absorb の「採用 0」判定が 3 日後も holding か (c) framing-triggered drift 露出。

## Per-Method Judgment Table (Phase 2 Pass 1 + Pass 2)

| 手法 | verdict | matched_prior (3点セット) | 強化余地 |
|---|---|---|---|
| Loop = 4-step program (prompt/read/decide/re-prompt) | Already (強化不要) | `2026-06-17-loops-with-claude` "4-step loop primitive" / Osmani 引用同定義 | なし |
| Five-loop terminology progression (ReAct→AutoGPT→ralph→/loop+/goal→orchestration) | Already (強化不要) | `2026-06-17-loops-with-claude` "5-stage terminology progression" / 進化系譜 | なし |
| Six parts (trigger/isolation/context/tool-reach/verifier/state) | Already (強化不要) | `2026-04-02-ralph-loop` + `2026-04-11-multi-agent-coordination-patterns` / 個別実装済: trigger=cron+hooks+launchd, isolation=worktree, context=CLAUDE.md+references, tool-reach=MCP+gh, verifier=Codex Review Gate, state=docs/plans+MEMORY+JSONL | なし (cmux/launchd で thinness 確保) |
| PR babysitter pattern | Already (強化不要) | `2026-06-17-loops-with-claude` "/babysit-prs cadence example" / 同名 example | Plan stall は別件 (Validation-only #1) |
| /goal as contract (end-state/evidence/constraints/budget) | Already (強化不要) | `references/scheduling-decision-table.md:23-95` `/goal pilot` 行 + `2026-06-12-fable5-14steps` T3 採用 | 4 要素全て統合済 |
| Cherny 5-step unattended (auto-perm/ultracode/loop/cloud/self-verify) | Already (強化不要) | `2026-06-17-loops-with-claude` "Cherny 5-step" + `2026-06-03-dynamic-workflows` "Workflow tool deliberate non-adopt" / 全要素照合済 | Workflow tool は deliberate non-adopt 維持 |
| Multi-model role split (planner/executor/evaluator/vision) | Already (強化不要) | `references/model-routing.md` Tier 表 + `2026-04-11-multi-agent-coordination-patterns` Generator-Verifier | なし |
| crabfleet (board/durable/child-spawn/sandbox) | N/A | `references/cmux-ecosystem.md` + `2026-05-23-cmux-coding-agent-workflow` / cmux 同型 | 外部 product のため取り込み対象外 |
| Cost = iterations not tokens | Already (強化不要) | `2026-06-17-loops-with-claude` "iteration budget over token budget" / 同主張 | なし |
| Weak-verifier as expensive bug | Already (強化不要) | `2026-05-31-hermes-eval-loop` + `verification-before-completion` skill / verifier 設計 Codex Review Gate 集約 | なし |
| When-not-to-loop (one-shot/unscoped/no-check) | Already (強化不要) | `references/governance-levels.md` + core_principles YAGNI | なし |
| 6-step "build your own" | Already (強化不要) | 上記要素の reorder、新規要素なし | なし |
| Failure modes (verification debt/comprehension gap/silent drift) | Already (強化不要) | `references/comprehension-debt-policy.md` (Osmani 出典明記 live, last_reviewed 2026-04-23) + `silent-failure-hunter` agent | なし |

### Sonnet imagination ガード

Pass 1 で Sonnet (Explore) が `references/scheduling-decision-table.md` を「存在しない」と誤判定 → 実体は `.config/claude/references/scheduling-decision-table.md` (8.1K、`/goal` 4 要素統合済) を Bash で確認、誤判定として除外。同 file の "HIGH 強化可能" 4 件のうち実体は 1 件のみ (PR babysitter Phase A stall) で残りは Sonnet imagination として棄却。`memory/feedback_absorb_sonnet_imagination.md` の典型例。

## Phase 2.5 (Refine) Skip 理由

- adopt=0 確定 (議論対象なし)
- Codex bash-unreachable (MEMORY: feedback_codex_bash_tool_unreachable.md)
- Gemini CLI sunset (MEMORY: feedback_gemini_cli_sunset.md)
- light-phase2 protocol で Phase 2.5 は省略可

Phase 2 結果が「全 Already + Validation-only 1 件」で大方針判断 (multi-agent-orchestration family の deliberate non-adopt 維持) に修正を要する点がないため、cmux Worker での Codex 起動は対費用効果なしと判定。

## Adopted Decisions

なし (adopt=0)。

## Rejected Decisions

全 13 手法 (matched_prior 名指し完了)。詳細は per-method 照合台帳参照。

## Validation-only Follow-up

| # | 対象 | 露出内容 | 訂正方針 |
|---|------|----------|----------|
| 1 | `docs/plans/active/2026-05-19-pr-review-agent-plan.md` | Phase A (launchd polling) 未着手 31 日経過 (2026-05-20 last_updated → 2026-06-20) | user 判定 `kept` で frontmatter に `kept-by: 2026-06-20` 追記済。記事の "PR babysitter" framing が stale-plan audit トリガーとして機能 |

副次観察 (記事と無関係):

- crontab 全 entry が `[PAUSED 20260616-012634]` で停止中 (4 日経過)。user 判定「意図的 (skill 更新 / nightly 移行中)」→ `docs/wiki/log.md` に memo 追記済

## Family Lessons (追記候補なし)

loop-engineering family の `_index.md` family lesson は 6/17 absorb で既に確立 (Osmani 一次は既 absorb、二次紹介は構造的に採用 0)。本 absorb は family lesson を強化せず、validation-only として記録に留める。

## 参照

- 一次源頭: Addy Osmani "AI-assisted coding loops" (`references/comprehension-debt-policy.md` 内出典)
- 直近 twin: `docs/research/2026-06-17-loops-with-claude-absorb-analysis.md` (kumai_yu/Qiita)
- 関連 family: `docs/research/_index.md` "multi-agent-orchestration / loop-engineering" 節
- 露出された plan: `docs/plans/active/2026-05-19-pr-review-agent-plan.md`
- 露出された運用状態: `docs/wiki/log.md` [2026-06-20] memo entry
