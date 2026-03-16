# Qodo 式レビュー強化 + Eval パイプライン実稼働

## 概要

Qodo のコードレビューベンチマーク記事の知見を dotfiles のレビュー基盤に統合する。
Recall 向上（観点別エージェント追加 + 信頼度3層化 + dedup）と、
定量計測基盤の実稼働（eval テストケース拡充 + ベースライン/改善後比較）の両方を実現する。

**着想元**: [Qodo Outperforms Claude in Code Review Benchmark](https://www.qodo.ai/blog/qodo-outperforms-claude-in-code-review-benchmark/)

## 背景

### 現状の課題

1. **Recall の盲点**: `code-reviewer` + `codex-reviewer` はロジックバグとベストプラクティスに強いが、エッジケースとクロスファイル依存の検出が弱い
2. **信頼度フィルタが攻撃的すぎる**: 60-79 の指摘を全て切り捨てており、有用な指摘も失われている
3. **重複排除が不十分**: 同一行の重複のみ処理。セマンティックに同じ問題の重複が残る
4. **eval 基盤が未稼働**: `run_reviewer_eval.py` + `evaluator_metrics.py` は設計済みだがドライラン止まり。テストケースも 10 件のみ

### Qodo の知見

- **観点別エージェント並列**: ロジックエラー、ベストプラクティス、エッジケース、クロスファイル依存の4観点で特化エージェントを並列実行
- **検証・重複排除ステップ**: 並列結果を検証→dedup→統合
- **Recall 重視**: 「Precision はフィルタで改善可能、Recall こそ本質」
- **マルチモデル**: 複数プロバイダの強みを動的に活用

## 設計

### 1. 新エージェント

#### `edge-case-hunter`

境界値・異常系・nil パス・空コレクション・ゼロ値など「正常系では通らないパス」の検出に特化。

**検出対象** (言語横断):
- 空配列/nil map への操作
- 整数オーバーフロー / ゼロ除算
- 文字列の空・Unicode・マルチバイト境界
- ファイル I/O のパーミッション・存在チェック漏れ
- タイムゾーン / 日付境界（月末、閏年）
- 並行処理のレースコンディション

**モデル**: Sonnet
**トリガー**: 全レビューで常時起動（エッジケースはどのコードにも潜む）

#### `cross-file-reviewer`

変更が他ファイルに与える影響の検出に特化。

**検出対象**:
- 関数シグネチャ変更 → 呼び出し元の未更新
- 型/インターフェース変更 → 実装側の不整合
- export 追加/削除 → import 側の破損
- 設定値変更 → 参照箇所の未追従
- DB スキーマ変更 → クエリ側の未対応

**モデル**: Sonnet
**トリガー**: 変更が 2 ファイル以上にまたがる場合（単一ファイル変更ではスキップ）

### 2. 信頼度3層化

現状の2層（80+ 表示 / 79以下 切り捨て）を3層に変更:

| 層 | スコア | ラベル | 扱い |
|----|--------|--------|------|
| Critical | 90-100 | 修正必須 | 変更なし |
| Important | 80-89 | 検討推奨 | 変更なし |
| **Watch** | **60-79** | **要注意（新設）** | 表示するが blocking にしない |

Watch 層の指摘に対するユーザーフィードバックを `review-feedback.jsonl` に記録し、AutoEvolve で閾値を学習する。

**Watch 層フィードバックスキーマ** (既存の accept/ignore スキーマを拡張):
```json
{
  "finding_id": "rf-2026-03-16-001",
  "outcome": "accepted" | "ignored" | "watch_useful" | "watch_noise",
  "confidence_tier": "critical" | "important" | "watch",
  "reason": "optional string"
}
```
- `watch_useful`: Watch 層の指摘がユーザーにとって有用だった（将来的に閾値引き上げの根拠）
- `watch_noise`: Watch 層の指摘がノイズだった（閾値維持 or 引き下げの根拠）
- 既存の `accepted` / `ignored` は Critical/Important 層で引き続き使用

**Watch 層と判定への影響**: Watch 層の指摘は PASS/NEEDS_FIX/BLOCK 判定に**影響しない**。Critical が1件以上 → BLOCK、Important が3件以上 → NEEDS_FIX、それ以外 → PASS。Watch はあくまで参考情報として表示のみ。

### 3. セマンティック Dedup + 信頼度ブースト

並列レビュー結果の統合時:

1. **セマンティック dedup**: 同一ファイル ±10行以内 + 同一 failure_mode → 最高信頼度の1件に統合
2. **クロスレビューアー信頼度ブースト**: 複数レビューアーが同じ問題を指摘 → `max(scores) + 5`（上限100）
3. **対立検出**: 同じ箇所で矛盾する指摘 → 両方残して `[CONFLICT]` タグ付与

### 4. レビューアールーティング更新

改善後のスケーリングマトリクス:

| 変更規模 | レビューアー |
|----------|-------------|
| ~10行 | スキップ |
| ~50行 | code-reviewer + codex-reviewer + **edge-case-hunter** |
| ~50行 (2+ファイル) | + **cross-file-reviewer** (コンテンツシグナルベース: diff のファイル数 ≥ 2) |
| ~200行 | + golang-reviewer (if .go) / 言語チェックリスト |
| 200行超 | + product-reviewer (if spec) + design-reviewer (if UI) |

### 5. Eval パイプライン実稼働

#### テストケース拡充: 10 → 30 件

Go 10 / TypeScript 10 / Python 10、各言語で以下の failure mode をカバー:

| FM | カテゴリ | 例 |
|----|----------|-----|
| FM-001 | nil/null 安全性 | nil map 書き込み、Optional 未チェック |
| FM-002 | サイレント失敗 | 空 catch、`_ = err` |
| FM-003 | 境界値 | off-by-one、空配列、ゼロ値 |
| FM-004 | 型安全性 | `any` 乱用、unsafe cast |
| FM-005 | インジェクション | SQL/XSS/コマンド注入 |
| FM-006 | レースコンディション | goroutine リーク、共有状態 |
| FM-007 | クロスファイル不整合 | シグネチャ変更の未追従 |
| FM-008 | エラーハンドリング | エラー情報の欠落、不適切な retry |
| FM-009 | リソースリーク | close 漏れ、defer 誤用 |
| FM-010 | ロジックバグ | 条件反転、短絡評価の誤り |

#### 計測メトリクス

各レビューアーに対して:
- **Recall**: 注入した問題のうち検出できた割合
- **Precision**: 指摘のうち実際に正しかった割合
- **F1**: Recall と Precision の調和平均
- **コスト**: 1レビューあたりの所要時間

#### モデル出力パース方式（Recall/Precision 算出）

eval スクリプトはレビューアーの出力を以下のルールでパースし、指摘数を算出する:

1. **指摘の検出**: `[MUST]`, `[CONSIDER]`, `[NIT]` プレフィクス、または `file:line` パターン（`foo.go:42`）を含む行を1件の指摘としてカウント
2. **FM マッチング**: 各指摘のテキストに含まれるキーワードを failure mode にマッピング（例: `nil`, `null`, `optional` → FM-001）。テストケースの `expected_fm` と照合
3. **Recall 分母**: テストケースに注入した既知の問題数（= テストケース数 = 30）
4. **Recall 分子**: 既知の問題のうち、対応する FM が出力に含まれていた件数
5. **Precision 分母**: レビューアーが出力した指摘の総数（上記パースで検出した件数）
6. **Precision 分子**: 指摘のうち、注入した FM に正しくマッチした件数

#### 実行フロー

```
reviewer-eval-tuples.json (30件)
  ↓
run_reviewer_eval.py (各レビューアーを個別に実行 + 出力パース)
  ↓
eval/results/YYYY-MM-DD-{reviewer}-eval.json
  ↓
eval/scripts/aggregate_benchmark.py (Recall/Precision/F1 算出 + 比較レポート生成)
  ↓
eval/results/YYYY-MM-DD-benchmark-report.md
  ↓
emit_benchmark.py → learnings/review-benchmarks.jsonl (AutoEvolve 連携)
```

**責務分離**:
- `run_reviewer_eval.py`: テストケース実行 + 出力パース + 個別結果 JSON 出力
- `eval/scripts/aggregate_benchmark.py`: **新規作成**。個別結果を集約し Recall/Precision/F1 算出、Before/After 比較レポート生成
- `emit_benchmark.py`: 既存。集約結果を AutoEvolve learnings に永続化
- `evaluator_metrics.py`: 既存。本番レビューの accept/ignore フィードバック集計（eval パイプラインとは独立）

#### Before / After 比較

1. 現行構成でベースライン計測 → Recall / Precision / F1 を記録
2. 新エージェント追加 + 信頼度3層化 + dedup 適用
3. 同じテストケースで再計測 → 差分を定量評価

**注意**: Step 3（ベースライン計測）完了前に Step 4〜6（新エージェント・ロジック変更）を適用しないこと。ベースライン汚染を防止するため。

## 変更対象ファイル

| ファイル | 変更内容 |
|----------|----------|
| `agents/edge-case-hunter.md` | **新規作成** |
| `agents/cross-file-reviewer.md` | **新規作成** |
| `skills/review/SKILL.md` | ルーティング追加、dedup ロジック、信頼度ブーストロジック、3層分類 |
| `skills/review/references/reviewer-routing.md` | ルーティング表更新、信頼度スコア表更新 |
| `skills/review/templates/review-output.md` | Watch 層テンプレート追加（判定には影響しない旨を明記） |
| `scripts/eval/reviewer-eval-tuples.json` | 10→30 テストケース拡充 |
| `scripts/eval/run_reviewer_eval.py` | 新レビューアー対応、出力パースロジック追加 |
| `scripts/eval/aggregate_benchmark.py` | **新規作成**。Recall/Precision/F1 算出 + Before/After 比較レポート |
| `scripts/lib/evaluator_metrics.py` | Watch 層フィードバックスキーマ対応（`watch_useful`/`watch_noise` outcome 追加） |

## 成功基準

- **Recall**: ベースラインから +10pt 以上の改善
- **Precision**: ベースラインから -5pt 以内に維持
- **F1**: ベースラインから +5pt 以上
- **Watch 層の有用率**: Watch 指摘の 30% 以上がユーザーにとって有用

## リスクと対策

| リスク | 対策 |
|--------|------|
| エージェント増でコスト倍増 | Sonnet 使用、cross-file は2ファイル以上のみ起動 |
| Watch 層がノイズだらけ | フィードバック蓄積後に閾値を段階調整 (60→65→70) |
| dedup が正当な別指摘を消す | `[CONFLICT]` タグで対立を保全 |
| eval テストケースが合成的すぎる | Qodo 公開データセットを参考に現実的なパターンを再現 |
| ベースライン汚染 | Step 3 完了前に Step 4〜6 を適用しない（実装ステップ注記参照） |

## 実装ステップ（依存順）

| Step | 内容 | 変更対象 | 依存 |
|------|------|----------|------|
| 1 | eval テストケース拡充 (10→30) | `scripts/eval/reviewer-eval-tuples.json` | なし |
| 2 | eval 実行スクリプト修正 + パースロジック | `scripts/eval/run_reviewer_eval.py` | Step 1 |
| 2b | 集約スクリプト新規作成 | `scripts/eval/aggregate_benchmark.py` | Step 1 |
| 3 | **ベースライン計測**（Step 4〜6 を適用する前に実行すること） | eval 実行 | Step 2, 2b |
| 4 | `edge-case-hunter` エージェント作成 | `agents/edge-case-hunter.md` | なし |
| 5 | `cross-file-reviewer` エージェント作成 | `agents/cross-file-reviewer.md` | なし |
| 6 | 信頼度3層化 + dedup + ブーストロジック | `skills/review/SKILL.md`, `reviewer-routing.md` | なし |
| 7 | `/review` スキルにルーティング追加 | `skills/review/SKILL.md` | Step 4, 5, 6 |
| 8 | review-output テンプレートに Watch 層追加 | `skills/review/templates/review-output.md` | Step 6 |
| 9 | 改善後の計測 | eval 実行 | Step 7, 8 |
| 10 | ベンチマーク比較レポート生成 | `eval/results/` | Step 3, 9 |
