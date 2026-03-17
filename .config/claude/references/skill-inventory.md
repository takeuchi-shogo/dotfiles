# Claude Skill Inventory

Claude Code の skill を、常用すべき core と必要時だけ使う optional に分ける。

## Core Workflow

毎日の開発フローで優先して使う skill。

- `check-health` — reviewer
- `search-first` — pipeline
- `review` — reviewer
- `verification-before-completion` — pipeline+reviewer
- `continuous-learning` — pipeline
- `spec` — inversion+generator
- `spike` — pipeline
- `validate` — reviewer
- `codex-review` — reviewer

## Cross-Model / Research

外部モデルや深い調査が必要なときだけ使う。

- `codex` — tool-wrapper
- `gemini` — tool-wrapper
- `research` — pipeline
- `epd` — pipeline
- `interviewing-issues` — inversion

## Domain / Specialist

技術領域が明確なときだけ使う。

- `senior-architect` — tool-wrapper
- `senior-backend` — tool-wrapper
- `senior-frontend` — tool-wrapper
- `react-best-practices` — tool-wrapper
- `react-expert` — tool-wrapper
- `frontend-design` — generator
- `web-design-guidelines` — reviewer
- `webapp-testing` — tool-wrapper
- `vercel-composition-patterns` — tool-wrapper
- `edge-case-analysis` — reviewer
- `ui-ux-pro-max` — tool-wrapper+generator

## Automation / Meta

workflow 自体を改善するときに使う。

- `autonomous` — pipeline
- `create-pr-wait` — pipeline
- `improve` — pipeline
- `eureka` — generator
- `skill-audit` — reviewer
- `skill-creator` — pipeline+inversion
- `setup-background-agents` — generator
- `ai-workflow-audit` — reviewer

## Personal Ops

個人運用や GTD、知識管理で使う。通常の coding task では自動で前提にしない。

- `daily-report` — generator
- `dev-ops-setup` — pipeline
- `morning` — inversion+generator
- `capture` — generator
- `kanban` — tool-wrapper
- `meeting-minutes` — generator
- `weekly-review` — generator
- `dev-insights` — reviewer
- `obsidian-vault-setup` — generator
- `obsidian-knowledge` — tool-wrapper
- `obsidian-content` — generator

## Default Guidance

- まず `Core Workflow` の skill で足りるか確認する
- domain skill は task が明確に一致したときだけ使う
- `Personal Ops` は coding task の default にしない
- 新しい skill を増やす前に、既存 tier のどこへ入るかを決める

## Relationships (SkillNet)

スキル間の形式的関係。arXiv:2603.11808 SkillNet ontology に基づく。
skill-audit の conflict 検出と triage-router のスキル選択に使用。

### depends-on

| Upstream | Downstream | Context |
|----------|-----------|---------|
| spec | validate | validate は spec の acceptance criteria を評価する |
| spike | validate | validate は spike の実装結果を検証する |
| spec | epd | epd は spec → spike → validate → review の統合フロー |
| spike | epd | epd は spike の結果をもとに proceed/pivot/abandon を判断 |
| codex-review | review | 100行超の変更では codex-review が review に先行する |

### conflicts-with

| Skill A | Skill B | 理由 |
|---------|---------|------|
| frontend-design | ui-ux-pro-max | デザイン指針が競合する可能性 |
| react-best-practices | react-expert | React 知識の範囲が重複 |

### is-a-subset-of

| Subset | Superset | 備考 |
|--------|----------|------|
| react-expert | senior-frontend | React 以外の frontend 知識も含む |

### ガイダンス追記

- **conflicts-with 関係にある skill を同時に有効にしない**
- **depends-on 関係がある場合、upstream skill を先に実行する**
- **subset 関係にある場合、superset の方を優先検討する**

## Pattern Distribution

| Pattern | Count | Example Skills |
|---------|-------|----------------|
| tool-wrapper | 13 | codex, gemini, react-expert, senior-* |
| generator | 12 | eureka, daily-report, digest, frontend-design |
| reviewer | 10 | review, check-health, validate, skill-audit |
| inversion | 1 | interviewing-issues |
| pipeline | 11 | epd, autonomous, research, absorb |
| composite | 6 | spec (inv+gen), skill-creator (pipe+inv), verification-before-completion (pipe+rev) |
