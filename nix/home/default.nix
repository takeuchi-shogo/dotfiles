{ config, pkgs, ... }:

{
  home.username = "takeuchishougo";
  home.homeDirectory = "/Users/takeuchishougo";

  # HM release 文字列 enum。system.stateVersion (integer) とは別物。
  home.stateVersion = "25.11";

  home.packages = [ pkgs.hello ];

  # Phase 0+A: D6 (mkOutOfStoreSymlink) 実証用 fixture。
  # Phase B2 着手前に削除する (B2 plan で計画済み)。
  home.file.".config/zsh-test-nix" = {
    source = config.lib.file.mkOutOfStoreSymlink
      "${config.home.homeDirectory}/dotfiles/nix/test-fixtures/claude-like";
  };

  programs.home-manager.enable = true;
}
