---
name: codex-review
description: Codex AI を使ったコードレビューと CHANGELOG 自動生成。大規模リファクタリングやリリース前のレビューに使用。
---

# Codex Review

## 使い方
1. レビュー対象の変更を `git diff` で確認
2. Codex CLI を read-only モードで実行してレビュー:
   ```bash
   codex exec --skip-git-repo-check -m gpt-5.2 --config model_reasoning_effort="high" --sandbox read-only "Review the following changes for bugs, security issues, and code quality. Provide actionable feedback." 2>/dev/null
   ```
3. レビュー結果を元に修正を適用

## CHANGELOG 自動生成
```bash
codex exec --skip-git-repo-check -m gpt-5.2 --config model_reasoning_effort="medium" --sandbox read-only "Generate a CHANGELOG entry for the recent changes based on git log and conventional commits format." 2>/dev/null
```

## いつ使うか
- 大規模リファクタリング後のセカンドオピニオン
- リリース前の最終レビュー
- CHANGELOG.md の更新が必要なとき
