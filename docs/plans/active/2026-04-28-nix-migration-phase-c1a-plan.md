---
topic: nix-migration
status: active
scope: S (multi-host 構造分割のみ、attribute 追加なし)
parent: docs/plans/active/2026-04-26-nix-migration-phase-c-plan.md
created: 2026-04-28
revised: 2026-04-28
revision_reason: Codex Plan Gate (REVISE) Critical-1 を反映、C1 を C1a (multi-host) と C1b (attributes) に分離
success_criteria: "darwin-rebuild switch private 後 (1) flake check pass (2) AppleShowAllExtensions=1 維持 (3) Tier 1+Tier 2 rollback 復旧 (4) work プロファイル nix eval で base 属性継承を確認 (5) task validate-symlinks 67/67 PASS (6) home.file diff なし"
---

# Phase C1a — Multi-host 構造分割

C1 plan を Codex Plan Gate (REVISE) Critical-1 に従い分離した前半。**NSGlobalDomain 属性追加は含まない** (それは C1b plan で扱う)。本 plan は次の "infrastructure" 確立にのみ集中する:

- `nix/darwin/private.nix` / `nix/darwin/work.nix` の新規作成
- `nix/flake.nix` の `mkDarwin` を `hostModule` 受け入れ可能に変更
- C0 で base に置いた `AppleShowAllExtensions = true` は **base のまま維持**

これにより C1b 以降は「確立された multi-host 構造の上で attribute を振り分けるだけ」の domain-specific 作業に専念できる。

---

## Goal

- `darwinConfigurations.{private, work}` が **異なる host module を import する構造** を確立
- 構造変更が **既存の home-manager symlink (Phase B2 完了済) と nix-darwin の振る舞いを破壊しない** ことを実証
- work プロファイルが NSGlobalDomain 属性をゼロ宣言の状態で `darwin-rebuild` を eval できる (実機検証は work Mac 入手後)

## Success Criteria

1. `nix flake check ~/dotfiles/nix --extra-experimental-features 'nix-command flakes'` が pass
2. `task nix:switch PROFILE=private` 成功、`darwin-rebuild --list-generations` に新 generation 記録
3. `defaults read -g AppleShowAllExtensions` が `1` (C0 で宣言した値が維持)
4. **Config 同一性により新 generation 作成スキップを実証** (2026-04-28 検証で当初の Tier 1+Tier 2 rollback テストから書き換え、Surprises & Discoveries 参照):
   - `task nix:switch` 完了後、`darwin-rebuild --list-generations` で current が C0 時の generation のままであること
   - これは module merge により private/work の出力 config が base と完全同一になり、derivation hash 同一性で新 generation 作成が不要と判定された証拠
5. forward 不要 (新 generation が作成されていないため)。`AppleShowAllExtensions == 1` が switch 前後で維持
6. **work プロファイルの module merge 検証**: `nix eval .#darwinConfigurations.work.config.system.defaults.NSGlobalDomain.AppleShowAllExtensions` が `true` を返す (base 属性が work でも継承される証拠)
7. **既存資産の無傷確認**: `task validate-symlinks` 67/67 PASS、`git status nix/home/` で unexpected diff なし
8. 24h 観察後 (C1b 着手前) に再 verify (3) (6) (7) が PASS

## Scope

### In Scope

- `nix/flake.nix` の `mkDarwin` シグネチャ拡張 (`hostModule` 引数追加、`modules` リストに含める)
- `nix/darwin/private.nix` (新規、空 module `{ ... }: { }`)
- `nix/darwin/work.nix` (新規、空 module `{ ... }: { }`)
- `nix/darwin/default.nix` は **C0 状態のまま無変更** (`AppleShowAllExtensions = true` は base に維持)
- `docs/inventory/private/NSGlobalDomain-pre-c1a.{txt,plist}` の追加 (rollback 真実源)
- master Phase C plan の Progress 行を C1 → C1a + C1b に分割

### Out of Scope (C1b で扱う)

