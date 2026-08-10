# WSL (Windows) Setup

> SOP template: `.config/claude/agents/document-factory.md` の SOP / Runbook 型に準拠。

## Purpose

まっさらな Windows 機に WSL2 を立て、この dotfiles の CLI + AI エージェントハーネス層を展開する手順。
macOS 専用の WM / UI 層 (aerospace, karabiner, hammerspoon, sketchybar, borders) は移植対象外とし、
Windows 側では意図的に配線しない。

動機は Power Automate (Windows ネイティブ) と Claude Code の併用。両者は競合しないので、
ネイティブ Windows 版 dotfiles を作る必要はない。切り分けは末尾の「Power Automate との併用」を参照。

## Status: 未検証

この playbook は Linux 実機で走らせて確認していない。Nix インストール以降は
リポジトリのコードを読んで導いた手順で、実際に踏むと差異が出る可能性が高い。
詰まった箇所はこのファイルに追記して確定させること。

## Read First

- `nix/flake.nix` — 現状 `darwinConfigurations` のみ。Linux system の出力がない
- `nix/home/default.nix` — home-manager module。macOS 固有は L15 の `homeDirectory` と `home.file` 6 エントリのみ
- `nix/darwin/default.nix` L47-51 — bootstrap 層が Homebrew に残っている (B1.5 の判断)
- `.config/claude/settings.json` — nix 非管理。hook に macOS 絶対パスが入っている
- `.config/zsh/core/path.zsh` — PATH 構築

## 前提: 先に潰すブロッカー

Windows 機を触る前に、Mac 側で以下を済ませておく必要がある。ここが未了だと Phase C が走らない。

**B-1 / B-2 / B-3 は実装済み** (`docs/plans/active/2026-08-10-wsl-linux-support-plan.md`)。
残りは B-4 (`settings.json` の変換、Phase D-10 で実施) と、`CHANGEME` プレースホルダの差し替え。
以下は何をなぜ変えたかの記録として残す。

### B-1. Homebrew bootstrap 層に Linux 版を用意する

`nix/darwin/default.nix` の `homebrew.brews` にいる `git` `sheldon` `starship` `mise` `direnv` `go-task`
は Mac では brew が供給しているが、WSL には Homebrew がない。とくに **`go-task` が無いと `task` コマンドが
使えず、この repo のワークフローがすべて止まる**。

`nix/home/default.nix` の `home.packages` に、Linux でだけ効く分岐を足す。

```nix
home.packages = with pkgs; [
  # ... 既存の共通パッケージ ...
] ++ lib.optionals (!pkgs.stdenv.isDarwin) [
  git sheldon starship mise direnv go-task nodejs cargo rustc
];
```

Mac 側は B1.5 の判断どおり brew に残すので、この分岐は Linux にだけ効かせる。

`nodejs` を含めるのは、`node` が現状どこにも宣言されていないため。実体は `/opt/homebrew/bin/node`
(v25.6.1) だが `brews` にも `home.packages` にも書かれていない未宣言 drift で、WSL には何も無い状態になる。
`settings.json` の SessionStart hook が node を直接叩くので、ここを埋めないと起動のたびに hook が黙って落ちる。

`cargo` / `rustc` は `task build-hooks` (`cargo build --release`) のため。これも Mac 側は
どこにも宣言がなく、`task setup` チェーンの 1 本目なのでここで止まる。

`zsh` は入れない。Phase A-4 で apt から入れる (`chsh` が `/etc/shells` 掲載のシェルしか受け付けないため)。

attribute 名は `x86_64-linux` で全て解決することを確認済み — git 2.53.0 / sheldon 0.8.5 /
starship 1.24.2 / mise 2026.4.6 / direnv 2.37.1 / go-task 3.48.0 / nodejs 24.14.1 /
cargo 1.94.1 / rustc-wrapper 1.94.1。ただし**評価が通っただけでビルドは未検証**。
`direnv` の checkPhase ハングは Apple Silicon + Determinate 固有だったので Linux では再発しない見込みだが、確認はしていない。

### B-2. flake に Linux 出力を足す

`mkDarwin` の隣に `mkHome` を作る。`darwinConfigurations` とは別系統になるので、
`nix/darwin/` 配下は一切触らない (Homebrew も system defaults も Linux 側に漏れない)。

```nix
mkHome = { system, userName }:
  home-manager.lib.homeManagerConfiguration {
    pkgs = import nixpkgs { inherit system; overlays = [ herdr.overlays.default ]; };
    extraSpecialArgs = { inherit userName; };
    modules = [ ./home ];
  };

homeConfigurations."<unix-user>@wsl" = mkHome { system = "x86_64-linux"; userName = "<unix-user>"; };
```

