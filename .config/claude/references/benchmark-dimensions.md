# ベンチマーク次元定義

> Setup Health Benchmark の6次元の定義、計算方法、閾値。
> `scripts/benchmark/setup_health.py` で計算される。

## 次元一覧

| 次元 | 計算方法 | 良好 | 警告 | 危険 |
|------|---------|------|------|------|
| Error Rate | 直近7日のエラー数/セッション数 | < 1.0 | 1.0-3.0 | > 3.0 |
| Recovery Rate | エラー回復数/総エラー数 | > 0.7 | 0.4-0.7 | < 0.4 |
| Quality Score | 品質違反頻度 (低いほど良い) | < 5/週 | 5-15/週 | > 15/週 |
| Skill Health | スキル実行平均スコア | > 0.6 | 0.4-0.6 | < 0.4 |
| Improvement Velocity | CQS トレンド | CQS > 0 | CQS = 0 | CQS < 0 |
| Review Acceptance | レビュー指摘受入率 | > 0.7 | 0.4-0.7 | < 0.4 |

## データソース

| 次元 | JSONL ファイル |
|------|---------------|
| Error Rate | `learnings/errors.jsonl`, `metrics/session-metrics.jsonl` |
| Recovery Rate | `metrics/session-metrics.jsonl` |
| Quality Score | `learnings/quality.jsonl` |
| Skill Health | `learnings/skill-executions.jsonl` |
| Improvement Velocity | `experiments/experiment-registry.jsonl` (CQS) |
| Review Acceptance | `learnings/review-feedback.jsonl` |

## スコアリング

全次元は 0.0-1.0 に正規化される。Overall は6次元の平均値。

## 使用方法

```bash
# テキストレポート
python .config/claude/scripts/benchmark/setup_health.py

# JSON 出力
python .config/claude/scripts/benchmark/setup_health.py --json
```

`/improve` ダッシュボードの一部として使用される。
