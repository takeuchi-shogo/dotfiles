# terminal-code / tode (zenbu-labs) — ターミナル pane 内で動く VS Code 相当のエディタ。
# terminal-browser と同じ prebuilt Electron bundle 方式 (tarball に vendor/terminal-browser 同梱)。
# nixpkgs 未収載のため自前 derivation。
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

  # launcher (bin/tode) は ROOT を $HOME/.local/lib/tode 固定で参照する (installer 前提)。
  # ROOT の既定値を store path に差し替える (TODE_INSTALL_ROOT による上書き余地は残す)。
  # payload を $out/libexec に置くのは buildEnv の衝突回避:
  # terminal-browser と VERSION / CHANNEL / assets/fonts が同名衝突する。
  installPhase = ''
    mkdir -p $out/libexec/tode $out/bin
    cp -R . $out/libexec/tode

    # --replace-fail: upstream が launcher を書き換えて置換が空振りしたら、
    # 壊れたバイナリを配らずビルドを落とす
    substituteInPlace $out/libexec/tode/bin/tode \
      --replace-fail 'ROOT="''${TODE_INSTALL_ROOT:-$HOME/.local/lib/tode}"' "ROOT=\"\''${TODE_INSTALL_ROOT:-$out/libexec/tode}\""

    ln -s $out/libexec/tode/bin/tode $out/bin/tode
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
