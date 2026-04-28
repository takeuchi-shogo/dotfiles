---
topic: nix-migration
status: active
scope: M (NSGlobalDomain 属性 2 個追加 + assert-defaults.sh full 版実装)
parent: docs/plans/active/2026-04-26-nix-migration-phase-c-plan.md
created: 2026-04-28
revised: 2026-04-28
revision_reason: Codex Plan Gate (REVISE) 9 件 (Critical 3 / High 3 / Medium 3) を反映。型 normalize の実証 (plutil -extract raw で bool→true/false、normalize 不要) と defaults import semantics (replace 動作、man defaults 確認済) を取り込み
success_criteria: "task nix:switch private 後 (1) flake check pass (2) plutil -extract で 3 attribute (AppleShowAllExtensions=true / AppleEnableSwipeNavigateWithScrolls=false / _HIHideMenuBar=true) が nix expected と完全一致 (3) assert-defaults.sh domain mode が PASS (4) Tier 1 rollback 後に AppleEnableSwipeNavigateWithScrolls/_HIHideMenuBar が plist 残存し Tier 2 (defaults import = replace 動作) で pre-c1b state に完全復旧 (5) 24h 観察 (Mac 通常運用 + 再起動 + Safari/Finder/Dock 起動) 後の再 verify で 3 attribute・validate-symlinks 68/68・git status nix/home/ diff なし"
---

# Phase C1b — NSGlobalDomain 属性宣言

C1a (multi-host 構造) 完了を受けて、確立された構造の上で **NSGlobalDomain の保守的な user preference 3 個** を宣言する。同時に `.bin/assert-defaults.sh` を **domain 全体 jq diff モード** に拡張し、今後の milestone (C2a/C2b/C3/C4) で再利用できる検証基盤を整える。

C1a の発見「config 同一性で新 generation skip」を逆手に取り、**今回は config が実際に変化するため新 generation が作成され、Tier 1+Tier 2 rollback が意味を持つ**。これは C0 教訓 (Tier 1 だけでは plist 残存) の本番再現実証も兼ねる。

---

## Goal

- 3 attribute を宣言化し、`darwin-rebuild` 一発で適用可能にする
  - `default.nix` (base): `AppleShowAllExtensions = true` (C0 から維持、変更なし)
  - `private.nix`: `AppleEnableSwipeNavigateWithScrolls = false` + `_HIHideMenuBar = true` (新規追加)
- `assert-defaults.sh` を domain 全体 jq diff モードに拡張、bool↔int 等価視で false positive を抑制
- C1a で立証した「base / private 振り分け mechanism」を attribute 実例で再実証

## Success Criteria

1. `nix flake check ~/dotfiles/nix --extra-experimental-features 'nix-command flakes'` pass
2. `task nix:switch PROFILE=private` 成功、`darwin-rebuild --list-generations` で **新 generation 13 が current** (C1a と異なり今回は config 変化あり)
3. `defaults read -g AppleShowAllExtensions == 1`, `defaults read -g AppleEnableSwipeNavigateWithScrolls == 0`, `defaults read -g _HIHideMenuBar == 1`
4. `.bin/assert-defaults.sh private NSGlobalDomain` (domain mode) が PASS — 3 attribute すべて nix 宣言と実値一致
5. **Tier 1+Tier 2 rollback の本番実証**:
   - `darwin-rebuild --rollback` 後、`AppleEnableSwipeNavigateWithScrolls` と `_HIHideMenuBar` が **plist に残存**することを確認 (C0 教訓の本番再現)
   - `defaults import NSGlobalDomain $BACKUP_DIR/NSGlobalDomain-pre-c1b.plist` + `killall cfprefsd` で pre-c1b state に完全復旧
   - `assert-defaults.sh private NSGlobalDomain --expect-pre-state --pre-inventory $INV_DIR/NSGlobalDomain-pre-c1b.txt` PASS
6. forward (再 switch) 後、`assert-defaults.sh` 再度 PASS、`docs/inventory/private/NSGlobalDomain-post-c1b.txt` 保存
7. **既存資産の無傷確認**: `task validate-symlinks` 68/68 PASS、`git status nix/home/` で diff なし
8. work プロファイルの module merge: `nix eval .#darwinConfigurations.work.config.system.defaults.NSGlobalDomain.AppleEnableSwipeNavigateWithScrolls` が work.nix に未宣言なので **`null` または属性自体が存在しない** (private 限定確認)。一方 `AppleShowAllExtensions` は base にあるので work でも `true` (継続)
9. 24h 観察後 (C2a 着手前) の再 verify で (3) (4) (7) PASS

