---
name: codex-review
description: >
  Codex AI を使った read-only コードレビューと CHANGELOG 自動生成。手動レビュー(/codex-review)や
  自動レビューフロー(general-purpose Agent経由)で使用。--post-to-pr <PR番号> で GitHub PR にレビュー
  結果をコメント投稿可能。実装・編集には codex スキルを使うこと。
  S規模以上の全変更で Review Gate として使用可能。/review スキルからの自動起動にも対応。
  Do NOT use for posting comments without user confirmation — always preview before posting.
allowed-tools: "Read, Bash, Grep, Glob, Agent, AskUserQuestion"
disable-model-invocation: true
metadata:
  pattern: reviewer
---

# Codex Review

## レビュー実行

### 1. 変更差分を確認

```bash
git diff --stat
```

### 2. Codex CLI で構造化レビュー

```bash
codex exec --skip-git-repo-check -m gpt-5.4 --config model_reasoning_effort="xhigh" --sandbox read-only "$(cat <<'PROMPT'
Review the recent git changes. Check these 6 items in order:

1. **Correctness**: Logic errors, off-by-one, null/nil dereference, race conditions
2. **Security**: Injection, auth bypass, secrets exposure, unsafe deserialization
3. **Error Handling**: Swallowed errors, missing validation, unclear error messages
4. **Naming & Readability**: Misleading names, overly complex code, missing docs
5. **Performance**: Unnecessary allocations, N+1 queries, missing indexes
6. **Tests**: Missing edge cases, flaky patterns, inadequate coverage
7. **Plan Alignment**: Does the implementation match the plan's intent? Any scope drift, missing tasks, or unplanned additions? (Skip if no plan exists)

Output format — one line per finding:
[MUST/CONSIDER/NIT] file:line - description

Group findings by file. If no issues found, output "LGTM — no issues detected."
PROMPT
)" 2>/dev/null
```

### reasoning_effort ガイド

| シナリオ                   | 設定     | 理由                       |
| -------------------------- | -------- | -------------------------- |
| コードレビュー（全種別）   | `xhigh`  | 深い推論で品質を最大化     |
| CHANGELOG/ドキュメント生成 | `medium` | 生成タスクは深い推論不要   |

## CHANGELOG 自動生成

```bash
codex exec --skip-git-repo-check -m gpt-5.4 --config model_reasoning_effort="medium" --sandbox read-only "$(cat <<'PROMPT'
Generate a CHANGELOG entry for the recent changes.
Use conventional commits format. Group by: Added, Changed, Fixed, Removed.
Base on git log output.
PROMPT
)" 2>/dev/null
```

## セキュリティ特化レビュー

認証・暗号・入力処理の変更時に使用。`profiles.security`（xhigh + read-only）を利用:

```bash
codex exec --skip-git-repo-check -m gpt-5.4 -p security "$(cat <<'PROMPT'
Deep security review of the recent git changes. Analyze:

1. **Threat Model**: Trust boundaries, untrusted inputs, privileged actions, sensitive data paths
2. **Invariant Breaks**: Checks that happen before decode/parse/normalize/render and may not hold at the final interpretation point
3. **Injection**: SQL/NoSQL/OS command/LDAP injection via untrusted input
4. **Auth & Access Control**: Broken authentication, missing authorization checks, privilege escalation
5. **Cryptography**: Weak algorithms, hardcoded keys, improper key management, IV/nonce reuse
6. **Data Exposure**: Secrets in logs/responses, PII leakage, missing encryption at rest/transit
7. **Supply Chain**: Unpinned dependencies, known CVEs, typosquatting risk

Output format — one line per finding:
[CRITICAL/HIGH/MEDIUM/LOW] file:line - vulnerability description + attack scenario

For each finding, include threat-model assumptions and validation evidence when possible.

Treat scanner or audit findings as supporting evidence, not the starting point of the analysis.

If no issues found, output "SECURE — no vulnerabilities detected."
PROMPT
)" 2>/dev/null
```

## GitHub PR コメント投稿（--post-to-pr モード）

オプション引数 `--post-to-pr <PR番号>` を指定すると、レビュー結果を GitHub PR にコメントとして投稿する。
指定しなければ従来通りターミナル表示のみ（後方互換）。

### 使い方

```
/codex-review --post-to-pr 123
```

### ワークフロー

#### Step 1: PR 番号の解決

PR 番号が指定されていない場合、候補を一覧表示してユーザーに選択させる:

```bash
gh pr list --state open --limit 20
```

`AskUserQuestion` で「どの PR に投稿しますか？ 番号を入力してください」と確認する。

#### Step 2: 既存レビューの実行

上記「レビュー実行」セクションの手順をそのまま実行する（変更なし）。

#### Step 3: レビュー結果のパース

