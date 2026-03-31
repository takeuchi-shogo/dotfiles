# cmux マルチエージェントオーケストレーション設計

## 概要

cmux-team プラグインをベースに、コーディネーター（ユーザー対話中の Claude Code）が cmux ペインで複数 Worker を起動・指揮する仕組み。サブエージェント（Agent tool）と併用し、タスクの性質に応じて自動振り分けする。

## ユースケース

1. **並列実装**: 1つの大きな機能を分割し、複数 Worker に並列実装させる（API + Frontend + Test 同時進行）
2. **マルチモデル比較**: 同じタスクを Claude Code / Codex / Gemini に投げて結果を比較・統合
3. **常駐ワーカープール**: タスクキューに入れたものを自動的に拾って処理

## アーキテクチャ

```
ユーザー
  ↓ 指示
Master (この Claude Code セッション)
  ├── サブエージェント判定? ──→ Agent tool (従来通り)
  │   (短時間・構造化結果・Claude only)
  │
  └── cmux Worker 判定? ──→ Worker Router (/dispatch)
      ├── Claude Code Worker  (cmux ペイン + worktree)
      ├── Codex Worker        (cmux ペイン、codex exec)
      └── Gemini Worker       (cmux ペイン、gemini CLI)
```

### 判定フロー (Worker Router)

```
タスク受信
  ↓
[1] 5分以内 & 構造化結果が必要? → サブエージェント
[2] Codex/Gemini が必要? → cmux Worker (該当モデル)
[3] 30分以上 or 人間介入可能性? → cmux Worker (Claude Code)
[4] 5+ 並列? → cmux Worker
[5] それ以外 → サブエージェント (デフォルト)
```

既存の `rules/codex-delegation.md` と `rules/gemini-delegation.md` の判定基準を組み込む。新ルールではなく、既存ルールに「どこで実行するか」の層を追加する。

### 物理配置 (cmux ワークスペース)

```
workspace:main  → Master (ユーザー対話)
workspace:w-1   → Claude Code Worker (worktree 隔離)
workspace:w-2   → Codex Worker
workspace:w-3   → Gemini Worker
...必要に応じてスケール
```

Conductor と Worker は別ワークスペースに配置する（同一 workspace に詰め込むとペインが狭くなり `cmux send`/`read-screen` が破損するため）。

## 追加コンポーネント（3つだけ作る）

### 1. Worker Router スキル (`/dispatch`)

タスクを受けて「サブエージェント or cmux Worker（どのモデル）」を判定し起動する。

```
/dispatch "APIエンドポイントを実装して"
  → 30分超の実装 → cmux Claude Code Worker

/dispatch "このコードのセキュリティリスクを深く分析して"
  → 深い推論 → cmux Codex Worker

/dispatch "この3ファイルの型定義を確認して"
  → 5分以内の調査 → 従来のサブエージェント
```

### 2. Worker 起動スクリプト (`launch-worker.sh`)

モデル別のペイン起動を抽象化する。

```bash
./launch-worker.sh --model claude --task "API実装" --worktree feature/api
./launch-worker.sh --model codex --task "セキュリティ分析"
./launch-worker.sh --model gemini --task "コードベース全体分析"
```

処理内容:
1. `cmux new-workspace` でワークスペース作成
2. worktree 作成（Claude Code Worker の場合）
3. モデル別の起動コマンド実行
4. Trust 確認待ち（Claude Code の場合）
5. プロンプト送信
6. ワークスペースID を返す

### 3. 結果回収ユーティリティ (`collect-result.sh`)

Worker の完了検出 + 結果テキスト抽出を共通化する。

```bash
./collect-result.sh --workspace w-1 --timeout 1800
```

処理内容:
1. `read-screen --scrollback 500` で定期ポーリング
2. 完了パターン検出（プロンプト再出現 / 完了シグナル / タイムアウト）
3. 結果テキストを整形して返す
4. 完了時に `cmux notify` でコーディネーターに通知

## 通信プロトコル

### コーディネーター → Worker（指示）

```bash
cmux send --workspace "$WS" --surface surface:1 "${PROMPT}"
cmux send-key --workspace "$WS" --surface surface:1 return
```

プロンプトには以下を含める:
- タスク内容
- 期待する出力形式（ファイルパス or テキスト）
- 完了時のシグナル文字列（例: `===DONE===`）

### Worker → コーディネーター（結果報告）

2段構え:

1. **ファイルベース（プライマリ）**: Worker が `/tmp/cmux-results/{workspace-id}.md` に結果を書く → コーディネーターが読む
2. **screen ベース（フォールバック）**: ファイルが書けない場合に `read-screen` で回収

```
/tmp/cmux-results/
  ├── w-1.md    ← Claude Code Worker の結果
  ├── w-2.md    ← Codex Worker の結果
  └── w-3.md    ← Gemini Worker の結果
```

### ライフサイクル状態遷移

```
PENDING → LAUNCHING → RUNNING → COMPLETED
                        ↓
                      FAILED → RETRY (最大2回)
                        ↓
                      ESCALATE (人間に通知)
```

- **LAUNCHING**: ペイン作成〜プロンプト送信完了まで
- **RUNNING**: ポーリング監視中。`cmux set-progress` でサイドバーに進捗表示
- **COMPLETED**: 結果ファイル検出 or 完了シグナル検出
- **FAILED**: タイムアウト or エラーパターン検出 → 自動リトライ
- **ESCALATE**: リトライ上限超え → `cmux notify` + macOS 通知

