---
source: https://arxiv.org/pdf/2603.03329
date: 2026-03-31
status: integrated
---

# AutoHarness: improving LLM agents by automatically synthesizing a code harness

**著者**: Xinghua Lou, Miguel Lázaro-Gredilla, Antoine Dedieu, Carter Wendelken, Wolfgang Lehrach, Kevin P. Murphy (Google DeepMind)

## Source Summary

### 主張

LLM エージェントの失敗は「知識の欠如」ではなく「実行の不正確さ」に起因する。Kaggle GameArena チェス大会で Gemini-2.5-Flash の敗北の 78% が違法手。LLM 自身にコードハーネスを書かせ、環境フィードバックで反復改善すれば、小モデル+ハーネスが大モデル単体を上回る。

### 手法

1. **Harness-as-Action-Filter**: `propose_action()` で手を生成 → `is_legal_action()` で検証 → 違法なら再生成（rejection sampling）
2. **Harness-as-Policy**: コードが直接次の手を出力。推論時 LLM 呼び出し不要
3. **Thompson sampling 木探索**: コード候補を木構造で管理。各ノードのヒューリスティック値=合法手成功率。探索と搾取のバランス
4. **Critic-Refiner ループ**: 10 並列環境で Rollout → 最大 5 件のエラーを Critic が集約 → Refiner (LLM) がコード改善
5. **コードへの知識蒸留**: LLM の戦略的知識を Python コードに蒸留

### 根拠（定量結果）

- 145 TextArena ゲームで **合法手率 100%** 達成（平均 14.5 反復で収束）
- 2P ゲーム: **Gemini-2.5-Flash+Harness** vs Gemini-2.5-Pro → **9/16 勝**（勝率 56.3%）
- 1P ゲーム: Flash+Harness 平均報酬 **0.745** > Gemini-2.5-Pro **0.707**
- Harness-as-Policy: 平均報酬 **0.870** > GPT-5.2-High **0.844**、推論コスト **≈ $0**（GPT-5.2 は ~$640）

### 前提条件

- 「合法/違法」が明確に判定可能なドメイン（ゲーム環境）
- 環境からのフィードバック（エラーメッセージ、合法性判定）が得られること
- 訓練に Gemini-2.5-Flash を使用（比較的安価な LLM で十分）

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Action Filter パターン | Partial | hook で出力検証（golden-check, completion-gate）はあるが rejection sampling ループとして体系化されていない |
| 2 | Thompson sampling 木探索 | Gap | 未実装。コード改善は線形的で複数候補の並列管理なし |
| 3 | Code as Policy（蒸留） | Gap | hook/script は人間が書いたもので LLM 自動生成ではない |
| 4 | Critic-Refiner 分離 | Partial | session-learner + findings-to-autoevolve が類似するが明示的 2 段階パイプラインではない |
| 5 | Scaffolding > Model | Already (強化可能) | CLAUDE.md に原則として明記済み。Harness-as-Policy (0.870) > GPT-5.2-High (0.844) の定量根拠を追記可能 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|-------------|-------------|--------|
| 5 | CLAUDE.md「Scaffolding > Model」 | Flash+Harness(0.870) > GPT-5.2-High(0.844)。コスト $0 vs $640 | 原則に定量根拠を 1 行追記 |

## Integration Decisions

全 5 項目を統合:

- T1: 本レポート（本ファイル）
- T2: `references/autoharness-patterns.md` に 3 パターン整理
- T3: CLAUDE.md「Scaffolding > Model」に定量根拠追記
- T4: `references/improve-policy.md` に Critic-Refiner 分離パターン追記
- T5: MEMORY.md にポインタ追記
