# Setup Doctor — Spec

**Status**: Draft
**Created**: 2026-05-13
**Owner**: takeuchi-shogo
**Platform**: macOS (nix-darwin) only — Linux/WSL は対象外 (`darwin-rebuild` 等 macOS 固有 binary を前提)

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
| `binary` | 必須 binary 存在 + minimum version を **required / recommended / bootstrap-gated** で分類: **required** (不在=FAIL): rtk≥0.39, jq, gh, task, git, brew. **recommended** (不在=WARN): sheldon, direnv, mise, starship, claude (npm経由). **bootstrap-gated** (`darwin-rebuild` は `task nix:bootstrap` 後に出現する前提なので、未実行マシンでは SKIP) | hook が ENOENT、Taskfile が動かない |
| `symlink` | 既存 `validate-symlinks` を継承し、`~/.claude/`, `~/.config/`, `~/.zshrc` 配下の管理対象 link を確認 | dotfiles の編集が反映されない |
| `nix` | `nix flake check` + `hostname` と適用済み profile の整合 (private/work) | 別 profile を誤適用、再起動後の設定 drift |
| `hook` | settings.json の hook `command` を **静的 validation のみ** (read-only 厳守): (a) 第1トークンを resolve して binary 存在確認、(b) `rtk hook claude` のような subcommand を `<binary> <sub> --help` で「subcommand 認識可否」を確認、(c) `$HOME` 等の env 展開後パス存在確認。**実行 (空 JSON 投入含む) は禁止** — このリポジトリの hook は memory sync / background job / sound 再生等 side effect を持つため、health check のたびにマシン状態を破壊する | Claude Code 上の hook fail |
| `brew` | nix-darwin `homebrew.brews` + `homebrew.taps` の宣言と `brew list` / `brew tap` の差分 | 宣言したのに未 install / Cellar mismatch / tap 未追加 |

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
6. 「困った具体例」5 件 (本 spec 冒頭の表) を**全て検出できる**ことを **2 系統の fixture** で証明: (a) **input mock** = `PATH` を `tests/fixtures/doctor/bin-stubs/` で前置きし `rtk`/`brew`/`darwin-rebuild` 等を stub script (例: `echo "rtk 0.35.0"; exit 0`) に差し替え、(b) **golden output** = `tests/fixtures/doctor/expected/*.txt` に finding の期待値を保存し diff で比較。実環境の rtk を 0.35 にダウングレードする方式や hook 実行による fixture 生成は禁止。

## Open questions (decide during plan)

- Q1: minimum version の定義をどこに置くか → `.config/claude/references/setup-requirements.md` に YAML/TOML テーブルで一元化
- Q2: `task doctor` を pre-commit (lefthook) で走らせるか → **No** (環境依存で flaky になるため手動 only)

(言語選択 (shell vs Rust) と fixture 形式は plan の reversible decisions / 上記 acceptance criteria #6 で確定済み。元 Q4 (hook smoke test 入力) は read-only 化により消滅)

## Out of scope (explicitly NOT in this PR)

- 自動修復 (`task doctor:fix`) は Phase 2 で別 spec
- CI 統合は Phase 3 (GitHub Actions matrix で macOS-15 + macOS-14 の health check)
- 新マシン bootstrap chain (`task install` → `task doctor` → `task nix:bootstrap`) の orchestration

## References

- 既存検証: `Taskfile.yml` の `validate-*` ファミリ
- ハーネス契約: `docs/agent-harness-contract.md`
- harness stability: `.config/claude/references/harness-stability.md` (30-day evaluation rule)
- 撤退条件のひな型: `.config/claude/references/reversible-decisions.md`
- 失敗モード: `.config/claude/references/pre-mortem-checklist.md`
