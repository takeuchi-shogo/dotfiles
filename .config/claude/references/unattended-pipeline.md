# Unattended Pipeline (Stripe Minions パターン)

> Stripe の Minions: Slack でタスク受信 → devbox 起動(10秒) → Blueprint 実行 → PR 作成 → 通知。
> 週 1,300+ PR を無人で生成・マージ。人間の役割は「コード記述」から「コードレビュー」にシフト。

---

## 概要

Stripe Minions は E2E の無人パイプラインアーキテクチャ:

1. **タスク受信**: Slack メッセージまたは内部キューからタスクを取得
2. **環境構築**: 隔離された devbox を 10 秒で起動
3. **Blueprint 選択**: タスク種別を分析し、最適なワークフロー DAG を選択
4. **実行ループ**: Blueprint のノードに沿ってエージェントが自律実行
5. **PR 作成**: 成果物を PR として提出
6. **通知**: 完了状態を人間に通知（レビュー待ちキューに入る）

**核心**: 人間はコードを書かない。レビューだけする。

---

## 当セットアップでの実現

```
/autonomous {task}
  → Blueprint 選択（タスク分析から最適な blueprint を推薦）
  → Worktree 隔離
  → claude -p ヘッドレスセッション × N
  → Graduated Completion 判定
  → PR 作成（gh pr create）
  → 通知（macOS notification）
```

### 実行フロー詳細

```
┌─────────────────────────────────────────────────┐
│  /autonomous {task}                              │
│                                                  │
│  1. Analyze: タスク種別を判定                    │
│  2. Blueprint 選択: references/blueprints/ から  │
│  3. Plan: task_list.md + executor-prompt.md 生成 │
│  4. Worktree 作成（並列時）                      │
│  5. run-session.sh 起動                          │
│     ├─ claude -p × N セッション                  │
│     ├─ progress.md に進捗記録                    │
│     └─ Graduated Completion 判定                 │
│  6. PR 作成 or エラーレポート                    │
│  7. macOS 通知                                   │
└─────────────────────────────────────────────────┘
```

---

## Blueprint との統合

### Step 1: タスク分析と Blueprint 推薦

`/autonomous` の Analyze ステップでタスクのタイプを判定し、`references/blueprints/` から最適な blueprint を選択する:

| タスク種別 | Blueprint | 特徴 |
|-----------|-----------|------|
| バグ修正 | `bug-fix.yaml` | investigate → fix → test ループ |
| 新機能 | `feature.yaml` | plan → implement → test → lint |
| リファクタリング | `refactor.yaml` | snapshot → refactor → verify |

### Step 2: executor-prompt.md の構成

Blueprint のノードに従って executor-prompt.md を構成する:

1. Blueprint の `nodes` を順にプロンプトに展開
2. 各ノードの `tools` を `--allowedTools` に反映
3. `on_failure` ポリシーを指示に含める
4. `completion` ポリシー（strict / graduated）を環境変数に設定

### Step 3: ツールスコープの反映

Blueprint の各エージェントノードで宣言された `tools` を `--allowedTools` にマッピング:

```bash
# Blueprint のツール定義から自動生成
claude -p "$PROMPT" \
  --allowedTools "Read,Edit,Write,Grep,Glob" \
  --max-cost "$BUDGET"
```

不要なツールの使用を抑制し、トークン消費を最小化する。

---

## PR Delivery Step

`run-session.sh` の最後に PR 作成ステップを追加。

### PR 作成条件

| 状態 | アクション | PR タイトル |
|------|-----------|------------|
| 全タスク完了 (Full) | PR 作成 + 通知 | `[autonomous] {task-name}` |
| 部分完了 (Partial) | `[WIP]` PR + ハンドバックレポート + 通知 | `[WIP] [autonomous] {task-name}` |
| 着手不能 (Blocked) | PR なし、エラーレポート + 通知 | ― |

### PR テンプレート

`templates/pr-template.md` を使用して PR body を生成。含まれる情報:

- **Summary**: タスクの概要
- **Changes**: 変更差分の統計
- **Automated by**: Blueprint 名、セッション数、完了状態
- **Task Progress**: タスクリストの進捗
- **Handback Report**: 未完了タスクの詳細（Partial 時）

### 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `CREATE_PR` | `false` | `true` で PR 作成を有効化 |
| `COMPLETION_MODE` | `strict` | `graduated` で部分完了を許容 |
| `PR_TITLE_PREFIX` | `[autonomous]` | PR タイトルのプレフィックス |
| `BLUEPRINT` | `default` | 使用した Blueprint 名 |

---

## 通知

### 完了時通知 (macOS)

```bash
osascript -e 'display notification "{task}: {status}" with title "Autonomous Complete" sound name "Glass"'
```

### 通知に含まれる情報

- タスク名
- 完了状態 (Full / Partial / Blocked)
- 失敗時: エラーサマリー

### 将来拡張

| チャネル | 実装方法 | 優先度 |
|---------|---------|--------|
| macOS notification | `osascript` (実装済み) | 現在 |
| Slack webhook | `curl -X POST` | 将来 |
| GitHub Actions trigger | `gh workflow run` | 将来 |
| メール | SMTP or SendGrid | 低 |

---

## 将来の拡張ポイント

### 1. 外部トリガー

現在は手動で `/autonomous {task}` を実行するが、将来的に:

- **Slack bot**: Slack メッセージを受信して `/autonomous` を起動
- **GitHub webhook**: Issue や Comment をトリガーに起動
- **CLI wrapper**: `autonomous-cli submit "task description"` でキューに追加

### 2. CI 統合

```yaml
# .github/workflows/autonomous.yml
on:
  workflow_dispatch:
    inputs:
      task:
        description: 'Task description'
jobs:
  autonomous:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          COMPLETION_MODE=graduated CREATE_PR=true \
          bash .config/claude/skills/autonomous/scripts/run-session.sh \
          .autonomous/${{ github.event.inputs.task }} 10 5.00
```

### 3. スケジューリング

```bash
# cron + /autonomous の組み合わせ
# 毎日深夜にバックログタスクを消化
0 2 * * * cd ~/project && COMPLETION_MODE=graduated CREATE_PR=true \
  bash ~/.claude/skills/autonomous/scripts/run-session.sh \
  .autonomous/daily-backlog 5 3.00
```

---

## Anti-Patterns

| NG パターン | 理由 | 代替策 |
|------------|------|--------|
| PR を自動マージする | 人間レビューが必須。品質保証の最終防衛線 | `auto-merge: false` を徹底 |
| 外部トリガーなしで unattended を走らせる | 意図しない実行、リソース浪費 | 明示的なトリガー（手動 or webhook）を必須に |
| タイムアウトなしで実行する | 無限ループ、コスト爆発のリスク | `MAX_SESSIONS` + `BUDGET` を必ず設定 |
| Blocked 状態で PR を作成する | 着手不能なら PR の意味がない | エラーレポートのみ |
| graduated をデフォルトにする | 品質低下のリスク | 明示的 opt-in |
| ハンドバックレポートを省略する | 次のアクションが取れなくなる | 必ず生成 |

---

## 関連ドキュメント

- `references/blueprint-pattern.md` — Blueprint パターンの設計
- `references/graduated-completion.md` — Graduated Completion パターン
- `references/blueprints/` — 具体的な Blueprint 定義
- `skills/autonomous/SKILL.md` — `/autonomous` スキル本体
- `skills/autonomous/scripts/run-session.sh` — セッションランナー
- `skills/autonomous/templates/pr-template.md` — PR テンプレート
