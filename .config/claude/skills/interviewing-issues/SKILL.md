---
name: interviewing-issues
description: >
  曖昧なGitHub Issueを4段階のインタビューで明確化し、構造化された仕様を出力する。実装前の要件定義・スコープ確定に使用。
  Triggers: 'Issue 明確化', '要件定義', 'スコープ確定', 'interview issue', '曖昧な Issue', 'Issue を仕様に'.
  Do NOT use for: 仕様書作成（use /spec）、実装込みフロー（use /epd）、既に明確な Issue の実装（use /rpi）。
metadata:
  pattern: inversion
---

# /interviewing-issues — Issue を仕様に変換する

曖昧な GitHub Issue を 4 段階のインタビューで明確化し、実装可能な仕様を出力する。

## Trigger

- Issue の要件が曖昧で、すぐに実装に入れないとき
- スコープが不明確で「どこまでやるか」が決まっていないとき
- `/fix-issue` に渡す前に仕様を固めたいとき

## Workflow

```
1. PARSE（Issue 解析）
   → gh issue view で取得、曖昧箇所を特定

2. CLARIFY（質問による明確化）
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ スコープ  │ │  要件    │ │ エッジ   │
   │ 確認     │ │  詳細    │ │ ケース   │
   └──────────┘ └──────────┘ └──────────┘
   ┌──────────┐ ┌──────────┐
   │  優先度   │ │ 技術的   │
   │ 判定     │ │  制約    │
   └──────────┘ └──────────┘

3. CRITERIA（受け入れ条件定義）
   → Given/When/Then 形式で条件を定義、ユーザー確認

4. OUTPUT（構造化仕様出力）
   → 仕様ドキュメントを生成 → /fix-issue へチェーン
```

## Phase 1: Parse（Issue 解析）

1. `gh issue view <N>` で Issue の全情報を取得
2. title, body, labels, comments を分析
3. 曖昧箇所を洗い出す: スコープ境界、具体性不足の要件、暗黙の前提、矛盾
4. Issue に言及されたファイル・コンポーネントをコードベースで確認
5. 関連する Issue や PR がないか `gh issue list` で確認

## Phase 2: Clarify（質問による明確化）

`AskUserQuestion` ツールで 3-7 個の質問をユーザーに投げる。

| カテゴリ | 質問例 |
|---------|--------|
| **スコープ** | 「この変更は X のみ対象？それとも Y も含む？」 |
| **要件** | 「入力が空の場合は？ A) エラー B) デフォルト値 C) スキップ」 |
| **エッジケース** | 「ファイルが 1GB を超える場合の挙動は？」 |
| **優先度** | 「以下を Must / Should / Could で分類: ...」 |
| **技術的制約** | 「既存の X ライブラリ前提？別の選択肢も検討？」 |

- 選択肢付きの質問を優先（オープンエンドは最大 1-2 個）
- 1回の質問に全項目をまとめる（往復を最小化）
- 回答不十分な場合のみ追加質問（最大 2 ラウンド）

## Phase 3: Criteria（受け入れ条件の定義）

1. 回答を元に Given/When/Then 形式で受け入れ条件を作成
2. 条件をユーザーに提示して確認
3. 必要に応じて修正・追加・削除

```
例: Given: 設定ファイル編集中
    When: 無効な JSON を保存しようとした
    Then: エラー表示され、保存がブロックされる
```

## Phase 4: Output（構造化仕様出力）

以下の形式で仕様を出力:

```markdown
## Summary
[1-2文の要約]
## Acceptance Criteria
- [ ] Given ... When ... Then ...
## Out of Scope
- [やらないこと]
## Technical Notes
- [技術的な注意点]
```

出力後、「この仕様で実装を開始しますか？ `/fix-issue` に渡せます」と確認する。

## Usage

```
/interviewing-issues 42       # Issue #42 を分析
/interviewing-issues           # Issue 番号を聞く（AskUserQuestion で確認）
```

## 連携

- **`/fix-issue`**: 出力した仕様をそのまま渡して実装開始
- **`/interview`**: Issue 起点でない一般的な機能インタビューには `/interview` を使用
- **Issue コメント**: `gh issue comment <N> --body "..."` で仕様を投稿（確認後）
- **ラベル付与**: `gh issue edit <N> --add-label "spec-ready"` でステータス更新

## Anti-Patterns

| NG | 理由 |
|----|------|
| 質問せずに推測で仕様を書く | 曖昧な点は必ずユーザーに確認 |
| 7個超の質問 | 情報過多。優先度の高いものに絞る |
| 抽象的な受け入れ条件 | 「正しく動作する」ではなく具体的な入出力を書く |
| スコープを広げすぎる | Issue に書かれていない機能を追加しない |

## Skill Assets

- 構造化仕様書テンプレート: `templates/structured-spec.md`
- 質問パターン集: `references/question-patterns.md`

## Example

```
/interviewing-issues 42

Phase 1: Issue #42 「設定ファイルのバリデーション追加」→ 範囲・エラー表示が未定義
Phase 2: 質問 → JSON/YAML？ エラー動作は A)警告 B)ブロック C)両方？
Phase 3: Given/When/Then で受け入れ条件を定義 → ユーザー確認
Phase 4: 構造化仕様を出力 → /fix-issue へチェーン可能
```
