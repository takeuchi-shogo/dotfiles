---
source: https://arxiv.org/abs/2602.11988
date: 2026-03-18
status: integrated
---

## Source Summary

**Title**: Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?
**Authors**: Thibaud Gloaguen, Niels Mündler, Mark Müller, Veselin Raychev, Martin Vechev (ETH Zurich / LogicStar.ai)
**Date**: 2026-02-13

### 主張

AGENTS.md / CLAUDE.md などのコンテキストファイルが coding agent の性能に与える影響を初めて大規模に実証評価。LLM 生成ファイルは性能を下げ、人間記述ファイルは微増にとどまる。

### 手法

- **AGENTBENCH**: 12リポジトリ・138インスタンスの新ベンチマーク（開発者記述コンテキストファイル付き）
- **SWE-BENCH LITE**: 300タスク（None / LLM生成 / 開発者記述の3条件比較）
- 4エージェント: Claude Code (Sonnet-4.5), Codex (GPT-5.2, GPT-5.1 Mini), Qwen Code (Qwen3-30B)

### 核心的な発見

1. **LLM生成コンテキストファイルは性能低下**: 平均 -0.5%〜-2%、コスト +20〜23%
2. **開発者記述ファイルは微増**: 平均 +4%（AGENTBENCH）、コスト +19%
3. **指示は従われる**: uv 言及時 1.6回/instance 使用、未言及時 0.01回
4. **コードベース概要は無効**: 関連ファイルへの到達ステップ数に有意差なし
5. **既存ドキュメントと冗長**: docs 削除時、LLM生成が開発者記述を +2.7% 上回る
6. **推論トークン増加**: コンテキストファイルで reasoning tokens +10〜22%
7. **強いモデルでも良いファイルは生成できない**: GPT-5.2 生成 vs エージェント自身で一貫した差なし

### 根拠

- 4エージェント × 3条件 × 2ベンチマーク = 24設定の網羅的評価
- エージェントトレース分析（ツール使用頻度、推論トークン数）
- 既存ドキュメント削除時の ablation study

### 前提条件

- Python リポジトリのみ（ニッチ言語では結果が異なる可能性）
- SWE-bench 形式のバグ修正・機能追加タスク

## Gap Analysis

| 手法 | 判定 | 当セットアップの状況 |
|------|------|---------------------|
| コードベース概要を含めない | Already | CLAUDE.md にファイルツリーなし |
| 指示は従われる | Already | actionable な指示で構成 |
| 既存ドキュメントと重複しない | Already | Documentation=Infrastructure 原則 |
| Progressive Disclosure | Already | 3層構造で常時ロード最小化 |
| LLM生成ファイルへの警戒 | Partial→Integrated | /init-project に guardrail 追加 |
| 指示数の最小化 | Gap→Integrated | harness_guarantees 圧縮 (8→4項目) |
| MEMORY.md 肥大化対策 | Gap→Integrated | 210→~150行に圧縮 |
| 指示コスト意識 | Gap→Integrated | feedback_instruction_cost.md 追加 |

## Integration Decisions

全4項目を統合:

1. **harness_guarantees 圧縮**: hook メカニズム詳細（PostToolUse/Stop/SessionStart）を削除、1行に統合。禁止事項と行動期待のみ残す
2. **MEMORY.md 圧縮**: 詳細セクション（ハーネスエンジニアリング25行、AutoEvolve13行等）をトピックファイルに退避
3. **init-project guardrail**: Anti-Patterns に「概要禁止」「最小指示原則」追加、Phase 3 に最小性チェック追加
4. **指示コスト feedback memory**: 追加時のコスト意識を定着させる

## Plan

### Task 1: CLAUDE.md harness_guarantees 圧縮 (S)
- `<harness_guarantees>` を 8項目 → 4項目に圧縮
- PostToolUse/Stop/SessionStart の個別説明を 1行に統合
- permissions ポリシー行を削除（settings.json で管理）

### Task 2: MEMORY.md 圧縮 (M)
- ハーネスエンジニアリング: 25行 → 3行 + `harness_engineering_details.md`
- AutoEvolve: 13行 → 3行 + `autoevolve_details.md`
- Progressive Disclosure, マルチモデル連携, EPD, Background Agents: インライン圧縮
- 目標: 210行 → 150行以下

### Task 3: /init-project guardrail (S)
- Anti-Patterns に 2項目追加
- Phase 3 Verify に最小性チェック追加

### Task 4: feedback memory (S)
- `feedback_instruction_cost.md` 作成
