---
title: "MUSE-Autoskill: Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation — absorb analysis"
date: 2026-06-05
source:
  type: paper
  arxiv: "2605.27366"
  authors: "Huawei Lin, Peng Li, Jie Song, Fuxin Jiang, Tieying Zhang"
  url: "https://arxiv.org/abs/2605.27366"
status: light-phase2-only
family: self-evolving-skills (de-facto, N>=7, taxonomy 未登録)
saturation: SATURATED-but-novel (delta=4, novel=1 ambiguous=3)
adopt_count: 0
operation: ingest-skip (light Phase 2, adopt=0)
---

# MUSE-Autoskill — absorb analysis (light Phase 2, adopt=0)

## Source Summary

LLM エージェントが **スキルを使い捨て生成物ではなく「長命で進化する資産」として lifecycle 管理する** training-free フレームワーク。5段階 lifecycle (Creation / Evaluation / Management / Memory / Refinement)。核心の novelty は **skill-level memory** (`.memory.md` をスキル毎に sibling 配置し、失敗モード・入力の癖・教訓を invocation 横断で蓄積、ロード時に SKILL.md と並べて自動 surface)。SkillsBench (51/94 task, GPT-5.5) で自動生成スキルが生成成功 35 task 上 87.94% (人手スキル天井 68.40% 超)、cross-agent transfer で Hermes が人手スキルとの差の 79% を closure。ボトルネックは skill 生成品質ではなく Phase1 baseline 解決能力。

## Saturation Gate (Phase 1.5)

- 登録 taxonomy のキーワード閾値は未達 (skill-graphs / harness-engineering いずれも不成立) だが、de-facto で "self-evolving-skills / AutoEvolve" クラスタが N>=7 存在 (self-evolving-claude-code 3/30, subconscious-agent-self-improve 4/04, alphaevolve-autoevolve 4/07, asi-evolve-autoevolve 4/08, skill-eval-self-improving-loop 4/09, skillopt-self-evolving-skills 6/02, ai-tech-researcher-self-evolving 6/04)。
- 論文 (academic, 定量機構あり) のため blog listicle 飽和とは質が異なる。delta 計算で判定。
- 判定: **SATURATED-but-novel** (delta=4) → ユーザー選択 **light-phase2** → #2 で Gap 検出も **掘り下げない (adopt=0)** で確定。

## per-method 照合台帳 (全 current 手法、rehash 除外分も保持)

| # | MUSE 手法 | verdict | matched_prior (3点 / Pass2 判定) |
|---|---|---|---|
| 1 | 5段階 skill lifecycle (create/eval/manage/memory/refine) | excluded as rehash | `memory/autoevolve_details.md` の「4層ループ: セッション→日次→BG→/improve、master直変禁止・1サイクル最大3ファイル」+ create/refine/prune/merge を AutoEvolve がカバー |
| 2 | **Skill-level memory (`.memory.md` per-skill sibling、経験を invocation 横断で蓄積・co-located surface)** | **novel → Gap** | 対応物を名指しできない。dotfiles memory は 3-scope (user/project/local) で agent/session 単位。**Pass1=partial, Pass2=Gap (価値は要議論)**: topic-keyed feedback_*.md で per-skill 経験は実質蓄積済、差は「スキル invocation 時に co-located 自動 surface」する配線の有無。single-user harness では cost/benefit 薄く **adopt=0** |
| 3 | Test-gated skill registration (`tests/` 失敗で登録ブロック) | ambiguous → **N/A** | `skill-audit` の A/B eval に隣接するが登録時 unit-test gate は名指し同等でない。**Pass1=not_found, Pass2=N/A (文脈不一致)**: MUSE は runtime 自動生成のため必須、dotfiles は human-authored + skill-creator/skill-audit/Codex Review Gate で作成時にゲート済 → runtime 生成がなく不要 |
| 4 | Progressive-disclosure catalog 注入 (name+desc のみ、コスト一定) | excluded as rehash | `memory/feedback_claudemd_length.md` + CLAUDE.md→references→rules の Progressive Disclosure 設計 + skill description catalog で同等 |
| 5 | Transfer-excludes-memory (leading-dot で published surface 外、転移で経験を持ち越さない) | ambiguous → **Already (アーキで自動達成)** | **Pass1=partial, Pass2=Already**: MUSE が leading-dot で達成する分離を、dotfiles は memory が `agent-memory/` の別 namespace にあり skills-lock.json 配布対象 (スキルディレクトリ) に構造的に最初から含まれないことで無料で得ている |
| 6 | Context compression L1/L2 (oversized turn 書換 / node merge) | excluded as rehash | `references/context-constitution.md` P3 (PreCompact flush + PostCompact verify) + output-offload hook で同等 |
| 7 | Source-trajectory coupling overfit lesson (hvac 80%→20%、単一 trajectory 蒸留が noise に過適合) | ambiguous → **Already (強化不要)** | **Pass1=exists, Pass2=Already**: improve-policy.md Rule 40/47 (holdout 分割) + `anti-goodhart-checklist.md` Rule 43 + SkillOpt 分析 (判断系の単一 trajectory 蒸留を block) で完全カバー |

delta_methods = #2 (novel), #3 #5 #7 (ambiguous)。delta=4。

## Pass 2 判定サマリ

| # | 手法 | 最終判定 | 採用 |
|---|---|---|---|
| 2 | Skill-level memory | Gap (価値は要議論) | ✗ (adopt=0、ユーザー判断) |
| 3 | Test-gated registration | N/A (文脈不一致) | ✗ |
| 5 | Transfer-excludes-memory | Already (アーキで自動達成) | ✗ |
| 7 | Source-trajectory overfit | Already (強化不要) | ✗ |

## Decision (adopt=0)

実質候補は **#2 skill-level memory** の1件のみ。これは「single-user harness で topic-keyed feedback memory を per-skill co-located 化する価値があるか」という設計判断。現状 `feedback_*.md` (topic-keyed) で per-skill 経験は既に蓄積され、co-located 自動 surface の配線コストに見合う効果が薄いと判断し **掘り下げない (Pruning-First 準拠)**。Phase 2.5 (Codex+Gemini) は light flag で省略。

## 残す洞察 (採用はしないが記録価値あり)

- **MUSE が設計努力で達成する 2 点を dotfiles はアーキで無料取得**: (a) transfer-excludes-memory は memory が別 namespace (`agent-memory/`) ゆえ skills-lock.json 配布に構造的に非混入、(b) overfit 警告は holdout/anti-goodhart/SkillOpt で先行カバー。
- **唯一の真の delta は skill-level co-located memory**。将来 skill 数がさらに増え、特定スキルの失敗モードが MEMORY.md 注入で surface しきれなくなった場合に再検討する候補 (現時点は時期尚早)。
- **論文の meta 洞察 "ボトルネックは skill 生成品質ではなく baseline 解決能力"** は AutoEvolve の改善対象選定に通底する (生成機構より素の能力に投資)。これは既存方針と整合し新規アクション不要。
