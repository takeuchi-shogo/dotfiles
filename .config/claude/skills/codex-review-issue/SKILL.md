---
name: codex-review-issue
description: >
  Codex AI (gpt-5.4) を使って GitHub Issue の品質をレビューし、抜け漏れ・曖昧表現・エッジケース見落としを
  検出する。結果を Issue コメントとして投稿可能。
  Use when: 'Issue レビュー', 'Issue チェック', 'review issue', 'Codex で Issue 確認', 'Issue の品質',
  'Issue に抜け漏れがないか', 'Issue をレビューして'.
  Do NOT use for: コードレビュー (use /codex-review), Issue の明確化インタビュー (use /interviewing-issues),
  PR レビュー (use /review).
allowed-tools: "Read, Bash, Grep, Glob, AskUserQuestion"
disable-model-invocation: true
metadata:
  pattern: reviewer
  category: tooling
---

# Codex Review Issue

GitHub Issue の品質を Codex CLI (gpt-5.4) でレビューし、改善点を検出するスキル。

## ワークフロー

### Step 1 — Issue 情報を取得

```bash
gh issue view <N> --json title,body,labels,comments
```

Issue 番号が未指定の場合、`AskUserQuestion` で確認する。番号なしで実行しない。

### Step 2 — Issue 本文の前処理

- Issue 本文が 2000 文字を超える場合、要点を抽出してサマリーを作成してから Codex に渡す
- 日本語 Issue は、レビュー観点に関わる要点を英語に翻訳してから Codex に渡す（Codex は英語最適化のため）
- Issue がコードに言及している場合、該当コードを `Read` / `Grep` で確認し、コンテキストとして含める

### Step 3 — Codex CLI でレビュー実行

Step 1 で取得した Issue 情報を変数に格納し、プロンプトを組み立てる。
**重要**: single-quote HEREDOC (`<<'EOF'`) では変数展開されないため、double-quote HEREDOC (`<<EOF`) または直接文字列展開を使う。

```bash
# Step 1 で取得済みの値を変数に格納
ISSUE_TITLE="$(gh issue view <N> --json title --jq '.title')"
ISSUE_BODY="$(gh issue view <N> --json body --jq '.body')"

# プロンプトを組み立てて Codex に渡す
codex exec --skip-git-repo-check -m gpt-5.4 \
  --config model_reasoning_effort="xhigh" \
  --sandbox read-only \
  "Review the following GitHub Issue for completeness and clarity.

Check these aspects:
1. Requirements Completeness: Are all requirements clearly stated? Any missing requirements?
2. Ambiguity: Are there vague terms that could be interpreted multiple ways?
3. Edge Cases: Are boundary conditions and error scenarios addressed?
4. Acceptance Criteria: Are they measurable and testable?
5. Scope: Is the scope appropriate? Too broad or too narrow?
6. Dependencies: Are external dependencies or blockers identified?
7. Technical Feasibility: Any obvious technical concerns?

Issue:
Title: ${ISSUE_TITLE}
Body: ${ISSUE_BODY}

Output format:
## Issue Review Summary
**Overall Quality**: [Good/Needs Improvement/Major Gaps]

### Findings
[MUST/SHOULD/CONSIDER] - description

### Suggested Additions
- specific text to add to the issue" 2>/dev/null
```

### Step 4 — 結果をユーザーに表示

Codex のレビュー結果を日本語で報告する。Codex への指示は英語、ユーザーへの報告は日本語。

### Step 5 — 投稿確認

`AskUserQuestion` で「Issue コメントとして投稿しますか？」と確認する。確認なしに投稿しない。

### Step 6 — コメント投稿

確認後のみ実行:

```bash
gh issue comment <N> --body "..."
```

## reasoning effort

常に `xhigh` を使用する。「ねっとりレビュー」として深い推論で品質を最大化するため、effort を下げない。

## Decision: codex-review-issue vs codex-review vs interviewing-issues vs review

| 状況 | 推奨 | 理由 |
|------|------|------|
| Issue 本文の品質をレビューしたい | `/codex-review-issue` | Issue の抜け漏れ・曖昧さを Codex で検出 |
| コードの変更をレビューしたい | `/codex-review` | コード差分のレビュー専用 |
| Issue の仕様をユーザーと対話で明確化 | `/interviewing-issues` | 対話ベースの明確化プロセス |
| PR のコードレビュー | `/review` | コードレビュー全般 |

## Anti-Patterns

| # | NG | 理由 |
|---|------|------|
| 1 | Issue 番号なしで実行する | レビュー対象が不明確になる |
| 2 | reasoning effort を下げる | ねっとりレビューの意味がなくなる |
| 3 | レビュー結果を確認なしに投稿する | 誤った指摘をコメントする危険がある |
| 4 | コードベースを読まずにレビューする（Issue がコードに言及している場合） | 文脈なしでは的外れなレビューになる |
| 5 | 日本語 Issue をそのまま Codex に渡す | 英語最適化モデルなので品質が下がる |

## Gotchas

- **`--skip-git-repo-check` 必須**: dotfiles の symlink 問題で git repo 検出に失敗するため、常にこのフラグが必要
- **Issue 本文が長すぎる場合**: 2000 文字超はサマリーを先に Codex に渡す。全文だとコンテキストを圧迫する
- **日本語 Issue の翻訳**: Codex は英語最適化なので、要点を英語に翻訳してから渡す
- **2>/dev/null の副作用**: Codex CLI 自体のエラー（認証切れ等）が見えなくなる。問題時は外して実行
- **レート制限**: Codex CLI は API レート制限に引っかかることがある。429 エラー時は 30 秒待って再試行
