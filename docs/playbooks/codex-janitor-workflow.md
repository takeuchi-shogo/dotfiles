# Codex Janitor Workflow

`slop-janitor` の発想を、この repo の Codex harness に合わせて取り込むための playbook。

## Goal

- 同じ問題を同じ Codex session で反復する
- `find-best-refactor -> improve -> implement -> review` を deterministic に回す
- stopping rule、artifact、validation を repo 側に残す

## Entry Points

- `python3 tools/codex-janitor/runner.py --dry-run`
- `python3 tools/codex-janitor/runner.py --prompt "focus on testability"`
- `task codex-janitor -- --dry-run`
- `task codex-janitor -- --prompt "simplify codex workflow boundaries"`

## Current Contract

- stable CLI surface のみを使う
  - `codex exec`
  - `codex exec resume`
- initial stage で session を作り、その後は同じ session id に `resume` する
- stage ごとの raw stdout/stderr と final message を `tmp/codex-janitor/runs/` に保存する
- `skip` と low usefulness score で early stop する

## Safety Rules

- dirty repo ではデフォルトで実行しない
- 長時間試行や invasive な refactor は worktree で分離する
- approval は `approval_policy="never"` を command override で固定し、非対話実行を保つ
- global rule や Claude 側 hook に頼らず、runner の artifact だけで postmortem できる状態にする

## Worktree Guidance

- 推奨:
  - `git worktree add ../dotfiles-janitor -b chore/codex-janitor-run`
  - `cd ../dotfiles-janitor`
  - `task codex-janitor -- --prompt "focus on codex harness simplification"`
- main workspace が dirty のときに `--allow-dirty` で押し切らない

## Stopping Rules

- assistant が `skip` を返した
- `Usefulness score: N/10` で `N <= 3`
- stage command が non-zero で失敗した
- session file を取得できず continuity が壊れた

## Artifacts

- `tmp/codex-janitor/runs/<timestamp>-<workflow>/manifest.json`
- `tmp/codex-janitor/runs/<timestamp>-<workflow>/stages/*/stdout.jsonl`
- `tmp/codex-janitor/runs/<timestamp>-<workflow>/stages/*/stderr.log`
- `tmp/codex-janitor/runs/<timestamp>-<workflow>/stages/*/last-message.txt`

## Validation

- implementation changes:
  - `python3 -m unittest discover -s tools/codex-janitor/tests -p 'test_*.py' -v`
- dotfiles config changes:
  - `task validate-configs`
  - `task validate-symlinks`
- playbook or README changes:
  - `task validate-readmes`

## Follow-Ups

- `--worktree auto` の自動作成/cleanup
- usefulness 以外の stop condition
  - no-op diff
  - validation failure summary
  - token or time budget
- workflow 定義の複数化
  - refactor loop
  - branch review loop
  - docs consistency loop