## 通信ログ

全てのエージェント間通信を JSONL 形式でログに残す。誰が・誰に・何を送ったかを追跡可能にする。

### ログファイル

```
/tmp/cmux-dispatch-log/{session-id}.jsonl
```

セッション単位で1ファイル。JSONL 追記方式。

### ログエントリ形式

```jsonl
{"ts":"2026-03-30T10:15:00Z","from":"master","to":"w-1","type":"dispatch","model":"claude","task":"APIエンドポイント実装","workspace":"workspace:w-1"}
{"ts":"2026-03-30T10:15:05Z","from":"master","to":"w-1","type":"prompt","body":"以下の仕様に従って...","truncated_at":500}
{"ts":"2026-03-30T10:15:05Z","from":"master","to":"w-2","type":"dispatch","model":"codex","task":"セキュリティ分析","workspace":"workspace:w-2"}
{"ts":"2026-03-30T10:32:00Z","from":"w-1","to":"master","type":"result","status":"completed","result_file":"/tmp/cmux-results/w-1.md"}
{"ts":"2026-03-30T10:45:00Z","from":"w-2","to":"master","type":"result","status":"failed","error":"timeout"}
{"ts":"2026-03-30T10:45:01Z","from":"master","to":"w-2","type":"retry","attempt":1}
```

### フィールド定義

| フィールド | 説明 |
|-----------|------|
| `ts` | ISO 8601 タイムスタンプ |
| `from` | 送信元（`master` or ワーカーID） |
| `to` | 送信先（`master` or ワーカーID） |
| `type` | イベント種別: `dispatch`, `prompt`, `result`, `retry`, `escalate`, `state_change` |
| `model` | 使用モデル（dispatch 時） |
| `task` | タスク概要（dispatch 時） |
| `body` | 送信内容（prompt 時。長文は `truncated_at` で切り詰め） |
| `status` | 結果ステータス（result 時） |
| `error` | エラー内容（failed 時） |

### 記録タイミング

- `launch-worker.sh`: dispatch + prompt エントリを記録
- `collect-result.sh`: result エントリを記録
- 状態遷移時: state_change エントリを記録
- リトライ時: retry エントリを記録

### ログユーティリティ

```bash
# ログ閲覧（直近セッション）
./scripts/runtime/dispatch-log.sh show

# 特定ワーカーのログをフィルタ
./scripts/runtime/dispatch-log.sh filter --worker w-1

# サマリ（タスク数・成功率・平均所要時間）
./scripts/runtime/dispatch-log.sh summary
```

## 既存ハーネスとの統合

### 委譲ルールとの接続

```
rules/codex-delegation.md  ──→ Worker Router が参照
rules/gemini-delegation.md ──→ Worker Router が参照
references/subagent-vs-cmux-worker.md ──→ サブエージェント/cmux の分岐基準
```

### 既存スキルとの関係

| 既存スキル | cmux Worker 版での位置づけ |
|-----------|-------------------------|
| `/autonomous` | 長時間タスクは cmux Worker に置き換え可能。併存 |
| `/research` | マルチモデル並列リサーチで cmux Worker 活用の選択肢が増える |
| `/review` | サブエージェント並列レビューのまま（短時間・構造化結果向き） |
| `/debate` | 現状の CLI 呼び出しでも十分。cmux Worker は optional |
| `/dev-cycle` | Issue→実装→PR の長時間フロー → cmux Worker 向き |

**原則: 既存スキルは変えない**。`/dispatch` が新エントリポイント。スキル内部から cmux Worker を使いたい場合は `launch-worker.sh` を呼ぶ。

### hooks との連携

- **起動時**: `launch-worker.sh` が `cmux set-status` でサイドバーにワーカー状態表示
- **完了時**: `collect-result.sh` が `cmux notify` で通知
- **Worker 内の Claude Code**: CLAUDE.md 経由で既存 hooks（golden-check, completion-gate 等）が自動適用

## ファイル配置

```
.config/claude/skills/dispatch.md          ← Worker Router スキル
scripts/runtime/launch-worker.sh           ← Worker 起動スクリプト
scripts/runtime/collect-result.sh          ← 結果回収ユーティリティ
scripts/runtime/dispatch-log.sh            ← 通信ログユーティリティ
scripts/lib/dispatch_logger.sh             ← ログ記録共通関数
references/subagent-vs-cmux-worker.md      ← 判定基準（作成済み）
```

## 前提条件

- cmux インストール済み（Ghostty ベースのターミナル）
- cmux-team プラグイン (`hummer98/cmux-team`) インストール済み
- using-cmux プラグイン (`hummer98/using-cmux`) インストール済み
- Codex CLI / Gemini CLI がインストール済み（該当 Worker を使う場合）

## サブエージェントとの比較サマリ

詳細は `references/subagent-vs-cmux-worker.md` を参照。

- **デフォルトはサブエージェント**: 起動コスト・コンテキスト共有・結果受け渡しで優位
- **cmux Worker に昇格する条件**: 長時間タスク、マルチモデル、高並列、人間介入が必要な場合
- 両者は排他ではなく併用。Worker Router が自動振り分け
