---
topic: nix-migration-phase-b1
status: active
scope: M
parent: 2026-04-24-nix-migration-plan.md
prev_phase: 2026-04-24-nix-migration-phase-0a-plan.md
owner: takeuchi-shogo
created: 2026-04-24
success_criteria: "Brewfile が GUI cask / tap-only formula に縮退し、CLI 29 パッケージが `task nix:switch` 一発で揃う。新 shell で `which ripgrep` / `bat` / `gh` 等が nix 由来になる"
---

# Phase B1: Brewfile → flake 移植

マスタープラン: [2026-04-24-nix-migration-plan.md](./2026-04-24-nix-migration-plan.md)
前 phase (合格): [2026-04-24-nix-migration-phase-0a-plan.md](./2026-04-24-nix-migration-phase-0a-plan.md)

## Goal

現行 `Brewfile` の 46 エントリ (CLI 29 / cask 10 / font 2 / tap 3 / commented 2) を、**nixpkgs に在庫がある CLI は `home.packages` へ**、**GUI cask は `nix-darwin.homebrew.casks` で宣言的管理**、**tap-only / sandbox 制約のあるものは brew のまま**に再配置する。

Phase B1 完了時、`task brew` (brew bundle) タスクは形骸化し、Brewfile は GUI/cask 専用の短い declarative リストに縮退する。

## Scope

### In Scope
- **Tier 1**: 日常 CLI ツール 15 本前後 (`ripgrep`, `bat`, `eza`, `fd`, `dust`, `git-delta`, `yazi`, `fzf`, `zoxide`, `tree-sitter-cli`, `gh`, `jq`, `grep`, `neovim`, `lua`)
- **Tier 2**: 開発/周辺ツール 8-10 本 (`atuin`, `uv`, `nb`, `mo`, `git`, `sheldon`, `starship`, `direnv`)
- **Tier 3**: GUI cask 10 本 → `nix-darwin.homebrew.casks` 宣言化 (`wezterm`, `ghostty`, `aerospace`, `hammerspoon`, `karabiner-elements`, `sf-symbols`, `macskk`, `jordanbaird-ice`, `raycast`)
- **Tier 4**: tap 3 + tap-only formula (`FelixKratz/formulae` → `borders`, `k1LoW/tap` → `mo`, `nikitabobko/tap` → `aerospace`) を `nix-darwin.homebrew.taps` / `casks` で宣言
- **Bootstrap 最後**: `mise` の nix 化 (binary のみ、runtime 管理は mise のまま / D5 準拠)
- **PATH 統合**: `/etc/profiles/per-user/<name>/bin` を現行 `.config/zsh/core/path.zsh` に **後置** (brew 先頭順序を壊さない追加のみ)

### Out of Scope
- Font 2 本 (`font-hackgen-nerd`, `font-hack-nerd-font`) — nix fonts への移行は font cache 周りで罠が多く、**Phase C 以降で検討**。本 phase では brew cask のまま
- `macSKK` の nix 化 — macOS sandbox で /Library/Containers/ 配下に書くため nix 不向き。brew のまま固定
- symlink.sh の置換 — Phase B2
- `.config/zsh/core/path.zsh` の **順序再設計** — 本 phase では末尾 append のみ、B2 で本格 rewrite

### Decisions

| # | 決定 | 理由 |
|---|---|---|
| B1-D1 | brew binary 自体は残す | nix-darwin.homebrew module が brew CLI を必要とする (cask 宣言管理のため) |
| B1-D2 | tier 毎に「1 formula 単位」migrate: nix add → test → brew uninstall → Brewfile 削除 → commit | 万一 regression 発生時に `git revert` で 1 パッケージだけ戻せる |
| B1-D3 | bootstrap 系 (`sheldon`, `starship`, `mise`, `direnv`) は**最後に** migrate | shell 初期化順序への影響が最大、他を安定させてから |
| B1-D4 | fonts は B1 対象外 | macOS font cache の罠、優先度低 |
| B1-D5 | PATH に `/etc/profiles/per-user/<name>/bin` を末尾追加 | brew 先頭順序を保存しつつ nix package を findable にする (B2 で本格順序再設計) |
| B1-D6 | cask は brew install メカニズムを維持、宣言だけ nix-darwin に移す | nixpkgs に GUI app 相当物がない (wezterm/ghostty/raycast など) |
| B1-D7 | `home.packages` に nixpkgs 側の名前で記述 | 例: `brew "git-delta"` → `pkgs.delta` (名前が違う場合あり、Step 1 で全件 map を作る) |

