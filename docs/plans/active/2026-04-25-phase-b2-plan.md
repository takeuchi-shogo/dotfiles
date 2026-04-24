# Phase B2 — symlink.sh → home-manager

Status: planned
Created: 2026-04-25
Ref: `docs/plans/active/2026-04-24-nix-migration-plan.md` (master)
Strategy-source: Codex CLI 不可のため、Codex サブエージェント (agentId: aa6228d52e8a8ee27) がコード実体分析 + master plan 整合性確認で推論
Preceded-by: Phase B1.5 (2026-04-25 completed)

## Background

`.bin/symlink.sh` (498 lines, 8 processing blocks) を `home-manager` + `mkOutOfStoreSymlink` に移行。D6 decision で Phase 0+A に mkOutOfStoreSymlink を `.config/zsh-test-nix/` で実証済み。

## Inventory Discovery (2026-04-25 調査)

| 項目 | 実測値 |
|---|---|
| symlink.sh 行数 | 498 |
| dotfiles 内 total files (find 対象) | 14,587 |
| 現 exclude regex パターン数 | 37 (master plan の "26" より増加) |
| 意図された symlinks (~/ top-level + ~/.config/) | ~40-50 |
| **意図しない symlinks** (exclude 漏れ) | `~/codex-best-practice/*`, `~/everything-cc/*`, `~/sample-cc-best-practice/*` = 80+ items |

**Phase B2 は雑多な現状の正規化機会**。意図しない symlink は whitelist 方式で除去可能。

## Processing Block Analysis

| # | Block | Items | Translation |
|---|---|---|---|
| 1 | `DIRECTORY_SYMLINKS` | `.hammerspoon`, `.config/zsh` | `mkOutOfStoreSymlink` (D6 実証済み) |
| 2 | Claude (`.config/claude` → `~/.claude`) | 4 files + 5 dirs | `mkOutOfStoreSymlink` list |
| 3 | Codex (`.codex` → `~/.codex`) | 2 files | `mkOutOfStoreSymlink` list |
| 4 | Gemini (`.gemini` → `~/.gemini`) | 1 file | `mkOutOfStoreSymlink` list |
| 5 | Cursor (`.cursor` → `~/.cursor`) | 1 file + 5 dirs | `mkOutOfStoreSymlink` list |
| 6 | Dynamic skill-sharing | `SKILL.md` `platforms:` frontmatter ベース | **`home.activation` script** で Python helper を呼ぶ |
| 7 | `find` 全走査 + 37 exclude regex | exclude 外の全 file/symlink | **whitelist 方式** で静的列挙 |

## Strategy Decision (from Codex)

**3 階層分離モデル** を採用:

1. **Static blocks (1-5)**: Nix 化 (low risk)
2. **Dynamic block (6)**: `home.activation` script (medium risk、Python helper 保護)
3. **Auto-discovered (7)**: whitelist pre-enumeration (high risk、`~/` 破壊 risk 最大)

理由: Python helper は dev loop (edit → darwin-rebuild で即反映) を保護すべく activation に寄せ、regex ロジックは Nix 表現性が低いため whitelist に変換する。

## Subphase Decomposition

### B2.0 — Prep (着手前必須、master plan 要求)

- [ ] 37 exclude regex → whitelist 翻訳表 (markdown)
- [ ] `.bin/list-dotfiles-symlinks.sh` prototype (既存 symlink.sh との差分テスト harness)
- [ ] Backup: `tar czf ~/backup-symlinks-pre-b2.tar.gz ~/{.claude,.codex,.gemini,.cursor,.hammerspoon,.config/zsh}`
- [ ] Phase 0+A test fixture (`~/.config/zsh-test-nix`) 削除
- **DoD**: whitelist が `symlink.sh` の実行結果と 1:1 で一致（セマンティック同等、`~/codex-best-practice/*` 等の unintended symlinks は除く）

### B2.1 — Static Declarative Symlinks (low risk)

- [ ] `nix/home/default.nix` に block 1-5 (Claude/Codex/Gemini/Cursor/`.hammerspoon`/`.config/zsh`) の `mkOutOfStoreSymlink` 宣言を追加
- [ ] `task nix:switch` 実行、B2.0 backup 比較で差分ゼロを確認
- **DoD**: `claude-code` 起動 OK、`codex --help` 動作、`~/.config/zsh` が sourcing 可能