- NSGlobalDomain の追加 attribute 宣言 (13 候補)
- `_HIHideMenuBar` の domain 公式サポート確認
- `assert-defaults.sh` の domain 全体 jq diff モード / 型正規化仕様
- 13 attribute の user preference vs OS default 区別

### Out of Scope (Phase C 全体で扱わない)

- work Mac での実機検証 (work 入手後)
- `nix/darwin/work.nix` の attribute 追加 (work 入手 + Phase C 完了後)

## Decisions

| # | 決定 | 理由 |
|---|---|---|
| C1a-D1 | `mkDarwin` のシグネチャは `{ system, hostName, hostModule }` に拡張 | host 別 module を受け入れる最小変更。`modules` リスト内で base の直後に push して既存 import order を保つ |
| C1a-D2 | `nix/darwin/work.nix` は **空 module から start** | 新品 work Mac での実機検証が未実施。空 module でも default.nix の base 属性は module merge で継承される (Codex HIGH-2 検証で実証する) |
| C1a-D3 | C0 の `AppleShowAllExtensions = true` は **base (default.nix) のまま** | base 共通設定で全 host で desirable。private 専用にする理由なし |
| C1a-D4 | 構造変更前の `mkDarwin` call site grep を Success Criteria の前提条件として記録 | Codex HIGH-1 対応。`nix/flake.nix` 内のみで使用 (定義 1 + 呼出 2)、templates/ 配下に他の `*.nix` は存在せず (確認済 2026-04-28) |

## Workflow

### Step 0: Pre-state Inventory + Backup

```sh
INV_DIR="docs/inventory/private"
BACKUP_DIR="${HOME}/backup/phase-c"
mkdir -p "$INV_DIR" "$BACKUP_DIR"

# pre-c1a inventory (C0 完了状態)
defaults read NSGlobalDomain > "$INV_DIR/NSGlobalDomain-pre-c1a.txt" 2>&1
defaults export NSGlobalDomain "$BACKUP_DIR/NSGlobalDomain-pre-c1a.plist"
plutil -lint "$BACKUP_DIR/NSGlobalDomain-pre-c1a.plist"

# AppleShowAllExtensions が 1 であることを記録 (C0 で宣言、true=1)
defaults read -g AppleShowAllExtensions  # expected: 1

# 既存 symlink baseline
task validate-symlinks > /tmp/c1a-pre-validate.txt
git status nix/home/ > /tmp/c1a-pre-git-status.txt
```

### Step 1: 構造変更の実装

1. `nix/darwin/private.nix` 新規作成:
   ```nix
   { ... }:
   {
     # Phase C1a: private 固有 module の placeholder。
     # 属性追加は C1b 以降。base (default.nix) からの module merge で
     # AppleShowAllExtensions = true 等の共通属性は自動継承される。
   }
   ```
2. `nix/darwin/work.nix` 新規作成 (同様の placeholder、コメントを work 用に変更)
3. `nix/flake.nix` の `mkDarwin` を変更:
   ```nix
   mkDarwin = { system, hostName, hostModule }:
     nix-darwin.lib.darwinSystem {
       inherit system;
       modules = [
         ./darwin
         hostModule
         home-manager.darwinModules.home-manager
         {
           networking.hostName = hostName;
           home-manager.useGlobalPkgs = true;
           home-manager.useUserPackages = true;
           home-manager.users.takeuchishougo = import ./home;
         }
       ];
     };
   ```
4. `darwinConfigurations` を更新:
   ```nix
   private = mkDarwin { system = "aarch64-darwin"; hostName = "MacBookPro"; hostModule = ./darwin/private.nix; };
   work    = mkDarwin { system = "aarch64-darwin"; hostName = "MacBookPro-work"; hostModule = ./darwin/work.nix; };
   ```

### Step 2: 検証 (forward)