## Steps

1. **[Research]** Brewfile 全 46 エントリを nixpkgs で検索。`nix search nixpkgs '^<name>$'` で在庫と正確な attribute 名を確認し、`docs/plans/active/2026-04-24-phase-b1-inventory.md` に以下 table で記録:
   | Brewfile 行 | brew name | nixpkgs attr | classification |
   |---|---|---|---|
   | `brew "ripgrep"` | ripgrep | `pkgs.ripgrep` | tier 1 |
   | `brew "borders"` | FelixKratz/formulae/borders | (なし) | tap-only / brew retain |
   | `cask "wezterm"` | wezterm | (N/A, GUI) | tier 3 cask |
   | ... | | | |
   Classification 値: `tier1-cli` / `tier2-tooling` / `tier3-cask` / `tier4-tap` / `bootstrap` / `brew-retain` / `font-defer`
2. **[Design]** PATH append 設計: `.config/zsh/core/path.zsh` のどこに `/etc/profiles/per-user/<name>/bin` を追加するか決定。ルール: (a) brew 先頭を動かさない、(b) mise shim より先・brew より後、(c) 移行途中で brew と nix 両方から同名ツールが見える期間を短縮する。設計を **Step 7 で適用**するため一旦 design memo だけ書く
3. **[Impl-Tier1]** 日常 CLI 15 本を `home.packages` に追加。1 formula 単位でループ:
   - `nix/home/default.nix` に pkg 追加 → `task nix:switch` → 新 shell で `which <pkg>` が nix 由来を返すこと確認 → `brew uninstall <pkg>` → `Brewfile` から行削除 → commit
   - 15 本分の commit が積まれる想定 (log で進捗管理)
