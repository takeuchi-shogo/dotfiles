---
status: active
last_reviewed: 2026-04-23
---

# AI Evals フレームワーク × dotfiles リポジトリ 分析レポート

**調査日**: 2026-03-12
**ソース**: "How to Build App-Specific AI Metrics" (Error Analysis → Failure Modes → App-Specific Metrics → Evaluator Alignment)
**対象**: dotfiles リポジトリの AutoEvolve, hooks, review, skill-audit 等

---

## 全体マッピング

| 記事のステップ | dotfiles での対応 | 成熟度 |
|---|---|---|
| 1. Error Analysis (Open/Axial Coding) | AutoEvolve 学習収集 + autolearn 分析 | **部分実装** |
| 2. Failure Modes → Metrics | importance scoring + GP-001~005 | **部分実装** |
| 3. Code-Based vs LLM-as-Judge | hooks (regex) + review agents (LLM) | **十分実装** |
| 4. Evaluate the Evaluators (TPR/TNR) | skill-audit のみ | **未実装** |

---

## 1. 既に実装されているもの（強み）

### A. 二層評価アーキテクチャ — 記事の推奨と完全一致

記事は「Code-Based Evals」と「LLM-as-Judge Evals」の使い分けを推奨している。dotfiles はこれを既に高い水準で実装済み。

| 層 | 実装 | 特徴 |
|---|---|---|
| **Code-Based** | `golden-check.py`, `protect-linter-config.py`, `completion-gate.py`, `error-to-codex.py` | regex ベース、決定論的、高速、安価 |
| **LLM-as-Judge** | `code-reviewer`, `security-reviewer`, `product-reviewer`, `design-reviewer`, `silent-failure-hunter` 等 | 意味的分析、並列実行、confidence スコア付き |
| **Hybrid** | `error-to-codex.py` + `error-fix-guides.md` | regex 検出 → fix guide 注入 → codex-debugger 提案 |

### B. 継続的学習ループ — 記事の「止まるな」思想を体現

記事の結論「You can never stop looking at data」に対して、AutoEvolve の4層ループ（Session → Daily → Cron → On-demand）がこれを自動化している:

```
emit_event() → current-session.jsonl → session-learner.py → learnings/*.jsonl
    → autolearn (分析) → knowledge-gardener (整理) → autoevolve (改善提案)
```

### C. Confidence-based フィルタリング

記事が推奨する「binary pass/fail から始めよ」に対して、レビューシステムは confidence 0-100 のスコアリングに加え、**80未満を自動除外**するフィルタを持っている。これは記事の「Start with binary checks」の実質的な実装。

### D. Content-Signal ベースのスペシャリスト自動選択

`/review` スキルが diff の内容シグナル（catch ブロック → silent-failure-hunter、型定義 → type-design-analyzer、UI 変更 → design-reviewer）で専門レビューアーを自動起動するのは、記事の「each evaluator tackles a single failure mode」に近い設計。

---

## 2. 活かせるもの（改善機会）

### A. Specification Failure vs Generalization Failure の区別 — 最大のギャップ

記事の最も実用的な洞察は「失敗を2種類に分類せよ」:

| 種類 | 意味 | アクション |
|---|---|---|
| **Specification Failure** | 指示（プロンプト）が曖昧/不完全 | プロンプトを修正。Evaluator は不要 |
| **Generalization Failure** | 明確な指示を正しく実行できない | Evaluator を構築 |

**現状の問題**: `session_events.py` の4カテゴリ（error, quality, pattern, correction）にはこの区別がない。エラーが「プロンプトの曖昧さ」起因か「LLM の実行能力不足」起因か分からないため、autoevolve が「プロンプト改善」と「ルール追加」のどちらを優先すべきか判断できない。

**改善案**: `correction` カテゴリに `failure_type: "specification" | "generalization"` フィールドを追加し、autolearn の分析で分岐させる。

### B. Open Coding → Axial Coding の体系化 — autolearn の質的向上

記事の質的研究手法:

```
Step 1: トレース読み取り → 自由記述メモ（Open Coding）
Step 2: 類似メモをクラスタリング（Axial Coding）
Step 3: 失敗モードの定義を確定
Step 4: 全トレースを再コーディング → 理論的飽和まで繰り返す
```

**現状の問題**: `autolearn` エージェントは頻度カウント（3回以上 → recurring）で分析しているが、記事が推奨する「クラスタリングによる失敗モードの発見」は行っていない。同じ regex パターンに一致するエラーは同一カテゴリとして扱われるが、意味的に異なる失敗モードが同じカテゴリに混在している可能性がある。

**改善案**: autolearn に「Axial Coding フェーズ」を追加。learnings の蓄積が一定量（例: 50件）を超えたら、LLM でクラスタリングし、新しい失敗モードを `insights/failure-taxonomy.md` として生成。その taxonomy を次の分析サイクルで使う反復ループ。

### C. Evaluator の信頼性測定（TPR/TNR）— 最も欠落している仕組み

記事の核心メッセージ: **「Judge を Judge する仕組みがなければ、Judge は信頼できない」**

**現状**:
- `skill-audit` はスキルの有無で品質を A/B 比較するが、**レビューエージェントの精度**は測定していない
- `code-reviewer` が出した指摘が本当に正しいか、false positive がどれだけあるかを追跡する仕組みがない
- confidence < 80 のフィルタは経験的な閾値であり、データに基づいていない

