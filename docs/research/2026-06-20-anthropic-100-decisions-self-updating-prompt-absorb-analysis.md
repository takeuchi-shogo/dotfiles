---
date: 2026-06-20
status: adopt-0
family: self-evolving
source_title: "How to Make Claude's Prompt Update Itself After Every 100 User Decisions"
source_author: "Nick Mayhew (Anthropic) on stage, recruiting context"
source_url: paste-only
phase: full-workflow (Phase 1.5 SATURATED-pure-rehash で skip 提示 → user continue 選択 → Pass 2 で adopt 0 確定)
---

# Self-Updating Prompt (100 User Decisions) Absorb Analysis

## Source Summary

Anthropic 顧客の recruiting 事例 (2,740 件/日応募) を題材に「prompt を config ではなく apprentice として扱い、100 ユーザー決定ごとに背後で書き換える」設計を提唱する blog 風記事。

主張 4 点:
1. Markdown prose prompt (rule-based / weighted rubric ではなく自然言語の散文)
2. 100-200 decision batch update (毎回ではない、1 件はノイズ・100 件は signal)
3. Two-layer split (Haiku evaluator hot path + smart apprentice rare batch)
4. Feedback loop as product (ユーザーは判断のみ、prompt は背後で進化)

## Phase 1.5 Saturation Gate

- family: self-evolving / self-improving prompts
- N: 21+ (実ファイル列挙、`docs/research/_index.md` 索引で N≥10 確認、6/18 + 6/20 Kimi 二件 + 6/20 loop-engineering 二件で連続 adopt 0)
- 直近 3 件採用率: 0/3 (2026-06-20 loop-engineering double-source / 6-20 essay / 6-20 Kimi K2.6 self-verifying)
- delta: 0 (全 5 手法 rehash、matched_prior 名指し成立)

### per-method 照合台帳

| current 手法 | verdict | matched_prior (3 点セット) |
|--------------|---------|---------------|
| Markdown prose prompt | rehash | `2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md` "text-space optimizer (OPRO 系)" — skill markdown を直接書き換える設計、dotfiles 全 skill/agent/CLAUDE.md が同型 |
| Batch decision update ~100 件 | rehash | `2026-06-05-recursive-self-improvement-anthropic-absorb-analysis.md` A=`scripts/learner/calibration-verdict-logger.py` 実装 — auto-triage 人間裁定 agree/disagree を batch 記録、agreement rate=個人版 Mythos、同じ「batch で signal を貯めて判定」設計 |
| Two-layer split (Haiku evaluator + smart apprentice) | rehash | `references/model-routing.md` 4-tier 階層 + `2026-06-02-skillopt-...md` objective-lane (verifiable) vs subjective-lane (judgment) 分離、記事の cheap evaluator / smart apprentice と同型 |
| Human decision logging | rehash | `2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md` patterns.jsonl + session_events、`scripts/lib/session_events.py:417` emit_review_feedback、`scripts/learner/calibration-verdict-logger.py:78` log_verdict — 記事の decision pile と同じ蓄積層 |
| Feedback loop as product (背後で進化) | rehash | `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md` learned 昇格ループ設計 + `2026-06-05-sonicgarden-...md` Wave3 YAGNI 確定 (mechanical 0/139) で「完全無人 prompt 更新は判断系で fail」を実証済 |

判定: **SATURATED-pure-rehash** (delta=0)
user 選択: continue (フル workflow)

## Phase 2 Pass 1 (Sonnet Explore) 結果

