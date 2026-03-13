---
name: improve
description: AutoEvolve のオンデマンド改善サイクルを実行。学習データの分析 → 知識整理 → 設定改善提案を一括で行う。/improve で起動。
allowed-tools: Read, Bash, Grep, Glob, Agent
---

# AutoEvolve On-Demand Improvement Cycle

蓄積されたセッション学習データを分析し、Claude Code の設定（エージェント、スキル、ルール、hook）の
改善提案を自律的に生成するオンデマンドサイクル。

## 処理手順

以下の手順を **必ず順番に** 実行すること。

### Step 0: トレースレビュー（Open Coding）

人間がトレースを直接読む儀式。"Error Analysis: The Highest-ROI Activity in AI Engineering" に基づく。

```bash
python3 -c "
import sys, os
sys.path.insert(0, os.path.expanduser('~/.claude/scripts'))
from lib.trace_sampler import sample_recent_traces, sample_unclassified_traces, format_for_review
traces = sample_recent_traces(n=20)
print('=== 直近 20 トレース ===')
print(format_for_review(traces))
print()
unclassified = sample_unclassified_traces()
print(f'=== 未分類トレース: {len(unclassified)} 件 ===')
if unclassified[:5]:
    print(format_for_review(unclassified[:5]))
"
```

**ユーザーに以下を提示**:

1. 上記スクリプトの出力テーブルを表示
2. 「以下のトレースを確認してください。気になるパターン・驚き・想定外の動作はありますか？」と質問
3. ユーザーの回答を `open_coding_notes` として保持し、Step 4 の autoevolve-core プロンプトに渡す

**データがない場合またはユーザーがスキップを希望した場合**: 「自動分析のみ実行します」と報告し Step 1 に進む。

### Step 1: データ可用性チェック

学習データ・メトリクスが存在するか確認する:

```bash
echo "=== データ可用性チェック ==="
for f in errors.jsonl quality.jsonl patterns.jsonl; do
  path="$HOME/.claude/agent-memory/learnings/$f"
  if [ -f "$path" ]; then
    count=$(wc -l < "$path" | tr -d ' ')
    echo "✓ learnings/$f: ${count} 件"
  else
    echo "✗ learnings/$f: 未作成"
  fi
done

metrics="$HOME/.claude/agent-memory/metrics/session-metrics.jsonl"
if [ -f "$metrics" ]; then
  count=$(wc -l < "$metrics" | tr -d ' ')
  echo "✓ metrics/session-metrics.jsonl: ${count} 件"
else
  echo "✗ metrics/session-metrics.jsonl: 未作成"
fi

# 最新の分析レポート
latest=$(ls -t "$HOME/.claude/agent-memory/insights/analysis-"*.md 2>/dev/null | head -1)
if [ -n "$latest" ]; then
  echo "✓ 最新分析: $(basename "$latest")"
else
  echo "- 分析レポート: なし（初回実行）"
fi
```

**データが全て未作成の場合**: 「学習データがまだ蓄積されていません。セッションを重ねてから再実行してください。」と報告して **終了**。

### Step 2: 実験トラッカーの確認

過去の改善実験の状態を確認する:

```bash
if [ -f "$HOME/.claude/scripts/experiment-tracker.py" ]; then
  python3 "$HOME/.claude/scripts/experiment-tracker.py" status
else
  echo "experiment-tracker.py が未配置です（スキップ）"
fi
```

- **pending** な実験がある場合 → 一覧を表示し、ユーザーに状況を伝える
- **merged** だが効果測定未実施の実験がある場合 → Step 3 で測定する

### Step 3: マージ済み実験の効果測定

Step 2 で効果測定対象が見つかった場合:

```bash
python3 "$HOME/.claude/scripts/experiment-tracker.py" measure-all
```

測定結果をユーザーに報告する。対象がない場合はスキップ。

### Step 4: 4 カテゴリ並列分析

