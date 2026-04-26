# GitHub Quick Review (microsoft/ghqr) — GitHub 設定の best-practices 監査 CLI。
# nixpkgs 未収載のため自前 derivation。Go 1.26 以上必須 (upstream go.mod 指定)。
{ lib, buildGo126Module, fetchFromGitHub }:

buildGo126Module rec {
  pname = "ghqr";
  version = "0.2.0";

  src = fetchFromGitHub {
    owner = "microsoft";
    repo = "ghqr";
    rev = "v.${version}";
    hash = "sha256-QNonvy0T5IkROyzqzBJmpStjtl03v9A7xhVjDRSbUL8=";
  };

  vendorHash = "sha256-CCg0FXwnhuNBDFlaXybIIeuo5VhHIMlP6CozDehzfNE=";

  subPackages = [ "cmd/ghqr" ];

  ldflags = [
    "-s" "-w"
    "-X github.com/microsoft/ghqr/cmd/ghqr/commands.version=${version}"
  ];

  meta = with lib; {
    description = "GitHub Quick Review — security/best-practices auditor for GitHub orgs and repos";
    homepage = "https://github.com/microsoft/ghqr";
    license = licenses.mit;
    mainProgram = "ghqr";
    platforms = platforms.unix;
  };
}
