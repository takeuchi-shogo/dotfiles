---
status: active
last_reviewed: 2026-04-23
---

# AI Evals フレームワーク統合

**作成日**: 2026-03-12
**ステータス**: active
**規模**: L

## 概要

記事 "How to Build App-Specific AI Metrics" のフレームワークを dotfiles の AutoEvolve/review/hooks に統合する。

## 実装ステップ

### Phase 1: 基盤 (P1 → P2 → P0)

- [x] P1: Failure Taxonomy の明示化 — `references/failure-taxonomy.md`
- [x] P2: session_events.py に failure_type / failure_mode フィールド追加
- [x] P0-a: /review に findings 保存ステップ追加 (Step 5)
- [x] P0-b: review-feedback-tracker.py hook 新規作成 + settings.json 登録
- [x] P0-c: autolearn.md に feedback 分析 + Axial Coding セクション追加

### Phase 2: 分析 (P3)

- [x] P3: autolearn に accept_rate 計算ロジック追加（レポートフォーマット含む）
- [ ] P3: insights レポートに Evaluator 精度セクション追加（データ蓄積後に有効化）

### Phase 3: テスト (P4)

- [x] P4: Synthetic Tuple 定義 — `scripts/eval/reviewer-eval-tuples.json` (10タプル、4言語×5FM)
- [x] P4: Eval runner — `scripts/eval/run_reviewer_eval.py` (dry-run 確認済み)

## 設計判断

- **P0 アプローチ**: ハイブリッド（Git diff 自動検出 + 任意手動補正）
- **サブエージェント隔離**: hook は Python で軽量完結、深い分析は /improve 時に autolearn 委譲
- **P3/P4**: review-feedback.jsonl のデータ蓄積後に有効化
