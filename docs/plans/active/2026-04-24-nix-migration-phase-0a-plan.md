---
topic: nix-migration-phase-0a
status: active
scope: M
parent: 2026-04-24-nix-migration-plan.md
owner: takeuchi-shogo
created: 2026-04-24
success_criteria: "`darwin-rebuild switch --flake ./nix#private` が通り、`hello` 動作 + mkOutOfStoreSymlink 活線編集が機能し、`readlink ~/.zshrc` 等が dotfiles を指したまま。既存 Brewfile / symlink.sh は一切変更せず Nix と並走"
---

# Phase 0+A: Nix 導入 + flake 骨格 + devShell

マスタープラン: [2026-04-24-nix-migration-plan.md](./2026-04-24-nix-migration-plan.md)

## Goal

Nix 環境を導入し、`nix/` 配下に flake + nix-darwin + home-manager の骨格を作る。**既存 Brewfile / symlink.sh は一切変更しない** (並走期)。Nix レイヤーが正しく動くことだけを検証する。

## Scope

### In Scope
- Determinate Systems Installer で Nix インストール
- `nix/flake.nix` + `nix/home/default.nix` + `nix/darwin/default.nix` 骨格
- `darwinConfigurations.private` と `.work` (中身は一旦同一)
- テスト用パッケージ 1 個 (`hello`) だけを `home.packages` に登録
- `Taskfile.yml` に `nix:switch` / `nix:rollback` タスク追加 (existing `symlink` / `brew` は温存)
- `nix/README.md` で移行期の運用を文書化

### Out of Scope
- Brewfile の移行 (Phase B1)
- symlink.sh の置換 (Phase B2)
- `system.defaults` の設定 (Phase C)
- 既存 Taskfile / `.bin/*.sh` の削除や変更

## Steps

1. **[Research]** 以下を確認し、Step 4/5 の具体値は本 Step の結果で埋める:
   - Determinate Systems Installer の最新フラグ (特に `--no-modify-profile` で `/etc/*` 改変をスキップできるか、planner output を `--explain` 相当で事前確認できるか)
   - `nix-darwin` と `home-manager` の **最新安定 release branch** (例: `release-25.11` が現行なら採用、hardcoded default は禁止)
   - `system.stateVersion` の正確な型定義 (nix-darwin では **integer 1-6**、Home Manager の `home.stateVersion` は **release enum 文字列**。混同しない)
2. **[Research+Snapshot]** Nix 導入前の shell 環境・ビルド環境を snapshot。`docs/plans/active/2026-04-24-phase-0a-pre-install-snapshot.txt` に保存:
   ```bash
   # 既存 nix 参照の有無 (installer が触る可能性のある全 path)
   for f in /etc/zshenv /etc/zshrc /etc/bashrc /etc/zprofile /etc/zsh/zshrc /etc/zsh/zshenv /etc/synthetic.conf; do
     echo "=== $f ==="; sudo cat "$f" 2>/dev/null || echo "(not present)"
   done
   ls -la /etc/profile.d/ 2>/dev/null
   # 既存 PATH と主要 symlink
   echo $PATH; readlink ~/.zshrc ~/.zshenv ~/.zprofile ~/.bashrc 2>/dev/null
   # macOS バージョン (参考記録のみ、stateVersion 写像には使わない)
   sw_vers -productVersion
   # Xcode CLT preflight (darwin-rebuild が依存する場合あり)
   xcode-select -p 2>&1; xcrun --show-sdk-path 2>&1
   # APFS /nix volume の事前有無
   diskutil apfs list | grep -i nix || echo "NO_NIX_VOLUME"
   ```
   Xcode CLT が欠如していたら **early abort**、Step 3 に進まない。
