---
status: reference
last_reviewed: 2026-04-23
---

# Negative Knowledge Playbook

「やるな」知識の構造化ストア。session-learner が自動追記、/improve が参照する。

## 手書きエントリ

下の表は session-learner の自動追記。人が書いた「やるな」はここに置く。

### Codex の名前付き custom agent は作らない (2026-08-02)

codex-cli 0.144.6 の `spawn_agent` が取るパラメータは 3 つだけ。

```
task_name
message
fork_turns
```

`agent_type` が無いので、`.codex/agents/*.toml` に custom agent を定義しても選ぶ手段がない。
「Sol をオーケストレータ、Luna Max を worker に」系の記事はこの前提で書かれているが、
少なくともこの機体では成立しない。過去に 12 個定義して 5 ヶ月間 1 度も動かなかった
(`docs/plans/2026-03-17-codex-subagents-improvement.md:410` に `unknown agent_type` の観測が残る)。

Codex 側でモデルを使い分けるなら `codex exec -m <model>` を使う。
**`[profiles.*]` は使えない** — 0.144.6 は legacy profile テーブルを拒否する。

```
Error loading config.toml: --profile `review` cannot be used while
/Users/takeuchishougo/.codex/config.toml contains legacy `profile = "review"` or
`[profiles.review]` config; move those settings into
/Users/takeuchishougo/.codex/review.config.toml and remove the legacy profile selector/table.
```

profile は `$CODEX_HOME/<name>.config.toml` の別ファイル方式に移行した (`rules/codex-delegation.md:151`)。
`~/.codex/config.toml` には `[profiles.*]` が 6 個残っていて、いずれも `-p` で選べない。

**撤退条件**: 次のコマンドで `agent_type` が現れたら、この判断は無効になる。

```bash
codex exec --skip-git-repo-check --sandbox read-only -c model_reasoning_effort=low \
  "List the parameter names of your spawn_agent tool, one per line. Nothing else."
```

| Date | Project | Anti-Pattern | Reason | Outcome |
|------|---------|-------------|--------|---------|
| 2026-04-04 | dotfiles | [FM-007] Error: Cannot find module ./utils from src/index.ts |  | failure |
| 2026-04-04 | dotfiles | [FM-007] Error: Cannot find module ./utils from src/index.ts |  | failure |
| 2026-04-04 | dotfiles | [FM-008] TypeError: undefined is not a function |  | failure |
| 2026-04-14 | dotfiles | [FM-000] (exit_code!=0, no output) — post-bash hook test entry | hook self-test | failure |
| 2026-04-14 | dotfiles | [FM-008] TypeError: Cannot read property | hook self-test | failure |
| 2026-04-14 | dotfiles | [FM-009] 設定ファイルが見つかりません (config file not found) | hook self-test | failure |