Codex の出力から `[MUST/CONSIDER/NIT] file:line - description` 形式の行を抽出し、指摘リストを構築する。

- 各指摘の severity（MUST / CONSIDER / NIT）、ファイルパス、行番号、説明を分離
- "LGTM" 出力の場合は指摘件数 0 として扱う

#### Step 4: プレビューと投稿確認

`AskUserQuestion` でユーザーにプレビューを表示し、投稿の承認を得る:

```
--- PR #123 へのレビューコメント プレビュー ---

投稿方法: インラインコメント（3件）

1. [MUST] src/auth.go:42 - nil チェックが抜けている
2. [CONSIDER] src/handler.go:88 - エラーメッセージが曖昧
3. [NIT] src/utils.go:15 - 変数名が不明瞭

投稿してよいですか？ (yes/no)
```

**ユーザーが承認しない限り、絶対に投稿しない。**

#### Step 5: 投稿方法の選択と実行

| 指摘件数 | 投稿方法 | コマンド |
|---------|----------|----------|
| 0（LGTM） | Approve | `gh pr review <N> --approve --body "LGTM -- Codex review passed"` |
| 1-5 | インラインコメント | `gh api` で個別ファイル:行にコメント |
| 6+ | 総合コメント | `gh pr review <N> --comment --body "..."` |

**MUST 指摘がある場合は、指摘件数 0 でも approve してはならない。**

##### インラインコメント（1-5件）の投稿

PR の最新コミット SHA を取得し、各指摘をインラインコメントとして投稿する:

```bash
# リポジトリ情報と最新コミット SHA を取得
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
COMMIT_SHA=$(gh pr view <N> --json headRefOid --jq '.headRefOid')

# 各指摘をインラインコメントとして投稿
gh api "repos/${REPO}/pulls/<N>/comments" \
  -f body="[MUST] nil チェックが抜けている" \
  -f commit_id="$COMMIT_SHA" \
  -f path="src/auth.go" \
  -F line=42 \
  -f side="RIGHT"
```

##### 総合コメント（6件以上）の投稿

全指摘を Markdown テーブルにまとめて投稿する:

```bash
gh pr review <N> --comment --body "$(cat <<'EOF'
## Codex Review Summary

| Severity | File | Line | Description |
|----------|------|------|-------------|
| MUST | src/auth.go | 42 | nil チェックが抜けている |
| CONSIDER | src/handler.go | 88 | エラーメッセージが曖昧 |
...

_Reviewed by Codex AI (gpt-5.4, reasoning_effort=xhigh)_
EOF
)"
```

##### LGTM（指摘なし）の投稿

```bash
gh pr review <N> --approve --body "LGTM -- Codex review passed. No issues detected."
```

## いつ使うか

- 大規模リファクタリング後のセカンドオピニオン
- リリース前の最終レビュー
- CHANGELOG.md の更新が必要なとき
- S 規模以上の全変更で Review Gate として起動（reasoning_effort: xhigh）
- M/L 規模では code-reviewer + 言語専門レビューアーと並列起動
- **セキュリティ特化**: 認証・暗号・API エンドポイント・依存関係の変更時
- **PR コメント投稿**: `--post-to-pr <N>` でレビュー結果を GitHub PR に直接投稿したいとき

## Gotchas

- **レート制限**: Codex CLI は API レート制限に引っかかることがある。429 エラー時は 30秒待って再試行
- **日本語コメントの扱い**: reasoning_effort=xhigh でも日本語コメント内の意図を誤解することがある。レビュー指摘が的外れな場合はスキップ
- **--skip-git-repo-check 必須**: dotfiles のような symlink リポジトリでは git repo 検出に失敗するため、常にこのフラグが必要
- **大きすぎる diff**: 500行超の diff は Codex のコンテキストを圧迫する。`--stat` で概要を先に確認し、ファイル単位で分割レビューを検討
- **2>/dev/null の副作用**: エラー出力を捨てているため、Codex CLI 自体のエラー（認証切れ等）が見えなくなる。問題時は外して実行

## Skill Assets

- レビュー出力テンプレート: `templates/review-output.md`
- レビューチェックリスト: `references/review-checklist.md`

## Anti-Patterns

| NG | 理由 |
|----|------|
| Codex の指摘を無批判に適用する | Codex も誤判定する。指摘は検証してから適用する |
| codex-review でコードを編集する | read-only スキル。編集が必要なら /codex を使う |
| 確認なしに PR にコメント投稿する | 誤った指摘を投稿すると PR が荒れる。必ず AskUserQuestion でプレビュー+承認を得る |
| MUST 指摘があるのに LGTM として approve する | 矛盾した状態になる。MUST 指摘がある場合は approve ではなく comment で投稿する |
