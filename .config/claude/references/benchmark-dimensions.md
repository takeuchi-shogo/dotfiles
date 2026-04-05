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

### Supporting Indicators（6D overall に含まない補助指標）

| Indicator | Source |
|-----------|--------|
| Telemetry Completeness | `learnings/telemetry.jsonl` — 必須 type の観測率 |
| Friction Visibility | `learnings/friction-events.jsonl` — 摩擦パターン検出数 |
| Tier Alignment | `metrics/skill-tier-shadow.jsonl` — 宣言 tier と使用実態の一致率 |

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

## Retroactive Scoring

新スキル導入時やデータ不足時に、過去の実行記録からベースラインスコアを遡及算出する。

```bash
# 特定スキルのバッチスコアリング
python .config/claude/scripts/benchmark/retroactive_scorer.py --skill improve

# 全スキル
python .config/claude/scripts/benchmark/retroactive_scorer.py --all

# プレビュー（書き込みなし）
python .config/claude/scripts/benchmark/retroactive_scorer.py --all --dry-run
```

スコアは `skill-executions.jsonl` に `scored_by: "retroactive"` として追記される。
閾値・信号分類は `references/scoring-config.json` の `outputSignal` を参照する。