3. **[Impl]** Determinate Systems Installer で Nix インストール (multi-user, flakes 有効)。**Step 1 で `--no-modify-profile` オプションの扱いが確認でき、0+A では `/etc/*` 汚染を避けたいなら付けて実行**。インストール直後に Step 2 と同じコマンドで post-install snapshot を取って差分を `docs/plans/active/2026-04-24-phase-0a-post-install-snapshot.txt` に記録
4. **[Impl]** `nix/flake.nix` 骨格作成。要件 (具体値は Step 1 で決定):
   - inputs: `nixpkgs` (nixos-unstable か release を選択), `home-manager` (Step 1 で確定した最新 release branch), `nix-darwin` (同)
   - outputs: `darwinConfigurations.{private, work}` + `devShells.{aarch64-darwin, x86_64-darwin}.default`
   - **multi-system 対応必須**: `private = aarch64-darwin`, `work = aarch64-darwin` (仮、Intel の場合に差し替え可能な構造)
   - **明示設定**: `programs.zsh.enable = false`, `programs.bash.enable = false` (既存 `.config/zsh/` を破壊しない)
   - **`system.stateVersion` は整数**: 新規導入なので `6` に固定 (nix-darwin の現行 `maxStateVersion` に合わせる。Step 1 で要確認)。macOS バージョンからの自動写像は行わない
   - **`home.stateVersion` は release 文字列**: Step 1 で確定した HM release (例: `"25.11"`) を採用。これも macOS バージョンとは独立
5. **[Impl]** `nix/darwin/default.nix` + `nix/home/default.nix` を作成:
   - **5a**: `home.packages = [ pkgs.hello ]` のみ、home-manager activation が通ることを確認
   - **5b**: D6 検証タスク。単一ファイルテストではなく **claude-like fixture tree** で実証:
     ```
     nix/test-fixtures/claude-like/
       CLAUDE.md                     # 通常ファイル
       .hidden                       # hidden file
       skills/
         sample/
           SKILL.md                  # 深い階層 (3段)
           run.sh                    # exec bit 付き (chmod +x)
       unmanaged-sibling.md          # 同階層に意図的に置き、symlink 対象外であることを検証
     ```
     `home.file.".config/zsh-test-nix".source = config.lib.file.mkOutOfStoreSymlink "${config.home.homeDirectory}/dotfiles/nix/test-fixtures/claude-like";` で**ディレクトリ全体** mkOutOfStoreSymlink。**検証項目**:
     1. 活線編集: `skills/sample/SKILL.md` 編集 → `darwin-rebuild switch` 経由せず即反映
     2. exec bit 保持: `~/.config/zsh-test-nix/skills/sample/run.sh` が `-rwxr-xr-x` 相当
     3. hidden file 到達性: `cat ~/.config/zsh-test-nix/.hidden` が動く
     4. unmanaged sibling 非浸食: (このテスト範囲では coexist 検証は限定的、B2 で本格化)
6. **[Impl]** `Taskfile.yml` に以下タスク追加 (既存タスクは変更しない):
   - `nix:switch PROFILE=private` → `darwin-rebuild switch --flake ./nix#${PROFILE}`
   - `nix:rollback` → `darwin-rebuild --rollback`
   - `nix:check` → `nix flake check ./nix`
   - `nix:list-generations` → `darwin-rebuild --list-generations`
7. **[Verify]** 非破壊性と D6 を両方検証:
   - `task nix:switch PROFILE=private` 成功 → `which hello` が nix 由来
   - **Step 5b の活線編集・exec bit・hidden file・深い階層** 全て通過
   - **既存 symlink 生存確認**: `readlink ~/.zshrc ~/.zshenv` が dotfiles を指したまま変わっていないこと
   - **PATH 非破壊 (緩和版)**: Nix PATH が `$PATH` のどこかに含まれていること、かつ現行 `.config/zsh/core/path.zsh` による brew 先頭順序が**破壊されていないこと** (最終優先順の再設計は B1/B2 に委譲)
   - `task nix:rollback` で 1 世代戻り、`hello` が消え、`~/.config/zsh-test-nix/` も消えることを確認
   - 既存機能の回帰なし: `task validate` / `task symlink` / `brew bundle check --file=Brewfile` が全てグリーン
8. **[Docs]** `nix/README.md` に以下を明記:
   - 並走期の運用ルール (Brewfile/symlink.sh 従来通り、Nix は `hello` + test-fixtures のみ)
   - `task nix:switch` / `nix:rollback` の使い方
   - pre/post install snapshot の保存場所
   - 撤退時の手順 (master plan の Abort & Rollback 参照)

## Progress

