{
  description = "takeuchi-shogo dotfiles: flake + nix-darwin + home-manager";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    # nix-darwin release branches are strictly pinned to matching nixpkgs YY.MM.
    # nixpkgs-unstable (currently 26.05) pairs only with nix-darwin master.
    nix-darwin.url = "github:nix-darwin/nix-darwin/master";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";

    home-manager.url = "github:nix-community/home-manager/master";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";

    # AI エージェント multiplexer。overlay 経由で自分の nixpkgs toolchain でビルドするため
    # follows で herdr 側の pinned nixpkgs を lock に混ぜない。
    herdr.url = "github:ogulcancelik/herdr";
    herdr.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, nix-darwin, home-manager, herdr, ... }:
    let
      mkDarwin = { system, hostName, hostModule, userName }:
        nix-darwin.lib.darwinSystem {
          inherit system;
          modules = [
            ./darwin
            hostModule
            home-manager.darwinModules.home-manager
            {
              networking.hostName = hostName;
              # herdr を pkgs.herdr として供給。useGlobalPkgs=true なので home 側にも波及する。
              nixpkgs.overlays = [ herdr.overlays.default ];
              home-manager.useGlobalPkgs = true;
              home-manager.useUserPackages = true;
              # 既存の実ファイル/ディレクトリと衝突したら *.backup に退避してから link する
              home-manager.backupFileExtension = "backup";
              home-manager.extraSpecialArgs = { inherit userName; };
              home-manager.users.${userName} = import ./home;
              _module.args.userName = userName;
            }
          ];
        };
    in
    {
      darwinConfigurations = {
        private = mkDarwin { system = "aarch64-darwin"; hostName = "MacBookPro";      hostModule = ./darwin/private.nix; userName = "takeuchishougo"; };
        work    = mkDarwin { system = "aarch64-darwin"; hostName = "MacBookPro-work"; hostModule = ./darwin/work.nix;    userName = "shogo_takeuchi"; };
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
