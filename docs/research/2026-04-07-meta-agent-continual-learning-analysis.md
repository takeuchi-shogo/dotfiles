---
source: https://github.com/canvas-org/meta-agent + "The Great Convergence" blog post
date: 2026-04-07
status: integrated
---

# meta-agent: Continual Learning for Agents + The Great Convergence

## Source Summary

### 記事1: meta-agent (Anthropic / canvas-org)

**主張**: プロダクションのトレースからハーネスを自動改善できる。LLM judge + proposer + holdout validation のループで、ラベルなしでも67%→87%の精度改善を実現。

**手法**:
- Read→Judge→Propose→Validate→Repeat のフィードバックループ
- LLM judge が個別トレースを自然言語批評付きでスコアリング（"agent refunded without checking cancellation policy"）
- 小さな labeled holdout セットで変更の accept/reject を自動判定
- ファイルシステムベースの永続記憶（prior candidates, traces, scores）
- 1回1変更の最小修正 + "smallest effective fix"
- 過学習防止: "State your change as a rule about agent behavior. If you can only justify it by pointing to specific traces, it's too narrow."
- ビジネスルールを skill に移動した変更が最大改善（→80%）

**根拠**:
- tau-bench v3 airline: holdout 67%→87%（judge-based）、67%→80%（labeled-search）
- Judge-based が labeled-search を上回った — 自然言語批評が binary supervision より豊かな最適化シグナルを提供
- 4-10 イテレーションで最良ハーネスに到達
- Haiku 4.5 + Opus 4.6 proposer 構成

**前提条件**: Claude Agent SDK、holdout セット必要、proposer prompt品質が成果に直結

### 記事2: The Great Convergence

**主張**: テック企業がハーネス+モデル+ツールの自己改善エージェントに収斂。勝者はモデルではなく observation→improvement ループが最短の者。

**手法**: 自律性スライダー、CLM (Continuously Learning Machine) パターン、ハーネス自己改善ループ

**根拠**: Cruise CLM（quarterly→weekly deploy）、Meta-Harness研究、AutoResearch

**前提条件**: エンタープライズ知識労働の自動化という文脈

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Per-trace LLM judge scoring | **Gap** | session-learner が learnings 抽出するが個別トレースへの自然言語批評なし |
| 2 | Holdout validation gate | **Gap** | skill-audit に A/B ベンチマークはあるが holdout 精度での自動 accept/reject なし |
| 3 | Anti-overfit prompt technique | **Gap** | improve-policy に類似ルールなし |
| 4 | Continuous automated loop | **Partial** | `--evolve` で反復可能だが手動起動必要。Judge→Validate フィードバック未自動化 |
| 5 | Proposer meta-loop | **N/A** | 過度な複雑性。AutoEvolve 成熟後に検討 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 |
|---|---|---|---|
| A1 | FS ベース永続記憶 (session-trace-store.py + runs/) | meta-agent も同アーキテクチャ | **強化不要** — Meta-Harness 論文から統合済み |
| A2 | Single-change 規律 (`--single-change` オプション) | "one targeted change at a time, smallest effective fix" がデフォルト | **強化可能** — デフォルト化の根拠が強化 |
| A3 | Skills as domain rule containers | ビジネスルール skill 化が最大改善 (→80%) | **強化可能** — skill 化優先ヒューリスティック追加 |
| A4 | Scaffolding > Model (CLAUDE.md) | Haiku 4.5 で 67→87% | **強化不要** — 定量根拠付き記載済み |
| A5 | Autonomy slider (`/autonomous`) | 競争軸は自律性スライダー | **強化不要** |
| A6 | Continuous learning (`/continuous-learning`) | CLM パターン、失敗トレース→ルール抽出 | **強化可能** — trace-based 自動ルール抽出パス未接続 |

## Integration Decisions

### 選択: 全件取り込み

**Gap/Partial:**
1. Per-trace LLM judge scoring → Wave 2 (概念ルール追加 + 将来実装)
2. Holdout validation gate → Wave 2 (概念ルール追加 + 将来実装)
3. Anti-overfit prompt technique → Wave 1 (improve-policy Rule 40)
4. Continuous automated loop → Wave 3 (将来実装)

**強化:**
1. Single-change デフォルト化 → Wave 1 (Rule 20 修正)
2. Skill 化優先ヒューリスティック → Wave 1 (improve-policy Rule 41)
3. CL → trace-based ルール抽出 → Wave 2 (continuous-learning SKILL.md 修正)

## Plan

### Wave 1: Proposer 指示強化（S規模 — 即実行）

| # | タスク | ファイル | 変更内容 |
|---|--------|---------|---------|
| T1 | Anti-overfit rule | `references/improve-policy.md` | Rule 40 追加: 「ルールとして述べよ」指示 |
| T2 | Single-change デフォルト化 | `references/improve-policy.md` | Rule 20 修正: デフォルト動作に変更 |
| T3 | Skill 化優先ヒューリスティック | `references/improve-policy.md` | Rule 41 追加: prompt修正 vs skill作成の判断基準 |

### Wave 2: Judge/Holdout 概念 + CL接続（S規模 — 同セッション）

| # | タスク | ファイル | 変更内容 |
|---|--------|---------|---------|
| T4 | Judge 概念ルール | `references/improve-policy.md` | Rule 42: per-trace critique の方向性を記載 |
| T5 | Holdout 概念ルール | `references/improve-policy.md` | Rule 43: holdout validation gate の方向性を記載 |
| T6 | CL→trace抽出パス | `skills/continuous-learning/SKILL.md` | 失敗トレース→行動ルール抽出セクション追加 |

### Wave 3: 自動ループ拡張（M規模 — 将来セッション）

| # | タスク | ファイル | 変更内容 |
|---|--------|---------|---------|
| T7 | Judge→Validate 自動ループ | `skills/improve/SKILL.md` | `--evolve` の Phase 拡張 |
