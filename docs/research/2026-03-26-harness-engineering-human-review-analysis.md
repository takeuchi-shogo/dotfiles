---
source: https://zenn.dev/theaktky/articles/1c6c3b9333117c
date: 2026-03-26
status: integrated
---

## Source Summary

### 主張
意思決定を伴わないコード品質チェックは人間のレビューが不要であり、AIに完全に任せるべき。AIを安定運用するにはモデル単体の能力ではなく「ハーネスエンジニアリング」という環境設計が重要。

### 手法
1. **5ステップレビューループ**: Review→Triage→Fix→Validate→Commit (max 6回)
2. **Severity トリアージ**: CRITICAL/IMPORTANT/LOW分類、LOW破棄
3. **オシレーション検出**: commit diff から A→B→A パターン検出、directive pinning で固定
4. **スコープ判定**: 未変更コードの指摘除外
5. **モデル役割分離**: Codex=精度(レビュー/修正)、Composer=広域探索(トリアージ/検証)
6. **別セッション検証**: 根本原因 vs バンドエイド修正の明示判定
7. **Rigg ツール**: YAML ワークフロー定義で再現性確保
8. **コーディングガイドライン参照**: 判断基準のハードコード回避
9. **ゼロ指摘ループ終了条件**
10. **ハーネス4役割**: Constrain, Inform, Verify, Correct

### 根拠
- LangChain事例: モデル変更なしでハーネス改善だけで52.8%→66.5%に向上
- 人間の限界(一部把握、疲労、遠慮) vs AI優位性(全体を一貫基準で評価)

### 前提条件
- 意思決定を伴わない「コード品質チェック」段階での使用
- 概念・設計方針は確定後
- チームでコーディングガイドラインが存在

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 7 | Rigg ツール (YAML ワークフロー定義) | N/A | hooks ベースのオーケストレーションで同等機能を実現済み |

### Already 項目の強化分析

| # | 手法 | 既存の仕組み | 記事が示す新知見 | 強化案 |
|---|------|-------------|-----------------|--------|
| 1 | 5ステップループ (max 6) | Review-Fix cycle (max 3) | max 6 + 独立 Triage ステップ | 強化不要 — 3回で収束しなければ人間判断が妥当 |
| 2 | Severity トリアージ | Critical/Important/Watch + confidence<60 除外 | CRITICAL/IMPORTANT/LOW、LOW破棄 | 強化不要 — 既存の方がより精密 |
| 3 | オシレーション検出 | Convergence Stall Detection（レビューアー間の矛盾検出） | commit diff から A→B→A パターンを検出し directive pinning | **強化** — review-consensus-policy.md §3.1 にコード振り子検出を追加 |
| 4 | スコープ判定 | Synthesis Rule 8: diff 追加行以外の指摘を除外 | 未変更コード指摘除外 | 強化不要 — 完全カバー |
| 5 | モデル役割分離 | code-reviewer(内省) + codex-reviewer(推論) | Codex=精度、Composer=広域 | 強化不要 — 同等設計 |
| 6 | 別セッション検証 | Review-Fix cycle の再レビュー | 根本原因 vs バンドエイド明示判定 | **強化** — /review Step 5 にバンドエイド検出チェックを追加 |
| 8 | ガイドライン参照 | references/, rules/, review-checklists/ | 判断基準のハードコード回避 | 強化不要 |
| 9 | ゼロ指摘終了 | Critical/Important=0 → PASS | 指摘ゼロでループ終了 | 強化不要 |
| 10 | ハーネス4役割 | PreToolUse/SessionStart/Stop/PostToolUse | Constrain/Inform/Verify/Correct | 強化不要 |

## Integration Decisions

- **#3 コード振り子検出**: 取り込み。review-consensus-policy.md §3.1 に追加
- **#6 バンドエイド検出**: 取り込み。/review SKILL.md Step 5 に追加

## Plan

### Task 1: コード振り子検出 (S)
- **ファイル**: `.config/claude/references/review-consensus-policy.md`
- **変更**: §3 の後に §3.1 "Code Oscillation Detection" を追加
- **内容**: NEEDS_FIX 再レビュー時に前回修正との diff を取り、revert パターンを検出。検出時は directive を固定

### Task 2: Fix-Validate ゲート (S)
- **ファイル**: `.config/claude/skills/review/SKILL.md`
- **変更**: Step 5 に Fix-Validate ゲートを独立ステップとして追加
- **内容**: Fix と Re-Review の間に軽量な修正品質チェック（根本原因対処/スコープ適切性/副作用リスク）を挟む。バンドエイド検出はこのステップに統合。不適切な修正は Re-Review に回す前に自己修正（1回のみ）。記事の「検出と分類は異なる認知タスク」という知見に基づき、Re-Review（新問題探索）と Validate（修正品質検証）を問いのレベルで分離
