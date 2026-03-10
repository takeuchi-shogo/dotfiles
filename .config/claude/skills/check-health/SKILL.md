---
name: check-health
description: ドキュメント鮮度・コード乖離・参照整合性をチェックする。M/Lタスクの Plan ステージで自動実行、または手動で /check-health で実行。
---

# Health Check

プロジェクトのドキュメント健全性を検査する。

## 実行内容

1. **コード・ドキュメント乖離チェック** — 直近のコミットでコード変更があったのにドキュメントが更新されていないか
2. **ドキュメント鮮度チェック** — 30日以上更新されていないドキュメントを検出
3. **参照整合性チェック** — ドキュメント内のファイル参照が実在するか

## 手順

### Step 1: チェック実行

以下の2つのスクリプトを Bash で実行する:

```bash
python3 $HOME/.claude/scripts/lifecycle/context-drift-check.py --commits 10 --json 2>/dev/null || true
```

```bash
python3 $HOME/.claude/scripts/lifecycle/doc-garden-check.py 2>/dev/null || true
```

### Step 2: 結果分析

- 警告がなければ「Health Check: 問題なし」と報告
- 警告があれば内容をサマリーし、必要に応じて `doc-gardener` エージェントへの委譲を提案

### Step 3: 深刻な問題への対応

参照が壊れている場合は `doc-gardener` エージェントに修正を委譲する:

```
Agent tool → subagent_type: doc-gardener
prompt: "doc-garden-check が以下の問題を検出しました: {warnings}. 修正してください。"
```
