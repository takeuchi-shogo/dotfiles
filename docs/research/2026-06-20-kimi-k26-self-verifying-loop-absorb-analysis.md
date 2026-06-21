---
date: 2026-06-20
title: "The Self-Verifying Loop: 300 agents, 4,000 steps, 5 live data feeds on autopilot with Kimi K2.6"
source: Kimi.ai ベンダーマーケ記事 (テキスト貼り付け)
family: multi-agent-orchestration
saturation: SATURATED-pure-rehash
delta_methods: 0
adopted: 0
status: light-phase2-only
related:
  - docs/research/2026-06-18-kimi-k26-self-improving-swarm-loop-absorb-analysis.md
  - docs/research/2026-06-03-dynamic-workflows-absorb-analysis.md
  - docs/research/2026-04-11-multi-agent-coordination-patterns-analysis.md
---

# Source Summary

Kimi.ai が同一ベンダーから 2 日違い (6/18 と 6/20) で出した 2 本目のマーケ記事。
6/18 は generic な "self-improving loop"、今回は具体事例として「100 EV-market companies を分析、5 live feeds (Binance/Yahoo/WB/IMF/stock) で検証、3 verify passes で 0 error」。

主張: Opus 4.8 が plan + verify、Kimi K2.6 swarm が execute、PER-COMPANY CHECKLIST が verifier の rubric。
- 1st pass: 12/100 fail (revenue mismatch / citation 404 / margin empty)
- 2nd pass: 3/100 fail
- 3rd pass: 0 → loop が自己停止

framing: "Another DeepSeek moment"、Kimi $20B、OpenRouter weekly leaderboard #1。

# Phase 1.5 Saturation Gate

- family: **multi-agent-orchestration** (今朝の Khairallah absorb で N=30+ 確認、同日午後にこの記事で +1)
- 過去 absorb の代表: `2026-06-18-kimi-k26-self-improving-swarm-loop`, `2026-06-20-khairallah-agent-team-intro`, `2026-06-03-dynamic-workflows`, `2026-04-11-multi-agent-coordination-patterns`
- 採用率: 直近 3 件 (6/20 Khairallah=0 / 6/18 Kimi=1 borderline / 6/3 dynamic-workflows=0) → ~10% (< 20% 閾値)
- delta 算出: 全 9 手法 rehash + 2 N/A → **delta = 0**
- 判定: **SATURATED-pure-rehash** (skip 推奨)

user 選択: continue (フル workflow、台帳照合に念のため疑いを通すため)。

## Per-method 照合台帳 (delta=0 立証)

| # | current 手法 | verdict | matched_prior (ファイル + 引用 + 同等性理由) |
|---|--------------|---------|---------|
| 1 | Swarm + verify loop (Opus plans/verifies + Kimi executes) | rehash | `2026-06-18-kimi-k26-self-improving-swarm-loop-absorb-analysis.md` "Generator-Verifier swarm pattern" — 同一ベンダー6日前 absorb、構造的同一 (planner=Opus / executor=Kimi / verifier=Opus) |
| 2 | 300 parallel agents | rehash | 上記 6/18 absorb "300-agent swarm" — 同じ数値、`references/multi-agent-coordination-patterns.md` で fan-out 既出 |
| 3 | 4000 steps + 3 verify passes to zero (iterate-until-clean) | rehash | `2026-06-03-dynamic-workflows-absorb-analysis.md` "loop-until-done | Already" + `scripts/runtime/completion-gate.py` + 6/18 absorb の同パターン — 失敗 0 までループは同等 |
| 4 | PER-COMPANY CHECKLIST が verifier の rubric | rehash | `references/review-checklists/` 各 lang + Codex Review Gate の 7項目 + 6/18 absorb の deterministic verifier rubric — checklist=verifier input は既存パターン |
| 5 | Reject failed → requeue → run until clean | rehash | `references/best-of-n-guide.md` Best-of-N + Workflow `loop-until-dry/loop-until-count` patterns + 6/18 で Cost-Arbitrage 採用時に同パターン明記 |
| 6 | 5 live data feeds (Binance/Yahoo/WB/IMF/stock) as source-of-truth | rehash | `/research` + `/deep-research` skill description "fan-out web searches, fetch sources, adversarially verify claims, synthesize a cited report" — 外部 source-of-truth 照合は既存 |
| 7 | Opus 4.8 plan + Kimi K2.6 execute (model split) | rehash | `references/model-routing.md` Tier 表 (Opus=推論/判断, Sonnet=実装/探索) + 6/18 absorb で同一を rehash 認定済 |
| 8 | "Quality equals the checklist" (rubric=quality contract) | rehash | `skill-audit` + Codex Review Gate 7項目 rubric + `2026-06-17-agentic-code-review-absorb-analysis.md` "deterministic gate" 採用 — rubric=品質契約は既存 |
| 9 | Citation URL resolvability + numerical tolerance check | rehash | `/deep-research` skill description "adversarially verify claims" — adversarial 検証は既存 (具体 sub-check はその上位概念に内包) |
| 10 | "DeepSeek moment" + $20B framing + OpenRouter #1 | N/A | vendor marketing、手法でない。6/18 absorb で同一を N/A 認定済 |
| 11 | Kimi 強み (Finance/Academic/200k context/Traceability) | N/A | vendor product claim、手法でない |

