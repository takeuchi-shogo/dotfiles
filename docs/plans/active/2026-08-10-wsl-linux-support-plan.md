---
lifecycle: active
success_criteria: "nix flake check が通り、homeConfigurations.<user>@wsl が評価でき、Mac 側の darwinConfigurations 評価と PATH 順序が変わらない"
artifacts: "nix/flake.nix, nix/home/default.nix, .config/zsh/core/path.zsh, docs/playbooks/wsl-windows-setup.md"
asserts: "validate-configs"
---

# WSL (Linux) 向け home-manager 出力の追加

## Goal

Windows 機の WSL2 上でこの dotfiles の CLI + AI エージェントハーネス層を動かせるようにする。
Mac 側 (`darwinConfigurations`) の挙動は一切変えない。

背景と全体手順は `docs/playbooks/wsl-windows-setup.md`。この plan はそのうち
「Phase B: 先に Mac 側で片付ける repo 変更」だけを担当する。

## Success Criteria

- `nix flake check ~/dotfiles/nix` が通る
- `nix eval ~/dotfiles/nix#homeConfigurations."<user>@wsl".config.home.homeDirectory` が `/home/<user>` を返す
- `nix eval ~/dotfiles/nix#darwinConfigurations.private.system.name`（または同等）が従来どおり評価できる
- Mac の login shell で `echo $PATH` の先頭が従来どおり `/opt/homebrew/bin` のまま
- `task validate-configs` / `task validate-symlinks` が通る

## Scope

触る:

- `nix/home/default.nix` — `home.packages` の Linux 分岐、`home.homeDirectory` の分岐、macOS 専用 `home.file` の切り出し
- `nix/flake.nix` — `mkHome` と `homeConfigurations` の追加
- `.config/zsh/core/path.zsh` — standalone home-manager の profile を PATH に入れる Linux 分岐
- `docs/playbooks/wsl-windows-setup.md` — 上の変更を反映して手順を更新

触らない:

- `nix/darwin/` 一式 — Homebrew と system defaults。`darwinConfigurations` からしか参照されない
- `.config/claude/settings.json` — nix 非管理。WSL 側の変換は playbook の手順に置く（tracked file を増やすと drift 源になる）
- `home/{common,darwin,linux}.nix` への 3 分割 — 共通が 9 割なので今は不要

## Constraints

- Mac の PATH 順序を変えない。`path.zsh` は `/opt/homebrew/bin` 先頭を意図的に保っている
- Homebrew に残した bootstrap 層 (git/sheldon/starship/mise/direnv) は Mac 側では brew のまま。B1.5 の判断を覆さない
- `settings.json` を tracked file として二重化しない
- ハーネス変更なので `task validate-configs` / `task validate-symlinks` を最低検証とする

## Unknowns

- **自前 derivation 4 本** (ghqr, crit, terminal-browser, mirador) と herdr overlay が `x86_64-linux` でビルドできるか未確認。落ちたら該当分を `lib.optionals pkgs.stdenv.isDarwin` に退避する
- **`direnv` の checkPhase ハング**は Apple Silicon + Determinate 固有だったので Linux では再発しない見込みだが未確認
- **attribute 名**: `sheldon` と `go-task` が nixpkgs でその名前か未確認
- **UNIX ユーザー名が未定**。Ubuntu 初回起動で決まる。`homeConfigurations` のキーはプレースホルダで置き、ユーザーが 1 文字列だけ差し替える
- **standalone home-manager に `home-manager.backupFileExtension` は無い**（nix-darwin/NixOS module 側のオプション）。初回衝突は CLI の `-b backup` で回避する
- Linux 実機がないので、この plan の検証は `nix flake check` までの評価レベルに留まる。実際の `switch` は未検証

## Validation

- `nix flake check ~/dotfiles/nix`
- `task validate-configs`
- `task validate-symlinks`
- Mac の login shell で PATH 先頭が変わっていないこと

## Steps

1. `nix/home/default.nix` の `home.packages` に Linux 限定分岐を足す（bootstrap 層 + nodejs + cargo/rustc）
2. `nix/home/default.nix` の `home.homeDirectory` を分岐し、macOS 専用 `home.file` を `optionalAttrs isDarwin` に切り出す
3. `nix/flake.nix` に `mkHome` と `homeConfigurations` を足す
4. `.config/zsh/core/path.zsh` に Linux 分岐を足す（`uname` gate。Mac には `~/.nix-profile` が実在するので `-d` 判定だけでは Mac の PATH 順序を壊す）
5. `docs/playbooks/wsl-windows-setup.md` を更新（`backupFileExtension` の誤り訂正、path.zsh 済みの反映、settings.json 変換手順の具体化）
6. 検証を回す

