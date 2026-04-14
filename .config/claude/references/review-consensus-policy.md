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

> **理論的根拠** (Tu 2026): 必要チェック数 m >= ln(W * epsilon_leaf) / (-ln delta_+) = O(log W)。
> delta_+ < 1（ベリファイアが完全盲目でない）が唯一の必須条件であり、m=2 でも指数抑制が機能する。
> ただし相関 rho が高い同種レビューアーでは有効独立数 m_eff = m/(1+(m-1)*rho) が 1 に近づく。
> 詳細: `references/structured-test-time-scaling.md` §4

### Heterogeneous Signal Priority

> Del et al. "How Uncertainty Estimation Scales with Sampling in Reasoning Models" (arXiv:2603.19118) の知見。
> 異なる種類の信号（内省 VC + 合意 SC）を 2 サンプル組み合わせた SCVC は、
> 同種信号を 8 サンプルまでスケールした場合を上回る（数学: 84.2 > 81.4/79.6 AUROC）。

**原則: 同種レビューアーの追加より、異種シグナルのレビューアーを優先する。**

> **実験的裏付け** (MemCollab, arXiv:2603.23234): 異アーキテクチャ間の対比メモリが同族対比を上回る。
> Qwen-2.5-32B + LLaMA-3-8B (cross-family): 95.2% vs Qwen-2.5-32B + Qwen-2.5-7B (same-family): 93.6%。
> 異なるアーキテクチャは相補的な推論パターンを露出し、モデル固有バイアスをより効果的に抑制する。

- ベースラインは code-reviewer（内省型: confidence スコア重視）+ codex-reviewer（推論型: 深い論理検証）の 2 体
- スペシャリスト追加時は、既存レビューアーと**異なる観点**を持つものを選ぶ（例: Logic 重視が 2 体いるなら Security を追加）
- 同じ観点のレビューアーを 3 体以上並べても、追加ゲインは急速に逓減する

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

### 不一致の分類: 異種 vs 同種

> Del et al. (arXiv:2603.19118): VC と SC の Kendall τ 相関は少サンプル時に低く（=相補的）、
> サンプル増加で収束する。相関が低い信号間の不一致は情報価値が高い。

不一致を検出した場合、まず**レビューアーの種類**で分類する:

| 不一致の種類 | 例 | 解釈 | アクション |
|-------------|-----|------|-----------|
| **異種間不一致** | code-reviewer (Style) vs security-reviewer (Security) | 異なる観点からの相補的情報。両方が正しい可能性が高い | 両指摘を併記し、ドメインごとに判断 |
| **同種間不一致** | code-reviewer vs codex-reviewer が同一ロジックで矛盾 | 真の矛盾。どちらかが誤り | Convergence Stall フラグ → ユーザー判断 |

異種間不一致は Agreement Rate 計算から除外する（異なるドメインの指摘は「矛盾」ではなく「補完」）。

### 段階的 Escalation

> context-and-impact の Ensemble Quality Gate（stddev>20 → collect_more）の応用。
> 即座に CONVERGENCE STALL とせず、追加レビューアーで合意改善を試みる。

Agreement Rate が中程度（70-89%）で同種間不一致が存在する場合、段階的に対応する:

| 条件 | アクション |
|------|----------|
| Agreement Rate 70-89% かつ同種間不一致 >= 2件 | 未参加のスペシャリスト1体を追加起動 |
| 追加レビュー後、Agreement Rate >= 70% | 通常合成（Conflicts セクション付き） |
| 追加レビュー後、Agreement Rate < 70% | CONVERGENCE STALL（下記の「対応」フロー） |

**制約**:
- 追加するレビューアーは §1 Reviewer Scaling Upper Bound を超えない
- 追加は1回のみ（escalation ループを防止）
- 追加するレビューアーは既存レビューアーと**異なる観点**を持つものを選ぶ（§1 Heterogeneous Signal Priority に従う）

