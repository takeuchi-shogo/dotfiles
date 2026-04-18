---
name: github-review-workflow
description: Use when the user wants help with GitHub PR comments, failing GitHub Actions checks, or a short workflow that routes between gh-address-comments and gh-fix-ci.
platforms: [agents, codex]
---

# GitHub Review Workflow

GitHub の review comment 対応と CI failure 対応を、毎回 skill 名を思い出さなくても扱える wrapper。

## When To Use

- PR review comments を処理したい
- current branch の PR の failing checks を見たい
- GitHub review / CI 周りの次アクションを短く呼びたい

詳細な呼び出し例は `references/usage.md` を使う。

## Sources Of Truth

- `gh-address-comments`
- `gh-fix-ci`

## Routing

まずユーザーの目的を次のどれかに分類する。

- `comments`
  - PR review comments / review threads を見て対処したい
- `ci`
  - GitHub Actions の failing checks を調べたい
- `both`
  - PR comment と CI を両方片付けたい
- `unknown`
  - どちらかわからない

## Ask-Back Rule

以下が曖昧なら、先に短く聞き返す。

1. PR comments と failing CI のどちらを見ますか。
2. current branch の PR でよいですか。
3. 修正まで進めるのか、まず状況整理だけか、どちらですか。

## Workflow

1. `gh auth status` が通る前提か確認する。
2. `comments` の場合:
   - `gh-address-comments` を使う
   - open PR の comment / thread を番号付きで要約する
   - どの番号を対応するかをユーザーに確認する
   - 選ばれたものだけ修正する
3. `ci` の場合:
   - `gh-fix-ci` を使う
   - failing checks と failure snippet を要約する
   - fix plan を出す
   - 実装は explicit approval の後だけ行う
4. `both` の場合:
   - まず `ci` を先に片付ける
   - 次に `comments` を処理する
5. 結果として次のいずれかを返す:
   - 状況整理だけ
   - 修正候補と plan
   - 実際の修正結果

## Guardrails

- `gh` 認証がなければ、先に `gh auth login` を案内する
- GitHub Actions 以外の external CI provider は URL 報告に留める
- `gh-fix-ci` の explicit approval 要件を飛ばさない
- comment 全対応を勝手に進めず、番号付きで確認を挟む

## Output Modes

- `summary`
  - failing checks / comments の状況だけ返す
- `plan`
  - 修正方針まで返す
- `apply`
  - 承認済みの修正を実施する

ユーザー指定がなければ `plan` を使う。

## Anti-Patterns

- CI と review comment を混ぜて雑に処理する
- auth 未確認のまま `gh` コマンドを進める
- `gh-fix-ci` の approval 前提を無視して実装する
