{
  description = "takeuchi-shogo dotfiles: flake + nix-darwin + home-manager";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    nix-darwin.url = "github:nix-darwin/nix-darwin/nix-darwin-25.11";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";

    home-manager.url = "github:nix-community/home-manager/release-25.11";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, nix-darwin, home-manager, ... }:
    let
      mkDarwin = { system, hostName }:
        nix-darwin.lib.darwinSystem {
          inherit system;
          modules = [
            ./darwin
            home-manager.darwinModules.home-manager
            {
              networking.hostName = hostName;
              home-manager.useGlobalPkgs = true;
              home-manager.useUserPackages = true;
              home-manager.users.takeuchishougo = import ./home;
            }
          ];
        };
    in
    {
      darwinConfigurations = {
        private = mkDarwin { system = "aarch64-darwin"; hostName = "MacBookPro"; };
        work    = mkDarwin { system = "aarch64-darwin"; hostName = "MacBookPro-work"; };
      };

      devShells = nixpkgs.lib.genAttrs [ "aarch64-darwin" "x86_64-darwin" ] (system:
        let pkgs = nixpkgs.legacyPackages.${system}; in {
          default = pkgs.mkShell {
            packages = [ pkgs.hello ];
            shellHook = ''echo "nix devShell ready (phase 0+A placeholder)"'';
          };
        });
    };
}
