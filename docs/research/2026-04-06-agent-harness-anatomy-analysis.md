---
source: "The Anatomy of an Agent Harness" by @akshay_pachaar
date: 2026-04-06
updated: 2026-04-07
status: integrated
---

## Source Summary

**主張**: Agent harness（LLMを包むインフラ全体）がモデル自体よりもエージェント性能を決定する。LangChainはハーネス変更のみで TerminalBench 2.0 で30位圏外→5位にジャンプ。

**手法**:
- 12コンポーネントモデル: Orchestration Loop, Tools, Memory, Context Management, Prompt Construction, Output Parsing, State Management, Error Handling, Guardrails, Verification Loops, Subagent Orchestration (+Ralph Loop)
- 7つのアーキテクチャ決定: single/multi-agent, ReAct/plan-and-execute, context strategy, verification design, permission model, tool scoping, harness thickness
- Build to Delete / Scaffolding metaphor: ハーネスはモデル改善で薄くなるべき過渡的技術
- Co-evolution principle: モデルはハーネスとセットで post-training
- Future-proofing test: モデル改善でハーネス複雑さ追加なしにスケールするか

**根拠**: TerminalBench 2.0（ハーネスのみで20+ランク変動）、ACON（26-54%トークン削減/95%+精度維持）、Boris Cherny（検証ループで品質2-3x向上）

**前提条件**: production-grade のエージェント開発。デモレベルでは不要なコンポーネントが多い。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Orchestration Loop | Already | completion-gate.py + S/M/L ワークフロー |
| 2 | Tools (6カテゴリ) | Already | File/Search/Exec/Web/CodeIntel/Subagent + MCP |
| 3 | 3層メモリ | Already | MEMORY.md → topic files → transcripts |
| 4 | Memory as hint | Already | memory instructions に明記 |
| 5 | Context rot 対策 | Already | wiki, compaction policy, sub-agent delegation |
| 6 | Prompt Construction | Already | system + tools + CLAUDE.md + memory + history |
| 7 | Output Parsing | N/A | プラットフォーム側機能 |
| 8 | State Management | Already | /checkpoint, checkpoint_recover.py |
| 9 | Error type 4分類 | Partial | 6カテゴリ+FM codes あるが recovery strategy 未紐付け |
| 10 | Guardrails (3層) | Already | tool-scope-enforcer, protect-linter-config 等 |
| 11 | Verification Loops | Already | verification-before-completion + /review + LLM-as-Judge |
| 12 | Subagent Orchestration | Already | model routing + worktree + background agents |
| 13 | Ralph Loop | Already | plugin + completion-gate.py 統合 |
| 14 | Build to Delete | Already | CLAUDE.md core principles |
| 15 | Tool scoping | Already | tool-scope-enforcer + lazy-loaded skills |
| 16 | Co-evolution / Future-proofing test | Gap | 定期検証プロセスなし |
| 17 | 定期ハーネス簡素化監査 | Gap | Build to Delete のオペレーション化なし |
| 18 | Runtime/Harness Logic 分離 | Already | agent-harness-contract.md |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|--------------|--------|
| A1 | Error handling (6カテゴリ+FM) | recovery strategy が型に紐づいていない | FM に recoveryType フィールド追加 |
| A2 | Context management | Observation masking 未実装 | context-compaction-policy.md に参照追記 |
| A3 | Tool scoping | 定期的なツール使用量監査なし | /audit に Tool Usage Audit セクション追加 |
| A4 | Verification loops | — | 強化不要。3種すべてカバー済み |
| A5 | Build to Delete | 「いつ削除するか」のトリガー未定義 | Gap #17 と統合 |

## Integration Decisions

全項目を取り込み:

- **Gap #9 (Partial)**: FM-001〜FM-020 に recoveryType フィールドを追加
- **Gap #16+#17**: harness-simplification-checklist.md を新規作成（Co-evolution test + 定期棚卸し統合）
- **強化 A2**: context-compaction-policy.md に Observation Masking セクション追記
- **強化 A3**: /audit SKILL.md に Tool Usage Audit (Step 4.5) 追加

## Plan

### Round 1 (2026-04-06)

| # | タスク | ファイル | 状態 |
|---|--------|---------|------|
| T1 | FM に recoveryType 追加 | references/failure-taxonomy.md | Done |
| T2 | Observation masking 参照追記 | references/context-compaction-policy.md | Done |
| T3 | ハーネス簡素化チェックリスト | references/harness-simplification-checklist.md | Done |
| T4 | Tool Usage Audit セクション | skills/audit/SKILL.md | Done |
| T5 | 分析レポート保存 | docs/research/2026-04-06-agent-harness-anatomy-analysis.md | Done |

### Round 2 (2026-04-07) — 再分析で発見した追加項目

| # | タスク | ファイル | 状態 |
|---|--------|---------|------|
| T6 | ACON compaction 優先順位テーブル追加 | references/context-compaction-policy.md | Done |
| T7 | ツール数閾値 + エラー複合則 追加 | references/resource-bounds.md | Done |
| T8 | ステップ追加時のエラー複合コスト評価参照 | references/workflow-guide.md | Done |
| T9 | Co-evolution ツール定義安定性セクション追加 | references/harness-simplification-checklist.md | Done |
