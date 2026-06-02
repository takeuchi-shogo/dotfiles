---
title: "Microsoft SkillOpt: 自己進化スキル (text-space optimizer) absorb 分析"
date: 2026-06-02
source:
  title: "I want to create self-evolving agent skills (SkillOpt の解説記事)"
  author: unknown (blog)
  type: blog
  url_paper: "https://arxiv.org/pdf/2605.23904"
  url_repo: "https://github.com/microsoft/SkillOpt"
  fetched: pasted-text
family: skill-prompt-empirical-optimization
status: planned
adopted: 4
rejected: 0
validation_only: 2
related:
  - docs/research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md
  - docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md
---

## Source Summary

**主張**: SkillOpt (Microsoft Research, 2026-05, arXiv:2605.23904) は「スキル = エージェントに渡す自然言語の指示文」を、重みではなく **テキストそのものを訓練対象**として最適化する text-space optimizer。frozen model の前段に置く永続スキル文書を、正解キー付き例題で実証的に改善する。

**手法** (4つのコア部品 + 前提):
- **frozen target model**: 現スキルでタスク実行（モデルは固定）
- **optimizer model**: 成功/失敗の minibatch を読み、構造化編集 (add/delete/replace) を提案。訓練時のみ使用しデプロイには同梱しない
- **bounded edit budget ("textual learning rate")**: 1ステップ最大 Lt 編集 (default 4 → 2 decay)。unbounded rewrite が効いていたルールを消すのを防ぐ
- **validation gate**: held-out で **厳密にスコア向上 (tie は reject)** した編集だけ採用。最も load-bearing な部品で、answer key の正直さに全面依存
- **rejected-edit buffer**: 落ちた編集のスコア低下を記録 → optimizer が再提案しない (削除すると結果が測定可能に悪化)
- **slow / meta update**: epoch 末に「恒常的に効いている」note を fast edit が上書きできない保護領域へ書き込む (momentum)
- **成果物**: 小さな `best_skill.md` (380-2,000 tokens, 1-4 accepted edits)。監査可能

**根拠**: 6 ベンチマーク × 7 モデル × 3 harness の 52/52 セルで best/tied-best。GPT-5.5 direct chat で 6 bench 平均 58.8 → 82.3 (+23.5)。最大の伸びは**手続き的タスク** (tool use / output format の規律) に集中。transfer も実証 (harness 間 +59.7)。

