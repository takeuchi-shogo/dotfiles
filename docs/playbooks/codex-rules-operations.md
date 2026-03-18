# Codex Rules Operations

Codex の `Rules` をこの repo で使うときの最小運用メモ。

## Purpose

- `AGENTS.md`
  - 自然言語の行動方針
- `.codex/rules/*.rules`
  - sandbox 外 command の機械判定

同じ承認を繰り返している command prefix だけを `.rules` に昇格する。

## File Location

- user / repo layer の第一候補: `.codex/rules/default.rules`

この repo では `~/.codex` が `.codex/` に symlink されるため、repo 内で管理してよい。

## Decision Policy

- `allow`
  - 完全に read-only で、反復度が高く、prefix も狭いもの
- `prompt`
  - 有用だが毎回無条件に通したくないもの
- `forbidden`
  - 既存方針上ほぼ常時禁止したい destructive prefix

初回導入では broad allowlist を作らない。

## Authoring Rules

- `prefix_rule()` には必ず `justification` を付ける
- `match` と `not_match` を付けて意図した prefix だけに効くか確認する
- shell wrapper を前提に抜け道を作らない
- `forbidden` には代替行動を `justification` に書く

## Verification

代表例は `codex execpolicy check` で確認する。

```bash
codex execpolicy check --pretty \
  --rules .codex/rules/default.rules \
  -- git status
```

compound command も 1 つ確認する。

```bash
codex execpolicy check --pretty \
  --rules .codex/rules/default.rules \
  -- bash -lc "git status && git reset --hard HEAD"
```

期待値:

- read-only prefix は `allow`
- review や重い command は必要に応じて `prompt`
- destructive prefix が混ざる compound command は最終的に `forbidden`

注意:

- 公式 docs は単純な `bash -lc` / `zsh -lc` command chain を分解評価できると説明している
- ただし 2026-03-19 時点の local `codex-cli 0.115.0` で `codex execpolicy check` を試した範囲では、shell wrapper invocation は match を返さなかった
- そのため、この repo では shell wrapper 分解に依存せず、まず direct command token に対する rule を整備する
- shell wrapper の挙動は CLI 更新時に再確認する

## Rollout

1. `.codex/rules/default.rules` を更新する
2. `codex execpolicy check` で representative command を確認する
3. `.codex/AGENTS.md` と必要な contract/playbook を更新する
4. `task validate-configs`
5. `task validate-symlinks`
6. docs を変えたら `task validate-readmes`
7. Codex を再起動する

## Initial Rules In This Repo

- `allow`
  - `git status`
  - `git diff`
  - `git log`
  - `codex execpolicy check`
- `prompt`
  - `codex review --uncommitted`
- `forbidden`
  - `git reset --hard`
  - `git checkout --`

このセットは「よく使う read-only inspection を低摩擦化し、既存 repo 方針で避けている destructive revert を明示的に止める」ための最小導入。
