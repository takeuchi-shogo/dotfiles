---
status: active
last_reviewed: 2026-05-19
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

## hub-and-spoke (conductor = メイン Claude)

ブラッシュアップ系 (debate / 設計判断 / セカンドオピニオン / 比較) のデフォルト型。
複数モデルを spoke に並列起動し、メイン Claude が conductor として統合する。
Sakana Fugu の「学習済み conductor が役割を割り当てて統合」を、conductor = メイン
(ルールベース) で手作り再現したもの。

### 手順

```bash
# 1. spoke を並列起動 (役割を割り当てる: 主張役 / 反証役 / 検証役 など)
launch-worker.sh --model codex  --task '反証・検証の役割...'   # => workspace:N w-...-codex
launch-worker.sh --model claude --task '主張・設計の役割...'   # => workspace:M w-...-claude

# 2. 回収 (結果ファイル /tmp/cmux-results/<worker_id>.md を検出)。codex は exec で数分
#    かかるので background 推奨
collect-result.sh --workspace workspace:N --worker w-...-codex  --timeout 600
collect-result.sh --workspace workspace:M --worker w-...-claude --timeout 600

# 3. conductor = メインが両者を統合 → 撤退条件つき結論
```

### 運用 tip (実証 2026-06-24)

- **env 不要**: `dispatch_logger.sh` が `DISPATCH_RESULT_DIR=/tmp/cmux-results` と
  `DISPATCH_DONE_SIGNAL` のデフォルトを供給する。`launch-worker.sh` /
  `collect-result.sh` は `DISPATCH_*` を export せず直接呼べる。
- **claude worker は workspace が残る** (codex/gemini は成功時に `&& close-workspace`
  で自動 close)。統合後に `cmux close-workspace --workspace workspace:M` で掃除する。
- **gemini は sunset** (IneligibleTierError) なので実質 codex + claude の 2 spoke。
- **独立 context が価値**: 各 spoke は別 workspace = 別 context なので視点が割れる。
  単一モデルの fan-out (同一 context) より多様性が出る。
- **多数決・無制限ラリーは品質を上げない** (「収束して見える誤答」を作る)。conductor
  が撤退条件つきで統合判断するのが核心 — fan-out + judge より文脈適合ルーティング + 検証。

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

## Issue #51: 自動 worktree 連携 — Phase 0 実現可能性調査 (2026-05-19)

`cmux new-workspace` で workspace 作成時に自動で git worktree を切る wrapper / hook の実現可能性を調査。

### 調査結果

| 機能 | 実在 | 用途 | 検証コマンド |
|------|------|------|------------|
| `cmux events` (newline-delimited JSON stream) | ✅ | event subscribe 永続化、`--reconnect` + `--cursor-file` で再開可 | `cmux events --reconnect --category workspace --cursor-file ~/.cache/cmux/seq` |
| `workspace.create` RPC method | ✅ | プログラム制御で workspace 作成 | `cmux capabilities` の methods に存在 |
| `workspace.created` event 配信 | ✅ 配信 (実機確認 2026-05-19) | daemon 側 listener のトリガー | payload に `workspace_id` / `cwd` / `title` / `custom_title` / `index` / `tab_count` を含む |
| 宣言的 `onWorkspaceCreate` hook (cmux.json) | ❌ | — | `notifications.hooks` は通知系のみ、`cmux hooks` は agent 側 (codex/opencode 等) install 用 |

**結論**: 宣言的 workspace lifecycle hook は無いが、`cmux events --reconnect` 永続接続で event-driven daemon が実装可能。

### Phase 1 設計選択肢

| 方式 | 実装コスト | 信頼性 | 注意点 |
|------|----------|--------|--------|
| A) wrapper コマンド (`cmux-new-workspace-with-worktree`) | 低 | 高 (同期実行) | ユーザー明示的呼び出し必要 |
| B) `cmux events` daemon (永続 listener) | 中 | 中 (daemon 死活管理必要) | LaunchAgent or systemd unit、`--cursor-file` で resume |
| C) `cmux.json` action から zsh 関数呼び出し | 低 | 中 | Issue #49 action 機構の応用 |

**推奨**: Issue #48 (`wt-new`) で実用上十分か体感評価を先行。不十分なら C → B の順で導入。

### Phase 2 自動化レベル

| モード | 挙動 | 推奨度 |
|--------|------|--------|
| 完全自動 (workspace 名 = worktree 名で常に作る) | 全 workspace で worktree 強制 | 低 (一回限り workspace で過剰) |
| opt-in (`--with-worktree` フラグ付き起動時のみ) | 明示的指定時のみ | **高** |
| smart auto (cwd が git repo の workspace のみ) | repo 内 workspace で自動 | 中 (誤検出リスク) |

