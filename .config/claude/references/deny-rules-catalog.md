---
status: reference
last_reviewed: 2026-10-13
---

# Deny Rules Catalog (settings.json permissions auditability)

`.config/claude/settings.json` の `permissions` を **カテゴリ別**に読めるようにした台帳。
目的は auditability — 88 件の deny / 72 件の allow / 18 件の ask の **意図** をカテゴリ単位で追えるようにする
(claude-code-harness の番号付きガードレールレジストリに相当、ただし「生成」はせず読み物に留める)。

> **single source は `settings.json` の `permissions` ブロック。本ファイルは編集しても挙動を変えない**
> (auditability 用)。`## DENY (N)` / `## ALLOW (N)` / `## ASK (N)` ヘッダの件数は `task validate-configs`
> (`.bin/validate_configs.sh`) が settings.json と自動照合し、drift すると CI が fail する。
> 手動同期に頼らず、件数が変わったらヘッダ・合計・カテゴリを直すこと。

## Premise: agent runs with the user's privileges by default

> 出典（読めた範囲）:
> - [@dkfj 2109473604069195827](https://x.com/dkfj/status/2109473604069195827)
>   「何もしなければ、AIエージェントは自分と同じ権限で動きます」
> - [Speaker Deck: 生成AI時代のクレデンシャルとパーミッション設計](https://speakerdeck.com/nrinetcom/seisei-ai-jidai-no-to-pa-misshon-sekkei)
>   (NRI Netcom / 佐々木拓郎, Developers Summit 2026 KANSAI)
>
> Caveat: スライド転写は Speaker Deck transcript 経由。口頭補足・質疑は未取得。
> 本節は transcript に明示された設計軸だけを採る。

既定ではエージェントは **操作者本人と同じ権限** で動く（読めるファイル・打てるコマンドが同じ）。
任せる範囲を広げるほど事故面も広がるため、台帳と `permission-audit.py` は次の 3 軸で読む:

| 軸 | 問い | この repo での主な制御面 |
|----|------|-------------------------|
| **できること** | 何を許可/禁止するか | `permissions.deny` / `allow` / `ask` + hooks |
| **届く範囲** | どこまで触れられるか | sandbox / worktree / container（設定ファイルの「触るな」だけでは境界にならない） |
| **鍵の渡し方** | 値をどう渡すか（渡さないか） | deny で直読み遮断 + **agent-dedicated credentials** + 代理実行 |

### Least privilege / agent-dedicated credentials（監査観点）

Speaker Deck が明示する鍵の渡し方 4 段階（下ほど安全）:

1. 直読み（`.env` / `~/.aws` 等を AI が読む）
2. 平文の外部注入（環境変数）
3. ストア経由の注入（取り出しは AI の外）
4. 代理実行（値そのものを渡さず、許可した操作だけ実行させる）

本台帳の deny（秘密ファイル/ディレクトリ Read・Edit、環境変数 dump）は主に **段階 1 の遮断**。
audit では加えて次を見る（自動修正はしない）:

- **ユーザー個人の長期鍵を agent と共有していないか**（agent-dedicated / short-lived を推奨）
- **allow が least privilege を超えて広がっていないか**（Bash wildcard・過大 allow）
- **指示書（CLAUDE.md）だけで権限を守ろうとしていないか**（強制力は settings/hooks 側）

機械チェックの実装: `scripts/lifecycle/permission-audit.py`
（`--agent-credentials` で上記観点のシグナルを出す）。

## DENY (88)

| tier (category) | 件数 | 代表パターン | rationale |
|-----------------|------|--------------|-----------|
| 破壊的 Bash | 10 | `rm -rf *`, `rm -r *`, `git push --force *`, `git reset --hard *`, `git clean -f *`, `git checkout -- *`, `chmod 777 *`, `git commit --no-verify *`, `git commit -n *`, `git commit -n` | 破壊・履歴改変・hook 迂回の前置形を deny。末尾 `--no-verify` や env / `-c core.hooksPath` は deny 外。`claude-hooks` pre-bash の argv 検査で補完するが、release 再ビルド前は効かない。永続 `git config core.hooksPath` や別呼び出しの `export` 引き継ぎ、`push`/`merge` の `--no-verify` は未カバー |
| ネットワーク・外部実行 Bash | 14 | `curl *`, `wget *`, `sudo *`, `su *`, `ssh *`, `scp *`, `nc/ncat/netcat *`, `osascript *`, `security *`, `pbcopy/pbpaste *`, `open *` | 外部送信・権限昇格・リモート実行・クリップボード/GUI 経由の持ち出しを遮断 (exfiltration boundary) |
| 環境変数・秘密露出 Bash | 16 | `printenv`, `env`, `* .env*`, `* ~/.ssh/*`, `* ~/.aws/*`, `* ~/.gnupg/*`, `* ~/.config/gcloud/*`, `* ~/.git-credentials`, `* ~/.netrc`, `* ~/.npmrc`, `* ~/.vault-token` ほか | Bash 経由での環境変数 dump / 秘密ディレクトリ・認証ファイルの読み出しを遮断 |
| 秘密ファイル Read (glob) | 19 | `Read(.env*)`, `Read(**/*.pem)`, `Read(**/*.p12)`, `Read(**/*credentials*)`, `Read(**/*secret*)`, `Read(**/*.key)`, `Read(**/id_rsa*)`, `Read(**/*password*)`, `Read(**/.htpasswd)`, `Read(**/*.kdbx)`, `Read(**/auth.json)` ほか | Read tool での秘密ファイル混入を内容パターンで遮断 |
| 秘密ディレクトリ Read (~/) | 13 | `Read(~/.ssh/**)`, `Read(~/.gnupg/**)`, `Read(~/.aws/**)`, `Read(~/.config/gcloud/**)`, `Read(~/.password-store/**)`, `Read(~/.config/gh/**)`, `Read(~/.git-credentials)`, `Read(~/.netrc)`, `Read(~/.npmrc)` ほか | ユーザーホームの認証情報ディレクトリを明示パスで遮断 (glob の取りこぼし対策) |
| 秘密ディレクトリ Edit (~/) | 12 | `Edit(~/.ssh/**)`, `Edit(~/.aws/**)`, `Edit(~/.gnupg/**)`, `Edit(~/.config/gcloud/**)`, `Edit(~/.config/gh/**)`, `Edit(~/.git-credentials)`, `Edit(~/.vault-token)` ほか | 認証情報ディレクトリへの書き込み・編集を遮断。Edit ルールは Write 含む全 file-editing tool に適用されるため Write() ルールは不要 (Write() は permission check にマッチせず警告になる) |
| shell rc Edit | 4 | `Edit(~/.zshrc)`, `Edit(~/.bashrc)`, `Edit(~/.zprofile)`, `Edit(~/.bash_profile)` | shell 起動ファイルの改変 (永続的バックドア・PATH 汚染) を遮断。dotfiles 管理外の直接編集も禁止 |

**deny 合計: 10 + 14 + 16 + 19 + 13 + 12 + 4 = 88** (settings.json と一致)

## ALLOW (72) — カテゴリ要約

| category | 件数 | 例 |
|----------|------|----|
| JS/TS ツールチェーン | 7 | `npm run *`, `pnpm *`, `bun *`, `npx prettier/eslint/oxlint/@biomejs/biome *` |
| ブラウザ自動操作 | 1 | `agent-browser *` (headless の使い捨てプロファイル。実ブラウザ接続は ASK 側で止める) |
| Go ツールチェーン | 4 | `go build/test/run/mod *` |
| git (read + 安全な write) | 8 | `git status/log/diff/branch/add/commit *`, `git worktree list` |
| バージョン probe | 10 | `node --version`, `go version`, `rustc --version` ほか |
| brew read | 2 | `brew list/info *` |
| AI CLI | 2 | `codex exec *`, `agy *` |
| linter | 1 | `ruff *` |
| ネットワーク (許可) | 2 | `WebFetch(*)`, `WebSearch` |
| gh PR read | 5 | `gh pr view/checks/diff/list *`, `*gh-unresolved-threads*` |
| security scan | 1 | `npx ecc-agentshield *` |
| 読み取り専用 file inspect | 25 | `ls/cat/head/tail/wc/diff/jq/sort/uniq/cut/stat/tree/...` |
| tool 許可 | 4 | `Read`, `Glob`, `Grep`, `Agent(Explore)` |

**allow 合計: 7+1+4+8+10+2+2+1+2+5+1+25+4 = 72** (settings.json と一致)

## ASK (18) — カテゴリ要約

ask は deny の後・allow の前に評価される。allow の広いルールから、確認を挟みたい呼び出しだけを切り出す用途。

| category | 件数 | 例 | 理由 |
|----------|------|----|------|
| パッケージ追加・実行 | 8 | `pnpm add/dlx/remove/update *`, `bun add/x/remove/update *` | `pnpm *` / `bun *` の allow から、依存の変更と未知パッケージの実行を切り出す |
| 実ログイン状態の持ち込み | 9 | `agent-browser *--cdp*`, `*--auto-connect*`, `*connect *`, `*--session arc*`, `*--profile*`, `*--state*`, `*--restore*`, `*state load*`, `*auth *` | 実ブラウザへの CDP 接続や保存済み cookie・認証情報の読み込みを伴うと、任意 JS・cookie 読み出し・upload が本物のセッションで動く |

| Arc の再起動 | 1 | `arc-debug*` | Arc をデバッグポート付き / 通常起動に切り替える zsh 関数。中で `osascript` と `open -a Arc` を呼ぶので `Bash(osascript *)` / `Bash(open *)` deny の**意図的な例外**になる (deny はコマンド文字列にしか一致せず、関数本体には届かない)。再起動はユーザーの作業を中断しうるので、auto mode でも毎回確認を挟む |

実ログイン状態の残余リスク: この ask は列挙型なので境界ではなく「確認の摩擦」に留まる。ask を承認して接続した後、
別名 session で `--cdp` を付けずに操作を続ける呼び出しはルールに一致しない。手順 (`webapp-testing` skill) で
Arc 操作を常に `--session arc` に固定してこれを塞いでいる。agent-browser 側の設定ファイルで profile 等を既定化した場合も一致しない。
環境変数 (`AGENT_BROWSER_AUTO_CONNECT=1` 等) を前置した呼び出しは、allow が既知の安全な変数以外の代入を越えて一致しないため確認になる。

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
