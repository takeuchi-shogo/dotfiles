---
source: https://github.com/MiniMax-AI/skills
date: 2026-03-23
status: analyzed
---

## Source Summary

MiniMax-AI/skills は AI コーディングエージェント向けスキルライブラリ（MIT, Star 1,583, 2026-03-17 作成）。
10スキル収録。Claude Code / Cursor / Codex / OpenCode の4ツール対応。

**主張**: ドメイン知識を「百科事典型スキル」として構造化し、Decision Table・Anti-Patterns テーブル・Mandatory Workflow の3パターンで LLM の判断を規定できる。

**手法**:
- Decision Table: 技術選択肢を表形式で整理し「When」列で判断基準を明示
- Anti-Patterns テーブル: 番号付き ❌/✅ 対比で制約を簡潔に表現
- Mandatory Workflow: Step 0~N の強制手順でスキル発火後の行動を規定
- Scope 明示: SKILL.md 本文に USE / NOT FOR を記載
- マルチ言語コード例: 同一パターンを TS/Python/Go で提示
- Metadata: name, version, category, sources を末尾に配置

**前提条件**: 読み物型スキルとして設計。hook/agent 連携の自動実行レイヤーなし。

## Gap Analysis

| # | パターン | 判定 | 実装度 | 差分 |
|---|---------|------|--------|------|
| 1 | Decision Table | Partial | 60% | 一部スキル(review, search-first)に存在するが体系的ではない |
| 2 | Anti-Patterns テーブル | Already | 100% | 全59スキルに配置済み。ただし箇条書きで ❌/✅ 対比表ではない |
| 3 | Mandatory Workflow | Already | 100% | Step/Phase 実装済み。完成度高い |
| 4 | Scope 明示（USE/NOT FOR） | Already | 85% | YAML description + Trigger に分散。統一 Scope セクション未設置 |
| 5 | マルチ言語コード例 | Gap | 10% | JS/TS のみ。複数言語での同一パターン提示ほぼなし |
| 6 | Metadata（version/sources） | Partial | 70% | name/pattern のみ。version, category, sources なし |

## Integration Decisions

全4項目を統合対象に選択:
1. [Partial] Decision Table 強化 — 判断が必要なスキルに Decision Table を追加
2. [Already→進化] Anti-Patterns を ❌/✅ 対比表に進化
3. [Gap] マルチ言語コード例 — 開発系スキルに複数言語例を追加
4. [Partial] Metadata 拡張 — version/category/sources フィールド追加

## Plan

`docs/plans/2026-03-23-minimax-skills-integration.md` に統合プランを記載。
