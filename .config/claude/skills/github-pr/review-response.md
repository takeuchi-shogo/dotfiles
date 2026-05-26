# レビューコメント対応

レビュワーからのコメントに対応する。フェーズごとにまとめて進め、1件ずつ直列で完了させない。

## コミュニケーション原則

Google eng-practices `handling-comments.md` 準拠。Phase 1–3 の前提として内面化する。

### コードへの指摘として受け取る

レビューコメントはコードの品質向上を意図したもの。「なぜ私が？」ではなく「レビュワーが伝えようとしていることの建設的な意味は何か？」を問い、その意図を前提に行動する。

怒りや苛立ちを感じたまま返信しない。作業から離れて落ち着いてから返す。レビューツールに残った返信は永続する。

### コードで応答する（ツール内説明は最後の手段）

「このコードが分からない」と言われた場合の対応優先順位:

1. **コード自体を書き直す**（最優先）— リネーム・分割・リファクタリングで疑問ごと消す
2. **コードコメントを追加する** — コードを変えられない場合、なぜそのコードが存在するかを *why* で補足
3. **レビューツール内で説明する**（最後の手段）— 通常の読者が既知の内容をレビュワーが知らない場合のみ

> レビューツール内の説明は将来のコード読者に届かない。コードとコメントは届く。

### 協調的に返す（防御的にならない）

意見の相違があるときの返信フォーマット（eng-practices 原文引用）:

```
Bad:  "No, I'm not going to do that."

Good: "I went with X because of [these pros/cons] with [these tradeoffs].
      My understanding is that using Y would be worse because of [these reasons].
      Are you suggesting that Y better serves the original tradeoffs, that we should
      weigh the tradeoffs differently, or something else?"
```

返信に含める 3 要素: (1) 自分のアプローチの根拠（pros/cons + tradeoffs）、(2) 相手案への懸念（技術的根拠で）、(3) 相手の意図の確認（複数の可能性で問い返す）。

## Phase 1: 分析（変更なし）

### 1. 未解決コメントの取得

```bash
~/.claude/skills/github-pr/gh-unresolved-threads <URL>
```

### 2. 分類

各コメントを分類:

**対応不要（resolveしない）:**
- コード説明のコメント、FYI的な情報共有、確認済みの指摘
- resolveせずスレッドをそのまま残す。レビュワーの知見や補足情報はスレッド上に残す価値がある

**コード修正不要だがresolveが必要:**
- 別issue/PRで対応する場合 → 対応先issueのURLを貼ってresolve
- nit/optionalに対応しない場合 → 対応しない理由を記載してresolve

**対応が必要:**
- 議論が残っている・回答待ちのスレッド

## Phase 2: 報告・議論

MUST: 分類結果をユーザーに提示し、各コメントの対応方針を議論する。合意なく修正に着手しない。

| # | スレッド | 分類 | 対応案 |
|---|----------|------|--------|
| 1 | 該当箇所の要約 | 対応必要 / 対応不要 | 修正方針 or 不要理由 |
| ... | ... | ... | ... |

判断が必要な項目（値の選定、命名、設計判断など）は、前例調査や根拠を添える。

未解決コメントが0件の場合 → その旨を報告して完了。

## Phase 3: 実行

合意した方針に従い、バッチで対応する。

### ステップ1: 対応宣言

全件に「対応します」とコメント（作業前に対応意思を先んじて伝える）。

### ステップ2: 実装

全件の修正をまとめて実施・コミット。

### ステップ3: push

コミットをリモートにpushする。GitHub上でコミットハッシュをリンク化するために必要。

### ステップ4: 完了報告

全件に完了コメント+resolveをまとめて実行。

完了コメントにはコミットハッシュと対応理由を添える。自明な場合は簡潔でよい。

<example>
# Good: コミットハッシュ+理由あり
abc1234 で対応しました。nilチェックが漏れておりpanicの可能性がありました。

# Good: 自明な場合
abc1234 で対応しました。typo修正です。

# Bad: コミットハッシュなし
対応しました。
</example>

### ステップ5: re-request review

全対応完了後、レビュワーにre-request reviewを送る。

```bash
gh pr edit <URL> --add-reviewer <REVIEWER_LOGIN>
```

## GraphQL操作リファレンス

### スレッドへの返信

`gh-unresolved-threads`の出力に含まれる`id`（THREAD_ID）を使って返信する:

```bash
gh api graphql -f query='
  mutation {
    addPullRequestReviewThreadReply(input: {
      pullRequestReviewThreadId: "<THREAD_ID>"
      body: "返信内容"
    }) { comment { id } }
  }'
```

### スレッドのresolve

```bash
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "<THREAD_ID>"}) {
      thread { isResolved }
    }
  }'
```

返信とresolveを両方行う場合は、返信→resolveの順で実行する。
