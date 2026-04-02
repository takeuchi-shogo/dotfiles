---
source: "How to Vibe Code: A Developer's Playbook" (Mistral AI / Akshay Pachaar)
date: 2026-04-02
status: integrated
---

## Source Summary

**主張**: AI支援開発の成否はプロンプト技巧ではなく、エンジニアリング規律（仕様→計画→検証ループ）にかかる。RCTで熟練開発者がAIツールで19%遅くなったが本人は20%速くなったと感じた（40ポイントの認知ギャップ）。

**手法**:
1. Spec before prompt — Intent / Constraints / Acceptance criteria の3柱
2. Context engineering > prompt engineering — 新タスクで新セッション、JITコンテキスト取得
3. Plan → Execute → Verify ループ — 原子的タスク分割、具体的フィードバック
4. Testing as foundation — テストファースト、失敗確認してから実装
5. Security & review non-negotiable — セキュリティコンテキスト注入、自己反省ループ、サプライチェーン監視
6. Anti-patterns — 無限エラーループ / 理解せずマージ / セッションドリフト
7. Subagent context isolation — 検証をサブエージェントに委譲しメインコンテキストを保護
8. Skills as reusable workflows — Markdown定義のスラッシュコマンド
9. Agent modes (trust matching) — Plan / Default / Accept-edits / Auto-approve の4段階

**根拠**: RCT 40ポイントギャップ、AI生成コードの45%にセキュリティ脆弱性、AI共著PRで2.74x脆弱性率、170+本番アプリ露出事例

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Spec before prompt | Already | `/spec`, `/interview`, `overconfidence-prevention.md` |
| 2 | Context engineering | Already | Progressive Disclosure + `<important if>` + worktree |
| 3 | Plan → Execute → Verify | Already | S/M/L ワークフロー + Codex Gate + verification-before-completion |
| 4 | Testing as foundation | Already | `/autocover`, test-engineer agent, `rules/common/testing.md` |
| 5 | Security & review | Already | `/security-review`, security-reviewer agent |
| 6 | Anti-pattern: endless error loop | Already (強化可能) | Doom-Loop検出あり、検出後のガイダンスが薄い |
| 7 | Anti-pattern: comprehension gap | Already | `overconfidence-prevention.md` の委譲パターンチェック |
| 8 | Anti-pattern: session drift | Already | worktree + `/check-context` |
| 9 | Subagent context isolation | Already | `subagent-delegation-guide.md` + worktree |
| 10 | Skills as reusable workflows | Already | 60+ スキル |
| 11 | Agent modes (trust matching) | Partial → 統合済み | Trust Level マッピングを workflow-guide.md に追加 |
| 12 | Supply chain vigilance (slopsquatting) | Partial → 統合済み | slopsquatting チェック手順を security-reviewer に追加 |
| 13 | Security self-reflection loop | Partial → 統合済み | Pre-commit Security Self-check を workflow-guide.md に追加 |
| 14 | Productivity overconfidence (RCT data) | N/A | ユーザー側の認知バイアス。エージェント側は既カバー |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|-------------|---------------|--------|------|
| 6 | Doom-Loop 検出 (20fp/3rep) | 検出後に根本原因を特定せず再試行する | Recovery Protocol 追加 → 統合済み | 強化完了 |
| 1-5,7-10 | 各種仕組み | 記事の知見で強化不要 | なし | 強化不要 |

## Integration Decisions

選択: #6, #11, #12, #13 の全4項目

## Plan (実施済み)

| # | タスク | 対象ファイル | 変更内容 |
|---|--------|-------------|---------|
| T1 | Doom-Loop Recovery Protocol | `references/resource-bounds.md` | STOP→READ→DIAGNOSE→RE-PLAN の4ステップ追加 |
| T2 | Slopsquatting チェック | `agents/security-reviewer.md` | Supply chain risks に AI パッケージ実在確認手順追加 |
| T3 | Pre-commit Security Self-check | `references/workflow-guide.md` | Step 5.5 として5項目の自問チェックリスト追加 |
| T4 | Trust Level マッピング | `references/workflow-guide.md` | L1-L4 の4段階パーミッションモード選択ガイド追加 |