4. **[Impl-Tier2]** 開発/周辺ツール 8-10 本を同じループで移植。`git` は config の所在 (`.gitconfig` symlink) が絡むため慎重に。`sheldon`/`starship` は tier2 でなく bootstrap 扱いに格下げする可能性あり (Step 1 の inventory で最終判断)
5. **[Impl-Tier3]** GUI cask 10 本を `nix-darwin.homebrew.casks` に宣言化:
   ```nix
   # nix/darwin/default.nix
   homebrew = {
     enable = true;
     casks = [ "wezterm" "ghostty" "aerospace" "hammerspoon" "karabiner-elements"
               "sf-symbols" "macskk" "jordanbaird-ice" "raycast" ];
     onActivation.cleanup = "none";  # 既存 cask を勝手に uninstall しない
   };
   ```
   `onActivation.cleanup` は初回 `"none"` 固定 (Codex review Consider-#4)。`task nix:switch` 後、対応する `cask "..."` 行を Brewfile から削除
6. **[Impl-Tier4]** tap-only formula を `nix-darwin.homebrew.taps` + `brews` (CLI tap) or `casks` で宣言:
   ```nix
   homebrew.taps = [ "FelixKratz/formulae" "k1LoW/tap" "nikitabobko/tap" ];
   homebrew.brews = [ "borders" "mo" ];
   ```
7. **[Impl-Bootstrap]** bootstrap set を最後に migrate: `mise`, `direnv`, `sheldon`, `starship`。それぞれ shell 再起動して `mise --version` / `starship --version` 等が nix 由来で動くことを確認。同時に Step 2 で設計した PATH append を `.config/zsh/core/path.zsh` に実装 (既存 config への最小変更)
8. **[Verify & Docs]** Brewfile 最終形: CLI 全消去、cask は tier3 tier4 分を残すが「nix-darwin から管理されている」コメント付き。`nix/README.md` 更新 (B1 完了、Brewfile の位置づけ変更)。`task nix:check` が pass、`task validate` green、新 shell で日常ツール全て `which` で nix 由来

## Progress

- [ ] Step 1: Brewfile inventory + nixpkgs マッピング
- [ ] Step 2: PATH append design memo
- [ ] Step 3: Tier 1 CLI 15 本を逐次移植 (1 commit/formula 目安)
- [ ] Step 4: Tier 2 ツール 8-10 本を逐次移植
- [ ] Step 5: Tier 3 GUI cask 宣言化 (nix-darwin.homebrew.casks)
- [ ] Step 6: Tier 4 tap 宣言化 (nix-darwin.homebrew.taps/brews)
- [ ] Step 7: Bootstrap 系移植 + PATH append 適用
- [ ] Step 8: Brewfile 最終縮退 + README 更新 + 検証

## Verification (Exit 条件)

- `brew bundle list --file=Brewfile | wc -l` → 15 以下 (GUI cask + font のみ)
- 新 shell で `which ripgrep bat eza fd gh` 全て `/etc/profiles/per-user/.../bin/` or nix-profile 配下
- `task nix:switch` の後、`darwin-rebuild --list-generations` で複数世代が積まれ、**gen N → gen N-1 の rollback 成功** (S7 の Determinate 衝突は初期世代に限る前提の実地確認)
- `task validate` / `task symlink` 両方 green (regression なし)
- 実機 daily workflow で違和感なし (fzf tab 補完、yazi 起動、starship prompt、zoxide ジャンプ)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| nixpkgs に必須 formula がない (borders 等) | 小 | Step 1 inventory で検出、brew-retain 分類へ |
| 移行途中で PATH に brew と nix 両方の同名 tool | 中 | Step 3/4 で「nix add → brew uninstall → Brewfile 削除」を**同 commit 内で完結**、同名共存期間を最短化 |
| `homebrew.onActivation.cleanup` が意図せず既存 cask 消す | 中 | 初回は `"none"`、挙動を目視確認後に設定変更 (Codex review Consider-#4) |
| `git` を nix に移したら既存 .gitconfig が読まれない | 中 | git 本体の XDG 規約は nix build でも変わらない想定、`~/.gitconfig` symlink が壊れていないことを migrate 前後で `git config --global --get user.name` で確認 |
| bootstrap tool (sheldon/starship) を nix 化した瞬間に shell が壊れる | 大 | Step 7 で tmux を別セッションで立てた状態で作業、新 shell が壊れても rollback で復旧可能な状態を保つ |
| `mise` を nix に移して runtime (.mise.toml) が読めなくなる | 中 | mise の runtime 管理は `~/.local/share/mise/` 配下で binary 位置に非依存、config は `~/.config/mise/` で独立 |
| Font 系が Brewfile に残り `brew bundle` 不整合 | 小 | Brewfile は短縮後も存在、`task brew` は scope 明記 (fonts + cask のみ) |

## Abort & Rollback

1 formula 移行に失敗: `git revert <commit>` で該当 1 commit を戻す → `task nix:switch` で前世代適用。
Phase 全体を abort: master plan の **Abort & Rollback Criteria** (Phase B1 行) に従い、flake.nix revert + `brew bundle --file=Brewfile` で元の Brewfile 経由 install を復活。

## Decision Log

- (Step 実行中に追記)

## Surprises & Discoveries

- (実装中に追記)

## Outcome

- (Phase 完了時に追記)

## Next Phase

Phase B2 (symlink.sh → home-manager 移植) — 本 phase 完了を待って plan 起草。**B2 着手前提として、Phase 0+A Step 5b で作った test fixture (`nix/test-fixtures/claude-like/` と `~/.config/zsh-test-nix/`) を削除するタスクを B2 plan の Step 1 に含めること**。
