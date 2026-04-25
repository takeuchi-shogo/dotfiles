---
topic: nix-migration
status: active
scope: M (B2.0 deliverable)
parent: docs/plans/paused/2026-04-25-phase-b2-plan.md
created: 2026-04-25
---

# Phase B2.0 — symlink.sh → home-manager whitelist 翻訳表

`.bin/symlink.sh` の 37 exclude regex を whitelist に翻訳する。Phase B2.1-B2.3 で `nix/home/default.nix` への移植時に参照する一次資料。

## 1. 実測 baseline (2026-04-25)

| 指標 | 値 |
|---|---|
| dotfiles 内 total files (find 対象) | **14,588** |
| 37 exclude pattern 適用後の symlink 候補 | **3,146** |
| うち「intended」(blocks 1-6 + 必要な find-pass) | **~573** |
| **「unintended」(B2.3 cleanup target)** | **~2,573 (82%)** |

`.bin/symlink.sh` は 4 種の処理ブロックで symlink を作る:

| Block | 数 | Translation 先 |
|---|---|---|
| 1 DIRECTORY_SYMLINKS | 2 dirs | `mkOutOfStoreSymlink` (B2.1) |
| 2-5 Custom (claude/codex/gemini/cursor) | 4 dirs + ~13 entries | `mkOutOfStoreSymlink` list (B2.1) |
| 6 Skill-sharing (Python helper) | 動的 | `home.activation` script (B2.2) |
| 7 find-walk (37 exclude regex) | ~3,146 | **whitelist 方式** (B2.3) |

## 2. Plan の Inventory Discovery 訂正

`docs/plans/paused/2026-04-25-phase-b2-plan.md` の Inventory Discovery には実測との齟齬がある:

| Plan の主張 | 実測 | 訂正 |
|---|---|---|
| 「意図された symlinks ~40-50」 | block 1-5 だけで ~13 entries、find-pass 経由で更に ~560 | 「意図された symlinks: top-level + custom + .config 以下の 個別 file = ~573」 |
| 「意図しない symlinks 80+ items (`~/codex-best-practice/*`, `~/everything-cc/*`, `~/sample-cc-best-practice/*`)」 | これら 3 dir + 5 dir (`~/tools/`, `~/scripts/`, `~/templates/`, `~/references/`, `~/reports/`) も **`~/` 直下に実ディレクトリとして作られている**。配下に **2,573 file symlinks** | **意図しない: 8 dirs / 2,573 file symlinks** |
| B2.3 DoD の `ls ~ \| grep -c '^\.'` チェック | `~/codex-best-practice/` などは leading dot なしで漏れる | DoD は `find ~ -maxdepth 2 -type l \| wc -l` に変更 |

## 3. Whitelist (intended targets only)

### 3.1 Block 1: DIRECTORY_SYMLINKS (`mkOutOfStoreSymlink`)

```
.hammerspoon       → ~/.hammerspoon
.config/zsh        → ~/.config/zsh
.config/nvim       → ~/.config/nvim    (現状 ~/.config/nvim は dir-level symlink。B2 で明示化)
```

### 3.2 Block 2-5: Custom mappings

`.config/claude/` → `~/.claude/`:

| 種別 | エントリ |
|---|---|
| Files | `CLAUDE.md`, `settings.json`, `settings.local.json`, `statusline.sh` |
| Dirs  | `agents`, `channels`, `commands`, `scripts`, `skills` |

`.codex/` → `~/.codex/`:

| 種別 | エントリ |
|---|---|
| Files | `config.toml`, `AGENTS.md` |

`.gemini/` → `~/.gemini/`:

| 種別 | エントリ |
|---|---|
| Files | `GEMINI.md` |

`.cursor/` → `~/.cursor/`:

| 種別 | エントリ |
|---|---|
| Files | `hooks.json` |
| Dirs  | `rules`, `skills`, `agents`, `commands`, `hooks` |

### 3.3 Block 6: Skill-sharing (動的、`home.activation`)

`scripts/lib/skill_platforms.py` (129 行) を `home.activation` から呼び出し、SKILL.md の `platforms:` frontmatter を解析して以下に展開:

- `~/.codex/skills/<skill>` ← `.config/claude/skills/<skill>` (claude→codex)
- `~/.agents/skills/<skill>` ← `.config/claude/skills/<skill>` (claude→agents)
- `~/.codex/skills/<skill>` ← `.agents/skills/<skill>` (agents→codex)
- `~/.agents/skills/<skill>` ← `.agents/skills/<skill>` (agents→agents)

エラーは non-fatal (logger 出力のみ)。

### 3.4 Block 7: Top-level dotfiles (file symlinks at `~/`)

| Source | Target | 根拠 |
|---|---|---|
| `.cursorignore` | `~/.cursorignore` | Cursor が `~/.cursorignore` を読む |
| `.gitignore` | `~/.gitignore` | git global ignore |
| `.tmux.conf` | `~/.tmux.conf` | tmux 起動時参照 |
| `.worktreeinclude` | `~/.worktreeinclude` | worktree シェル統合 |
| `.zshrc` | `~/.zshrc` | shell entry point |
| `AGENTS.md` | `~/AGENTS.md` | Codex CLI が `~/AGENTS.md` を読む |
| `Brewfile` | `~/Brewfile` | `brew bundle` のデフォルトパス |

**判断保留** (B2.3 着手前に user 確認):