**改善案**:
1. レビュー指摘に対するユーザーのアクション（修正した / 無視した / 反論した）を追跡
2. `accept_rate = 修正した / 全指摘数` をレビューエージェントごとに計測
3. 一定期間のデータが溜まったら、TPR/TNR を近似計算
4. 閾値（現在の 80）をデータに基づいて調整

### D. Synthetic Tuple による網羅的テスト

記事の手法: `(feature × persona × scenario)` の組み合わせでテストケースを自動生成。

**現状**: `skill-audit` は3種のプロンプト（clear-trigger, borderline, domain-depth）を生成するが、**レビューエージェント自体のテスト**には使っていない。

**改善案**: レビューエージェント用に `(言語 × 失敗モード × 深刻度)` のタプルを生成し、意図的にバグを含むコードで評価。例:

```
(TypeScript × empty-catch × critical)  → silent-failure-hunter が検出すべき
(Go × nil-pointer × high)              → code-reviewer + nil-path が検出すべき
(React × a11y-missing × medium)        → design-reviewer が検出すべき
```

---

## 3. 改善が必要なもの（具体的なギャップ）

### A. Failure Taxonomy の明示的定義がない

現状は regex パターンのリスト（`IMPORTANCE_RULES`）が暗黙的な failure taxonomy として機能しているが、記事が求める「small, coherent, non-overlapping set of binary failure types」にはなっていない。

```
現状: 15個の regex パターン → importance スコア
    (意味的に重複するパターンがある: "build failed" と "compilation failed" は同じ失敗モード？)

記事が求める形:
    FM-001: Null Safety Violation — nullable値の未チェックアクセス
    FM-002: Error Suppression — catch/except で黙殺
    FM-003: Dependency Drift — 暗黙の依存追加
    ...
    各失敗モードが binary (pass/fail) で判定可能
```

### B. Event の promotion_status が活用されていない

全イベントに `"promotion_status": "pending"` が付与されるが、`knowledge-gardener` が promotion 提案するまで実質的に未使用。記事のフレームワークでは、十分なデータが溜まった失敗モードから順に Evaluator を構築する進行フローがあるが、dotfiles では promotion パスが手動承認待ちで停滞しやすい。

### C. レビュー結果のフィードバックループが閉じていない

```
現在のフロー:
  /review → 指摘生成 → ユーザーが読む → (修正するかしないか) → END

欠落しているフロー:
  /review → 指摘生成 → ユーザーが修正/却下 → 結果を learnings に emit
      → autolearn が指摘精度を分析 → autoevolve がレビュープロンプトを改善
```

レビュー指摘の「受け入れ率」がデータとして蓄積されないため、AutoEvolve がレビューシステム自体を改善できない。

---

## 4. 優先度付き改善ロードマップ

| 優先度 | 改善項目 | 影響度 | 実装コスト | 記事との対応 |
|---|---|---|---|---|
| **P0** | レビュー結果のフィードバックループ | 高 | M | Eval the Evals |
| **P1** | Failure Taxonomy の明示化 | 高 | S | Axial Coding |
| **P2** | Spec vs Generalization の分類 | 中 | S | Failure Type Analysis |
| **P3** | Evaluator 精度測定 (accept_rate) | 高 | L | TPR/TNR |
| **P4** | Synthetic Tuple テスト | 中 | L | Synthetic Data |

---

## 5. まとめ

dotfiles の既存システムは記事のフレームワークの**前半（Error Analysis + Evaluator 二層構造）を高い水準で実装済み**。特に AutoEvolve の学習ループと、Code-Based / LLM-as-Judge の二層レビューは記事の推奨と完全に一致している。

最大のギャップは**後半（Evaluator の信頼性検証）**にある。記事の核心メッセージ「AI evals isn't engineering. It's product judgment.」が示す通り、重要なのは「レビューアーが出した指摘は本当に正しいのか？」を測定する閉じたフィードバックループ。これが実装されれば、AutoEvolve がレビューシステム自体を自己改善できるようになり、記事が言う「85%に入らないチーム」になる。

---

## 参考: 記事のキーコンセプト

### Error Analysis の4ステップ
1. **Sampling**: LLM トレースをサンプリング
2. **Open Coding**: 各トレースに問題・驚き・不正確な動作のメモ
3. **Axial Coding**: 類似メモをクラスタリング → 失敗モード定義
4. **Re-Coding**: 全トレースを失敗モードで再コーディング → 理論的飽和まで反復

### Evaluator の2種類
- **Code-Based Evals**: ルールベース（XML/SQL/Regex）、高速・安価・決定論的
- **LLM-as-Judge Evals**: 単一の失敗モード、binary pass/fail、主観的チェック向き

### Failure Type の2分類
- **Specification Failure**: 指示が曖昧 → プロンプトを修正
- **Generalization Failure**: 指示は明確だが実行失敗 → Evaluator を構築

### Evaluator の信頼性指標
- **TPR (True Positive Rate)**: Judge が Pass と言った時、人間も Pass → 最重要
- **TNR (True Negative Rate)**: Judge が Fail と言った時、人間も Fail