`<unix-user>` は Phase A-2 で Ubuntu の初回起動時に決める UNIX ユーザー名と同じ文字列。
リポジトリには `CHANGEME` をプレースホルダとして置いてあるので、**attr key と `userName` の
2 箇所を差し替える**。

初回衝突は `mkHome` 側では防げない。`home-manager.backupFileExtension` は
nix-darwin / NixOS module 側のオプションで、standalone `homeManagerConfiguration` には存在しない
(書くと unknown option で落ちる)。Ubuntu 既存の `~/.profile` と apt zsh の `~/.zshrc` との衝突は、
Phase C の CLI 側 `-b backup` で回避する。

### B-3. macOS 専用 symlink を分岐に落とす

`nix/home/default.nix` の `home.file` から macOS 専用エントリを切り出す。

```nix
home.homeDirectory =
  if pkgs.stdenv.isDarwin then "/Users/${userName}" else "/home/${userName}";

home.file = {
  # ... 共通エントリはそのまま ...
} // lib.optionalAttrs pkgs.stdenv.isDarwin {
  ".hammerspoon"       = outLink ".hammerspoon";
  ".config/aerospace"  = outLink ".config/aerospace";
  ".config/borders"    = outLink ".config/borders";
  ".config/karabiner"  = outLink ".config/karabiner";
  ".config/sketchybar" = outLink ".config/sketchybar";
  "Brewfile"           = outLink "Brewfile";
};
```

ファイルを `home/{common,darwin,linux}.nix` に 3 分割するのは、WSL 固有の設定が実際に増えてからでいい。
今は共通部分が 9 割なので、先に割ると共通側を触るたびに 3 ファイル見ることになる。

### B-4. settings.json の WSL 版を用意する

`.config/claude/settings.json` は nix 非管理で、新マシンでは手動 cp が正規手順
(`nix/home/default.nix` L72-75)。ただし素のまま cp すると 2 系統の hook が壊れる。

| 壊れる箇所 | 理由 | 対応 |
|---|---|---|
| `/opt/homebrew/bin/node` × 4 | Linux に存在しない | `~/.nix-profile/bin/node` 等の絶対パスに置換。単なる `node` にすると、hook が非ログインシェルで PATH 無しに走るという元のバグが再発する |
| `rtk hook claude` | `rtk` は `k1LoW/tap` 専用で Linux ビルドが無い | 該当 hook を落とす |

**この表は完全ではない。** 監査したのは `settings.json` だけで、ハーネス配下
(`.config/claude` / `.codex` / `.cursor` / `scripts`、計 1409 ファイル) のうち
`/opt/homebrew` `/Users/` `Library/Application Support` `osascript` `pbcopy` のいずれかを含むものが
84 ファイルある。残り 82 は未 triage で、実行時に追加で表面化する。

---

## Standard Steps

### Phase A: Windows 素の状態 → Nix が動く WSL

repo の状態に依存しない。Windows 11、または Windows 10 2004 以降が前提。

1. 管理者権限の PowerShell で `wsl --install` を実行し、Windows を再起動する
2. Ubuntu が初回起動したら UNIX ユーザー名とパスワードを設定する。**この名前は B-2 の `mkHome` に入る文字列と一致させる**
3. systemd を有効化する。`/etc/wsl.conf` に以下を書き、PowerShell 側で `wsl --shutdown` してから入り直す

   ```ini
   [boot]
   systemd=true
   ```

   nix-daemon と、launchd 相当の定期実行に必要。

4. 下地パッケージを入れる。`sudo apt update && sudo apt install -y curl git zsh`
   - ここで入れる `git` は clone のための踏み台。B-1 で nix 側にも git が入るので二重になる
5. Nix を入れる。Mac と同じ Determinate 版でいい。

   ```bash
   curl -fsSL https://install.determinate.systems/nix | sh -s -- install
   ```

   終わったらシェルを開き直す。

6. dotfiles を clone する。**必ず WSL 側の `~` に置く。**

   ```bash
   git clone https://github.com/takeuchi-shogo/dotfiles.git ~/dotfiles
   ```

   **HTTPS で clone する。** repo は public なので、この時点では認証が要らない
   (`gh auth login` は D-12 で、clone より後)。Mac 側の remote は SSH (`git@github.com:...`) だが、
   SSH のままだと鍵が無い初期状態で clone できない。

   push もするなら D-12 と D-13 (認証と鍵) の後に remote を張り替える:

   ```bash
   git -C ~/dotfiles remote set-url origin git@github.com:takeuchi-shogo/dotfiles.git
   ```

   `/mnt/c` 以下に置くと symlink とパーミッションが壊れ、I/O も体感でわかるほど遅くなる。

