---
source: https://hermes-agent.nousresearch.com/docs/guides/tips/
date: 2026-03-23
status: integrated
---

## Source Summary

Hermes Agent (Nous Research) の公式 Tips & Best Practices。39件のTipsを8カテゴリ（Getting Results, CLI, Context Files, Memory/Skills, Performance, Messaging, Security）に分類。

**主張**: エージェントの効率はプロンプトの具体性、コンテキストファイルの最適化、メモリとスキルの適切な分離で決まる。

**手法**:
- Context File の階層的配置（root = 全体、subdirectory = チーム固有）
- Memory = "what"（事実）、Skill = "how"（手順）の明確な境界
- Prompt Cache の安定性維持（system prompt を変更しない）
- Memory Snapshot の制約認識（セッション中の変更は即反映されない）
- スキル化の定量基準（5+ステップ × 再発タスク）

**根拠**: Hermes Agent の運用経験に基づく実践的知見。定量的なベンチマークは未提示。

**前提条件**: LLM ベースのエージェントシステム全般に適用可能。一部は Hermes Agent 固有（Telegram/Discord 連携、SOUL.md 等）。

## Gap Analysis

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | Be Specific / Provide Context | Already | CLAUDE.md core principles |
| 2 | Context File Size Optimization | Already | compact-instructions.md + IFScale |
| 3 | Hierarchical Context Discovery | Already | Progressive Disclosure 設計 |
| 4 | Memory vs Skills 境界 | Partial | skill-writing-principles.md に手順側のみ。memory 側に対称ルールなし |
| 5 | Prompt Cache 安定性 | Gap | 未文書化 |
| 6 | Memory Snapshot 制限 | Gap | 未文書化 |
| 7 | スキル作成の定量基準 | Partial | 定性ガイドのみ。定量閾値なし |

## Integration Decisions

全4件を取り込み:

1. **Memory vs Skills 境界** → `memory-safety-policy.md` に「Memory = what, Skill = how」原則を追記
2. **Prompt Cache 安定性** → `compact-instructions.md` にキャッシュ破壊リスクの注意書きを追加
3. **Memory Snapshot 制限** → `workflow-guide.md` のメモリ記録ルールに Snapshot 制限を追記
4. **スキル作成の定量基準** → `skill-writing-principles.md` に「5+ステップ × 2回以上」閾値を追加

## Changes Made

| ファイル | 変更内容 |
|---------|---------|
| `references/memory-safety-policy.md` | 4分類の判断基準の後に Memory/Skill 境界原則を追加 |
| `references/compact-instructions.md` | 冒頭に Prompt Cache 安定性セクションを追加 |
| `references/workflow-guide.md` | メモリ記録ルールに Snapshot 制限の bullet を追加 |
| `skills/skill-creator/references/skill-writing-principles.md` | 原則 3.5 としてスキル化閾値を追加 |
