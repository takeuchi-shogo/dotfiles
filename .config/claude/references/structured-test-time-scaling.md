# Structured Test-Time Scaling Theory

> Source: Tu (2026) "Hierarchical MAS Theory"
> Integration: 2026-03-26

長期推論の信頼性スケーリングを支える3層構造的デカップリングの理論的フレームワーク。
既存の仕組み（サブエージェント委譲、スコープ分離、多段検証）が**なぜ**機能するかを数学的に説明し、
**どのレバーを引くべきか**の判断基準を提供する。

## 1. 統一信頼性方程式

```
P_success ≈ exp(-η·D) × exp(-W·ε_leaf·δ₊^m)

対数形:
-ln P_success ≈ η·D + W·ε_leaf·δ₊^m
```

| 記号 | 意味 | dotfiles での対応 |
|------|------|-------------------|
| W | 原子作業単位の総数 | タスク規模（S/M/L） |
| D | 階層深度 | Depth-1 ルール → D=1（通常）|
| η | 層あたりのドリフト確率 | コンテキスト汚染率 |
| ε_leaf | 分離後のリーフ誤り率 | subagent のタスク失敗率 |
| δ₊ | 検証の偽陽性率（不正な候補を受け入れ）| evaluator-calibration-guide TPR/TNR |
| δ₋ | 検証の偽陰性率（正しい候補を棄却）| 活性制約に直結 |
| m | 冗長検証チェック数 | review scaling table (2-8) |

### 線形 vs 階層の比較

| 量 | 線形 CoT | 階層型 MAS |
|----|----------|------------|
| スパン S | Θ(W) | Θ(log_k W) |
| グローバルドリフト | e^(-ηW) | e^(-ηD) |
| 残留リーフ誤り | Wε_mono | Wε_leaf·δ₊^m |

## 2. 3メカニズムと因果依存チェーン

```
Mechanism I: Topology → 分解境界を作成
    ↓ (境界が存在して初めて)
Mechanism II: Scope Isolation → 離散的・検証可能なアーティファクトを生産
    ↓ (検証可能なアーティファクトがあって初めて)
Mechanism III: Verification → δ₊^m の指数抑制を実現
```

**診断フロー**: 検証が機能しない場合、まず分離を確認。分離が不十分なら、トポロジー（分解境界）を確認。

### Mechanism I: Topology（制御スパン圧縮）

- **対応**: subagent-delegation-guide.md, blueprint-pattern.md, workflow-guide.md
- **核心**: S = Θ(D) により、誤り複合を対数的に抑制
- **ファンアウト k の上限**: 意味的統合容量 = O(k) 推論タスク。k を極端化するとマネージャに線形崩壊を転嫁

### Mechanism II: Scope Isolation（状態/コンテキスト分離）

- **対応**: output-offload.py, session-protocol.md, compact-instructions.md
- **核心**: L_leaf ≪ L_root, N_leaf ≪ N_root により ε_leaf を低減
- **永続的設計原理**: 無限コンテキストでも信号ノイズ比は低下する（認知帯域幅の劣化）。分離はパッチではなく構造的必須要件

### Mechanism III: Verification（ゲートでのエラー訂正）

- **対応**: review-consensus-policy.md, completion-gate.py, evaluator-calibration-guide.md
- **核心**: m 個の独立チェックで残留誤りを δ₊^m に抑制
- **真の必須条件**: δ₊ < 1（ベリファイアが完全盲目でなければ、指数抑制は機能する）

## 3. レジーム分析

タスク特性に応じて、どのメカニズムに投資すべきかが異なる。

### 分離支配レジーム

**条件**: W·ε_leaf が十分小さい（タスクが小規模 or 分離が十分）
- 明示的な検証チェック不要
- **対応**: S 規模タスク → Implement → Verify のみ（レビュー省略可）

### 検証支配レジーム

**条件**: W·ε_leaf が大きい（タスクが大規模 or 分離が不十分）
- m を成長させて q = ε_leaf·δ₊^m を O(1/W) に駆動
- **対応**: L 規模タスク → フル検証パイプライン（テスト + 多段レビュー）

### 現ワークフローへのマッピング

| タスク規模 | W 推定 | レジーム | 推奨検証量 |
|-----------|--------|---------|-----------|
| S | ~5 | 分離支配 | テスト実行のみ (m=0-1) |
| M | ~20 | 遷移領域 | テスト + code-reviewer + codex-reviewer (m=2) |
| L | ~100+ | 検証支配 | フル検証: テスト + 並列レビュー (m=4-8) |

