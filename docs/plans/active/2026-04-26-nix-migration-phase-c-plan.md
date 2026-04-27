---
topic: nix-migration
status: active
scope: L (system.defaults 段階的宣言、致命 risk あり)
parent: docs/plans/active/2026-04-24-nix-migration-plan.md
created: 2026-04-26
revised: 2026-04-27
revision_reason: Codex Plan Gate (8 findings, Verdict REVISE) を反映
---

# Phase C — `system.defaults` 統合

macOS システム設定 (Dock / Finder / Keyboard 等) を `nix/darwin/default.nix` の `system.defaults` 配下で宣言化し、`darwin-rebuild switch --flake ./nix#<host>` 一発で work Mac を再現できる状態にする。

Phase B2 完了直後 (2026-04-26) の重大な発見: `init-install.sh` には `defaults write` 命令が **存在しない**。つまり Phase C は「既存命令の翻訳」ではなく **「ユーザーが GUI で手動構成した状態を nix で再現可能にする」** 設計タスクである。

---

## Scope

### In Scope (本 Phase)

- 13 domain のうち、致命 risk が低〜中の domain を **5 milestone** に分けて宣言化:
  - **C0 (Phase 0 検証)**: rollback + `defaults import` の end-to-end 復旧テスト (1 attribute だけで実演)
  - **C1**: `NSGlobalDomain` (key repeat / scrollbar / save dialog 等)
  - **C2a**: `com.apple.dock` 単独 (cascade 破損リスク隔離のため finder と分離)
  - **C2b**: `com.apple.finder` 単独
  - **C3**: `com.apple.trackpad` + `com.apple.universalaccess`
  - **C4**: `com.apple.menuextra.{clock,battery}` + `com.apple.screensaver` + `com.apple.controlcenter`
- 各 milestone で:
  - Step 0: `defaults read` で現状 inventory 取得 → **`docs/inventory/<host>/<domain>.txt` に永続化**
  - Step 1: nix 宣言 + `darwin-rebuild switch` + **自動 assertion (defaults read vs 期待値)**
  - Step 2: 動作確認 + `darwin-rebuild --rollback` 実演 + **24h 稼働観察 (次 milestone 着手前 mandatory)**
  - Step 3: forward して commit、master plan の Progress 更新

### Out of Scope (Phase D / E+ で扱う)

- **Phase D (致命 risk domain)**: `com.apple.HIToolbox` (入力ソース)、`com.apple.symbolichotkeys` (Spaces 切替等のショートカット) — 設定ミスで入力不能・操作不能の可能性、専用 plan + spike 先行
- **Phase E+ (アプリ固有)**: Safari / Terminal / Zoom / etc. — 各 app 単位で個別 plan
- **Phase F (未確定)**: `com.apple.spaces` — nix-darwin module の対応状況が不明、要事前調査
- nixvim (master plan D7 で対象外宣言済み)

`master plan` の Phase 構成 table に **Phase D, E, F を追加**することで、最終的な「`darwin-rebuild` 1 発で work Mac 再現」までの road map を可視化する (本 Plan revision と同時に実施)。

---

## Pre-mortem

### 1. 中核仮定が間違っていたら？

**仮定**: nix-darwin の `system.defaults.<domain>.<key>` は実 macOS の `defaults write <domain> <key>` と 1:1 対応している

**外れた場合**:
- 宣言した attribute がシステムに反映されない (silent no-op) → 動作変化なしに見えて手動 GUI 設定が温存される。ある日 `--rollback` した時に手動設定が消える
- 別 attribute と衝突して macOS preferences plist が破損 → System Settings.app 起動不能 / Dock 消失等の致命

