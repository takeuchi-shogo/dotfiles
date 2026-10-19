---
status: reference
last_reviewed: 2026-10-19
---

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

4. **壊した版で必ず失敗すること（verifier 感度）** — 対象は **新しく導入するチェック** に限る
   - 新しい検証（テスト・ゲート・形式チェック・生成した verify skill）を導入するときは、守る性質を意図的に壊した変種で一度失敗を確認する
   - **新規導入時に** 失敗を見たことがないチェックは「通るだけの儀式」であり、**その新規チェックを** Layer 0 として信頼しない
   - 既存の Layer 0（lint / typecheck / 既存テスト / `completion-gate.py` の実行済み確認）やルール 1・2 を無効化しない。感度未証明の新規チェックが、既に動いている決定論ゲートの優先順位を下げたり「未実行扱い」にしたりはしない
   - 出典の考え方: pstack `/create-formal-verification-skill` の "Able to fail"（研究メモ `docs/research/2026-10-19-pstack-formal-verification-absorb-analysis.md`）。meta-skill 本体は未移植

5. **検証範囲を正直に書く**
   - Pass の報告には、何を・どの境界/仮定の下で検証したか、何を見ていないかを添える
   - モデル・バウンド・モック境界の外まで「システム全体が正しい」と言い切らない
   - 出典の考え方: 同上 "Honest about scope"。完了宣言の evidence 契約を具体化したもの

6. **検証結果は三値。INCONCLUSIVE を PASS / 完了扱いにしない**
   - 主張・変更単位の判定は `VERIFIED` / `NOT VERIFIED` / `INCONCLUSIVE` のどれか一つにする
   - **必須** validation が環境要因で実行できない・比較が無効なときは `INCONCLUSIVE`。完了や「問題なし」に読み替えない
   - **Fail と INCONCLUSIVE が混在したら Fail（NOT VERIFIED）を優先**する
   - **必須 / optional / SKIP（対象外）** — 「対象外」はこの意味だけ:
     - **必須**: 変更種別に対し Dotfiles Hints / Taskfile / CI / 当該 playbook・skill が要求するもの
     - **optional**: 文書が「未導入時は skip 可」と明記した optional binary、または変更面に無関係なチェック
     - **SKIP** = 対象外（optional または変更面に無関係）。三値の外。VERIFIED / PASS の根拠にしない
     - 自分で optional と宣言しただけでは SKIP できない。必須が実行できないなら SKIP ではなく INCONCLUSIVE
   - 境界（完了宣言 skill と同型）:
     - **環境起因**の失敗（測定基盤ダウン、環境差で比較不能など）→ `INCONCLUSIVE`
     - **変更そのものが原因**の ImportError・構文エラー・テスト Fail → `NOT VERIFIED`（Fail）。INCONCLUSIVE にしない
     - 必須チェックの一部だけ Pass、他が Fail → `NOT VERIFIED`（Fail 優先）
     - 主張と無関係な箇所だけ Pass（主張面を測っていない）→ `INCONCLUSIVE`
   - 出典の考え方: pstack `/figure-it-out` Phase C（`docs/research/2026-10-19-pstack-formal-verification-absorb-analysis.md` 追記節）。隣接実装: Cursor `verify-this` skill。本ルールに hook / gate 強制は無い（ルール 4・5 と同じ文書規律）

### 既存判定語彙との対応（ルール 6）

| 既存語彙 | 役割 | 三値との関係 |
|----------|------|--------------|
| Layer 0 Pass / Fail | 決定論チェックの生結果 | Pass は VERIFIED の材料、Fail は NOT VERIFIED の材料。単体で完了宣言の三値全体にはならない |
| ルール 1 の reviewer PASS / BLOCK | Layer 1-2 の合意・拒否 | ルール 1 の BLOCK は、主に **Layer 0 のテスト失敗が reviewer PASS を上書きする**ときの完了拒否（NOT VERIFIED 寄り）。reviewer PASS でも Layer 0 Fail やテスト未実行があれば完了にしない |
| `/review` の PASS / NEEDS_FIX / BLOCK / NEEDS_HUMAN_REVIEW | レビュー合成 verdict | 別軸。三値は「主張の実証」。テスト未実行時は review PASS でも完了にせず **警告を付加**する（ルール 2 / review SKILL） |
| `completion-gate.py` | 決定論の block / allow | 三値を機械強制しない。`CLAUDE_SKIP_TEST_GATE=1` はゲート全体を無効化する抜け道（PASS 扱いの根拠にしない。本 PR では未修正） |

## 適用箇所

- `completion-gate.py`: Layer 0 チェック（テスト実行済み確認）を Review Gate より前に配置
- `/review` Step 4 Synthesis: テスト未実行時は verdict に警告を付加
- `rationalization-scanner.py`: PostToolUse(Agent) で FM-018 パターンを検出
- `derivation-honesty-hook.py`: PostToolUse(Bash|Write|Edit) で FM-016 パターンを検出
- **ルール 4・5・6 に対応する hook / gate / 自動強制は無い**（2026-10-19 時点）。文書上の導入規律であり、`completion-gate.py` やルール 1・2 の機械的強制とは別レイヤ。強制が必要になったら別タスクで仕組みを足す
- Codex 完了前検証: `.agents/skills/codex-verification-before-completion/SKILL.md` がルール 6 の三値を完了宣言側で参照する

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
