# cmux カスタマイズ調査メモ (handoff)

- 日付: 2026-05-15
- 目的: 別セッションで cmux の設定カスタマイズを再開できる完全リファレンス
- ソース: cmux 公式日本語ドキュメント全章 (https://cmux.com/ja/docs/) を 2026-05-15 取得
- 取得方法: WebFetch (Haiku 要約経由)。**Haiku 要約由来の不確実箇所は ⚠️ で注記**
- 既存環境: `~/.config/cmux/cmux.json` は template 状態（全コメントアウト）。`scripts/runtime/cmux-notify.sh` 既存。`references/cmux-ecosystem.md` あり
- 方針: **まだ未決定**。Section 11「取りうる方向性」から選ぶフェーズ

---

## 1. cmux のメンタルモデル

### 階層 (公式 concepts)

```
Window (macOS window)
  └── Workspace (サイドバー項目 = タブ風 UI)
        └── Pane (workspace 内の split 領域)
              └── Surface (pane 内のタブ = terminal or browser)
                    └── Panel (内部概念、terminal/browser の 2 種)
```

### 各層の環境変数

- `CMUX_WORKSPACE_ID` — 現在の workspace
- `CMUX_SURFACE_ID` — 現在の surface
- `TERM_PROGRAM=ghostty`, `TERM=xterm-ghostty` — cmux ターミナルで自動設定

### macOS 要件

macOS 14.0 以降、Apple Silicon または Intel Mac。

---

## 2. インストール / 起動 / 更新

### Install

```bash
# 推奨 (DMG)
open https://github.com/manaflow-ai/cmux/releases/latest/download/cmux-macos.dmg

# Homebrew
brew tap manaflow-ai/cmux
brew install --cask cmux
brew upgrade --cask cmux
```

### CLI シンボリックリンク (外部から `cmux` コマンド呼び出し)

```bash
sudo ln -sf "/Applications/cmux.app/Contents/Resources/bin/cmux" /usr/local/bin/cmux
```

### 設定リロード

- `Cmd+Shift+,` (デフォルト `reloadConfiguration`)
- または `cmux reload-config`

### 設定検証 (v0.64.3+)

```bash
cmux config doctor   # ソケット不要で cmux.json を検証
```

---

## 3. 設定ファイル全体像

### ファイル配置と優先順位

| 順位 | ファイル | スコープ | 上書き範囲 |
|---|---|---|---|
| 1 (最高) | `./.cmux/cmux.json` | プロジェクトローカル | actions, commands, UI wiring, notifications **のみ** (グローバル設定は不可) |
| 1' | `./cmux.json` | プロジェクト fallback | 同上 (既存リポ互換) |
| 2 | `~/.config/cmux/cmux.json` | グローバル | 全項目 |
| 3 | Settings UI 保存値 | グローバル | 全項目 |
| 4 (fallback) | `~/.config/cmux/settings.json` | レガシー | 未指定キーのみ |
| 4' (fallback) | `~/Library/Application Support/cmux/` | レガシー | 未指定キーのみ |

### 別ファイル

- **`~/.config/cmux/dock.json`** or `./.cmux/dock.json` — Dock の TUI コントロール定義 (`cmux.json` とは別)
- **Ghostty config** — ターミナル本体の設定は cmux ではなく Ghostty 側:
  - `~/.config/ghostty/config`
  - `~/Library/Application Support/com.mitchellh.ghostty/config`

### フォーマット

- **JSONC**: コメント (`//`, `/* */`) + trailing comma 許容
- Schema URL: `https://raw.githubusercontent.com/manaflow-ai/cmux/main/web/data/cmux.schema.json`
- `schemaVersion`: 現状 `1` 固定。将来は auto-upgrade

---

## 4. cmux.json 全カテゴリ完全リファレンス

トップキーは `$schema`, `schemaVersion` + 以下 9 セクション。

### 4.1 `app`

| キー | 型 | デフォルト | enum / 備考 |
|---|---|---|---|
| `language` | string | `"system"` | system, en, ar, bs, zh-Hans, zh-Hant, da, de, es, fr, it, ja, ko, nb, pl, pt-BR, ru, th, tr |
| `appearance` | string | `"system"` | system, light, dark |
| `appIcon` | string | `"automatic"` | automatic, light, dark |
| `menuBarOnly` | boolean | `false` | Dock アイコン非表示・メニューバー専用 |
| `newWorkspacePlacement` | string | `"afterCurrent"` | top, afterCurrent, end |
| `workspaceInheritWorkingDirectory` | boolean | `true` | 新規 ws が現 cwd を継承 |
| `minimalMode` | boolean | `false` | タイトルバー非表示・コントロールをサイドバーへ |
| `keepWorkspaceOpenWhenClosingLastSurface` | boolean | `false` | |
| `focusPaneOnFirstClick` | boolean | `true` | |
| `preferredEditor` | string | `""` | Cmd+クリックのファイルプレビュー用エディタ |
| `openSupportedFilesInCmux` | boolean | `true` | text/code/PDF/image を cmux で開く |
| `openMarkdownInCmuxViewer` | boolean | `false` | Markdown を cmux 内ビューアで開く |
| `reorderOnNotification` | boolean | `true` | 通知あり workspace を top へ |
| `iMessageMode` | boolean | `false` | エージェント送信メッセージを iMessage 風表示 |
| `sendAnonymousTelemetry` | boolean | `true` | |
| `warnBeforeQuit` | boolean | `true` | |
| `warnBeforeClosingTab` | boolean | `true` | |
| `renameSelectsExistingName` | boolean | `true` | |
| `commandPaletteSearchesAllSurfaces` | boolean | `false` | |

### 4.2 `terminal`

| キー | 型 | デフォルト | 備考 |
|---|---|---|---|
| `showScrollBar` | boolean | `true` | TUI サーフェスでは自動抑制 |
| `autoResumeAgentSessions` | boolean | `true` | Claude Code/Codex/OpenCode の再開 |

### 4.3 `notifications`

| キー | 型 | デフォルト | enum / 備考 |
|---|---|---|---|
| `dockBadge` | boolean | `true` | |
| `showInMenuBar` | boolean | `true` | |
| `unreadPaneRing` | boolean | `true` | |
| `paneFlash` | boolean | `true` | |
| `sound` | string | `"default"` | default, Basso, Blow, Bottle, Frog, Funk, Glass, Hero, Morse, Ping, Pop, Purr, Sosumi, Submarine, Tink, custom_file, none |
| `customSoundFilePath` | string | `""` | `sound: "custom_file"` と併用 |
| `command` | string | `""` | 通知時シェルコマンド (シンプル版) |
| `hooksMode` | string | `"append"` | append / replace |
| `hooks` | array<object> | `[]` | 複合シェルフック (詳細は §5) |

### 4.4 `sidebar`

14 個の boolean フラグ (全て default `true`、`branchLayout` のみ string):

`hideAllDetails`, `showWorkspaceDescription`, `branchLayout` (`"vertical"`/`"inline"`), `showNotificationMessage`, `showBranchDirectory`, `showPullRequests`, `makePullRequestsClickable`, `openPullRequestLinksInCmuxBrowser`, `openPortLinksInCmuxBrowser`, `showSSH`, `showPorts`, `showLog`, `showProgress`, `showCustomMetadata`

### 4.5 `workspaceColors`

| キー | 型 | デフォルト |
|---|---|---|
| `indicatorStyle` | string | `"leftRail"` (他: solidFill, rail, border, wash, lift, typography, washRail, blueWashColorRail) |
| `selectionColor` | string/null | `null` |
| `notificationBadgeColor` | string/null | `null` |
| `colors` | object | 16 色組み込み (Red, Crimson, Orange, Amber, Olive, Green, Teal, Aqua, Blue, Navy, Indigo, Purple, Magenta, Rose, Brown, Charcoal) |
| `paletteOverrides` | object | `{}` (legacy, 新規は `colors` 使用) |
| `customColors` | array | `[]` (legacy) |

### 4.6 `sidebarAppearance`

| キー | 型 | デフォルト |
|---|---|---|
| `matchTerminalBackground` | boolean | `false` |
| `tintColor` | string | `"#000000"` |
| `lightModeTintColor` | string/null | `null` |
| `darkModeTintColor` | string/null | `null` |
| `tintOpacity` | number | `0.03` (0–1) |

### 4.7 `automation` ⭐ 最重要

| キー | 型 | デフォルト | enum / 備考 |
|---|---|---|---|
| `socketControlMode` | string | `"cmuxOnly"` | off, cmuxOnly, automation, password, allowAll, openAccess, fullOpenAccess, notifications, full |
| `socketPassword` | string\|null | `""` | `password` モード時のみ |
| `claudeCodeIntegration` | boolean | `true` | Claude Code hooks 有効化 |
| `claudeBinaryPath` | string | `""` | `claude` バイナリのカスタムパス |
| `cursorIntegration` | boolean | `true` | Cursor hooks |
| `geminiIntegration` | boolean | `true` | Gemini hooks |
| `portBase` | integer | `9100` | workspace `CMUX_PORT` の起点 |
| `portRange` | integer | `10` | workspace ごとに予約するポート数 |

**socketControlMode の意味**:

| 値 | アクセス許容 |
|---|---|
| `off` | ソケット無効 |
| `cmuxOnly` | cmux 内プロセスのみ |
| `automation` | プログラム制御 (API 用途) |
| `password` | パスワード認証必須 |
| `allowAll` / `openAccess` / `fullOpenAccess` | 段階的にローカルプロセス全許可 |
| `notifications` | 通知特化制御 |
| `full` | 最大権限 |

⚠️ Haiku 要約のため `allowAll` と `openAccess` と `fullOpenAccess` の差は曖昧。共有マシンでは `off` か `cmuxOnly` 推奨 (公式注記)。

### 4.8 `browser`

| キー | 型 | デフォルト | enum |
|---|---|---|---|
| `defaultSearchEngine` | string | `"google"` | google, duckduckgo, bing, kagi, startpage |
| `showSearchSuggestions` | boolean | `true` | |
| `theme` | string | `"system"` | system, light, dark |
| `openTerminalLinksInCmuxBrowser` | boolean | `true` | |
| `interceptTerminalOpenCommandInCmuxBrowser` | boolean | `true` | `open https://...` を捕捉 |
| `hostsToOpenInEmbeddedBrowser` | array<string> | `[]` | allowlist |
| `urlsToAlwaysOpenExternally` | array<string> | `[]` | system ブラウザ強制 |
| `insecureHttpHostsAllowedInEmbeddedBrowser` | array<string> | `["localhost","*.localhost","127.0.0.1","::1","0.0.0.0","*.localtest.me"]` | HTTP 許可 |
| `showImportHintOnBlankTabs` | boolean | `true` | |
| `reactGrabVersion` | string | `"0.1.29"` | toolbar helper version |

### 4.9 `shortcuts.bindings`

#### Syntax

- 単一: `"cmd+b"`, `"ctrl+b"`, `"shift+/"`
- Chord (2 段): `["ctrl+b", "c"]`
- Unbind: `null`, `""`, `"none"`, `"clear"`, `"unbound"`, `"disabled"`

#### 全 binding (公式キー名)

**App**: `openSettings`(cmd+,) / `reloadConfiguration`(cmd+shift+,) / `showHideAllWindows`(ctrl+opt+cmd+.) / `globalSearch`(opt+cmd+f) / `commandPalette`(cmd+shift+p) / `commandPaletteNext`(ctrl+n) / `commandPalettePrevious`(ctrl+p) / `newWindow`(cmd+shift+n) / `closeWindow`(ctrl+cmd+w) / `toggleFullScreen`(ctrl+cmd+f) / `sendFeedback`(unbound) / `reopenPreviousSession`(cmd+shift+o) / `quit`(cmd+q)

**Workspace**: `toggleSidebar`(cmd+b) / `toggleFileExplorer`(cmd+opt+b) / `newTab`(cmd+n) / `openFolder`(cmd+o) / `goToWorkspace`(cmd+p) / `nextSidebarTab`(ctrl+cmd+]) / `prevSidebarTab`(ctrl+cmd+[) / `selectWorkspaceByNumber`(cmd+1..9) / `renameWorkspace`(cmd+shift+r) / `editWorkspaceDescription`(opt+cmd+e) / `focusRightSidebar`(cmd+shift+e) / `navigateRightSidebarRows`(j/k) / `closeWorkspace`(cmd+shift+w)

**Surface**: `newSurface`(cmd+t) / `nextSurface`(cmd+shift+]) / `prevSurface`(cmd+shift+[) / `selectSurfaceByNumber`(ctrl+1..9) / `renameTab`(cmd+r) / `closeTab`(cmd+w) / `closeOtherTabsInPane`(opt+cmd+t) / `reopenClosedBrowserPanel`(cmd+shift+t) / `toggleTerminalCopyMode`(cmd+shift+m) / `saveFilePreview`(cmd+s)

**Split**: `focusLeft/Right/Up/Down`(opt+cmd+矢印) / `splitRight`(cmd+d) / `splitDown`(cmd+shift+d) / `splitBrowserRight`(opt+cmd+d) / `splitBrowserDown`(opt+cmd+shift+d) / `toggleSplitZoom`(cmd+shift+enter) / `equalizeSplits`(ctrl+cmd+=)

**Browser**: `openBrowser`(cmd+shift+l) / `focusBrowserAddressBar`(cmd+l) / `browserBack`(cmd+[) / `browserForward`(cmd+]) / `browserReload`(cmd+r) / `browserZoomIn/Out/Reset`(cmd+=/-/0) / `toggleBrowserDeveloperTools`(opt+cmd+i) / `showBrowserJavaScriptConsole`(opt+cmd+c) / `toggleReactGrab`(cmd+shift+g)

**Search**: `find`(cmd+f) / `findInDirectory`(cmd+shift+f) / `findNext`(cmd+g) / `findPrevious`(opt+cmd+g) / `hideFind`(opt+cmd+shift+f) / `useSelectionForFind`(cmd+e)

**Notification**: `showNotifications`(cmd+i) / `jumpToUnread`(cmd+shift+u) / `markOldestUnreadAndJumpNext`(ctrl+cmd+u) / `triggerFlash`(cmd+shift+h)

合計約 60 個。

---

## 5. 通知 hook の完全スキーマ ⭐

### Hook input/output (stdin/stdout、JSON)

```json
{
  "version": 1,
  "notification": {
    "workspaceId": "string",
    "surfaceId": "string",
    "title": "string",
    "subtitle": "string",
    "body": "string"
  },
  "context": {
    "cwd": "string",
    "configPath": "string",
    "hookId": "string",
    "appFocused": "boolean",
    "focusedPanel": "boolean"
  },
  "effects": {
    "record": "boolean",
    "markUnread": "boolean",
    "reorderWorkspace": "boolean",
    "desktop": "boolean",
    "sound": "boolean",
    "command": "boolean",
    "paneFlash": "boolean"
  }
}
```

→ hook は stdin で JSON 受け、**変更後の JSON を stdout** に返す = フィルタ/ルーティング/抑制が可能。

### Hook 定義

```jsonc
{
  "notifications": {
    "hooks": [
      {
        "id": "quiet-docs",
        "command": "sed 's/\"desktop\":true/\"desktop\":false/'",
        "timeoutSeconds": 20
      }
    ]
  }
}
```

### `notifications.command` 環境変数

- `CMUX_NOTIFICATION_TITLE`
- `CMUX_NOTIFICATION_SUBTITLE`
- `CMUX_NOTIFICATION_BODY`

### 抑制条件 (デスクトップアラート)

cmux にフォーカスあり / 通知元 workspace がアクティブ / 通知パネル開放中 → デスクトップ通知抑制 (in-app のみ)。

### hooksMode

- `append` (default): グローバル + 親ディレクトリの `.cmux/cmux.json` フックを継承マージ
- `replace`: プロジェクトフックのみ使用

### CLI 通知発火

```bash
cmux notify --title "Build" --body "Done"
cmux notify --title "Claude Code" --subtitle "Waiting" --body "Agent needs input"
```

---

## 6. Socket API / CLI subcommand 全リスト ⭐

### Socket パス

- リリース: `/tmp/cmux.sock`
- デバッグ: `/tmp/cmux-debug.sock` / `/tmp/cmux-debug-<tag>.sock`
- 上書き: `CMUX_SOCKET_PATH`

### リクエスト形式

```
{"id":"req-1","method":"workspace.list","params":{}}\n
```

レスポンス: `{"id":"req-1","ok":true,"result":{...}}`

### Socket メソッド

| カテゴリ | メソッド |
|---|---|
| workspace | `workspace.list`, `.create`, `.select`, `.current`, `.close` |
| surface | `surface.split`, `.list`, `.focus`, `.send_text`, `.send_key` |
| notification | `notification.create`, `.list`, `.clear` |
| system | `system.ping`, `.capabilities`, `.identify` |

### CLI subcommand (全列挙)

**Workspace 系**: `list-workspaces`, `new-workspace`, `select-workspace`, `current-workspace`, `close-workspace`

**Surface 系**: `new-split` (`--direction left/right/up/down`), `list-surfaces`, `focus-surface`, `send`, `send-key`, `send-surface`, `send-key-surface`

**Notification 系**: `notify`, `list-notifications`, `clear-notifications`

**Status / Progress / Log**: `set-status`, `clear-status`, `list-status`, `set-progress` (0.0–1.0), `clear-progress`, `log` (`--level info/progress/success/warning/error`), `clear-log`, `list-log`

**Inspection**: `sidebar-state`, `ping`, `capabilities`, `identify`

**Browser**: `browser <subcmd>` (詳細は §8)

**SSH**: `ssh user@host`

**Config**: `config doctor` (v0.64.3+), `reload-config`

**Session**: `restore-session`

**System**: `top` (v0.64.0+ task manager)

**Agent integrations**: `claude-teams`, `omx`, `omc`, `omo` (詳細は §7)

**Internal**: `__tmux-compat` (tmux shim 用)

### 共通 CLI フラグ

```
--socket PATH
--json
--window ID / --workspace ID / --surface ID
--id-format refs|uuids|both
--icon hammer --color "#ff9500"
--limit N
--level error --source build
```

### 環境変数

```
CMUX_SOCKET_PATH
CMUX_SOCKET_ENABLE      # 1/0, true/false, on/off
CMUX_SOCKET_MODE        # cmuxOnly, allowAll, off
CMUX_WORKSPACE_ID       # 自動設定
CMUX_SURFACE_ID         # 自動設定
CMUX_PORT               # workspace ごとに自動割当 (portBase+portRange)
TERM_PROGRAM=ghostty
TERM=xterm-ghostty
```

### MCP server

⚠️ 公式 docs では言及なし。Socket API + CLI のみ。

---

## 7. エージェント連携 4 種 比較

全て **同一アーキテクチャ**: tmux shim を `~/.cmuxterm/<name>-bin/tmux` に置き、PATH 先頭に挿入、`TMUX`/`TMUX_PANE`/`CMUX_SOCKET_PATH` を inject。上流ツールの tmux コマンドを cmux API に変換。共有 store: `~/.cmuxterm/tmux-compat-store.json`。

| 統合 | サブコマンド | 上流ツール | インストール | 特徴 |
|---|---|---|---|---|
| **claude-teams** | `cmux claude-teams [--continue] [--model sonnet]` | Claude Code 公式 | (Claude Code 同梱) | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` + teammate mode `auto`。**実験フラグ** |
| **omx** (oh-my-codex) | `cmux omx [--madmax --high] [team]` | OpenAI Codex CLI | `npm i -g @openai/codex oh-my-codex` → `omx setup` → `omx doctor` | 30+ 専門エージェント / HUD / madmax モード |
| **omc** (oh-my-claudecode) | `cmux omc [team N:claude "..."] [--watch]` | Claude Code CLI | ⚠️ `npm i -g oh-my-claude-sisyphus` (Haiku 要約、正式名要検証) | 19 エージェント / smart model routing / `NODE_OPTIONS` 注入 |
| **omo** (oh-my-opencode) | `cmux omo [--continue] [--model claude-sonnet-4-6]` | OpenCode | npm `oh-my-opencode` (bun/npm) | Claude/GPT/Gemini/Grok 並列 / shadow config (`OPENCODE_CONFIG_DIR`) / アイドル自動クリーンアップ / queueing |

### omo の専門エージェント名 (公式 docs より)

Hephaestus, Atlas, Oracle, etc. — グリッドレイアウト `main-vertical` 標準。

### 既知の罠

- 3 つ (4 つ) とも `~/.cmuxterm/<name>-bin/tmux` を生成し PATH 先頭に → **同時起動は先勝ち**
- claude-teams は experimental flag 依存 → upstream 変更で壊れる可能性
- SSH セッション内でも `cmux claude-teams` / `cmux omo` 動作する (v0.62.0+)

### v0.64.5 (2026-05-13) で追加

- **Codex Teams サブエージェント**: Codex のサブエージェントを cmux pane にマップ
- oh-my-{opencode,codex,claudecode} の hooks 対応

---

## 8. Browser Automation 全コマンド

cmux 内蔵ブラウザを `cmux browser` CLI で自動化。MCP/Playwright 不要。

| カテゴリ | コマンド |
|---|---|
| ナビゲーション | `open`, `navigate`, `back`, `forward`, `reload`, `url`, `focus-webview` |
| 描画 | `screenshot --out /tmp/cmux-page.png` |
| 操作 | `click "button[type='submit']" --snapshot-after` |
| 待機 | `wait --load-state complete`, `wait --selector`, `wait --text` |
| 観測 | `console list`, `errors list`, `snapshot --interactive --compact` |
| ストレージ | `cookies get`, `storage local set`, `state save/load` |

### 既存環境への影響

- 既存 `webapp-testing` skill, `ui-observer` agent, `playwright-test` skill との重複あり
- 利点: shell から直接呼べる + 内蔵ブラウザに直結 (Playwright のセットアップ不要)
- 限界: ⚠️ サンドボックス境界の記載なし、CDP 直接アクセスは不明

### v0.64.4 追加

- `cmux://ssh` ディープリンクは guard プロンプト後実行
- 他ブラウザからの Cookie インポート CLI

---

## 9. Skills (cmux 独自系統)

### 配置 (Anthropic 公式 `~/.claude/skills/` とは別!)

```
~/.codex/skills/<name>/         # または $CODEX_HOME/skills
  ├── SKILL.md
  ├── agents/openai.yaml         # OpenAI メタデータ (name, 短い description, default prompt)
  ├── references/*.md
  ├── scripts/*
  └── templates/*
```

### 配布

```bash
curl -fsSL https://raw.githubusercontent.com/manaflow-ai/cmux/main/skills.sh | bash

# ローカル開発
./skills.sh --list
./skills.sh --skill cmux --skill cmux-browser
./skills.sh --dest ~/.codex/skills
./skills.sh --dry-run
./skills.sh --ref <branch/tag/commit>
```

### 付属 5 skill

| Skill | 機能 |
|---|---|
| **cmux Core** | `cmux identify --json` 等の workspace/pane 制御 |
| **cmux Browser** | `cmux browser surface:2 snapshot --interactive` |
| **cmux Markdown Viewer** | `cmux markdown open plan.md` ライブリロード付き |
| **cmux Debug Windows** | debug UI 管理 |
| **cmux Release** | バージョン選択→changelog→PR→tag |

### 発見

- macOS Help メニューから Skills アクセス
- ⚠️ Codex CLI からの auto-discovery 機構の詳細は不明

### 二重管理の罠 ⚠️

- 既存 `~/.claude/skills/` 66 個 (google/skills, mizchi/skills 等) は **Anthropic Claude Code 用**
- cmux skills は `~/.codex/skills/` 配置 → Codex セッションから利用
- 同じ skill を両方に配置する場合は同期戦略が必要 (重複コピー or symlink)

---

## 10. Custom Commands (Command Palette)

### 定義 (cmux.json `actions` セクション)

```jsonc
{
  "actions": {
    "run-tests": {
      "type": "command",          // command | agent | workspaceCommand | builtin
      "title": "Run Tests",
      "subtitle": "npm test",
      "keywords": ["test", "ci"],
      "palette": true,            // false で Command Palette 非表示
      "shortcut": "cmd+shift+c",  // or ["cmd+k", "cmd+t"]
      "confirm": false,
      "command": "npm test",
      "target": "newTabInCurrentPane",  // currentTerminal | newTabInCurrentPane
      "cwd": "./server",          // . | ~/path | 絶対パス
      "env": { "NODE_ENV": "test" }
    }
  }
}
```

### ⚠️ nightly 必須機能

- `actions`
- `shortcut` (action 単位)
- `ui.surfaceTabBar.buttons`

### 信頼確認

プロジェクトローカル action 初回実行時にフィンガープリント単位で trust prompt 出現。

---

## 11. Dock (別ファイル `dock.json`)

```
~/.config/cmux/dock.json   # global
./.cmux/dock.json          # project
```

```jsonc
{
  "controls": [
    {
      "id": "build-log",
      "title": "Build",
      "command": "tail -f build.log",
      "cwd": "./",
      "height": 200,
      "env": { "DEBUG": "1" }
    }
  ]
}
```

右サイドバーに TUI コントロール (mini Ghostty terminal) を追加。

---

## 12. Session Restore

### 復元される

- Window / workspace / pane layout
- Working directories
- Terminal scrollback (best effort)
- Browser URL & history

### 復元されない

任意のライブプロセス状態 (tmux, vim, shell 等)。supported integration がない限り通常起動。

### 制御

```jsonc
"terminal": { "autoResumeAgentSessions": false }
```

または Settings > Terminal > Resume Agent Sessions on Reopen をオフ。

### Session JSON 実体

`~/Library/Application Support/cmux/session-<bundle-id>.json` (※私の環境: `session-com.cmuxterm.app.json` を実機確認済み)

### 手動復元

- File > Reopen Previous Session
- `Cmd+Shift+O` (`reopenPreviousSession` binding)
- `cmux restore-session`

---

## 13. SSH

`cmux ssh user@remote` でリモート workspace 構築。

特徴:
- ブラウザ pane が HTTP/WS をリモート経由ルーティング
- Drag&Drop ファイル → scp 自動アップロード
- リモートプロセスからの通知をローカルで受信
- `cmux claude-teams` / `cmux omo` が SSH 内動作 (v0.62.0+)
- 自動再接続 (exponential backoff)
- v0.64.4: file sidebar が SSH workspace 対応

⚠️ `sidebar.showSSH` 等の関連設定の細部は docs に明記なし。

---

## 14. 既存環境との接続マップ (再開時の起点)

| 既存資産 | パス | cmux 接続案 |
|---|---|---|
| cmux.json template | `~/.config/cmux/cmux.json` | 全コメントアウト状態 → ここに書き込む |
| cmux notify script | `dotfiles/.config/claude/scripts/runtime/cmux-notify.sh` | `notifications.command` または `hooks` から呼出可 |
| cmux ecosystem doc | `dotfiles/.config/claude/references/cmux-ecosystem.md` | 既存運用知識、追加後に更新 |
| Claude Code hooks | `~/.claude/hooks/` | `automation.claudeCodeIntegration: true` で連携 |
| Codex CLI | (skills は `~/.codex/skills/`) | cmux skills 配置先と一致 |
| Anthropic 66 skills | `~/.claude/skills/` | cmux skills とは別系統、二重管理リスク |
| dotfiles worktrees | `.claude/worktrees/`, `.worktrees/` | `app.workspaceInheritWorkingDirectory` 関連 |
| Ghostty config | `~/.config/ghostty/config` (要確認) | ターミナル本体の設定はここ |

---

## 15. 取りうる方向性 6 個 (まだ未決)

### Option 1: 通知 hook 整備 (S 規模、最も実用的)

- `notifications.command` で既存 `cmux-notify.sh` を呼ぶ、または
- `notifications.hooks` で stdin/stdout JSON フィルタを書く (例: docs workspace の desktop 通知を抑制)
- 効果: Claude Code Stop/SubagentStop → cmux 通知 + Dock badge
- 必要 fetch: なし

### Option 2: automation セクション最適化 (S)

- `claudeCodeIntegration: true` / `cursorIntegration: false` / `geminiIntegration: false` (使うものだけ)
- `portBase: 9100` / `portRange: 10` の現状確認 → 他ツール (Vite/Next) と衝突しないか
- `socketControlMode: cmuxOnly` 維持 (`automation` への昇格は API 制御使うとき)

### Option 3: claude-teams 試運転 (M)

- `cmux claude-teams` 起動 → サブエージェントが cmux split に展開される体験
- リスク: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 実験フラグ
- 既存 subagent ワークフローとの比較評価必要

### Option 4: browser-automation を webapp-testing 代替評価 (M)

- 既存 skill (`webapp-testing`, `ui-observer`, `playwright-test`) と機能比較
- 利点: shell 直呼び、Playwright セットアップ不要
- 評価軸: snapshot 品質 / console capture / network capture / 並列性

### Option 5: cmux skills を `~/.codex/skills/` に展開 (M)

- `./skills.sh --dest ~/.codex/skills` 実行
- 既存 mizchi/skills と棲み分け方針必要
- Codex CLI セッション (`cmux omx`) からの利用が前提

### Option 6: shortcuts.bindings を tmux/Ghostty 風に統一 (S)

- 現状: cmux デフォルト (cmd+ベース)
- 案: prefix `ctrl+b` + chord で tmux 風 (`["ctrl+b", "c"]` 等)
- 認知負荷低減 vs cmux ネイティブ感の trade-off

### Option 7: cmux.json 最小起動構成 (S)

何も決められない場合の defensive 最小構成:
```jsonc
{
  "app": { "newWorkspacePlacement": "end", "iMessageMode": true },
  "terminal": { "autoResumeAgentSessions": true },
  "automation": { "cursorIntegration": false, "geminiIntegration": false },
  "browser": {
    "hostsToOpenInEmbeddedBrowser": ["localhost", "127.0.0.1"],
    "urlsToAlwaysOpenExternally": []
  }
}
```

---

## 16. 未解決事項 (次セッションで要確認)

| # | 項目 | 確認方法 |
|---|---|---|
| 1 | `oh-my-claudecode` の正式 npm package 名 | `npm search oh-my-claude` or GitHub `manaflow-ai/oh-my-claudecode` |
| 2 | `automation.socketControlMode` の `allowAll`/`openAccess`/`fullOpenAccess` の差分 | 公式 docs 英語版 or `cmux capabilities --json` |
| 3 | `notifications.hooks[].command` の sh の流儀 (bash? sh?) と作業 cwd | 実機テスト or schema 確認 |
| 4 | cmux MCP server の有無 | `~/Library/Application Support/cmux/` 内 / `cmux capabilities` |
| 5 | `actions` / `shortcut` action 単位 / `ui.surfaceTabBar.buttons` の nightly 配布チャネル | brew tap manaflow-ai/cmux-nightly? 未確認 |
| 6 | cmux skills の auto-discovery 機構 (Codex CLI 側で読み込まれるか) | Codex CLI docs |
| 7 | Ghostty config の現状 (`~/.config/ghostty/config`) | `cat ~/.config/ghostty/config` |

---

## 17. 次セッションでの再開手順

```
1. このメモを読む:
   docs/research/2026-05-15-cmux-customization-notes.md

2. 既存状態を再確認:
   cat ~/.config/cmux/cmux.json
   ls -la ~/Library/Application\ Support/cmux/
   ls ~/.cmuxterm/ 2>/dev/null   # 既に何か統合済みか
   cmux --version

3. 方針決定 (Section 15 の Option 1-7 から):
   - 即効性なら Option 1 (通知 hook)
   - 探索なら Option 3 (claude-teams 試運転)
   - 整備なら Option 7 (最小起動構成) から開始

4. 編集:
   ~/.config/cmux/cmux.json は JSONC、コメント残してよい。
   編集後 Cmd+Shift+, または `cmux reload-config`。
   `cmux config doctor` で検証。

5. 検証:
   - 設定: cmux config doctor
   - 通知: cmux notify --title test --body hello
   - socket: echo '{"id":"1","method":"system.ping","params":{}}' | nc -U /tmp/cmux.sock
   - capabilities: cmux capabilities --json

6. このメモを更新:
   - Section 16 の未解決事項を埋める
   - Section 14 の接続マップを更新
   - 採用した方針を別ファイル化 (docs/plans/) する場合は判断
```

---

## 18. 参考 URL (全 docs 章)

- https://cmux.com/ja/docs/getting-started
- https://cmux.com/ja/docs/concepts
- https://cmux.com/ja/docs/configuration
- https://cmux.com/ja/docs/session-restore
- https://cmux.com/ja/docs/custom-commands
- https://cmux.com/ja/docs/dock
- https://cmux.com/ja/docs/keyboard-shortcuts
- https://cmux.com/ja/docs/api
- https://cmux.com/ja/docs/browser-automation
- https://cmux.com/ja/docs/skills
- https://cmux.com/ja/docs/notifications
- https://cmux.com/ja/docs/ssh
- https://cmux.com/ja/docs/agent-integrations/claude-code-teams
- https://cmux.com/ja/docs/agent-integrations/oh-my-codex
- https://cmux.com/ja/docs/agent-integrations/oh-my-claudecode
- https://cmux.com/ja/docs/agent-integrations/oh-my-opencode
- https://cmux.com/ja/docs/changelog
- GitHub: https://github.com/manaflow-ai/cmux
- Schema: https://raw.githubusercontent.com/manaflow-ai/cmux/main/web/data/cmux.schema.json

---

## 19. 最近の changelog ハイライト (2026-02 - 2026-05)

- **v0.64.6** (May 14): SSH キーストローク喪失修正 / コマンドパレットから bool 設定操作可
- **v0.64.5** (May 13): **Codex Teams サブエージェント** / グローバル検索 / oh-my-{opencode,codex,claudecode} hooks
- **v0.64.4** (May 11): SSH ファイルサイドバー / Vault 連携で agent session 復元
- **v0.64.3** (May 5): **`cmux config doctor`** 追加 (socket 不要検証)
- **v0.64.0** (May 5): **cmux.json 正式化** (JSONC) / Custom Commands / **menuBarOnly** / **iMessageMode** / Cursor/Gemini integration / Task Manager (`cmux top`)
- **v0.62.0** (Mar 12): **Claude Code Teams** / **oh-my-openagent (omo)** / SSH / Markdown viewer / 17 言語ローカライズ
- **v0.61.0** (Feb 25): ワークスペース色 17 プリセット / Command Palette `Cmd+Shift+P`
- **v0.60.0** (Feb 21): タブ右クリックメニュー / WebKit DevTools / 通知リング / CJK IME / Claude Code デフォルト ON

---

## 注意 (このメモ自体について)

- WebFetch 経由のため Haiku 要約が混ざる。⚠️ マーク箇所は原典または実機で再確認推奨
- 公式 docs は更新頻度高い (1 週間で複数版) → 再開時に changelog を確認
- このメモは `docs/research/` 配下だが、採用方針確定後は `docs/plans/` に Plan として切り出す
