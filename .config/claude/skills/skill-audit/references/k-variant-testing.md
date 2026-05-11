# K-Variant Testing (RLOO/GRPO)

`/skill-audit` skill の K-Variant Testing セクションを切り出した詳細実装。
SKILL.md からは要約と本ファイルへの参照のみ残し、ここで完全なフローを定義する。

スキルの設定バリエーションを K>=3 個用意し、
RLOO/GRPO advantage で最適な variant を特定する。

## 手順

1. 対象スキルの SKILL.md を K 個の variant にコピー
2. 各 variant で `run_eval.sh` を実行し result JSON を生成
3. `aggregate_benchmark.py --variants` で比較:

```bash
python3 ~/.claude/scripts/eval/aggregate_benchmark.py \
    --variants v1.json v2.json v3.json \
    --output report.md
```

4. レポートの Advantage 値を確認:
   - **RLOO Advantage > 0**: baseline より優れている
   - **RLOO Advantage < 0**: baseline より劣っている
   - **GRPO Advantage**: z-score 正規化された相対位置

## RLOO Advantage 解釈ガイド

| Advantage | 解釈 | アクション |
|-----------|------|-----------|
| > +0.5 | 明確に優秀 | merge 推奨 |
| +0.1 ~ +0.5 | やや優秀 | 追加テスト推奨 |
| -0.1 ~ +0.1 | 差なし | 変更不要 |
| < -0.1 | 劣化 | revert 推奨 |

GRPO は z-score なので ±1.0 が1標準偏差。
±2.0 を超える variant は外れ値として注意。