全 9 手法 (1〜9) に `matched_prior` の 3 点セット (ファイル名 + prior 手法名 + 同等性理由) が揃った。delta=0 確定。

# Phase 2 Pass 2 — Already 強化分析

| # | 既存仕組み | 記事の具体検証項目 | 強化案候補 | 採否 |
|---|-----------|------------------|-----------|------|
| 1 | `/deep-research` skill "adversarially verify claims" | (a) source URL resolvable / (b) numeric tolerance / (c) no empty field | description / rubric に 3 項目を例示として加える | **棄却** — Claude Code 組み込み skill で本体不可視 (description のみ、ファイル実体到達不能)。編集対象が存在しない。中国語版 `~/dotfiles/.agents/skills/deep-research/SKILL.md` は Codex platform 用で Claude Code から起動しないので対象外 |
| 2 | `completion-gate.py` + Codex Review Gate | Convergence telemetry (1st 12/100 → 2nd 3/100 → 3rd 0) | rejection count を pass ごとにログ出力 | **棄却** — overkill。「loop が回って 0 で停止する」観測可能性は既存で十分、各 pass の reject 件数を見たい運用ケースが想定不能 (YAGNI) |
| 3 | Codex Review Gate 7 項目 rubric | "verifier checklist is the most important part of the prompt" | research/review skill instruction に "verifier checklist=contract" 一文追加 | **棄却** — Codex Review Gate 7 項目 + skill-audit + `2026-06-17-agentic-code-review` の "deterministic gate" 採用で同概念は既に明文化済み。冗長追加は重複 |

3 候補全棄却。

# Phase 2.5 — Refine (degraded)

| 委譲先 | 結果 |
|-------|------|
| Codex (`codex exec --sandbox read-only`, gpt-5.5 xhigh, 480s timeout) | **silent exit** — 8分間で出力 0 行、assistant message を出さず終了。`feedback_codex_bash_tool_unreachable.md` の典型パターン (Bash tool 経由で TTY 不在 → Considering 段階で silent stall) |
| Gemini (`gemini -p`) | **sunset** — Code Assist for individuals は IneligibleTierError (Antigravity 移行要求)。`feedback_gemini_cli_sunset.md` 確認済み |

両者 unavailable で **degraded fallback** に進む。Opus 自己分析で結論を確定 (self-bias 補正なしを明示)。
SKILL.md `Phase 2.5` セクションの「Codex 失敗時は fallback 理由を分析レポートに明記して Phase 3 に進んでよい」に準拠。

self-bias 補正が無いケースの risk: Opus が「採用 0 が妥当」と即断した可能性。
反証材料: per-method 台帳の全 9 行で `matched_prior` の 3 点セット (ファイル名 + 手法名 + 理由) を明示済み。台帳行が削れる可能性は低い (rehash の立証が立っている)。
強化候補 3 件の棄却理由も構造的 (本体不可視 / overkill / 重複) で、Codex 批評で覆る種類のものではない。

# Phase 3 — Triage

- Gap / Partial: 0 件 → Step 1 skip
- Already (強化可能): 3 候補全棄却 (Pass 2) → Step 2 skip

**採用: 0 件。**

# Phase 4 — Plan

分析レポートのみ作成 (本ファイル)。実装プランなし。

## Validation-only Follow-up

drift / stale fact の露出: **なし**。
- `/deep-research` の description は Claude Code platform の組み込み skill で正常
- `references/best-of-n-guide.md` の Cost-Arbitrage 小節は 6/18 absorb で追加済、本記事の手法はそこに既に内包
- `references/multi-agent-coordination-patterns.md` の Generator-Verifier 記述は最新

# 教訓

1. **同一ベンダーの連続マーケ記事パターン**: Kimi.ai が 6/18 と 6/20 で 2 本のマーケ記事を出し、後発は前作の reframing (具体事例追加だけ)。次回 Kimi 記事は Phase 1 でベンダー検出 → reference-only に短絡可 (Cyril 「著者ベース短絡」と同型、`hermes` family と同じ判定)。
2. **`/deep-research` の本体不可視性**: Claude Code 組み込み skill は description のみ可視、SKILL.md 本体に到達できないため editor-style の "強化案" は構造的に成立しない。「組み込み skill の中身を編集して強化」は absorb の強化候補から除外する。
3. **Phase 2.5 dual-degraded 経験**: Codex silent exit + Gemini sunset の同時 unavailable で Opus 自己分析で結論を確定するケースが続いている (今日2件目: Khairallah + Kimi)。self-bias 補正なしのリスクは台帳の `matched_prior` 3点セット立証で代替する。
4. **Saturation-pure-rehash で user が continue を選択する価値**: 結論は変わらないが、台帳の per-method 照合を 1 行ずつ立証する作業自体が drift 検出のチェックポイントになる (今回は drift 0 だったが、6/12 fable5-14steps のように drift 露出する場合もある)。
