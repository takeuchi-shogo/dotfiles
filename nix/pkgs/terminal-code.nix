# terminal-code / tode (zenbu-labs) — ターミナル pane 内で動く VS Code 相当のエディタ。
# terminal-browser と同じ prebuilt Electron bundle 方式で、tarball に terminal-browser の
# pinned build (vendor/terminal-browser) を同梱する。nixpkgs 未収載のため自前 derivation。
# 初回起動時に code-server (~100MB) を ~/.local/share/tode/runtime へ自前で取りに行く。
# store には入らないので、オフライン環境では最初の 1 回だけ失敗する。
# 更新手順: `gh api repos/zenbu-labs/terminal-code/releases --jq '.[0].tag_name'` で最新版を見て、
# `nix-prefetch-url --type sha256 <下の url>` の出力を `nix hash convert --to sri` した値に hash を差し替える。
{ lib, stdenvNoCC, fetchurl }:

stdenvNoCC.mkDerivation rec {
  pname = "terminal-code";
  version = "0.2.0";

  src = fetchurl {
    url = "https://github.com/zenbu-labs/terminal-code/releases/download/v${version}/tode-darwin-arm64.tar.gz";
    hash = "sha256-p9hov1gVpsHshoAYIN0+RqipN+EY5KShbH/pOqbC8b4=";
  };

  sourceRoot = "tode";

  # prebuilt Electron app bundle — strip/patch すると macOS code signature が壊れるため無効化
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  # payload を $out/libexec に置くのは buildEnv の衝突回避:
  # terminal-browser と VERSION / CHANNEL / assets/fonts が同名衝突する。
  installPhase = ''
    root=$out/libexec/tode
    vendored=$root/vendor/terminal-browser

    mkdir -p $root $out/bin
    cp -R . $root

    # このパッケージが依存する upstream の前提を明示的に検査する。
    # 下の launcher 生成は tarball の中身が変わっても黙って成功してしまうため、
    # hash bump だけ通って実行時に壊れる事故をここで止める。
    grep -qF 'TODE_TERMINAL_BROWSER_BIN' $root/dist/runtime/release.js \
      || { echo "release.js が TODE_TERMINAL_BROWSER_BIN override を持たない (回避策の前提が崩れた)"; exit 1; }
    pinned=$(sed -n 's/.*PINNED_VERSION = "\([^"]*\)".*/\1/p' $root/dist/runtime/release.js)
    [ -n "$pinned" ] && [ "$pinned" = "$(cat $vendored/VERSION)" ] \
      || { echo "vendor/terminal-browser が PINNED_VERSION ($pinned) と一致しない"; exit 1; }
    test -x $vendored/electron/terminal-browser.app/Contents/MacOS/terminal-browser \
      || { echo "vendored electron entrypoint が想定の場所にない"; exit 1; }
    test -f $vendored/cli/dist/main.js \
      || { echo "vendored cli entrypoint が想定の場所にない"; exit 1; }

    # 1. dist/runtime/release.js の resolveRuntime() は起動のたびに vendor 側の launcher を
    #    writeFileSync で書き直す (XDG パスを焼き込むため) → read-only な store で EACCES。
    #    同関数の TODE_TERMINAL_BROWSER_BIN override 経路だけが writeLauncher() を通らないので、
    #    launcher をビルド時に同等内容で焼いてから override を指させる。
    #    内容は release.js の writeLauncher(darwin) と等価 (XDG 既定値の解決順も含む)。
    cat > $vendored/bin/terminal-browser <<LAUNCHER
    #!/bin/sh
    ROOT="$vendored"
    export TERMINAL_BROWSER_DIST_ROOT="\$ROOT"
    export ELECTRON_RUN_AS_NODE=1
    export NATIVE_SCROLL_HELPER="\''${NATIVE_SCROLL_HELPER:-\$ROOT/bin/native-scroll-helper}"
    _data="\''${XDG_DATA_HOME:-\$HOME/.local/share}"
    _state="\''${XDG_STATE_HOME:-\$HOME/.local/state}"
    _cache="\''${XDG_CACHE_HOME:-\$HOME/.cache}"
    export XDG_DATA_HOME="\''${TODE_BROWSER_DATA:-\$_data/tode/browser/share}"
    export XDG_STATE_HOME="\''${TODE_BROWSER_STATE:-\$_state/tode/browser/state}"
    export XDG_CACHE_HOME="\''${TODE_BROWSER_CACHE:-\$_cache/tode/browser}"
    # XDG_RUNTIME_DIR はセッションの値を残す (daemon socket は install root の hash で名前空間化済み)
    if [ -n "\''${TODE_BROWSER_RUN:-}" ]; then export XDG_RUNTIME_DIR="\$TODE_BROWSER_RUN"; fi
    export TERMINAL_BROWSER_APPDATA="\''${TODE_BROWSER_APPDATA:-\$_data/tode/browser/chromium}"
    mkdir -p "\$XDG_DATA_HOME" "\$XDG_STATE_HOME" "\$XDG_CACHE_HOME" "\$TERMINAL_BROWSER_APPDATA"
    exec "\$ROOT/electron/terminal-browser.app/Contents/MacOS/terminal-browser" "\$ROOT/cli/dist/main.js" "\$@"
    LAUNCHER
    chmod 755 $vendored/bin/terminal-browser

    # 2. bin/tode は ROOT を $HOME/.local/lib/tode 固定で参照する (installer 前提で $0 相対ですらない)。
    #    store path に差し替えると同時に、上の override を渡す。
    #    TODE_INSTALL_ROOT は捨てる: これを残すと tode 本体だけ custom root に向き、
    #    browser は store 固定のまま、という upstream にない組み合わせができてしまう
    #    (dist/runtime/paths.js も同じ env を読むため unset して JS 側の __dirname 解決に揃える)。
    # --replace-fail: upstream が launcher を書き換えて置換が空振りしたら、
    # 壊れたバイナリを配らずビルドを落とす
    # 置換文字列は 1 行に畳んである。nix の多行文字列はブロック全体の最小インデントを剥がすため、
    # ここに 1 行でも左端始まりの行を置くと剥がし量が 0 になり、上の <<LAUNCHER の終端子が
    # 列 0 でなくなってヒアドキュメントが終わらなくなる (しかもビルドは成功してしまう)。
    substituteInPlace $root/bin/tode \
      --replace-fail 'ROOT="''${TODE_INSTALL_ROOT:-$HOME/.local/lib/tode}"' \
      "unset TODE_INSTALL_ROOT; export TODE_TERMINAL_BROWSER_BIN=\"\''${TODE_TERMINAL_BROWSER_BIN:-$vendored/bin/terminal-browser}\"; ROOT=\"$root\""

    ln -s $root/bin/tode $out/bin/tode

    # 上の launcher 生成が途中で壊れても build は通ってしまうので、成果物側から検査する
    test -x $out/bin/tode || { echo "$out/bin/tode が生成されていない"; exit 1; }
    sh -n $vendored/bin/terminal-browser || { echo "生成した launcher が sh として壊れている"; exit 1; }
    grep -qF 'TODE_TERMINAL_BROWSER_BIN' $root/bin/tode \
      || { echo "bin/tode に override が注入されていない"; exit 1; }
  '';

  meta = with lib; {
    description = "VS Code in the terminal";
    homepage = "https://terminal-code.com";
    # バンドル内に LICENSE 同梱なし。根拠は source repo (gh api repos/zenbu-labs/terminal-code/license → SPDX: MIT)
    license = licenses.mit;
    mainProgram = "tode";
    platforms = [ "aarch64-darwin" ];
  };
}
