---
name: codex-review
description: >
  Codex AI を使った read-only コードレビューと CHANGELOG 自動生成。手動レビュー(/codex-review)や
  自動レビューフロー(general-purpose Agent経由)で使用。実装・編集には codex スキルを使うこと。
  Do NOT use for standard code reviews under 100 lines — use /review skill instead.
allowed-tools: "Read, Bash, Grep, Glob, Agent"
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

## いつ使うか

- 大規模リファクタリング後のセカンドオピニオン
- リリース前の最終レビュー
- CHANGELOG.md の更新が必要なとき
- 200行超の変更で code-reviewer + 言語専門レビューアーに追加して使用
