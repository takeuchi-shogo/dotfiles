# Analysis & Gardening (Step 4-5)

## Step 4: 4 カテゴリ並列分析

**Agent ツールで `autoevolve-core` (phase: analyze) エージェントを 4 並列起動** し、以下のカテゴリを同時に分析する:

| カテゴリ       | プロンプト概要                                                       |
| -------------- | -------------------------------------------------------------------- |
| **errors**     | `learnings/errors.jsonl` の繰り返しエラーパターン分析                |
| **quality**    | `learnings/quality.jsonl` の品質違反パターン分析                     |
| **agents**     | `metrics/session-metrics.jsonl` のエージェント効率分析               |
| **skills**     | `learnings/skill-executions.jsonl` + `learnings/skill-benchmarks.jsonl` からスキル健全性分析（トレンド/閾値判定/失敗パターン/クロスデータ相関） |
| **environment** | エラー・品質データを環境設計の観点から横断分析（4つの診断質問）      |

各エージェントへのプロンプトには以下を含める:

```
あなたは「{カテゴリ}」の分析担当です。

## ユーザーの Open Coding メモ（Step 0）

{open_coding_notes があれば挿入、なければ「メモなし（自動分析のみ）」}

このメモに含まれるパターンや驚きを、分析の優先事項として考慮してください。

~/.claude/agent-memory/ 配下のデータを分析し、以下を特定してください:
1. 繰り返しパターン（3回以上）
2. 改善機会
3. 優先度付けされた提案

分析結果を insights/analysis-{today}-{カテゴリ}.md に出力してください。
```

**environment カテゴリのプロンプト（Harness Audit Framework）:**

"The Harness Is Everything" 記事の環境監査フレームワークに基づく4つの診断質問で分析する。
各質問に対して、learnings データから具体的な証拠を挙げて回答すること。

````
あなたは「environment（環境設計）」の分析担当です。

## ユーザーの Open Coding メモ（Step 0）

{open_coding_notes があれば挿入、なければ「メモなし（自動分析のみ）」}

## 4つの診断質問

以下の各質問に対して、~/.claude/agent-memory/ のデータを横断的に分析し、
具体的な証拠（ファイル名、エラーメッセージ、発生回数）とともに回答してください。

### Q1: アクセス不能な情報
エージェントが必要としているが、現在アクセスできない情報は何か？
（繰り返し同じ調査をしている、外部システムの情報が必要、等）

### Q2: 欠落したフィードバックループ
ミスが伝播してから検出されているケースはあるか？
どの時点でフィードバックがあればミスを即座にキャッチできたか？
（例: edit 時の linter、test 時のカバレッジ、review 時のチェックリスト）

### Q3: コンテキスト汚染
無関係な情報でコンテキストが汚染されているケースはあるか？
（大量の出力、古いセッション情報の残留、不要なファイルの読み込み）

### Q4: 機械的に強制すべき制約
現在エージェントの判断に依存しているが、hook や linter で
機械的に強制すべき制約はあるか？

## 出力フォーマット

各質問に対して:
- 証拠（データからの具体例、3件以上）
- 改善提案（具体的なファイル名と変更内容）
- 優先度（HIGH / MEDIUM / LOW）

insights/analysis-{today}-environment.md に出力してください。
````

**起動条件**: errors.jsonl が 20 件以上、かつ前回の environment 分析から 7 日以上経過している場合にのみ起動する。データが少ない段階では有意義な分析ができないため。

**注意**: データが存在しないカテゴリはスキップする。存在するカテゴリのみ起動すること。

**skills カテゴリの追加コンテキスト（EvoSkill 統合）:**

**ベンチマーク自動実行（Issue #30）:**

前回ベンチマークから 14 日以上経過している場合、分析前にトップ利用スキル（上位 5 件）のベンチマークを `skill-audit` で実行する。
ベンチマーク結果は `skill-benchmarks.jsonl` に追記される。
retire 判定のスキルがある場合、分析レポートで「retire 対応フロー」を提案する:
1. delta < -1.0 かつ実行 0 件 → 削除提案
2. delta < -1.0 かつ実行あり → 設計レビュー提案（`/spike`）
3. delta > 0 かつ実行 0 件 → トリガー条件見直し提案

分析前に以下を実行し、フィードバック履歴を取得:

```bash
python3 $HOME/.claude/scripts/experiment_tracker.py proposer-context --skill {target_skill}
```

取得した履歴をエージェントプロンプトに含める。`autoevolve-core.md` の Proposer Anti-Patterns (AP-1〜4) に従うこと。

**追加分析チェック（agents カテゴリ実行時）**:

- **Knowledge Embedding Ratio チェック**: 各エージェント定義（`agents/*.md`）のドメイン知識比率を概算。ドメイン知識（Symptom-Cause-Fix テーブル、コードパターン、failure modes、設計制約）が全体の 50% 未満のエージェントを改善候補として報告。Codified Context 論文: "Over half of each specification's content is project-domain knowledge rather than behavioral instructions"

## Step 5: 知識整理とクロスカテゴリ分析

**Agent ツールで `autoevolve-core` (phase: garden) エージェントを起動** し、以下を実行させる:

```
以下のタスクを実行してください:

1. 重複排除: learnings/*.jsonl 内の重複エントリを検出・整理
2. 陳腐化チェック: 古い insights/learnings の棚卸し
   + Dead Weight Scan: `references/dead-weight-scan-protocol.md` に従い、
     CLAUDE.md / references / hooks / agents の「まだ必要か？」を問う
3. クロスカテゴリ相関分析: Step 4 で生成された各カテゴリの分析結果を横断的に見て、
   カテゴリ間の関連性（例: 特定エラーと品質違反の相関）を特定
4. 昇格候補の特定: MEMORY.md やスキル/ルールへの昇格候補をリストアップ
5. ヘルスチェック: 知識ベースの健全性確認
```
