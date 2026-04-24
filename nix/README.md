# nix/ — Nix 移行層 (Phase 0+A 並走期)

## 位置づけ

このディレクトリは [docs/plans/active/2026-04-24-nix-migration-plan.md](../docs/plans/active/2026-04-24-nix-migration-plan.md) に従って dotfiles を Nix (flake + nix-darwin + home-manager) に段階的に移行するための作業領域。

**Phase 0+A 並走期の運用ルール**: 既存の `Brewfile` / `.bin/symlink.sh` / `.bin/init-install.sh` は**一切変更しない**。Nix 側は疎通確認用 (`hello`) と D6 (`mkOutOfStoreSymlink`) 実証用 fixture のみ。

## 構成

```
nix/
├── flake.nix                        # darwinConfigurations.{private, work} + devShells
├── darwin/default.nix               # system レイヤ (programs.zsh.enable = false 等)
├── home/default.nix                 # home-manager レイヤ (hello + mkOutOfStoreSymlink fixture)
└── test-fixtures/claude-like/       # D6 検証用 (Phase B2 着手前に削除)
    ├── CLAUDE.md
    ├── .hidden
    ├── unmanaged-sibling.md
    └── skills/sample/{SKILL.md, run.sh}
```

## Setup (初回のみ)

1. **Pre-install snapshot** (Phase 0+A Step 2):
   ```sh
   # docs/plans/active/2026-04-24-phase-0a-pre-install-snapshot.txt に保存
   for f in /etc/zshenv /etc/zshrc /etc/bashrc /etc/zprofile /etc/zsh/zshrc /etc/zsh/zshenv /etc/synthetic.conf; do
     echo "=== $f ==="; sudo cat "$f" 2>/dev/null || echo "(not present)"
   done
   ls -la /etc/profile.d/ 2>/dev/null
   echo $PATH
   readlink ~/.zshrc ~/.zshenv ~/.zprofile ~/.bashrc 2>/dev/null
   sw_vers -productVersion
   xcode-select -p 2>&1; xcrun --show-sdk-path 2>&1
   diskutil apfs list | grep -i nix || echo "NO_NIX_VOLUME"
   ```
   Xcode CLT 欠如の場合は `xcode-select --install` を先に実行。

2. **Installer dry-run** (Step 3 前半):
   ```sh
   task nix:explain  # 実行するコマンドを表示するだけ
   # 表示された curl コマンドを実行して差分を確認
   ```

3. **Nix インストール** (Step 3 後半):
   ```sh
   curl -fsSL https://install.determinate.systems/nix | sh -s -- install
   ```
   直後に Step 2 と同じコマンドで `docs/plans/active/2026-04-24-phase-0a-post-install-snapshot.txt` を取得。

4. **Apply nix-darwin**:
   ```sh
   task nix:switch PROFILE=private
   ```

## 日常運用

| タスク | コマンド |
|---|---|
| 設定反映 (private) | `task nix:switch PROFILE=private` |
| 設定反映 (work) | `task nix:switch PROFILE=work` |
| 前世代に戻す | `task nix:rollback` |
| flake 静的検証 | `task nix:check` |
| 世代一覧 | `task nix:list-generations` |

## Verification (Phase 0+A Exit 条件)

```sh
# hello 疎通
which hello

# D6 活線編集: repo 側を編集 → switch なしで反映を確認
echo "live-edit test" >> nix/test-fixtures/claude-like/CLAUDE.md
cat ~/.config/zsh-test-nix/CLAUDE.md  # 追記が見える

# exec bit 保持
ls -la ~/.config/zsh-test-nix/skills/sample/run.sh  # -rwxr-xr-x 相当
~/.config/zsh-test-nix/skills/sample/run.sh         # 実行可能

# hidden file 到達性
cat ~/.config/zsh-test-nix/.hidden

# 既存 symlink 非破壊
readlink ~/.zshrc ~/.zshenv ~/.zprofile  # dotfiles を指したまま

# 既存機能回帰なし
task validate
brew bundle check --file=~/dotfiles/Brewfile

# rollback
task nix:rollback
which hello  # 消える
ls ~/.config/zsh-test-nix 2>&1  # 消える
```

## 撤退 (Nix を完全に剥がす)

[Master plan: Abort & Rollback Criteria](../docs/plans/active/2026-04-24-nix-migration-plan.md#abort--rollback-criteria) の「全面撤退」手順に従う。uninstaller だけでは APFS volume / Keychain secret / `/etc/synthetic.conf` / launchd residue が残る場合があるため best-effort + residual check の流れで実施。

## 次 Phase への遷移

Phase 0+A の Exit 条件を全て満たした後、[2026-04-24-nix-migration-phase-0a-plan.md](../docs/plans/active/2026-04-24-nix-migration-phase-0a-plan.md) の Outcome を記入し、Phase B1 plan (Brewfile → flake 移植) を起こす。
