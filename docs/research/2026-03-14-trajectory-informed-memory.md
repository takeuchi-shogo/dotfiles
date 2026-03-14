# Trajectory-Informed Memory Generation for Self-Improving Agent Systems

> **論文**: Fang et al. (IBM Research), arXiv:2603.10600, 2026-03-11
> **調査日**: 2026-03-14
> **目的**: AutoEvolve システムへの適用可能性の評価

## Executive Summary

IBM Research の論文は、エージェントの実行軌跡（trajectory）から構造化された「Tips」を自動抽出し、将来のタスク実行時にセマンティック検索で注入するフレームワークを提案。AppWorld ベンチマークで **TGC +3.6pp、SGC +14.3pp**（難易度3では **+28.5pp / 149%相対改善**）を達成。

現行 AutoEvolve システムとの比較により、**5つの重要な改善機会**を特定した。

---

## 1. 論文のコアアーキテクチャ

### 4コンポーネント

| # | コンポーネント | 役割 |
|---|--------------|------|
| 1 | **Trajectory Intelligence Extractor** | 実行ログからエージェントの思考パターン（分析・計画・検証・リフレクション）を意味的に分類 |
| 2 | **Decision Attribution Analyzer** | 因果分析 — 即時原因・近因・根本原因・寄与因子を特定 |
| 3 | **Contextual Learning Generator** | 3種の Tips を生成: Strategy / Recovery / Optimization |
| 4 | **Adaptive Memory Retrieval** | タスク実行時にコサイン類似度 or LLM ガイドで関連 Tips を注入 |

### 3種の Tips

| Tip 種別 | 内容 | 例 |
|---------|------|-----|
| **Strategy Tips** | 成功パターンの抽出 | 「チェックアウト前に前提条件（カート・住所・決済）を体系的に検証する」 |
| **Recovery Tips** | 失敗→回復シーケンス | 「決済エラー時は payment method を確認し、未設定なら追加してからリトライ」 |
| **Optimization Tips** | 非効率パターンの改善 | 「カート全削除は remove_from_cart() ループではなく empty_cart() を使う」 |

### 実験結果のハイライト

| 構成 | TGC | SGC |
|------|-----|-----|
| Baseline（メモリなし） | 69.6% | 50.0% |
| Subtask + LLM-guided | **73.2%** (+3.6) | **64.3%** (+14.3) |
| Subtask + Cosine (τ≥0.6) | 73.8% (+4.2) | 57.1% (+7.1) |
| Task-level + Cosine (τ≥0.6) | 72.0% (+2.4) | 62.5% (+12.5) |

**Key Finding**: Tips の粒度（subtask-level）が TGC を駆動し、検索戦略（LLM-guided）が SGC を駆動する。

---

## 2. 現行 AutoEvolve との比較分析

### アーキテクチャ対照表

| 側面 | 論文のアプローチ | 現行 AutoEvolve | ギャップ |
|------|----------------|----------------|---------|
| **データ収集** | Trajectory 全体の意味的分析 | イベント単位の hook 収集（error/quality/pattern） | 🔴 Trajectory レベルの分析なし |
| **因果分析** | 即時原因→近因→根本原因の3層 | regex ベースの FM-001〜FM-010 タグ付け | 🟡 タグはあるが因果チェーンなし |
| **Tips 分類** | Strategy / Recovery / Optimization | error / quality / pattern / correction | 🟡 類似だが Recovery Tips が欠落 |
| **Tips 粒度** | Task-level + Subtask-level | イベント単位（atomic） | 🔴 サブタスク分解なし |
| **統合・重複排除** | コサイン類似度≥0.85 でクラスタリング | 同一メッセージの単純重複排除 | 🔴 セマンティッククラスタリングなし |
| **検索** | コサイン類似度 + LLM ガイド選択 | プロファイルベースフィルタ + regex | 🔴 セマンティック検索なし |
| **注入タイミング** | タスク開始時（ランタイム） | SessionStart + PostToolUse | 🟢 より多い注入ポイント |
| **来歴追跡** | Tips → 元 trajectory ID のリンク | promotion_status のみ | 🟡 部分的 |
| **汎化** | Entity抽象化 + Action正規化 | なし（生データのまま保存） | 🔴 汎化処理なし |

### 現行の強み（論文にないもの）