### 関連 Issue

- #48: `wt-*` zsh worktree wrappers (✅ 完了 f1ea539) — Phase 1 wrapper 方式の基盤
- #49: `cmux.json` Worktree Agents action (✅ 完了 5bbebf) — Phase 1 C 方式の基盤
- #51: 本 Issue (cmux new-workspace + worktree 自動連携) — Phase 0 完了、Phase 1 B + Phase 2 smart auto 実装済 (2026-05-19)

## Issue #51: Phase 1 B 実装 (公式 events.jsonl tail 方式)

`scripts/runtime/cmux-worktree-daemon.sh` を LaunchAgent (`com.cmux.worktree-daemon`) として常駐させ、公式 events.md で明記された `~/.cmuxterm/events.jsonl` (「Every emitted event is also appended」) を `tail -F` で listen。

**経緯**: 当初 `cmux events --reconnect --cursor-file` (Resume 契約) を採用したが、launchctl 環境では cmux events 子 process が起動直後に exit する症状あり (TTY/session 関連、env-iso foreground では正常動作)。`events.jsonl` は socket/Mach port 不要で append-only に依存するため launchctl でも安定動作。公式 events.md 範囲内の代替実装。

### 動作 (smart auto モード, default)

1. `workspace.created` event 受信
2. payload (`workspace_id`, `cwd`, `title`/`custom_title`) を抽出
3. cwd が git repo の **main repo** か検査 (worktree 内なら再帰防止で skip)
4. title sanitize (`[^a-zA-Z0-9_+.-]` → `-`) → worktree 名
5. 既存 worktree あれば skip
6. `git worktree add <repo>/.claude/worktrees/<name> -b worktree-<name>` 実行

### 環境変数

| 変数 | 用途 | default |
|------|------|---------|
| `CMUX_WORKTREE_DAEMON_DISABLE=1` | kill switch (no-op exit) | unset (有効) |
| `CMUX_WORKTREE_DAEMON_OPT_IN_PREFIX` | title 先頭一致のみ通過する opt-in mode | unset (smart auto モード) |
| `CMUX_EVENTS_JSONL` | tail 対象 events.jsonl の path | `~/.cmuxterm/events.jsonl` |
| `CMUX_WORKTREE_LOG_FILE` | log 出力先 | `~/.cache/cmux/cmux-worktree-daemon.log` |

### Install / Uninstall

```
task cmux:worktree-daemon:install     # plist install + launchctl bootstrap
task cmux:worktree-daemon:uninstall   # bootout + plist 削除
tail -f ~/.cache/cmux/cmux-worktree-daemon.log   # 動作確認
```

### Phase 2 自動化レベル (env で切替)

- **smart auto (default)**: cwd が git repo の main repo の workspace のみ自動 worktree 化
- **opt-in**: `CMUX_WORKTREE_DAEMON_OPT_IN_PREFIX="wt:"` 等を export すると、title 先頭一致のみ通過
- **完全自動**: 該当 mode なし (smart auto で git repo を判定するため、非 git workspace は自然 skip)
- **kill switch**: `CMUX_WORKTREE_DAEMON_DISABLE=1` で daemon を no-op に切替

### 運用前提・既知 limitation

- **LaunchAgent 経由運用が前提**: plist の `KeepAlive=true` + `ThrottleInterval=10` で daemon クラッシュ時に macOS launchd が自動再起動する。foreground 実行 (`bash scripts/runtime/cmux-worktree-daemon.sh`) は test only — `tail -F` は cmux app 終了後も続くため、必ず手動 kill が必要。
- **`tail -F` 起動時点で events.jsonl 末尾から開始** (`-n 0`): daemon 起動前の workspace は対象外。cmux 起動時の既存 workspaces は対象外で意図通り。
- **events.jsonl rotation 対応**: `tail -F` は cmux による rotation (`events.jsonl.1` への移動) に追従する。
- **multi-instance 防止**: LaunchAgent (macOS launchd) が 1 instance を保証。foreground で複数起動すると重複 event 処理 + branch 競合エラーが起きるため、test 後は `pkill -f cmux-worktree-daemon` で確実に kill する。
- **path-special name の reject**: `payload.title` が `.` / `..` / `.git` / 先頭ドット (`.foo` 等) の場合は sanitize で空文字に reject される (path traversal + dotfile 衝突防止)。
- **bare repo / worktree 内 cwd**: bare repo (`--is-bare-repository=true`) は skip、worktree 内 cwd は `git_dir != git_common_dir` で skip して再帰防止。
- **既存 worktree との区別**: 正規 worktree は `git worktree list --porcelain` で検査して skip、orphan directory (SIGTERM 中断等で残った壊れた path) は警告ログ + skip で手動 cleanup を要求。
