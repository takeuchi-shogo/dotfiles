{ pkgs, userName, ... }:

{
  # programs.zsh.enable = true は /etc/zshrc を nix-darwin 管理下に置き、
  # 既存 .config/zsh/ と二重衝突するため Phase B2 まで false 固定。
  programs.zsh.enable = false;
  programs.bash.enable = false;

  # integer (types.ints.between 1 maxStateVersion). maxStateVersion = 6 (2026-04).
  system.stateVersion = 6;

  system.primaryUser = userName;

  # nix-darwin master + home-manager master では、home-manager 側の home.homeDirectory が
  # ここの users.users.<name>.home を source にする。未宣言だと null 扱いで eval 失敗。
  users.users.${userName} = {
    name = userName;
    home = "/Users/${userName}";
  };

  # Determinate Nix が daemon/設定を管理するため、nix-darwin 側の nix management は無効化。
  # nix.settings.* (experimental-features 等) は Determinate 側の config で制御する。
  nix.enable = false;

  nixpkgs.config.allowUnfree = true;

  # Phase C0 (2026-04-27): 復旧 e2e テスト用 1 attribute 宣言。
  # 詳細: docs/plans/active/2026-04-26-nix-migration-phase-c-plan.md
  # この宣言は C0 検証完了後に C1 (NSGlobalDomain 本番) へ統合する想定。
  system.defaults.NSGlobalDomain.AppleShowAllExtensions = true;

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
      # Bootstrap tools (Phase B1.5: brew-retain per docs/plans/active/2026-04-25-phase-b1.5-plan.md)
      # direnv checkPhase hangs under Determinate Nix + sudo + Apple Silicon, and
      # overrideAttrs (doCheck=false) invalidates Hydra cache. Keep these in brew
      # until upstream improves (tracked separately; non-blocking).
      "git"
      "sheldon"
      "starship"
      "mise"
      "direnv"
      # Tap-only formulae
      "borders"   # FelixKratz/formulae tap
      "mo"        # k1LoW tap
      # LLM token-saving CLI proxy. Hook: `rtk hook claude` (see .config/claude/settings.json)
      "rtk"
      # Task runner (Taskfile.yml executor)
      "go-task"
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
