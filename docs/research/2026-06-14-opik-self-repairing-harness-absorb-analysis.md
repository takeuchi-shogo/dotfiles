---
date: 2026-06-14
status: light-phase2-only
adoption: 0
operation: validation-only (stale-plan audit + dead-code flag)
family: self-evolving / self-healing-harness (N>=13)
saturation: PASS (warning) — 高採用率ファミリだが本記事は全手法 rehash
source:
  - https://x.com/_avichawla/status/2065727218991735000 (Avi Chawla, Karpathy "loop engineering" 引用)
  - "Your Agent Harness Should Repair Itself" (Comet ML / Opik, vendor article)
---

# Opik Self-Repairing Harness + Karpathy Loop Engineering 分析レポート

**フェーズ**: Extract → Saturation Gate (per-method delta ledger) → Validation-only Follow-up
**取得経路**: 記事全文が会話内に貼付済 (WebFetch 不要、引用 faithfulness 確保)
**結論**: 採用 0。全 12 手法が named prior で rehash。記事 framing が `/improve` 退役 orphan (regression-gate.py + T4-C plan) を露出 → 退役処理。

## Phase 1: 記事要点 (Extract)

### 主張
エージェントは「ループエンジニアリング」(schedule + maker loop + 独立 checker + disk state + 明示的 exit) で自走させ、さらにハーネス自体が観測トレースから自己修復 (trace→診断→修正→exact failing input で検証→regression test として固定) すべき。

### 手法 (12)
1. Loop engineering: scheduler / maker loop / separate checker / disk state
2. Separate checker (not self-grading) — findings を maker に返す
3. Exit conditions before loop (done / max-iter / budget)
4. State on disk not context (MD/knowledge graph, resumable)
5. Verification bar → loop safety (mechanical = safe, judgment = checker 依存)
6. Failure mode: green-but-unread (someone must read merges)
7. Failure mode: harness drift as models change
8. Self-repairing harness: trace → diagnose → fix → verify against exact input → lock regression
9. Observability → action gap (trace shows what, not why/how-to-fix)
10. Plain-English assertions / LLM-as-judge tests
11. Failures become regression tests (grow suite from prod failures)
12. Agent sandbox (test harness changes before shipping)

Opik 記事は本質的に observability 製品 (Opik/Comet ML) の vendor pitch。"Ollie" coding agent / "Test Suites" / "Agent Sandbox" は製品機能。概念核 (loop engineering + self-repair) は dotfiles で飽和。

## Phase 1.5: Saturation Gate — per-method 照合台帳

family: self-evolving / self-healing-harness、N>=13 (`docs/research/_index.md`)。採用率 >=20% (sonicgarden 2 / fable5 3 / self-healing 4 / ralph-loop 5) → **PASS (warning)**。最も直接的な prior:
- `2026-04-02-ralph-loop-harness-engineering-analysis.md` = loop engineering 丸ごと
- `2026-04-29-self-healing-harness-absorb-analysis.md` (CREAO) = self-repair 丸ごと (同ジャンル・同種ソース)

