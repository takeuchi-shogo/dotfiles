# Setup Doctor — Spec

**Status**: Draft
**Created**: 2026-05-13
**Owner**: takeuchi-shogo

## Why now

別マシン (work profile) で dotfiles を bootstrap した際、以下の症状が混在して切り分けに時間を要した:

| 症状 | 具体例 (このセッションで遭遇) |
|---|---|
| バージョン drift | `rtk` 0.35 のローカルに対し settings.json が 0.39 の `rtk hook claude` を呼んで `[rtk: No such file or directory (os error 2)]` |
| 未インストールバイナリ | nix-darwin `homebrew.brews` に追加した formula がローカルに未 apply、`task` / `jq` 等の前提 binary 不在 |
| Symlink 抜け | `~/.claude/` 配下の一部ファイルが dotfiles 管理から漏れて旧版が残存 |
| Profile mismatch | `darwin-rebuild switch --flake .#private` 想定のマシンで `#work` を適用するなどの取り違え |
| Hook 起動失敗 | settings.json の hook `command` が PATH 不整合や旧 subcommand で `exit≠0`、Claude Code 上で `Failed with non-blocking status code` 連発 |

既存 `task validate-{configs,agents,readmes,symlinks}` は **静的 syntax 検証のみ**で、上記の動的・環境依存な問題を検出できない。

## Scope (what `task doctor` checks)

| カテゴリ | 検出対象 | 失敗時の症状 |
|---|---|---|
| `binary` | 必須 binary 存在 + minimum version (rtk≥0.39, jq, gh, task, sheldon, direnv, mise, starship, git, brew, darwin-rebuild, claude) | hook が ENOENT、Taskfile が動かない |
| `symlink` | 既存 `validate-symlinks` を継承し、`~/.claude/`, `~/.config/`, `~/.zshrc` 配下の管理対象 link を確認 | dotfiles の編集が反映されない |
| `nix` | `nix flake check` + `hostname` と適用済み profile の整合 (private/work) | 別 profile を誤適用、再起動後の設定 drift |
| `hook` | settings.json の hook `command` を **dry-run smoke test** (空 JSON を stdin で投入し exit code 確認) | Claude Code 上の hook fail |
| `brew` | nix-darwin `homebrew.brews` 宣言と `brew list` の差分 | 宣言したのに未 install / Cellar mismatch |

### Non-goals

- 自動修復は **Phase 2 以降**。本 spec の MVP は **検出のみ** (read-only)。
- npm/cargo/pip 等の言語別 lockfile 検証は `dependency-auditor` skill 側の責務。
- ネットワーク依存テスト (homebrew tap reachability、claude.ai 疎通) はスコープ外。

## Acceptance criteria

1. `task doctor` 単体で全カテゴリを順次実行し、終了コードは `failure 0件 → 0`, `≥1件 → 1`。
2. 各 finding は `[CATEGORY] severity: message (hint)` の 1 行形式で stdout に出力。例:
   ```
   [binary] FAIL: rtk 0.35.0 found, requires ≥0.39.0 (run: brew upgrade rtk)
   [hook]   WARN: command "rtk hook claude" subcommand missing (rtk version too old)
   [nix]    OK:   hostname=MacBookPro matches profile=private
   ```
3. `task doctor:<category>` で個別実行可能 (例: `task doctor:binary`)。
4. 既存 `task validate` は **変更なし** (互換維持)。`task doctor` は新規 task として並列追加。
5. `--json` フラグ (将来) のための内部表現は構造化されているが、MVP では plain text 出力で可。
6. 「困った具体例」5 件 (本 spec 冒頭の表) を**全て検出できる**ことを test fixture で証明。

## Open questions (decide during plan)

- Q1: 単一 shell script (`scripts/lifecycle/doctor.sh`) か Rust binary (`tools/claude-hooks` 流用) か → **shell first** で開始、200 行超えたら Rust 再検討
- Q2: minimum version の定義をどこに置くか → `references/setup-requirements.md` に YAML/TOML テーブルで一元化
- Q3: `task doctor` を pre-commit (lefthook) で走らせるか → **No** (環境依存で flaky になるため手動 only)
- Q4: hook smoke test の入力 JSON は何を使うか → `tests/fixtures/hook-smoke-input.json` に共通 fixture

## Out of scope (explicitly NOT in this PR)

- 自動修復 (`task doctor:fix`) は Phase 2 で別 spec
- CI 統合は Phase 3 (GitHub Actions matrix で macOS-15 + macOS-14 の health check)
- 新マシン bootstrap chain (`task install` → `task doctor` → `task nix:bootstrap`) の orchestration

## References

- 既存検証: `Taskfile.yml` の `validate-*` ファミリ
- ハーネス契約: `docs/agent-harness-contract.md`
- harness stability: `references/harness-stability.md` (30-day evaluation rule)
- 撤退条件のひな型: `references/reversible-decisions.md`
- 失敗モード: `references/pre-mortem-checklist.md`
