---
status: reference
last_reviewed: 2026-04-23
---

# AutoHarness パターンカタログ

> Source: Lou et al. "AutoHarness: improving LLM agents by automatically synthesizing a code harness" (arXiv:2603.03329, 2026)

LLM エージェントの出力品質を **コードによる検証** で担保する 3 パターン。
ゲーム環境で実証されたが、ソフトウェア開発ハーネスにも概念的に適用可能。

---

## Pattern 1: Rejection Sampling Loop

**概要**: LLM 出力を生成 → コードで検証 → 不合格なら再生成。

```
propose(context) → validate(output) → accept / retry with feedback
```

**論文での実装**: `propose_action(obs)` → `is_legal_action(obs, action)` → 違法なら "illegal action" 警告付きで再生成。

**我々のハーネスとの対応**:

| 論文 | 当ハーネス | 差分 |
|------|----------|------|
| `is_legal_action()` | `golden-check.py` | golden-check は事後検出。rejection sampling ループ（再生成）は手動 |
| `propose_action()` | LLM の出力 | — |
| retry with feedback | `completion-gate.py` | ゲートは判定+failure info をフィードバック返却。ただし体系的な再生成ループは未構築 |

**適用ポイント**: hook が検出した問題を LLM にフィードバックし自動再生成するループを、将来的に一般化できる。現状は hook が検出 → ユーザーまたは LLM が手動修正。

---

## Pattern 2: Critic-Refiner Pipeline

**概要**: エラー分析（Critic）と改善提案（Refiner）を明示的に分離する 2 段階パイプライン。

```
Rollout → errors → Critic (aggregate & diagnose) → Refiner (propose fix) → New Code
```

**論文での実装**:
- Critic: 最大 5 件の失敗ステップとエラーメッセージを集約。エラーの種類（コード実行エラー vs 合法性違反）を分類
- Refiner: Critic の集約結果 + 元コードを受け取り、改善コードを生成

**我々のハーネスとの対応**:

| 論文 | 当ハーネス | 差分 |
|------|----------|------|
| Critic | `session-learner.py` | session-learner はセッション終了時に実行。リアルタイム集約ではない |
| Refiner | AutoEvolve の Propose フェーズ | `findings-to-autoevolve.py` は入力整形（findings→L1 Recovery Tips 変換）であり Refiner 自体ではない。改善提案生成は `/improve` の Propose が担う |

**適用ポイント**: AutoEvolve の Analyze → Propose フェーズで、エラー集約（何が問題か）と改善提案（どう直すか）を明示的に分離する。Critic の品質が Refiner の品質を決定する — "garbage in, garbage out" を防ぐ。

---

## Pattern 3: Code as Policy（知識蒸留）

**概要**: LLM の知識をコードに蒸留し、推論時に LLM 呼び出しを不要にする。

```
LLM knowledge → iterative code synthesis → standalone code (no LLM at runtime)
```

**論文での実装**: Gemini-2.5-Flash が Python コード（numpy 等の標準ライブラリのみ使用）を生成。16 ゲームで平均報酬 0.870、GPT-5.2-High (0.844) を上回り、推論コスト ≈ $0。

**我々のハーネスとの対応**:

| 論文 | 当ハーネス | 差分 |
|------|----------|------|
| LLM が policy コードを生成 | 人間が hook/script を記述 | 自動生成ではない |
| 反復的改善 | AutoEvolve の `--evolve` | 対象はスキル/エージェント定義であり、hook コード自体ではない |

**適用ポイント**: 将来的な方向性として、LLM が hook/script を自動生成・改善し、人間がレビューして採用するワークフローが考えられる。ただし現時点では hook の安全性・信頼性要件から人間による記述が妥当。

---

## 横断的洞察: Scaffolding > Model の定量的根拠

論文が示した最も重要な知見:

> **Harness-as-Policy (0.870) > GPT-5.2-High (0.844)**
> Harness-as-Policy は Gemini-2.5-Flash が生成した純粋な Python コード（推論時 LLM 不要）。
> 注: Flash+Harness（action filter）の 1P 平均報酬は 0.745。0.870 は Code as Policy バリアント。

小さいモデルが生成したコード > 大きいモデルの推論。これは我々の「Scaffolding > Model」原則を支持するデータ。
