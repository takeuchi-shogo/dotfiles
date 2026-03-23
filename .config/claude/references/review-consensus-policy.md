# Review Consensus Policy

> 論文 "Can AI Agents Agree?" (arXiv:2603.01213) の知見に基づく。
> LLM エージェント群の合意は、benign 設定ですら信頼性が低く、
> グループサイズ増加・外れ値出力で急速に劣化する。

---

## 1. Reviewer Scaling Upper Bound

**原則**: レビューアは増やすほど良いわけではない。N の増加は合意コストを増大させる。

| 変更規模 | 最大レビューア数 | 根拠 |
|----------|-----------------|------|
| ~30行    | 2               | code-reviewer + codex-reviewer で十分 |
| ~50行    | 4               | コア2 + スペシャリスト2 |
| ~200行   | 6               | コア2 + スペシャリスト3 + Gemini 1 |
| 200行超  | 8               | 上限。これ以上は合成の矛盾コストが指摘の価値を上回る |

上限を超えるスペシャリスト候補がある場合、コンテンツシグナルの強さでトリアージし、上限内に収める。

---

## 2. Agreement Rate Computation

レビューア間の一致度を定量化する。

### 計算式

```
agreement_rate = 1 - (conflict_count / total_findings)
```

- `conflict_count`: 同一ファイル・同一行（+-5行）で矛盾する指摘の組数
- `total_findings`: 全レビューアの指摘総数

### 解釈ガイド

| Agreement Rate | 解釈 | アクション |
|----------------|------|-----------|
| >= 90% | 高い一致 | 合成結果を信頼して報告 |
| 70-89% | 中程度の一致 | Conflicts セクションを明記して報告 |
| < 70% | 低い一致 | 収束停滞フラグを立て、ユーザーに矛盾点を明示して判断を委ねる |

---

## 3. Convergence Stall Detection

### 定義

複数レビューアの出力が矛盾し、オーケストレータが単一の verdict に収束できない状態。

### 検出条件（いずれかを満たす場合）

1. **Critical 矛盾**: 2体以上のレビューアが同一箇所で PASS vs BLOCK の矛盾を出力
2. **Verdict 分裂**: PASS を出すレビューアと NEEDS_FIX を出すレビューアが同数
3. **Agreement Rate < 70%**

### 対応

収束停滞を検出した場合:

1. 合成レポートの冒頭に `[CONVERGENCE STALL]` フラグを付与
2. 矛盾する指摘を Conflicts セクションに全て列挙
3. オーケストレータは verdict を `NEEDS_HUMAN_REVIEW` とし、自動判定しない
4. ユーザーにどちらのレビューアの指摘を優先するか判断を委ねる

---

## 4. Outlier Review Output Detection

### 定義

1体のレビューアの出力が他のレビューア群と著しく乖離している状態。

### 検出基準

| 指標 | 閾値 | 説明 |
|------|------|------|
| **Finding 重複率** | < 20% | そのレビューアの指摘が他のどのレビューアとも 20% 未満しか重ならない |
| **Severity 乖離** | 2段階以上 | 他が全員 Watch なのに1体だけ Critical を付けている（逆も同様） |
| **Finding 数の外れ値** | 平均の 3x 以上 | 1体だけ異常に多い/少ない指摘数 |

### 対応

1. 外れ値レビューアの出力を Reviewer Breakdown に `[OUTLIER]` タグ付きで記載
2. 合成の verdict 計算から除外（ただし情報は保持）
3. 外れ値の理由を推測して注記（例: 「codex-reviewer のみが検出した深い推論に基づく指摘の可能性」）
4. 除外した場合、ユーザーに除外した旨を明示

**注意**: Codex の深い推論による指摘は他のレビューアが見逃す可能性が高い。
Severity 乖離で外れ値判定された場合でも、Codex の指摘は除外せず `[DEEP_REASONING]` タグで保持する。

---

## 5. Verbosity Bias Mitigation

> 論文 "Expert Personas Improve LLM Alignment but Damage Accuracy" (arXiv:2603.18507) の知見に基づく。
> LLM-as-judge による pointwise 評価は長い回答を過大評価する（verbosity bias）。

### 問題

レビュー合成時、オーケストレータが「どちらのレビューアの指摘が妥当か」をペアワイズ比較する際、
長い・詳細な指摘が短い・簡潔な指摘より自動的に優先されるバイアスが存在する。

### 対策: 位置入替ペアワイズ比較

矛盾する指摘を比較する場合、以下の手順でバイアスを軽減する:

1. 指摘 A と指摘 B を `A → B` の順で提示し、どちらが妥当か判定
2. 順序を入れ替え `B → A` で再判定
3. **両方の順序で同じ指摘が勝った場合のみ**、その指摘を優先する
4. 順序で結果が変わった場合、バイアスの可能性があるため両方を併記してユーザーに判断を委ねる

### 適用条件

- Convergence Stall（セクション3）検出時の矛盾解消に使用
- Outlier（セクション4）判定の Severity 乖離確認に使用
- 通常の合成（Agreement Rate >= 90%）では不要

---

## 6. Capability-Weighted Synthesis

> HACRL (arXiv:2603.02604) の知見に基づく。
> 能力差を無視した等価重み付けは特に困難なケースで大幅に劣化する (AIME2025 で -44%)。
> レビューアーのドメイン別 capability score で指摘を重み付けし、合成精度を向上させる。

### 適用条件

- **3体以上**のレビューアー構成時に適用
- 2体以下では等価扱い（capability weighting のオーバーヘッドが利益を上回る）

### スコア参照

`reviewer-capability-scores.md` の Score Table を使用する。

### 合成ルール

```
effective_weight(finding) = capability_score[reviewer][domain] * severity_multiplier
```

#### Severity Multiplier

| Severity | Multiplier |
|----------|-----------|
| Critical | 3 |
| Important | 2 |
| Watch | 1 |

#### 同一指摘の合算

同一ファイル +-10行以内 + 同一 failure_mode の指摘が複数レビューアーから出た場合、
effective_weight を合算する（HACRL の joint baseline に相当）。

```
合算例:
  codex-reviewer (Logic: 0.90) が Critical で指摘 → 0.90 * 3 = 2.70
  code-reviewer  (Logic: 0.80) が Critical で同一指摘 → 0.80 * 3 = 2.40
  合算 effective_weight = 2.70 + 2.40 = 5.10
```

#### 判定への影響

- effective_weight による重み付けは**優先順位の決定**に使用する
- verdict (PASS/NEEDS_FIX/BLOCK) の判定基準（ルール6）は変更しない
- Synthesis レポートの指摘一覧を effective_weight 降順でソートする
- 同一 severity 内での並び順を capability-weighted order にする

### Verbosity Bias との関係

Capability weighting は Section 5 (Verbosity Bias Mitigation) と併用する。
矛盾する指摘の比較時は、まず位置入替ペアワイズ比較（Section 5）で順序バイアスを除去し、
その上で capability score を判断材料に加える。

---

## References

- arXiv:2603.01213 "Can AI Agents Agree?" (Berdoz et al., 2026)
- arXiv:2603.18507 "Expert Personas Improve LLM Alignment but Damage Accuracy" (Hu et al., 2026) — Verbosity bias mitigation
- arXiv:2603.02604 "Heterogeneous Agent Collaborative Reinforcement Learning" (Zhang et al., 2026) — Capability-weighted synthesis (Section 6)
- `reviewer-capability-scores.md` — Reviewer x Domain score table (Section 6)
- `agency-safety-framework.md` - Adversarial framing trade-offs section
- `failure-taxonomy.md` - FM-009 (Resource Exhaustion / Timeout)
