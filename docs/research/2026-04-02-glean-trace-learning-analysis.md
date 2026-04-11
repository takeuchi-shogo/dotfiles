---
source: "Glean - Trace Learning for Self-Improving Agents (blog post, 2026)"
date: 2026-04-02
status: analyzed
---

## Source Summary

### 主張
エージェントは実行トレースから学習し、タスクごとに白紙状態から始めるのではなく環境固有の専門知識を蓄積すべき。Glean はオフライン学習（teacher-student 比較）+ オンライン適用（メモリ検索・適用）の2段階で実現。

### 手法
1. **Teacher-Student 比較**: 高推論予算 teacher + 制約付き複数 student トレース比較でベスト戦略抽出
2. **Multi-trace 合意検証**: 複数トレースから事実主張を抽出・合意チェック。不一致解消不能時は学習しない
3. **ワークフローレベルのツール戦略**: 個別ツール呼び出しではなくツール間の組み合わせパターンを学習
4. **Deployment/User 2層メモリ**: 共有ワークフロー戦略 vs 個人プリファレンスを分離
5. **Shadow path 実行**: 本番データに触れず write 操作をリプレイして学習（→ N/A: 個人環境向け）
6. **意図的に狭いツール戦略**: "この状況ではこの戦略を優先" の粒度
7. **成功+失敗の対比学習**: ReasoningBank 式。成功パスと失敗パスの分岐点分析

### 根拠
- Dynamic Cheatsheet, ACE (Agentic Context Engineering), ReasoningBank の先行研究
- Glean 企業デプロイメントでの実績
- user-level メモリ追加で significant performance impact

### 前提条件
- 大量タスク実行トレース蓄積
- 繰り返しタスクパターン
- 複数モデル/予算での実行環境

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Teacher-Student 比較 | Partial | Codex Gate が teacher 的レビューを実行するが、複数予算/制約での student トレース比較は未実装 |
| 2 | Multi-trace 合意検証 | Gap | `session-trace-store.py` は raw トレース保存、`trace_sampler.py` はサンプリングするが、合意チェックなし |
| 3 | ワークフローレベルツール戦略自動抽出 | Partial | `/analyze-tacit-knowledge` がパターン抽出するが、ツール組み合わせパターンの自動抽出は未実装 |
| 5 | Shadow path 実行 | N/A | 企業マルチテナント向け。個人 dotfiles セットアップでは不要 |
| 7 | 成功+失敗の対比学習 | Partial | `edit-failure-tracker.py` + `lessons-learned` が失敗を記録するが、成功/失敗の明示的対比分析なし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す改善点 | 強化案 |
|---|-------------|-----------------|--------|
| 4 | 3スコープメモリ (user/project/local) | deployment レベルはツール名・シーケンスのみ保存し PII 除外 | `session-trace-store.py` で tool_strategy と context を分離保存 |
| 6 | improve-policy + error-fix-guides + tacit-knowledge | "この状況ではこの戦略を優先" の粒度で意図的に狭く蓄積 | `references/situation-strategy-map.md` として状況→戦略マップを新設 |

## Integration Decisions

全項目取り込み（#5 Shadow path を除く6項目）。

## Plan

→ `docs/plans/2026-04-02-trace-learning-integration.md` 参照
