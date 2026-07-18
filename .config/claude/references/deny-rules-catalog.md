---
status: reference
last_reviewed: 2026-06-18
---

# Deny Rules Catalog (settings.json permissions auditability)

`.config/claude/settings.json` の `permissions` を **カテゴリ別**に読めるようにした台帳。
目的は auditability — 88 件の deny / 71 件の allow の **意図** をカテゴリ単位で追えるようにする
(claude-code-harness の番号付きガードレールレジストリに相当、ただし「生成」はせず読み物に留める)。

> **single source は `settings.json` の `permissions` ブロック。本ファイルは編集しても挙動を変えない**
> (auditability 用)。`## DENY (N)` / `## ALLOW (N)` ヘッダの件数は `task validate-configs`
> (`.bin/validate_configs.sh`) が settings.json と自動照合し、drift すると CI が fail する。
> 手動同期に頼らず、件数が変わったらヘッダ・合計・カテゴリを直すこと。`ask` tier は現状 0 件。

## DENY (88)

| tier (category) | 件数 | 代表パターン | rationale |
|-----------------|------|--------------|-----------|
| 破壊的 Bash | 10 | `rm -rf *`, `rm -r *`, `git push --force *`, `git reset --hard *`, `git clean -f *`, `git checkout -- *`, `chmod 777 *`, `git commit --no-verify *`, `git commit -n *`, `git commit -n` | 不可逆な破壊・履歴改変・lefthook バイパスを防ぐ。`--no-verify`/`-n` 禁止は CLAUDE.md の commit gate と対 |
| ネットワーク・外部実行 Bash | 14 | `curl *`, `wget *`, `sudo *`, `su *`, `ssh *`, `scp *`, `nc/ncat/netcat *`, `osascript *`, `security *`, `pbcopy/pbpaste *`, `open *` | 外部送信・権限昇格・リモート実行・クリップボード/GUI 経由の持ち出しを遮断 (exfiltration boundary) |
| 環境変数・秘密露出 Bash | 16 | `printenv`, `env`, `* .env*`, `* ~/.ssh/*`, `* ~/.aws/*`, `* ~/.gnupg/*`, `* ~/.config/gcloud/*`, `* ~/.git-credentials`, `* ~/.netrc`, `* ~/.npmrc`, `* ~/.vault-token` ほか | Bash 経由での環境変数 dump / 秘密ディレクトリ・認証ファイルの読み出しを遮断 |
| 秘密ファイル Read (glob) | 19 | `Read(.env*)`, `Read(**/*.pem)`, `Read(**/*.p12)`, `Read(**/*credentials*)`, `Read(**/*secret*)`, `Read(**/*.key)`, `Read(**/id_rsa*)`, `Read(**/*password*)`, `Read(**/.htpasswd)`, `Read(**/*.kdbx)`, `Read(**/auth.json)` ほか | Read tool での秘密ファイル混入を内容パターンで遮断 |
| 秘密ディレクトリ Read (~/) | 13 | `Read(~/.ssh/**)`, `Read(~/.gnupg/**)`, `Read(~/.aws/**)`, `Read(~/.config/gcloud/**)`, `Read(~/.password-store/**)`, `Read(~/.config/gh/**)`, `Read(~/.git-credentials)`, `Read(~/.netrc)`, `Read(~/.npmrc)` ほか | ユーザーホームの認証情報ディレクトリを明示パスで遮断 (glob の取りこぼし対策) |
| 秘密ディレクトリ Edit (~/) | 12 | `Edit(~/.ssh/**)`, `Edit(~/.aws/**)`, `Edit(~/.gnupg/**)`, `Edit(~/.config/gcloud/**)`, `Edit(~/.config/gh/**)`, `Edit(~/.git-credentials)`, `Edit(~/.vault-token)` ほか | 認証情報ディレクトリへの書き込み・編集を遮断。Edit ルールは Write 含む全 file-editing tool に適用されるため Write() ルールは不要 (Write() は permission check にマッチせず警告になる) |
| shell rc Edit | 4 | `Edit(~/.zshrc)`, `Edit(~/.bashrc)`, `Edit(~/.zprofile)`, `Edit(~/.bash_profile)` | shell 起動ファイルの改変 (永続的バックドア・PATH 汚染) を遮断。dotfiles 管理外の直接編集も禁止 |

**deny 合計: 10 + 14 + 16 + 19 + 13 + 12 + 4 = 88** (settings.json と一致)

## ALLOW (71) — カテゴリ要約

| category | 件数 | 例 |
|----------|------|----|
| JS/TS ツールチェーン | 7 | `npm run *`, `pnpm *`, `bun *`, `npx prettier/eslint/oxlint/@biomejs/biome *` |
| Go ツールチェーン | 4 | `go build/test/run/mod *` |
| git (read + 安全な write) | 8 | `git status/log/diff/branch/add/commit *`, `git worktree list` |
| バージョン probe | 10 | `node --version`, `go version`, `rustc --version` ほか |
| brew read | 2 | `brew list/info *` |
| AI CLI | 2 | `codex exec *`, `gemini *` |
| linter | 1 | `ruff *` |
| ネットワーク (許可) | 2 | `WebFetch(*)`, `WebSearch` |
| gh PR read | 5 | `gh pr view/checks/diff/list *`, `*gh-unresolved-threads*` |
| security scan | 1 | `npx ecc-agentshield *` |
| 読み取り専用 file inspect | 25 | `ls/cat/head/tail/wc/diff/jq/sort/uniq/cut/stat/tree/...` |
| tool 許可 | 4 | `Read`, `Glob`, `Grep`, `Agent(Explore)` |

**allow 合計: 7+4+8+10+2+2+1+2+5+1+25+4 = 71** (settings.json と一致)

## 監査の観察 (2026-05-30)

- deny は **不可逆操作 + exfiltration boundary + 秘密ファイル/ディレクトリ + shell rc** の 4 系統に集約される。
  秘密系は Read/Edit の 2 ルールで全経路を塞ぐ (Edit ルールが Write 含む全 file-editing tool をカバー。glob + 明示 ~/ パス)。
- allow は **read-only 検査 + 既知の安全なツールチェーン** が中心。書き込み系で許可されるのは git の通常操作のみ。
- `rtk hook claude` は hooks 側で `permissionDecision: "allow"` を返すため、hook のためだけに `Bash(rtk *)` を allow へ追加しない。
- 新規 deny/allow 追加時は本表の該当カテゴリに反映し、合計を settings.json と一致させる。

## 再生成 (drift チェック)

```bash
python3 -c "import json;p=json.load(open('.config/claude/settings.json'))['permissions'];print('deny',len(p['deny']),'ask',len(p.get('ask',[])),'allow',len(p['allow']))"
```
