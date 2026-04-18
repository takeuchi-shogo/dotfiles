---
name: create-issue
description: >
  ユーザーの要件テキスト（自由文）から構造化された GitHub Issue を生成し、gh issue create で投稿する。
  タイトル・本文（背景/要件/受入基準/技術メモ）・ラベルを自動生成し、プレビュー確認後に投稿。
  Triggers: 'Issue 作りたい', 'Issue 作成', 'create issue', '要件を Issue にして', 'GitHub Issue'.
  Do NOT use for: 既存 Issue の明確化（use /interviewing-issues）、仕様書作成（use /spec）、PR 作成（use /pull-request）。
origin: self
allowed-tools: Read, Bash, Grep, Glob, AskUserQuestion
metadata:
  pattern: generator
---

# Create Issue: 要件テキストから GitHub Issue を生成

ユーザーの自由文テキストから構造化された GitHub Issue を生成し、確認後に `gh issue create` で投稿する。

## Workflow

```
1. CAPTURE（要件テキスト受け取り）
   → ユーザーの自由文を解析

2. ANALYZE（コンテキスト収集）
   → リポジトリの既存 Issue・ラベル・コードベースを調査

3. STRUCTURE（Issue 構造化）
   → タイトル・本文・ラベルを自動生成

4. PREVIEW（プレビュー確認）
   → AskUserQuestion でユーザーに確認

5. POST（投稿）
   → gh issue create で投稿、Issue 番号を返す
```

## Phase 1: Capture（要件テキスト受け取り）

ユーザーの入力を受け取る。入力形態は以下のいずれか:

- スキル呼び出し時の引数テキスト
- 会話中の自由文（「こういう機能がほしい」「このバグを直したい」等）

入力が不十分な場合のみ `AskUserQuestion` で補足質問する（最大 2 問）:

| 不足情報 | 質問例 |
|---------|--------|
| 何をしたいか不明 | 「具体的にどんな動作を期待していますか？」 |
| バグか機能か不明 | 「これは既存の不具合の修正ですか？それとも新機能ですか？」 |

## Phase 2: Analyze（コンテキスト収集）

リポジトリのコンテキストを収集して Issue の品質を上げる:

1. **既存ラベル取得**: `gh label list --json name,description` で利用可能なラベルを確認
2. **重複チェック**: `gh issue list --state open --search "キーワード"` で類似 Issue がないか確認
3. **関連コード調査**: 要件に関係するファイル・関数を Grep/Glob で特定（技術メモに反映）

重複 Issue が見つかった場合は `AskUserQuestion` でユーザーに報告し、続行するか確認する。

## Phase 3: Structure（Issue 構造化）

以下の構造で Issue を生成する:

### タイトル

- 簡潔な 1 行（50 文字以内目安）
- 動詞始まり推奨（「追加する」「修正する」「改善する」）
- 曖昧な表現を避ける（NG: 「いい感じにする」→ OK: 「検索結果の表示速度を改善する」）

### 本文テンプレート

```markdown
## 背景

（なぜこの Issue が必要か。ユーザーの要件テキストから背景を要約）

## 要件

- [ ] 要件 1
- [ ] 要件 2
- [ ] 要件 3

## 受入基準

- [ ] 基準 1（検証可能な形で記述）
- [ ] 基準 2

## 技術メモ

（関連ファイル・影響範囲・実装上の注意点。Phase 2 の調査結果を反映）
```

### ラベル選択

- リポジトリの既存ラベルから最適なものを選択する（**新規ラベルは作成しない**）
- 選択基準: bug / feature / enhancement / chore / documentation 等の基本カテゴリ
- 最大 3 個まで（関連性の高い順）

## Phase 4: Preview（プレビュー確認）

`AskUserQuestion` で以下を表示し、ユーザーの確認を得る:

```
以下の内容で Issue を作成します。確認してください。

【タイトル】{title}
【ラベル】{labels}

【本文】
{body}

---
修正が必要な箇所があれば指摘してください。
問題なければ「OK」と回答してください。
```

- ユーザーが修正を指示した場合 → 修正して再プレビュー
- ユーザーが「OK」または承認の意思を示した場合 → Phase 5 へ

**重要: ユーザーの明示的な承認なしに投稿してはならない。**

## Phase 5: Post（投稿）

```bash
gh issue create \
  --title "タイトル" \
  --body "$(cat <<'EOF'
本文
EOF
)" \
  --label "label1,label2"
```

投稿後:

1. 作成された Issue の URL と番号を表示する
2. `gh issue view <number> --json url,number,title` で投稿結果を確認する

## Anti-Patterns

| NG | 理由 |
|----|------|
| 要件を勝手に膨らませる | ユーザーの意図を超えたスコープ追加は混乱を招く。書かれていないことは追加しない |
| 確認なしに投稿する | 誤った Issue が作られると修正・削除の手間が発生する。必ず Preview を経る |
| ラベルを 4 個以上つける | ラベル過多は分類の意味を失わせる。最大 3 個に絞る |
| 存在しないラベルを指定する | `gh issue create` が失敗する。Phase 2 で取得した既存ラベルのみ使用 |
| 本文をマークダウンなしのプレーンテキストで書く | 可読性が下がる。セクション見出し・チェックリストを活用する |

## 関連スキル

- `/interviewing-issues` — **既存** Issue を明確化するスキル。create-issue は **ゼロから** Issue を作る
- `/spec` — 仕様書（PRD）を作成する。create-issue は GitHub Issue として投稿する
- `/pull-request` — PR を作成する。Issue と PR は別物

## Gotchas

- **gh 認証**: `gh auth status` が失敗する場合は投稿できない。エラー時はユーザーに `gh auth login` を案内する
- **リポジトリ外実行**: git リポジトリ外で実行すると `gh` コマンドが失敗する。`git rev-parse --show-toplevel` で事前確認する
- **ラベル不在**: リポジトリにラベルが未設定の場合は `--label` オプションを省略する
- **長文本文**: 本文が極端に長い場合（2000 文字超目安）はユーザーに要約を提案する
