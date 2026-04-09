# Anti-Goodhart チェックリスト

eval hill-climbing がメトリクスハック（Goodhart's Law）に陥っていないかを確認するためのガイド。

> "When a measure becomes a target, it ceases to be a good measure." — Goodhart's Law

## Quick Reference: gaming-detector Rules

| Rule | 検出対象 | 閾値 | 実装 |
|------|---------|------|------|
| 21 | スコア急上昇 | +5pp 以上 | `_detect_score_jump()` |
| 21-ext | eval タプル数減少 | -20% 以上 | `_detect_eval_suite_shrinkage()` |
| 21-ext | FM 検出率偏り | max/min > 4:1 | `_detect_fm_skew()` |
| 22 | 評価基準の自己変更 | proximity pattern | `_detect_self_referential_edit()` |
| 23 | 単一メトリクス | 1 metric only | `_detect_single_metric()` |
| 29 | accept rate 急上昇 | +20pp 以上 | `_detect_acceleration_guard()` |
| 30 | 選択的改善（1指標↑他↓） | +5pp/-3pp | `_detect_selective_improvement()` |

## Eval Suite Integrity 判定基準

### タプル数（eval_tuple_count）

| 状態 | 判定 | アクション |
|------|------|-----------|
| 前回比 ±20% 以内 | OK | なし |
| 前回比 -20% 以上減少 | WARNING | タプル削除の理由を確認 |
| 前回データなし | SKIP | baseline として記録 |

### FM 検出率偏り

| 状態 | 判定 | アクション |
|------|------|-----------|
| max/min 比 < 4:1 | OK | なし |
| max/min 比 >= 4:1 | SKEWED | 低検出率 FM の eval タプル追加を検討 |
| 検出率 0% の FM 存在 | WARNING | eval スイートから除外されている FM を確認 |

## スコア上昇時の確認フロー

1. **スコアが +3pp 以上上昇した？**
   - No → OK、通常の改善
   - Yes → Step 2 へ

2. **eval タプル数は減少していないか？**
   - 減少なし → Step 3 へ
   - 減少あり → Goodhart 疑義。タプル削除の理由を記録

3. **per-FM 検出率に大きな偏りはないか？**
   - max/min < 4:1 → Step 4 へ
   - max/min >= 4:1 → FM カバレッジ不足。低検出 FM のタプル追加

4. **assertion 数・テスト難易度は維持されているか？**
   - 維持 → 正当な改善と判断
   - 低下 → Goodhart 疑義。変更をレビュー

## Proposals Outcome 監視

> `/improve` REPORT の Proposals Outcome 統計セクションと併用する。

| 指標 | 正常範囲 | 警告 |
|------|---------|------|
| accept rate (merged/total) | 30-80% | >80% は基準が甘い可能性 |
| revert rate (reverted/merged) | <30% | >30% は提案品質に懸念 |
| accept rate 前回比変動 | ±20pp 以内 | +20pp 以上は Rule 29 確認 |

## Holdout Validation（方向性 — Rule 43）

- `scripts/eval/split_holdout.py` で train/holdout 分割を実行可能
- search セット (train 70%) で改善を評価、holdout (30%) で汎化を確認
- search で改善、holdout で劣化 → 過学習の兆候
- 現状は手動実行。evolve ループへの自動接続は次ステップ

## 関連ファイル

- `scripts/policy/gaming-detector.py` — 自動検出スクリプト
- `references/improve-policy.md` — Rule 21-23, 29, 43 の詳細定義
- `scripts/eval/split_holdout.py` — holdout 分割スクリプト
- `~/.claude/agent-memory/metrics/improve-history.jsonl` — eval_tuple_count 記録
