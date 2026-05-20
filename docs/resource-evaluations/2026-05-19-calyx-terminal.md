---
source: "https://github.com/yuuichieguchi/Calyx"
date: 2026-05-19
category: tool
relevance: 3
novelty: 3
actionability: 4
status: evaluated
---

## Summary

**Calyx** は macOS 26+ (Tahoe) 専用のネイティブターミナルアプリで、Mitchell Hashimoto の [libghostty](https://github.com/ghostty-org/ghostty) (v1.3.1) を Metal GPU バックエンドに使用し、Liquid Glass UI でラップした構成。Swift 6.2 + AppKit + SwiftUI で、AI Agent IPC (MCP server) と Browser Automation (25 CLI コマンド) を独自機能として提供する。著者: Yuuichi Eguchi (東京・ロンドン大 CS 学部生、followers 7、19 repos)。MIT License、233 stars / 14 forks、最終更新 2026-05-10 (active development)、最新 v0.24.1。

## Key Insights

- **既存 Ghostty config を継承**: `~/.config/ghostty/config` を読む。ただし `background-opacity` `background-blur` `font-codepoint-map` `foreground` 等は Glass UI 用に上書きされる
- **AI Agent IPC が独自価値**: Claude Code / Codex CLI / OpenCode / Hermes が異なるタブ/ペインを跨いで MCP 経由でメッセージング (`register_peer` / `send_message` / `broadcast` / `receive_messages` 等)。Command Palette → "Enable AI Agent IPC" で `~/.claude.json` `~/.codex/config.toml` 等に自動書き込み
- **Scriptable Browser**: `calyx browser snapshot/click/fill/eval/screenshot/wait/get-*` の 25 CLI コマンド。`localhost:41840` で常駐サーバ、no enable step (cmux 風)
- **Diff Review Comments → Agent 連携**: gutter `+` でインラインコメント、Submit Review で Claude Code/Codex/OpenCode/Hermes タブに直接送信
- **Compose Overlay (`Cmd+Shift+E`)**: 長文プロンプト用フローティングエディタ
- **0.x ステージ**: 9 日間で v0.22.5 → v0.24.1。breaking change リスクあり

## Gap Analysis

| # | 手法/知見 | 判定 | 詳細 |
|---|-----------|------|------|
| 1 | **AI Agent IPC (MCP peer-to-peer)** | **Gap** | 既存セットアップは Claude↔Codex を subagent dispatch / cmux Worker / `codex:rescue` で連携。タブ間ピアトゥピアの message passing は未実装。ただし memory `feedback_codex_invocation_pattern.md` の文脈で MCP 直叩きより skill 経由が原則 |
| 2 | **Scriptable Browser (`calyx browser ...`)** | **Partial** | 既存 `webapp-testing` skill は agent-browser CLI (`localhost:???`) を使用。Calyx は `localhost:41840` で別実装。Browser server lifecycle は `references/agent-browser-server-lifecycle.md` 既存。**共存可能だが二重 server リスク** |
| 3 | **Diff Review Comments → Agent prompt** | **Already (強化不要)** | `/difit` skill (`difit --comment` で GitHub 風 diff viewer + AI prompt copy) が既存。Calyx は GUI 完結、`/difit` は CLI 完結。思想は同じ |
| 4 | **Compose Overlay (長文プロンプト UI)** | **N/A** | TUI 環境では `$EDITOR` (nvim) 起動 + heredoc で代替可能。Claude Code TUI の input box でも multi-line OK |
| 5 | **Liquid Glass UI / Tab Groups / Split Panes** | **N/A** | 純粋に UX。WezTerm / iTerm2 / 素の Ghostty で代替可。functional 価値は薄い |
| 6 | **Ghostty config 継承** | **Already (強化不要)** | ユーザーが Ghostty を使っていれば自動継承される。Calyx-managed keys のみ override |
| 7 | **OSC 9/99/777 Desktop Notifications** | **Partial** | 既存 cmux-notify hook (commit 2c255fb) が hook ベースの notify を提供。OSC escape による terminal-native notify は未対応 |

## Setup Notes

### インストール (推奨: Homebrew)

```bash
brew tap yuuichieguchi/calyx
brew install --cask calyx
```

直接ダウンロード版は Sparkle 経由で自動更新、Homebrew 版は `brew upgrade --cask calyx` で更新。

### 前提条件

- **macOS 26+ (Tahoe)** — 必須。macOS 25 以下では起動不可
- Ghostty 設定 (`~/.config/ghostty/config`) があれば自動継承

### Build from source (オプション)

```bash
git clone --recursive https://github.com/yuuichieguchi/Calyx.git
cd Calyx
cd ghostty && zig build -Demit-xcframework=true -Dxcframework-target=native && cd ..
cp -R ghostty/macos/GhosttyKit.xcframework .
xcodegen generate
xcodebuild -project Calyx.xcodeproj -scheme Calyx -configuration Debug build
```

要件: Xcode 26+, Zig (ghostty の `build.zig.zon` と version 一致), XcodeGen (`brew install xcodegen`)

### CLI セットアップ

`calyx` バイナリは `Calyx.app/Contents/Resources/bin/` 内に同梱。Command Palette (`Cmd+Shift+P`) → **Install CLI to PATH** で `/usr/local/bin/calyx` などに symlink。

## Usage Notes

### キーバインド主要なもの

| Group | Shortcut | Action |
|-------|----------|--------|
| Global | `Cmd+Shift+P` | Command Palette |
| Global | `Cmd+Shift+E` | Compose Overlay (長文入力) |
| Tab | `Cmd+T` / `Cmd+W` / `Cmd+1..9` | 新規/閉じる/切替 |
| Split | `Cmd+D` / `Cmd+Shift+D` | 右/下分割 |
| Split | `Cmd+Option+Arrow` | フォーカス移動 |
| Search | `Cmd+F` / `Cmd+G` | スクロールバック検索 |
| Group | `Ctrl+Shift+N` / `Ctrl+Shift+W` | グループ新規/閉じる |
| Notify | `Cmd+Shift+U` | 直近未読通知タブへジャンプ |

### AI Agent IPC 利用手順

1. Command Palette → **Enable AI Agent IPC** を実行
2. 別タブ/ペインで `claude` `codex` `opencode` `hermes` を起動
3. 各エージェントが自動的に peer 登録される
4. MCP tools が使えるようになる:
   - `register_peer` / `list_peers` / `send_message` / `broadcast` / `receive_messages` / `ack_messages` / `get_peer_status`

**自動書き込み先 (注意)**:
- `~/.claude.json` (Claude Code MCP 設定)
- `~/.codex/config.toml` (Codex CLI MCP 設定)
- `~/.config/opencode/{opencode.json,AGENTS.md}`
- `~/.hermes/config.yaml`

**無効化**: Command Palette → **Disable AI Agent IPC**

### Browser 自動化 (cmux 互換)

```bash
calyx browser list                          # 全タブ一覧
calyx browser snapshot --tab-id <id>        # accessibility tree + element refs
calyx browser get-text h1 --tab-id <id>
calyx browser click a --tab-id <id>
calyx browser fill input --value "text"
calyx browser eval 'document.title'
calyx browser screenshot
calyx browser wait --selector ".loaded"
calyx browser get-attribute a href
calyx browser get-links                     # JSON で全リンク
calyx browser get-inputs                    # JSON で全 input
calyx browser is-visible '#sidebar'
calyx browser hover '#menu-item'
calyx browser scroll down --amount 500
```

サーバ: `localhost:41840`、設定: `~/.config/calyx/browser.json`

## 既存セットアップとの統合上の注意

### MCP 干渉リスク (最重要)

- **AI Agent IPC を有効化すると `~/.claude.json` が自動編集される**
- 既存の MCP 設定 (context7, openaiDeveloperDocs, brave-search, playwright, alphaxiv, scite, Obsidian/Gmail/Calendar/Drive) との競合可能性
- `scripts/policy/mcp-audit.py` の VeriGrey Tool Filter が **enforcement** (`sys.exit(2)` で hard block) のため、Calyx 由来の MCP tool は audit 対象に追加する必要あり
- 対策: enable 前に `~/.claude.json` を git で commit/backup、enable 後の diff を確認

### Browser server 二重起動リスク

- 既存 `webapp-testing` skill の agent-browser CLI と Calyx browser server (`:41840`) が共存
- `references/agent-browser-server-lifecycle.md` に Calyx 起動時のチェック追加 (どちらを使うか判断ルール) を後日検討

### 日本語環境の既知バグ

- 全角文字行で **cursor click-to-move がオフセット** (Ghostty 内部で arrow-key 変換のため)
- 影響: 日本語コミットメッセージや CJK ドキュメントで cursor 位置ずれ

### Ghostty config の override

Calyx が上書きするキー (Settings → Ghostty Config Compatibility で全リスト):
- `background-opacity`
- `background-blur`
- `background-opacity-cells`
- `font-codepoint-map`
- `foreground`

その他のキー (font, keybind, shell-integration 等) は hot-reload。

## Risk Summary

| リスク | 度合い | 根拠 |
|-------|--------|------|
| **macOS 26 必須** | High | Tahoe 未更新マシンでは起動不可 |
| **0.x ステージ (v0.24.1)** | Medium | 9 日で 3 minor バージョン、breaking change リスク |
| **MCP 設定への自動書き込み** | Medium | `~/.claude.json` 干渉、mcp-audit との競合 |
| **メンテナンス信頼性** | Low-Med | 著者 followers 7 / 19 repos / 4 年アカウント、track record 限定的。ただし active commit + Trending 経緯あり |
| **License (MIT)** | Low | dotfiles と互換 |
| **Ghostty 設定 override** | Low | Glass UI 用、明示されている |

## Decision

- [x] **試用 (好奇心ベース)**: cmux 代替検討ではなく「触ってみたい」が動機。撤退コスト最小の形で試用
- [ ] スキップ
- [ ] 全面採用 (cmux からの乗り換え) — N/A: cmux と機能重複が大きく、現時点で乗り換え合理性は薄い
- [ ] 後日再評価: 試用結果と v1.0 安定後の AI Agent IPC 価値を再判断

### Phase 1: 撤退コスト最小の試用 (現在のステップ)

```bash
brew tap yuuichieguchi/calyx
brew install --cask calyx
```

**やる**:
- 通常ターミナルとして起動して感触を見る
- Ghostty config (`~/.config/ghostty/config`) の継承挙動を確認
- Liquid Glass UI / Tab Groups / Split / Command Palette / Compose Overlay (`Cmd+Shift+E`) / Quick Terminal を試す
- 日本語環境の cursor バグ影響を観察

**やらない (撤退コストを上げる行為を回避)**:
- Command Palette → "Enable AI Agent IPC" (`~/.claude.json` などへの自動書き込みを起こさない)
- `Install CLI to PATH` (既存 `calyx`/`cmux` CLI と衝突しないよう保留)
- デフォルトターミナル変更 (cmux/iTerm2/Ghostty はそのまま)

**撤退手順**: `brew uninstall --cask calyx` のみ。IPC enable していなければ `~/` 配下への永続書き込みなし。

### Phase 2: IPC/Browser 採用 (試用が気に入った場合のみ)

1. `~/.claude.json` を `git stash` または backup
2. Command Palette → Enable AI Agent IPC
3. diff を確認、`scripts/policy/mcp-audit.py` allowlist 更新
4. Claude↔Codex の peer messaging を 1-2 タスクで実験
5. `webapp-testing` skill と Calyx Browser の使い分け方針を `references/agent-browser-server-lifecycle.md` に追記
6. cmux との共存方針 (どっちをデフォルトにするか) を決める

### 撤退条件

- 0.x で重大な regression が頻発する場合
- MCP 干渉で既存 audit policy が破綻する場合
- 日本語 cursor バグが操作性を著しく損なう場合
- → アンインストール: `brew uninstall --cask calyx` + `~/.claude.json` を backup から復元

## Sources

- README: https://github.com/yuuichieguchi/Calyx/blob/main/README.md
- Releases: https://github.com/yuuichieguchi/Calyx/releases (v0.24.1 @ 2026-05-10)
- Author: https://github.com/yuuichieguchi
- Ghostty (upstream): https://github.com/ghostty-org/ghostty
- Demo videos:
  - Theme: https://www.youtube.com/watch?v=cUYc7yzI_eM
  - Diff Review: https://www.youtube.com/watch?v=_O2Lr4oFf4c
  - AI Agent IPC: https://www.youtube.com/watch?v=Xty0ad9gGcM
  - Compose Overlay: https://www.youtube.com/watch?v=qhwYnk8adF4

## Investigation Notes

- 初回 Gemini grounding 調査は **Hallucination** (Calyx を別の "dotfiles" repo と完全に混同し、「100+ skills」「Karpathy 4 原則」「.config/claude/agents/」など捏造)。`gh api repos/yuuichieguchi/Calyx` で独立検証して訂正
- 教訓: memory の Nav Toor / zodchixquant の教訓と一致 — **content farm signal がなくても Gemini grounding は信頼性低**、`gh api` 直接検証が必須
- 出典追跡: README は `gh api repos/yuuichieguchi/Calyx/readme` で base64 取得・デコード
