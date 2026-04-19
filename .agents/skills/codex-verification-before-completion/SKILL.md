---
name: codex-verification-before-completion
description: Mandatory verification workflow for Codex. Use before declaring work complete, after edits, before commit or review-ready reports, or whenever you need evidence from build, test, lint, diff, or validation commands.
platforms: [agents, codex]
---

# Codex Verification Before Completion

完了宣言の前に、必ず実コマンドを実行して結果を確認する。

## Workflow

1. 変更対象に最も近い validation を選ぶ。
2. review-ready report や複数領域変更では、必要なら `pr_explorer`、`reviewer`、`docs_researcher` の subagent review を先に走らせる。
3. build / test / lint / typecheck / diff のうち必要なものだけ実行する。
4. exit code と要点を確認する。
5. 失敗があれば修正し、同じコマンドを再実行する。
6. 実行できない場合は、その理由を明示して完了扱いにしない。

## Minimum Evidence

- 実行したコマンド
- exit code
- 重要な warning / failure の有無
- `git diff --stat` または同等の差分確認
- subagent review を使った場合は、その findings を最終判断へ統合したこと

## Dotfiles Hints

- config / script 変更: `task validate-configs`
- README / doc 変更: `task validate-readmes`
- symlink / `.codex` / `.claude` 変更: `task validate-symlinks`
- 複数領域変更: `task validate`
- validation 選定に迷う場合: `validation_explorer` を使うか、`Taskfile.yml` と `.bin/validate_*.sh` を直接読む

## Anti-Patterns

- コマンド未実行で「完了」と言う
- 古い成功結果を使い回す
- failure を把握せずに warning 扱いで流す
- diff を見ずに副作用なしと判断する
