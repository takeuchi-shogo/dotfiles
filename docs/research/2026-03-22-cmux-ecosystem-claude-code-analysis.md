---
source: "https://zenn.dev/hummer/articles/cmux-ecosystem-claude-code"
date: 2026-03-22
status: integrated
---

## Source Summary

- **主張**: cmux エコシステムにより Claude Code が「単一セッション」から「複数ワークスペースを横断するマルチエージェント」に進化する
- **手法**: 5コンポーネント（using-cmux, cmux-team, cmux-remote, cfork, plugin-packager）
- **根拠**: ワークスペース分離でサブエージェント安定運用、リアルタイム可視性向上、ゼロ遅延フォーク
- **前提条件**: cmux インストール済み、macOS

### コンポーネント詳細

| コンポーネント | リポジトリ | 役割 |
|--------------|-----------|------|
| using-cmux | hummer98/using-cmux | Claude Code に cmux 操作を教えるスキル |
| cmux-team | hummer98/cmux-team | 複数エージェントの並列協調フレームワーク |
| cmux-remote | hummer98/cmux-remote | iPhone からリアルタイム監視する PWA |
| cfork | hummer98/cfork | 会話コンテキストを保ったフォーク |
| plugin-packager | hummer98/plugin-packager | スキル配布の自動化 |

### 核となるアーキテクチャ

**リソース階層**:
```
window → workspace → pane → surface
```
pane（レイアウト）と surface（中身）が分離されている点が従来のターミナルマルチプレクサとの決定的な違い。

**ワークスペース分離原則**:
```
workspace:1 → Conductor（操作側、広いペイン）
workspace:2+ → Worker（実行側、各 workspace 内で分割）
```
同一 workspace に詰め込むとペインが狭くなり cmux send/read-screen が破損する。

**サブエージェント起動パターン**:
```bash
WS=$(cmux new-workspace "task-name")
cmux send --workspace "$WS" --surface surface:1 "claude --dangerously-skip-permissions\n"
# Trust 確認待ち
cmux send --workspace "$WS" --surface surface:1 "${PROMPT}"
cmux send-key --workspace "$WS" --surface surface:1 return
# 完了検出: cmux read-screen --scrollback 500
```

**cfork の実装**（たった2行）:
```bash
S=$(cmux new-split "${DIRECTION:-right}")
cmux send --surface "$S" "claude --continue --fork-session\n"
```

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | cmux 通知統合 | Already | cmux-notify.sh + settings.json hook 統合済み |
| 2 | cmux AI coding terminal 運用 | Already | aerospace workspace 4 に配置済み |
| 3 | worktree 並列 Claude Code | Already | /autonomous + worktree パターン確立済み |
| 4 | using-cmux plugin | Gap | Claude Code が cmux を直接操作するスキル未導入 |
| 5 | cmux-team マルチエージェント | Gap | Conductor + Worker 並列オーケストレーション未導入 |
| 6 | cmux-remote iPhone 監視 | Gap | リモート監視手段なし |
| 7 | cfork 会話フォーク | Gap | --fork-session を手動実行している |
| 8 | plugin-packager 配布自動化 | N/A | 外部配布は現時点で不要 |
| 9 | ワークスペース分離原則 | Partial | 概念は理解済みだが未ドキュメント化 |
| 10 | サブエージェント起動パターン | Gap | cmux send/read-screen による監視パターン未記録 |

## Integration Decisions

### 統合対象（全6件）

1. **using-cmux plugin**: `/plugin marketplace add hummer98/using-cmux` でインストール
2. **cmux-team**: `/plugin install hummer98/cmux-team` でインストール
3. **cmux-remote**: `git clone hummer98/cmux-remote` + Tailscale 経由で iPhone 接続
4. **cfork**: `/plugin install hummer98/cfork` or `!cfork` シェルスクリプト設置
5. **ワークスペース分離原則**: `references/cmux-ecosystem.md` にドキュメント化
6. **サブエージェント起動パターン**: 同 reference にドキュメント化

### 見送り（1件）

- **plugin-packager**: スキルの外部配布は現時点で不要

## 追加統合（2026-03-30 再分析）

記事再取得で新たに詳述されていた知見を追加統合。

| # | 手法 | 判定 | 対応 |
|---|------|------|------|
| 1 | cmux-team 4層アーキテクチャ (Master/Manager/Conductor/Agent) | Partial→統合 | `references/cmux-ecosystem.md` に4層+pull型通信+イベント駆動パターン追記 |
| 2 | Plugin vs Agent Skills 判断基準 | Gap→統合 | 同 reference にコンポーネント構成別の使い分け表追記 |
| 3 | タブ自動表示（SessionStart hook） | Gap→統合 | 同 reference に Plugin 限定の surface 番号表示機能を記録 |
| A3 | ワークスペース分離原則の強化 | Already→強化 | 4層アーキテクチャを分離原則の上位設計として紐付け |

## Plan

### T1: Plugin インストール（ユーザーアクション）

```bash
# using-cmux（cmux 操作スキル）
/plugin marketplace add hummer98/using-cmux
/plugin install using-cmux

# cmux-team（マルチエージェント協調）
/plugin install hummer98/cmux-team

# cfork（会話フォーク）
/plugin install hummer98/cfork
```

### T2: cmux-remote セットアップ（ユーザーアクション）

```bash
git clone https://github.com/hummer98/cmux-remote
cd cmux-remote/server
bun install && bun run src/index.ts
# Tailscale 経由で iPhone からアクセス
```

### T3: reference ドキュメント作成（自動）

`references/cmux-ecosystem.md` にワークスペース分離原則とサブエージェント起動パターンを記録。

### T4: MEMORY.md 更新（自動）

ターミナル構成セクションに cmux エコシステム情報を追加。
