---
status: active
last_reviewed: 2026-04-23
---

# Comprehension Debt Integration Plan

**Source**: [Addy Osmani - Comprehension Debt](https://addyosmani.com/blog/comprehension-debt/)
**Size**: L (6 tasks, 8+ files)
**Status**: completed

## Overview

AI生成コードの「理解債務」に対する6つの防御メカニズムを既存ワークフローに統合する。

## Tasks

### Task 1: Design Rationale Gate (pre-review)

**Files**: `references/comprehension-debt-policy.md` (new), `agents/code-reviewer.md` (edit), `skills/review/SKILL.md` (edit)

レビュー開始前に実装者が設計意図を3行で記述する義務を追加。

```
## Design Rationale (required for M/L changes)
1. **What**: この変更は何を解決するか
2. **Why this approach**: なぜこのアプローチを選んだか（却下した代替案含む）
3. **Risk mitigation**: 何が壊れうるか、どう防いでいるか
```

- review SKILL.md の Step 1 (Pre-analysis) 後に「Design Rationale 確認」ステップ追加
- code-reviewer の ASK カテゴリに「rationale が不十分な場合は MUST に昇格」ルール追加
- M/L 変更のみ適用（S は免除）

### Task 2: Tautological Test Detection

**Files**: `agents/test-analyzer.md` (edit), `rules/common/comprehension-debt.md` (new)

同一セッションで実装とテストを同時生成した場合の検出・警告。

- test-analyzer に「テストが実装の鏡像になっていないか」チェック追加:
  - テストが実装の内部構造に依存していないか
  - テストが「何を」検証しているか vs「どう」実装されているか
  - assertion が具体的な値ではなく実装の戻り値をそのまま使っていないか
- `rules/common/comprehension-debt.md`: tautological testing の Bad Example 併記

### Task 3: Comprehension Metrics

**Files**: `references/improve-policy.md` (edit)

improve-policy に comprehension 関連メトリクスを追加。

- **design_revision_rate**: レビュー指摘で設計変更が必要になった割合（高い = 理解不足）
- **repeated_investigation_count**: 同じコード領域を複数セッションで繰り返し調査（stagnation-detector と連携）
- **spec_slop_detection_rate**: overconfidence-prevention の Spec Slop 検出頻度

### Task 4: Passive Delegation Detection

**Files**: `rules/common/comprehension-debt.md` (append), `rules/common/overconfidence-prevention.md` (edit)

「丸投げ」パターンの定義と検出基準を明文化。

受動的委譲の兆候:
- AI 出力をレビューせず即 accept
- 「とりあえず動いたからOK」で設計意図を説明できない
- エラー時に自分で調査せず AI に「直して」と丸投げ

overconfidence-prevention に「委譲パターンチェック」セクション追加:
- 「この変更の設計意図を説明できますか？」の自問を促すガイダンス

### Task 5: Spec Review Gate Enforcement

**Files**: `references/workflow-guide.md` (edit)

M/L タスクで `/spec` 通過を必須化する。

workflow-guide.md のワークフローテーブル更新:
- M: `Spec Review → Plan → Risk Analysis → Implement → Test → Verify`
- L: `Spec Review → Plan → Risk Analysis → Implement → Test → Review → Verify → Security Check`

Spec Review の定義:
- overconfidence-prevention の 6 Slop 指標をパス
- 曖昧な要件が 0 になるまで質問で解消
- S は免除（変更が自明）

### Task 6: Review Thoroughness Signal

**Files**: `skills/review/SKILL.md` (edit)

変更規模に対するレビューの網羅性チェック。

- review orchestrator の Synthesis ステップに「coverage check」追加
- 変更ファイル数 vs レビューで言及されたファイル数の比率を出力
- 大規模変更（100行超）で全ファイルに言及がない場合は警告
- comprehension_confidence スコア (1-5) をレビュー出力テンプレートに追加

## Dependencies

```
Task 1 (Design Rationale) ← independent
Task 2 (Tautological Test) ← independent
Task 3 (Comprehension Metrics) ← independent
Task 4 (Passive Delegation) ← independent
Task 5 (Spec Gate) ← independent
Task 6 (Review Thoroughness) ← depends on Task 1 (rationale format)
```

## Execution Strategy

Task 1-5 は独立。並列実行可能。
Task 6 は Task 1 の rationale フォーマット確定後に実装。

**推奨**: 新セッションで `/rpi` を使い、Task 1-5 を並列エージェントで実行 → Task 6 を逐次実行。
