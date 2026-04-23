---
status: active
last_reviewed: 2026-04-23
---

# cmux エコシステム リファレンス

cmux を活用したマルチエージェント開発の設計パターンと運用ガイド。

## CLI 基本情報

- **CLI パス**: `/Applications/cmux.app/Contents/Resources/bin/cmux`
  - PATH 上の `/Applications/cmux.app/Contents/MacOS/cmux` はメインバイナリ。Bash tool からはソケット通信がハングするので使わない
- **コマンド名**: ハイフン区切り（`send-key`, `read-screen`, `close-surface`）
  - アンダースコア（`send_key`, `read_screen`）は**動かない**
- **対象指定**: `--workspace <id|ref>`, `--surface <id|ref>` で対象を指定
  - 環境変数 `CMUX_WORKSPACE_ID`, `CMUX_SURFACE_ID` がセットされていればデフォルトで使われる
  - ref 形式: `workspace:1`, `surface:43`, `pane:22` など

## よく使うコマンド

| コマンド | 用途 | 例 |
|---------|------|-----|
| `list-workspaces` | ワークスペース一覧 | |
| `list-panels` | 現ワークスペースのサーフェス一覧 | |
| `list-panes` | ペイン一覧 | |
| `new-split <direction>` | 分割してサーフェス作成 | `new-split right` → `OK surface:43 workspace:1` |
| `new-workspace` | ワークスペース作成 | `new-workspace --command "codex"` |
| `send --surface <ref> <text>` | テキスト入力 | `send --surface surface:43 "ls -la"` |
| `send-key --surface <ref> <key>` | キー送信 | `send-key --surface surface:43 enter` |
| `read-screen --surface <ref>` | 画面読み取り | `read-screen --surface surface:43 --scrollback --lines 200` |
| `close-surface --surface <ref>` | サーフェス閉じ | `close-surface --surface surface:43` |

## リソース階層

```
window          ← OS ウィンドウ
└── workspace   ← セッション相当（プロジェクト単位）
    └── pane    ← 画面分割のレイアウト領域
        └── surface ← ペイン内のコンテンツ（ターミナル or ブラウザ）
```

pane（レイアウト）と surface（中身）は分離されている。

## サブエージェント起動パターン

### 基本フロー: 起動 → 監視 → 結果回収

```bash
CMUX=/Applications/cmux.app/Contents/Resources/bin/cmux

# 1. スプリット作成（右に新ペイン）
SURFACE=$($CMUX new-split right | awk '{print $2}')
# => surface:43

# 2. CLI ツール起動（例: codex）
$CMUX send --surface "$SURFACE" "codex"
$CMUX send-key --surface "$SURFACE" enter

# 3. 起動待ち
sleep 5
$CMUX read-screen --surface "$SURFACE" --lines 20

# 4. プロンプト送信
$CMUX send --surface "$SURFACE" "質問テキスト"
$CMUX send-key --surface "$SURFACE" enter

# 5. 完了検出 + 結果回収（ポーリング）
sleep 30
$CMUX read-screen --surface "$SURFACE" --scrollback --lines 200

# 6. クリーンアップ
$CMUX send --surface "$SURFACE" "/exit"
$CMUX send-key --surface "$SURFACE" enter
sleep 2
$CMUX close-surface --surface "$SURFACE"
```

### 完了検出のコツ

- `read-screen --scrollback --lines N` でバッファの最新 N 行をキャプチャ
- ポーリング間隔: 軽い質問は 10秒、重い推論は 30-60秒
- 完了判定: 入力プロンプト再出現（Codex なら `›`、Claude なら `>`）
- `--scrollback` なしだと表示中の画面のみ、`--scrollback` で履歴バッファ込み

### ワークスペース分離（大規模時）

別ワークスペースに配置する場合:

```bash
# ワークスペース作成
$CMUX new-workspace --command "codex"

# ワークスペース一覧で確認
$CMUX list-workspaces
```

**理由**: 同一 workspace に詰め込むとペインが極端に狭くなり、`read-screen` の出力が破損する。

## cmux-team 4層アーキテクチャ

```
Master（ユーザー対話、task 作成）
└── Manager（アイドル待機、task 検出 → Conductor 起動）
    └── Conductor（git worktree でタスク自律実行）
        └── Agent（実装・テスト・リサーチ）
```

| 層 | 役割 | 通信方式 |
|----|------|---------|
| Master | ユーザーと対話し task を作成 | — |
| Manager | **イベント駆動**でアイドル待機。task 検出時に Conductor を起動 | **pull 型** — Manager が能動的にタスクキューを監視 |
| Conductor | git worktree 内で自律実行。ワークスペースごとに隔離 | スクリプト化された起動 |
| Agent | Conductor 配下で実装・テスト・リサーチを担当 | Conductor が指示 |

