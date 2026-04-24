---
topic: nix-migration
status: active
scope: L
owner: takeuchi-shogo
created: 2026-04-24
success_criteria: "Brewfile と symlink.sh が nix/flake.nix に吸収され、`darwin-rebuild switch --flake ./nix#private` 一発でマシン再現可能"
---

# Nix 全面移行 — マスタープラン

既存の Homebrew + 独自 symlink.sh + init-install.sh 構成を、段階的に `flake.nix` + `home-manager` + `nix-darwin` に置き換える。

## Goal

`dotfiles` リポジトリを clone して 1 コマンド (`darwin-rebuild switch --flake ./nix#<host>`) 実行するだけで、プライベート/仕事用どちらの macOS も再現可能にする。Homebrew は **tap/cask 固有の GUI 依存のみ** に縮退させ、CLI と dotfiles symlink は完全に宣言化する。

## Scope

### In Scope
- Brewfile (46 entries) → `nix/` 配下の flake に吸収
- symlink.sh (498 lines, 26 除外) → `home-manager` + `mkOutOfStoreSymlink`
- init-install.sh (11KB) → `nix-darwin` に吸収可能な部分を移行
- macOS システム設定 (`system.defaults`) → Phase C
- マルチホスト対応: `private` (現 MacBookPro) + `work` (今後の仕事用 Mac)

### Out of Scope
- **nixvim (Neovim 設定の Nix 化)** — 別プロジェクトとして Phase C 完了後に spike
- **Rust claude-hooks / Python codex-janitor の Nix 化** — Taskfile 残置、`rustPlatform.buildRustPackage` 等は将来検討
- **`mise` 管理下の runtime (Node/Go/Python/Ruby)** — `mise` バイナリを nix で入れるのみ、runtime 本体は mise のまま
- **`.config/claude/` 配下のハーネス実装** — Nix で symlink を張るだけで、コード・Python 依存は触らない
- **CI/GitHub Actions の Nix 化** — 現行 workflow を壊さない範囲で

## Decision Log

| # | 決定 | 理由 |
|---|---|---|
| D1 | `nix/` サブディレクトリに隔離 | repo root は既に肥大。flake を独立管理したい |
| D2 | `darwinConfigurations.{private, work}` 名前付きキー | hostname 依存は macOS 更新や rename で壊れやすい |
| D3 | nixpkgs first (CLI 全移行) | 宣言的・rollback・clean uninstall の恩恵を最大化 |
| D4 | GUI app / tap 固有は `nix-darwin.homebrew.casks` で宣言 | borders/ice/macskk/nb は cask/tap のみ提供 |
| D5 | `mise` は併用 (binary のみ nix 管理) | runtime 切替頻度・project-local `.mise.toml` 連携を壊さない |
| D6 | `mkOutOfStoreSymlink` を `.config/claude`, `.codex`, `.gemini`, `.cursor`, `.config/zsh`, `.hammerspoon` に適用 | ハーネス dev loop (edit → 即反映) 保護 |
| D7 | nixvim は今回対象外 | AstroNvim からの翻訳コストが別規模 |
| D8 | `claude-hooks` (Rust), `codex-janitor` (Python) は Taskfile 残置 | `mkOutOfStoreSymlink` パターンと競合しない既存パスを温存 |
| D9 | Homebrew は `nix-darwin.homebrew` module 経由で宣言的に残す | GUI cask / tap-only formula (borders 他) は nix だけで賄えない |

## Phase 構成

Compound Ceiling (≤ 8 steps) に従い、phase 単位で plan を分割する。

