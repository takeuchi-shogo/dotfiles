# Setup Doctor — Implementation Plan

**Spec**: [docs/specs/2026-05-13-setup-doctor.md](../../specs/2026-05-13-setup-doctor.md)
**Size**: M (Plan → Codex Spec/Plan Gate → Edge Case → Implement → Test → Codex Review Gate → Verify)
**Branch**: 本 PR は **spec/plan のみ**。実装は別 PR (`feat/setup-doctor-phase1`)。

## Phase breakdown

### Phase 0 — Spec + Plan (this PR)
- 仕様確定とレビューによる合意形成のみ
- 実装ファイルゼロ
- 完了条件: spec/plan が merge され、Phase 1 着手 OK

### Phase 1 — Detection MVP (read-only)
- `scripts/lifecycle/doctor.sh` 新設
- 5 カテゴリの check 関数を実装 (`check_binary`, `check_nix`, `check_hook`, `check_brew`)。`symlink` カテゴリは新規実装せず `Taskfile.yml` 内で `deps: [validate-symlinks]` として既存 task を引用する (重複排除、pre-mortem 行と一貫)
- `references/setup-requirements.md` で minimum version を一元定義
- `Taskfile.yml` に `doctor` + `doctor:<category>` 追加
- Test fixture: 「困った 5 例」を再現する dry-run スナップショット
- 完了条件: spec の acceptance criteria 6 項目を満たす

### Phase 2 — Repair suggestions (still read-only)
- 各 finding に対し machine-readable な `hint:` を付与
- `task doctor --suggest` で fix コマンドの一覧出力 (実行はしない)
- 完了条件: 全 finding に hint があり、人間が copy-paste で fix 可能

### Phase 3 — Optional auto-fix (opt-in)
- `task doctor:fix` で危険度の低い fix (brew upgrade, symlink relink) を実行
- 危険な fix (nix profile 切替) はガード付きで confirm
- 完了条件: Phase 2 の hint のうち **safe category (brew upgrade / symlink relink) の idempotent fix 100%**。danger category (nix profile 切替、binary downgrade) は対象外

## Reversible decisions (撤退条件)

| 決定 | 撤退条件 |
|---|---|
| shell script で実装 | `doctor.sh` が **`.bin/validate_*.sh` の最大行数 × 1.5 倍**を超える OR check 関数が 8 以上 → Rust 再評価。Phase 1 着手時に最大行数を計測し閾値を確定 |
| Phase 1 を read-only | Phase 1 merge 後 30 日で 0 invocation → harness-stability に従い削除検討 |
| `references/setup-requirements.md` を YAML | parse コスト > 価値の証跡 (`time task doctor` > 2s) → plain bash array に縮退 |

## Pre-mortem (失敗モード)

| 失敗モード | 対策 |
|---|---|
| **過剰検出**: 開発中ブランチで FAIL 連発 → 信頼喪失 | カテゴリごとに `WARN` と `FAIL` を区別、デフォルト exit は FAIL のみ非ゼロ |
| **PATH 環境差で false-positive**: GUI 起動 vs ターミナル起動 | doctor は **対話シェル前提**と明記、GUI 起動はサポート外 |
| **rtk のような mid-flight upgrade**: stable と HEAD で挙動差 | minimum version は spec に明記、HEAD 依存は別マーカーで管理 |
| **brew tap drift**: tap だけ追加忘れ | `check_brew` で `homebrew.taps` の宣言と `brew tap` 結果を diff |
| **Profile mismatch を fail にできない**: 単一 profile マシンでは正常 | `hostname` ベースの heuristic + `~/.dotfiles-profile` override file 検討 (Phase 2) |
| **既存 `validate-*` との重複**: 同じ check が 2 箇所 | `task doctor` 内で `task: validate-symlinks` を呼ぶ (引用)。新規 `check_symlink` は書かない |
| **sudo PATH 喪失で `darwin-rebuild` not found**: `sudo` 経由で呼ぶと user PATH が消えて nix 関連 binary が見えない (別マシン bootstrap で頻発) | `check_nix` は `/run/current-system/sw/bin/darwin-rebuild` を絶対パスで存在確認 |
| **対話型 CLI が stdin 待ちで hang**: codex 等が prompt を出すと doctor 自体が止まる (本セッションで実発生) | 全 external call を `timeout 5s` で wrap、subcommand 確認は `</dev/null` を必ず stdin に与える |
| **nix-darwin `homebrew.brews` の attrset 形式**: `{ name = "rtk"; args = [ "HEAD" ]; }` を平文 string と一緒に parse 必要 | Phase 1 で `nix eval --json` または awk で両形式に対応、形式不明な entry は WARN |

## Open questions to resolve before Phase 1

1. **scope creep ガード**: 各 Phase の "done" を客観基準で測れるか? acceptance criteria を Phase 1 着手前に再確認
2. **codex spec/plan gate**: M 規模なので Phase 1 着手前に codex-plan-reviewer に投げる (本 PR では `codex review --base master` で実施済み、指摘 P2/P3×2 を反映)
3. **依存検証先**: minimum version table の権威ソース (rtk は upstream release notes、jq は brew formula、claude は npm package.json)
4. **既存 `validate-symlinks` カバレッジ調査**: `.bin/validate_symlinks.sh` が現状どの link をチェックしているか棚卸しし、spec の `~/.claude/` / `~/.config/` / `~/.zshrc` カバレッジに抜けがないか Phase 1 着手前に確認 (重複/抜け検出)

## File touchpoints (estimated, Phase 1)

| File | 操作 | 行数概算 |
|---|---|---|
| `scripts/lifecycle/doctor.sh` | new | 150-200 |
| `references/setup-requirements.md` | new | 60-80 |
| `Taskfile.yml` | edit (task 追記) | +20 |
| `tests/fixtures/doctor/*.txt` | new | 5 fixtures |
| `CLAUDE.md` (root) | edit (Taskfile reference 追記) | +2 行以内 |

合計約 250-330 行、L 規模に膨らむ場合は Phase 1 をさらに 1a/1b に分割。

## Out of scope (再掲)

- 自動修復 (Phase 3)
- GitHub Actions 化
- 新マシン bootstrap chain orchestration
