# cmux エコシステム リファレンス

cmux を活用したマルチエージェント開発の設計パターンと運用ガイド。

## リソース階層

```
window          ← OS ウィンドウ
└── workspace   ← セッション相当（プロジェクト単位）
    └── pane    ← 画面分割のレイアウト領域
        └── surface ← ペイン内のコンテンツ（ターミナル or ブラウザ）
```

pane（レイアウト）と surface（中身）は分離されている。

## ワークスペース分離原則

Conductor（操作側）と Worker（実行側）は **別ワークスペース** に配置する。

```
workspace:1  → Conductor（親 Claude Code、広いペイン）
workspace:2  → Researcher x3（3分割）
workspace:3  → Implementer x2 + Reviewer
workspace:4  → Tester + DocKeeper
```

**理由**: 同一 workspace に詰め込むとペインが極端に狭くなり、`cmux send`/`cmux read-screen` が破損する。

## サブエージェント起動パターン

### 基本フロー: 起動 → 監視 → 結果回収

```bash
# 1. ワークスペース作成
WS=$(cmux new-workspace "task-name")

# 2. Claude Code 起動
cmux send --workspace "$WS" --surface surface:1 \
  "claude --dangerously-skip-permissions\n"

# 3. Trust 確認待ち（プロンプト出現を検出）
sleep 3  # or cmux wait-for

# 4. プロンプト送信
cmux send --workspace "$WS" --surface surface:1 "${PROMPT}"
cmux send-key --workspace "$WS" --surface surface:1 return

# 5. 完了検出 + 結果回収
cmux read-screen --workspace "$WS" --surface surface:1 --scrollback 500
```

### 監視のコツ

- `--scrollback 500` でバッファの最新500行をキャプチャ
- 5〜10秒ごとの `read-screen` ポーリングで進捗監視
- 完了判定: 特定キーワード出現 / エラーメッセージ / プロンプト再出現

## 会話フォーク（cfork）

```bash
!cfork        # 右に新ペインで会話フォーク（ゼロ遅延）
!cfork down   # 下方向にフォーク
```

LLM を経由しないシェル直実行のため即座に完了。内部実装:

```bash
S=$(cmux new-split "${DIRECTION:-right}")
cmux send --surface "$S" "claude --continue --fork-session\n"
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