| Phase | 目的 | Plan ファイル | Exit 条件 |
|---|---|---|---|
| **0+A** | Nix 導入 + flake 骨格 + **D6 mkOutOfStoreSymlink 実検証** | `2026-04-24-nix-migration-phase-0a-plan.md` | `hello` 動作 + mkOutOfStoreSymlink で `~/.config/zsh-test-nix/` (claude-like fixture tree) が live symlink として機能 + rollback 動作確認済み |
| **B1** | Brewfile → flake 移植 | (Phase 0+A 完了後に作成) | 46 パッケージ全てが `darwin-rebuild` で揃う。**Exit 条件: 1 formula ずつ切替** (brew uninstall → nix add → 動作確認のループ) |
| **B2** | symlink.sh → home-manager | (B1 完了後に作成、**着手前に 26 exclude pattern の whitelist 翻訳表を先行作成**) | `.bin/symlink.sh` を捨てても `.claude/`, `.codex/` 等が live symlink で機能 |
| **C** | `system.defaults` 統合 | (B2 完了後に作成) | Dock/Finder/入力ソース設定が宣言化、work Mac セットアップが `darwin-rebuild` 1 発 |

各 phase の内訳は phase plan で詳細化。master plan はあくまで "全体の歯車が揃っているか" の検証用。

## PATH Resolution Strategy

### 現状 (Phase 0+A 開始時点 / 不変)

`.config/zsh/core/path.zsh` で `/opt/homebrew/bin` を先頭 prepend、`.config/zsh/tools/mise.zsh` で mise activate。つまり実効優先は:

```
現状 (変更禁止):
1. Homebrew: /opt/homebrew/bin (先頭)
2. mise: ~/.local/share/mise/shims (activate 経由)
3. System: /usr/bin, /bin
```

### Phase 0+A の扱い

Phase 0+A では **この順序を保存する**。Nix PATH が追加されることは許容するが、優先順位を再設計しない。検証条件は「Nix が `$PATH` のどこかに含まれ、かつ既存 brew 先頭順序が壊れていない」まで。

### 将来の目標 (B1/B2 で確定)

```
目標 (B1/B2 で実装と同時に決定):
1. Project-local: mise (.mise.toml per project)
2. User Nix profile: ~/.nix-profile/bin
3. System Nix profile: /run/current-system/sw/bin
4. Homebrew: (縮退、GUI cask と tap-only formula のみ)
5. System: /usr/bin, /bin
```

**原則**: mise と nix は同じツール (例: `git`, `node`) を両方から入れない。nix に入れるか mise に入れるかは phase B1 の unit 設計で決める。`.config/zsh/core/path.zsh` の rewrite は **Phase B1 の最後または B2 で** 実施し、Phase 0+A では触らない。

## Abort & Rollback Criteria

各 phase で撤退可能な条件と手順を事前に固定する。

| Phase | Abort condition | Rollback 手順 |
|---|---|---|
| **0+A** | `darwin-rebuild switch` 失敗 / rollback 不能 / mkOutOfStoreSymlink テスト失敗 | `darwin-rebuild --rollback` → Nix アンインストール (Determinate: `/nix/nix-installer uninstall`) |
| **B1** | `nix flake update` で lock 破壊、または必須 formula が nixpkgs にない | `git revert` flake.nix → `darwin-rebuild switch` → 必要なら `brew bundle --file=Brewfile` |
| **B2** | home-manager activation が `.claude/` 等の既存 symlink を破壊 | **事前 backup 必須**: `tar czf ~/backup/dotfiles-state-$(date +%s).tar.gz ~/.claude ~/.codex ~/.gemini ~/.cursor ~/.hammerspoon ~/.config/zsh` → revert flake → `.bin/symlink.sh` 再実行 |
| **C** | `system.defaults` が macOS を破壊 (Dock 消失、入力不能等) | `darwin-rebuild --rollback` → Safe Mode で起動 → 再度 rollback |

**全面撤退 (Nix を完全に剥がす — best-effort + residual check)**:

uninstaller だけでは残渣が残る可能性があるため、以下を順に実施し、各段階で残渣チェックする。