## Scope

### In Scope

- `nix/darwin/default.nix`: 既存の `AppleShowAllExtensions = true` のまま (変更なし)
- `nix/darwin/private.nix`: `system.defaults.NSGlobalDomain.AppleEnableSwipeNavigateWithScrolls = false` と `system.defaults.NSGlobalDomain._HIHideMenuBar = true` を追加
- `.bin/assert-defaults.sh` の拡張:
  - 既存 single-key モード後方互換維持
  - 新規 domain mode: `assert-defaults.sh <host> <domain>` で全宣言 key を jq diff (bool↔int 等価視)
  - 新規 pre-state mode: `assert-defaults.sh <host> <domain> --expect-pre-state --pre-inventory <path>`
- `docs/inventory/private/NSGlobalDomain-{pre,post}-c1b.{txt,plist}` 追加
- master Phase C plan の Progress C1b 行を [x]

### Out of Scope (将来 phase / 別 plan)

- B 6 個の attribute (auto-substitution + KeyboardUIMode) — OS default lock 回避方針で本 phase 含めず
- C `NSTableViewDefaultSizeMode` — user 記憶なしのため除外、必要なら未来 phase で再検討
- 見送り 4 個 (KeyRepeat / Dark Mode / scrollbar) — 個別の user preference 確認後に再判断
- Schema 外 3 個 (`AppleMiniaturizeOnDoubleClick` / `NSAutomaticTextCompletionEnabled` / `AppleAntiAliasingThreshold`) — `CustomUserPreferences` 経由は別 phase で検討
- C2a (Dock) 以降の domain — 24h 観察後に着手

## Decisions

| # | 決定 | 理由 |
|---|---|---|
| C1b-D1 | `AppleEnableSwipeNavigateWithScrolls = false` と `_HIHideMenuBar = true` を **`private.nix` に置く** | Plan 原則「判断不能 → private (保守的)」に従う。base 昇格は work Mac 入手後「両 host で欲しい」と判明したら別 phase で実施 |
| C1b-D2 | `AppleShowAllExtensions = true` は **base のまま維持** (C0 から変更なし) | 拡張子常時表示は普遍的 user preference、base 共通設定が妥当 |
| C1b-D3 | B 6 個は **lock しない** | 全て macOS OS default = inventory 値のため、明示宣言は冗長。drift detection (将来の inventory diff) で OS が default を変更した場合に検出 |
| C1b-D4 | `assert-defaults.sh` の型正規化は **`plutil -convert json` + jq walk による bool↔int 統一** | nix 宣言 (boolean) と plist (integer) の型差を吸収、実装時に macOS の実際の書き込み型を verify |
| C1b-D5 | `nix-darwin` schema 外 3 個は **本 phase で扱わない** | `system.defaults.<schema-key>` で宣言不可、`CustomUserPreferences` 経由は別 phase の責任 |
| C1b-D6 | C1a の発見 (config 同一性で gen skip) は **本 phase では発生しない** | 今回は実 attribute 追加で config が変化、新 generation 13 が作成される (Tier 1+Tier 2 rollback の本番実証が成立) |
| C1b-D7 | `assert-defaults.sh` は **`plutil -extract <key> raw -o -` 経路** で実装、bool↔int normalize 不要 | 2026-04-28 実証: nix で `true` 宣言 → plist に bool で書き込み → `plutil -extract raw` は `true`/`false` を出力 → nix eval --json `jq -r` の出力 (`true`/`false`) と完全一致。`plutil -convert json` を domain 全体に適用すると binary data (`_AKBAACertMarkerKey` 等) で fail するため per-key 抽出に切替 |
| C1b-D8 | `defaults import <domain> <plist>` は **replace 動作** (plist にない key は削除) | `man defaults` 記述「writes the plist at path to domain」+ C0 実証 (Tier 2 で AppleShowAllExtensions が absent に戻った)。これにより Tier 2 復旧で「pre-c1b plist に含まれない C1b 新規 attribute は確実に削除」が保証される |
| C1b-D9 | pre-inventory は **`.plist` (binary plist) 一本に統一** | `assert-defaults.sh --pre-inventory` は plutil で扱える plist のみ受け付ける。`defaults read` 出力 (.txt) は人間可読フォーマットで型情報が失われるため、検証用 input としては不適切。.txt は inventory 永続化 (git tracked) 用、.plist は backup + 検証 input 用と用途分離 |
| C1b-D10 | `assert-defaults.sh` の **scope は NSGlobalDomain (scalar key) に限定** | C2a (Dock) の `persistent-apps` は array of dict、C2b (Finder) の `FXDefaultSearchScope` は scalar string。array/dict 対応は別 plan (C2a 着手時) で拡張、本 phase では NSGlobalDomain の scalar (bool/int/string) のみサポートと明記 |

