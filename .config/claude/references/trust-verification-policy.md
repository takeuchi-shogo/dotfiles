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