### Phase B: repo 変更を反映

上の「前提」セクション B-1 〜 B-4 を Mac 側で済ませ、push しておく。WSL 側では `git pull` するだけ。

### Phase C: 適用

7. home-manager を初回適用する。standalone なので `nix run` 経由で起動する。

   ```bash
   nix run home-manager/master -- switch --flake ~/dotfiles/nix#<unix-user>@wsl
   ```

8. PATH を確認する。`command -v task starship sheldon mise node` が全部通ること。
   `.config/zsh/core/path.zsh` の WSL 分岐は**追加済み**。standalone home-manager は
   nix-darwin の `/etc/profiles/per-user/$USER/bin` ではなく `~/.nix-profile` に置くため、
   そちらを PATH 先頭に足して `hm-session-vars.sh` を手動 source する
   (`programs.zsh.enable = false` のため)。`$OSTYPE` で Linux に限定してあるので Mac 側の
   PATH 順序には影響しない — macOS にも `~/.nix-profile` が実在するので `-d` 判定だけでは壊れる。

   この段階ではまだ zsh がログインシェルではない (D-11 で切り替える) ので、
   `zsh -lc 'command -v task starship sheldon mise node'` で確認する。

   **2 回目以降の switch は `nh home switch`。** `nix run` は home-manager 未インストール時の
   ブートストラップ用。`programs.nh` は `flake = ~/dotfiles/nix` を共通で指しているが、
   サブコマンドが Mac (`nh darwin switch`) と違うので注意。

### Phase D: 手動作業

9. Claude Code を入れる。**npm 版を選ぶこと。**

   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

   `task upgrade-claude` / `patch-claude` は `cli.js` へのテキストパッチを前提にしており、
   native installer 版はコンパイル済みバイナリになってパッチが当たらなくなる
   (memory: `project_dotfiles_tooling_gotchas`)。

10. `~/.claude/settings.json` を生成する。**素の cp では hook が 2 系統壊れる** (B-4)。
    node パスの書き換えと rtk hook group の除去を同時にやる。`rtk` は独立した matcher group
    なので `sed` では安全に落とせない。この変換は Mac 上で出力を検証済み
    (`/opt/homebrew` 0 件、`rtk ` 0 件、node hook 4 件を書き換え)。

    ```bash
    python3 - <<'PY'
    import json, pathlib
    src = pathlib.Path.home() / "dotfiles/.config/claude/settings.json"
    dst = pathlib.Path.home() / ".claude/settings.json"
    d = json.loads(src.read_text())
    for ev, groups in d.get("hooks", {}).items():
        # rtk は k1LoW/tap 専用で Linux ビルドが無い → hook group ごと落とす
        groups[:] = [g for g in groups
                     if not any("rtk " in h.get("command", "") for h in g.get("hooks", []))]
        for g in groups:
            for h in g.get("hooks", []):
                if "command" in h:
                    h["command"] = h["command"].replace(
                        "/opt/homebrew/bin/node", "$HOME/.nix-profile/bin/node")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("wrote", dst)
    PY
    ```

    Mac 側の `settings.json` を更新したらこれを再実行する。tracked な WSL 版を作らないのは、
    このファイルが既に nix 非管理で live drift の実績があるため (variant を増やすと drift 源が 2 倍になる)。
11. ログインシェルを zsh にする。`chsh -s /usr/bin/zsh` — A-4 で apt から入れた実体を指定する。
    nix 側には zsh を入れていないので `/usr/bin/zsh` が正しい実体。パスを明示するのは、
    将来 nix 側に zsh が入ったとき `$(which zsh)` がそちらを拾い、`/etc/shells` 不掲載で `chsh` が拒否するのを防ぐため
12. `gh auth login` で GitHub 認証を通す
13. SSH 鍵を配置する (`~/.ssh/`、パーミッション 600)
14. Nerd Font を **Windows 側に** インストールする。描画は Windows のターミナル側で走るので、WSL 内に入れても効かない
15. `task setup` の各ステップを個別に実行する。丸ごとは通らない (下の Watchouts 参照)

## Minimum Validation

- `nix flake check ~/dotfiles/nix` — ただし `x86_64-linux` は "incompatible systems" として
  スキップされ、`homeConfigurations` は非標準 output なので評価されない。**WSL 側の検証にはならない。**
  Mac から確かめるなら
  `nix eval ~/dotfiles/nix#homeConfigurations."<user>@wsl".config.home.homeDirectory` を直接叩く