**前提条件**: **「正解キーで照合できるタスク」専用** (extraction / classification / structured generation / QA with reference / runnable code)。`"correct" が存在しない判断タスクには「間違ったツール」と記事が明言。コストは一時的だが膨大 (0.6M-46M tokens / test 1pt gain)。

## Phase 2.5 検証 (Codex + Gemini 並列批評)

- **Gemini grounding**: SkillOpt は実在 (MS Research 2026-05)。**OPRO 系譜**。DSPy (few-shot 選定) / TextGrad (逐次勾配) と異なり、textual learning rate で catastrophic forgetting を防ぎ、rejected-edit buffer で momentum を持つのが独自点。既知制約: ground-truth 依存・eval overfitting・推論コスト膨大。個人 harness では**フルループは過重、特定の繰り返し失敗スキルに絞る部分最適化が最効率**。
- **Codex (gpt-5.5, xhigh)**: 判定の方向性は正しいが `Already` が 2 点甘い。**(a) bounded edit budget は Already → Partial** (Rule 20/28 は規律であって structured patch budget ではない: improve-policy.md:279)。**(b) Gap #6 は "answer-key discriminator" より "optimizer eligibility classifier" と呼ぶべき** (Knowledge Pyramid Tier2 は知見昇格条件であって最適化対象の入口分類ではない: knowledge-pyramid.md:19)。LLM-as-judge 反論は「判断タスクに適用可」ではなく「judge の代理目的を最適化可」にすぎず、frozen judge / human anchor / TPR-TNR / drift 検出が無いと Goodhart 化。**/improve は復活させず新しい小型 lane を作れ** (improve-policy.md は deprecated)。

## Gap Analysis (Pass 1 + Pass 2.5 修正済み)

| # | SkillOpt 手法 | 判定 | 詳細 |
|---|---|---|---|
| 1 | bounded edit budget (textual learning rate) | **Partial** (Codex で Already から降格) | Rule 20 (単一変更) + Rule 28 (epsilon stepwise clipping 0.2→0.15→0.1) は規律。structured patch (add/delete/replace) + step snapshot 管理ではない |
| 2 | rejected-edit buffer | **Partial** | rejected-patterns.jsonl + Rule 14 + edit-failure-tracker.py 存在。category field drift でデータフロー停止中 |
| 3 | held-out validation gate (strict, tie reject) | **Partial (核心)** | split_holdout.py は層化分割器のみ (split_holdout.py:43)。Rule 47 (improve-policy.md:307) 設計済も「wiring 次サイクル予定」のまま未配線。/improve は A/B delta±2pp 自動 merge で 2026-05-03 retire (false-positive 多発) |
| 4 | slow / meta update (momentum, 保護領域) | **Partial** | Rule 30-31 + playbook 設計のみ。/improve retire 中で運用実績なし |
| 5 | optimizer model による構造化編集提案 | **Partial** | autoevolve-core / meta-analyzer 存在も unwired |
| 6 | objectively-checkable 前提の入口分類 | **Gap** → **optimizer eligibility classifier** | 改善対象スキルが客観照合可能か事前判別する分類器が無い。これが /improve false-positive 死の根因 |
| 7 | eval_only.py で no-skill baseline と比較 | **Already** | skill-audit が baseline + with-skill A/B 実施済 |
| 8 | best_skill.md の token compactness / auditability | **Already** | brevity research + skill-writing 原則で担保 (ただし dotfiles は成果物が skill群/policy/memory に散逸: SkillOpt の1ファイル固定思想とは逆) |
| 9 | 訓練コスト (0.6M-46M tokens/pt) | **N/A** (cheap-first 思想のみ転用) | 単一ユーザー harness にフル run は過重 |
| 10 | portability / transfer (model/harness 間) | **N/A** | 単一ユーザー・単一モデル運用に該当薄い |

## Integration Decisions (4件採用 / Codex 推奨2件を superset)

ユーザーは Triage で全4件を選択。Codex 最小推奨 (#1 #2) に #3 (rejected-buffer) と Validation-only を追加。

| # | 項目 | 規模 | 依存 |
|---|------|------|------|
| #1 | Optimizer Eligibility Classifier (objective lane vs judgement lane の入口分類を codify) | S | なし (他タスクの前提) |
| #2 | Objective-lane held-out strict accept gate (candidate edit→train eval→holdout strict accept(tie reject) の小型 script + playbook、split_holdout.py 再利用) | M | #1 |
| #3 | rejected-edit buffer の per-lane idempotent 再配線 | S〜M | #1 + category drift 修復 (learned-promotion-loop) |
| VO | Validation-only follow-up (下記) | — | — |

**Block (Codex と一致、採用しない)**: 旧 /improve の全面復活、判断系 skill (absorb/review/think) の自動 SkillOpt 化。

## 診断: ユーザーの「evolving 実感ない」の根因

> SkillOpt の概念はほぼ全て dotfiles に**設計済み**。欠けているのは概念ではなく **(a) 配線** と **(b) どのスキルを自動最適化してよいかの入口判別**。

2つの構造的理由:
1. **対象ミスマッチ**: dotfiles のスキル大半 (absorb/review/think/各 recipe) は**判断タスク**で、SkillOpt が "間違ったツール" と明言するケース。客観正解キーが無いものを自動最適化して false-positive を量産した = /improve が 2026-05-03 に retire した理由そのもの。
2. **設計済み・未配線**: held-out gate (Rule 47)、rejected buffer、momentum (Rule 30-31) はほぼ全部設計があるのに patterns.jsonl の category drift と /improve retire で動いていない。

→ 進む道は **「objective-checkable lane を明示し、そこにだけ SkillOpt 的な strict gate を小さく配線する」**。判断系は human-in-loop (現行 /promote-learnings) のまま据え置く。

## Validation-only Follow-up (採用件数に数えない / 実ファイルで裏取り済み)

| 対象 | drift 内容 | 訂正方針 |
|---|---|---|
| `docs/research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md` | frontmatter `status: integrated` だが、T1/T2/T4 は全て `.config/claude/skills/improve/` を実装ターゲットにしていた。/improve は本レポート作成 (04-19) 後の **2026-05-03 に retire** → タスク孤児化。`qualitative_signals.jsonl` (T1 成果物「採用」) は**未作成** (scripts/eval/ に存在せず確認済)。T3 (spec template の scenarios) のみ実施済 | frontmatter を `partially-superseded` に更新し、「T1/T2/T4 は /improve retire により孤児化、本 SkillOpt absorb の objective-lane gate へ統合し直す」と追記 |
| `references/improve-policy.md` Rule 47 | SkillOpt により holdout gate 設計の妥当性が**学術的に裏付けられた** (OPRO 系の strict held-out validation)。ただし wiring は未実装のまま | Rule 47 に「SkillOpt (arXiv:2605.23904) が strict-improve + tie-reject を実証」と外部裏付けを注記。配線先は deprecated な /improve ではなく新 objective-lane gate (#2) |

## Plan (詳細は docs/plans/active/2026-06-02-skillopt-objective-lane-optimization-plan.md)

L 規模 (新 reference + 新 script + playbook + 既存3ファイル編集 + drift 訂正)。新セッションで `/rpi` 推奨。

### Task #1: Optimizer Eligibility Classifier (S)
- **Files**: `references/optimizer-eligibility.md` (新規) + `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md` / `references/knowledge-pyramid.md` からポインタ
- **Changes**: スキル/artifact を `objective-checkable lane` (正解キーで照合可 = routing / extraction / code-review finding 分類 / validator 選択) と `judgement lane` (人間嗜好・文脈適合 = absorb/review/think) に二分する判定基準を codify。前者のみ #2 の strict gate 対象。

### Task #2: Objective-lane held-out strict accept gate (M)
- **Files**: `.config/claude/scripts/eval/holdout_accept_gate.py` (新規) + `docs/playbooks/` に運用 playbook
- **Changes**: `candidate edit → train(search)セットで eval → holdout で strict accept (tie reject)` の小型 pure-logic script。split_holdout.py の train/holdout 出力を入力に取る。**/improve には依存しない**。Rule 47 の「strictly-improves / tie reject」を明記。
- **依存**: #1 (eligibility lane 定義)

### Task #3: rejected-edit buffer の per-lane 再配線 (S〜M)
- **Files**: `references/improve-policy.md` Rule 14 周辺 (deprecated だが概念保持) + objective-lane gate プロンプト
- **Changes**: objective lane ごとに直近 rejected edits を idempotent 記録し gate 提案に再注入。category drift 修復が前提 (learned-promotion-loop と連動)。
- **依存**: #1 + category drift 修復

### Task VO: Validation-only 訂正 (S)
- **Files**: 上記 Validation-only テーブルの2ファイル frontmatter / 注記更新