## Progress

- [x] Step 1 — `home.packages` の Linux 分岐
- [x] Step 2 — `homeDirectory` 分岐 + macOS 専用 `home.file` の切り出し
- [x] Step 3 — `mkHome` + `homeConfigurations."CHANGEME@wsl"`
- [x] Step 4 — `path.zsh` の Linux 分岐 (`$OSTYPE` gate)
- [x] Step 5 — playbook 更新
- [x] Step 6 — 検証

## Surprises & Discoveries

- Mac には `~/.nix-profile` が実在する (`~/.local/state/nix/profiles/profile` への symlink)。standalone home-manager 用の PATH 分岐を `[ -d ~/.nix-profile/bin ]` だけで書くと Mac の PATH 順序を壊すため、`uname` で切る必要がある
- `rtk hook claude` は `PreToolUse` の独立した matcher group ({"matcher":"Bash"}) として入っている。sed では安全に落とせないので、WSL 側の変換は JSON を読む処理が必要
- `cargo` / `rustc` が repo のどこにも宣言されていない。Mac では偶然入っているだけで、`task build-hooks` は未宣言依存の上に成立している

## Decision Log

- **`settings.json` の WSL 版を tracked file にしない**: 既に nix 非管理で live drift の実績がある (memory: `project_claude_settings_live_drift`)。variant を増やすと drift 源が 2 倍になる。playbook 側に変換手順を置く
- **home モジュールを 3 分割しない**: macOS 固有が 1 行 + `home.file` 6 エントリで、共通が 9 割。先に割ると共通側を触るたびに 3 ファイル見ることになる
- **`zsh` を nix 側に入れない**: Ubuntu の `chsh` が `/etc/shells` 掲載のシェルしか受け付けないため、apt 版を使う

## Outcome

Mac 側の repo 変更 (Phase B) は完了。実測した検証結果:

| 検証 | 結果 |
|---|---|
| `nix eval .#homeConfigurations."CHANGEME@wsl".config.home.homeDirectory` | `/home/CHANGEME` |
| Linux 側 `home.file` に macOS 専用 6 エントリが無い | `[]` (0 件) |
| Linux 側 `home.packages` の bootstrap 層 | git 2.53.0 / sheldon 0.8.5 / starship 1.24.2 / mise 2026.4.6 / direnv 2.37.1 / go-task 3.48.0 / nodejs 24.14.1 / cargo 1.94.1 / rustc-wrapper 1.94.1 — 全て解決 |
| darwin 側 `homeDirectory` | `/Users/shogo_takeuchi` (不変) |
| darwin 側 macOS 専用 6 エントリ | 6 件すべて存在 |
| `nix flake check` | exit 0 |
| Mac の PATH (path.zsh 変更前後の diff) | byte 単位で同一 |
| `task validate-configs` / `task validate-symlinks` | exit 0 / exit 0 |
| `settings.json` WSL 変換 snippet | `/opt/homebrew` 0 件、`rtk ` 0 件、node hook 4 件を書き換え |

### 未解決

- **Linux でのビルドは未検証。** 上は全て評価 (eval) レベル。`nix flake check` は `x86_64-linux` を
  "incompatible systems" としてスキップし、`homeConfigurations` は非標準 output なので評価対象にすら入らない。
  自前 derivation 4 本 (ghqr, crit, terminal-browser, mirador) と herdr overlay が実際にビルドできるかは
  WSL 実機で `switch` するまで分からない
- **`CHANGEME` プレースホルダが残っている。** Ubuntu 初回起動でユーザー名が決まったら
  `nix/flake.nix` の attr key と `userName` の 2 箇所を差し替える。上の eval が証明しているのは
  `/home/CHANGEME` が評価できることだけなので、**差し替え後に同じ eval を再実行する**
  (`nix eval ~/dotfiles/nix#homeConfigurations."<user>@wsl".config.home.homeDirectory`)
- **`task validate-configs` は非対話シェルで失敗する。** `python3` が `/usr/bin/python3` に解決され
  tomllib (3.11+) が無い。mise shims を PATH に入れれば通る。この plan の変更とは無関係の既存事象で、
  memory `project_dotfiles_tooling_gotchas` の「cmux 子プロセスの PATH は mise activate を経由しない」と同類
- **`.config/cmux` / `.config/ghostty` / `.config/wezterm` は macOS 専用ブロックに入れていない。**
  cmux は cask (macOS >= 14) 専用、ghostty は Windows ビルドなし、wezterm はターミナルなので WSL 内では無意味。
  ただし Linux で dangling symlink が生えるだけで無害なため、scope 外として据え置いた。整理するなら別途
