# Graded Guardrails 設計ドキュメント

> Bengio 論文の「有害確率が閾値を超えたら拒否」に倣い、binary 判定から confidence-weighted judgment への移行を設計する。
> このドキュメントは設計のみ。実装は Spike で検証後に着手する。

## 概念

現在のハーネスのガードレールは binary（pass/fail）判定。これには2つの問題がある:

1. **偽陽性のノイズ**: 低信頼度の検出が同じ重みで報告され、開発者の注意を分散させる
2. **データ不足での過剰反応**: 少数の観測で極端な判定を出す（例: 1回の失敗で skill をスコア 0 に）

**解決**: 検出の severity と confidence を分離し、graded な判定を導入する。

---

## 適用ポイント

### 1. golden-check（severity scoring）

| 現状 | 拡張案 |
|------|--------|
| ルールマッチで WARN/FAIL の binary 出力 | 違反の severity × confidence でスコア化 |

**設計**:

```
graded_score = severity_weight[rule_id] * match_confidence
```

- `severity_weight`: GP-001〜011 ごとに定義（0.1〜1.0）
  - GP-001 (ハードコードされた値): severity 0.3（低）
  - GP-005 (セキュリティ違反): severity 1.0（高）
- `match_confidence`: パターンマッチの確度（正規表現の specificity に基づく）
  - 完全一致: 1.0
  - 部分一致: 0.5
  - コンテキスト不明: 0.3

**判定**:
- `graded_score >= 0.7` → WARN（現状通り additionalContext 出力）
- `graded_score < 0.7` → INFO（ログのみ、additionalContext に出さない）

### 2. completion-gate（変更リスクスコア）

| 現状 | 拡張案 |
|------|--------|
| テスト pass/fail の binary | テストカバレッジ率 + 変更リスクスコアで graded 判定 |

**設計**:

```
risk_score = file_count_weight + change_type_weight + module_boundary_weight
```

- `file_count_weight`: 変更ファイル数（1-3: 0.2, 4-10: 0.5, 11+: 0.8）
- `change_type_weight`: 変更種別（追記のみ: 0.1, ロジック変更: 0.5, API変更: 0.8）
- `module_boundary_weight`: モジュール境界を跨ぐか（同一モジュール: 0.0, 跨ぐ: 0.5）

**判定**:
- `risk_score >= 1.0` → テスト必須（現状通り）
- `risk_score < 0.5` → テスト推奨（ドキュメントのみ変更等は SKIP 可能）

### 3. review 信頼度（動的閾値）

| 現状 | 拡張案 |
|------|--------|
| 80 未満フィルタ（固定） | コンテキストで動的調整 |

**設計**:

```
effective_threshold = base_threshold + context_adjustment
```

- `base_threshold = 80`
- `context_adjustment`:
  - 変更 100 行超: -5（大規模変更は低信頼度でも表示すべき）
  - セキュリティ関連ファイル: -10（安全寄りに）
  - ドキュメントのみ: +10（ノイズ削減）

### 4. skill-tracker（ベイズ平均）

| 現状 | 拡張案 |
|------|--------|
| 0-1 の raw スコア | ベイズ平均で prior に回帰 |

**設計**:

```python
bayesian_score = (prior_mean * prior_weight + observed_sum) / (prior_weight + n_observations)
```

- `prior_mean = 0.5`（中立）
- `prior_weight = 5`（5回の仮想観測）
- 実行回数が少ないうちは prior（0.5）に引っ張られ、データが増えると observed に収束
- Bengio 論文の「不確実性の明示的定量化」に対応

**例**:

| 実行回数 | 成功回数 | Raw スコア | ベイズ平均 |
|---------|---------|-----------|-----------|
| 1 | 1 | 1.0 | 0.58 |
| 1 | 0 | 0.0 | 0.42 |
| 5 | 4 | 0.8 | 0.65 |
| 10 | 8 | 0.8 | 0.70 |
| 20 | 16 | 0.8 | 0.74 |

→ 少数実行での過剰反応を抑制しつつ、データが増えると実測値に収束する。

---

## 段階的導入計画

### Phase A（短期）: skill-tracker にベイズ平均導入

- **変更対象**: `scripts/policy/skill-tracker.py`
- **影響範囲**: `/improve` サイクルの判定精度
- **リスク**: 低（ログ/メトリクス変更のみ、blocking しない）
- **検証**: 既存の skill-executions.jsonl データでベイズ平均を遡及計算し、raw スコアとの乖離を確認

### Phase B（中期）: golden-check に severity scoring 導入

- **変更対象**: `scripts/policy/golden-check.py`
- **影響範囲**: 全エディット操作の自動検証
- **リスク**: 中（低 severity の検出が INFO に降格 → 見逃しリスク）
- **検証**: 過去 30 日の golden-check ログで severity scoring を遡及適用し、INFO 降格された検出の安全性を確認

### Phase C（長期）: completion-gate に変更リスクスコア導入

- **変更対象**: `scripts/policy/completion-gate.py`
- **影響範囲**: 全タスク完了判定
- **リスク**: 高（テスト SKIP の判定ミス → 品質劣化）
- **検証**: Spike でプロトタイプ実装 → 2週間の shadow mode 運用 → 問題なければ本番適用

---

## Agency Framework との位置づけ

確率的ガードレールは **Goal-directedness 制限** に分類される（`references/agency-safety-framework.md` 参照）。
binary 判定の粗さを改善することで、制限の精度を上げつつ偽陽性を減らす。Intelligence 柱は制限しない。
