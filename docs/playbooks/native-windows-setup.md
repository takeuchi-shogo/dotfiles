# Native Windows Setup (WSL なし)

> SOP template: `.config/claude/agents/document-factory.md` の SOP / Runbook 型に準拠。
> WSL 版は `docs/playbooks/wsl-windows-setup.md`。どちらか一方を選ぶこと。両方立てると
> どちらの設定を直しているか分からなくなる。

## Purpose

WSL を使わず、Windows ネイティブに Claude Code とこの dotfiles の宣言層を展開する手順。
動機は Power Automate Desktop (Windows ネイティブ GUI) と同じ OS で作業すること。

## 先に理解しておくこと

**Claude Code は OS を問わず GUI アプリを操作できない。** ネイティブ Windows にしても
Power Automate Desktop のフローを Claude Code に組ませることはできない。ネイティブを選ぶ利点は
GUI 操作ではなく、パスがネイティブになること、CRLF 変換が挟まらないこと、2 つの OS を
行き来する認知負荷が消えることにある。

## 何が動いて何が動かないか

出典: [Claude Code Advanced setup](https://code.claude.com/docs/en/setup) (2026-08-10 確認)。

| 層 | ネイティブ Windows |
|---|---|
| Claude Code 本体 | **動く。** Windows 10 1809+ / Server 2019+ で公式サポート |
| 宣言テキスト層 (`CLAUDE.md`, `skills/`, `agents/`, `commands/`, `references/`) | **動く。** ただの Markdown |
| bash hook (`.sh` 9 本 + shell ワンライナー 14 個) | **Git for Windows を入れれば動く見込み。** Claude Code は Bash ツールに Git Bash を使う。未入れなら PowerShell ツールになり bash は使えない |
| python hook (37 個) | 要検証。`python3` というコマンド名が Windows で解決するかが鍵 (下の Watchouts) |
| Nix (`nix/` 一式) | **動かない。** Nix はネイティブ Windows に存在しない。パッケージ供給と symlink 配線は手動になる |
| Sandboxing | **非対応。** 公式に native Windows は sandboxing 未サポート (WSL 2 のみ) |
| macOS 専用層 (aerospace / karabiner / hammerspoon / sketchybar / borders) | 動かない。PowerToys 等で代替 |

つまり**失うのは Nix と sandboxing**で、ハーネスの大半は持ち込める。以前 WSL を勧めた
最大の理由は「bash が無い」だったが、これは Git Bash で埋まる。

## Status: 部分的に検証

上の表のうち公式ドキュメント由来の行 (Claude Code 本体 / Git Bash / sandboxing / 設定パス) は
出典つきで確定。**それ以外の「実際にこの repo の hook が動くか」は未検証。** Windows 機が
手元にないため、実機で踏んで差異を追記すること。

## Read First

- `.config/claude/settings.json` — hook 63 個。うち 23 個が shell 依存、37 個が python
- `nix/home/default.nix` の `home.file` — Windows で何をどこに配線するかの一覧として読む
- `docs/playbooks/wsl-windows-setup.md` — WSL 版。B-4 の settings.json 変換は共通で使える

## Standard Steps

すべて **PowerShell** で打つ。管理者権限が要るのは 4 だけ。

1. Git for Windows を入れる。**Bash ツールの前提なので最初に入れる。**

   ```powershell
   winget install --id Git.Git
   ```

2. Python と GitHub CLI を入れる。

   ```powershell
   winget install --id Python.Python.3.13
   winget install --id GitHub.cli
   ```

3. Claude Code を入れる。

   ```powershell
   winget install Anthropic.ClaudeCode
   ```

   `winget` 版は自動更新しない。`winget upgrade Anthropic.ClaudeCode` を定期実行するか、
   自動更新が要るなら native installer (`irm https://claude.ai/install.ps1 | iex`) を選ぶ。

4. **管理者 PowerShell で**開発者モードを有効にする (symlink 作成に必要)。
   設定アプリの「システム > 開発者向け > 開発者モード」でも可。これを飛ばすと 6 の symlink が作れない。

5. dotfiles を clone する。repo は public なので認証不要。

   ```powershell
   git clone https://github.com/takeuchi-shogo/dotfiles.git $env:USERPROFILE\dotfiles
   ```

6. 宣言層を `%USERPROFILE%\.claude\` に配線する。Nix が無いので手動。

   ```powershell
   $src = "$env:USERPROFILE\dotfiles\.config\claude"
   $dst = "$env:USERPROFILE\.claude"
   New-Item -ItemType Directory -Force -Path $dst | Out-Null
   foreach ($n in "agents","commands","skills","references","output-styles","workflows","scripts") {
     New-Item -ItemType SymbolicLink -Force -Path "$dst\$n" -Target "$src\$n"
   }
   New-Item -ItemType SymbolicLink -Force -Path "$dst\CLAUDE.md" -Target "$src\CLAUDE.md"
   ```

   symlink にするのは、Mac 側と同じ「repo が SSOT」を保つため。開発者モードが無効なら
   symlink が作れないので、その場合は `Copy-Item -Recurse` に落とす (ただし drift する)。

7. `settings.json` を配置する。**素の cp では macOS 固有パスが残る。**
   WSL 版 playbook の Phase D-10 の python snippet が使えるが、置換先が違う。
   Windows では node パスを Claude Code 同梱のものに合わせるか、該当 hook を落とす。
   `rtk hook claude` は Windows ビルドが無いので落とす。

   Git Bash が見つからないと言われたら `settings.json` の `env` に足す:

   ```json
   { "env": { "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe" } }
   ```

8. Power Automate Desktop を確認する。Windows 11 は標準搭載。無ければ
   `winget search "Power Automate"` で探す。

9. PowerToys を入れる。諦めた WM / キーリマップ層の代替 (FancyZones / Keyboard Manager)。

   ```powershell
   winget install --id Microsoft.PowerToys
   ```

## Minimum Validation

- `claude --version` がバージョンを表示する
- `claude doctor` — install 健全性と settings ファイルの検証エラーを読み取り専用で出す。**ここが一次診断**
- `claude` を起動して SessionStart hook がエラーを吐かない
- `dir $env:USERPROFILE\.claude` で symlink が張れている

## Watchouts

- **`python3` は Windows で解決しないことがある。** python.org 版は `python.exe` / `py.exe` を置き、
  `python3` が無いか、Windows の App Execution Alias が Microsoft Store を開く挙動になる。
  hook 37 個が `python3` を直に叩いているので、ここが最大の詰まりどころ。`settings.json` 側を
  `py -3` に書き換えるか、`python3.exe` を PATH に用意する
- **Nix が無いので CLI ツールは全部手動。** Mac で `home.packages` が供給している bat / delta / eza /
  fd / fzf / ripgrep / neovim 等は winget か scoop で個別に入れる。`nix/home/default.nix` の
  リストを買い物リストとして使う
- **`task` (go-task) も手動。** `winget install Task.Task` 等。これが無いと repo のワークフローが動かない
- **sandboxing は使えない。** native Windows は公式に非対応。危険なコマンドの実行分離が要るなら WSL 2 を選ぶ
- **Git Bash は MSYS2 の bash。** パス変換 (`/c/Users/...`) と `/tmp` の扱いが Linux と違う。
  `date +%s > /tmp/...` 系のワンライナーは動くかどうか実機で確認する
- **`.claude/settings.json` は nix 非管理のまま。** Mac 側と同じで、live drift の実績がある
  (memory: `project_claude_settings_live_drift`)。Windows でも symlink 化せず実ファイルで置く
- **launchd 依存の定期実行は全滅。** `scripts/runtime/nightly/launchd-install.sh` 等。
  タスク スケジューラに置き換えるか、使わないと決める

## 出典

- [Claude Code Advanced setup](https://code.claude.com/docs/en/setup) — 対応 OS、native Windows の
  install コマンド、Git for Windows と Bash ツールの関係、`CLAUDE_CODE_GIT_BASH_PATH`、
  sandboxing の対応表、`%USERPROFILE%\.claude` の設定パス
