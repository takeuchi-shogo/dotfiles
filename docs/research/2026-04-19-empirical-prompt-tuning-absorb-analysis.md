---
source: "https://github.com/mizchi/chezmoi-dotfiles/blob/main/dot_claude/skills/empirical-prompt-tuning/SKILL.md"
date: 2026-04-19
status: integrated
author: mizchi
---

## Source Summary

**主張**: プロンプト品質はサードパーティ評価でしか分からない。バイアスを排した新規サブエージェントによる反復評価で著者には見えない構造的欠陥が顕在化する。

**手法**:
- Baseline Preparation: 2-3 シナリオ (中央値+エッジ) + 3-7 要件チェックリスト ([critical] タグ)
- Unbiased Execution: 新規サブエージェント派遣で確認バイアス排除
- Dual-Axis Evaluation: 定性 (曖昧さ・再試行) + 定量 (tool_uses, 実行時間, 成否)
- Minimal Differential Patching: 1 反復 1 テーマ修正、要件チェックリストにリンク
- Convergence Testing: 2 連続で新規曖昧さゼロ・改善≤3%・メトリクス±10-15% 安定 + 保留シナリオ検証

**根拠**: 著者自身のプロンプト改善ループ実践から導出。Dual-Axis (定性+定量) の組み合わせにより構造的欠陥の顕在化を確認。

**前提条件**: タスクツール/サブエージェント派遣可能な環境。反復コストを正当化する重要度のプロンプト。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Baseline Preparation: シナリオ+[critical]チェックリスト | Already | spec template + acceptance_criteria + [CRITICAL] tag が存在するが scenarios 構造化が未対応 |
| 2 | Unbiased Execution: 新規サブエージェントで確認バイアス排除 | Already | codex-reviewer blind-first + compare.sh + adversarial-gate が存在するが memory 由来バイアスが残存 |
| 3a | tool_uses + Precision of Tool Use を eval primary 指標化 | Partial | session-trace-store.py が tool_count 記録済み・aggregate.py 未接続 |
| 3b | 定性シグナル記録: 曖昧さ・再試行・失敗理由 | Gap | qualitative_signals.jsonl 等の記録基盤なし |
| 4 | Minimal Differential Patching: 1反復1テーマ + back-link | Already | Rule 20 単一変更規律 + 仮説事前明記で本質カバー (back-link は nice-to-have) |
| 5 | Convergence Testing: holdout 検証 + evaluator drift 対策 | Partial | 既存は adoption_rate≤0.30 + 2連続フロンティア不変のみ。holdout と drift 対策が未整備 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | spec template + acceptance_criteria + [CRITICAL] tag | 「2-3 シナリオ（中央値+エッジ）」構造化が template 未対応 | scenarios: median/edge_cases + holdout_scenarios セクション追加 | 強化可能 |
| S2 | codex-reviewer blind-first + compare.sh + adversarial-gate | 新規 session_id だけでは memory 由来バイアス残存。Self-preference Bias (同モデルファミリー evaluator は甘くなる) | 異モデル必須・local memory disable 契約明記 | 強化可能 |
| S3 | Rule 20 単一変更規律 + 仮説事前明記 | back-link なし | nice-to-have に止まる | 強化不要 |

## Phase 2.5 批評統合 (Codex + Gemini)

### Codex (codex-rescue) の指摘
- Convergence (手法5) を Already → Partial に格下げ
- Dual-Axis の定性軸が薄い（手法 3b として独立計上）
- 手法4 は Rule 20 で本質カバー、棄却推奨
- blind の前提誤り: session_id 切替だけでは不十分
- 最優先: 3a の tool_count 集計接続