## Workflow

### Step 0: Pre-state Inventory + Backup

```sh
INV_DIR="docs/inventory/private"
BACKUP_DIR="${HOME}/backup/phase-c"
mkdir -p "$INV_DIR" "$BACKUP_DIR"

# C1a 完了状態 = pre-c1b
defaults read NSGlobalDomain > "$INV_DIR/NSGlobalDomain-pre-c1b.txt" 2>&1
defaults export NSGlobalDomain "$BACKUP_DIR/NSGlobalDomain-pre-c1b.plist"
plutil -lint "$BACKUP_DIR/NSGlobalDomain-pre-c1b.plist"

# pre-state 値の確認 (新規 2 個)
defaults read -g AppleEnableSwipeNavigateWithScrolls  # expected: 0 (現状値)
defaults read -g _HIHideMenuBar                       # expected: 1 (現状値)
defaults read -g AppleShowAllExtensions               # expected: 1 (C0 維持)

# baseline
task validate-symlinks > /tmp/c1b-pre-validate.txt
git status nix/home/ > /tmp/c1b-pre-git-status.txt
```

### Step 1: assert-defaults.sh full 版の実装 (per-key extraction 経路)

2026-04-28 の事前検証 (C1b-D7/D9) を踏まえて以下の設計に確定:

```sh
# 1. domain mode (新規、scalar key only — C1b-D10)
.bin/assert-defaults.sh <host> <domain>
#  ── for each key in nix eval --json .#darwinConfigurations.<host>.config.system.defaults.<domain>:
#      expected = jq -r ".\"$key\"" expected.json    # nix → "true"/"false"/"N"/string
#      actual   = plutil -extract "$key" raw -o - /tmp/actual.plist 2>/dev/null || echo "<absent>"
#      [ "$expected" = "$actual" ] || record MISMATCH
#  ── exit 0 if all match, exit 1 with mismatch key list otherwise
#  ── normalize 不要: nix bool → plist bool → plutil raw "true"/"false" 完全一致

# 2. pre-state mode (新規、--pre-inventory は .plist のみ受付 — C1b-D9)
.bin/assert-defaults.sh <host> <domain> --expect-pre-state --pre-inventory <plist-path>
#  ── 期待値を nix eval ではなく plist から読む
#  ── for each key in plutil -extract <root> json で取得した key list:
#      expected = plutil -extract "$key" raw -o - "$plist-path"
#      actual   = plutil -extract "$key" raw -o - <(defaults export "$domain" -)
#      [ "$expected" = "$actual" ] || MISMATCH
#  ── これで「pre-c1b plist と現在 defaults が完全一致」を確認

# 3. 既存 single-key mode (後方互換、変更なし)
.bin/assert-defaults.sh <host> <domain> <key> <expected>
.bin/assert-defaults.sh <host> <domain> <key> --absent
```

**実装言語**: bash (既存スクリプトの拡張)。shellcheck pass + sample run で 3 mode の手動テストを着手前に完了させる。

**実装上の境界条件**:

- `plutil -extract <key> raw` で対象 key が存在しない場合 → exit code != 0 + `Could not extract value` メッセージ。スクリプトは `<absent>` 判定にして expected と比較
- nix eval --json で `null` を返す key はあり得る (option の defaultText が `null` の場合)。本 phase では現れないが、`null` を `<absent>` と等価視するロジックを導入
- domain 全体の plist 取得は `defaults export <domain> /tmp/actual.plist` で binary plist を生成、plutil で扱う (plutil -convert json は不可)