| # | 手法 | verdict | 立証ファイル |
|---|------|---------|------------|
| 1 | Markdown prose prompt | exists | CLAUDE.md, agents/code-reviewer.md:1, agents/security-reviewer.md:1, skills/promote-learnings/SKILL.md, scripts/runtime/nightly/run-learned-promote.sh:86 |
| 2 | Batch decision update ~100 件 | partial | scripts/learner/calibration-verdict-logger.py:117 (--last N), scripts/runtime/promote-patterns.py:35 (WINDOW_DAYS=30), references/evaluator-calibration-guide.md:111 (~100 ラベル例ガイド) |
| 3 | Two-layer split | exists | references/model-routing.md:14 (4-tier), :140 (Haiku grader 境界), agents/security-reviewer.md:5 (opus), agents/code-reviewer.md:5 (sonnet) |
| 4 | Human decision logging | exists | scripts/lib/session_events.py:417 (review-feedback.jsonl), :436 (review-findings.jsonl), scripts/learner/calibration-verdict-logger.py:78 (triage-calibration.jsonl), scripts/learner/findings-to-autoevolve.py:75 (FP 除外), references/benchmark-dimensions.md:31 |
| 5 | Feedback loop as product | partial | scripts/runtime/nightly/run-learned-promote.sh:1 (PR ゲート merge-coupled), scripts/autoevolve-runner.sh:66 (退役), references/autoevolve-artifacts.md:1 (DEPRECATED 2026-05-03), skills/auto-triage/SKILL.md:19 (Wave3 未着手), commands/improve.md:119 (Phase C 必須) |

## Phase 2 Pass 2 (Opus) — 強化判断

### 手法 2 (Batch decision update) — 強化不要
- 既存: `--last N` 窓 + `WINDOW_DAYS=30` + 「~100 ラベル例」ガイド既存
- 記事原文の specific 提案: 「100 decisions = signal」(author 経験則、数値根拠なし)
- 反論: (a) dotfiles 1 人運用は 100 decisions/day も貯まらない → 件数閾値より時間窓が現実的 (b) ガイドに既に明記 (c) SkillOpt「判断系の自動最適化は block」境界に抵触

### 手法 5 (Feedback loop as product) — 強化不要 (意図的 reject)
- 記事の core claim は「完全無人 prompt 自動更新」= dotfiles 確定的 reject 方針と逆方向
- autoevolve 2026-05-03 retire (認知負荷 > 価値)、sonicgarden Wave3 YAGNI 確定、RSI governance frontier で「ガバナンスはループ設計に統合」採用済
- 記事をそのまま採用したら退役判断を踏み戻すことになる

## Phase 2.5 Refine — Codex 批評統合

Codex (gpt-5.5, medium effort) で 480s bounded timeout で起動、応答取得成功。Gemini は IneligibleTierError (sunset) で skip。

Codex 指摘:
1. partial の扱いはやや甘い — 手法 2 は Gap 寄り (集計器あるが「100 件到達の節目」が無い)
2. 手法 5 は Gap 寄りだが retire / Wave3 YAGNI が強い反証で adopt 不要妥当
3. recruiting 2,740 件/日と個人 dotfiles の差分処理は妥当
4. 見落としリスク = 「軽量な手動月次 calibration」程度。完全自動進化は不要
5. 採用 0 は概ね妥当

修正テーブル:
- 手法 2: partial → Already (borderline、Codex の「月次 calibration ceremony」borderline 候補は Phase 3 で user 判断)
- 手法 5: partial → Already (意図的 reject)

## Phase 3 Triage — user 判断

唯一の borderline 候補「月次 calibration review ceremony」(calibration-verdict-logger.py stats を cron で月次出力し agreement rate trend を briefing に含める) → **skip 推奨を user が確定**

理由: stats CLI 手動起動で十分、cron 追加は YAGNI、ponytail: speculative need。

## Phase 4 Plan

空 (adopt 0)。実装タスクなし。

## 教訓

1. **self-evolving family は完全 saturated**: N=21+、直近 6/20 三連続 adopt 0。次回 Phase 1 で「self-update / apprentice / 100 decisions / feedback loop is product」keyword 検出時は即 saturation gate skip テンプレ送付可
2. **vendor blog 風記事 (Anthropic 顧客事例 framing) は per-method 照合台帳が綺麗に書ける = 全 rehash の典型サイン**: 著者経験則の数値 (100 decisions) を「signal」と称するが calibration 根拠なし、SkillOpt/sonicgarden で既に「判断系の自動最適化は block / 完全無人は YAGNI」確定済
3. **drift 露出なし**: 検証中に dotfiles 内 stale fact / 死蔵 plan は露出しなかった。autoevolve は明示的に DEPRECATED 記録あり、Wave3 は SKILL.md で未着手と明記。validation-only follow-up なし

## Source

paste-only (URL なし、本文ペースト)。Nick Mayhew (Anthropic) on stage 発言の blog 風記事化。