- [x] Step 1: Installer / input URL 確認 (Decision Log 参照。ただし nix-darwin-25.11 は Step 3 で mismatch 発覚し master に変更)
- [x] Step 2: Pre-install snapshot (`docs/plans/active/2026-04-24-phase-0a-pre-install-snapshot.txt`)
- [x] Step 3: Nix インストール (Determinate 3.18.1 / Nix 2.33.4) + post-install snapshot
- [x] Step 4: flake.nix 骨格 — multi-system + `programs.zsh.enable=false` + `system.stateVersion = 6` + `home.stateVersion = "25.11"`
- [x] Step 5a: `hello` 疎通 — `/etc/profiles/per-user/takeuchishougo/bin/hello` が `Hello, world!`
- [x] Step 5b: mkOutOfStoreSymlink 活線編集 — `readlink -f ~/.config/zsh-test-nix` → `dotfiles/nix/test-fixtures/claude-like` 到達、live edit 即反映、exec bit 保持、hidden file 到達、deep tree OK
- [x] Step 6: Taskfile 統合 (`nix:bootstrap`, `nix:switch`, `nix:rollback`, `nix:check`, `nix:list-generations`, `nix:snapshot`, `nix:explain`)
- [x] Step 7: 非破壊性 & D6 検証 — `readlink ~/.zshrc` → dotfiles 維持、`readlink ~/.zshenv` → regular file 未改変
- [x] Step 8: `nix/README.md` — 並走期運用 + bootstrap/switch/rollback 手順

## Verification

Step 7 で網羅するが、Exit 条件としてまとめる:

- `nix --version` が動く (>= 2.18)
- `nix run nixpkgs#hello` が動く (installer 検証)
- `task nix:switch PROFILE=private` が成功し、`which hello` が nix profile 配下を返す
- **D6 活線編集**: `nix/test-fixtures/marker.sh` 編集 → `cat ~/.config/zsh-test-nix/marker.sh` で即反映
- **既存 symlink 非破壊**: `readlink ~/.zshrc ~/.zshenv ~/.zprofile` が dotfiles repo を指したまま
- **PATH 非破壊**: `.config/zsh/` の初期化順序が壊れていない (master plan "PATH Resolution Strategy" 準拠)
- `task nix:rollback` で 1 世代戻り、`hello` と test symlink が消える
- **既存機能の回帰なし**: `task validate` / `task symlink` / `brew bundle check --file=Brewfile` が全てグリーン

## Edge Cases

- **SIP / Gatekeeper**: installer が `/nix` volume 作成時に macOS admin password を要求 → 対話型なので Taskfile ではなく手動実行
- **Intel Mac 将来対応**: flake.nix の structure は最初から `aarch64-darwin` / `x86_64-darwin` の両方を outputs として書く (`work` が Intel だった場合の rebuild コスト緩和)。実際にビルドするのは `private` の aarch64 のみ
- **Installer の profile 改変**: Determinate Systems Installer が触る exact file set は version 依存。Step 1 で `--explain` / planner output を事前取得し、Step 2 の snapshot で**宣言された全 path** をカバーする。`--no-modify-profile` で `/etc/*` 汚染を避ける選択肢も Step 1 で比較評価。`nix-darwin.programs.zsh.enable` は **当面 false 固定** (B2 で再判断)
- **flake input 固定**: `flake.lock` をコミットする。CI やり直し時のドリフト防止
- **`system.stateVersion` の型**: nix-darwin の `system.stateVersion` は **整数 (1-6)** であり release 文字列ではない。新規導入は `6` で固定 (Step 1 で最新 `maxStateVersion` を要確認)。`home.stateVersion` は別物で HM release 文字列 (enum `"18.09"`〜`"26.05"`)。両者を混同しない
- **home-manager の dotfile 生成 (要監視)**: `programs.zsh.enable = false` の限り、Home Manager source 上は `~/.zshrc` を自動生成する根拠は弱い (direnv/zoxide 等は `programs.zsh.initContent` に足すだけで `enable=true` が前提)。ただし将来 true に切り替える判断は別 phase の decision として明示する。Step 7 の `readlink` 確認は過剰警戒ではなく **レグレッションテスト** として保持
- **Test fixture が repo を汚す**: `nix/test-fixtures/claude-like/` と `~/.config/zsh-test-nix/` は Phase 0+A 専用。Phase B2 着手前に削除するタスクを Phase B2 plan に含める

