---
name: codex-review
description: >
  Codex AI を使った read-only コードレビューと CHANGELOG 自動生成。手動レビュー(/codex-review)や
  自動レビューフロー(general-purpose Agent経由)で使用。実装・編集には codex スキルを使うこと。
  Do NOT use for standard code reviews under 100 lines — use /review skill instead.
allowed-tools: "Read, Bash, Grep, Glob, Agent"
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

## いつ使うか

- 大規模リファクタリング後のセカンドオピニオン
- リリース前の最終レビュー
- CHANGELOG.md の更新が必要なとき
- 200行超の変更で code-reviewer + 言語専門レビューアーに追加して使用
- **セキュリティ特化**: 認証・暗号・API エンドポイント・依存関係の変更時

## Gotchas

- **レート制限**: Codex CLI は API レート制限に引っかかることがある。429 エラー時は 30秒待って再試行
- **日本語コメントの扱い**: reasoning_effort=xhigh でも日本語コメント内の意図を誤解することがある。レビュー指摘が的外れな場合はスキップ
- **--skip-git-repo-check 必須**: dotfiles のような symlink リポジトリでは git repo 検出に失敗するため、常にこのフラグが必要
- **大きすぎる diff**: 500行超の diff は Codex のコンテキストを圧迫する。`--stat` で概要を先に確認し、ファイル単位で分割レビューを検討
- **2>/dev/null の副作用**: エラー出力を捨てているため、Codex CLI 自体のエラー（認証切れ等）が見えなくなる。問題時は外して実行