- `command -v task starship sheldon mise node git` — bootstrap 層が PATH にいる
- `ls -la ~/.claude/` — symlink が張れており、macOS 専用エントリ (`.hammerspoon` 等) が生えていない
- `claude` を起動して SessionStart hook がエラーを出さない — B-4 の node パス修正が効いているか

## Watchouts

- **nixpkgs の `nodejs` は `npm install -g` の prefix が store を指して落ちる可能性がある。**
  D-9 でこけたら `npm config set prefix ~/.npm-global` して PATH に足すか、
  mise 側の node (`.config/mise/config.toml` で 24.13.0 を宣言済み) を使う
- **`task doctor` は FAIL する。** `scripts/lifecycle/doctor.sh:101` の `check_nix` が
  `/run/current-system/sw/bin/darwin-rebuild` を決め打ちしているため。`check_brew` のほうは
  brew 不在で SKIP になり無害
- **`task patch-claude` は未検証。** Claude Code のインストール形態に依存する処理で、
  native installer 版は `~/.local/share/claude/versions/` のコンパイル済みバイナリになりテキストパッチが効かない
  (memory: `project_dotfiles_tooling_gotchas`)。Linux 側の挙動は確認していない
- **ターミナルエミュレータは WSL の外側で動く。** `.config/wezterm` と `.config/ghostty` を
  WSL の home-manager からリンクしても効かない。Ghostty は Windows ビルドが存在しない。
  WezTerm はネイティブ版があるので、Windows 側の `~/.wezterm.lua` に別ルートで配る必要がある
- **`.config/zsh/core/path.zsh` の macOS 絶対パスは無害。** `/opt/homebrew/bin` も
  Windsurf / Antigravity / WezTerm.app のパスも素の `export PATH` 前置きで、
  `brew shellenv` のような実行を伴わない。存在しないディレクトリが PATH に並ぶだけでログインシェルは落ちない
- **定期実行は launchd 前提のまま。** `scripts/runtime/nightly/launchd-install.sh`、
  `patrol-agent.sh`、`daily-health-check.sh` は WSL では動かない。systemd timer に置き換えるか、
  使わないと決めること。WSL 自体が常時起動しているとは限らないので、「動いているつもりで発火していない」が
  一番起きやすい失敗
- **`nix/home/default.nix` の自前 derivation 4 本** (ghqr, crit, terminal-browser, mirador) と
  herdr overlay が `x86_64-linux` でビルドできるかは未確認。落ちたら該当分だけ
  `lib.optionals pkgs.stdenv.isDarwin` に落とす

---

## Power Automate との併用

### 切り分け: GUI は Windows、CLI は WSL

| 何を | どこで動かす | 備考 |
|---|---|---|
| Power Automate Desktop | Windows 側 | ネイティブ GUI アプリ。WSL 内では動かない。Windows 11 は標準搭載 |
| Power Automate (Cloud) | Windows 側のブラウザ | ブラウザ完結なので Mac からでも作れる |
| Claude Code / エージェントハーネス | WSL 側 | この playbook で立てる環境 |

Nix がネイティブ Windows で動かない問題は、この切り分けなら発生しない。Windows 側には
Power Automate しか置かず、dotfiles は WSL 側に閉じるため。

### ファイルの置き場所 — Phase A-6 の例外

Phase A-6 で「`/mnt/c` に置くな」と書いたのは **repo の置き場所**の話。区別すること。

- **dotfiles 本体は WSL の `~/dotfiles`** — `/mnt/c` では symlink とパーミッションが壊れ、home-manager が機能しない
- **作業対象ファイルは `/mnt/c` 経由で触ってよい** — Windows 側で作ったフロー定義を WSL の Claude Code に読ませる経路がこれ

Windows 側のファイルは改行が CRLF なので、Claude Code に編集させたら差分が汚れていないか一度確認する。

### 環境構築より先に確認すること

**フロー定義がファイルとして取り出せるか。** ここで Claude Code の役割が変わる。

- **Cloud フロー**: ソリューションとして JSON エクスポートできるので、Claude Code に読ませて編集する余地がある
- **Desktop フロー**: 職場アカウントでサインインすると Dataverse 側に保存されるのが既定。ローカルの編集可能ファイルとして素直に取り出せるかは**未確認**

取り出せない場合、Claude Code は「フローを直接書く」のではなく、設計相談・アクション列の下書き・
ドキュメント化に寄る。環境構築の前に 5 分で確かめられるので先に見る。

### Windows 機が必要かの判断

- **Cloud フローだけなら Windows は要らない** — ブラウザ完結なので Mac で足りる
- **Desktop (RPA、顧客 PC の操作自動化) を触るなら Windows 必須** — この playbook が必要になるのはこちら
