{
  description = "Project development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # === 言語ランタイム（必要なものをコメント解除） ===
            # nodejs_22
            # python312
            # go
            # rustc
            # cargo

            # === ツール ===
            # nodePackages.pnpm
            # nodePackages.yarn
            # uv
            # poetry
          ];

          shellHook = ''
            echo "🚀 開発環境が読み込まれました"
          '';
        };
      });
}