**設計ポイント**: push ではなく **pull 型通信** により、Manager が自律的にタスクを検出・分配する。

## 会話フォーク（cfork）

```bash
!cfork        # 右に新ペインで会話フォーク（ゼロ遅延）
!cfork down   # 下方向にフォーク
```

LLM を経由しないシェル直実行のため即座に完了。内部実装:

```bash
CMUX=/Applications/cmux.app/Contents/Resources/bin/cmux
S=$($CMUX new-split "${DIRECTION:-right}" | awk '{print $2}')
$CMUX send --surface "$S" "claude --continue --fork-session"
$CMUX send-key --surface "$S" enter
```

### 活用シーン

- アーキテクチャ検証: 異なる設計案を並行で実装・比較
- 言語選択: Python vs Go の実装パフォーマンスを同時テスト
- 段階的最適化: 元の会話はそのまま、別ペインで大胆な改造を試験

## cmux-team スラッシュコマンド

| コマンド | 動作 |
|---------|------|
| `/team-init` | チーム初期化 |
| `/team-research` | 並列リサーチ（3エージェント） |
| `/team-design` | 設計 + レビュー |
| `/team-impl` | 並列実装 |
| `/team-review` | コードレビュー |
| `/team-test` | テスト実行 |
| `/team-status` | 進捗確認 |
| `/team-disband` | 全エージェント終了 |

## cmux-remote（iPhone 監視）

```
iPhone (PWA: React + xterm.js)
    ↕ WebSocket
Bridge Server (Bun + Hono)
    ↕ Unix Domain Socket
cmux (~/.../cmux.sock)
```

- 2本指上下スワイプ: ワークスペース切り替え
- 2本指左右スワイプ: ペイン切り替え
- 認証はネットワーク層（Tailscale P2P）に委ねる

## dispatch (Worker Router)

サブエージェントと cmux Worker を自動振り分けする `/dispatch` スキル。

### コンポーネント

| ファイル | 役割 |
|---------|------|
| `skills/dispatch/SKILL.md` | Worker Router スキル（判定ロジック） |
| `scripts/runtime/launch-worker.sh` | Worker 起動（cmux ワークスペース作成 + モデル別 CLI 起動） |
| `scripts/runtime/collect-result.sh` | 結果回収（ポーリング + 完了検出 + リトライ） |
| `scripts/runtime/dispatch-log.sh` | 通信ログ閲覧（show / filter / summary） |
| `scripts/lib/dispatch_logger.sh` | ログ記録共通関数（JSONL 追記） |
| `references/subagent-vs-cmux-worker.md` | 判定基準の比較表 |

### 振り分け基準

- **デフォルト**: サブエージェント（Agent tool）
- **cmux Worker 昇格条件**: 長時間(30分+)、マルチモデル(Codex/Gemini)、高並列(5+)、人間介入

### 通信ログ

`/tmp/cmux-dispatch-log/{session-id}.jsonl` に全通信を記録。`dispatch-log.sh summary` でサマリ表示。

## Plugin vs Agent Skills の使い分け

| コンポーネント構成 | 推奨方法 | 理由 |
|------------------|---------|------|
| スキルのみ | Agent Skills (`npx skills add`) | 軽量。フック不要なら十分 |
| スキル + コマンド | Plugin (`/plugin install`) を推奨 | コマンド登録には Plugin が必要 |
| スキル + コマンド + フック | **Plugin 必須** | SessionStart 等のフックは Plugin でのみ動作 |

**タブ自動表示**: Plugin インストール時、SessionStart フックで `[87] Claude Code` 形式にタブが自動更新され、surface 番号が常に見える。マルチエージェント時の surface 混同を防止する。Agent Skills インストールではこの機能は非対応。

## エコシステムコンポーネント

| コンポーネント | リポジトリ | インストール |
|--------------|-----------|-------------|
| using-cmux | hummer98/using-cmux | `/plugin install` (推奨) or `npx skills add` |
| cmux-team | hummer98/cmux-team | `/plugin install` |
| cmux-remote | hummer98/cmux-remote | `git clone` + `bun run` |
| cfork | hummer98/cfork | `/plugin install` or `!cfork` |
| plugin-packager | hummer98/plugin-packager | `/package` コマンド |

## 既存ワークフローとの関係

| 既存パターン | cmux エコシステム版 | 違い |
|------------|-------------------|------|
| `/autonomous` + worktree | cmux-team + ワークスペース分離 | 可視性向上、リアルタイム介入可能 |
| `claude --fork-session` 手動 | `!cfork` | ゼロ遅延、ペイン自動作成 |
| PC 画面で監視 | cmux-remote | iPhone から外出中も監視可能 |
