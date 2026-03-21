---
source: "Ghostty SAND Keybindings article (davila7) + cmux investigation"
date: 2026-03-22
status: integrated
---

## Source Summary

### Ghostty SAND Keybindings (davila7)

- **主張**: VSCode terminal は AI-scale output に耐えられない。Ghostty + SAND mnemonic でパネル管理を習慣化すべき
- **手法**: SAND = Split (Cmd+D/Shift+D), Across (Cmd+T/Shift+Left/Right), Navigate (Cmd+Alt+Arrows/Shift+E/Shift+F), Destroy (Cmd+W)
- **根拠**: M4 Mac でも VSCode terminal が Claude Code 長時間セッションでクラッシュ
- **前提条件**: Ghostty 使用、macOS、Claude Code ヘビーユーザー

### cmux (manaflow-ai/cmux)

- **概要**: Ghostty (libghostty) ベースの macOS ネイティブターミナル。AI coding agent 特化
- **手法**: vertical tabs, agent notifications (OSC 9/99/777), socket API, in-app browser, tmux 互換 CLI
- **根拠**: 7.7k GitHub stars (初月)、Ghostty config 互換
- **前提条件**: macOS only、v0.62.2 (2026-03)

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | SAND keybindings | Already | keybind.conf に全て設定済み |
| 2 | lazygit + yazi split | Already | ツール利用中、Ghostty split で可能 |
| 3 | worktree 並列 Claude Code | Already | /autonomous + worktree パターン確立済み |
| 4 | cmux Ghostty config 互換性 | Partial | テーマ/フォント/色は共有。タブ系 keybind は issue #135 で未対応 |
| 5 | cmux 通知を hooks に統合 | Gap -> Integrated | cmux-notify.sh 作成、settings.json 更新 |
| 6 | cmux socket API 活用 | Gap (deferred) | 将来的にワークスペース自動セットアップに活用可能 |
| 7 | cmux in-app browser | N/A | Playwright MCP でカバー済み |
| 8 | aerospace workspace 最適化 | Partial -> Integrated | コメントで役割明記 |
| 9 | tmux 役割見直し | Gap -> Integrated | リモート SSH 専用に位置づけ直し |

## Integration Decisions

### 統合済み (3件)

1. **cmux-notify.sh**: Stop/Notification hook で cmux notify + claude-hook notification を使用。cmux 外では osascript フォールバック
2. **aerospace コメント**: workspace 4 (cmux) に AI coding terminal としての役割を明記
3. **tmux 役割明確化**: .tmux.conf にリモート SSH 専用コメントを追加

### 見送り (2件)

- **cmux socket API 自動化**: workspace/tab の自動セットアップは将来タスク。現状の手動管理で十分
- **keybind 統一**: cmux issue #135 が OPEN。upstream 対応待ち

## Key Findings

### cmux CLI は非常にリッチ

```
cmux notify --title <text> --body <text>      # 通知
cmux claude-hook <session-start|stop|notification>  # Claude Code 専用
cmux set-status <key> <value>                  # サイドバーメタデータ
cmux set-progress <0.0-1.0>                    # 進捗バー
cmux read-screen [--scrollback]                # 画面読み取り
cmux send <text>                               # テキスト送信
cmux browser <subcommand>                      # ブラウザ自動化
```

環境変数 `CMUX_WORKSPACE_ID`, `CMUX_SURFACE_ID` が cmux 内で自動設定される。

### Ghostty keybind の互換性

| カテゴリ | 互換性 |
|---------|--------|
| テーマ/フォント/色 | 完全互換 (~/.config/ghostty/config を読む) |
| terminal split keybind | 互換 (libghostty ベース) |
| tab keybind | 非互換 (cmux が独自管理、issue #135) |
| window keybind | cmux 独自 |
