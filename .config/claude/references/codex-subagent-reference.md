---
status: reference
last_reviewed: 2026-04-23
---

# Codex Subagent Reference (.codex/AGENTS.md 退避先)

`.codex/AGENTS.md` から分離した Subagent Usage の詳細 (2026-04-23)。

## Configured Custom Agents

| Agent | Model | 用途 | Sandbox |
|---|---|---|---|
| `pr_explorer` | `gpt-5.3-codex-spark` | diff の影響範囲・依存関係マッピング | `read-only` |
| `reviewer` | `gpt-5.5` | correctness / security / test gap レビュー | `read-only` |
| `docs_researcher` | `gpt-5.3-codex-spark` | ドキュメント・config の整合確認 | `read-only` |
| `validation_explorer` | `gpt-5.3-codex-spark` | dotfiles 変更に対する最小 validation 選定 | `read-only` |
| `search_specialist` | `gpt-5.3-codex-spark` | search-first 段階の codebase / external source 探索 | `read-only` |
| `security_auditor` | `gpt-5.5` | auth / secrets / validation / config の security 深掘り | `read-only` |
| `debugger` | `gpt-5.5` | failing validation / runtime anomaly / test failure の切り分け | `read-only` |

## 使い方

- subagent は親 agent に明示的に依頼して起動する
- 並列委譲で独立した観点を調査させ、親 agent が統合する
- 全 custom agent は read-only。ファイル編集は親 agent が行う
- subagent の主目的は速度だけでなく context isolation であり、noisy な探索を main thread に積まないために使う
- `search_specialist` は search-first や外部調査の初動で使う
- `security_auditor` は `.codex/`、`.mcp.json`、script、auth、secrets、input validation の変更で使う
- `debugger` は validation failure、CLI 挙動不良、再現が曖昧な不具合の切り分けで使う

## Branch Review パターン

```text
Review this branch with parallel subagents.
Use pr_explorer for code path mapping, reviewer for correctness/security/test gaps, and docs_researcher for documentation/config consistency.
Wait for all three, then return a prioritized summary with file references.
```

## Repo Exploration パターン

```text
Explore this repo with parallel subagents.
Use pr_explorer on the target directory structure, docs_researcher on documentation and config files.
Return consolidated findings without proposing edits.
```

## Validation Selection パターン

```text
Choose the smallest sufficient validation commands for this change.
Use validation_explorer on Taskfile.yml, validate scripts, change surface matrix, and nearby README guidance.
Return recommended commands in priority order with rationale, and do not run commands.
```

## Runtime 制御

- `max_threads = 4`: 同時 subagent 数。token 消費を見て調整
- `max_depth = 1`: subagent の subagent は禁止
- subagent は親の sandbox を継承するが、custom agent 側で `read-only` に上書き済み

## 注意事項

- `codex --version` と `codex features list` で runtime 状態を確認すること
- 2026-03-17 時点のローカル確認では `codex-cli 0.115.0`、`multi_agent stable true`
- 2026-03-19 時点のローカル確認では `codex execpolicy check` は使えるが、`bash -lc ...` / `zsh -lc ...` の shell wrapper は match を返さなかった。`Rules` は direct command token 前提で検証する
- `child_agents_md` は未有効のため、agent 固有の運用ガイドは引き続き `.codex/AGENTS.md` と playbook で管理する
- custom agent 定義は current CLI が受け付ける最小項目に寄せ、追加フィールドを入れたら local parser か `codex review --uncommitted` で確認する
- custom agent 名解決や UI 表示の挙動は CLI 更新時に再確認する
- write-capable subagent は Phase 2 で検討。現時点では read-only のみ

## 詳細 playbook

- `docs/playbooks/codex-subagent-usage.md` — テンプレートと事例
