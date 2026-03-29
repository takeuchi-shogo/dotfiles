# Trust Verification Policy

> 「信頼は検証の関数であり、能力の関数ではない」
> — モデルがどれほど賢くなっても自己評価を信頼してはいけない。

Anthropic Harness Design v2 + Stripe Minions Part 2 の知見に基づく 4 層信頼モデル。

---

## 4 層信頼モデル

```
Layer 0: Deterministic Verification（嘘をつけない検証者）
  lint → type-check → selective-test → full-test
  Pass/Fail の事実。LLM 判断より常に優先

Layer 1: Adversarial Evaluation（敵対的評価）
  Generator ≠ Evaluator の構造的分離
  懐疑的ペルソナ + ドメイン別採点基準 + Rationalization 自動スキャン

Layer 2: Cross-Model Consensus（異種モデル合意）
  Claude + Codex + Gemini の独立評価
  Capability-Weighted Synthesis + Shared Blind Spot 警告

Layer 3: Human Escalation（人間エスカレーション）
  Graduated Completion + CONVERGENCE_STALL → 人間判断
```

## 優先ルール

1. **テスト結果 > レビュー合意 > 自己評価**
   - Layer 0 の Pass/Fail は Layer 1-2 の判断に優先する
   - 全 reviewer が PASS でもテストが失敗していれば BLOCK

2. **テスト未実行は PASS とみなさない**
   - テストファイルが存在するのにテストが実行されていない場合、レビュー verdict に関わらずテスト未実行警告を付加する

3. **Rationalization の自動検出**
   - レビュー出力に矮小化表現が含まれる場合、`[RATIONALIZATION_WARNING]` を発出する
   - 問題を発見した後の自己説得による承認を防止する

## 適用箇所

- `completion-gate.py`: Layer 0 チェック（テスト実行済み確認）を Review Gate より前に配置
- `/review` Step 4 Synthesis: テスト未実行時は verdict に警告を付加
- `rationalization-scanner.py`: PostToolUse(Agent) で FM-018 パターンを検出
- `derivation-honesty-hook.py`: PostToolUse(Bash|Write|Edit) で FM-016 パターンを検出

---

## Verifier 配置ヒューリスティック

Verifier（検証ゲート）の配置は「全ステップに挿入」ではなく**戦略的配置**が最適。

> 出典: Yue et al. 2026 "From Static Templates to Dynamic Runtime Graphs" §7.4
> "verifiers deliver the largest returns when they are both cheap and semantically meaningful"

### 配置原則

| 原則 | 説明 |
|------|------|
| **Cheap + Meaningful** | コストが低く、かつ意味のあるフィードバックを返す箇所に配置 |
| **候補生成直後** | 高コストな下流ステップの前に配置し、無駄なパスを刈り込む |
| **高コストステップ前** | LLM 呼び出し、外部 API、長時間処理の前にゲートを置く |
| **全ステップ配置は非効率** | 軽微な中間ステップごとに verifier を挟むとレイテンシが支配的になる |

### dotfiles での適用マップ

```
Plan → [Risk Analysis ← cheap verifier: plan-lifecycle.py]
  → Implement
    → [Test ← cheap + meaningful: unit test 自動実行]
      → [Review ← meaningful but costly: 並列 reviewer]
        → [Verify ← completion-gate.py: テスト実行済み確認]
          → [Security ← costly: security-reviewer agent]
```

**配置の ROI 判定**:
- `completion-gate.py`（Layer 0）: cheap + meaningful → **最高 ROI**
- `rationalization-scanner.py`: cheap（正規表現）+ meaningful（FM-018）→ **高 ROI**
- 並列 reviewer（Layer 1-2）: costly + meaningful → **必要だが頻度を制御**
- 全 Edit/Write への verifier: cheap だが semantically weak → **非推奨**
