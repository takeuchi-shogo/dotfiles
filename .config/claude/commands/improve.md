---
allowed-tools: Bash(cat *), Bash(wc *), Bash(ls *), Bash(jq *), Bash(head *)
argument-hint: "[--evolve] [--single-change|--multi-change] [--dry-run] [ultrathink]"
description: AutoEvolve 改善サイクルをオンデマンドで実行し、蓄積データから改善提案を生成する
---

# AutoEvolve Improvement Cycle

蓄積されたセッションデータを分析し、改善提案を生成する。

## 引数

`$ARGUMENTS` で受け取るフラグ:

- `--evolve`: イテレーティブループを起動 (policy Rule 16-20 の制約下、worktree 隔離必須)
- `--single-change` (default) / `--multi-change`: 1 サイクルあたりの変更箇所数
- `--dry-run`: 提案生成のみ。Step 4 (実行) を skip し提示のみで終了
- `ultrathink`: 推論深度を引き上げる

引数解釈は autoevolve-core サブエージェントに委譲する (Step 2 / Step 5 で `$ARGUMENTS` をそのまま渡す)。

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

`autoevolve-core` エージェントをサブエージェントとして起動し、Analyze + Garden フェーズを実行させる:

- `learnings/errors.jsonl` — エラーパターンの頻度分析
- `learnings/quality.jsonl` — 品質違反パターンの分析
- `learnings/patterns.jsonl` — 成功パターンの集計
- `metrics/session-metrics.jsonl` — プロジェクト別の統計

autoevolve-core エージェントに以下を指示する:

> `~/.claude/agent-memory/` のデータを分析し（Analyze フェーズ）、知識ベースを整理し（Garden フェーズ）、`insights/analysis-YYYY-MM-DD.md` にレポートを生成してください。繰り返しエラー、頻出品質違反、プロジェクト別統計、改善提案、重複排除、昇格候補を含めてください。
>
> 起動フラグ: `$ARGUMENTS`
>
> 注意:
>
> - `errors.jsonl` は producer 不在で stale な可能性が高い (改善ポリシー参照)。欠損 / 24h 以上 stale なら主入力から除外し、`quality.jsonl` / `patterns.jsonl` / `friction-events.jsonl` / `session-metrics.jsonl` で代替する
> - フラグ解釈: `--dry-run` が含まれる場合、Step 4 (実行) は skip され、提示のみで終わることを認識して提案を生成する
> - `ultrathink` が含まれる場合、推論深度を引き上げる

## Step 3: 統合レポート表示

Step 2 の結果を以下の形式でユーザーに表示する:

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

## Step 4: 承認と実行

`$ARGUMENTS` に `--dry-run` が含まれる場合は本ステップを skip し、「dry-run のため適用は行いません」と表示してサイクルを終える。

それ以外の場合、ユーザーに改善提案を提示し、承認を求める:

1. 各提案に番号を振る
2. 「承認する提案の番号を入力してください（例: 1,3,5 / all / none）」と聞く
3. 承認された提案のみ実行する:
   - **MEMORY.md 追記**: 該当プロジェクトの MEMORY.md にエントリを追加
   - **ルール追加**: `.config/claude/rules/` に新規ルールファイルを作成
   - **スキル改善**: 該当スキルファイルを編集
   - **error-fix-guides 追加**: `references/error-fix-guides.md` にエントリを追加
4. 実行結果を報告する

## Step 5: AutoEvolve 設定改善提案（オプション）

Step 4 の実行完了後、ユーザーに以下を確認する:

> 「設定の自動改善提案も生成しますか？（autoevolve-core の Improve フェーズを起動）」

### ユーザーが承認した場合

`autoevolve-core` エージェントをサブエージェントとして起動し、Improve フェーズを指示する:

> `references/improve-policy.md` を読み込み、今回の分析結果（insights/analysis-YYYY-MM-DD.md）を基に設定の自動改善を実行してください。
>
> 制約:
>
> - `autoevolve/*` ブランチを作成して作業する
> - 変更は最大 3 ファイルまで
> - 変更後にテストを実行し、パスすることを確認する
> - 完了後、diff と変更レポートを提示する

### autoevolve-core 完了後

1. autoevolve-core エージェントが提示した diff とレポートをユーザーに表示する
2. ユーザーに以下の選択肢を提示する:
   - **承認**: `autoevolve/*` ブランチを master にマージする
   - **修正**: 指摘箇所を修正してから再度提示する
   - **却下**: ブランチを削除し、変更を破棄する
3. 選択に応じて実行し、結果を報告する

### ユーザーが拒否した場合

Step 5 の結果をもって改善サイクルを完了する。

## 重要な注意事項

- MEMORY.md やルール/スキルへの変更はユーザー承認なしに絶対に行わない
- 分析データ（learnings/）は読み取り専用 — 変更しない
- 出力（insights/）への書き込みのみ自動で行う
- データが不十分な場合は無理に分析せず、素直に報告する
