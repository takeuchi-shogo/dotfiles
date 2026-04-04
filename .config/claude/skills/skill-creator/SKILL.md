---
name: skill-creator
description: >
  Create new skills, modify and improve existing skills, and measure skill performance.
  Use when users want to create a skill from scratch, edit, or optimize an existing skill,
  run evals to test a skill, or benchmark skill performance.
  Triggers: 'skill-creator', 'スキル作成', 'create skill', 'スキル改善', 'skill eval', 'スキルのテスト'.
  Do NOT use for: スキル一括監査（use /skill-audit）、AI ワークフロー監査（use /ai-workflow-audit）。
metadata:
  pattern: pipeline+inversion
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Use the `eval-viewer/generate_review.py` script to show the user the results for them to look at, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Then after the skill is done (but again, the order is flexible), you can also run the skill description improver, which we have a whole separate script for, to optimize the triggering of the skill.

Cool? Cool.

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. If you haven't heard (and how could you, it's only very recently that it started), there's a trend now where the power of Claude is inspiring plumbers to open up their terminals, parents and grandparents to google "how to install npm". On the other hand, the bulk of users are probably fairly computer-literate.

So please pay attention to context cues to understand how to phrase your communication! In the default case, just to give you some idea:

- "evaluation" and "benchmark" are borderline, but OK
- for "JSON" and "assertion" you want to see serious cues from the user that they know what those things are before using them without explaining them

It's OK to briefly explain terms if you're in doubt, and feel free to clarify terms with a short definition if you're unsure if the user will get it.

---

## Workflow

### 1. Capture Intent, Quality Gate, Write SKILL.md

Read `instructions/capture-and-write.md` for the full procedure:

- **Capture Intent**: Understand purpose, category, triggers, output format, success criteria
- **Quality Gate**: Recurrence / Verification / Non-obviousness / Generalizability
- **Pattern Selection**: Choose from pipeline, inversion, reviewer, generator, tool-wrapper
- **Interview and Research**: Edge cases, formats, dependencies
- **Write the SKILL.md**: Frontmatter, pattern-aware scaffolding, critical rules
- **Workflow Spec Checklist** (skillify パターン — 各スキルに以下の6要素が揃っているか確認):
  1. **Goal** — trigger / when_to_use が明確か
  2. **Inputs** — 引数と前提条件が定義されているか
  3. **Ordered Steps** — 手順が順序立てて記述されているか
  4. **Success Criteria** — 各ステップの完了条件が明示されているか（最重要）
  5. **Human Checkpoint** — ユーザー判断が必要なポイントが特定されているか
  6. **Hard Rules** — NG パターン / Anti-Patterns が記述されているか
- **5D Quality Check**: Safety / Completeness / Executability / Maintainability / Cost-awareness
- **Anti-Patterns**: Recommend including an Anti-Patterns section
- **Security Scan**: Run `skill-security-scan.py` before testing

### 2. Skill Writing Guide

Read `instructions/skill-writing-guide.md` for guidance on:

- Anatomy of a skill (directory structure)
- Progressive Disclosure (3-level loading)
- Skill Writing Principles (7 principles, see `references/skill-writing-principles.md`)
- Domain organization, Principle of Lack of Surprise
- Writing patterns and style

### 2.5. Skill Refinement Debug Runs (Meta-Harness Tip)

本番テスト前に、3-5回の短いデバッグランで Skill テキスト自体を精錬する:

1. **2-3個のシンプルなテストケース** で Skill を実行する（本番テストセットではない）
2. **出力を観察**: Skill の指示がどう解釈されたか、意図と乖離がないか確認
3. **Skill テキストを修正**: 曖昧な表現、不足している制約、過剰な指示を調整
4. **3-5回繰り返す**: Skill テキストが安定するまで（出力の質が一貫するまで）

これは Step 3 の本番テストとは別のフェーズ。ここでは Skill テキストの品質を上げることが目的で、出力の品質評価は Step 3 以降で行う。

