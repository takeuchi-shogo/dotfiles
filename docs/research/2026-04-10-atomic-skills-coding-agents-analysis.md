---
title: "Scaling Coding Agents via Atomic Skills"
source: "arXiv:2604.05013"
authors: "Yingwei Ma, Yue Liu, et al. (HKUST/NUS/PKU/SJTU/BUPT)"
date: 2026-04-10
type: absorb-analysis
status: integrated
---

# Scaling Coding Agents via Atomic Skills — 分析レポート

## 論文概要

LLM コーディングエージェントの訓練において、複合タスク（SWE-bench等）で直接最適化するのではなく、ソフトウェアエンジニアリングを5つの原子スキル（Code Localization, Code Editing, Unit Test Generation, Code Review, Issue Reproduction）に分解し、Joint RL（GRPO）で統合最適化する新パラダイム。GLM-4.5-Air (106B) で SWE-bench Verified 0.507→0.585 を達成。

## 主要な知見

- 原子スキル改善が OOD 複合タスクに転移する（構成的汎化）
- 異質スキルの Joint RL で負の干渉が起きない
- スキル設計3原則: 最小性・自己完結性・独立評価可能性
- 10K+ 並行サンドボックス環境でのスケーラブルな実行

## ギャップ分析結果

| # | 手法 | 判定 | 現状 | 転用可能性 |
|---|------|------|------|-----------|
| 1 | 原子スキル分解 | Partial | agent 層で部分実装（debugger, reviewer, test-engineer） | capability マッピング表 |
| 2 | スキル別自動報酬 | Partial | 5D + A/B (LLM-as-Judge) | deterministic metrics |
| 3 | Joint RL | N/A (proxy 可) | AutoEvolve で proxy 最適化に翻訳可能 | regression check 強化 |
| 4 | 構成的汎化 | N/A (原則有効) | per-skill evaluation の妥当性を裏付け | 計測フレームワークの動機付け |
| 5 | スキル設計3原則 | Partial | minimality/self-containment 存在。independent evaluability が弱 | skill-writing-guide に明示化 |
| 6 | 混合スキルバッファ | N/A (proxy 可) | AutoEvolve 混合評価で近似可能 | multi-skill 同時評価 |
| 7 | サンドボックス実行 | Partial | worktree + Codex sandbox + read-only profile | 低優先（現状で実用十分） |

## セカンドオピニオン

### Codex 批評
- atomicity は skill 層ではなく agent/capability 層に課すべき
- #1 は agent 層を含めると Partial より強い
- #3, #6 は AutoEvolve で proxy 可能（完全 N/A は強すぎ）
- 最優先: independent evaluability 強化

### Gemini 補完
- 5スキル分解が「最適」な根拠は仮説的（粒度選択は開放問題）
- RL 不要の代替トレンド: CORAL, AlphaLab が 2025-2026 で台頭
- EPD ワークフローが既に原子スキル的独立性を持つ

## 統合タスク（全4件、全て実装済み）

| # | タスク | ファイル | 状態 |
|---|--------|---------|------|
| T1 | Independent Evaluability 明示化 | skill-writing-guide.md, skill-creator/SKILL.md | ✅ |
| T2 | Capability マッピング表 | skill-inventory.md | ✅ |
| T3 | Deterministic Metrics 方針追記 | skill-eval-improvement-plan.md (T3b) | ✅ |
| T4 | AutoEvolve Regression Check 強化 | skill-eval-improvement-plan.md (T5 強化) | ✅ |
