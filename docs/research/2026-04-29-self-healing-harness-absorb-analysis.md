---
status: active
last_reviewed: 2026-04-29
---

# Self-Healing Agent Harness 記事分析レポート

**日付**: 2026-04-29
**ソース**: "The Self-Healing Agent Harness" by CREAO CTO (Peter Pang, 25 人規模スタートアップ)
**関連**: 同著者の前作「Why Your AI-First Strategy Is Probably Wrong」(2026-04-14 absorb 済み、4 抽象原理を採用)
**分析対象**: 個人 Claude Code dotfiles ハーネス (/Users/takeuchishougo/dotfiles)
**フェーズ**: Extract → Pass1+Pass2 ギャップ分析 → Refine (Codex + Gemini 並列批評) → Triage → Plan

## Phase 1: 記事要点 (Extract)

### 中核主張

Evaluation と QA は同じループであるべき。bad agent response は metric であり bug でもある。grade → triage → fix → verify → gate を一つの harness に統合する。

### 3 components

1. **The Grader**
   - Tri-judge panel (Anthropic + OpenAI + Google) で self-preference bias を相殺
   - out-of-band 評価 (live user latency に影響しない async grading endpoint)
   - 12 domain categorical router で domain 別 rubric 振り分け
   - 5-field schema-locked structured output

2. **The Engineering Pipeline** (6 jobs)
   - Detect → Investigate → Auto-fix → Verify → Re-grade → Report
   - 9-dim severity engine
   - auto-fix guardrails (3 PR/run 上限、`.env` / `.github/` / IAM 触る PR は auto-close)

3. **The Bridge** — AI-gated grey rollout
   - 10 → 20 → 50 → 100% 段階展開
   - score drop ≥ 0.15 で abort、p < 0.05、n = 200

### 2 大教訓

- **Grade outcome not trajectory** — 経路を罰しない。最終結果のみで判定する
- **A score with no ticket means nothing** — Engineering Pipeline なき Grader は無意味

### 16 手法 (本文より列挙)

1. Async grading endpoint
2. Per-model sampling (10% dominant, 100% minority)
3. Categorical Router (12 domain)
4. Tri-judge panel (3 vendor 横断)
5. Schema-locked structured output (5-field)
6. 9-item issues taxonomy
7. Mathematical consensus (averaging)
8. Per-judge persistence + drift audit
9. Periodic human calibration
10. Score → Ticket 6-job pipeline
11. 9-dim severity engine
12. Auto-fix guardrails
13. Telemetry verify
14. Re-grade closed clusters 100% / 24h
15. AI-gated grey rollout
16. Grade outcome not trajectory

## Phase 2: ギャップ分析 (Pass 1: 存在チェック + Pass 2: 強化チェック)

