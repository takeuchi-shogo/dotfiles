# AutoEvolve — Claude Code 自律改善システム

**日付**: 2026-03-08
**着想**: [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
**ステータス**: 設計承認済み

## コンセプト

autoresearch の「人間が方針を書き、AIが自律的に改良ループを回す」パターンを Claude Code の設定改善に適用する。

```
Observe (収集) → Learn (蓄積) → Evolve (最適化)
```

## 構築フェーズ

- **Phase 1 (AutoLearn)**: セッションデータを自動収集・整理し、知識として蓄積
- **Phase 2 (AutoConfig)**: 蓄積された知識を元に、設定自体を自律的に最適化

## アーキテクチャ

```
┌─────────────────────────────────────────────────┐
│                  AutoEvolve                      │
│                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │ Observe  │───▶│  Learn   │───▶│  Evolve  │   │
│  │ (収集)   │    │ (蓄積)   │    │ (最適化) │   │
│  └──────────┘    └──────────┘    └──────────┘   │
│       ▲               │               │         │
│       │               ▼               ▼         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │ Sessions │    │ Knowledge│    │  Config  │   │
│  │ (日常)   │    │  Store   │    │ Changes  │   │
│  └──────────┘    └──────────┘    └──────────┘   │
└─────────────────────────────────────────────────┘
```

## 4つのループ層

| 層                   | トリガー                 | やること                             | Phase |
| -------------------- | ------------------------ | ------------------------------------ | ----- |
| **セッション**       | SessionEnd hook          | セッション中の学びを自動抽出・記録   | 1     |
| **日次**             | cron / daily-report 拡張 | 蓄積された学びを整理・統合・品質管理 | 1     |
| **バックグラウンド** | cron / 手動起動          | 学びを元に設定改善を探索・テスト     | 2     |
| **オンデマンド**     | `/improve` コマンド      | 明示的に改善サイクルを実行           | 1+2   |

## セキュリティ境界

| Git (公開OK)      | ローカルのみ (非公開)  |
| ----------------- | ---------------------- |
| エージェント定義  | API キー・トークン     |
| スキル・ルール    | プロジェクト固有の学び |
| hook ロジック     | ユーザー修正の生ログ   |
| 改善の diff・履歴 | セッションデータ       |

## Phase 1: AutoLearn

### 観察対象シグナル

| シグナル         | 検出方法                          | 例                                     |
| ---------------- | --------------------------------- | -------------------------------------- |
| ユーザー修正     | ユーザーが訂正した箇所            | 「tabs じゃなくて spaces で」          |
| レビュー指摘     | `/review` の結果                  | GP-004 違反が繰り返し検出              |
| 成功パターン     | タスク完了時のアプローチ          | 「このプロジェクトでは Vitest が正解」 |
| エラー→解決      | error-to-codex で解決したパターン | 「この型エラーは X が原因」            |
| コンテキスト効率 | トークン使用量                    | 「このエージェントは重すぎた」         |

### ストレージ構造

```
~/.claude/agent-memory/
├── learnings/
│   ├── corrections.jsonl        # ユーザー修正ログ
│   ├── patterns.jsonl           # 成功パターン
│   └── errors.jsonl             # エラー→解決マップ
├── insights/
│   ├── weekly-summary.md        # 週次で整理された知見
│   └── project-profiles/       # プロジェクトごとの特徴
│       └── {project-name}.md
└── metrics/
    └── session-metrics.jsonl    # セッション統計
```

### コンポーネント

| コンポーネント       | 種別              | 役割                                 |
| -------------------- | ----------------- | ------------------------------------ |
| `session-learner.py` | hook (SessionEnd) | セッション終了時に学びを自動抽出     |
| `autolearn`          | agent             | セッションデータを分析、jsonl に記録 |
| `knowledge-gardener` | agent             | 日次で知識を整理・重複排除・品質管理 |
| `/improve`           | command           | オンデマンドで学び→改善を実行        |
| daily-report 拡張    | skill 修正        | 日報に「今日の学び」セクション追加   |

### 知識の昇格パス

```
生ログ (jsonl)
  → 3回以上出現 → insights/ に整理
  → 確信度高 → memory/MEMORY.md に追記
  → 汎用性高 → skill / rule に昇格提案（人間が承認）
```

## Phase 2: AutoConfig

### autoresearch との対応

```
program.md (方針)    = improve-policy.md
train.py (改良対象)   = agents/, skills/, rules/, hooks
val_bpb (評価指標)    = 複合スコア
5分の訓練            = テストセッション or ドライラン
keep/discard         = ブランチ → 人間レビュー
```

### 評価指標

単一指標ではなく傾向で判断:

- ユーザー修正回数 ↓
- レビュー指摘数 ↓（同種の問題が減る）
- コンテキスト効率 ↓（同種タスクのトークン使用量）
- 人間の感覚（数値化できないもの）

### 安全機構

| 安全弁       | 仕組み                                               |
| ------------ | ---------------------------------------------------- |
| ブランチ隔離 | `autoevolve/*` ブランチに変更。master に直接触らない |
| 人間レビュー | diff で提示、承認しないと merge しない               |
| ロールバック | 変更前のコミットハッシュを記録                       |
| スコープ制限 | 1回の改善サイクルで変更は3ファイルまで               |
| ドライラン   | 変更前にバリデーション（構文チェック等）             |

### 改善サイクルのフロー

```
/improve or バックグラウンドトリガー
  → knowledge-gardener が insights/ を分析
  → autoevolve agent が改善案を生成（git worktree で隔離）
  → 人間に diff + 理由 + 期待効果を提示
  → 承認 → master に merge + commit
     却下 → 理由を記録（次回に反映）
```

## 構築ロードマップ

### Step 1: データ収集基盤（最小 MVP）

- `session-learner.py` (SessionEnd hook)
- `learnings/` ディレクトリ構造
- jsonl 記録フォーマット

### Step 2: 知識整理

- `autolearn` agent
- `knowledge-gardener` agent
- daily-report への「今日の学び」追加

### Step 3: オンデマンド改善

- `/improve` コマンド
- `autoevolve` agent
- `improve-policy.md`

### Step 4: 自律ループ

- cron 設定
- ブランチ管理自動化
- メトリクス傾向分析

## 設計原則

- **安全第一**: 設定変更は必ず人間レビューを経由
- **段階的構築**: Step 1 から小さく動かし、改良を加える
- **機密分離**: 生データはローカルのみ、整理済み知識のみ git 候補
- **既存資産活用**: continuous-learning, daily-report, memory システムを拡張

## バックグラウンド実行の設定

### cron 設定

```bash
# 毎日午前3時に実行
crontab -e
0 3 * * * ~/.claude/scripts/autoevolve-runner.sh >> ~/.claude/agent-memory/logs/autoevolve-cron.log 2>&1
```

### 手動バックグラウンド実行

```bash
# ドライラン（何が実行されるか確認）
~/.claude/scripts/autoevolve-runner.sh --dry-run

# 実際に実行
~/.claude/scripts/autoevolve-runner.sh &
```

### 結果確認

```bash
# ログ確認
cat ~/.claude/agent-memory/logs/autoevolve-cron.log

# 提案されたブランチの確認
cd ~/dotfiles && git branch --list "autoevolve/*"

# 変更内容の確認
git diff master..autoevolve/YYYY-MM-DD

# 承認してマージ
git checkout master && git merge autoevolve/YYYY-MM-DD

# 却下してブランチ削除
git branch -D autoevolve/YYYY-MM-DD
```
