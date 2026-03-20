---
source: https://rlhfbook.com/c/04-instruction-tuning, https://rlhfbook.com/c/05-reward-models, https://rlhfbook.com/rl-cheatsheet
date: 2026-03-20
status: integrated
related: docs/research/2026-03-18-policy-gradients-rlhf-analysis.md
---

# RLHF Book Ch4/Ch5 — 報酬モデリングとインストラクションチューニングの応用分析

## Source Summary

Nathan Lambert "RLHF Book" の Ch4 (Instruction Tuning) と Ch5 (Reward Models) を分析。
Ch6 (Policy Gradients) は 2026-03-18 に分析・統合済み（`rl-optimization-guide.md`）。

### Ch4: Instruction Tuning

- **プロンプトマスキング**: 応答部分のみ損失計算。ユーザー質問の予測学習は不要
- **低学習率**: 事前学習比 1-2 桁低い値で保守的更新
- **分布マッチング**: 訓練データは下流タスク分布と類似すべき
- **段階的最適化**: 個別段階より全体最適化が重要

### Ch5: Reward Models

- **Bradley-Terry**: P(i>j) = sigmoid(r_i - r_j)。スコア差のみが有意、絶対値は無意味
- **マージン損失**: 選好の強さ m(y_c, y_r) を損失に組み込む（Llama 2）
- **K-wise ランキング**: Plackett-Luce モデルで K≥3 の順序付き比較。K=2 で Bradley-Terry に帰着
- **ORM (Outcome RM)**: トークン単位の正確性確率。検証可能ドメイン向け
- **PRM (Process RM)**: 推論ステップごとの報酬。ステップ境界で +1/0/-1 の3クラス
- **生成型 RM**: LLM を審判として使用。温度=0 でロバスト性向上

### RL Cheatsheet

全 RL 損失関数の 1 枚リファレンス。Ch6 分析でカバー済み。

## Gap Analysis

| # | 手法 | 判定 | 現状 / 差分 |
|---|------|------|------------|
| 1 | Bradley-Terry（スコア差のみ有意） | **Already** | `rl-optimization-guide.md` の advantage 計算が同概念 |
| 2 | LLM-as-Judge | **Already** | `evaluator-calibration-guide.md` で TPR/TNR/Rogan-Gladen 補正済み |
| 3 | Prompt Masking（応答部分のみ学習） | **Already** | session-learner がエージェント出力のみ記録 |
| 4 | 低学習率（保守的更新） | **Already** | AutoEvolve の max 3 files/cycle + clip_ratio |
| 5 | PRM（ステップレベル報酬） | **Partial** | `step_credit()` は呼び出し回数比。各ステップの「正しさ」個別評価なし |
| 6 | ORM/PRM 使い分け | **Partial** | outcome 分類あるが、タスク種別に応じた報酬モデル切替なし |
| 7 | マージン損失（選好の強さ） | **Gap** | A/B で「どちらが良いか」はあるが度合いを反映しない |
| 8 | K-wise ランキング（Plackett-Luce） | **Gap** | K=2 ペアワイズのみ。K>=3 の順序付きランキング集約なし |
| 9 | 分布マッチング | **Gap** | 改善提案が実使用パターンとマッチしているか検証しない |
| 10 | マルチターンマスキング戦略 | **N/A** | ニューラルネット学習ではない |
| 11 | チャットテンプレート / Jinja | **N/A** | エージェントプロンプトに無関連 |
| 12 | バッチサイズ削減 | **N/A** | 離散最適化に不適用 |

## Integration Decisions

全 Gap/Partial 項目を取り込む（ユーザー選択: 全部）:

1. **[Partial] PRM ステップ評価** — step_credit に正しさ判定を追加
2. **[Partial] ORM/PRM 使い分け** — タスク種別でスコアリング切替
3. **[Gap] マージン損失** — A/B 比較に度合いを反映
4. **[Gap] K-wise ランキング** — Plackett-Luce で K>=3 集約
5. **[Gap] 分布マッチング** — 改善提案の使用パターン適合検証

## Plan

### Task 1: `rl_advantage.py` に margin_advantage と plackett_luce_ranking を追加

**ファイル**: `scripts/lib/rl_advantage.py`

```python
def margin_advantage(score_a: float, score_b: float) -> float:
    """マージン付き advantage。差の大きさを保持する。"""

def plackett_luce_ranking(scores: list[float]) -> list[float]:
    """K>=3 の Plackett-Luce 順序付きランキングスコア。"""
```

### Task 2: `step_credit()` に quality 評価を追加

**ファイル**: `scripts/lib/rl_advantage.py`

現在の `step_credit()` は呼び出し回数比で配分。PRM 的に各ステップの
正しさ（success/neutral/failure）で重み付けするオプションを追加。

```python
def step_credit(outcome, invocations, events, step_quality=None):
    """step_quality: Optional[dict[str, float]] — スキル名→品質スコア"""
```

### Task 3: `rl-optimization-guide.md` に Ch5 由来の関数ドキュメント追加

**ファイル**: `.config/claude/references/rl-optimization-guide.md`

- margin_advantage, plackett_luce_ranking の使用例追加
- step_credit の quality 引数ドキュメント追加
- ORM/PRM 使い分けガイドライン追加

### Task 4: `scoring-rules.md` にタスク種別ルーティング追加

**ファイル**: `.config/claude/references/scoring-rules.md`

| タスク種別 | スコアリング | 理由 |
|-----------|------------|------|
| 推論系（デバッグ、設計） | PRM 的（ステップ品質重視） | 中間推論の正しさが重要 |
| 結果系（生成、変換） | ORM 的（最終結果重視） | 最終出力のみが重要 |

### Task 5: `autoevolve-core.md` に分布マッチング検証を追加

**ファイル**: `.config/claude/agents/autoevolve-core.md`

Improve フェーズで改善提案を生成する際、直近 N セッションの
スキル使用頻度と提案対象が一致しているか検証するステップを追加。

### 規模

M（5 ファイル変更）。同一セッションで実行可能。
