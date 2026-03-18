---
name: spec
description: "Prompt-as-PRD を生成する。アイデアを構造化プロンプトとして記述し、docs/specs/ にバージョン管理する。agent にそのまま渡せる実行可能な仕様書を作成。"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user-invocable: true
metadata:
  pattern: inversion+generator
---

# Spec: Prompt-as-PRD Generator

アイデアを構造化プロンプト（Prompt-as-PRD）に変換し、バージョン管理する。
生成されたファイルは agent にそのまま渡せる実行可能な仕様書として機能する。

## Philosophy: Spec は思考ツールである

仕様書の第一の目的は **人間の思考を整理すること** であり、agent への入力は副次的な効果。

- **考えを明確にするために書く**: 仕様書は「何を作るか」を自分自身が理解するための道具
- **生成最適化に走らない**: agent が読みやすいかより、要件が正しく捉えられているかを優先する
- **精密さには天井がある**: 仕様書を精密にしすぎるとコードと1:1対応になり、仕様を書く意味が消える（Borges の地図問題）
- **速度で品質を犠牲にしない**: 急いで書いた仕様書は "slop"（形式は整っているが中身が空虚な文書）になる

## Workflow

### Standard Mode（デフォルト）

1. ユーザーのアイデア・要求を受け取る
2. 対話で要件を明確化する（2-5 個の質問、1回に1つ）
3. 構造化プロンプトを生成する
4. `docs/specs/{feature}.prompt.md` に保存する

### Deep Interview Mode（`/interview` または引数に `--interview`）

1. 既存の spec/ドラフト/アイデアを読み込む
2. **AskUserQuestionTool** で体系的にインタビューする（10-40+ 問）
3. 回答を統合して構造化プロンプトを生成する
4. `docs/specs/{feature}.prompt.md` に保存する
5. **Session Handoff**: 「この spec を新しいセッションで実行してください」とガイダンス出力

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

## Deep Interview Protocol

AskUserQuestionTool を使った深いインタビューモード。
大規模機能（L スケール）や不確実性の高いプロジェクトで使用する。

### 起動条件

以下のいずれかで Deep Interview Mode に入る:
- `/interview` コマンドから呼ばれた場合
- `/spec --interview` で引数指定された場合
- `/epd` の Phase 1 で L 規模と判定された場合

### インタビュー手順

1. **コンテキスト把握**: 既存の spec ファイル、関連コード、ドキュメントを先に読む
2. **AskUserQuestionTool で質問**: 以下の 10 カテゴリから非自明な質問を選択
3. **バッチ質問**: 1回に 2-3 問ずつ、関連するカテゴリをまとめて質問
4. **深掘り**: 回答から新たな疑問が生じたらフォローアップ
5. **収束確認**: 「他に聞いておくべきことはありますか？」で完了を確認
6. **spec 書き出し**: 全回答を統合して Prompt-as-PRD を生成

### 質問カテゴリ（10 カテゴリ）

| # | カテゴリ | 質問例 |
|---|---------|--------|
| 1 | **ユーザーペルソナ** | 「主なユーザーは？ A) 開発者 B) 非技術者 C) 両方」 |
| 2 | **課題・動機** | 「現在の最大のペインは？」 |
| 3 | **技術実装** | 「データストアは A) SQLite B) PostgreSQL C) ファイルシステム？」 |
| 4 | **UI/UX** | 「エラー時の表示は A) トースト B) インライン C) モーダル？」 |
| 5 | **トレードオフ** | 「速度 vs 正確性、どちらを優先？」 |
| 6 | **エッジケース** | 「入力が 10万件を超える場合は？」 |
| 7 | **セキュリティ** | 「認証は必要？ A) 不要 B) API キー C) OAuth」 |
| 8 | **パフォーマンス** | 「許容レイテンシは？ A) <100ms B) <1s C) 気にしない」 |
| 9 | **既存システム統合** | 「既存の X との互換性は必要？」 |
| 10 | **スコープ境界** | 「V1 で必須なのはどこまで？ V2 に回せるものは？」 |

### ルール

- **質問は選択肢付き**を優先（AskUserQuestionTool の強みを活かす）
- **自明な質問はしない**（コードベースから読み取れることは聞かない）
- **質問数の目安**: S=5-10, M=10-20, L=20-40+
- **フォローアップ**: 曖昧な回答には必ず深掘り
- 回答から判明した技術的制約は即座に Constraints に反映

## Session Handoff

Deep Interview Mode で生成した spec には、以下のガイダンスを出力する:

```
---
✅ Spec 完成: docs/specs/{feature}.prompt.md

📋 次のステップ:
  新しい Claude Code セッションで以下を実行してください:

  /epd docs/specs/{feature}.prompt.md
  または
  claude --model opus "Read docs/specs/{feature}.prompt.md and implement it"

💡 なぜ新セッション？
  - インタビューの会話履歴がコンテキストを圧迫しない
  - 実装に集中できるクリーンなコンテキスト
  - spec が「契約」として機能する
```

Standard Mode では Session Handoff は出力しない（同一セッションで続行可）。

## Precision Ceiling: Spec → Code 切り替え判断

仕様書が以下の兆候を示したら、**書き足すのをやめて直接コードを書く** べきサイン:

| 兆候 | 説明 |
|------|------|
| **DB スキーマの全カラム定義** | テーブル名と主要リレーションで十分。全フィールドは実装で決める |
| **擬似コードが実装の 1/3 超** | 擬似コードを書くなら本物のコードを書いた方が検証可能 |
| **条件分岐の網羅的記述** | if/else の全パスを spec に書くのはコードの二重管理 |
| **型定義・インターフェースの詳細** | 型は spec ではなくコードで表現すべき正式な契約 |
| **「agent に伝わるように」の書き直し** | 仕様書がコードに収束している兆候 |

**到達したら**: spec の Prompt セクションは意図と制約のみに留め、`/spike` で実装に移る。

## Anti-Patterns

- 要件を確認せずにすぐ生成する（必ず最低2つは質問する）
- acceptance_criteria が曖昧（「うまく動く」ではなく検証可能な形で）
- Prompt セクションが抽象的すぎる（agent が実装できる具体性が必要）
- Out of Scope を省略する（スコープクリープの最大の原因）
- **Spec slop**: AI に生成させた仕様書を精査せずに使う（形式的に正しいが一貫性のない文書）
- **過剰精密化**: 実装の 1:1 写像になるまで spec を書き込む（コードを書いた方が速い）

## Templates

- `templates/prompt-as-prd-template.md` — PRD テンプレート。新しい spec 作成時にコピーして使用

## Updating Specs

既存の spec を更新する場合:

1. `status` を `draft` に戻す
2. 変更内容を Requirements に反映
3. acceptance_criteria を更新
4. 変更理由をコミットメッセージに記載

## Skill Assets

- Spec Slop 検知基準: `references/precision-ceiling.md`
- PRDテンプレート: `templates/prompt-as-prd-template.md` (既存)