### Step 2: 属性追加 + flake check

`nix/darwin/private.nix` を編集:

```nix
{ ... }:

{
  # Phase C1b (2026-04-29 想定): NSGlobalDomain の private 限定 attribute。
  # base (default.nix) の AppleShowAllExtensions = true は module merge で継承される。
  system.defaults.NSGlobalDomain = {
    AppleEnableSwipeNavigateWithScrolls = false;  # スワイプによる戻る/進む無効化
    _HIHideMenuBar = true;                          # メニューバー自動非表示
  };
}
```

```sh
nix flake check ~/dotfiles/nix --extra-experimental-features 'nix-command flakes'
```

### Step 2.5: Module merge 影響の事前検証 (CRITICAL-3 対応)

C1a で「empty module は base 継承」が実証されたが、C1b では private に attribute が追加され、work が依然 empty という非対称構造になる。この時の work eval 振る舞いを **switch の前** に確認する:

```sh
# private (新規 2 個 + base 1 個 が見える想定)
nix eval ~/dotfiles/nix#darwinConfigurations.private.config.system.defaults.NSGlobalDomain.AppleEnableSwipeNavigateWithScrolls \
  --extra-experimental-features 'nix-command flakes'
# expected: false

nix eval ~/dotfiles/nix#darwinConfigurations.private.config.system.defaults.NSGlobalDomain._HIHideMenuBar \
  --extra-experimental-features 'nix-command flakes'
# expected: true

# work (private 限定 attribute が **null** であること)
nix eval ~/dotfiles/nix#darwinConfigurations.work.config.system.defaults.NSGlobalDomain.AppleEnableSwipeNavigateWithScrolls \
  --extra-experimental-features 'nix-command flakes'
# expected: null  ← nix-darwin の system.defaults スキーマは optional default = null
# ※ もし error/false を返した場合は Plan 仮定 (private 限定) が崩れているので Pre-mortem #6 へ

# base 共通 (work でも継承されること)
nix eval ~/dotfiles/nix#darwinConfigurations.work.config.system.defaults.NSGlobalDomain.AppleShowAllExtensions \
  --extra-experimental-features 'nix-command flakes'
# expected: true
```

**Step 2.5 の expected が想定外なら Step 3 (switch) に進まない**。Pre-mortem #6 に従って対応。

### Step 3: switch + 検証 (forward) — daemon reload を Step 4 と統一 (HIGH-2 対応)

```sh
task nix:switch PROFILE=private

# 新 generation が作成されたこと (C1a と異なり今回は config 変化あり)
sudo /run/current-system/sw/bin/darwin-rebuild --list-generations | tail -3
# expected: gen 13 (current)

# OS daemon に plist 再読み込みを強制 (HIGH-2: forward/rollback で同一手順)
killall cfprefsd Dock SystemUIServer 2>/dev/null || true
sleep 3  # daemon 再起動を待つ

# 全 attribute の forward 状態確認 (per-key plutil -extract で型一致 verify)
defaults read -g AppleShowAllExtensions               # 1
defaults read -g AppleEnableSwipeNavigateWithScrolls  # 0
defaults read -g _HIHideMenuBar                       # 1

# domain assertion (新仕様 per-key plutil -extract raw)
.bin/assert-defaults.sh private NSGlobalDomain
# expected: PASS for 3 keys

# 目視確認:
#   ・メニューバーがアプリ非アクティブ時に自動非表示になるか (_HIHideMenuBar)
#   ・トラックパッド 2-finger スワイプで Safari 等の history navigation が無効か (AppleEnableSwipeNavigateWithScrolls)
#   ・Finder で拡張子 (例: .txt) が常時表示されるか (AppleShowAllExtensions)

# 既存資産無傷
task validate-symlinks 2>&1 | grep -cE '^ok '         # 68
git status nix/home/                                   # no diff
```

### Step 4: Tier 1+Tier 2 rollback の本番実証 (defaults import = replace 動作 / MEDIUM-3 fallback)

