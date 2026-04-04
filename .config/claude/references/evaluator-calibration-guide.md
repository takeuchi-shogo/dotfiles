# Evaluator Calibration Guide

LLM ジャッジ（レビューアー）の信頼性を定量的に校正する手法ガイド。
hamelsmu/evals-skills の validate-evaluator 手法を内部向けに適応。

## 概要

1. 人間ラベル付きデータを train/dev/test に分割
2. ジャッジを dev セットで実行し TPR/TNR を計測
3. TPR/TNR > 90% になるまでジャッジを改善
4. test セットで最終計測（1回のみ）
5. プロダクションデータに Rogan-Gladen 補正を適用

## TPR と TNR

**TPR (True Positive Rate)**: 人間が Pass と判定したとき、ジャッジも Pass とする割合

```
TPR = (judge=Pass AND human=Pass) / (human=Pass)
```

**TNR (True Negative Rate)**: 人間が Fail と判定したとき、ジャッジも Fail とする割合

```
TNR = (judge=Fail AND human=Fail) / (human=Fail)
```

raw accuracy ではなく TPR/TNR を使う理由: クラス不均衡下で accuracy は misleading。
Pass が 90% のデータでは「常に Pass」で accuracy 90% だが TNR は 0%。

## データ分割

| Split | サイズ | 目的 | ルール |
|-------|--------|------|--------|
| **Train** | 10-20% | few-shot 例のソース | 明確な Pass/Fail のみ。プロンプトに直接使用 |
| **Dev** | 40-45% | 反復改善 | プロンプトに含めない。繰り返し評価 |
| **Test** | 40-45% | 最終計測 | 開発中は見ない。最後に1回だけ使用 |

目標: dev + test で各クラス 30-50 例。実分布が偏っていてもバランスを取る。

**データリーケージ防止**: dev/test の例を few-shot に使うと精度が膨らむ。train split からのみ選出する。

## 不一致の分析

| タイプ | ジャッジ | 人間 | 対策 |
|--------|----------|------|------|
| False Pass | Pass | Fail | ジャッジが甘い → Fail 定義を強化、エッジケース例を追加 |
| False Fail | Fail | Pass | ジャッジが厳しい → Pass 定義を明確化、例を調整 |

## 停止基準

- **目標**: TPR > 90% AND TNR > 90%
- **最低許容**: TPR > 80% AND TNR > 80%

### 活性制約 (Liveness Constraint)

> Tu (2026): delta_- (偽陰性率 = 1 - TPR) が高すぎると、正しい候補も棄却されシステムが停止する。
> 正しい候補の生存確率 = (1 - delta_-)^m = TPR^m。m=5, TPR=0.7 で生存率 16.8%。
> TNR を上げすぎて TPR が下がると、レビューが何も PASS にしなくなる。
> `review-consensus-policy.md` §3 の NEEDS_HUMAN_REVIEW 判定は活性制約違反の検出に相当する。
> 詳細: `references/structured-test-time-scaling.md` §6

## Rogan-Gladen 補正

ジャッジの生スコアにはバイアスがある。集約 pass rate を報告する場合は補正する:

```
theta_hat = (p_obs + TNR - 1) / (TPR + TNR - 1)
```

- `p_obs` = ジャッジが Pass とした割合（ラベルなし本番データ）
- `theta_hat` = 補正された真の成功率
- TPR + TNR - 1 が 0 に近い場合は無効（ジャッジがランダムと同等）

**例**: TPR=0.92, TNR=0.88, 500トレース中400がPass (p_obs=0.80)
→ theta_hat = (0.80 + 0.88 - 1) / (0.92 + 0.88 - 1) = 0.68 / 0.80 = **0.85**

## Bootstrap 信頼区間

点推定だけでは不十分。`bootstrap_ci()` で 95% CI を計算する。

```python
from evaluator_metrics import compute_tpr_tnr, rogan_gladen_correction, bootstrap_ci

metrics = compute_tpr_tnr(human_labels, eval_labels)
corrected = rogan_gladen_correction(p_obs=0.80, tpr=metrics["tpr"], tnr=metrics["tnr"])
ci = bootstrap_ci(human_labels, eval_labels, p_obs=0.80)
```

## 実用ガイダンス

- LLM ジャッジのモデルバージョンを固定する（`gpt-4o-2024-05-13` 等、`gpt-4o` ではない）
- ジャッジプロンプト変更、モデル切替、CI 拡大時に再校正
- ~100 ラベル例（50 Pass, 50 Fail）を推奨。60 未満は CI が広い
- TPR 改善は TNR 改善より CI を狭める効果が大きい

## Anti-Patterns

- ジャッジが「正しく動く」と仮定し校正を省く
- raw accuracy や percent agreement を使用する（TPR/TNR を使え）
- dev/test 例を few-shot に使用する（データリーケージ）
- dev セットの性能を最終精度として報告する（test セットが公平な推定）
- Rogan-Gladen 補正なしで集約 pass rate を報告する
- 信頼区間なしの点推定のみ報告する
- レビューアーの verbalized confidence を校正済み指標として扱う（下記 Discount 原則を参照）

## Verbalized Confidence Discount 原則

> Zhao et al. "Wired for Overconfidence" (arXiv:2604.01457, 2026-04):
> LLM の信頼度言語化回路 (CMC) は事実性回路と構造的に分離しており、
> 言語化された信頼度は**体系的に膨張**する。モデル固有の構造的特性であり、
> プロンプト調整だけでは完全に解消できない。

### ルール

1. **高信頼度への懐疑**: confidence >= 90% を額面通り受け取らない。判定（PASS/FAIL）は信頼するが、confidence スコアの精度は低い
2. **低信頼度の方が正確**: 「自信がない」は膨張バイアスがないため、高信頼度より信頼性が高い
3. **集団校正を優先**: 個々の confidence 値より TPR/TNR（Rogan-Gladen 補正）が信頼できる
4. **全員高信頼度は警告信号**: `review-consensus-policy.md` の Confidence Inflation Alert を参照
