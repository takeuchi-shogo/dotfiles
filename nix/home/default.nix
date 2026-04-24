{ config, pkgs, ... }:

{
  home.username = "takeuchishougo";
  home.homeDirectory = "/Users/takeuchishougo";

  # HM release 文字列 enum。system.stateVersion (integer) とは別物。
  home.stateVersion = "25.11";

  # Tier 1 CLI (Phase B1 Step 3). Name mapping: delta=git-delta,
  # gnugrep=grep, dust derivation is du-dust, tree-sitter=tree-sitter-cli.
  # Bootstrap (git, sheldon, starship, mise, direnv) は Phase B1.5 に先送り:
  # overrideAttrs で cache が無効化される + 一部 pkg の checkPhase が Determinate
  # 環境で真にハング (direnv の make test-zsh が sleep 状態で 20 分無反応)。
  home.packages = with pkgs; [
    bat
    delta
    dust
    eza
    fd
    fzf
    gh
    gnugrep
    lua5_4              # pkgs.lua is 5.2.4; sketchybar/colors.lua uses 5.3+ bitwise ops
    neovim
    # Tier 2 tooling (Phase B1 Step 4)
    atuin
    uv
    nb
    ripgrep
    tree-sitter
    yazi
    zoxide
  ];

  # Phase 0+A: D6 (mkOutOfStoreSymlink) 実証用 fixture。
  # Phase B2 着手前に削除する (B2 plan で計画済み)。
  home.file.".config/zsh-test-nix" = {
    source = config.lib.file.mkOutOfStoreSymlink
      "${config.home.homeDirectory}/dotfiles/nix/test-fixtures/claude-like";
  };

  programs.home-manager.enable = true;
}