**Agent ツールで `autoevolve-core` (phase: analyze) エージェントを 4 並列起動** し、以下のカテゴリを同時に分析する:

| カテゴリ       | プロンプト概要                                                       |
| -------------- | -------------------------------------------------------------------- |
| **errors**     | `learnings/errors.jsonl` の繰り返しエラーパターン分析                |
| **quality**    | `learnings/quality.jsonl` の品質違反パターン分析                     |
| **agents**     | `metrics/session-metrics.jsonl` のエージェント効率分析               |
| **skills**     | `learnings/patterns.jsonl` + メトリクスからスキル改善候補の分析      |

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

**注意**: データが存在しないカテゴリはスキップする。存在するカテゴリのみ起動すること。

### Step 5: 知識整理とクロスカテゴリ分析

**Agent ツールで `autoevolve-core` (phase: garden) エージェントを起動** し、以下を実行させる:

```
以下のタスクを実行してください:

1. 重複排除: learnings/*.jsonl 内の重複エントリを検出・整理
2. 陳腐化チェック: 古い insights/learnings の棚卸し
3. クロスカテゴリ相関分析: Step 4 で生成された各カテゴリの分析結果を横断的に見て、
   カテゴリ間の関連性（例: 特定エラーと品質違反の相関）を特定
4. 昇格候補の特定: MEMORY.md やスキル/ルールへの昇格候補をリストアップ
5. ヘルスチェック: 知識ベースの健全性確認
```

### Step 6: カテゴリ別改善提案の生成

Step 4 の分析結果で **改善機会** が見つかったカテゴリに対して、
**Agent ツールで `autoevolve-core` (phase: improve) エージェントを起動** する。

各カテゴリに対して:

```
以下のカテゴリの改善を実施してください:

カテゴリ: {カテゴリ名}
分析結果: {Step 4 の該当カテゴリの分析サマリー}
クロス分析: {Step 5 のクロスカテゴリ相関で関連する知見}

improve-policy.md の方針に従い、autoevolve/* ブランチで変更を実装してください。
```

**注意**:
- 改善機会がないカテゴリは起動しない
- 複数カテゴリに改善機会がある場合は、優先度の高いものから順に起動する
- 1 サイクルで最大 3 ファイルの変更制約を守る（autoevolve-core エージェントの制約）

### Step 7: レビューレポートの生成

全ステップの結果を統合し、以下のフォーマットでユーザーに報告する:

```markdown
# AutoEvolve 改善サイクル レポート

## データ概況

- エラー: N 件
- 品質違反: N 件
- パターン: N 件
- セッション: N 件

## 実験ステータス

- 進行中: N 件
- 効果測定済み: N 件（成功: N / 改善なし: N）

## 分析結果サマリー

### エラーパターン

- {主要な発見}

### 品質違反パターン

- {主要な発見}

### エージェント効率

- {主要な発見}

### スキル改善

- {主要な発見}

### クロスカテゴリ相関

- {カテゴリ間の関連性}

## 知識ベースの健全性

- learnings サイズ: OK / 警告
- insights 数: N 件
- MEMORY.md: N 行 / 200行制限
- 昇格候補: N 件

## 改善提案

### 実施済み（ブランチ作成済み）

- `autoevolve/YYYY-MM-DD-{topic}`: {変更内容}
  - 根拠: {データに基づく理由}
  - 次のアクション: `git merge` or レビュー

### 昇格候補（ユーザー承認待ち）

- [ ] {MEMORY.md への追記提案}
- [ ] {スキル/ルール化の提案}

## 次回への申し送り

- {次回の /improve で優先すべき事項}
```

## 注意事項

- データが少ない段階（初期）では無理に分析しない。「データ不足」は正常な状態
- experiment-tracker.py が未配置の場合は Step 2-3 をスキップして続行する
- 各エージェントの実行結果が空・エラーの場合は、その旨をレポートに記載して続行する
- このスキルは **読み取り + 分析 + 提案** が目的。master への直接変更は行わない
