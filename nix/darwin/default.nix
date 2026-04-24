{ pkgs, ... }:

{
  # programs.zsh.enable = true は /etc/zshrc を nix-darwin 管理下に置き、
  # 既存 .config/zsh/ と二重衝突するため Phase B2 まで false 固定。
  programs.zsh.enable = false;
  programs.bash.enable = false;

  # integer (types.ints.between 1 maxStateVersion). maxStateVersion = 6 (2026-04).
  system.stateVersion = 6;

  system.primaryUser = "takeuchishougo";

  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  nixpkgs.config.allowUnfree = true;
}
