---
status: reference
last_reviewed: 2026-05-23
---

# Claude Skill Inventory

Claude Code の skill を、常用すべき core と必要時だけ使う optional に分ける。

各 skill には **use-case category** を付与する (Anthropic 公式 Skills ガイド 2026-01 推奨)。

| Category | 意味 |
|----------|------|
| **Doc** | 知識・記録・ジャーナル系。読みと書きが中心、副作用なし |
| **Workflow** | 多段プロセスを走らせる pipeline / inversion / composite |
| **MCP-Enhance** | 外部 CLI / MCP server を wrap した tool-wrapper |
| **Reference** | 言語・フレームワーク・API のリファレンス知識 |

## Core Workflow

毎日の開発フローで優先して使う skill。

| Skill | Pattern | Category |
|-------|---------|----------|
| check-health | reviewer | Workflow |
| search-first | pipeline | Workflow |
| review | reviewer | Workflow |
| verification-before-completion | pipeline+reviewer | Workflow |
| continuous-learning | pipeline | Workflow |
| spec | inversion+generator | Workflow |
| spike | pipeline | Workflow |
| validate | reviewer | Workflow |
| codex-review | reviewer | Workflow |

## Cross-Model / Research

外部モデルや深い調査が必要なときだけ使う。

| Skill | Pattern | Category |
|-------|---------|----------|
| codex | tool-wrapper | MCP-Enhance |
| gemini | tool-wrapper | MCP-Enhance |
| research | pipeline | Workflow |
| epd | pipeline | Workflow |
| interviewing-issues | inversion | Workflow |

## Domain / Specialist

技術領域が明確なときだけ使う。

| Skill | Pattern | Category |
|-------|---------|----------|
| senior-architect | tool-wrapper | Reference |
| senior-backend | tool-wrapper | Reference |
| senior-frontend | tool-wrapper | Reference |
| react-best-practices | tool-wrapper | Reference |
| react-expert | tool-wrapper | Reference |
| frontend-design | generator | Workflow |
| web-design-guidelines | reviewer | Reference |
| webapp-testing | tool-wrapper | MCP-Enhance |
| vercel-composition-patterns | tool-wrapper | Reference |
| edge-case-analysis | reviewer | Workflow |
| ui-ux-pro-max | tool-wrapper+generator | Reference |

## Automation / Meta

workflow 自体を改善するときに使う。

| Skill | Pattern | Category |
|-------|---------|----------|
| autonomous | pipeline | Workflow |
| create-pr-wait | pipeline | Workflow |
| improve | pipeline | Workflow |
| eureka | generator | Doc |
| skill-audit | reviewer | Workflow |
| skill-creator | pipeline+inversion | Workflow |
| setup-background-agents | generator | Workflow |

## Personal Ops

個人運用や GTD、知識管理で使う。通常の coding task では自動で前提にしない。

| Skill | Pattern | Category |
|-------|---------|----------|
| daily-report | generator | Doc |
| dev-ops-setup | pipeline | Workflow |
| morning | inversion+generator | Doc |
| capture | generator | Doc |
| kanban | tool-wrapper | MCP-Enhance |
| meeting-minutes | generator | Doc |
| weekly-review | generator | Doc |
| dev-insights | reviewer | Doc |
| obsidian-vault-setup | generator | Workflow |
| obsidian-knowledge | tool-wrapper | MCP-Enhance |
| obsidian-content | generator | Doc |

## Default Guidance

- まず `Core Workflow` の skill で足りるか確認する
- domain skill は task が明確に一致したときだけ使う
- `Personal Ops` は coding task の default にしない
- 新しい skill を増やす前に、既存 tier のどこへ入るかを決める
- **Category 偏りチェック**: 1 tier に Reference / Doc / MCP-Enhance のいずれかが集中していたら抽象階層を見直す

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
| **Reproduction** (Issue 再現・デバッグ) | debugger, cmux Worker (codex) | fix-issue, systematic-debugging |

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