| Source | Target | 懸念 |
|---|---|---|
| `CLAUDE.md` | `~/CLAUDE.md` | 現状 `~/CLAUDE.md` 不在。Claude が global で参照するのは `~/.claude/CLAUDE.md` なので不要かも |
| `CURSOR.md` | `~/CURSOR.md` | 同上、Cursor は `~/.cursor/` 配下を読む |
| `EXAMPLE.md` | (skip) | 用途不明 |
| `lefthook.yml` | (skip) | per-repo にすべき |
| `llms.txt` | (skip) | 用途不明 |
| `ruff.toml` | (skip) | per-repo にすべき |
| `karpathy_llm_kb_extraction.json` | (skip) | 一時的成果物 |

### 3.5 Block 7: `.config/` 配下 (個別 file symlinks)

dotfiles 内に存在する `.config/<tool>/` のうち、以下を `~/.config/<tool>/` 配下に file-level symlink で展開:

| Subdir | 現状 ~/.config/ 内の symlinks | 翻訳方針 |
|---|---|---|
| `aerospace/` | 3 file symlinks | 同等の file-level (B2.3) |
| `borders/` | 1 | 同上 |
| `gh/` | 0 (空) | 翻訳不要 |
| `ghostty/` | 11 | 同上 |
| `git/` | 1 | 同上 |
| `karabiner/` | 2 | 同上 |
| `lazygit/` | 1 | 同上 |
| `nvim/` | dir-level symlink | block 1 に昇格 (3.1 参照) |
| `sheldon/` | 1 | 同上 |
| `sketchybar/` | 34 | 同上 |
| `starship.toml` | 1 (file) | 同上 |
| `wezterm/` | 15 | 同上 |
| `zed/` | 1 | 同上 |

合計 ~71 file symlinks + 1 dir symlink (nvim)

## 4. Cleanup targets (whitelist から **除外** = B2.3 で削除)

以下は dotfiles 内の実ディレクトリだが、`~/` 配下に展開する意図がなかったもの:

| Path (in dotfiles) | 現状 ~/ での pollution | symlink 数 |
|---|---|---|
| `everything-cc/` | `~/everything-cc/` 配下に 1,715 file symlinks | 1,715 |
| `sample-cc-best-practice/` | `~/sample-cc-best-practice/` 配下に 318 | 318 |
| `tools/` | `~/tools/` 配下に 385 | 385 |
| `codex-best-practice/` | `~/codex-best-practice/` 配下に 101 | 101 |
| `scripts/` | `~/scripts/` 配下に 39 | 39 |
| `templates/` | `~/templates/` 配下に 11 | 11 |
| `references/` | `~/references/` 配下に 2 | 2 |
| `reports/` | `~/reports/` 配下に 2 | 2 |
| `.bin/` | `~/.bin/` 配下に 9 | 9 |
| `.github/` | `~/.github/` 配下に 4 | 4 |
| `.dmux/` | `~/.dmux/` 配下に 2 | 2 |
| `skills-lock-history/` | `~/skills-lock-history/` 配下に 1 | 1 |
| **合計** | | **2,589** |

**B2.3 DoD 訂正版**: `find ~ -maxdepth 4 -type l -lname '*dotfiles*' | wc -l` の baseline (B2.0) が 約 3,146 → 約 573 (intended のみ) に減ること。

## 5. Block 7 (find-walk) の現状残存挙動

現在 `~/` 直下に作られている **想定外の実ディレクトリ + 内部 symlink** は、B2.3 で `home.file` 宣言に置き換える際に **明示的に除去対象** とする。具体的には:

1. B2.3 commit 直前に `rm -rf ~/{everything-cc,sample-cc-best-practice,tools,codex-best-practice,scripts,templates,references,reports,.bin,.github,.dmux,skills-lock-history}` (backup 検証後のみ)
2. `home-manager` が whitelist 内のみを `~/` に作る
3. `find ~ -maxdepth 4 -type l -lname '*dotfiles*' | wc -l` で baseline 比較

## 6. B2.0 Prep の DoD

- [x] 実測 baseline 取得 (3,146 / 2,573 unintended)
- [x] 37 exclude pattern → whitelist 翻訳 (本文書)
- [x] Plan Inventory Discovery 齟齬の特定 (§2)
- [ ] `.bin/list-dotfiles-symlinks.sh` で 3,146 件を再現可能 (B2.0-2)
- [ ] `tar tzf ~/backup-symlinks-pre-b2.tar.gz` で 6 dir 全て含む (B2.0-3)
- [ ] Plan 本文の訂正 (B2.0-4)

## 7. Open Questions (B2.1 着手前に解決)

1. §3.4 「判断保留」の 7 ファイルを `~/` に置くか?
2. §3.5 の `.config/<tool>/` を **dir-level symlink** に統一するか **file-level** で残すか?
   - dir-level: 簡潔、git-ignored ファイル混入なし、新規ファイル自動反映
   - file-level: 局所的に real file を混在可能、ただし新規追加時に nix 再ビルド必要
3. `.dmux/` (2 file symlinks) は dotfiles 配下管理続けるか? 別 repo に切り出すか?

## References

- Master plan: `docs/plans/active/2026-04-24-nix-migration-plan.md`
- B2 plan: `docs/plans/paused/2026-04-25-phase-b2-plan.md`
- symlink.sh: `.bin/symlink.sh` (498 行)
- skill-sharing helper: `scripts/lib/skill_platforms.py` (129 行)
- 既存 `.config/zsh-test-nix`: home-manager 管理 (Phase 0+A 残存、B2.1 で削除)
