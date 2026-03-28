# Review Consensus Policy

レビューアー間の合意形成・対立解消・外れ値処理のポリシー。
review SKILL.md Step 4 (Synthesis) から参照される。

## Section 1: セマンティック重複排除

同一ファイル ±10行以内 AND 同一 failure_mode の指摘を1件に統合する。

- 統合時は最高 confidence のレビューアーの指摘を代表とする
- 統合元は「(他 N 件のレビューアーも同様の指摘)」と注記
- ±10行の判定は diff の行番号基準（ファイル全体の行番号ではない）

## Section 2: 信頼度ブースト

複数の独立レビューアーが同一問題を指摘した場合:

```
boosted_confidence = max(individual_scores) + 5 * (agreeing_reviewers - 1)
```

上限 100。2人が同じ問題を指摘 → +5、3人 → +10。

## Section 3: 対立検出と解消

同一箇所で矛盾する指摘が出た場合:

1. 両方残して `[CONFLICT]` タグを付与
2. 各レビューアーの capability_score で重み付けし、高い方を「推奨」とする
3. 重み差が 2x 以上 → 高い方を採用、低い方を「参考」に格下げ
4. 重み差が 2x 未満 → 両方残して verdict は `NEEDS_HUMAN_REVIEW`

## Section 4: Codex 指摘の必須対応

codex-reviewer の指摘は特別扱い:

- `[DEEP_REASONING]` タグを常時付与
- Critical/Important は個別に対応を明記
- 「他レビューアーが指摘していない」は無視の理由にならない
- verdict 計算から除外してはならない
- Outlier 判定の対象外

## Section 5: 収束停滞検出

以下のいずれかで `[CONVERGENCE STALL]` → verdict を `NEEDS_HUMAN_REVIEW` に:

| 条件 | 閾値 |
|------|------|
| Critical 矛盾 | 2+ レビューアが同一箇所で PASS vs BLOCK |
| Verdict 分裂 | PASS と NEEDS_FIX が同数 |
| 低合意率 | Agreement Rate < 70% |

Agreement Rate の算出:

```
agreement_rate = 1 - (conflict_count / total_findings)
```

- conflict_count: 同一ファイル ±5行で矛盾する指摘の組数
- 全レビュー構成で実施（3-way に限定しない）

## Section 6: 外れ値検出

codex-reviewer **以外** のレビューアーを対象に:

1. 他レビューアーとの指摘重複率 < 20%
2. AND 指摘数が平均の 3x 以上

→ `[OUTLIER]` タグを付与し verdict 計算から除外（情報は保持）

codex-reviewer は常に `[DEEP_REASONING]` として verdict に含める。

## Section 7: Capability-Weighted Synthesis

全レビュー構成（2体以上）で適用:

```
effective_weight = capability_score[reviewer][domain] × severity_multiplier
```

severity_multiplier:
- Critical: 3
- Important: 2
- Watch: 1

同一指摘が複数レビューアーから出た場合は重みを合算。
合成レポートの指摘一覧を effective_weight 降順でソートする。

capability_score の値は `reviewer-capability-scores.md` を参照。