```sh
# Tier 1: gen 13 → gen 12 に rollback
sudo /run/current-system/sw/bin/darwin-rebuild --rollback

# Step 3 と同じ daemon reload 手順 (HIGH-2 統一)
killall cfprefsd Dock SystemUIServer 2>/dev/null || true
sleep 3

# C0 教訓の本番再現: rollback 後も plist は残存
defaults read -g AppleEnableSwipeNavigateWithScrolls  # expected: 0 のまま残存
defaults read -g _HIHideMenuBar                       # expected: 1 のまま残存
# (gen 12 は AppleShowAllExtensions = true のみ宣言、新規 2 個は宣言なし。
#  でも plist 上には Tier 1 では消えない)

# Tier 2: defaults import = replace 動作 (C1b-D8) で pre-c1b plist に完全置換
defaults import NSGlobalDomain "$BACKUP_DIR/NSGlobalDomain-pre-c1b.plist"
killall cfprefsd Dock SystemUIServer 2>/dev/null || true
sleep 3

# pre-state mode assertion (C1b-D9: .plist 一本)
.bin/assert-defaults.sh private NSGlobalDomain --expect-pre-state \
  --pre-inventory "$BACKUP_DIR/NSGlobalDomain-pre-c1b.plist"
# expected: PASS — pre-c1b plist と完全一致

# 確認: 新規 attribute が削除されていること
defaults read -g AppleEnableSwipeNavigateWithScrolls  # expected: error (does not exist)
defaults read -g _HIHideMenuBar                       # expected: error (does not exist)
```

**Tier 2 fallback (MEDIUM-3 対応)**: `defaults import` が万が一 partial state を残した場合の手動 fallback:

```sh
# Tier 2-fallback: replace 動作が機能しなかった場合に個別 key を delete
defaults delete -g AppleEnableSwipeNavigateWithScrolls 2>/dev/null || true
defaults delete -g _HIHideMenuBar 2>/dev/null || true
killall cfprefsd Dock SystemUIServer 2>/dev/null || true
sleep 3
.bin/assert-defaults.sh private NSGlobalDomain --expect-pre-state \
  --pre-inventory "$BACKUP_DIR/NSGlobalDomain-pre-c1b.plist"
# 期待: PASS、ここでも FAIL なら Pre-mortem 反証条件 (Tier 2 諦め設計に縮退)
```

forward 復帰:

```sh
sudo /run/current-system/sw/bin/darwin-rebuild switch --flake ~/dotfiles/nix#private
killall cfprefsd Dock SystemUIServer 2>/dev/null || true
sleep 3

# post inventory
defaults read NSGlobalDomain > "$INV_DIR/NSGlobalDomain-post-c1b.txt"
.bin/assert-defaults.sh private NSGlobalDomain  # expected: PASS
```

### Step 5: コミット + 24h 観察 (MEDIUM-2 対応で観察項目を明記)

- 本 plan を `completed/` に移動、master Phase C plan の Progress C1b を [x]
- **24h 観察項目** (次の milestone C2a 着手前に PASS が mandatory):
  - **通常運用**: メール / ブラウジング / Slack 等の日常タスクを 24h 中にこなす
  - **Mac 再起動 1 回**: 再起動後に `_HIHideMenuBar` (メニューバー自動非表示) と `AppleEnableSwipeNavigateWithScrolls=false` (スワイプ無効) が persist しているか目視確認
  - **アプリ起動チェック**: Safari / Finder / Dock / Karabiner-Elements / Hammerspoon / Aerospace / Ghostty を起動、異常なクラッシュ・挙動変化なし
  - **再 verify (24h 後)**: `defaults read -g <3 keys>` で 1/0/1、`assert-defaults.sh private NSGlobalDomain` PASS、`task validate-symlinks` 68/68、`git status nix/home/` で diff なし
  - **時刻記録**: 24h 経過時刻を Resume Anchor に記載 (例: 2026-04-29T08:00 = C2a 着手可能)

## Pre-mortem (C1b 固有)

### 1. 失敗モード

