---
title: "How to Build An Agentic OS using Fable 5 (Builder's Guide) — absorb analysis"
date: 2026-07-08
source:
  title: "How to Build An Agentic OS using Fable 5 (Builder's Guide)"
  author: unknown (user's notes, edited by Claude Opus 4.8 max)
  url: pasted text
  type: article
status: implemented
family: harness-engineering / multi-agent-orchestration / self-evolving
adopted: 1
validation-only: 1
---

## Source Summary

**主張**: Fable 5 は単体では「高価に impressive な誤りを生む」が、system の中に置けば「1 日 3 ドルで雇える従業員」になる。8 BUILD で CLAUDE.md 憲法 → conductor/worker/verifier ループ → trust ledger → standing goals → budget → optional loops → cron/runbook/30日 trust schedule を積む。

**3 原則**: (1) Laws not tips — 全ルールに number/never/check command (2) Nothing grades its own homework — planner/worker/verifier/gate は 4 者、最後は決定論的 (3) Nothing that passed once goes unwatched — 完了は再検証される invariant に昇格。

**手法 (BUILD 0-8)**: Fable 5 engine config / laws-not-tips CLAUDE.md / contract + deterministic verify.sh / conductor-worker-verifier heartbeat (cheap 三分割) / per-skill trust ledger (20 runs 95% → auto) / standing goals daily re-verify / budget metabolism (cost per tick) / optional loops (quorum/ratchet/sparring/compost) / Makefile + cron + 30日 trust schedule。

## Fact-check (grounding)

Fable 5 の BUILD 0 運用事実 4 件を claude-code-guide agent (WebSearch/WebFetch) で公式 docs 照合 — **全て CONFIRMED**（vendor hallucination ではない）:

| 主張 | 判定 | 出典 |
|------|------|------|
| reasoning_extraction refusal ("show your thinking" が誘発) | **CONFIRMED** | platform.claude.com/.../prompting-claude-fable-5 + refusals-and-fallback |
| refusals are HTTP 200 (stop_reason で判定) | **CONFIRMED** | .../refusals-and-fallback, handling-stop-reasons |
| max_tokens caps thinking + response (high/xhigh は 64k+) | **CONFIRMED** | .../effort, prompting-claude-fable-5 |
| effort low/medium/high/xhigh/max, high=default, Fable low が旧 xhigh 超え | **CONFIRMED** | .../effort |

Gemini は sunset (IneligibleTierError) のため Phase 2.5 は Codex 単独批評 + claude-code-guide grounding。

## Saturation Gate (Phase 1.5)

**判定: PASS (warning)** — harness-engineering / multi-agent-orchestration / self-evolving family。`docs/research/_index.md` grep で **N=17**。family 全体の採用率は ~50% (0 件と 2-4 件が混在) で 20% 閾値超のため PASS。

近接する過去 absorb 3 本と強く重複:
- `2026-06-12-fable5-14steps` — **同じ Fable 5 の self-improving system**。Model Safety Boundary section / verification_status / /goal 行を既に追加済
- `2026-06-14-claude-fable5-system-prompt` — Fable 5 の prose/behavior
- `2026-07-06-dk-devflow-superpowers` — 自己改善ループ

無人 self-improving ship loop は `2026-06-05-sonicgarden` (報酬ハッキング/Goodhart)・`2026-06-14-opik` (注意資源の負債化 + 無人ループ YAGNI を 2 回確定)・`2026-05-31-hermes` (retire 維持が正解) で **3 回却下済**。本記事の novel 機構の多くはこの却下済み loop に結合する。

## Pass 1/2 Judgment (existence + enhancement)

| # | 手法 | 判定 | 既存 / 根拠 |
|---|------|------|------------|
| 1 | DISPATCH テーブル | Already | `model-routing.md` Tier 0-3 (軸が推論深度だが概念同一) |
| 3 | 決定論的 verify gate | Already | `completion-gate.py` (Stop hook → test → 差し戻し) |
| 4 | conductor/worker/verifier 分離 | Already | Review Gate (codex-reviewer + code-reviewer 並列) + Tier0 最終 verify |
| 7 | Budget (cost per tick) | Already | `cost-gate.py` (cycle-cost.json, WARN 5.0/STOP 10.0) |
| 11 | Cron/launchd 自律実行 | Already | daily-health-check + patrol-agent plist |
| 8 | Quorum loop | N/A (意図的却下) | `debate` skill が多数決を明示アンチパターン化。Codex も却下維持支持 |
| 9 | Compost loop (自動版) | N/A (退役済) | `improve-policy.md` 2026-05-03 退役 (false-positive)。後継は手動 promote-learnings |
| 10 | Sparring loop | N/A (install 条件未達) | 記事自身「毎日 code ship する人向け」限定。dotfiles 非該当 |
| 5 | Trust Ledger (per-skill pass-rate) | N/A | governance-levels がカテゴリ単位で承認率昇格。per-skill pass-rate は偽精度 (Codex: サンプル小・失敗要因混在)。qualitative status は auto-triage + governance で既カバー |
| 6 | Standing Goals (daily 再検証) | Already (Codex refine: watchdog-only) | symlink/config/docs/budget は daily-health-check + `task validate-*` + cost-gate で既カバー。新 ledger は instruction DRY 違反 |
| 2 | Laws-not-tips | Partial (意図的設計差) | core-invariants.md は number+never+verify 完備。CLAUDE.md 本体は Progressive Disclosure prose (IFScale 由来) |
| 12 | Refusal (stop_reason) | Partial → 採用 B | platform 側 fallback。無人 claude -p 14 本が exit code 依存 (下記) |
| 13 | reasoning echo 禁止 | Gap → 採用 A | 監査 grep 0 ヒット (現状クリーン)。予防ルール |

## Phase 2.5 (Codex critique)

Codex (gpt-5.5, read-only) の要点:
1. **Standing Goals を一括 N/A は粗い** — 「自動修正なし・daily predicate で drift 報告のみ」の watchdog 版なら単独価値。ただし対象は腐りやすい invariant (symlink/config/budget/stale docs) 限定 → これらは既に daily-health-check + validate-* + cost-gate でカバー済のため **Already に確定**、新 ledger 化は見送り (Pruning-First)。
2. **Trust Ledger per-skill pass-rate は偽精度** — サンプル小 + 失敗要因 (環境 drift/外部 API/要件差) 混在。qualitative status メモなら余地あるが governance-levels + auto-triage が実質カバー → N/A 維持。
3. **reasoning-echo が唯一の明確 Gap** — 低コスト・実害直結で採用支持。Quorum/Compost/Sparring/self-improving loop は「人間主導 harness-engineering」と設計思想衝突で却下維持が妥当。

Codex は私の「却下済み loop 結合」判断を self-bias でなく妥当と追認。

## Adopted (採用 1 件 + validation 1 件)

すべて `references/model-routing.md` への軽量追記 (既存 section へ DRY 統合、新規ファイルなし):

- **A (採用): reasoning-echo 禁止** — Model Safety Boundary section に項目 3 追記。skill/prompt/harness 指示に `show your thinking` 等の reasoning echo を書かない (Fable 5 `reasoning_extraction` refusal 誘発)。CONFIRMED 事実・**予防ルール** (現状違反 0)。
- **B (validation-only, 非採用カウント): stop_reason 判定** — 同 section に項目 4 追記。無人 `claude -p` 14 本が exit code 依存で refusal (HTTP 200) を取りこぼしうる。ただし現行 prompt は reasoning-echo/cyber/bio を含まず発生確率ゼロ → **ハンドラ構築は YAGNI**、認知として記録し「無人ジョブに該当系 prompt を足す時だけ入れる」条件を明記。
- **C (採用): effort 規律** — Stage別 effort 表に「Fable 5 の low/medium が旧 xhigh 超え → worker effort を上げない、high/xhigh は max_tokens 64k+」を追記。

## Rejected / N/A

- Quorum / Compost自動版 / Sparring / Trust Ledger(per-skill) / 無人 self-improving loop — 却下維持 (設計思想衝突 + 3 回却下済 + Codex 追認)。
- Standing Goals ledger 新設 — Already (daily-health-check + validate-* + cost-gate) + instruction DRY。
- Laws-not-tips 全面化 — CLAUDE.md の Progressive Disclosure (IFScale) と意図的にトレードオフ済。

## 教訓

- **N=17 飽和 family の典型的帰結**: 記事は良質だが dotfiles が ~90% 実装済 + 残りは意図的却下。genuine 新規は 1 行 (reasoning-echo 予防) のみ。
- **framing が drift を露出 (validation-only)**: 無人 claude -p の exit-code 依存という silent-failure 表面を露出。ただし発生確率ゼロで YAGNI defer が正解 = 「起こり得ないシナリオへのハンドリングは追加しない」の実践。
- **Fable 5 運用事実は grounding して採用**: reasoning-echo/refusal/max_tokens/effort は全て公式裏付けあり。vendor 主張でも「概念のみ採用・数値は UNVERIFIED」区分せず、この 4 件は docs で CONFIRMED のため確信を持って codify。
- 却下済み無人ループへの結合を skip 根拠にする判断を Codex が self-bias でなく追認 (per-method 照合で rehash 立証済)。
