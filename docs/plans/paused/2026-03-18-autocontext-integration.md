---
status: active
last_reviewed: 2026-04-23
---

# autocontext 知見の統合プラン

> Source: `docs/research/2026-03-18-autocontext-recursive-improvement-analysis.md`
> 規模: L（8-10ファイル変更）
> Status: **paused** — 分析・プラン生成完了。実装は新セッションで実行。
> 推奨実行: `/rpi docs/plans/paused/2026-03-18-autocontext-integration.md`

## 概要

autocontext の5つの知見を AutoEvolve エコシステムに統合する。
既存のアーキテクチャを活かし、最小限の変更で最大の効果を狙う。

## 依存関係

```
Task 1 (累積品質スコア) ← 独立
Task 2 (次元別ルブリック) ← 独立
Task 3 (統合ベンチマーク) ← Task 1 に依存（スコアを使用）
Task 4 (蒸留パス標準化) ← 独立
Task 5 (役割分離) ← Task 2, 4 に依存（出力フォーマットを参照）
```

→ Task 1, 2, 4 は並列実行可能。Task 3 → Task 5 は逐次。

---

## Task 1: 累積品質スコア（Elo-inspired Quality Score）

### 設計方針

完全な Elo（対戦相手が必要）ではなく、**累積品質スコア (CQS)** を導入する。
各実験の結果（keep/discard/neutral）に応じてスコアが変動し、
AutoEvolve 全体の「改善力」をトラッキングする。

### 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `scripts/experiment_tracker.py` | `compute_cqs()` 関数追加。実験結果から累積スコアを計算 |
| `references/improve-policy.md` | CQS 基準の追記（CQS 低下時の改善サイクル制限等） |

### 詳細設計

```python
def compute_cqs() -> dict:
    """Cumulative Quality Score を計算する。

    - keep: +10 * abs(change_pct) / 100  (改善幅に比例)
    - discard: -15  (悪化ペナルティは固定で大きく)
    - neutral: -2  (効果なしは軽いペナルティ)

    CQS = sum(deltas) / total_experiments
    """
```

### improve-policy への追記

```markdown
## 累積品質スコア (CQS)

| CQS 範囲 | 状態 | アクション |
|----------|------|-----------|
| > 5.0 | Excellent | 通常改善サイクル |
| 2.0-5.0 | Good | 通常改善サイクル |
| 0.0-2.0 | Stagnant | 仮説の質を見直し |
| < 0.0 | Degrading | 改善サイクルを一時停止、根本原因分析 |
```

---

## Task 2: 次元別レビュールブリック

### 設計方針

レビューアーの出力に **5次元スコア** を追加する。
findings リストはそのまま維持し、先頭にスコアサマリーを追加する形式。
autocontext の「最弱次元を狙い撃ち」パターンを取り入れる。

### 次元定義

| 次元 | 説明 | 重み |
|------|------|------|
| correctness | ロジックの正しさ、バグの有無 | 0.30 |
| security | セキュリティ脆弱性、入力検証 | 0.25 |
| maintainability | 可読性、テスタビリティ、複雑度 | 0.20 |
| performance | 不要な計算、N+1、メモリリーク | 0.15 |
| consistency | 既存コードベースとの一貫性 | 0.10 |

### 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `agents/code-reviewer.md` | 出力フォーマットに次元別スコア（1-5）を追加 |
| `agents/codex-reviewer.md` | 同上 |
| `scripts/policy/review-feedback-tracker.py` | スコアパース + review-feedback.jsonl への記録 |
| `scripts/lib/session_events.py` | `emit_review_scores()` 関数追加 |

### レビューアー出力フォーマット変更

```markdown
## Review Scores
correctness: 4/5
security: 5/5
maintainability: 3/5
performance: 4/5
consistency: 4/5
weakest: maintainability

## Findings
... (既存フォーマット維持)
```

### review-feedback-tracker の拡張

review-feedback.jsonl に scores フィールドを追加:
```json
{
  "finding_id": "...",
  "verdict": "accepted",
  "scores": {"correctness": 4, "security": 5, "maintainability": 3, "performance": 4, "consistency": 4},
  "weakest_dimension": "maintainability"
}
```

### AutoEvolve Phase 1 への接続

- 次元別スコアの時系列を分析
- 弱い次元が特定パターンに起因するか調査
- 改善提案を弱い次元に集中させる

---

## Task 3: セットアップ統合ベンチマーク

### 設計方針

autocontext の「ゲームシナリオ + エージェントタスク」を参考に、
セットアップ全体の品質を測定するベンチマーク基盤を構築する。

ただし、完全な自動実行（autocontext のように実際にエージェントを走らせる）は
コスト・複雑さが大きいため、**計測可能なプロキシ指標** を定義して
既存の learnings データから算出する。

### 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| 新規: `scripts/benchmark/setup_health.py` | ベンチマークスコア計算スクリプト |
| 新規: `references/benchmark-dimensions.md` | ベンチマーク次元定義 |
| `references/improve-policy.md` | ベンチマーク参照の追記 |

### ベンチマーク次元

| 次元 | データソース | 計算方法 |
|------|-------------|---------|
| Error Rate | errors.jsonl | errors / sessions (直近30日) |
| Recovery Rate | session-metrics.jsonl | recovery / (recovery + failure) |
| Quality Score | quality.jsonl | 1 - (violations / sessions) |
| Skill Health | skill-executions.jsonl | healthy_skills / total_skills |
| Improvement Velocity | experiment-registry.jsonl | CQS トレンド (Task 1) |
| Review Acceptance | review-feedback.jsonl | accepted / total |

