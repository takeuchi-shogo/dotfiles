# Phase B1 Brewfile Inventory (2026-04-24T12:49:32Z)

自動生成: `nix/scripts/brewfile-inventory.sh`

## CLI (`brew "<name>"`)

| brew name | nixpkgs attr | nixpkgs name | description | classification |
|---|---|---|---|---|
| `git` | `git` | git-2.53.0 | Distributed version control system | tier2-tooling (gitconfig symlink 要注意) |
| `neovim` | `neovim` | neovim-0.12.1 | Vim text editor fork focused on extensibility and agility | tier1-cli |
| `sheldon` | `sheldon` | sheldon-0.8.5 | Fast and configurable shell plugin manager | bootstrap (最後に移植) |
| `starship` | `starship` | starship-1.24.2 | Minimal, blazing fast, and extremely customizable prompt for | bootstrap (最後に移植) |
| `fzf` | `fzf` | fzf-0.71.0 | Command-line fuzzy finder written in Go | tier1-cli |
| `lua` | `lua` | lua-5.2.4 | Powerful, fast, lightweight, embeddable scripting language | tier1-cli |
| `ripgrep` | `ripgrep` | ripgrep-15.1.0 | Utility that combines the usability of The Silver Searcher w | tier1-cli |
| `bat` | `bat` | bat-0.26.1 | Cat(1) clone with syntax highlighting and Git integration | tier1-cli |
| `eza` | `eza` | eza-0.23.4 | Modern, maintained replacement for ls | tier1-cli |
| `zoxide` | `zoxide` | zoxide-0.9.9 | Fast cd command that learns your habits | tier1-cli |
| `atuin` | `atuin` | atuin-18.15.2 | Replacement for a shell history which records additional com | tier2-tooling |
| `git-delta` | `delta` | delta-0.19.2 | Syntax-highlighting pager for git | tier1-cli |
| `dust` | `dust` | du-dust-1.2.4 | Intuitive version of du in rust | tier1-cli (attr は `dust`、derivation 名が `du-dust`) |
| `yazi` | `yazi` | yazi-26.1.22 | Blazing fast terminal file manager written in Rust, based on | tier1-cli |
| `fd` | `fd` | fd-10.4.2 | Simple, fast and user-friendly alternative to find | tier1-cli |
| `tree-sitter-cli` | `tree-sitter` | tree-sitter-0.26.8 | Parser generator tool and an incremental parsing library | tier1-cli |
| `grep` | `gnugrep` | gnugrep-3.12 | GNU implementation of the Unix grep command | tier1-cli |
| `gh` | `gh` | gh-2.91.0 | GitHub CLI tool | tier1-cli |
| `mise` | `mise` | mise-2026.4.6 | Front-end to your dev env | bootstrap (最後に移植) |
| `uv` | `uv` | uv-0.11.7 | Extremely fast Python package installer and resolver, writte | tier2-tooling |
| `borders` | `_NO_` | N/A | N/A | brew-retain (tap-only) |
| `nb` | `nb` | nb-7.25.3 | Command line note-taking, bookmarking, archiving, and knowle | tier2-tooling |
| `direnv` | `direnv` | direnv-2.37.1 | Shell extension that manages your environment | bootstrap (最後に移植) |
| `k1LoW/tap/mo` | `_NO_` | N/A | N/A | brew-retain (tap-only) |

## Cask (`cask "<name>"`)

| cask name | nixpkgs attr | description | classification |
|---|---|---|---|
| `wezterm` | `wezterm` | GPU-accelerated cross-platform terminal emulator and multipl | tier3-cask (cask 維持 / CLI もあるが GUI app は cask) |
| `ghostty` | `ghostty` | Fast, native, feature-rich terminal emulator pushing modern | tier3-cask (cask 維持 / newer, nixpkgs に入った可能性あり) |
| `aerospace` | N/A | nikitabobko/tap | tier3-cask (brew retain, nix-darwin.homebrew.casks で宣言) |
| `hammerspoon` | N/A | macOS GUI / no nixpkgs | tier3-cask (brew retain, nix-darwin.homebrew.casks で宣言) |
| `karabiner-elements` | N/A | macOS GUI / no nixpkgs | tier3-cask (brew retain, nix-darwin.homebrew.casks で宣言) |
| `sf-symbols` | N/A | Apple font browser / no nixpkgs | tier3-cask (brew retain, nix-darwin.homebrew.casks で宣言) |
| `macskk` | N/A | sandbox 制約 / brew 固定 | tier3-cask (brew retain, nix-darwin.homebrew.casks で宣言) |
| `jordanbaird-ice` | N/A | macOS GUI / no nixpkgs | tier3-cask (brew retain, nix-darwin.homebrew.casks で宣言) |
| `raycast` | N/A | macOS GUI / no nixpkgs | tier3-cask (brew retain, nix-darwin.homebrew.casks で宣言) |

## Taps

- `FelixKratz/formulae` → borders (tap-only)
- `k1LoW/tap` → mo (tap-only)
- `nikitabobko/tap` → aerospace (tap-only cask)

→ nix-darwin.homebrew.taps に宣言: `[ "FelixKratz/formulae" "k1LoW/tap" "nikitabobko/tap" ]`

## Fonts

- `font-hackgen-nerd` / `font-hack-nerd-font` → **Phase B1 対象外** (Phase C 以降、macOS font cache の罠回避)

## Notes on Version Specifics

- `lua`: nixpkgs default `pkgs.lua` は **5.2.4** 系。Neovim が要求する場合 `pkgs.lua5_4` / `pkgs.luajit` 等への切替が必要になる可能性あり (Tier 1 移植時に確認)
- `tree-sitter`: brew の `tree-sitter-cli` は CLI 本体、nixpkgs `pkgs.tree-sitter` も同じ CLI を提供 (derivation 名 `tree-sitter-0.26.8` 確認済み)
- `dust`: nixpkgs の attribute は `dust` だが derivation の内部 name は `du-dust`。flake で記述するのは `pkgs.dust`
- `grep` → `gnugrep`: macOS 標準の BSD grep と区別するため nixpkgs の attribute は `gnugrep`。brew "grep" と同じ挙動

## Summary

- **Tier 1 (日常 CLI, 14 本)**: git, neovim, fzf, lua, ripgrep, bat, eza, zoxide, git-delta→delta, dust, yazi, fd, tree-sitter-cli→tree-sitter, grep→gnugrep, gh — 全て nixpkgs にあり
- **Tier 2 (ツール, 4 本)**: atuin, uv, nb, k1LoW/tap/mo (mo は tap のみ → **brew-retain**、残り 3 本は nix)
- **Bootstrap (4 本)**: sheldon, starship, mise, direnv — 全て nixpkgs にあり、最後に移植
- **brew-retain (CLI 2 本)**: borders, mo — tap-only
- **Cask (9 本)**: 全て `nix-darwin.homebrew.casks` 宣言化、brew install mechanism は維持
- **Font (2 本)**: Phase C 以降
