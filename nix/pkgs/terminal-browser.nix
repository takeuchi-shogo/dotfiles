# terminal-browser (zenbu-labs) — ターミナル pane 内で動くブラウザ。
# agent-browser 互換 CLI を持ち、AI エージェントからの表示・操作に対応。
# nixpkgs 未収載 + 配布は自前 CDN の prebuilt Electron bundle のみのため自前 derivation。
# hash は upstream installer (https://terminal-browser.sh/install) 内の SHA256 pin と同一。
# 更新手順: installer の VERSION/SHA256 を確認し version と hash を bump する。
{ lib, stdenvNoCC, fetchurl }:

stdenvNoCC.mkDerivation rec {
  pname = "terminal-browser";
  version = "0.3.3";

  src = fetchurl {
    url = "https://terminal-browser.sh/install/dl/stable/v${version}/terminal-browser-darwin-arm64.tar.gz";
    hash = "sha256-gAQjGCeiscquAyL5mEgllp1xbtVTwtfM3HhNPPhH/Qk=";
  };

  sourceRoot = "terminal-browser";

  # prebuilt Electron app bundle — strip/patch すると macOS code signature が壊れるため無効化
  dontPatch = true;
  dontConfigure = true;
  dontBuild = true;
  dontFixup = true;

  # launcher (bin/terminal-browser) は $0 相対で ROOT を解決するため、
  # upstream tarball と同じレイアウトのまま $out 直下に展開する ($out/bin だけの symlink 化は ROOT がズレて不可)
  installPhase = ''
    mkdir -p $out
    cp -R . $out
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
