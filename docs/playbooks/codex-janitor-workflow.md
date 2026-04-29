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
- `no_op_diff`: stage 完了後も HEAD SHA / working tree が変化しない
- `validation_failed:<tail>`: `[stop_rules.validation]` で指定した command が non-zero
- `time_budget_exceeded:<seconds>`: 累積 wall clock が `[stop_rules.time_budget].seconds` を超過
- `snapshot_drift:<reason>`: apply 系 stage 直前で commit/file 状態が start から drift（後述）
- `destructive_without_evidence:deletions=N,insertions=M`: 大量削除 + low usefulness の同時発生

When in doubt, skip — `destructive_without_evidence` と `usefulness_below_threshold` は判断保留シグナル。confidence が低いまま破壊的変更を進めるより、停止して人間が見る方が安全。

## Single-run Drift Detection

`[stop_rules.snapshot_drift]` を有効化すると、run 開始時に `snapshot_start` (commit + 影響ファイル sha256) を記録する。`apply_labels` に該当する label を持つ stage の **直前** に再 snapshot を取り、commit または影響ファイルが変化していれば該当 stage を skip して run を停止する。

**Scope は single-run 内のみ**:

- cron tier 化 (hot/warm/cold) や cross-run snapshot 比較は **対象外**。個人 dotfiles で頻発する手動編集と衝突して friction を生むため、本機構を always-on の watchdog として広げない。
- `apply_labels` のデフォルトは `["implement"]`。custom workflow で apply 系 stage label を変えた場合は toml で上書き。

`manifest.json` には `snapshot_start` / `snapshot_pre_apply` フィールドが記録され、stage ごとに `decision` (`verdict` + `reason`) と `evidence` ([{kind, ref}]) が含まれる。

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
- ~~usefulness 以外の stop condition~~ — **Implemented (2026-04-29)**: `no_op_diff` / `validation_failed` / `time_budget_exceeded` (wall clock fallback) / `snapshot_drift` / `destructive_without_evidence`
- workflow 定義の複数化
  - refactor loop
  - branch review loop
  - docs consistency loop
- Codex CLI が token usage を `--json` 出力するようになったら `time_budget` を token-based に拡張
