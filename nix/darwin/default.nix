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

  # Phase B1 Step 5+6: GUI cask / tap-only formula を宣言的に管理。
  # brew CLI は引き続き install 実行に使用。onActivation.cleanup = "none" で
  # 既存 formula/cask を勝手に uninstall しない (Codex Consider-#4 準拠)。
  homebrew = {
    enable = true;
    onActivation.cleanup = "none";

    taps = [
      "FelixKratz/formulae"   # borders
      "k1LoW/tap"             # mo
      "nikitabobko/tap"       # aerospace
    ];

    brews = [
      "borders"   # FelixKratz/formulae tap
      "mo"        # k1LoW tap
    ];

    casks = [
      "wezterm"
      "ghostty"
      "aerospace"             # nikitabobko/tap
      "hammerspoon"
      "karabiner-elements"
      "sf-symbols"
      "macskk"
      "jordanbaird-ice"
      "raycast"
    ];
  };
}