| #  | 手法 | 判定 | 関連ファイル | 要約 |
|----|------|------|--------------|------|
| 1  | Async grading endpoint | N/A | evaluator_metrics.py | personal dotfiles に live user latency 概念なし |
| 2  | Per-model sampling | N/A | trace_sampler.py | live traffic 不在 |
| 3  | Categorical Router | Already (棄却) | triage-router.md | router は分類器、judge ではない (Codex 指摘) |
| 4  | Tri-judge panel | Already (強化採用) | absorb/SKILL.md Phase 2.5 | Opus + Codex + Gemini = 既に 3 family。bias mitigation rationale だけ明記 |
| 5  | Schema-locked output | 棄却 | structured-output-guide.md | 全レビュー schema 化はオーバーヘッド過多 |
| 6  | 9-item issues taxonomy | Already (強化不要) | failure-taxonomy.md | FM-001〜017 で既に richer |
| 7  | Mathematical consensus | N/A | - | judge 数 3 で voting/合議で十分、平均化不要 |
| 8  | Per-judge persistence + drift | Already (強化採用、トーンダウン) | evaluator_metrics.py + evaluator-calibration-guide.md | 自動 ±10pp 監視ではなく「再校正条件」として軽記述 |
| 9  | Periodic human calibration | 棄却 | evaluator-calibration-guide.md | 既存「変更時校正」で十分、儀式化は dead weight |
| 10 | Score → Ticket 6-job | N/A (前回棄却) | - | 2026-04-14 で「自動チケット化は注意資源の負債化」棄却済 |
| 11 | 9-dim severity engine | 棄却 | severity-matrix.md | dimension 数は品質ダイヤルではない |
| 12 | Auto-fix guardrails | Already (強化不要) | graded-guardrails.md + protect-linter-config | 既に hook 化済 |
| 13 | Telemetry verify | 棄却 | observability-signals.md | 既存 verification 文化と重複 |
| 14 | Re-grade closed clusters | Partial (T4-C に派生) | regression-gate.py | 100% / 24h は N/A、harness rule 変更時の re-run のみ採択 |
| 15 | AI-gated grey rollout | N/A (前回棄却) | - | multi-tenant 製品の機能 |
| 16 | Grade outcome not trajectory | Gap (採択) | evaluator-calibration-guide.md | evaluator contract として未明文化 |

### Already 強化チェック (Pass 2)

| #  | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|----|-------------|---------------|--------|------|
| S4 | Codex/Gemini/Opus 3 family review | self-preference bias 存在の rationale 不在 | absorb/SKILL.md Phase 2.5 起動部分に bias mitigation 5 行追記 | 強化可能 |
| S6 | failure-taxonomy.md (FM-001〜017) | 既に richer。記事は 9 項目のみ | 不要 | 強化不要 |
| S8 | evaluator_metrics.py + 校正ガイド | 「再校正をいつ走らせるか」の trigger 条件が暗黙 | 「停止基準」周辺に再校正条件 5 行追加 | 強化可能 |
| S12 | graded-guardrails.md + protect-linter-config | 既に linter config 保護、IAM/.env も範囲内 | 不要 | 強化不要 |

## Phase 2.5: Refine (Codex + Gemini 並列批評)

### Codex 批評の主要指摘

- **「Phase 2 verdict はまだ吸収しすぎ」** — 16 手法のうち多くは N/A 棄却で正解
- **#3 triage-router にカテゴリ別 rubric 追加は棄却** — router は分類器、judge ではない、肥大化リスク
- **#1, #5, #9, #11, #13 はすべて棄却推奨** — 個人 harness で害が大きい
- **#8 drift detection は「自動 ±10pp 監視」ではなく「再校正条件」に留める** — 儀式化禁止
- **#14 「harness rule 変更時に既知 cluster を少数 re-run」は useful** — ただし新 pipeline ではなく既存 regression gate 側に組み込む
- **採択 Top 3 (T1 / T2 / T3) を強く推奨** — 明文化と framing 強化のみ、新規 mechanism は最小

### Gemini CREAO 信頼性検証

- CTO: Peter Pang、25 人規模の小組織
- 「99% AI-written code」「3-8 deploys/day」は **自社主張、独立検証なし**
- 「99%」にボイラープレート (auto-gen schema, migrations) を含む可能性
- 高頻度 deploy は小組織ゆえ可能、エンタープライズ再現性は未検証
- **ベンダーバイアス前提で読む。CREAO の儀式そのまま移植は不適切**

### 前作との対比

- 2026-04-14 で抽出した 4 抽象原理 (観測可能にする / 判断をゲート化する / 批評を成果物にする / 失敗 → capability gap) を既に採用済 (CLAUDE.md core_principles)
- 今回の続編は「具体実装」を提示しているが、その大半は前回 N/A 判定済 (multi-tenant 製品の儀式)
- 採択は「明文化されていない暗黙原則」と「framing 強化」のみで、新規 mechanism 追加は T4-C のみ

## Phase 3: Triage (採択結果)

### 採択 (4 件)