| 現行の優位点 | 説明 |
|------------|------|
| **リアルタイム注入** | PostToolUse hook で即座に additionalContext 注入（論文はタスク開始時のみ） |
| **Evaluator メトリクス** | TPR/TNR によるレビュアー精度追跡 |
| **Spec/Gen 分岐** | 失敗を specification vs generalization に分類し、修正対象（instruction vs evaluator）をルーティング |
| **実験追跡** | experiment_tracker.py による改善効果の定量測定 |
| **Golden Principles** | GP-001〜008 の自動検出 + 学習ループ |
| **Skill Health** | スキル単位のスコアリング + A/B テスト |

---

## 3. 改善提案（優先度順）

### 提案 1: Recovery Tips の導入 🔴 高優先度

**What**: 「失敗→回復」シーケンスの自動抽出と保存

**Why**: 論文の最大の貢献は Recovery Tips。現行システムは error と pattern を別々に記録するが、「このエラーの後にこの修正で回復した」という因果ペアを保持していない。

**How**:

```python
# session_events.py に追加
def emit_recovery_tip(error_event: dict, fix_description: str):
    """エラー→回復ペアを recovery tips として保存"""
    tip = {
        "timestamp": now_iso(),
        "category": "recovery",
        "error_pattern": error_event.get("message", ""),
        "failure_mode": error_event.get("failure_mode", ""),
        "recovery_action": fix_description,
        "trigger_condition": extract_trigger(error_event),
        "importance": max(error_event.get("importance", 0.5), 0.7),
        "source_session": session_id(),
    }
    append_jsonl(LEARNINGS_DIR / "recovery-tips.jsonl", tip)
```

**Detection**: error-to-codex.py が Bash エラーを検出 → 次の成功 Bash 実行を監視 → ペアとして保存。

**Impact**: 繰り返しエラーの自動修正ガイド注入が可能に。error-fix-guides.md の手動メンテナンスを補完。

**Complexity**: M（session_events.py + error-to-codex.py の拡張）

---

### 提案 2: Subtask Description Generalization 🔴 高優先度

**What**: Tips の汎化処理 — エンティティ抽象化 + アクション正規化

**Why**: 論文で subtask-level tips が task-level を上回った要因。現行システムは生のエラーメッセージやファイルパスをそのまま保存するため、類似パターンの発見が困難。

**How**:

```python
# lib/tip_generalizer.py (新規)
def generalize_tip(tip: dict) -> dict:
    """Tips のエンティティを抽象化し、再利用性を高める"""
    text = tip.get("message", "") or tip.get("detail", "")

    # Entity abstraction
    text = re.sub(r'/Users/\w+/', '/Users/{user}/', text)
    text = re.sub(r'[a-f0-9]{7,40}', '{commit_hash}', text)
    text = re.sub(r'\b\d+\.\d+\.\d+\b', '{version}', text)
    text = re.sub(r'port \d+', 'port {N}', text)

    # Action normalization
    ACTION_MAP = {
        "install": "add_dependency",
        "add": "add_dependency",
        "remove": "remove_item",
        "delete": "remove_item",
        "update": "modify",
        "change": "modify",
    }

    tip["generalized_description"] = text
    return tip
```

**Impact**: 同一パターンの発見率向上。クラスタリングの前提条件。

**Complexity**: S（新規ユーティリティ + session-learner.py への組み込み）

---

### 提案 3: コサイン類似度ベースの Tips 検索 🟡 中優先度

**What**: SessionStart 時のプロファイルベースフィルタを、セマンティック類似度検索に拡張

**Why**: 論文の最大のパフォーマンス差はここ。プロファイルベース（planning/debugging）ではタスク固有の関連 Tips を見逃す。

**How**: 2段階アプローチ（KISS 原則に従い、まず軽量版から）

**Phase A — LLM ベースの関連性フィルタ（低コスト）**:

```javascript
// session-load.js の拡張
// SessionStart で現在のタスクコンテキスト（git diff, 直近のプロンプト）を取得
// LLM に「この Tips のうちどれが関連するか」を判定させる
// → 論文の LLM-Guided Selection に相当
```

**Phase B — Embedding ベース（将来）**:

```python
# lib/tip_retriever.py
# sentence-transformers で Tips を embedding → FAISS index
# タスク開始時にクエリ embedding → top-k 検索
# τ ≥ 0.6 でフィルタ
```

**Trade-off**: Phase A は LLM コール追加（レイテンシ）、Phase B は embedding モデルのセットアップが必要。現行のデータ量（~30 entries）では Phase A で十分。100+ entries で Phase B を検討。

