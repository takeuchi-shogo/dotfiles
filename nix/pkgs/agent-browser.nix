# agent-browser (vercel-labs) — AI エージェント向けのブラウザ自動操作 CLI。
# nixpkgs 収載版は flake.lock 時点で 0.25.4 と古く、flake update で上げると全パッケージが動くため
# GitHub Releases の prebuilt バイナリ (単体の native binary、依存は macOS システムライブラリのみ) で自前 derivation。
# 更新手順: `gh api repos/vercel-labs/agent-browser/releases --jq '.[0].tag_name'` で最新版を見て、
# `nix-prefetch-url --type sha256 <下の url>` の出力を `nix hash convert --to sri` した値に hash を差し替える。
{ lib, stdenvNoCC, fetchurl }:

stdenvNoCC.mkDerivation rec {
  pname = "agent-browser";
  version = "0.38.1";

  src = fetchurl {
    url = "https://github.com/vercel-labs/agent-browser/releases/download/v${version}/agent-browser-darwin-arm64";
    hash = "sha256-LmEoclkFPqlk0553ACxqNK8OWJ5VzP8l5lnvrn6JLg0=";
  };

  dontUnpack = true;
  # prebuilt binary — strip すると macOS code signature が壊れるため fixup を無効化
  dontFixup = true;

  installPhase = ''
    install -Dm755 $src $out/bin/agent-browser
  '';

  meta = with lib; {
    description = "Browser automation CLI for AI agents";
    homepage = "https://github.com/vercel-labs/agent-browser";
    license = licenses.asl20;
    mainProgram = "agent-browser";
    platforms = [ "aarch64-darwin" ];
  };
}