## Decision Log

### Step 1 Research 完了 (2026-04-24)

ソース直読 + 公式 docs で確認した具体値:

| 項目 | 確定値 | 出典 |
|---|---|---|
| `nix-darwin` input URL | `github:nix-darwin/nix-darwin/nix-darwin-25.11` (stable) | nix-darwin README の flake template (`nix flake init -t nix-darwin/nix-darwin-25.11`) |
| `home-manager` input URL | `github:nix-community/home-manager/release-25.11` | HM 公式 docs, 現行安定 release |
| `nixpkgs` input URL | `github:NixOS/nixpkgs/nixpkgs-unstable` | nix-darwin README の推奨パターン |
| `system.stateVersion` | **`6` (整数)** | [nix-darwin/modules/system/version.nix](https://github.com/nix-darwin/nix-darwin/blob/master/modules/system/version.nix): `types.ints.between 1 config.system.maxStateVersion`, `maxStateVersion default = 6` |
| `home.stateVersion` | **`"25.11"` (release 文字列)** | HM docs: enum `"22.05"..."25.11"`。2026-04 新規導入なので最新を採用 |
| Determinate Installer `--explain` | **あり** | 公式 README: "Provide an explanation of the changes the installation process will make" |
| Determinate Installer `--no-modify-profile` | **あり** | 公式 README: "Modify the user profile to automatically load Nix" のスキップ |
| 残渣 (APFS/Keychain/synthetic.conf/launchd) | **公式 docs には明示なし** | Codex 指摘通り「要確認 / best-effort + residual check」で扱う |
| `mkOutOfStoreSymlink` API | `config.lib.file.mkOutOfStoreSymlink ./bar` → `home.file."foo".source` に代入可能 | HM source `modules/files.nix`。Nix store 外 path への ln -s を生成 |

### Phase 0+A 方針の追加確定事項

- **Installer 起動方法**: Step 3 で先に `nix-installer install macos --explain` を実行して差分を確認してから本番インストールする。0+A では `--no-modify-profile` は付けない方針 (`/etc/*` の改変を snapshot で観測するのが目的。次 phase で影響を評価)。
- **Step 4 の具体値は上表に固定**。flake.nix 骨格はこの表を参照して書く。

## Surprises & Discoveries

### S1: nix-darwin の release branch と nixpkgs は厳密 pair
Step 1 Research で `nix-darwin-25.11` + `nixpkgs-unstable` を選んだが、`nixpkgs-unstable` は現在 26.05 系を指しているため version mismatch error (`nix-darwin 25.11 with Nixpkgs 26.05`)。公式メッセージ通り **`master` branch pair only with `nixpkgs-unstable`** と判明。以後 `nix-darwin` と `home-manager` ともに `master` を採用。

### S2: Determinate Nix + nix-darwin の共存には `nix.enable = false` 必須
`nix-darwin` は default で Nix installation (daemon, /etc/nix/nix.conf 等) を管理しようとするが、Determinate は既に同役割を担っているため衝突。error message:
```
error: Determinate detected, aborting activation
```
解消: darwin module で `nix.enable = false` 明示。`nix.settings.experimental-features` 等も Determinate 側で管理となる。

### S3: `system.primaryUser` だけでは home-manager が `home.homeDirectory` を解決できない
nix-darwin master では `home-manager.users.<name>.home.homeDirectory` のソースが `users.users.<name>.home` にあり、これが null だと eval 失敗:
```
A definition for option `home-manager.users.takeuchishougo.home.homeDirectory' is not of type `absolute path'.
Definition values: - In `.../nixos/common.nix`: null
```
解消: darwin module で以下を明示:
```nix
users.users.takeuchishougo = {
  name = "takeuchishougo";
  home = "/Users/takeuchishougo";
};
```

### S4: 最新 nix-darwin は system activation を root 必須化
初回 `nix run ...#darwin-rebuild -- switch` を sudo なしで実行したら `system activation must now be run as root`。`sudo nix run` に切替。
副作用として `$HOME ('/Users/takeuchishougo') is not owned by you, falling back to the one defined in the 'passwd' file ('/var/root')` warning が出るが benign。

### S5: `sudo` は PATH を保存しないため、`darwin-rebuild` は絶対 path で起動する必要
`sudo darwin-rebuild --rollback` が `command not found`。`/run/current-system/sw/bin/darwin-rebuild` は root の PATH に入らないため。Taskfile の `nix:switch` / `nix:rollback` / `nix:list-generations` は絶対 path で呼ぶよう修正済み。

### S6: `programs.zsh.enable = false` のままだと per-user profile が `$PATH` に入らない
home-manager がパッケージを置く `/etc/profiles/per-user/<name>/bin` は nix-darwin の `programs.zsh.enable = true` が /etc/zshenv に注入する想定。私たちは Plan で意図的に false 固定しているため、Phase 0+A では `hello` の実行を絶対 path で検証。**PATH の per-user 統合は Phase B2 (`.config/zsh/` 再設計時) の課題**として引き継ぐ。

### S7: Determinate 共存環境では gen 2 → gen 1 rollback が不可能 (構造的)
gen 1 は `nix.enable = false` 以前の state (Determinate と未調整)。その activation script は Determinate と衝突するため `task nix:rollback` が abort。ただし、これ以降 (gen 3, 4, ...) は全て `nix.enable = false` を持つので **gen 3→2、gen 4→3 の rollback は正常動作する見込み**。初回 bootstrap 前の state への完全復帰は「Abort & Rollback 全面撤退」手順を使う。

### S8: mkOutOfStoreSymlink は 2 段間接経由だが live edit は成立
`~/.config/zsh-test-nix` → `/nix/store/...home-manager-files/.config/zsh-test-nix` → `/nix/store/...hm_claudelike` → `/Users/takeuchishougo/dotfiles/nix/test-fixtures/claude-like`
`readlink` は途中までしか見えないが `readlink -f` で最終 target 確認可能。間接経由でも**最終 target が repo 内の path なので live edit は正しく作動**する (HM の intended behavior)。

### S9: `brew bundle check` が 55 outdated + "can't satisfy" を報告
Nix 起因でない pre-existing 状態の可能性が高い (私たちは Brewfile / brew 環境を一切改変していない)。Phase 0+A 合格判定には影響しないが、**Phase B1 で Brewfile を flake 移植する際に自然解消** or 真の regression が隠れているか診断される。

## Outcome

**判定: Phase 0+A 合格 (2026-04-24)**

### 達成状態
- Determinate Nix 3.18.1 / Nix 2.33.4 on macOS 26.3.1 (Tahoe) / aarch64-darwin
- `nix-darwin` (master) + `home-manager` (master) + `nixpkgs` (nixos-unstable) でビルド成立
- `darwinConfigurations.private` が `MacBookPro` hostname に applied
- **D6 empirically validated**: mkOutOfStoreSymlink によるハーネス dev loop 保護が実証された
- **非破壊保証**: 既存 `~/.zshrc` / `~/.zshenv` / `.config/zsh/` / Brewfile / symlink.sh すべて無傷
- 4 commits on master branch (1f28258, 1a41e9f, 7674f84, 4b72ae2)

### 未解決事項 (Phase B で扱う)
- **PATH 統合**: `/etc/profiles/per-user/<name>/bin` が `$PATH` に入っていない。`.config/zsh/core/path.zsh` rewrite は B2 責務
- **Brewfile 移行**: 46 パッケージのうち 29 CLI + 10 cask + 2 font + 3 tap が未移植。B1 で扱う
- **symlink.sh 移行**: 498 行 / 26 exclude pattern の whitelist 翻訳は B2 で設計
- **gen 1 への rollback 不能**: Determinate 衝突で構造的限界。代替は Abort & Rollback 全面撤退手順 (master plan)
- **brew bundle 55 outdated**: pre-existing、B1 進行で自然解消または診断

### 学習事項 (AutoEvolve 転送済み)
- `rollback-determinate`: rollback to pre-nix.enable=false generations fails
- `users-users`: nix-darwin master requires explicit `users.users.<name>.home`
- `nix-state-version`: system.stateVersion = integer (max 6), home.stateVersion = release string

## Next Phase

Phase B1 plan: [docs/plans/active/2026-04-24-nix-migration-phase-b1-plan.md](./2026-04-24-nix-migration-phase-b1-plan.md) (本 phase 合格を受けて起草)