### B2.2 — Skill-Sharing Activation Script (medium risk)

- [ ] `home.activation.shareSkills.text` で `scripts/lib/skill_platforms.py` を実行
- [ ] Error handling: Python エラー時も non-fatal (logger 出力のみ)
- **DoD**: `ls ~/.codex/skills/ | wc -l > 0`、各 symlink が live (not copy)

### B2.3 — Auto-Discovered Dotfile Symlinks (high risk)

- [ ] B2.0 で生成した whitelist (~/ top-level + ~/.config/) を `nix/symlink-list.nix` に変換
- [ ] home-manager で `home.file.<path>.source = mkOutOfStoreSymlink` として展開
- [ ] **Scope narrowing**: `codex-best-practice/`, `everything-cc/`, `sample-cc-best-practice/` は whitelist から除外 (意図しない symlink 除去)
- **DoD**: `ls ~ | grep -c '^\.'` が B2.0 backup と同数 ±5 (意図した除去分を許容)

### B2.4 — Test & Cleanup

- [ ] 全 block 比較テスト (B2.0 の test harness で全 symlink 存在確認)
- [ ] `.bin/symlink.sh` 削除 (`git rm`)
- [ ] README.md から symlink.sh 記述削除
- **DoD**: `symlink.sh` 不要、全 symlink live、24h 安定稼働

## Risks & Mitigations

| リスク | 影響度 | 対策 |
|---|---|---|
| home-manager activation で既存 symlink 上書き | 致命 | B2.1 前に backup (`tar czf ~/backup-symlinks-pre-b2.tar.gz`) |
| whitelist 生成で必須ファイル誤除外 | 中 | `list-dotfiles-symlinks.sh` は 37 regex をそのまま翻訳、差分テスト必須 |
| skill-sharing の Python エラー | 中 | try-catch + logger、non-fatal、Codex skills 不足は許容 |
| Phase 0+A `~/.config/zsh-test-nix` 残存 | 小 | B2.1 最初に削除 |
| **`~/` 破壊** (whitelist 誤りで重要 symlink 消失) | 致命 | B2.3 は backup 検証後のみ実行、tar restore の rehearsal を B2.0 で行う |

## Rollback Criteria

以下のいずれかで即 abort:

1. `darwin-rebuild switch` で `home-manager: activate profile` error
2. `claude-code` 起動失敗 (exit != 0)
3. `ls ~/.codex/skills | wc -l == 0` (skill-sharing 失敗)
4. 1 subphase あたり調査/修正が **4 時間超**

### Rollback 手順

```bash
# 1. symlink 復元
tar xzf ~/backup-symlinks-pre-b2.tar.gz -C ~

# 2. nix flake revert
git revert <B2.1/2/3 commit>

# 3. nix 前世代に戻す
darwin-rebuild switch --flake ./nix#private

# 4. (必要なら) .bin/symlink.sh を手動で再実行
~/dotfiles/.bin/symlink.sh
```

## Success Criteria

- [ ] B2.0: whitelist 翻訳表 + test harness + backup 完成
- [ ] B2.1: static blocks (1-5) 全て home-manager 管理下
- [ ] B2.2: skill-sharing が activation script で動作
- [ ] B2.3: auto-discovered symlinks が whitelist 方式で管理、unintended symlinks 除去
- [ ] B2.4: `symlink.sh` 削除、全 DoD verified
- [ ] Brewfile と `.bin/symlink.sh` の両方が flake に吸収され、`darwin-rebuild switch --flake ./nix#private` 一発でマシン再現可能 (master plan の success criteria)

## References

- Master plan: `docs/plans/active/2026-04-24-nix-migration-plan.md`
- Phase 0+A (D6 実証): `docs/plans/active/2026-04-24-nix-migration-phase-0a-plan.md`
- Phase B1 完了: `docs/plans/completed/` (B1 本体は active に残存)
- Phase B1.5 完了: `docs/plans/completed/2026-04-25-phase-b1.5-plan.md`
- symlink.sh 実体: `.bin/symlink.sh` (498 lines)
- Python helper: `scripts/lib/skill_platforms.py` (129 lines)
- Codex strategy (subagent id): aa6228d52e8a8ee27
