---
name: spec
description: "Prompt-as-PRD を生成する。アイデアを構造化プロンプトとして記述し、docs/specs/ にバージョン管理する。agent にそのまま渡せる実行可能な仕様書を作成。"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user-invocable: true
---

# Spec: Prompt-as-PRD Generator

アイデアを構造化プロンプト（Prompt-as-PRD）に変換し、バージョン管理する。
生成されたファイルは agent にそのまま渡せる実行可能な仕様書として機能する。

## Workflow

1. ユーザーのアイデア・要求を受け取る
2. 対話で要件を明確化する（1回に1つの質問）
3. 構造化プロンプトを生成する
4. `docs/specs/{feature}.prompt.md` に保存する
5. git commit する

## Output Format

生成するファイルの形式:

```yaml
---
title: Feature Name
status: draft
created: YYYY-MM-DD
acceptance_criteria:
  - criterion 1
  - criterion 2
scope: S | M | L
---
```

```markdown
## Context

なぜこの機能が必要か。ユーザーが抱えている課題。

## Requirements

- 機能要件を箇条書き
- 各要件は検証可能な形で記述

## Constraints

- 技術的制約
- 非機能要件（パフォーマンス、セキュリティ等）

## Out of Scope

- 明示的にやらないこと（スコープクリープ防止）

## Prompt

以下の仕様に基づいて実装してください：

（agent に渡す形式の具体的な実装指示。コンテキスト、要件、制約を踏まえた明確な指示文。）
```

## Clarification Guidelines

要件を明確化する際の質問の優先順位:

1. **誰のための機能か**（ユーザーペルソナ）
2. **何を解決するか**（課題・ペイン）
3. **成功をどう測るか**（acceptance criteria）
4. **何をやらないか**（out of scope）
5. **技術的制約は何か**（既存システムとの統合等）

## Anti-Patterns

- 要件を確認せずにすぐ生成する（必ず最低2つは質問する）
- acceptance_criteria が曖昧（「うまく動く」ではなく検証可能な形で）
- Prompt セクションが抽象的すぎる（agent が実装できる具体性が必要）
- Out of Scope を省略する（スコープクリープの最大の原因）

## Updating Specs

既存の spec を更新する場合:

1. `status` を `draft` に戻す
2. 変更内容を Requirements に反映
3. acceptance_criteria を更新
4. 変更理由をコミットメッセージに記載
