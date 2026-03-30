# Data Collection (Step 0-3)

## Step 0: トレースレビュー（Open Coding）

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

## Step 1: データ可用性チェック

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

for f in skill-executions.jsonl skill-benchmarks.jsonl; do
  path="$HOME/.claude/agent-memory/learnings/$f"
  if [ -f "$path" ]; then
    count=$(wc -l < "$path" | tr -d ' ')
    echo "✓ learnings/$f: ${count} 件"
  else
    echo "- learnings/$f: 未作成"
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

## Step 1.5: セッション outcome 統計

session-metrics.jsonl から outcome 分布を集計し、改善の方向性を判断する:

```bash
metrics="$HOME/.claude/agent-memory/metrics/session-metrics.jsonl"
if [ -f "$metrics" ]; then
  python3 -c "
import json, collections, os
outcomes = collections.Counter()
path = os.path.expanduser('~/.claude/agent-memory/metrics/session-metrics.jsonl')
with open(path) as f:
    for line in f:
        try:
            d = json.loads(line)
            outcomes[d.get('outcome', 'unknown')] += 1
        except json.JSONDecodeError:
            pass  # 破損行はスキップ
total = sum(outcomes.values())
if total > 0:
    print(f'セッション outcome 分布 (直近 {total} セッション):')
    for k, v in outcomes.most_common():
        print(f'  {k}: {v} ({v*100//total}%)')
else:
    print('outcome データなし')
"
else
  echo "session-metrics.jsonl 未作成（スキップ）"
fi
```

**分析への活用**:
- failure 率が 20% 超 → エラーパターン分析を優先（Step 4 で重点配分）
- recovery 率が高い → 自己修正は効いているが、根本原因の予防策を検討
- clean_success 率が 80% 超 → 安定期。新機能・効率改善にフォーカス

outcome 分布を `outcome_stats` として保持し、Step 4 の分析プロンプトに渡す。

## Step 2: 実験トラッカーの確認

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

## Step 2.5: 前回 Issue の棚卸し

前回の `/improve` で作成された GitHub Issue の実施状況を確認する:

```bash
gh issue list -R takeuchi-shogo/dotfiles --label autoevolve --json number,title,state,closedAt --jq '.[] | "\(.number) [\(.state)] \(.title)"'
```

- open Issue の一覧をユーザーに提示し、対応済み・未着手・不要を確認
- **実施率** (closed / total) を KPI として Step 7 のレポートに含める
- 前回提案が全て未対応の場合、「改善ループが停滞しています」と警告する

## Step 3: マージ済み実験の効果測定

Step 2 で効果測定対象が見つかった場合:

```bash
python3 "$HOME/.claude/scripts/experiment-tracker.py" measure-all
```

測定結果をユーザーに報告する。対象がない場合はスキップ。