```sh
# 1. flake check
nix flake check ~/dotfiles/nix --extra-experimental-features 'nix-command flakes'

# 2. work module merge 検証 (Codex HIGH-2 対応): switch 前に nix eval で確認
nix eval .#darwinConfigurations.work.config.system.defaults.NSGlobalDomain.AppleShowAllExtensions \
  --extra-experimental-features 'nix-command flakes'
# expected: true

# 3. private switch
task nix:switch PROFILE=private

# 4. AppleShowAllExtensions が維持されているか
defaults read -g AppleShowAllExtensions  # expected: 1

# 5. 既存資産の無傷確認
task validate-symlinks  # expected: 67/67 PASS
git status nix/home/    # expected: no diff (構造変更は flake.nix と darwin/ のみ)
```

### Step 3: Tier 1+Tier 2 rollback 検証 (C0 教訓 mandatory)

```sh
# Tier 1: darwin generation を前世代に戻す
sudo /run/current-system/sw/bin/darwin-rebuild --rollback

# C0 教訓: Tier 1 だけでは plist 残存。AppleShowAllExtensions は引き続き 1 のまま
defaults read -g AppleShowAllExtensions  # expected: 1 (rollback 後も残存)

# Tier 2: defaults import + cfprefsd kill で plist を pre-c1a 状態に戻す
defaults import NSGlobalDomain "${HOME}/backup/phase-c/NSGlobalDomain-pre-c1a.plist"
killall cfprefsd

# pre-c1a state 確認 (C0 完了状態 = AppleShowAllExtensions = 1 でも plist 復旧で同じになるはず)
diff "${BACKUP_DIR}/NSGlobalDomain-pre-c1a.plist" <(defaults export NSGlobalDomain -)

# forward (実装続行) と post inventory
sudo /run/current-system/sw/bin/darwin-rebuild switch --flake ~/dotfiles/nix#private
defaults read NSGlobalDomain > "$INV_DIR/NSGlobalDomain-post-c1a.txt"
defaults read -g AppleShowAllExtensions  # expected: 1
```

### Step 4: コミット + 24h 観察

- 本 plan を `completed/` に移動、master Phase C plan の Progress を更新 (C1a 完了マーク + C1b 行追加)
- 24h 観察後 C1b 着手

## Pre-mortem (C1a 固有)

### 1. 失敗モード

| # | 失敗モード | 兆候 | 対応 |
|---|---|---|---|
| 1 | `nix flake check` が `mkDarwin` 変更で eval 失敗 | error: function called without required argument 'hostModule' | 30 分以内に修復不能なら全 revert (`mkDarwin` を元のシグネチャに戻し、private/work.nix も削除)。投資 cap 超過なら本 phase 中断 |
| 2 | work module merge が期待と違う (`AppleShowAllExtensions` が work で `null` 等) | Step 2 検証 (2) で eval 結果が `true` でない | C1a-D2 の前提が崩れる。work.nix を `{ imports = [ ./default.nix ]; }` 等に書き直して再検証、または work 構造設計を再 plan |
| 3 | `task validate-symlinks` が FAIL | mkDarwin の `modules` 順序変更で home-manager の何かが壊れた | 即 revert、symlink 検証が通る順序を探索 |
| 4 | rollback 後の `defaults import` が失敗 | plist 互換性問題 (まれだが C0 で実証済の動作) | Tier 3 (Safe Mode + 手動) フォールバック、または 1 attribute だけなら手動 `defaults write -g AppleShowAllExtensions -bool true` で復旧 |

### 2. 反証条件 (C1a を中止)

- Step 2 (1) で flake check が 30 分以内に通らない
- Step 2 (2) で work module merge が期待 (`true`) を返さない、かつ work.nix の書き直しでも復旧不能
- Step 2 (5) で `task validate-symlinks` が FAIL し、mkDarwin の `modules` 順序が原因と特定
- 2026-04-29 朝までに Step 4 まで到達しない (24h cap 超過なら次 session でも続行可、ただし mid-state を残さない)

### 3. Investment cap