> 根拠: Meta-Harness (Lee+ 2026) 実装 Tips — "Run a few short debug runs (3-5 iterations) specifically to refine the skill before committing to a full run"

### 3. Testing and Evaluation

Read `instructions/testing-evaluation.md` for the full test/eval pipeline:

- **Test Cases**: Draft 2-3 realistic prompts, pattern compliance check
- **Step 1**: Spawn with-skill AND baseline runs in parallel
- **Step 2**: Draft assertions while runs are in progress
- **Step 3**: Capture timing data as runs complete
- **Step 4**: Grade, aggregate benchmark, analyst pass, launch viewer
- **Step 5**: Read user feedback from `feedback.json`

### 4. Improving the Skill

Read `instructions/improving.md` for the iteration strategy:

- Generalize from feedback (avoid overfitting)
- Keep the prompt lean
- Explain the why behind instructions
- Look for repeated work across test cases (bundle as scripts)
- The iteration loop: improve -> rerun -> review -> repeat
- Advanced: Blind comparison (optional, requires subagents)

### 5. Description Optimization

Read `instructions/description-optimization.md` for the triggering optimization workflow:

- **Step 1**: Generate 20 trigger eval queries (should-trigger + should-not-trigger)
- **Step 2**: Review with user via HTML template
- **Step 3**: Run the optimization loop (`scripts.run_loop`)
- **Step 4**: Apply `best_description` to frontmatter
- Package and Present (if `present_files` tool is available)

### 6. Platform-Specific Adjustments

Read `instructions/platform-specific.md` when running in:

- **Claude.ai**: No subagents, inline review, skip benchmarking/description optimization
- **Cowork**: Use `--static` for viewer, GENERATE THE EVAL VIEWER before evaluating yourself

---

## Reference files

The agents/ directory contains instructions for specialized subagents. Read them when you need to spawn the relevant subagent.

> **Note**: The following agent/reference files are planned but not yet created.
> Use the inline instructions in `instructions/testing-evaluation.md` and `instructions/improving.md` instead.
>
> - `agents/grader.md` — How to evaluate assertions against outputs
> - `agents/comparator.md` — How to do blind A/B comparison between two outputs
> - `agents/analyzer.md` — How to analyze why one version beat another
> - `references/schemas.md` — JSON structures for evals.json, grading.json, etc.

The references/ directory has additional documentation:
- `references/planning-guide.md` — Skill categories, description formula, design patterns, success criteria
- `references/validation-checklist.md` — Critical rules, YAML reference, before/during/after checklists
- `references/skill-writing-principles.md` — 7 principles for high-quality skill content (directives not wisdom, cut general knowledge, etc.)
- `references/troubleshooting.md` — Common issues: won't upload, doesn't trigger, triggers too often, instructions not followed

## Skill Assets (Archetype Reference)

- スキル型選択ガイド: `references/skill-archetypes.md` — 新スキル作成時に archetype を選択するためのフローチャートと各型の定義

---

## Core Loop

- Figure out what the skill is about
- Draft or edit the skill
- Run claude-with-access-to-the-skill on test prompts
- With the user, evaluate the outputs:
  - Create benchmark.json and run `eval-viewer/generate_review.py` to help the user review them
  - Run quantitative evals
- Repeat until you and the user are satisfied
- Package the final skill and return it to the user.

Please add steps to your TodoList, if you have such a thing, to make sure you don't forget. If you're in Cowork, please specifically put "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases" in your TodoList to make sure it happens.

Good luck!

## Gotchas

- **eval データ汚染**: テストケースがスキル本体の例と重複すると過学習。eval は独立したシナリオで作成
- **description triggering 精度**: description が長すぎると他スキルと競合。"Use when" + "Do NOT use for" の対で精度を上げる
- **scope creep**: 1スキルに複数カテゴリの機能を詰め込むと発火条件が曖昧になる。1スキル1カテゴリを維持
- **benchmark 分散**: 少数回の実行では分散が大きい。最低5回以上の eval で統計的に判断
- **既存スキルとの重複**: 作成前に `/skill-audit` で類似スキルがないか確認
