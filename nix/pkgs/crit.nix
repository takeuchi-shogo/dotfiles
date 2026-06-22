# crit (tomasz-tomczyk/crit) — AI エージェント出力 (plan.md / git diff / ローカル Web) に
# インラインコメントを付けてエージェントへ送り返すローカルレビュー CLI。
# nixpkgs 未収載のため自前 derivation。Go 1.26 必須 (upstream go.mod 指定)。
# レシピは upstream flake.nix を踏襲 (subPackages/doCheck/ldflags)。
{ lib, buildGo126Module, fetchFromGitHub }:

buildGo126Module rec {
  pname = "crit";
  version = "0.16.4";

  src = fetchFromGitHub {
    owner = "tomasz-tomczyk";
    repo = "crit";
    rev = "v${version}";
    hash = "sha256-1FYrI+IG829TNHGu7+xgr+15EqCZGFUKrL/WCrZ14I0=";
  };

  vendorHash = "sha256-Y/0K+tVkaYVvyKk0EYzomKc4BwHMMrc9vcDkxpCq/N8=";

  subPackages = [ "cmd/crit" ];

  # Nix sandbox の /build TMPDIR cleanup が debounced review file writer と race する
  # ため upstream は CI 専用ジョブでテスト、Nix ビルドでは doCheck=false。
  doCheck = false;

  ldflags = [
    "-s" "-w"
    "-X main.version=${version}"
  ];

  meta = with lib; {
    description = "Browser-based markdown review tool with inline commenting for AI agent output";
    homepage = "https://github.com/tomasz-tomczyk/crit";
    license = licenses.mit;
    mainProgram = "crit";
    platforms = platforms.unix;
  };
}