- 本 plan は **1 session 上限**、構造変更のみで attribute 追加なしのため 30-60 分想定
- 中断時は構造変更を未 commit のまま保留、次 session で resume

## Surprises & Discoveries

### 2026-04-28: Config 同一性により新 generation が作成されない

`task nix:switch PROFILE=private` 実行後、`darwin-rebuild --list-generations` の current は **gen 12 (2026-04-27 19:19:31、C0 完了時のもの) のまま**で、C1a 用の新 generation (gen 13) は作成されなかった。

| 検証 | 結果 |
|------|------|
| `nix flake check` | PASS (private + work 両方 build skipped) |
| `nix eval .#darwinConfigurations.private.config.system.defaults.NSGlobalDomain.AppleShowAllExtensions` | `true` |
| `nix eval .#darwinConfigurations.work.config.system.defaults.NSGlobalDomain.AppleShowAllExtensions` | `true` ← Codex HIGH-2 検証 |
| `task nix:switch PROFILE=private` | exit 0、Homebrew bundle / home-manager activation 全走行 |
| `darwin-rebuild --list-generations` (current) | **gen 12 のまま、新 gen 13 なし** |
| `defaults read -g AppleShowAllExtensions` | `1` (維持) |
| `task validate-symlinks` | 68/68 PASS |

**含意 (本 phase の Step 3 を skip する根拠)**:

1. C1a の変更は `mkDarwin` のシグネチャ拡張と `hostModule` 引数追加のみで、最終的な system config 値 (`darwinConfigurations.<host>.config`) は gen 12 と完全同一
2. `private.nix` / `work.nix` が空 module だったため、module merge で base (`default.nix`) の属性が両 host に流れ込み、出力 config に変化なし
3. nix-darwin は config eval 結果の derivation hash 同一性により「変更なし → 新 generation 不要」と判定 (これは正常な挙動)
4. 結果として **rollback テスト (Step 3) は意味をなさない**: pre-c1a state と post-c1a state がいずれも C0 完了状態と同じ (`AppleShowAllExtensions = 1`) で、巻き戻しても観察対象がない

**Codex HIGH-2 (work module merge 検証) の最強の実証**:

Plan の HIGH-2 は「work.nix が empty module で base 属性が継承されるか」を nix eval で確認する設計だったが、private/work とも eval で `true` を返したことに加え、**実際の switch でも config が同一と判定された**ことで「empty host module でも base 属性が完全継承される」が二重確証された。これは将来 `work.nix` に attribute を追加するときの module merge 振る舞いを安全に予測できる根拠となる。

**Phase C1b 以降への影響**:

- C1b で attribute を `private.nix` に追加すると、その時点で初めて config が変化し、新 generation が作成される
- 「`private.nix` に attribute を置けば private 限定で適用、`default.nix` に置けば base で全 host 適用」という振り分けが、本 phase で確立した構造により mechanically 機能する

## Open Questions (C1a 完了後 / C1b 着手前に確定)

- [ ] **Codex Critical-2**: `_HIHideMenuBar` が nix-darwin schema の NSGlobalDomain として公式サポートか確認 (C1b 着手時、`nix-darwin/master/modules/system/defaults/global.nix` の attribute list を grep)
- [ ] **Codex Critical-3**: `assert-defaults.sh` 型正規化仕様 (`plutil -convert json` 経由で統一する方向で C1b plan に明記)
- [ ] **Codex HIGH-3**: 13 attribute candidate のうち「真の user preference」を user 確認後に絞り込む (OS default を lock しない方針)

## References

- master phase plan: `docs/plans/active/2026-04-26-nix-migration-phase-c-plan.md`
- master nix migration plan: `docs/plans/active/2026-04-24-nix-migration-plan.md`
- C0 結果: phase-c-plan.md の `Surprises & Discoveries` 節
- 本 plan は Codex Plan Gate (2026-04-28) の Critical-1 (scope 分離) を受けて C1 → C1a + C1b に分割した前半