### Gemini (Google Search grounding) の周辺知識
- Self-preference Bias: 同モデルファミリー evaluator は甘くなる (Anthropic Agent Evals 公式手法と整合)
- Reward Hacking 警告: tool_use_count 単独は危険、Precision of Tool Use 併用必須 (arXiv:2403.03023)
- Holdout Contamination: 評価ケースが最適化ループに混入し overfitting (arXiv:2211.01910)
- Evaluator Drift: 評価用 LLM のバージョンアップで基準変動
- 代替手法: DSPy (https://github.com/stanfordnlp/dspy) / TextGrad (arXiv:2406.11671) / Inspect-AI (https://uk-aisi.github.io/inspect/) — 自動化路線、評価関数設計コスト高

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 3a | tool_uses + Precision of Tool Use を eval primary 指標化 | 採用 (T1, P1) | session-trace-store.py が tool_count 記録済みで接続コスト低・Reward Hacking 対策も兼ねる |
| 3b | 定性シグナル記録: 曖昧さ・再試行・失敗理由 | 採用 (T1, P1) | qualitative_signals.jsonl 基盤が完全欠如、convergence 判定の前提 |
| 5 | Convergence holdout + evaluator drift 対策 | 採用 (T2, P2) | T1 完了後に接続可能。arXiv:2211.01910 の Holdout Contamination リスクが実証的 |
| 4 | Minimal Differential Patching back-link | スキップ | Codex 評: Rule 20 で本質カバー、nice-to-have に過ぎない |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | spec template に scenarios 構造化 (median/edge_cases) | 採用 (T3, P2) | T2 の holdout_scenarios と template ファイルが重なるため統合可能 |
| S2 | blind 評価の memory 分離 + 異モデル契約 | 採用 (T4, P3) | Self-preference Bias は Gemini が実証的文献で補強、独立して実施可能 |
| S3 | back-link 追加 | スキップ | nice-to-have、Rule 20 で十分 |

## Plan

### Task 1: tool_uses + qualitative_signals 接続 (P1, 規模 M)
- **Files**:
  - `.config/claude/skills/skill-creator/scripts/aggregate.py` — tool_count + Precision of Tool Use を primary 指標化
  - `.config/claude/skills/improve/SKILL.md` — Convergence Check に tool_uses 安定性 (±10-15%) 追加
  - `.config/claude/skills/improve/instructions/evolve-mode.md` — eval 出力に tool_uses + qualitative_signals 含める指示
  - `.config/claude/skills/skill-creator/instructions/testing-evaluation.md` — qualitative_signals.jsonl 記録規約
  - `.config/claude/references/qualitative-signals-spec.md` (新規) — 「曖昧さ・再試行・失敗理由」スキーマ定義
- **Changes**: aggregate.py に tool_count 集計接続、qualitative_signals.jsonl スキーマ策定・記録フロー整備
- **Size**: M
- **依存**: なし（最優先）

### Task 2: Convergence holdout + evaluator drift 対策 (P2, 規模 M)
- **Files**:
  - `.config/claude/skills/improve/SKILL.md` — `--validate-holdout` フェーズ追加
  - `.config/claude/scripts/runtime/learner/` 配下の improve-history schema — `evaluator_model_version` フィールド追加（該当ファイル特定要）
  - `.config/claude/references/improve-policy.md` — Rule 24/25 として「holdout 検証」「evaluator drift 検出」追加
- **Changes**: holdout_scenarios を spec から分離保持、evaluator_model_version 記録でドリフト検出
- **Size**: M
- **依存**: T1 完了後 (qualitative_signals が convergence 判定の前提)

### Task 3: spec template に scenarios 構造化 (P2 強化, 規模 S)
- **Files**:
  - `.config/claude/skills/spec/templates/prompt-as-prd-template.md` — scenarios: median/edge_cases + holdout_scenarios セクション
  - `.config/claude/scripts/policy/spec-quality-check.py` — scenarios.median 必須チェック追加
- **Changes**: T2 と template ファイルが重なるので統合実施
- **Size**: S
- **依存**: T2 と統合可能

### Task 4: blind 評価の memory 分離 + 異モデル契約 (P3 強化, 規模 S)
- **Files**:
  - `.config/claude/skills/improve/instructions/phase4-adversarial-gate.md` — 「異モデル必須・local memory disable」契約明記
  - `.config/claude/agents/codex-reviewer.md` — Self-preference Bias 警告追記
- **Changes**: session_id 切替だけでは不十分という前提を明文化、異モデル評価を必須化
- **Size**: S
- **依存**: 独立

## リスクと対策

| リスク | 出典 | 対策 |
|------|------|------|
| Self-preference Bias | Gemini / Anthropic Agent Evals | T4 で異モデル必須化 |
| Reward Hacking (tool_uses 単独最適化) | Gemini, arXiv:2403.03023 | T1 で Precision of Tool Use 併用 |
| Holdout Contamination | Gemini, arXiv:2211.01910 | T2 で holdout_scenarios を spec から分離保持 |
| Evaluator Drift | Gemini | T2 で evaluator_model_version 記録 |
| 共有 memory バイアス | Codex | T4 で local memory disable 契約 |

## Chaining 提案

- 全体規模: 約 10-12 ファイル → M-L 規模 → `docs/plans/` に昇格 + 新セッションで `/rpi` 推奨
- L 規模に膨らむなら `/epd` で Spec フェーズから
- 実装: `/rpi docs/research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md`
