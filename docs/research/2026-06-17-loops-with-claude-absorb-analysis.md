---
title: "How to Create Loops with Claude (kumai_yu/Qiita) absorb 分析"
date: 2026-06-17
source: https://qiita.com/kumai_yu/items/54ded70a5a68a5ca15d5
family: loop-engineering / multi-agent-orchestration
saturation: SATURATED-pure-rehash (N=15, delta=0)
adoption: 0
status: reference-only
---

# How to Create Loops with Claude — absorb 分析 (採用 0)

## 結論

loop engineering family **N=15 件目**、新規論点ゼロ (delta=0)。全11手法を per-method
照合で prior に名指しでき、採用0。直近の同 family 採用0/skip 判定 (3日前 Opik 記事
`2026-06-14-opik-self-repairing-harness`、khairallah 14-features skip) と完全一致。

**決定的証拠**: 記事が引用する Addy Osmani の loop engineering エッセイは、既に
`references/comprehension-debt-policy.md` に**出典明記で absorb 済み**。一次ソースが
取り込まれているため、その二次紹介である本記事に新規性はない。

ユーザーは Saturation Gate で `continue` を選択 (台帳照合の念押し検証)。フル workflow
(Phase 2 Pass1/Pass2 + Phase 2.5 Gemini 批評) を回した結果も採用0で確定。

## Source Summary (主張)

- 「coding agent を prompt するな、agent を prompt する loop を設計せよ」(Cherny/Steinberger)
- loop = recursive goal。6部品 (automations/worktrees/skills/connectors/sub-agents/memory)
- writer≠checker (evaluator-optimizer)、hard stop (Ralph Wiggum loop 回避)、autonomy ladder
  (4段階)、token cost 監視 + command allowlist、loop pipeline、comprehension debt 等の caveat

## per-method 照合台帳 (全 current 手法 → prior 名指し)

| current 手法 | verdict | matched_prior (rehash 立証) |
|---|---|---|
| Loop = recursive goal | rehash | `2026-06-14-opik` Karpathy loop core / `2026-04-02-ralph-loop` — Cherny "I write loops" 引用共通 |
| Automations (cron/hook) | rehash | `references/managed-agents-scheduling.md` (launchd/cron) + `scripts/auto-triage-runner.sh` + `auto-morning-briefing.sh` |
| Worktrees | rehash | `CLAUDE.md` L45 worktree 隔離 + `dynamic-workflows` Already |
| Skills (手順マニュアル) | rehash | `skills/` 100+ + `2026-04-12-tan-thin-harness-fat-skills` (intent debt 同概念) |
| Connectors (MCP) | rehash | `references/mcp-toolshed.md` + settings.json mcp hook |
| Sub-agents (maker≠checker) | rehash | `references/multi-agent-coordination-patterns.md` Generator-Verifier + `30-subagents` + Codex Review Gate |
| Memory file (PROGRESS.md) | rehash | `references/resume-anchor-contract.md` (HANDOFF/RUNNING_BRIEF) + `cc-7-layer-memory-model.md` |
| Hard stop (Ralph Wiggum) | rehash | `2026-04-02-ralph-loop` + `review-loop-patterns.md` (max-iterations 100) + `resource-bounds.md` Doom-Loop |
| Autonomy ladder (4段階) | rehash | `references/governance-levels.md` 4段階 (Observe/Review/Auto-Merge/Trusted) — 記事 level1-4 と同型 |
| Token cost + command allowlist | rehash | `references/deny-rules-catalog.md` (102 deny/71 allow) + `resource-bounds.md` |
| Build second loop / pipeline | rehash | `dynamic-workflows` pipeline() + learned 昇格ループ (`auto-triage`→`promote-learnings`) |
| caveat: comprehension debt | rehash | `references/comprehension-debt-policy.md` — **Osmani 記事を出典に既 absorb** (専用ファイル) |
| caveat: cognitive surrender / two-people-opposite | rehash | comprehension-debt-policy.md が概念カバー。用語のみ未文書化だが新規実装提案なし → 追記は instruction cost の無駄 (Sonnet imagination として除外) |

delta = 0 (名指しできない手法ゼロ)。

## Phase 2.5 (Gemini 批評) — novel 候補の棄却記録

Gemini grounding が周辺知識から novel 候補2点を提示したが、Pass 2 で両方棄却:

| Gemini Q3 候補 | 棄却理由 |
|---|---|
| context window poisoning 対策 (中間コンテキストリセット) | (a) **記事の主張ではない** (記事原文に poisoning の言及なし) (b) `context-constitution.md` PreCompact flush/PostCompact verify + `feedback_tool_call_parse_context.md` で既存 |
| tool call 回数上限 (同一ファイル50回検索の抑制) | (a) **記事の主張ではない** (記事の allowlist はセキュリティ目的で回数制限ではない) (b) `resource-bounds.md` Doom-Loop Window (20 fingerprints) で既存 |

Q1 (loop detection/escape hatch) は既存 stagnation/hard-stop の言い換え。Q2 (Cherny/Steinberger
発言の一次資料) は grounding 不可。Codex は MEMORY 既知問題 (Bash tool から到達不能) +
3日前 Opik で同一トピックを Codex 批評済みのため fallback 条項に沿い省略。

## Validation-only Follow-up

なし。governance-levels.md は記事の autonomy ladder と同型 (4段階) で drift なし。
Pass1 で Sonnet が「記事は L0-L4 の5段階」と報告したが、記事原文は level 1-4 の4段階
(suggest→draft→apply-with-approval→auto-complete) で段階数一致 = Sonnet 誤読、drift ではない。

## 教訓 (family-level)

- loop engineering vendor/紹介記事は概念核が全飽和。一次ソース (Osmani) が
  comprehension-debt-policy.md に既 absorb 済みのため、二次紹介は構造的に採用0になる。
- Gemini の周辺知識補完は「記事に無い一般論」を novel と誤提示しやすい。採用候補は
  必ず「記事原文の specific 提案か」を引用照合してから昇格する (Gemini imagination ガード)。