## 4. 冗長性の対数モデル

```
必要チェック数: m ≥ ln(W·ε_leaf) / (-ln δ₊) = O(log W)

例: W=100, ε_leaf=0.05, δ₊=0.3
m ≥ ln(5) / ln(3.33) ≈ 1.6 / 1.2 ≈ 1.3 → m=2 で十分
```

### 相関によるチェック効果の減衰

```
有効独立チェック数: m_eff = m / (1 + (m-1)·ρ)

ρ = 0:   完全独立 → m_eff = m（理想）
ρ = 0.5: 中程度相関 → m_eff ≈ 2m/(m+1)（m=4 で m_eff≈1.6）
ρ → 1:   完全相関 → m_eff → 1（冗長性が無効化）
```

**設計指針**: 同種レビューアー（ρ高）3体より異種レビューアー（ρ低）2体が有効。
→ review-consensus-policy §1 Heterogeneous Signal Priority の理論的裏付け。

### デコリレーション戦略（ρ を下げる方法）

| 戦略 | ρ への効果 | dotfiles 実装 |
|------|----------|---------------|
| 異種モデル（Claude ↔ Codex ↔ Gemini） | 強 | cross-model-insights.md |
| Blind-first review（diff のみ vs diff + コンテキスト） | 中 | code-reviewer vs codex-reviewer |
| 異なるレビュー次元（Logic/Security/Style） | 中 | reviewer-capability-scores.md |
| ツール検証（コンパイラ/テスト） | 強（直交） | completion-gate.py |

## 5. コスト最適化 (c_v / c_g)

| レジーム | 条件 | 戦略 |
|---------|------|------|
| **古典的** (c_v ≪ c_g) | コンパイラ、型チェック、テスト | 重い冗長性 (m ≫ 1) は安価。積極的に活用 |
| **重検証** (c_v ≈ c_g) | LLM ベースレビュー | m を増やすコストが高い。δ₊ を下げる（直交性設計）方が効率的 |

**現実的な指針**: まずツール検証（古典的レジーム）を最大化し、残りの誤りに LLM レビューを適用。

## 6. 活性制約

δ₋ が高すぎると、正しい候補も棄却され続けシステムが停止する。

```
正しい候補の生存確率: (1-δ₋)^m

m=5, δ₋=0.3: (0.7)^5 = 0.168 → 正しい候補の 83% が棄却される
m=5, δ₋=0.1: (0.9)^5 = 0.590 → 正しい候補の 41% が棄却される
```

**設計指針**:
- MAX_RETRIES (completion-gate.py) = 活性制約の実装
- Agreement Rate < 70% → NEEDS_HUMAN_REVIEW (review-consensus-policy §3) = 活性制約違反の検出
- δ₊ を下げつつ δ₋ を上げすぎない — 両方を同時に最適化はできない

## 7. 失敗チャネル分類

failure-taxonomy.md の FM を2チャネルで分類:

### Global Drift（スパン/深度駆動）
制御フローが長くなるほど蓄積する誤り。トポロジー圧縮で軽減。

- FM-003 Context Window Overflow
- FM-007 Goal Drift
- FM-009 Resource Exhaustion
- FM-019 Agentic Laziness (premature stop)

### Local Residual（作業駆動）
個々のタスクノードで発生する誤り。分離 + 検証で軽減。

- FM-001 Wrong Fix
- FM-002 Incomplete Fix
- FM-004 Test Gaps
- FM-005 Regression Introduction
- FM-016 Result Fabrication
- FM-018 Evaluator Rationalization
- FM-020 Probabilistic Cascade

### Hybrid（両チャネル）
- FM-006 Scope Creep (drift が residual を誘発)
- FM-008 Communication Failure (マルチエージェント間)

## 8. エラーモード直交性の設計原則

エラーモード直交性は固定特性ではなく**建築設計選択**。

レビューアー追加時の判断基準:
1. 既存レビューアーと**異なる失敗モード**をキャッチするか？
2. 既存レビューアーと**異なる情報ソース**を使うか？（diff のみ vs コンテキスト込み vs 外部ツール）
3. 既存レビューアーと**異なるモデル**か？

3つ全て「はい」→ ρ が低く、追加価値が高い。
全て「いいえ」→ 同種の追加であり、m_eff への寄与は逓減。
