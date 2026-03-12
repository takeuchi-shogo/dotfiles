# Claude Skill Inventory

Claude Code の skill を、常用すべき core と必要時だけ使う optional に分ける。

## Core Workflow

毎日の開発フローで優先して使う skill。

- `check-health`
- `search-first`
- `review`
- `verification-before-completion`
- `continuous-learning`
- `spec`
- `spike`
- `validate`
- `codex-review`

## Cross-Model / Research

外部モデルや深い調査が必要なときだけ使う。

- `codex`
- `gemini`
- `research`
- `epd`
- `interviewing-issues`

## Domain / Specialist

技術領域が明確なときだけ使う。

- `senior-architect`
- `senior-backend`
- `senior-frontend`
- `react-best-practices`
- `react-expert`
- `frontend-design`
- `web-design-guidelines`
- `webapp-testing`
- `vercel-composition-patterns`
- `edge-case-analysis`
- `ui-ux-pro-max`

## Automation / Meta

workflow 自体を改善するときに使う。

- `autonomous`
- `create-pr-wait`
- `improve`
- `eureka`
- `skill-audit`
- `skill-creator`
- `setup-background-agents`
- `ai-workflow-audit`

## Personal Ops

個人運用や GTD、知識管理で使う。通常の coding task では自動で前提にしない。

- `daily-report`
- `dev-ops-setup`
- `morning`
- `capture`
- `kanban`
- `meeting-minutes`
- `weekly-review`
- `dev-insights`
- `obsidian-vault-setup`
- `obsidian-knowledge`
- `obsidian-content`

## Default Guidance

- まず `Core Workflow` の skill で足りるか確認する
- domain skill は task が明確に一致したときだけ使う
- `Personal Ops` は coding task の default にしない
- 新しい skill を増やす前に、既存 tier のどこへ入るかを決める
