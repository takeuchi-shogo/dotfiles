{ config, pkgs, ... }:

let
  # Determinate + sudo + Apple Silicon 組み合わせで一部 pkg の checkPhase が hang する
  # (direnv: test/.envrc loop、他: +HELLO echo で停止)。upstream CI ではテスト済みなので
  # end-user build ではスキップして支障なし。
  noCheck = pkg: pkg.overrideAttrs (_: { doCheck = false; });
in
{
  home.username = "takeuchishougo";
  home.homeDirectory = "/Users/takeuchishougo";

  # HM release 文字列 enum。system.stateVersion (integer) とは別物。
  home.stateVersion = "25.11";

  # Tier 1 CLI (Phase B1 Step 3). Name mapping: delta=git-delta,
  # gnugrep=grep, dust derivation is du-dust, tree-sitter=tree-sitter-cli.
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
  ] ++ map noCheck [
    # Bootstrap (Phase B1 Step 7) — checkPhase 無効化
    git
    sheldon
    starship
    mise
    direnv
  ];

  # Phase 0+A: D6 (mkOutOfStoreSymlink) 実証用 fixture。
  # Phase B2 着手前に削除する (B2 plan で計画済み)。
  home.file.".config/zsh-test-nix" = {
    source = config.lib.file.mkOutOfStoreSymlink
      "${config.home.homeDirectory}/dotfiles/nix/test-fixtures/claude-like";
  };

  programs.home-manager.enable = true;
}
