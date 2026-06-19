---
title: "How to Build Claude Subagents Better Than 99% of People (Jey) — absorb 分析"
date: 2026-06-20
status: light-phase2-only
family: multi-agent-orchestration / subagent
source:
  author: Jey
  type: playbook post
saturation: SATURATED-trending
adopted: 2
---

# How to Build Claude Subagents Better Than 99% of People (Jey)

/ absorb の light-phase2 分析。記事は subagent 構築の入門ベストプラクティス 20 項目。

## Saturation Gate (Phase 1.5)

- **Family**: `multi-agent-orchestration / subagent`
- **N**: 9 (grep ベース。Kimi K2.6 2026-06-18 / Hermes VPS 2026-06-17 を含め実質 N≈14)
- **採用率**: 形式上 ≥ 20% で PASS。だが **Step 4.5 trend ガード発火** — 直近 2 件 (Kimi K2.6, Hermes VPS) が連続でほぼ採用 0 → **SATURATED-trending**
- **delta = 3** (ambiguous: #7 YAML quote / #9 agent injection scan / #10 max_turns)。20 手法中 17 が名指し rehash
- **判定**: ユーザー選択で `light-phase2` (delta_methods 3 件のみ Phase 2 検証)

## per-method 照合台帳 (全 20 手法)

rehash として delta から除外した分も `excluded as rehash` で matched_prior を残す。

| # | 記事の手法 | verdict | matched_prior |
|---|-----------|---------|---------------|
| 1 | clean/isolated context (22.8K→数行) | excluded as rehash | `subagent_patterns.md` + `2026-06-03-dynamic-workflows` context isolation |
| 2 | fleet economics・model routing | excluded as rehash | `references/model-routing.md` Tier 表 + MEMORY「モデル階層の徹底」|
| 3 | general-purpose を 5 通り prompt = 5 persona | excluded as rehash | `agent-harness-contract.md` + Explore/Plan/general-purpose built-in |
| 4 | custom subagent = `.claude/agents/` の MD+YAML | excluded as rehash | `.config/claude/agents/*.md` 実体 |
| 5 | description = trigger (progressive disclosure) | excluded as rehash | MEMORY「Progressive Disclosure 設計」+ `30-subagents` agent-design-lessons |
| 6 | description は短く保つ | excluded as rehash | MEMORY skill listing budget (PR#70) + IFScale |
| 7 | YAML quote 閉じ忘れで trigger silent 死 | **ambiguous → 検証** | validate-agents.sh が frontmatter 構文を検証するか未確認 |
| 8 | read-only を tools 層で強制 | excluded as rehash | 既存 agents `tools:` 制限 + PostHog Capability Restriction |
| 9 | DL した他人の agent file を verifier で injection scan | **ambiguous → 検証** | `skills:verify` は hash 整合のみ。内容 scan は別物の可能性 |
| 10 | max_turns で runaway を cap | **ambiguous → 検証** | Workflow 総数上限はあるが個別 subagent max_turns は未活用 |
| 11 | model をタスクに合わせる (per-agent field) | excluded as rehash | #2 と同じ `model-routing.md` |
| 12 | 4 つの起動経路 (Automatic/Proactive/Explicit/Direct) | excluded as rehash | 既存 agents の "Use PROACTIVELY" 多用 |
| 13 | project-level vs global agent | excluded as rehash | MEMORY「Skill scope 判断」同一原則 |
| 14 | skill と subagent は compose | excluded as rehash | `skillnet_integration.md` + MEMORY「skill=知識/agent=実行」|
| 15 | dynamic workflow で swarm (3/40/210) | excluded as rehash | **Workflow tool = deliberate non-adopt** (`2026-06-03-dynamic-workflows`) |
| 16 | 2 回やったら specialist 化 | excluded as rehash | core principle「2回説明したら書き下ろせ」+ DRY 3回 |
| 17 | independent+disposable/repeated は委譲 | excluded as rehash | `subagent-delegation-guide.md` + `superpowers:dispatching-parallel-agents` |
| 18 | subagent 同士は会話不可 (協調は agent-teams) | excluded as rehash | `multi-agent-coordination-patterns.md` Agent Teams + MEMORY「TaskList 空問題」|
| 19 | orchestrator だけが user と話す | excluded as rehash | `feedback_explore_subagent_bash_limit.md` + Hermes Nested Orchestrator N/A |
| 20 | fresh-context reviewer で sycophancy 回避 | excluded as rehash | MEMORY「Claude=Sycophancy」+ security-reviewer Blind-first + absorb Phase 2.5 |

## Phase 2 判定 (delta_methods のみ、Pass 1 Sonnet Explore → Pass 2 Opus)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 7 | YAML quote 検証 | **Partial → 採用** | yamllint/pyyaml ゼロ。validate-agents.sh は awk 簡易パースで unclosed quote 検出不可 |
| 9 | 外部 install agent の injection scan | **Already + 外部パス配線 Gap → 採用** | `skill-security-scan.py` (arXiv G1/G2) は記事超え。自作/手動 checklist には配線済だが外部 install パス未配線 |
| 10 | max_turns runaway cap | **Already (N/A)** | `check_doom_loop` + `check_exploration_spiral` + `stagnation-detector.py` の 3 系統。soft intervention は意図的設計 |

Phase 2.5 (Codex/Gemini) は light flag で省略。#9 は grep で客観確認済み (self-bias リスク低)。

## one-shot security scan の実測 (#9 検証で副次的に判明)

`skill-security-scan.py` を全 121 skill に走らせた結果:

- **14 FAIL / 121 だが全て false positive / 良性**
  - VeriGrey `autonomy-emphasis` (salesforce-rest-api 12, absorb, review 等) — 正規の `proactively/autonomously` 文言を injection と誤検知
  - `subprocess.*` (gh-fix-ci 等) — 正当な CI/API 呼び出し
  - skill-creator CRITICAL — 自作 `scripts/aggregate.py:439` の `eval()` (外部脅威でない)
- **skills-lock.json の外部 64 skill で CRITICAL = 0** → 供給網 clean を確定
- **発見**: scanner の G2 VeriGrey / G1 subprocess は HIGH FP が多く、そのまま gate 配線すると正規 install を全ブロックする

→ この実測が当初の「#9継続: skills:verify にそのまま配線」案を覆し、**CRITICAL-only gate** に修正した。

## 採用 (2 件)

### #9: 外部 install agent への CRITICAL-only injection scan を配線

- `skill-security-scan.py` に `--critical-only` フラグ追加 (HIGH=VeriGrey/subprocess FP を除外、CRITICAL のみ block)
- `scripts/runtime/skill-hash-verify.sh` の外部スキル列挙ループに CRITICAL-only scan を相乗り (hash 検証と同時)。`security_fail` をカウントし exit code に反映
- 対象は skills-lock.json の外部スキルのみ → 自作 skill-creator (eval CRITICAL) は対象外で FP 回避
- 検証: skill-creator (CRITICAL)=block / salesforce (HIGH only)=pass / lock 64 skill CRITICAL=0 で clean 通過

### #7: agent frontmatter の YAML 構文検証 (Check 0)

- `validate-agents.sh` に ruby (psych 標準、依存ゼロ) による frontmatter YAML.load チェックを追加
- unclosed quote 等の構文エラーで WARN。pyyaml 不在環境のため ruby を採用 (ruby 不在なら graceful skip)
- 検証: 既存 21 agents で誤検出ゼロ (WARN 0)

## 非採用

- **#10 max_turns**: doom_loop + exploration_spiral + stagnation の 3 系統でカバー済。soft intervention は意図的設計 (hard kill は正当な長時間作業も殺す)。N/A
- **#1-6, #8, #11-20 (17 手法)**: 全て名指し rehash (台帳参照)

## 教訓

- subagent family は採用率では PASS でも trend ガードで拾える典型。delta=3 の ambiguous は light-phase2 で「2 件は配線 drift / 1 件は意図的設計」に分離できた
- 記事 #9 (入門 tip) を実装しようとして、既存 capability (`skill-security-scan.py`) の **install パス配線 drift** + **scanner の FP 品質問題** の両方が露出した。article-backed adoption と platform drift validation の合わせ技