1. `darwin-rebuild --rollback` を Nix 導入前世代まで繰り返す
2. Nix アンインストール: `/nix/nix-installer uninstall` (Determinate) を実行
3. **残渣チェック & 手動削除** (Determinate uninstaller でも残ることがある):
   - `/etc/zshenv` / `/etc/bashrc` / `/etc/zshrc` / `/etc/zprofile` / `/etc/zsh/*` の Nix 行を手動削除 (Step 2/3 の snapshot 差分を参照)
   - `/etc/synthetic.conf` に `nix` 行が残っていないか確認・削除
   - APFS volume: `diskutil apfs list | grep -i nix` で残存確認、残っていれば `diskutil apfs deleteVolume disk*s*` で削除
   - Keychain: "Nix Store" など encrypted volume 用 secret を Keychain Access で確認・削除
   - launchd residue: `launchctl list | grep -i nix` / `/Library/LaunchDaemons/org.nixos.*.plist` / `/Library/LaunchAgents/org.nixos.*.plist` を確認・unload/削除
   - `/var/root/.nix-*` / `~/.nix-profile` / `~/.nix-defexpr` / `~/.nix-channels` の残存確認
4. `brew bundle --file=Brewfile` で既存 Brewfile を復元
5. `.bin/symlink.sh` で symlink を復元
6. 各 phase で削除した Brewfile エントリや symlink.sh 除外パターンは git 履歴から復旧
7. 再起動後、`mount` に `/nix` が出ないこと、`echo $PATH` に `/nix` 参照が残らないことを確認

## Progress (phase level)

- [ ] Phase 0+A: Bootstrap (plan: active/2026-04-24-nix-migration-phase-0a-plan.md)
- [ ] Phase B1: Brewfile migration
- [ ] Phase B2: symlink.sh migration
- [ ] Phase C: system.defaults

## Surprises & Discoveries

- (実装中に追記)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| home-manager の `/nix/store` read-only symlink がハーネス dev loop を破壊 | 致命 | **D6** (`mkOutOfStoreSymlink`) を B2 の原則として固定 |
| nix と brew の両方で同じパッケージが入り PATH 衝突 | 中 | B1 で "brew を剥がしてから nix に切替" を 1 パッケージずつ実施、移行期は両立禁止 |
| `darwin-rebuild` 失敗時にシステム不整合 | 中 | 各 phase の Exit 条件に "rollback テスト" を必須化。Nix の世代管理で `darwin-rebuild --rollback` を常時利用可能にしておく |
| 仕事用 Mac が未入手のため `work` config が検証不能 | 中 | `work = private` のエイリアスとして宣言。ただし flake.nix は最初から multi-system (`aarch64-darwin` + `x86_64-darwin`) 対応構造で書く。仕事用が Intel Mac だった場合の flake.lock rebuild リスクを Phase 0+A で緩和 |
| `macSKK` / `aerospace` など sandbox/permission 要求アプリ | 小 | `homebrew.casks` 宣言後も初回起動での手動許可は必要。README に明記 |
| Determinate Systems installer と Apple SIP の相互作用 | 小 | 公式 multi-user install を選択。`/etc/zshrc` 管理は **Phase 0+A 〜 B1 までは `nix-darwin.programs.zsh.enable = false` 固定** (既存 `.config/zsh/` との二重衝突を避ける)。`true` 化の判断は B2 で shell 初期化を再設計する際に別 decision として扱う |

## Outcome

- (全 phase 完了時に追記)

## References

- 参考資料:
  - [NixOS 公式](https://nixos.org/)
  - [asa1984: Nix Introduction](https://zenn.dev/asa1984/books/nix-introduction/viewer/02-what-is-nix)
  - [ryota2357: Nix CLI 運用](https://ryota2357.com/blog/2025/use-and-start-nix-as-cli-mma2025b/)
  - [hanao: Zero to Nix](https://zenn.dev/hanao/articles/140d8a1ce32830)
- 既存資産:
  - `Brewfile` — 46 entries (CLI 29 / cask 10 / font 2 / tap 3 / 既に comment out されたもの 2)
  - `.bin/symlink.sh` — 498 lines, exclusion 26 patterns, directory-level symlinks 7 targets
  - `.bin/init-install.sh` — 11KB bootstrap script
  - `Taskfile.yml` — 23 tasks, うち `symlink` / `install` / `brew` は本移行で置換対象