### Confidence Inflation Alert

> Zhao et al. "Wired for Overconfidence" (arXiv:2604.01457, 2026-04):
> 言語化された信頼度は構造的に膨張する。全レビューアーが高 confidence を報告した場合、
> それは合意の質の証明ではなく、共有バイアスの表出である可能性がある。

**検出条件**: 全レビューアーが confidence >= 85% を報告し、かつ全員 PASS を出力

**アクション**:
- レポートに `[CONFIDENCE INFLATION RISK]` タグを付与
- 高信頼度であっても「検証済み」ではなく「高合意だが過剰自信リスクあり」と表記
- 可能なら外部検証（テスト実行、ドキュメント照合）を追加

§3 の Convergence Stall が**表面上の不一致**を検出するのに対し、この Alert は**表面上は健全に見える合意**のリスクを検出する。

### 3.1 Code Oscillation Detection（コード振り子検出）

> 記事 "ハーネスエンジニアリングで人間のコードレビューをやめる" (Akatsuki, 2026) の知見。
> Review-Fix サイクルで修正が振り子状に揺れ戻る（A→B→A パターン）問題を
> commit diff ベースで検出し、directive pinning で固定する。

**背景**: §3 の Convergence Stall Detection は**レビューアー間**の矛盾を検出するが、
**コード自体**が修正→再修正で元に戻るパターンは検出しない。
修正が振り子状に揺れると、Review-Fix サイクルの回数を消費するだけで品質が向上しない。

#### 検出方法

NEEDS_FIX / BLOCK で再レビューに入る際、以下を実行する:

1. 前回の修正 commit と今回の修正 commit の diff を取得
2. 前回の修正で **追加された行が今回削除されている**、または **前回削除された行が今回復活している** パターンを検出
3. 同一ファイル +-5行以内で revert パターンが **2箇所以上** ある場合、`[CODE OSCILLATION]` フラグを立てる

```
検出例:
  Cycle 1: funcA() を method に変更
  Cycle 2: method を funcA() に戻す ← revert detected
```

#### Directive Pinning

コード振り子を検出した場合:

1. 振り子の2つの状態（A と B）を特定
2. レビューアーの指摘を比較し、**より多くのレビューアーが支持した方**を採用
3. 支持が同数の場合は **capability-weighted score（§7）** が高い方を採用
4. 採用した方を `[DIRECTIVE]` として再レビューのプロンプトに注入し、以降の修正で遵守を義務付ける

```
[DIRECTIVE] file.ts:42 — funcA() をクラスメソッドとして維持すること。
理由: code-reviewer + codex-reviewer の2/3が支持。振り子を防止するため固定。
```

**制約**:
- Directive は当該 Review-Fix サイクル内でのみ有効（次のレビューセッションには引き継がない）
- Directive に対する新たな指摘は `[DIRECTIVE OVERRIDE REQUEST]` タグを付けてユーザーに判断を委ねる

### 対応

収束停滞を検出した場合:

1. 合成レポートの冒頭に `[CONVERGENCE STALL]` フラグを付与
2. 矛盾する指摘を Conflicts セクションに全て列挙（異種/同種を明記）
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

**IMPORTANT: codex-reviewer の指摘は Outlier 判定の対象外とする。**
Codex は deep reasoning (effort: xhigh) で他レビューアーが見落とす問題を検出する設計であり、
重複率が低いこと自体が期待された動作である。Codex の指摘は常に `[DEEP_REASONING]` タグで
verdict 計算に含める。Finding 重複率・指摘数の外れ値基準は codex-reviewer 以外のレビューアーにのみ適用する。

---

## 5. Verbosity Bias Mitigation

