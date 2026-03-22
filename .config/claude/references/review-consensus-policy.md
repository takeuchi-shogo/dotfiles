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

## References

- arXiv:2603.01213 "Can AI Agents Agree?" (Berdoz et al., 2026)
- `agency-safety-framework.md` - Adversarial framing trade-offs section
- `failure-taxonomy.md` - FM-009 (Resource Exhaustion / Timeout)
