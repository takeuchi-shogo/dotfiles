---
status: draft
created: 2026-05-20
last_reviewed: 2026-05-20
trigger: "新規 work Mac (会社支給機) 入手時"
---

# Work Mac 実機検証 Spec

## 背景

Phase C1a (2026-04-28) で `nix/darwin/{private,work}.nix` の multi-host 分離が完了。`work.nix` は空 placeholder で、`mkDarwin` の module merge により共通属性 (AppleShowAllExtensions 等) は base から継承される (Codex Plan Gate HIGH-2 で検証済)。

しかし**実機での `darwin-rebuild switch --flake ./nix#work` end-to-end 動作は未実証**。`flake.nix:39` の `userName = "shogo_takeuchi"` と `hostName = "MacBookPro-work"` も実機との対応未確認。

## 目的

新品 work Mac で `darwin-rebuild switch --flake ./nix#work` が一発成功する。失敗時の修復手順を確定する。

## 受入条件 (Acceptance Criteria)

1. `task nix:bootstrap PROFILE=work` が成功し、`darwin-rebuild` が system profile に入る
2. `task nix:switch PROFILE=work` が成功し、AppleShowAllExtensions=true 等の継承属性が `defaults read` で確認できる
3. `task validate-symlinks` が work 環境でも 68/68 pass (B2 で private 検証済の数値)
4. home-manager 管理下の 19+22 paths が `~/...` に展開されている
5. 失敗時のロールバック (`task nix:rollback` で N-1 generation 復帰) が動作する

## 検証手順

### Step 0: 事前確認 (work Mac 到着時)

```sh
# 実機の whoami と hostname を確認
whoami        # → flake.nix:39 の userName と一致するか?
hostname -s   # → MacBookPro-work と一致するか? (一致しなければ flake.nix 更新)
```

**ユーザー名が違う場合**: `flake.nix:39` を `userName = "<実際のユーザー名>"` に変更してから次へ。

### Step 1: Pre-install snapshot

```sh
cd ~/dotfiles  # repo clone 後
task nix:snapshot PHASE=pre
```

### Step 2: Nix インストール

```sh
task nix:explain  # dry-run で curl コマンド確認
curl -fsSL https://install.determinate.systems/nix | sh -s -- install
task nix:snapshot PHASE=post
```

### Step 3: Bootstrap (work プロファイル)

```sh
task nix:bootstrap PROFILE=work
```

`darwin-rebuild` が `/run/current-system/sw/bin/` に入ることを確認。

### Step 4: Switch

```sh
task nix:switch PROFILE=work
```

### Step 5: 検証

```sh
task validate-symlinks    # 期待: 68/68 pass
task validate-configs     # 期待: 全 pass
defaults read -g AppleShowAllExtensions  # 期待: 1
ls -la ~/.codex/skills/   # home-manager 管理下の symlink 確認
```

### Step 6: ロールバック検証 (任意)

```sh
! sudo /run/current-system/sw/bin/darwin-rebuild --list-generations
task nix:rollback         # N-1 に戻る
defaults read -g AppleShowAllExtensions  # この時点の状態
task nix:switch PROFILE=work  # 最新に戻す
```

## 失敗モード (Pre-Mortem)

| 失敗パターン | 検出方法 | 対処 |
|---|---|---|
| `userName` 不一致 | bootstrap で home dir 不在エラー | flake.nix:39 を実機 whoami に修正 |
| `hostName` 不一致 | switch で networking.hostName mismatch warning | flake.nix:39 hostName を更新 or 無視 (warning のみ) |
| Brewfile 依存パッケージ不在 | switch 後ツール起動失敗 | `task brew:install` を手動実行、または Brewfile を C2 で Nix に移行 |
| AppleShowAllExtensions 未継承 | `defaults read` が `0` | base/default.nix の `system.defaults.NSGlobalDomain` 共通宣言を確認 |
| symlink validation 失敗 | `task validate-symlinks` で N/68 | 不足 path を `nix/home/default.nix` の outLink リストに追加 |

## 撤退条件

- Step 3 (bootstrap) が 30 分以上ハング → ログ確認後 Determinate installer の bug report 提出、手動 Nix インストールに fallback
- Step 4 で `darwin-rebuild` が 5 回連続失敗 → C2 計画自体を再検討 (work Mac 専用の minimal config に縮退)

## Out of Scope

- `system.defaults.<domain>` の work 固有設定 (例: 仕事用アプリの設定) — 別 spec で扱う
- `home-manager` の work 固有 packages — work.nix module で個別追加する想定だが、本 spec では基本動作のみ検証

## 関連

- Phase C1a plan: `docs/plans/completed/2026-04-28-nix-migration-phase-c1a-plan.md`
- Master plan: `docs/plans/active/2026-04-24-nix-migration-plan.md`
- 進捗: `RUNNING_BRIEF.md` の Progress Log
