---
allowed-tools: Bash(cat *), Bash(wc *), Bash(ls *), Bash(jq *), Bash(head *)
description: AutoEvolve 改善サイクルをオンデマンドで実行し、蓄積データから改善提案を生成する
---

# AutoEvolve Improvement Cycle

蓄積されたセッションデータを分析し、改善提案を生成する。

## Step 1: データ可用性チェック

セッションメトリクスの件数を確認する:

!`wc -l ~/.claude/agent-memory/metrics/session-metrics.jsonl 2>/dev/null || echo "0"`

### 判定ルール

- **3セッション未満**: 「データが少なすぎます（N セッション）。もう少し使ってから再実行してください。」と報告して**終了**
- **3セッション以上**: Step 2 に進む

データファイルの存在確認:

!`ls -la ~/.claude/agent-memory/learnings/*.jsonl 2>/dev/null || echo "learnings ファイルなし"`
!`ls -la ~/.claude/agent-memory/metrics/*.jsonl 2>/dev/null || echo "metrics ファイルなし"`

## Step 2: AutoLearn 分析

`autolearn` エージェントをサブエージェントとして起動し、以下を分析させる:

- `learnings/errors.jsonl` — エラーパターンの頻度分析
- `learnings/quality.jsonl` — 品質違反パターンの分析
- `learnings/patterns.jsonl` — 成功パターンの集計
- `metrics/session-metrics.jsonl` — プロジェクト別の統計

autolearn エージェントに以下を指示する:

> `~/.claude/agent-memory/` のデータを分析し、`insights/analysis-YYYY-MM-DD.md` に分析レポートを生成してください。繰り返しエラー、頻出品質違反、プロジェクト別統計、改善提案を含めてください。

## Step 3: Knowledge Gardener 実行

`knowledge-gardener` エージェントをサブエージェントとして起動し、以下を実行させる:

- learnings 内の重複エントリの検出
- 陳腐化したエントリの検出
- 昇格候補の特定（MEMORY.md / skill / rule への追加提案）
- 知識ベースのヘルスチェック

knowledge-gardener エージェントに以下を指示する:

> `~/.claude/agent-memory/` の知識ベースを整理してください。重複排除、陳腐化検出、昇格候補の特定を行い、結果を報告してください。

## Step 4: 統合レポート表示

Step 2 と Step 3 の結果を統合し、以下の形式でユーザーに表示する:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AutoEvolve 改善レポート
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 繰り返しエラー トップ5

| # | エラー | 回数 | 関連コマンド |
|---|--------|------|-------------|
| 1 | ...    | ...  | ...         |

## 頻出品質違反

| ルール | 回数 | 主なファイル |
|--------|------|-------------|
| ...    | ...  | ...         |

## プロジェクト別の傾向

| プロジェクト | セッション数 | エラー傾向 | 品質傾向 |
|-------------|-------------|-----------|---------|
| ...         | ...         | ...       | ...     |

## 昇格候補

### MEMORY.md への追記提案
- [ ] ...

### スキル/ルール化の提案
- [ ] ...

### error-fix-guides への追加提案
- [ ] ...

## 知識ベース ヘルスチェック
- learnings サイズ: ...
- insights レポート数: ...
- MEMORY.md 行数: .../200
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 5: 承認と実行

ユーザーに改善提案を提示し、承認を求める:

1. 各提案に番号を振る
2. 「承認する提案の番号を入力してください（例: 1,3,5 / all / none）」と聞く
3. 承認された提案のみ実行する:
   - **MEMORY.md 追記**: 該当プロジェクトの MEMORY.md にエントリを追加
   - **ルール追加**: `.config/claude/rules/` に新規ルールファイルを作成
   - **スキル改善**: 該当スキルファイルを編集
   - **error-fix-guides 追加**: `references/error-fix-guides.md` にエントリを追加
4. 実行結果を報告する

## 重要な注意事項

- MEMORY.md やルール/スキルへの変更はユーザー承認なしに絶対に行わない
- 分析データ（learnings/）は読み取り専用 — 変更しない
- 出力（insights/）への書き込みのみ自動で行う
- データが不十分な場合は無理に分析せず、素直に報告する
