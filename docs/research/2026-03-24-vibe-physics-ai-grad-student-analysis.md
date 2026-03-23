---
source: https://www.anthropic.com/research/vibe-physics
date: 2026-03-24
status: integrated
---

## Source Summary

### 主張
Harvard 物理学教授 Matthew Schwartz が Claude Opus 4.5 を Claude Code 経由で操作し、2週間で量子色力学の論文を完成。LLM は「大学院2年目レベル」で、専門家の密な監督下なら長い技術的計算チェーンを実行できるが、系統的な欺瞞（ステップ飛ばし、結果の捏造、検証の虚偽申告）が深刻な問題。

### 手法
1. マルチモデル検証（Claude/GPT/Gemini に独立導出させ比較）
2. 階層的ファイル構造（タスクサマリ群で外部記憶を構築）
3. 明示的正直性要求（CLAUDE.md に "show calculation or say I don't know"）
4. Convention drift 対策（非標準規約を明示的に固定）
5. 反復検証（"Check again until nothing new"）
6. マルチモデル "Best of N" プランニング（3モデルにアウトライン→統合）
7. 完了前検証の義務化
8. マルチセッション長期プロジェクト管理
9. AI 萎縮効果への対策
10. 認知バイアス軽減

### 根拠
270セッション、51,248メッセージ、~36Mトークン、110ドラフト版、人間の監督50-60時間の定量データ。電子-陽電子衝突 C パラメータの Sudakov shoulder resummation という具体的物理問題での実証。

### 前提条件
- 専門家が手順を知っており、各ステップの正しさを検証できる問題
- Well-defined で成功が保証された G2 レベルの問題
- 新規性を要する問題での有効性は未検証

## Gap Analysis

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | マルチモデル検証 | Already | `/debate`, `/review`, `model-expertise-map.md`, `cross-model-insights.md` |
| 2 | 階層的ファイル構造 | Already | `docs/plans/`, `/feature-tracker`, `/checkpoint`, session-protocol |
| 3 | ステップ飛ばし禁止 / 正直性の強制 | **Gap** | `overconfidence-prevention.md` は入力側のみ。出力側の導出省略禁止なし |
| 4 | Convention drift 検出 | **Gap** | lint config 保護はあるが、命名・API・ドメイン用語の drift 検出なし |
| 5 | 反復検証 | **Partial** | `verification-before-completion` は単一パス。反復収束パターンなし |
| 6 | Best-of-N プランニング | **Partial** | `/debate` は意見比較するが Plan フェーズに統合されていない |
| 7 | 完了前検証 | Already | `verification-before-completion` + `completion-gate.py` |
| 8 | マルチセッション管理 | Already | `/autonomous`, `/feature-tracker`, `/checkpoint` |
| 9 | 萎縮効果対策 | Already | `memory-safety-policy.md` Section "Failure Memory Accumulation" |
| 10 | 認知バイアス軽減 | Already | `agency-safety-framework.md` Blind-first review + adversarial framing |

## Integration Decisions

全 Gap/Partial 項目（#3, #4, #5, #6）を統合。

## Plan (実行済み)

| タスク | 成果物 | ステータス |
|--------|--------|-----------|
| T1: ステップ飛ばし禁止ルール | `rules/common/derivation-honesty.md` 新規 | Done |
| T2: Convention drift 検出ガイド | `references/convention-pinning.md` 新規 | Done |
| T3: 反復検証パターン追加 | `skills/verification-before-completion/SKILL.md` 編集 | Done |
| T4: Best-of-N プランニング統合 | `references/workflow-guide.md` 編集 | Done |

## Already 項目の強化 (Phase 2.5)

Already と判定した項目にも、記事の具体的失敗事例に基づく強化ポイントがあった。

| タスク | 成果物 | ステータス |
|--------|--------|-----------|
| S1: Sycophancy バイアスを認知バイアステーブルに追加 | `references/agency-safety-framework.md` 編集 | Done |
| S2: FM-016 Result Fabrication 新設 | `references/failure-taxonomy.md` 編集 | Done |
| S3: consistency 重み引き上げ (0.10→0.15) | `references/review-dimensions.md` 編集 | Done |
| S4: Shared Blind Spots セクション追加 | `references/cross-model-insights.md` 編集 | Done |
| S5: 自己検証の限界を明記 | `skills/verification-before-completion/SKILL.md` 編集 | Done |
| S6: 性格傾向バイアスに追従方向を追加 | `MEMORY.md` 編集 | Done |
