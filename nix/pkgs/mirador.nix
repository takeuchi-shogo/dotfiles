# mirador (jchultarsky/mirador) — ターミナル常駐のパーソナルダッシュボード
# (世界時計 / カレンダー / 天気 / タスク / メモ / 市況 / CPU・ネットワークグラフ)。
# nixpkgs 未収載のため自前 derivation。
# ソースビルドはしない: crate は rustc 1.95 以上を要求するが pin 中の nixpkgs は 1.94.1
# (nixpkgs 全体を上げないと通らない)。GitHub Release の prebuilt を使えばこの依存が消える。
# 更新手順: `gh release view --repo jchultarsky/mirador` で tag を確認し version と hash を bump する。
{ lib, stdenvNoCC, fetchurl }:

stdenvNoCC.mkDerivation rec {
  pname = "mirador";
  version = "1.5.0";

  src = fetchurl {
    url = "https://github.com/jchultarsky/mirador/releases/download/v${version}/mirador-aarch64-apple-darwin.tar.gz";
    hash = "sha256-aggTj9OrEMlJwlTjcFWRjK3/VxUVxPvy9C2xBNAesw8=";
  };

  sourceRoot = "mirador-aarch64-apple-darwin";

  installPhase = ''
    runHook preInstall
    install -Dm755 mirador $out/bin/mirador
    runHook postInstall
  '';

  meta = with lib; {
    description = "An opinionated personal dashboard for your terminal";
    homepage = "https://github.com/jchultarsky/mirador";
    license = licenses.mit;
    mainProgram = "mirador";
    platforms = [ "aarch64-darwin" ];
  };
}
