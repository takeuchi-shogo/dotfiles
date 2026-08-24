# terminal-browser (zenbu-labs) — ターミナル pane 内で動くブラウザ。
# agent-browser 互換 CLI を持ち、AI エージェントからの表示・操作に対応。
# nixpkgs 未収載 + 配布は自前 CDN の prebuilt Electron bundle のみのため自前 derivation。
# 更新手順: `gh api repos/zenbu-labs/terminal-browser/releases --jq '.[0].tag_name'` で最新版を見て、
# `nix-prefetch-url --type sha256 <下の url>` の出力を `nix hash convert --to sri` した値に hash を差し替える。
# CDN (terminal-browser.sh) と GitHub Releases の tarball は同一バイト列 (v0.6.0 で照合済)。
{ lib, stdenvNoCC, fetchurl }:

stdenvNoCC.mkDerivation rec {
  pname = "terminal-browser";
  version = "0.6.0";

  src = fetchurl {
    url = "https://terminal-browser.sh/install/dl/stable/v${version}/terminal-browser-darwin-arm64.tar.gz";
    hash = "sha256-0tGgYLYgjxyMUEoa+CXu0PsFv629iyPx4AZWGcV350k=";
  };

  sourceRoot = "terminal-browser";

  # prebuilt Electron app bundle — strip/patch すると macOS code signature が壊れるため無効化
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  # launcher (bin/terminal-browser) は $0 相対で ROOT を解決するが、home-manager が profile を
  # 作るとき bin/ だけを集約 symlink するため、$0 相対の ROOT が electron/ を持たない
  # user-environment を指して起動に失敗する。ROOT を store path 固定に差し替えて $0 依存を断つ。
  #
  # payload を $out 直下でなく $out/libexec に置くのは buildEnv の衝突回避:
  # 同じ upstream 形式の terminal-code と VERSION / CHANNEL / assets/fonts が同名衝突する。
  # $out/bin に置くのは launcher の symlink だけ (ROOT は絶対パスなので symlink 経由でも解決する)。
  installPhase = ''
    mkdir -p $out/libexec/terminal-browser $out/bin
    cp -R . $out/libexec/terminal-browser

    # --replace-fail: upstream が launcher を書き換えて置換が空振りしたら、
    # 壊れたバイナリを配らずビルドを落とす
    substituteInPlace $out/libexec/terminal-browser/bin/terminal-browser \
      --replace-fail 'ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)"' "ROOT=$out/libexec/terminal-browser"

    ln -s $out/libexec/terminal-browser/bin/terminal-browser $out/bin/terminal-browser
  '';

  meta = with lib; {
    description = "A browser that runs directly inside your terminal, with agent-browser compatible CLI";
    homepage = "https://terminal-browser.com";
    # バンドル内に LICENSE 同梱なし。根拠は source repo (gh api repos/zenbu-labs/terminal-browser/license → SPDX: MIT)
    license = licenses.mit;
    mainProgram = "terminal-browser";
    platforms = [ "aarch64-darwin" ];
  };
}