**検出方法 (Codex Critical #2 対応)**: 各 milestone の Step 1 末尾で **自動 assertion script** を実行:

```sh
# 期待値を nix eval から JSON で取得
nix eval --json .#darwinConfigurations.<host>.config.system.defaults.<domain> > expected.json
# 実値を defaults read から JSON で取得
defaults export <domain> /tmp/actual.plist
plutil -convert json /tmp/actual.plist -o /tmp/actual.json
# diff で乖離検出 (jq で必要 key だけ抽出)
jq -S 'with_entries(select(.key | IN($keys[])))' --argjson keys "$(jq -S 'keys' expected.json)" /tmp/actual.json > /tmp/actual-filtered.json
diff <(jq -S . expected.json) /tmp/actual-filtered.json || { echo "MISMATCH"; exit 1; }
```

milestone plan で具体的な script を `.bin/assert-defaults.sh <host> <domain>` として実装、Step 1 完了の DoD に組み込む。

### 2. 失敗モード 3 つ

| # | 失敗モード | 兆候 | 検出方法 | 影響 |
|---|---|---|---|---|
| 1 | Dock が消失 / 起動しない | Dock UI が表示されない、`killall Dock` でも復活しない | switch 後の目視 + `pgrep Dock` | 致命 (Safe Mode 必要) |
| 2 | キーボード入力に異常 | キーリピート速度が極端、modifier 効かない | switch 後に terminal で typing test | 中 (terminal で `defaults` 直接修正可能) |
| 3 | 自動 assertion で partial apply 検出 | 一部 key だけ実値が宣言と乖離 | `assert-defaults.sh` の diff 出力 | 軽微 (即時 rollback で戻る) |

### 3. 反証条件 — これが起きたら設計を捨てる

- C0 (Phase 0 検証) で `defaults import` が plist 形式互換性により復旧不能 → Phase C 設計を「`darwin-rebuild --rollback` のみに依存」モードに変更し、`defaults import` フォールバックを諦める
- C1 (NSGlobalDomain) で rollback テストが失敗、または assertion script で実値が宣言と一貫して乖離 → Phase C を中断し `/spike` フェーズへ降格、最小単位 (1 attr) で再検証
- 実値の差分追跡が困難 (macOS が攻撃的に override) → 「nix で表現可能な範囲を限定する」原則に切替、`system.defaults` 全使用を諦め `system.activationScripts` で個別 `defaults write` 経由に変更

### 4. Investment cap

- 致命 risk のため **5 milestone を各 1 session 上限、合計 5 sessions** + Phase 0 検証 1 session = **6 sessions**
- C0 (Phase 0 検証) で復旧不能なら即時中断、追加投資しない
- inventory dump は milestone 着手前に毎回取得、過去 dump は `docs/inventory/<host>/` に永続化して **milestone 間で diff を取り、macOS の attacker override を検出**
- **24h 稼働観察 mandatory**: 次 milestone 着手前に最低 24h を空ける (週末挟みで自然に成立する想定)

### 5. なぜ "全部一括宣言" でなく段階的か

- 一括宣言で macOS が破壊された場合、rollback しても plist の partial state が残る可能性 (defaults plist は OS service が並行書き込み)
- 段階分割により「破壊された domain を特定する」コストを最小化
- 各 milestone 後に 24h 稼働観察できる (週末挟みで余裕を持たせる)

### なぜ "Phase C 自体を諦めない" か

- master plan の Goal「`darwin-rebuild` 一発で work Mac 再現」を満たすには `system.defaults` が不可欠
- これを諦めると Phase B までの投資 (Brewfile + symlink → nix) の価値が半減し、work Mac で手動 GUI セットアップが必要

### Codex Plan Gate 提言への反論メモ

- **#7 Milestone 順序 (C2→C1 推奨に対し、現状 C1→C2 維持)**: Codex の「単一 domain で 1:1 対応 verify を先に」論理は妥当だが、**Dock は visual + interaction に直結する致命影響が大きく、verify の場として不適切**。NSGlobalDomain は scrollbar / tab everywhere 等の表面的設定が中心で、宣言ミスでも目視で気付ける。先に NSGlobalDomain で「nix-darwin の表現と実 defaults の対応関係」を学習してから Dock に進む方が安全。**現状の C1 → C2a → C2b 順序を維持**。

---

## Milestone

| # | 対象 | risk | 主な観点 | 推定変更 (nix) |
|---|---|---|---|---|
| **C0** | 復旧 e2e テスト (1 attr のみ) | 低 | `defaults export` → switch → `--rollback` → `defaults import` の往復確認 | 1-2 行 |
| **C1** | `NSGlobalDomain` | 中 | key repeat / scrollbar / save dialog / tab everywhere | 10-20 |
| **C2a** | `com.apple.dock` 単独 | **高** | autohide / minimize / show-hidden / persistent-apps | 10-15 |
| **C2b** | `com.apple.finder` 単独 | 中 | FXPreferred * / ShowPathbar / NewWindowTarget | 8-12 |
| **C3** | `com.apple.trackpad` + `com.apple.universalaccess` | 中 | tap-to-click / 3finger-drag / reduceMotion | 10-15 |
| **C4** | `com.apple.menuextra.{clock,battery}` + `com.apple.screensaver` + `com.apple.controlcenter` | 低 | 24h time / battery percent / hot corners | 10-15 |

各 milestone は **独立 plan ファイル** (`<date>-phase-c<n>-...md`) を作成。本 plan は master 兼 hub。

---

## Per-milestone Workflow

### Step 0: Inventory + Backup (毎 milestone 着手前、永続化)

```sh
INV_DIR="docs/inventory/${HOST:-private}"
BACKUP_DIR="${HOME}/backup/phase-c"
mkdir -p "$INV_DIR" "$BACKUP_DIR"

for domain in <milestone-domains>; do
  # 永続 inventory (git tracked、host 別)
  defaults read "$domain" > "$INV_DIR/${domain//\//-}-pre-c<n>.txt" 2>&1
  # 復旧用 plist backup (gitignored、host outside)
  defaults export "$domain" "$BACKUP_DIR/${domain//\//-}-pre-c<n>.plist"
done

# 前回 milestone との diff (macOS 攻撃的 override 検出)
diff "$INV_DIR/${domain}-post-c<prev>.txt" "$INV_DIR/${domain}-pre-c<n>.txt" || echo "DRIFT DETECTED"
```

`docs/inventory/<host>/` は host 別 (private / work) に separate、git tracked。

### Step 1: 宣言 + 自動 assertion

```sh
# 1. nix/darwin/default.nix または nix/darwin/<host>.nix に system.defaults を追加
# 2. flake check
nix flake check ~/dotfiles/nix --extra-experimental-features 'nix-command flakes'
# 3. switch
task nix:switch PROFILE="${HOST:-private}"
# 4. 自動 assertion (Pre-mortem #1 の script)
.bin/assert-defaults.sh "${HOST:-private}" "<domain>"  # 全宣言 attr が実値と一致か
```

Step 1 の DoD は「assertion PASS」。FAIL なら Step 2 (rollback) に進む。

### Step 2: 動作確認 + rollback テスト

```sh
# 目視確認: Dock / Finder / Menu bar / 入力
# 自動: assertion script 再実行 (post-switch)
.bin/assert-defaults.sh "${HOST:-private}" "<domain>"

# rollback 実演 (mandatory、毎 milestone)
sudo /run/current-system/sw/bin/darwin-rebuild --rollback
.bin/assert-defaults.sh "${HOST:-private}" "<domain>" --expect-pre-state  # 元に戻ったか

# forward (実装続行)
sudo /run/current-system/sw/bin/darwin-rebuild switch --flake ~/dotfiles/nix#"${HOST:-private}"

# post-state inventory (次 milestone の Step 0 比較対象)
defaults read "$domain" > "$INV_DIR/${domain//\//-}-post-c<n>.txt"
```

### Step 3: コミット + 24h 観察

- milestone plan を `completed/` に移動、master plan の Progress を更新
- **次 milestone 着手まで最低 24h 空ける** (mandatory)。週末挟みで自然成立を狙う

---

## Abort & Rollback (Codex Critical #1 対応 — 強化)

master plan Phase C 行を踏襲。さらに各 milestone で多段フォールバック:

### 通常 rollback (Tier 1)

```sh
sudo /run/current-system/sw/bin/darwin-rebuild --rollback
```

成功すれば前 generation に戻る。assertion script で確認。

### `defaults import` 復旧 (Tier 2 — Tier 1 失敗時)

`darwin-rebuild --rollback` が成功しても plist の partial state が残るケース。`docs/inventory/<host>/<domain>-pre-c<n>.txt` の内容を **plist に変換し直して import**:

```sh
# Tier 2: 個別 domain の plist 復旧
for domain in <affected>; do
  defaults import "$domain" "${HOME}/backup/phase-c/${domain//\//-}-pre-c<n>.plist"
done
killall Dock SystemUIServer cfprefsd  # daemon に再読み込み強制
```

注意: macOS version 間で plist 形式は基本互換だが、保証なし。**C0 (Phase 0 検証) で必ず end-to-end 動作確認**。

### Safe Mode + 手動復旧 (Tier 3 — GUI 起動不能時)

GUI が起動しない、Dock が出ない等で Tier 1/2 が実行できない場合:

1. 電源 off → Touch ID ボタン長押しで起動オプション → Safe Mode で起動
2. Terminal を開き Tier 1 (rollback) を実行
3. 効かない場合は Tier 2 を Safe Mode から実行
4. それでも復旧不能なら **plist 直接編集**:
   ```sh
   sudo plutil -p /Library/Preferences/<domain>.plist  # 確認
   sudo plutil -replace <key> -<type> <value> /Library/Preferences/<domain>.plist
   ```
5. `~/Library/Preferences/<domain>.plist` (user level) も同様
6. 最悪 `cfprefsd` を kill して再読み込み: `sudo killall cfprefsd`

### Tier 4 (Tier 3 失敗、boot 不能時)

- macOS Recovery (起動時 Cmd+R) → ターミナル → `/Volumes/Macintosh HD/etc/...` を編集して nix-darwin 設定を空に戻す
- 最悪 macOS 再インストール (Time Machine からの復旧前提)

---

## Multi-host Design (Codex High #3 対応)

Open Question #3 (work baseline 流用) を **以下で決定**:

- **`nix/darwin/default.nix`**: 全 host 共通の base。スコープを「ほぼ確実に汎用」と判断できる attribute のみ (例: NSGlobalDomain の `AppleShowAllExtensions` 等)
- **`nix/darwin/private.nix`**: private プロファイル固有 (現 MacBookPro 限定の trackpad sensitivity 等)、`darwinConfigurations.private` から import
- **`nix/darwin/work.nix`**: work プロファイル固有 (新品 macOS、空ファイルから開始)、`darwinConfigurations.work` から import

各 milestone の Step 1 で attribute を追加する際、**「base / private-only / work-only」のどれに置くか必ず判断**して plan に記録する。判断不能な場合は `private.nix` (保守的) に置き、後で base に昇格できるか検討。

work プロファイルの `system.defaults` は **Phase C 完了後に新品 work Mac 上で実機検証**するまで未確定。本 Phase は private のみを対象とする。

---

## Progress

- [x] Plan 作成 (本ファイル)
- [x] Codex Plan Gate (REVISE → 本 revision で対応)
- [x] master plan revision (Phase D / E / F outline 追加)
- [x] **C0**: 復旧 e2e テスト (1 attribute で `defaults import` 動作確認) — 2026-04-27 完了
- [ ] **C1**: NSGlobalDomain
- [ ] **C2a**: dock 単独
- [ ] **C2b**: finder 単独
- [ ] **C3**: trackpad + universal access
- [ ] **C4**: menuextra + screensaver + controlcenter
- [ ] master plan の Progress 更新 (Phase C 完了マーク)

---

## Surprises & Discoveries

### C0 (2026-04-27): Tier 1 rollback では defaults 値が残る (Pre-mortem #3 実証)

`AppleShowAllExtensions` (NSGlobalDomain) で復旧 e2e テスト実施。重要な実証結果:

| Step | 操作 | AppleShowAllExtensions の状態 | 期待 vs 実測 |
|------|------|--------------------------------|--------------|
| pre-c0 | (initial) | absent | — |
| forward switch | `darwin-rebuild switch` (gen 11→12) | `1` | ✅ |
| Tier 1 rollback | `darwin-rebuild --rollback` (gen 12→11) | **`1` のまま残存** | ❌ (期待: absent) |
| Tier 2 recover | `defaults import` + `killall cfprefsd` | absent | ✅ |
| forward再switch | `darwin-rebuild switch` (gen 11→12) | `1` | ✅ |

**含意 (C1 以降に強制適用)**:

1. **Tier 1 だけでは plist 復旧不可能** — nix-darwin の `--rollback` は generation を前世代に戻すが、すでに `defaults write` で書き込まれた値は OS の plist 上に残存する。これは silent partial state で、表面的には rollback 成功に見えるが実体は残る。
2. **各 milestone で Tier 2 を必須化** — C1〜C4 では各 Step 2 (動作確認 + rollback テスト) で **Tier 1 rollback 後に必ず Tier 2 (`defaults import`) を実行** し、`assert-defaults.sh ... --absent` (もしくは pre-state 値) で復旧確認すること。
3. **backup plist の正確性が rollback 復旧の唯一の真実源** — `${HOME}/backup/phase-c/<domain>-pre-c<n>.plist` が壊れたら復旧不能。Step 0 (Inventory + Backup) で `plutil -lint` 検証を毎回必須化。

これは Codex Plan Gate Critical #1 で既に懸念として挙げられており、本検証で確証された。「Plan 通りの多段フォールバック設計」が機能することの実証でもある。

---

## Open Questions

- [ ] `com.apple.HIToolbox` (Phase D) で「darwin-rebuild 1 発再現」の最終ピースをどう扱うか — spike 先行で 1 attribute だけ実演して plan 化、もしくは永久に手動運用
- [ ] `com.apple.spaces` の nix-darwin 対応状況 (Phase F の調査タスク)
- [ ] `assert-defaults.sh` の実装責任 — C0 で minimum 版、C1 までに full 版
- [ ] `docs/inventory/` の secret 漏洩リスク — `defaults read` 出力に token 等が混入していないか scan する pre-commit hook が必要か

---

## References

- master plan: `docs/plans/active/2026-04-24-nix-migration-plan.md`
- `references/pre-mortem-checklist.md`
- `references/reversible-decisions.md`
- nix-darwin manual: <https://daiderd.com/nix-darwin/manual/index.html#opt-system.defaults> (要確認、C1 着手時)
- 既存 phase plan (B2 までの完了 plan): `docs/plans/completed/`
- Codex Plan Gate review log: 本 Plan の `revision_reason` 参照
