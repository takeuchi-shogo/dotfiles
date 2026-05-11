---
status: reference
last_reviewed: 2026-04-23
---

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

スキル間の形式的関係。[arXiv:2603.04448](https://arxiv.org/abs/2603.04448) SkillNet ontology に基づく。
skill-audit の conflict 検出と triage-router のスキル選択に使用。

### depend_on

| Upstream | Downstream | Context |
|----------|-----------|---------|
| spec | validate | validate は spec の acceptance criteria を評価する |
| spike | validate | validate は spike の実装結果を検証する |
| spec | epd | epd は spec → spike → validate → review の統合フロー |
| spike | epd | epd は spike の結果をもとに proceed/pivot/abandon を判断 |
| codex-review | review | 100行超の変更では codex-review が review に先行する |

### conflicts_with

同時有効化が禁止。設計指針が矛盾するため併用すると出力品質が劣化する。

| Skill A | Skill B | 理由 |
|---------|---------|------|
| frontend-design | ui-ux-pro-max | デザイン指針が競合する可能性 |
| react-best-practices | react-expert | React 知識の範囲が重複 |

### belong_to

| Child | Parent | 備考 |
|-------|--------|------|
| react-expert | senior-frontend | React 以外の frontend 知識も含む |

### similar_to

機能的に等価で置換可能。同時使用は可能だが冗長。

| Skill A | Skill B | 理由 |
|---------|---------|------|
| codex-review | review | どちらもコードレビュー。100行超では codex-review を先行 |
| senior-frontend | react-best-practices | React 最適化は両方カバー。深度が異なる |

### compose_with

独立だが頻繁に連携。出力→入力の関係。

| Source | Target | 理由 |
|--------|--------|------|
| spec | spike | spec で仕様定義 → spike で実験実装 |
| research | absorb | research で調査 → absorb で統合 |
| skill-creator | skill-audit | 作成後に品質監査 |

### ガイダンス

- **`conflicts_with`** 関係にあるスキルを同時に有効にしない
- **`depend_on`** 関係がある場合、upstream スキルを先に実行する
- **`belong_to`** 関係にある場合、parent の方を優先検討する
- **`similar_to`** 関係にあるスキルは、ユースケースに応じて使い分ける（同時使用は可能だが冗長）
- **`compose_with`** 関係にあるスキルは、連鎖実行を検討する
- **`similar_to` と `conflicts_with` の違い**: similar は同時使用可能だが冗長、conflicts は同時有効化が禁止（設計指針が矛盾）

## Capability Coverage

各 agent/skill が行使する atomic capability のマッピング。
5 capability は [arXiv:2604.05013](https://arxiv.org/abs/2604.05013) の SE 分解に基づく。
Codex 批評: atomicity は skill 層ではなく agent/capability 層に課す。

| Capability | Primary Agent(s) | Supporting Skill(s) |
|------------|-------------------|---------------------|
| **Localization** (バグ・修正箇所の特定) | debugger, Explore | check-health, fix-issue |
| **Editing** (コード修正・生成) | （直接実装） | epd, rpi, spike, frontend-design |
| **Testing** (テスト生成・検証) | test-engineer, test-analyzer | spike (validate), webapp-testing |
| **Review** (コード品質評価) | code-reviewer, codex-reviewer, golang-reviewer | review, codex-review, security-review |
| **Reproduction** (Issue 再現・デバッグ) | debugger, `/codex:rescue` | fix-issue, systematic-debugging |

### ガイダンス

- 新スキル/エージェント追加時、どの capability をカバーするか明示する
- 1 capability に複数の agent が存在するのは正常（粒度・専門性が異なる）
- capability カバレッジの偏りは skill-audit で検出する

## Pattern Distribution

| Pattern | Count | Example Skills |
|---------|-------|----------------|
| tool-wrapper | 13 | codex, gemini, react-expert, senior-* |
| generator | 12 | eureka, daily-report, digest, frontend-design |
| reviewer | 10 | review, check-health, validate, skill-audit |
| inversion | 1 | interviewing-issues |
| pipeline | 11 | epd, autonomous, research, absorb |
| composite | 6 | spec (inv+gen), skill-creator (pipe+inv), verification-before-completion (pipe+rev) |
