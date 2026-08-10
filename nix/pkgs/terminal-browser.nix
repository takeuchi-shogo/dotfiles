# terminal-browser (zenbu-labs) — ターミナル pane 内で動くブラウザ。
# agent-browser 互換 CLI を持ち、AI エージェントからの表示・操作に対応。
# nixpkgs 未収載 + 配布は自前 CDN の prebuilt Electron bundle のみのため自前 derivation。
# hash は upstream installer (https://terminal-browser.sh/install) 内の SHA256 pin と同一。
# 更新手順: installer の VERSION/SHA256 を確認し version と hash を bump する。
{ lib, stdenvNoCC, fetchurl }:

stdenvNoCC.mkDerivation rec {
  pname = "terminal-browser";
  version = "0.4.9";

  src = fetchurl {
    url = "https://terminal-browser.sh/install/dl/stable/v${version}/terminal-browser-darwin-arm64.tar.gz";
    hash = "sha256-amfynlTwESZcM8Du+pVbpd3LtevSkcPcv2tMWP9KxRE=";
  };

  sourceRoot = "terminal-browser";

  # prebuilt Electron app bundle — strip/patch すると macOS code signature が壊れるため無効化
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  # launcher (bin/terminal-browser) は $0 相対で ROOT を解決するため、
  # upstream tarball と同じレイアウトのまま $out 直下に展開する ($out/bin だけの symlink 化は ROOT がズレて不可)
  #
  # さらに $out 直下に置くだけでは足りない: home-manager が profile を作るとき
  # bin/terminal-browser だけを集約 symlink するため、$0 相対の ROOT が
  # electron/ を持たない user-environment を指して起動に失敗する。
  # ROOT を store path 固定に差し替えて $0 依存を断つ。
  installPhase = ''
    mkdir -p $out
    cp -R . $out

    # --replace-fail: upstream が launcher を書き換えて置換が空振りしたら、
    # 壊れたバイナリを配らずビルドを落とす
    substituteInPlace $out/bin/terminal-browser \
      --replace-fail 'ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)"' "ROOT=$out"
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