### 出力フォーマット

```
Setup Health Report — 2026-03-18
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Error Rate:           0.42 errors/session  (↓12% vs 30d ago)
Recovery Rate:        78%                  (↑5%)
Quality Score:        0.85                 (→ stable)
Skill Health:         12/15 healthy        (↑1)
Improvement Velocity: CQS 3.2             (↑0.5)
Review Acceptance:    72%                  (↑3%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall: GOOD (4.1/5.0)
```

### /improve との統合

- `/improve` 実行時に自動計算し、レポートに含める
- 前回値との比較で改善/悪化を可視化
- CQS < 0 のとき Setup Health も低下しているか確認（クロスバリデーション）

---

## Task 4: 知識蒸留パスの標準化

### 設計方針

現在 ad-hoc に行われている「Codex/Gemini 分析結果 → ドキュメント昇格」を
明確な蒸留パイプラインとして定義する。

### 蒸留パイプライン

```
Raw Events (errors.jsonl, patterns.jsonl)
  ↓ 3回以上出現
Recovery Tips (recovery-tips.jsonl)
  ↓ 5回以上 + 有効性検証済み
Error Fix Guides (references/error-fix-guides.md)
  ↓ 全プロジェクト共通 + 10回以上
Rules (rules/common/*.md)
  ↓ Golden Principle 候補
Golden Principles (references/golden-principles.md → golden-check.py)
```

### 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `references/improve-policy.md` | 蒸留パイプライン定義の追記 |
| `agents/autoevolve-core.md` | Phase 3 Garden に蒸留チェックリスト追加 |

### improve-policy への追記

```markdown
## 知識蒸留パイプライン (Knowledge Distillation Pipeline)

| レベル | ソース | 昇格先 | 昇格条件 |
|--------|--------|--------|---------|
| L0 | Raw events | recovery-tips.jsonl | 同じ error_pattern 3回以上 |
| L1 | recovery-tips | error-fix-guides.md | 5回以上 + 同パターンの再発なし |
| L2 | error-fix-guides | rules/common/*.md | 全プロジェクト共通 + 10回以上 |
| L3 | rules | golden-principles.md | 自動検出可能 + 高影響度 |

蒸留は Phase 3 Garden で評価し、条件を満たすものを昇格提案する。
Codex/Gemini の分析結果も L1 相当として error-fix-guides に直接投入可能。
```

---

## Task 5: 改善パイプラインの役割分離

### 設計方針

autocontext の6役（Competitor→Translator→Analyst→Coach→Architect→Curator）を
参考に、autoevolve-core の各フェーズ内にサブロールを定義する。

**6つの別エージェントを作らない**（YAGNI）。1エージェント内で逐次実行する。

### ロール対応表

| autocontext | AutoEvolve 対応 | フェーズ |
|-------------|----------------|---------|
| Competitor | （スキル実行自体がこの役割） | — |
| Translator | Phase 1 Analyze: データ正規化 | Analyze |
| Analyst | Phase 1 Analyze: パターン分析 + 因果帰属 | Analyze |
| Coach | Phase 2 Improve: 改善提案 + Proposer context | Improve |
| Architect | Phase 2 Improve: ツール/スクリプト改善 | Improve |
| Curator | Phase 3 Garden: 品質ゲート + 蒸留判定 | Garden |

### 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `agents/autoevolve-core.md` | 各フェーズにサブロール定義を追加。次元別スコア分析を Phase 1 に追加。蒸留チェックリストを Phase 3 に追加 |

### Phase 1 Analyze の強化

```markdown
### サブロール

1. **Normalizer** (Translator 相当):
   - learnings データの正規化、重複排除
   - 次元別レビュースコアの集計

2. **Pattern Analyst** (Analyst 相当):
   - エラーパターン分析（既存）
   - 次元別スコアの弱点分析（新規: Task 2 の出力を消費）
   - CQS トレンド分析（新規: Task 1 の出力を消費）
```

### Phase 3 Garden の強化

```markdown
### サブロール

1. **Quality Gate** (Curator 相当):
   - 蒸留パイプラインの昇格判定（Task 4）
   - CQS が Degrading なら改善提案を制限
   - Setup Health Report の生成（Task 3）
```

---

## 実行順序

```
並列 Phase:
  ├─ Task 1: experiment_tracker.py + improve-policy.md (CQS)
  ├─ Task 2: code-reviewer.md + codex-reviewer.md + review-feedback-tracker.py + session_events.py (ルブリック)
  └─ Task 4: improve-policy.md + autoevolve-core.md (蒸留パス)

逐次 Phase:
  ├─ Task 3: setup_health.py + benchmark-dimensions.md + improve-policy.md (ベンチマーク)
  └─ Task 5: autoevolve-core.md (役割分離 — Task 1,2,4 の出力を参照)
```

## 検証

- [ ] `python scripts/experiment_tracker.py status` が CQS を含む
- [ ] code-reviewer の出力に Review Scores セクションが含まれる
- [ ] `python scripts/benchmark/setup_health.py` が正常実行される
- [ ] improve-policy.md に蒸留パイプライン定義が含まれる
- [ ] autoevolve-core.md にサブロール定義が含まれる
- [ ] 既存テスト（`uv run pytest tests/`）が pass する
