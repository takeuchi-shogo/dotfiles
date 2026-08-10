{ config, pkgs, lib, userName, ... }:

let
  dotfiles = "${config.home.homeDirectory}/dotfiles";
  outLink = path: { source = config.lib.file.mkOutOfStoreSymlink "${dotfiles}/${path}"; };

  # nixpkgs 未収載の自前パッケージ。Go 1.26 必須 (buildGo126Module)。
  ghqr = pkgs.callPackage ../pkgs/ghqr.nix {};
  crit = pkgs.callPackage ../pkgs/crit.nix {};
  terminal-browser = pkgs.callPackage ../pkgs/terminal-browser.nix {};
  mirador = pkgs.callPackage ../pkgs/mirador.nix {};
in
{
  home.username = userName;
  # darwin は nix-darwin module 経由、linux (WSL) は standalone homeConfigurations 経由で入る。
  home.homeDirectory =
    if pkgs.stdenv.isDarwin then "/Users/${userName}" else "/home/${userName}";

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
    lazyjj              # TUI for jj (lazygit-like)
    lefthook            # git hooks (pre-commit/commit-msg) — task lefthook:install needs it in PATH
    lua5_4              # pkgs.lua is 5.2.4; sketchybar/colors.lua uses 5.3+ bitwise ops
    neovim
    # Tier 2 tooling (Phase B1 Step 4)
    atuin
    # uv は mise (.config/mise/config.toml) に移管。言語ランタイム系は二重管理を
    # 避けるため Nix home.packages に入れない (Intel brew /usr/local/bin/uv 事故の解消)。
    nb
    ripgrep
    superfile           # TUI ファイルマネージャ (yorukot/superfile, コマンドは spf)
    tree-sitter
    yazi
    zoxide
    # 自前 derivation: GitHub 設定の best-practices 監査 CLI (microsoft/ghqr)
    ghqr
    # 自前 derivation: AI エージェント出力のレビュー CLI (tomasz-tomczyk/crit)
    crit
    # 自前 derivation: ターミナル内ブラウザ + agent-browser 互換 CLI (zenbu-labs)
    terminal-browser
    # 自前 derivation: ターミナルダッシュボード (jchultarsky/mirador)
    mirador
    # flake overlay: AI エージェント multiplexer (github:ogulcancelik/herdr)
    herdr
  ] ++ lib.optionals (!stdenv.isDarwin) [
    # Linux (WSL) 限定。Mac ではこの層を Homebrew が供給している (nix/darwin/default.nix の brews)
    # が、WSL に Homebrew は無いので nixpkgs から入れる。Mac 側は B1.5 の判断どおり brew に残す。
    # go-task が欠けると `task` が使えず、この repo のワークフロー全体が止まる。
    git
    sheldon
    starship
    mise
    direnv
    go-task
    # node は repo のどこにも宣言が無い (Mac の実体は /opt/homebrew/bin/node)。settings.json の
    # hook が node を直接叩くので、ここを埋めないと WSL では hook が黙って落ちる。
    nodejs
    # task build-hooks (cargo build --release) 用。これも Mac では未宣言依存。
    cargo
    rustc
    # zsh は入れない。Ubuntu の chsh が /etc/shells 掲載のシェルしか受け付けないため apt 版を使う。
  ];

  # Phase B2.1: symlink.sh の block 1-5 を home-manager に移植 (D6 実証済み)。
  # mkOutOfStoreSymlink は dotfiles の中身を store にコピーせず、2-hop chain
  # (~/path → store/home-manager-files/X → dotfiles/X) を作る。dev loop の
  # live edit (dotfiles 編集 → ~ 即反映) は経験的に検証済み。
  # Phase 0+A fixture (.config/zsh-test-nix) は本リリースで削除。
  home.file = {
    # block 1: directory-level symlinks
    # (.hammerspoon は macOS 専用。末尾の optionalAttrs isDarwin ブロックへ)
    ".config/zsh"  = outLink ".config/zsh";

    # block 2: Claude (.config/claude → ~/.claude)
    # NOTE: settings.json は意図的に非管理。live (~/.claude/settings.json) は
    # Superset/Orca が hook を runtime 注入する実体ファイルで、symlink 化すると
    # 注入や /model 変更が消える (memory: project_claude_settings_live_drift)。
    # 新PC bootstrap は dotfiles/.config/claude/settings.json を手動 cp する。
    # terminal-browser 同梱の agent skill (installer が ~/.agents/skills に置くのと同じ配線を nix で再現)
    # v0.4.9 で同梱レイアウトが skill/ → skills/<agent-variant>/<skill-name>/ に変わった。
    # variant は tarball の skills/manifest 参照 (claude/cursor/gemini = default, codex = codex)。
    ".agents/skills/terminal-browser" = { source = "${terminal-browser}/skills/default/terminal-browser"; };

    ".claude/CLAUDE.md"            = outLink ".config/claude/CLAUDE.md";
    ".claude/settings.local.json"  = outLink ".config/claude/settings.local.json";
    ".claude/statusline.sh"        = outLink ".config/claude/statusline.sh";
    ".claude/agents"               = outLink ".config/claude/agents";
    ".claude/commands"             = outLink ".config/claude/commands";
    ".claude/scripts"              = outLink ".config/claude/scripts";
    ".claude/skills"               = outLink ".config/claude/skills";
    ".claude/workflows"            = outLink ".config/claude/workflows";
    ".claude/references"           = outLink ".config/claude/references";
    ".claude/output-styles"        = outLink ".config/claude/output-styles";

    # block 2b: memory-vec indexer source (個別ファイル symlink)。
    # skill-data/memory-vec/ は node_modules/index.db (ローカル生成物, gitignore) が
    # 同居するため dir 単位ではなく個別ファイルを symlink (real dir は維持)。
    # 注意: nix:switch 前に ~/.claude/skill-data/memory-vec/ の実体 .ts/.json/.yaml/lib を
    # 削除すること (home-manager が既存実ファイルと衝突するため)。node_modules/index.db は残す。
    ".claude/skill-data/memory-vec/reindex.ts"             = outLink ".config/claude/skill-data/memory-vec/reindex.ts";
    ".claude/skill-data/memory-vec/query.ts"               = outLink ".config/claude/skill-data/memory-vec/query.ts";
    ".claude/skill-data/memory-vec/package.json"           = outLink ".config/claude/skill-data/memory-vec/package.json";
    ".claude/skill-data/memory-vec/pnpm-lock.yaml"         = outLink ".config/claude/skill-data/memory-vec/pnpm-lock.yaml";
    ".claude/skill-data/memory-vec/lib/memory_redactor.py" = outLink ".config/claude/skill-data/memory-vec/lib/memory_redactor.py";

    # block 3: Codex (.codex → ~/.codex)
    # NOTE: .codex/config.toml は Codex.app/cmux が起動時に自己書き換え (notify / node_repl
    # MCP / plugins / marketplaces / hooks trust hash を注入) するため home.file 管理外。
    # symlink 管理すると実ファイル化で nix:switch が clobber する (cmux と同じ
    # self-rewriting app パターン)。初期設定はアプリが生成する。
    ".codex/AGENTS.md"   = outLink ".codex/AGENTS.md";

    # block 4: Gemini
    ".gemini/GEMINI.md" = outLink ".gemini/GEMINI.md";

    # block 5: Cursor
    # NOTE: .cursor/hooks.json は cmux が起動時に自己書き換え (afterAgentResponse /
    # beforeShellExecution 等のフックを注入) するため home.file 管理外
    # (.codex/config.toml と同じ self-rewriting app パターン)。
    # NOTE: ~/.cursor/cli-config.json も auth/model を含む self-rewriting。
    # deny のみ .cursor/cli-permissions.json → mergeCursorCliDeny activation で反映。
    ".cursor/rules"      = outLink ".cursor/rules";
    ".cursor/skills"     = outLink ".cursor/skills";
    ".cursor/agents"     = outLink ".cursor/agents";
    ".cursor/commands"   = outLink ".cursor/commands";
    ".cursor/hooks"      = outLink ".cursor/hooks";

    # block 6: herdr (.config/herdr → ~/.config/herdr)
    # NOTE: ~/.config/herdr にはランタイムファイル (*.sock, *.log, session.json) が
    # 同居するため dir 単位ではなく config.toml 単体を symlink (memory-vec と同パターン)。
    ".config/herdr/config.toml" = outLink ".config/herdr/config.toml";

    # Phase B2.3: auto-discovered (block 7) を whitelist 方式で展開。
    # symlink.sh の find-walk + 37 exclude regex を「明示的に列挙」に置換。
    # B2.0 whitelist 翻訳表 (docs/plans/active/2026-04-25-phase-b2-whitelist.md) に基づく。

    # Top-level dotfiles (5)
    ".crit.config.json" = outLink ".crit.config.json";  # crit global config (agent_cmd: Send to agent → Claude Code)
    ".cursorignore"     = outLink ".cursorignore";
    ".tmux.conf"        = outLink ".tmux.conf";
    ".worktreeinclude"  = outLink ".worktreeinclude";
    ".zshrc"            = outLink ".zshrc";
    # NOTE: ~/.gitignore は dotfiles 外 (system 由来 real file)、ここでは管理しない

    # Root config files at ~ (4 + Brewfile は macOS 専用ブロック)
    "AGENTS.md"     = outLink "AGENTS.md";
    "lefthook.yml"  = outLink "lefthook.yml";
    "llms.txt"      = outLink "llms.txt";
    "ruff.toml"     = outLink "ruff.toml";

    # .config/<tool> dir-level symlinks (9 + aerospace/borders/karabiner/sketchybar は macOS 専用ブロック)
    ".config/cmux"        = outLink ".config/cmux";
    ".config/gh"          = outLink ".config/gh";
    ".config/ghostty"     = outLink ".config/ghostty";
    ".config/git"         = outLink ".config/git";
    ".config/jj"          = outLink ".config/jj";
    ".config/lazygit"     = outLink ".config/lazygit";
    ".config/nvim"        = outLink ".config/nvim";
    ".config/sheldon"     = outLink ".config/sheldon";
    ".config/wezterm"     = outLink ".config/wezterm";
    ".config/zed"         = outLink ".config/zed";

    # .config single-file (3)
    ".config/starship.toml"    = outLink ".config/starship.toml";
    ".config/rtk/config.toml"  = outLink ".config/rtk/config.toml";
    ".config/mise/config.toml" = outLink ".config/mise/config.toml";  # mise グローバル設定 (言語ランタイム集約)
  } // lib.optionalAttrs pkgs.stdenv.isDarwin {
    # macOS 専用。WM / キーリマップ / ステータスバー層は Linux に移植先が無いので、
    # WSL では単に配線しない (Windows 側は PowerToys 等で代替する)。
    # Brewfile は Homebrew 自体が Linux に無いため同様。
    ".hammerspoon"        = outLink ".hammerspoon";
    ".config/aerospace"   = outLink ".config/aerospace";
    ".config/borders"     = outLink ".config/borders";
    ".config/karabiner"   = outLink ".config/karabiner";
    ".config/sketchybar"  = outLink ".config/sketchybar";
    "Brewfile"            = outLink "Brewfile";
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

  # Cursor CLI deny: SSOT (.cursor/cli-permissions.json) → live cli-config.json。
  # cli-config.json 全体は home.file に載せない (auth/model がアプリ書き換え)。
  home.activation.mergeCursorCliDeny = lib.hm.dag.entryAfter [ "writeBoundary" ] ''
    PY="${pkgs.python3}/bin/python3"
    HELPER="${dotfiles}/scripts/lib/merge_cursor_cli_deny.py"
    SSOT="${dotfiles}/.cursor/cli-permissions.json"
    LIVE="${config.home.homeDirectory}/.cursor/cli-config.json"

    [ -f "$HELPER" ] || { echo "merge_cursor_cli_deny.py not found, skip" >&2; exit 0; }
    [ -f "$SSOT" ] || { echo "cli-permissions.json not found, skip" >&2; exit 0; }

    $DRY_RUN_CMD "$PY" "$HELPER" --ssot "$SSOT" --live "$LIVE"
  '';

  programs.home-manager.enable = true;

  # nh: Nix helper CLI. `nh darwin switch` で flake auto-detect、nvd diff 同梱。
  # clean は launchd 連携が未検証のため OFF。手動 `nh clean all` を運用。
  programs.nh = {
    enable = true;
    flake = "${dotfiles}/nix";
  };
}
