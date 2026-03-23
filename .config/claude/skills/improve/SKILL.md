---
name: improve
description: >
  AutoEvolve のオンデマンド改善サイクルを実行。学習データの分析 → 知識整理 → 設定改善提案を一括で行う。/improve で起動。
  Triggers: '/improve', '改善提案', '設定見直し', 'autoevolve', 'optimize setup'.
  Do NOT use for: 外部記事の統合（use /absorb）、スキル個別の改善（use /skill-creator）、コードベース監査（use /audit）。
allowed-tools: Read, Bash, Grep, Glob, Agent
metadata:
  pattern: pipeline
---

# AutoEvolve On-Demand Improvement Cycle

蓄積されたセッション学習データを分析し、Claude Code の設定（エージェント、スキル、ルール、hook）の
改善提案を自律的に生成するオンデマンドサイクル。

## オプション

- `--evolve`: イテレーティブ進化ループを実行（デフォルト: 通常の 1 パス分析）
- `--iterations N`: ループ回数（デフォルト: 3、最大: 5）
- `--skills skill1,skill2`: 対象スキルを手動指定（デフォルト: degraded/failing スキル）
- `--single-change`: 1イテレーション1変更に制限（スキル最適化のデフォルト）。Changelog を自動生成

## 処理手順

以下の手順を **必ず順番に** 実行すること。
各ステップの詳細は instructions/ 配下のファイルを Read して参照する。

### Step 0-3: データ収集

**詳細: `instructions/data-collection.md` を Read**

0. **トレースレビュー（Open Coding）** — 直近トレースをユーザーと確認し `open_coding_notes` を取得
1. **データ可用性チェック** — learnings/*.jsonl とメトリクスの存在確認。全て未作成なら終了
2. **実験トラッカーの確認** — pending/merged 実験の状態確認
3. **マージ済み実験の効果測定** — 効果測定対象があれば測定実行

### Step 4-5: 分析・知識整理

**詳細: `instructions/analysis-gardening.md` を Read**

4. **4 カテゴリ並列分析** — errors / quality / agents / skills / environment を Agent で並列分析
5. **知識整理とクロスカテゴリ分析** — 重複排除・陳腐化チェック・クロスカテゴリ相関・昇格候補特定

### Step 6-7: 提案・レポート

**詳細: `instructions/proposals-report.md` を Read**

6. **カテゴリ別改善提案の生成** — 改善機会のあるカテゴリで autoevolve-core (phase: improve) を起動
7. **レビューレポートの生成** — 全ステップの結果を統合しユーザーに報告

## 注意事項

- データが少ない段階（初期）では無理に分析しない。「データ不足」は正常な状態
- experiment-tracker.py が未配置の場合は Step 2-3 をスキップして続行する
- 各エージェントの実行結果が空・エラーの場合は、その旨をレポートに記載して続行する
- このスキルは **読み取り + 分析 + 提案** が目的。master への直接変更は行わない

## --evolve モード

通常の Step 0-7 完了後にイテレーティブ進化ループを実行する。
対象スキルに対して Proposer → Builder → A/B 検証 → Verdict を繰り返し、スキルを自動改善する。

**詳細: `instructions/evolve-mode.md` を Read**

## Skill Assets

- 改善レポートテンプレート: `templates/improvement-report.md`
- 実験ログテンプレート: `templates/experiment-log.md`
- 分析カテゴリ判断基準: `references/analysis-categories.md`

## Anti-Patterns

| NG | 理由 |
|----|------|
| データなしで改善提案する | 学習データ・セッションログに基づかない提案は的外れになる |
| 1サイクルで10件以上変更する | 消化不良になる。1サイクル最大3ファイルの制約を守る |
| 改善を検証せずに適用する | A/B テストなしの変更は劣化リスクがある |