**Impact**: 論文では LLM-guided が SGC +7.2pp（コサイン比）の差。タスクバリアント間の一貫性が大幅改善。

**Complexity**: M（Phase A）/ L（Phase B）

---

### 提案 4: 因果帰属の深化 🟡 中優先度

**What**: Decision Attribution Analyzer に相当する因果分析の導入

**Why**: 現行は FM タグ付けのみ。論文は「即時原因→近因→根本原因」の3層分析で、より精度の高い Prevention Steps を生成。

**How**:

```python
# autoevolve-core Phase 1 の Analyze プロンプトに追加
CAUSAL_ANALYSIS_PROMPT = """
各エラーイベントについて以下を分析:
1. 即時原因: 直接トリガーした条件
2. 近因: その条件を生んだ先行判断
3. 根本原因: なぜその判断がなされたか（知識不足? 仕様誤解? ツール制限?）
4. 寄与因子: 再発を防ぐために変更すべきもの

出力形式:
- prevention_steps: 具体的な予防策
- detection_pattern: 早期検出のためのシグナル
"""
```

**Impact**: error-fix-guides.md の品質向上。根本原因に基づく改善で再発率を下げる。

**Complexity**: S（autoevolve-core.md のプロンプト拡張のみ）

---

### 提案 5: Multi-Outcome Learning 🟢 低優先度

**What**: 「成功だが非効率」パターンの明示的な抽出（Optimization Tips）

**Why**: 現行は成功=pattern、失敗=error の二値分類。論文は「clean success / inefficient success / recovery sequence」の3分類で、非効率な成功からも学習。

**How**:

```python
# session-learner.py の build_session_summary() に追加
def classify_outcome(events: list[dict]) -> str:
    errors = [e for e in events if e["category"] == "error"]
    corrections = [e for e in events if e["category"] == "correction"]

    if not errors:
        return "clean_success"
    elif corrections:
        return "recovery"  # エラー後に修正して成功
    else:
        return "failure"

# session-metrics.jsonl に outcome 分類を追加
# Optimization Tips: clean_success だがターン数が多い場合に抽出
```

**Impact**: 「動いたけど遅い」パターンの発見。agent の効率改善。

**Complexity**: S（session-learner.py の拡張）

---

## 4. 実装ロードマップ

```
Week 1: 提案 2 (Generalization) + 提案 5 (Multi-Outcome)
         → 基盤整備。データ品質の向上。

Week 2: 提案 1 (Recovery Tips)
         → error-to-codex.py の拡張。最も直接的な効果。

Week 3: 提案 4 (因果帰属)
         → autoevolve-core のプロンプト拡張。分析品質向上。

Week 4+: 提案 3 (セマンティック検索)
         → Phase A (LLM フィルタ) から開始。
         → データ蓄積後に Phase B (embedding) を検討。
```

---

## 5. 採用しない要素とその理由

| 論文の要素 | 不採用の理由 |
|-----------|------------|
| **FAISS / Vector DB** | 現行データ量（~30 entries）では過剰。100+ で再検討 |
| **Subtask-level decomposition** | Claude Code の hook アーキテクチャでは trajectory 全体の取得が困難（イベント単位で発火）。SessionEnd での post-hoc 分析で代替 |
| **Dense embedding storage** | 外部依存（sentence-transformers）が増える。KISS 原則に反する |
| **Cross-agent attribution** | 現行は single-agent 中心。マルチエージェント協調が増えた時点で検討 |

---

## 6. 論文から得た設計原則

1. **Tips の粒度が精度を決める** — 粗いカテゴリ分類より、サブタスク単位の具体的な Tips が効果的
2. **検索戦略が一貫性を決める** — SGC（シナリオ全体の成功率）の改善は LLM-guided 検索から。プロファイルベースでは不十分
3. **失敗からの学習は3種必要** — エラー回避（Strategy）、エラー回復（Recovery）、効率改善（Optimization）
4. **汎化は検索の前提条件** — 生データのままでは類似パターンの発見が困難
5. **来歴追跡が信頼性を担保** — Tips → 元 trajectory のリンクにより、品質評価と conflict resolution が可能

---

## References

- Fang et al., "Trajectory-Informed Memory Generation for Self-Improving Agent Systems", arXiv:2603.10600, 2026
- karpathy/autoresearch — AutoEvolve の着想元
- Harrison Chase, "How Coding Agents Are Reshaping EPD" — EPD-Driven Development の着想元
- "Error Analysis: The Highest-ROI Activity" — Failure Taxonomy の着想元