| # | 失敗モード | 兆候 | 対応 |
|---|---|---|---|
| 1 | `assert-defaults.sh` domain mode で false positive | nix `false` vs plutil `false` で文字列差 (改行・空白等) | 事前検証で `plutil -extract raw` 出力に trailing whitespace/newline がないことを確認、shell 側で trim 処理 |
| 2 | nix-darwin が `false` を bool でなく integer (`0`) で plist に書き込む | `plutil -extract raw` が `0` を返す | 2026-04-28 検証では bool 型で書き込まれた (AppleShowAllExtensions=true → plutil raw `true`)。新規 attribute (AppleEnableSwipeNavigateWithScrolls=false) も同じ型で書き込まれる想定だが、Step 3 の domain assertion で実 verify、mismatch なら normalize ロジック (`true→1`/`false→0`) を後付け |
| 3 | Tier 2 復旧後の `--expect-pre-state` が FAIL | pre-c1b と現在 plist の微差 | C1b-D8 (`defaults import` = replace) の前提が崩れた可能性。Step 4 fallback (`defaults delete` 個別) を試行、それでも FAIL なら反証条件 |
| 4 | switch 完了後 `_HIHideMenuBar` の挙動が変わらない | 目視確認で挙動なし | Step 3 の `killall cfprefsd Dock SystemUIServer` で daemon 再起動済の前提。それでも反応しない場合は schema 仕様 vs OS 実装の乖離、`_HIHideMenuBar` を private.nix から外して `system.activationScripts` で `defaults write` 経路に切替検討 |
| 5 | `task nix:switch` がハング (shareSkills 等の activation で詰まる) | 5 分以上 prompt 復帰なし | C1a で「shareSkills まで到達後切れた」が exit 0 だった経験あり、ターミナル出力長で truncate された可能性。実際にハングなら `^C` で中断、新 generation の有無で完了確認 |
| 6 | Step 2.5 で work eval が想定外 (error / false など、null でない) | nix-darwin schema の option default が null でなく false の可能性 | `null` 想定の Plan を修正。work での実値が `false` なら privacy 限定の前提が崩れる (work でも `AppleEnableSwipeNavigateWithScrolls=false` がデフォルト) → 新 generation 影響なし、設計上問題なし。但し Plan に「work では schema default を継承」と明記して修正 |

### 2. 反証条件 (C1b を中止)

- `assert-defaults.sh` のper-key extraction が技術的に解決不能 (例: 想定外型) → 設計再見直し、本 phase 中断
- Tier 2 復旧で plist 状態が pre-c1b に戻らない (Step 4 fallback も含めて FAIL) → Tier 2 設計を諦め `defaults delete` + activation script 経路に切替検討
- Step 2.5 で work eval が error を返し work プロファイルが eval 不能 → multi-host 設計の見直し、C1a に巻き戻し
- 2026-04-29 朝までに Step 5 まで到達しない → 次 session に持越し可、ただし mid-state 残さない

### 3. Investment cap

- 本 plan は **1 session 上限**、attribute 追加 + assert-defaults.sh 拡張 + Step 2.5 で 60-90 分想定
- C1a より複雑なため余裕を持つ。中断時は private.nix の attribute を未 commit のまま保留

## Open Questions (C1b 完了後 / C2a 着手前に確定)

- [ ] **HIGH-3 対応: work Mac 入手時の attribute 同期方針** — 選択肢: (A) `AppleEnableSwipeNavigateWithScrolls`/`_HIHideMenuBar` を base 昇格して両 host 共通にする、(B) work では別の値を宣言する、(C) work では宣言しない (schema default 継承)。C1b 完了後 + work Mac 実機検証で確定
- [ ] B 6 個と C 1 個と見送り 4 個の **将来扱い方針** — drift detection で OS default 変更が検知されたら個別に検討、または全 phase 完了後に一括棚卸し
- [ ] `assert-defaults.sh` の **CI 化** — shellcheck pass を pre-commit hook で強制するか別 plan で
- [ ] `docs/inventory/` の secret 漏洩 scan — Phase C 全完了時に検討
- [ ] `_HIHideMenuBar` が schema にあっても OS daemon の挙動が変わらない場合の対応 — Pre-mortem #4 で発生したら learning として記録

## References

- master phase plan: `docs/plans/active/2026-04-26-nix-migration-phase-c-plan.md`
- C1a plan: `docs/plans/active/2026-04-28-nix-migration-phase-c1a-plan.md`
- C0 結果: phase-c-plan.md の `Surprises & Discoveries` 節
- nix-darwin NSGlobalDomain options: `nix eval ~/dotfiles/nix#darwinConfigurations.private.options.system.defaults.NSGlobalDomain --apply builtins.attrNames` で取得可能 (2026-04-28 確認済、`_HIHideMenuBar` 含む 51 keys)
