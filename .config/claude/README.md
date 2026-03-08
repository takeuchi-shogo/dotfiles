# Claude Code 設定

## AutoEvolve Architecture

[karpathy/autoresearch](https://github.com/karpathy/autoresearch) に着想を得た自律改善システム。
セッションデータを自動収集・分析し、設定自体を改善する提案を生成する。

### 全体像

```
セッション中                   セッション終了             オンデマンド / 定期
┌──────────────┐             ┌──────────────┐         ┌───────────────┐
│ error-to-    │──emit──┐    │ session-     │         │  /improve     │
│ codex.py     │        │    │ learner.py   │         │  コマンド     │
├──────────────┤        ▼    │  (flush)     │         └───┬───────────┘
│ golden-      │──emit──▶tmp │──▶ jsonl     │             │
│ check.py     │       file  └──────────────┘             ▼
└──────────────┘                                   ┌──────────────┐
                                                   │  autolearn   │→ insights/
                  ~/.claude/agent-memory/           ├──────────────┤
                  ├── learnings/*.jsonl             │  knowledge-  │→ 整理・昇格
                  ├── metrics/                     │  gardener    │
                  ├── insights/                    ├──────────────┤
                  └── logs/autoevolve.log           │  autoevolve  │→ autoevolve/*
                                                   └──────────────┘   ブランチ
                                                          ▲
                                                   improve-policy.md
                                                   (人間が方向を操る)
```

### 4層ループ

| 層                   | トリガー                      | やること                            |
| -------------------- | ----------------------------- | ----------------------------------- |
| **セッション**       | Stop / SessionEnd hook        | エラー・品質指摘を jsonl に自動記録 |
| **日次**             | daily-report skill            | 「今日の学び」セクションで振り返り  |
| **オンデマンド**     | `/improve` コマンド           | 分析 → 整理 → 設定改善提案          |
| **バックグラウンド** | `autoevolve-runner.sh` (cron) | 深夜に自律改善、朝レビュー          |

### コンポーネント

#### データ収集

| ファイル                     | 種別                   | 役割                                 |
| ---------------------------- | ---------------------- | ------------------------------------ |
| `scripts/session_events.py`  | 共有モジュール         | イベントの emit / flush / 永続化     |
| `scripts/session-learner.py` | hook (Stop/SessionEnd) | セッション終了時にデータをフラッシュ |
| `scripts/error-to-codex.py`  | hook (PostToolUse)     | エラー検出時に `_emit("error")`      |
| `scripts/golden-check.py`    | hook (PostToolUse)     | 品質違反時に `_emit("quality")`      |

#### 分析・整理

| ファイル                       | 種別    | 役割                                       |
| ------------------------------ | ------- | ------------------------------------------ |
| `agents/autolearn.md`          | agent   | パターン分析、プロジェクトプロファイル生成 |
| `agents/knowledge-gardener.md` | agent   | 重複排除、陳腐化除去、昇格提案             |
| `commands/improve.md`          | command | `/improve` で改善サイクルを手動実行        |

#### 設定最適化

| ファイル                       | 種別      | 役割                              |
| ------------------------------ | --------- | --------------------------------- |
| `agents/autoevolve.md`         | agent     | insights を元に設定変更を提案     |
| `references/improve-policy.md` | reference | 改善方針・制約（program.md 相当） |
| `scripts/autoevolve-runner.sh` | script    | バックグラウンド実行用ランナー    |

### データフロー

```
生データ (jsonl)
  → 3回以上出現 → insights/ に整理 (autolearn)
  → 確信度高 → MEMORY.md に追記 (knowledge-gardener が提案)
  → 汎用性高 → skill / rule に昇格 (人間が承認)
```

### セキュリティ境界

| Git 管理 (公開OK)                | ローカルのみ (非公開)       |
| -------------------------------- | --------------------------- |
| エージェント定義、スキル、ルール | learnings/\*.jsonl (生ログ) |
| hook ロジック、improve-policy.md | metrics/ (セッション統計)   |
| autoevolve の diff・履歴         | logs/ (実行ログ)            |

### 安全機構

- 設定変更は `autoevolve/*` ブランチで作業（master 直接変更禁止）
- 1サイクル最大3ファイルの変更制限
- 変更後に `uv run pytest tests/` でテスト通過を確認
- 人間レビュー後にのみ merge

### 使い方

```bash
# 改善サイクルを手動で回す
/improve

# 改善の方向性を変える
vim ~/.claude/references/improve-policy.md

# バックグラウンドで実行
~/.claude/scripts/autoevolve-runner.sh

# cron で毎日自動実行
# crontab -e
# 0 3 * * * ~/.claude/scripts/autoevolve-runner.sh

# 提案されたブランチを確認
git branch --list "autoevolve/*"
git diff master..autoevolve/YYYY-MM-DD

# ログを確認
cat ~/.claude/agent-memory/logs/autoevolve.log
```