> 論文 "Expert Personas Improve LLM Alignment but Damage Accuracy" (arXiv:2603.18507) の知見に基づく。
> LLM-as-judge による pointwise 評価は長い回答を過大評価する（verbosity bias）。
>
> **補足 (2026-04-11)**: Mixture of Agents (MoA) アーキテクチャ自体にも verbosity failure mode が報告されている (Wang et al. "Mixture-of-Agents Enhances LLM Capabilities" ICLR 2025 Spotlight, arXiv:2406.04692 — failure mode #2)。マルチレビューア合成 (code-reviewer + codex-reviewer + gemini + ...) は MoA そのもので、Proposer 数が増えるほど出力が線形に冗長化しやすい。対策は review skill Step 4 Synthesis ルール 16 "Synthesis Output Verbosity Constraint"。Cross-MoA (異種レビューア優先) を採用する根拠は Li et al. "Rethinking Mixture-of-Agents" (arXiv 2025-02) で、Heterogeneous Signal Priority ポリシー (Section 1) と整合する。

### 問題

レビュー合成時、オーケストレータが「どちらのレビューアの指摘が妥当か」をペアワイズ比較する際、
長い・詳細な指摘が短い・簡潔な指摘より自動的に優先されるバイアスが存在する。

### 対策: 位置入替ペアワイズ比較

矛盾する指摘を比較する場合、以下の手順でバイアスを軽減する:

1. 指摘 A と指摘 B を `A → B` の順で提示し、どちらが妥当か判定
2. 順序を入れ替え `B → A` で再判定
3. **両方の順序で同じ指摘が勝った場合のみ**、その指摘を優先する
4. 順序で結果が変わった場合、バイアスの可能性があるため両方を併記してユーザーに判断を委ねる

### 適用条件

- Convergence Stall（セクション3）検出時の矛盾解消に使用
- Outlier（セクション4）判定の Severity 乖離確認に使用
- 通常の合成（Agreement Rate >= 90%）では不要

---

## 6. SCVC Hybrid Signal

> Del et al. "How Uncertainty Estimation Scales with Sampling in Reasoning Models" (arXiv:2603.19118) の知見。
> 内省的信号（confidence score）と合意的信号（agreement rate）を組み合わせると、
> いずれか単独をスケールするより大幅に識別力が向上する。

### 概念マッピング

| 論文の概念 | レビューシステムの対応物 |
|-----------|---------------------|
| Verbalized Confidence (VC) | 各レビューアーの confidence score (0-100) の平均 |
| Self-Consistency (SC) | agreement_rate（セクション 2） |
| SCVC | hybrid_score（以下の計算式） |

### 合成時の活用

verdict 判定時、agreement_rate と平均 confidence を**独立ではなく組み合わせて**評価する:

```
hybrid_score = 0.5 * normalized_agreement_rate + 0.5 * normalized_avg_confidence
```

- `normalized_agreement_rate`: agreement_rate をそのまま使用（0.0-1.0）
- `normalized_avg_confidence`: 全レビューアーの confidence score 平均 / 100（0.0-1.0）
- λ=0.5 は論文の感度分析で広範囲にロバストと実証済み

### 判定ガイド

| hybrid_score | 解釈 |
|-------------|------|
| >= 0.85 | 高信頼。合成結果をそのまま報告 |
| 0.70-0.84 | 中程度。Conflicts があれば明記 |
| < 0.70 | 低信頼。NEEDS_HUMAN_REVIEW を検討 |

---

## 7. Capability-Weighted Synthesis

> HACRL (arXiv:2603.02604) の知見に基づく。
> 能力差を無視した等価重み付けは特に困難なケースで大幅に劣化する (AIME2025 で -44%)。
> レビューアーのドメイン別 capability score で指摘を重み付けし、合成精度を向上させる。

### 適用条件

- **全てのレビューアー構成**（2体以上）で適用する
- 2体構成（code-reviewer + codex-reviewer）が最頻出であり、ここでの等価扱いは Codex の Logic 指摘（0.90）を code-reviewer と同じ重みにしてしまう。これは品質担保の観点で不適切

### スコア参照

`reviewer-capability-scores.md` の Score Table を使用する。

### 責務ドメイン軸との関係 (CREAO 統合 2026-04-14)

`triage-router.md` の 2 軸並列モデル（責務ドメイン × 言語 × 深さ）と本セクションの capability score は補完関係にある:

- **責務ドメイン軸** (triage-router) は「**誰を起動するか**」を決める (quality / security-if-risk / dependency-config)
- **capability score** (本セクション) は「**起動後の指摘をどう重み付けするか**」を決める

`dependency-config` 責務は `security-reviewer` が担当するが、その指摘は capability score 上では `Security` または `Architecture` ドメインにマッピングされる（dependency-config を独立カラムとして追加しない理由: 責務ドメインは task-routing 軸であり、品質ドメインは finding-classification 軸で直交）。

### 合成ルール

```
effective_weight(finding) = capability_score[reviewer][domain] * severity_multiplier
```

#### Severity Multiplier

| Severity | Multiplier |
|----------|-----------|
| Critical | 3 |
| Important | 2 |
| Watch | 1 |

#### 同一指摘の合算

同一ファイル +-10行以内 + 同一 failure_mode の指摘が複数レビューアーから出た場合、
effective_weight を合算する（HACRL の joint baseline に相当）。

```
合算例:
  codex-reviewer (Logic: 0.90) が Critical で指摘 → 0.90 * 3 = 2.70
  code-reviewer  (Logic: 0.80) が Critical で同一指摘 → 0.80 * 3 = 2.40
  合算 effective_weight = 2.70 + 2.40 = 5.10
```

#### 判定への影響

- effective_weight による重み付けは**優先順位の決定**に使用する
- verdict (PASS/NEEDS_FIX/BLOCK) の判定基準（ルール6）は変更しない
- Synthesis レポートの指摘一覧を effective_weight 降順でソートする
- 同一 severity 内での並び順を capability-weighted order にする

### Verbosity Bias との関係

Capability weighting は Section 5 (Verbosity Bias Mitigation) と併用する。
矛盾する指摘の比較時は、まず位置入替ペアワイズ比較（Section 5）で順序バイアスを除去し、
その上で capability score を判断材料に加える。

---

## 8. Reward Hacking Mitigation

> 出典: Anthropic "Multi-agent coordination patterns" (2026-04-10) §Generator-Verifier — Verifier の採点関数を Generator が学習し、表面的に PASS する出力を返す失敗モード。
>
> 関連: `references/multi-agent-coordination-patterns.md § Pattern 1 Generator-Verifier`

Generator-Verifier ループ（completion-gate / ralph-loop / Review-Fix サイクル）の最大の盲点は、**Verifier 自身の劣化** である。Verifier が形式的なパス基準で判定を続けると、Generator がその基準を学習して内容のない PASS を量産する。

§3 Convergence Stall Detection が**レビューアー間の矛盾**を、§3 Confidence Inflation Alert が**表面上の合意の過剰自信**を検出するのに対し、本セクションは**Verifier 自体が時間とともに緩む**問題に対処する。

### 検出シグナル（いずれか 1 つ以上で対処）

| # | シグナル | 検出方法 |
|---|---|---|
| 1 | 同一サイクル内で PASS 判定 → 直後の人手確認で FAIL | Review verdict と人間レビューの不一致記録 |
| 2 | ralph-loop / completion-gate で N サイクル連続 PASS | iteration 履歴で連続 PASS をカウント |
| 3 | 同種 Verifier の指摘が単調化（同じテンプレートのみ） | 同一 reviewer の複数 verdict 出力の差分が 90% 以上一致 |
| 4 | Generator が Verifier 出力を直接引用して「対応した」と報告 | diff コメントに verifier 文言の literal 引用 |

### 対応: 段階的 Escalation

| 状態 | アクション |
|---|---|
| シグナル #1-#3 を 1 回観測 | 次サイクルの Verifier プロンプトに「直前サイクルの判定が甘かった可能性。同じ基準を繰り返さず、新しい failure mode を探せ」を注入 |
| シグナル #1 を 2 回連続観測 | Verifier ペアの片方を異種に差し替え (`§1 Heterogeneous Signal Priority`)。例: code-reviewer → security-reviewer |
| シグナル #2 を観測（PASS 連続 N サイクル） | 人間監査を強制。下記 § 人間監査トリガー参照 |
| シグナル #3 / #4 を観測 | Verifier 基準を periodic update（下記 § Verifier 基準更新）|

### 人間監査トリガー

定期的な人間監査を Generator-Verifier ループに組み込む。トリガー条件:

| ループ種別 | トリガー | 監査内容 |
|---|---|---|
| `completion-gate.py` | MAX_RETRIES=2 を超えた回数の累計（5 回毎） | gate 通過後の成果物を人間が抜き取り検査 |
| `ralph-loop` (max-iterations=100) | **10 iteration 毎** に 1 回 | 直近 10 iteration の verdict と diff を抜き取り、PASS 連続が形式的でないか確認 |
| `/review` 並列 | 同一 reviewer が連続 5 PR で全 PASS | reviewer のチェックリストが現状コードベースに合っているか検証 |

監査結果はログに残し、`Verifier 基準更新` の入力にする。

### Verifier 基準更新（Periodic Update）

Verifier の判定基準は **時間とともに陳腐化する**。以下のタイミングで基準を見直す:

| トリガー | 更新対象 | 更新方法 |
|---|---|---|
| 上記検出シグナル #1-#4 のいずれか | 該当 Verifier の `references/review-checklists/` 該当ファイル | 検出された見落としケースを新しい check 項目として追加 |
| 月次 | 全 reviewer のチェックリスト | `/improve` サイクルで使用頻度の低い check 項目を整理、新規 failure_mode を追加 |
| アーキテクチャ大変更後 | 全関連 reviewer | 大変更で従来の check 項目が無関係化していないか確認 |

### ralph-loop 100 iteration 連続 PASS 警告

`ralph-loop` で max-iterations=100 まで全 PASS が出る場合、これは**成功ではなく警告シグナル**として扱う:

```
[REWARD HACKING WARNING] ralph-loop が N iteration 連続で PASS を返しています。
以下のいずれかの可能性があります:
  1. Verifier 基準が緩すぎる (false negative の量産)
  2. Generator が Verifier 基準を学習して形式的 PASS を返している
  3. 真にタスクが完了している (この場合のみ正常)

対応: 上記 § 人間監査トリガー の ralph-loop 行に従い、直近 10 iteration の
diff を抜き取り検査してください。
```

警告閾値: **連続 10 iteration 全 PASS** で警告タグを付与。20 iteration 連続で hard stop（人間判断を仰ぐ）。

### completion-gate との関係

`scripts/policy/completion-gate.py` の MAX_RETRIES=2 は **個別タスクの無限ループ防止** が目的で、Reward Hacking Mitigation とは別の防御線。Reward Hacking は**複数タスクにまたがる長期的な Verifier 劣化**を扱う。両者は補完関係。

---

## References

- arXiv:2603.01213 "Can AI Agents Agree?" (Berdoz et al., 2026)
- arXiv:2603.18507 "Expert Personas Improve LLM Alignment but Damage Accuracy" (Hu et al., 2026) — Verbosity bias mitigation
- arXiv:2603.02604 "Heterogeneous Agent Collaborative Reinforcement Learning" (Zhang et al., 2026) — Capability-weighted synthesis (Section 6)
- `reviewer-capability-scores.md` — Reviewer x Domain score table (Section 6)
- `agency-safety-framework.md` - Adversarial framing trade-offs section
- `failure-taxonomy.md` - FM-009 (Resource Exhaustion / Timeout)