| # | 手法 | verdict | matched_prior (ファイル名 + 引用句 + 同等性理由) |
|---|------|---------|------------------------------------------------|
| 1 | Loop engineering | rehash | `2026-04-02-ralph-loop` "while true ループ + レビューア Agent が品質基準まで自動修正" + completion-gate.py / AutoEvolve 4層。ループ構造そのものが同一 |
| 2 | Separate checker (not self-grading) | rehash | `2026-04-02-ralph-loop` "Sycophancy/false completion 防止" + `2026-04-29-self-healing` "Tri-judge で self-preference bias 相殺"。異種モデル checker = Codex Review Gate と同一 |
| 3 | Exit before loop (done/max-iter/budget) | rehash | `2026-04-02-ralph-loop` "`--completion-promise COMPLETE` + `--max-iterations 100`" + /loop & Workflow budget。明示的 exit 条件と同一 |
| 4 | State on disk not context | rehash | `2026-04-02-ralph-loop` "`.temp/review-feedback.md` 永続化で次イテレーション引継ぎ" + checkpoint/HANDOFF.md / patterns.jsonl。disk state と同一 |
| 5 | Verification bar → loop safety | rehash | `project_self_improving_loop_yagni` "全139件 mechanical 0/advisory 129 → 無人PR は YAGNI" + auto-triage mechanical/advisory 分類。"低検証=安全に loop 可" の同一結論 |
| 6 | Failure: green-but-unread | rehash | `2026-06-05-sonicgarden` YAGNI (無人マージを退けた根拠) + human-in-loop core principle。"human must read merges" と同一 |
| 7 | Failure: harness drift | rehash | `references/harness-stability.md` + change-surface-matrix.md + `feedback_model_fable_classifier_outage` (model drift で classifier 死亡)。harness drift と同一 |
| 8 | Self-repair: trace→fix→verify exact input→lock regression | ambiguous→rehash | TDD "reproduce-then-fix" + failure-escalation-protocol (Issue+worktree escalate) で概念カバー。**ただし自動 regression-lock 機構 = 死蔵** (下記 Validation-only) |
| 9 | Observability → action gap | rehash | `error_analysis_integration.md` + observability-signals.md + error-to-codex hook (post_bash.rs)。"trace shows what not why" → 診断 hook で同一 |
| 10 | Plain-English assertions / LLM-as-judge | rehash | review agents (LLM-as-judge) + validate skill + Codex Gate。assertion-based eval と同一 |
| 11 | Failures → regression suite | rehash | #8 と同じ (self-healing T4-C)。failure→test の同一概念 |
| 12 | Agent sandbox | rehash | worktree isolation + spike skill + harness-stability 30日評価。harness 変更を ship 前に隔離検証で同一 |

**delta = 0** (採用候補なし)。手法8の ambiguous は「概念カバー済 + 機構は死蔵」で rehash に確定。

## Validation-only Follow-up — 記事 framing が露出した死蔵

手法8 (self-repair → regression-lock) の検証中に、self-repair 機構が `/improve` 退役 orphan と判明:

| 対象 | drift 内容 | 訂正方針 (実施済) |
|------|-----------|------------------|
| `docs/plans/active/2026-04-29-self-healing-absorb-plan.md` | T4-C (regression-suite populate + harness hook) が `status: active` で放置。上流 /improve (retire 2026-05-03) 依存で孤立、eval-generator wiring 未完 | `status: superseded` + completed/ へ移動 |
| `scripts/eval/regression-gate.py` | docstring "Regression Gate for /improve Adversarial Phase"。regression-suite.json 未生成 → suite 不在時 silent-skip (NO-OP)。live caller ゼロ | decommission-log に flag (2026-07-14 評価)。隣接 orphan run_reviewer_eval.py / eval-generator.py / improve-policy.md 図も同 cluster として併記 |
| `docs/research/2026-04-29-self-healing-harness-absorb-analysis.md` | frontmatter `status: implemented` だが実際は T1/T2/T3 のみ、T4-C 未実装 | `status: partially-implemented` に訂正 + T4-C superseded 注記 |

**capability gap (実在だが非採用)**: dotfiles は「再発した失敗の exact input を恒久 regression case として捕捉する」自動機構を持たない。T4-C がこれを狙ったが /improve 退役で孤立。過去2回「注意資源の負債化」と判定 + sonicgarden で無人ループ YAGNI 確定済のため、revive せず退役を選択 (ユーザー判断 2026-06-14)。手動 TDD reproduce-then-fix + failure-escalation で代替。

## 教訓

- multi-agent-orchestration / self-evolving family は「何度 absorb しても deliberate non-adopt」を再確認 (MEMORY family-level lesson 通り)。loop engineering / self-repair の vendor 記事は概念核が全て既存。
- 採用 0 でも価値あり: 記事 framing (self-repair の headline) が眠った orphan plan + dead code を再浮上させ、stale-plan audit を駆動した (validation-only follow-up)。
- "platform drift validation" と "article-backed novel instruction" を分離。本件は前者のみ。
