{ config, pkgs, lib, userName, ... }:

let
  dotfiles = "${config.home.homeDirectory}/dotfiles";
  outLink = path: { source = config.lib.file.mkOutOfStoreSymlink "${dotfiles}/${path}"; };

  # nixpkgs 未収載の自前パッケージ。Go 1.26 必須 (buildGo126Module)。
  ghqr = pkgs.callPackage ../pkgs/ghqr.nix {};
in
{
  home.username = userName;
  home.homeDirectory = "/Users/${userName}";

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
    jujutsu
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
    # 自前 derivation: GitHub 設定の best-practices 監査 CLI (microsoft/ghqr)
    ghqr
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

    # Phase B2.3: auto-discovered (block 7) を whitelist 方式で展開。
    # symlink.sh の find-walk + 37 exclude regex を「明示的に列挙」に置換。
    # B2.0 whitelist 翻訳表 (docs/plans/active/2026-04-25-phase-b2-whitelist.md) に基づく。

    # Top-level dotfiles (5)
    ".cursorignore"     = outLink ".cursorignore";
    ".tmux.conf"        = outLink ".tmux.conf";
    ".worktreeinclude"  = outLink ".worktreeinclude";
    ".zshrc"            = outLink ".zshrc";
    # NOTE: ~/.gitignore は dotfiles 外 (system 由来 real file)、ここでは管理しない

    # Root config files at ~ (5)
    "AGENTS.md"     = outLink "AGENTS.md";
    "Brewfile"      = outLink "Brewfile";
    "lefthook.yml"  = outLink "lefthook.yml";
    "llms.txt"      = outLink "llms.txt";
    "ruff.toml"     = outLink "ruff.toml";

    # .config/<tool> dir-level symlinks (13)
    ".config/aerospace"   = outLink ".config/aerospace";
    ".config/borders"     = outLink ".config/borders";
    ".config/gh"          = outLink ".config/gh";
    ".config/ghostty"     = outLink ".config/ghostty";
    ".config/git"         = outLink ".config/git";
    ".config/jj"          = outLink ".config/jj";
    ".config/karabiner"   = outLink ".config/karabiner";
    ".config/lazygit"     = outLink ".config/lazygit";
    ".config/nvim"        = outLink ".config/nvim";
    ".config/sheldon"     = outLink ".config/sheldon";
    ".config/sketchybar"  = outLink ".config/sketchybar";
    ".config/wezterm"     = outLink ".config/wezterm";
    ".config/zed"         = outLink ".config/zed";

    # .config single-file (2)
    ".config/starship.toml"   = outLink ".config/starship.toml";
    ".config/rtk/config.toml" = outLink ".config/rtk/config.toml";
  };

  # Phase B2.2: skill-sharing を home-manager activation script に移植。
  # symlink.sh の create_codex_symlinks() 内 share_skill_directory() ループ相当。
  # python3 helper は frontmatter の `platforms:` 宣言を解析して symlink 対象を決定。
  # home.file で宣言しないのは skill 数が動的 (現在 4+9=13 件、追加で増減する) かつ
  # 一部既存 ~/.codex/skills/* は gh skill 等の外部経由 = home-manager 管理外を尊重するため。
  # ln -sfn で対象 path のみ上書き、既存の不関連 entry には触れない。
  home.activation.shareSkills = lib.hm.dag.entryAfter [ "writeBoundary" ] ''
    PY="${pkgs.python3}/bin/python3"
    HELPER="${dotfiles}/scripts/lib/skill_platforms.py"
    CLAUDE_SKILLS="${dotfiles}/.config/claude/skills"
    AGENTS_SKILLS="${dotfiles}/.agents/skills"
    CODEX_DIR="${config.home.homeDirectory}/.codex/skills"
    AGENTS_DIR="${config.home.homeDirectory}/.agents/skills"

    [ -f "$HELPER" ] || { echo "skill_platforms.py not found, skip" >&2; exit 0; }

    $DRY_RUN_CMD mkdir -p "$CODEX_DIR" "$AGENTS_DIR"

    share() {
      local target="$1" link="$2"
      [ -d "$target" ] || return 0
      if [ -L "$link" ]; then
        [ "$(readlink "$link")" = "$target" ] && return 0
        $DRY_RUN_CMD ln -sfn "$target" "$link"
      elif [ -e "$link" ]; then
        echo "skill-share: $link exists and is not a symlink, skipping" >&2
        return 0
      else
        $DRY_RUN_CMD ln -s "$target" "$link"
      fi
    }

    # claude skills → codex + agents
    "$PY" "$HELPER" --source claude --needs codex 2>/dev/null | while IFS= read -r skill; do
      [ -z "$skill" ] && continue
      share "$CLAUDE_SKILLS/$skill" "$CODEX_DIR/$skill"
      share "$CLAUDE_SKILLS/$skill" "$AGENTS_DIR/$skill"
    done

    # project (.agents) skills → codex + agents
    "$PY" "$HELPER" --source agents --needs codex 2>/dev/null | while IFS= read -r skill; do
      [ -z "$skill" ] && continue
      share "$AGENTS_SKILLS/$skill" "$CODEX_DIR/$skill"
      share "$AGENTS_SKILLS/$skill" "$AGENTS_DIR/$skill"
    done
  '';

  programs.home-manager.enable = true;
}
