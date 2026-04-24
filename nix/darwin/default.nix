{ pkgs, ... }:

{
  # programs.zsh.enable = true は /etc/zshrc を nix-darwin 管理下に置き、
  # 既存 .config/zsh/ と二重衝突するため Phase B2 まで false 固定。
  programs.zsh.enable = false;
  programs.bash.enable = false;

  # integer (types.ints.between 1 maxStateVersion). maxStateVersion = 6 (2026-04).
  system.stateVersion = 6;

  system.primaryUser = "takeuchishougo";

  # nix-darwin master + home-manager master では、home-manager 側の home.homeDirectory が
  # ここの users.users.<name>.home を source にする。未宣言だと null 扱いで eval 失敗。
  users.users.takeuchishougo = {
    name = "takeuchishougo";
    home = "/Users/takeuchishougo";
  };

  # Determinate Nix が daemon/設定を管理するため、nix-darwin 側の nix management は無効化。
  # nix.settings.* (experimental-features 等) は Determinate 側の config で制御する。
  nix.enable = false;

  nixpkgs.config.allowUnfree = true;
}