| #    | タスク | ファイル | 規模 | 実行 |
|------|-------|---------|------|------|
| T1   | "outcome over trajectory" 原則明文化 | evaluator-calibration-guide.md | S | 同セッション |
| T2   | model-family diversity (3 vendor) 明示 | absorb/SKILL.md | S | 同セッション |
| T3   | drift 再校正条件 (model/rubric 変更時) | evaluator-calibration-guide.md | S | 同セッション |
| T4-C | regression-suite.json populate + harness 変更時 hook | 複数 (要 plan) | M | 別セッション /rpi |

### 全棄却 (10 件)

| # | 項目 | 棄却理由 |
|---|------|---------|
| 1 | Async grading endpoint | live user latency 概念なし |
| 2 | Per-model sampling | live traffic 不在 |
| 3 | Categorical Router 追加 | router 肥大化リスク (Codex 指摘) |
| 5 | Schema-locked output 全面化 | オーバーヘッド過多 |
| 7 | Mathematical consensus | judge 3 で voting 十分 |
| 9 | Periodic human calibration | 儀式化は dead weight |
| 10 | Score → Ticket 6-job | 前回棄却済 (注意資源の負債化) |
| 11 | 9-dim severity engine | dimension 数は品質ダイヤルではない |
| 13 | Telemetry verify 専用 job | 既存 verification と重複 |
| 15 | AI-gated grey rollout | multi-tenant 製品機能 |

## Phase 4: 統合プラン (概要)

### 同セッション実装 (T1 + T2 + T3, 全 S 規模)

#### T1: Outcome over Trajectory 原則明文化

- **File**: `.config/claude/references/evaluator-calibration-guide.md`
- **Changes**: 冒頭付近に「Outcome over Trajectory」原則を 1 段落追加。「最終 artifact / 観測可能成果のみで評価する。経路 (使ったツール、tool_use 回数、retry 回数) は罰しない。ただし observability 上は記録する」と明記
- **Size**: S

#### T2: Model-family Diversity 明示

- **File**: `.config/claude/skills/absorb/SKILL.md`
- **Changes**: Phase 2.5 の Codex/Gemini 起動部分に bias mitigation rationale を 5 行追記。「Anthropic (Opus) + OpenAI (Codex) + Google (Gemini) の 3 family を意図的に使う。同 family は self-preference bias を相互強化する」
- **Size**: S

#### T3: Drift 再校正条件

- **File**: `.config/claude/references/evaluator-calibration-guide.md`
- **Changes**: 「停止基準」周辺に「再校正条件」を 5 行追加 (model 切替・rubric 変更時、十分な sample 後の trailing avg ズレ、±10pp は初期目安として記載するが automation はしない)
- **Size**: S

### 別セッション実装 (T4-C, M 規模)

詳細プランは `docs/plans/active/2026-04-29-self-healing-absorb-plan.md` 参照。

- **目的**: regression-suite.json の populate と、harness rule (skill / hook / agent contract) 変更時に既知 cluster を少数 re-run する hook 接続
- **対応する Codex 抽象原理**: 失敗を capability gap として durable artifact に変える
- **Size**: M (複数ファイル、検証含む)

## 参照

- 前作: `docs/research/2026-04-14-creao-ai-first-analysis.md` (4 抽象原理採用)
- 前作プラン: `docs/plans/2026-04-14-creao-absorb-plan.md`
- Codex 批評全文: セッション内取得、外部保存なし
- Gemini 信頼性検証: セッション内取得、外部保存なし

## 注記

- 採択 4 件のうち 3 件 (T1/T2/T3) は明文化と framing 強化のみで、新規 mechanism は追加しない (Pruning-First 原則)
- T4-C のみ新規 mechanism (regression hook) だが既存 regression-gate.py の延長
- 16 手法中 10 件全棄却は「個人 dotfiles では CREAO の企業儀式は害になる」という Codex 抽象原理の貫徹
