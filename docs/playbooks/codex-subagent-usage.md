# Codex Subagent Usage

Codex の subagent を dotfiles で使うときの playbook。

## When To Use

- branch review で複数観点を並列に見たい
- repo exploration をしつつ親 agent の文脈を汚したくない
- validation selection を変更実体と切り分けて調べたい
- docs / config / code path を別観点で独立に見たい

## When Not To Use

- 次の手が subagent の結果に即依存していて、親がすぐ自分で読んだ方が速い
- 同じファイル群へ同時編集を入れたい
- 役割が曖昧で、結局どの agent に何を任せるか説明できない

## Default Roles

- `pr_explorer`
  - diff、依存関係、影響範囲の把握
- `reviewer`
  - correctness、security、test gap のレビュー
- `docs_researcher`
  - README、AGENTS、docs、config、Taskfile の整合確認
- `validation_explorer`
  - `Taskfile.yml`、`.bin/validate_*.sh`、change surface matrix、README から最小 validation を選定
  - この agent は導入後に使用する

## Optional Specialist Roles

- `search_specialist`
  - search-first 段階の codebase / external source 探索
- `security_auditor`
  - auth、secrets、input validation、config、script の focused security review
- `debugger`
  - failing validation、CLI anomaly、runtime bug、failing test の root-cause isolation

## Framing Rules

- subagent には query だけでなく `objective` を渡す
- `scope` を明示し、触ってよい file / directory を絞る
- `expected output` を固定し、親 agent が統合しやすい返却形式にする
- read-only agent には編集提案ではなく findings / mapping / command candidates だけを返させる

## Output Contract

各 subagent には次を要求する。

- file references
- 優先度、または重要度
- 根拠を 1-2 文
- 不明点があれば assumptions として分離

親 agent は次を担当する。

- 重複 findings の統合
- 実際の編集
- validation 実行と最終判断
- requirements、decision、final output を main thread に保つこと

## Standard Templates

### Branch Review

使いどころ:
- diff review
- correctness と docs 整合を分離したい review

起動:
- `pr_explorer`
- `reviewer`
- `docs_researcher`

親から渡す内容:

```text
Objective: Review this branch without editing files.
Scope:
- diff against <base branch>
- touched files and directly related neighbors
Expected output:
- pr_explorer: impacted files, dependencies, likely follow-on touchpoints
- reviewer: prioritized correctness, security, and missing-test findings
- docs_researcher: stale docs/config/README references caused by this change
Return concise findings with file references only.
```

待機条件:
- 親の次の判断が review 結果に依存するため、通常は全 agent を待つ

### Repo Exploration

使いどころ:
- 実装前の全体把握
- docs と config を並列に読みたい調査

起動:
- `pr_explorer`
- `docs_researcher`

親から渡す内容:

```text
Objective: Map the relevant parts of this repo before edits.
Scope:
- target directories only
- nearby docs, configs, and validation scripts
Expected output:
- structure map
- key files to read next
- risks or hidden touchpoints
Do not propose edits yet.
```

待機条件:
- 親が別の非重複作業を進められるなら並行で進め、必要になった時点で待つ

### Validation Selection

使いどころ:
- dotfiles 変更後に最小 validation を決めたい
- symlink、config、README のどこまで検証するか迷う

起動:
- `validation_explorer`
  - 未導入なら親 agent が `Taskfile.yml` と `.bin/validate_*.sh` を直接読む

親から渡す内容:

```text
Objective: Choose the smallest sufficient validation commands for this change.
Scope:
- changed files
- Taskfile.yml
- related validate scripts
- change surface matrix and nearby README guidance
Expected output:
- recommended commands in priority order
- why each command is needed
- any optional checks that can be skipped
Do not run commands.
```

待機条件:
- 実編集後の verification に直結するため、必要になった時点で待つ

## Rules

- `max_depth = 1` を守る
- write-capable subagent は使わない
- 同じ観点の subagent を重複起動しない
- 緊急の blocking work は親 agent が自分で処理する
- subagent は parallel worker であると同時に parallel context でもある。探索ノイズを main thread に持ち込まないために使う
- main thread は要件整理、比較判断、統合、最終報告に集中させる

## Watchouts

- `multi_agent` の可用性は `codex --version` と `codex features list` で確認する
- custom agent 名解決が不安定なら built-in `explorer` / `worker` へ一時退避する
- background agent 由来の approval が起きうる前提で、sandbox は保守的に保つ

## Minimum Validation

- playbook 追加・更新時は `task validate-readmes`
- `.codex/` と合わせて変える場合は `task validate-symlinks`
