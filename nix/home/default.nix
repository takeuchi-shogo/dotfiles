{ config, pkgs, ... }:

let
  dotfiles = "${config.home.homeDirectory}/dotfiles";
  outLink = path: { source = config.lib.file.mkOutOfStoreSymlink "${dotfiles}/${path}"; };
in
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

  # Phase B2.1: symlink.sh の block 1-5 を home-manager に移植 (D6 実証済み)。
  # mkOutOfStoreSymlink は dotfiles の中身を store にコピーせず、2-hop chain
  # (~/path → store/home-manager-files/X → dotfiles/X) を作る。dev loop の
  # live edit (dotfiles 編集 → ~ 即反映) は経験的に検証済み。
  # Phase 0+A fixture (.config/zsh-test-nix) は本リリースで削除。
  home.file = {
    # block 1: directory-level symlinks
    ".hammerspoon" = outLink ".hammerspoon";
    ".config/zsh"  = outLink ".config/zsh";

    # block 2: Claude (.config/claude → ~/.claude)
    ".claude/CLAUDE.md"            = outLink ".config/claude/CLAUDE.md";
    ".claude/settings.json"        = outLink ".config/claude/settings.json";
    ".claude/settings.local.json"  = outLink ".config/claude/settings.local.json";
    ".claude/statusline.sh"        = outLink ".config/claude/statusline.sh";
    ".claude/agents"               = outLink ".config/claude/agents";
    ".claude/commands"             = outLink ".config/claude/commands";
    ".claude/scripts"              = outLink ".config/claude/scripts";
    ".claude/skills"               = outLink ".config/claude/skills";

    # block 3: Codex (.codex → ~/.codex)
    ".codex/config.toml" = outLink ".codex/config.toml";
    ".codex/AGENTS.md"   = outLink ".codex/AGENTS.md";

    # block 4: Gemini
    ".gemini/GEMINI.md" = outLink ".gemini/GEMINI.md";

    # block 5: Cursor
    ".cursor/hooks.json" = outLink ".cursor/hooks.json";
    ".cursor/rules"      = outLink ".cursor/rules";
    ".cursor/skills"     = outLink ".cursor/skills";
    ".cursor/agents"     = outLink ".cursor/agents";
    ".cursor/commands"   = outLink ".cursor/commands";
    ".cursor/hooks"      = outLink ".cursor/hooks";
  };

  programs.home-manager.enable = true;
}
