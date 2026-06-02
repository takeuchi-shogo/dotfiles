---
title: コードレビュー6段階と AI/人間の境界 absorb 分析
date: 2026-06-02
source: https://zenn.dev/kenimo49/articles/code-review-6-stages-ai-human-boundary
author: kenimo49 (Zenn)
family: code-review-best-practices
status: adopted (2件採用, S規模実装済)
adopted: 2
---

## Source Summary

**主張**: コードレビューを Format/Lint/Style/Logic/Design/Architecture の6段階に分け、各段階で AI 比率を 100%→0% へ段階的に下げる「AI/人間の境界モデル」。「正解が一意か否か」で問題の性質が変わり AI/人間境界が決まる。最も危険なのは Stage4 (Logic, AI カバー率60%) の中間ゾーンで、中途半端な高さが「AI が見たから大丈夫」という油断 (認知のショートカット) を生む。

**手法**:
- 6段階と AI比率: Format 100% / Lint 100% / Style 90% / Logic 60% / Design 30% / Architecture 0%
- Format と Lint を分離 (見た目の規約 vs 意味の規約)
- 逆説運用ルール: AI が指摘した部分は AI に任せ、AI が指摘しなかった部分こそ人間が念入りに見る。AI コメントゼロの PR こそ仕様書を開いて30分かける
- 仕様書由来のエッジケースは AI に見えない (コードベース内整合性しか見ない)。著者が本番に通した3バグ = 空配列スキップ仕様違反 / リトライ条件 429のみ vs 5xx / ページネーション境界1件ずれ
- Design層: 「パターンを増やすべきか減らすべきか」の方向性判断は AI 不可。tenant_id 等のローカルルールは AI に伝わりにくい
- Architecture層: ADR を事前に書く。ADR を書くと Stage6 の一部が Stage5/4 に降りてくる (文章化で AI 比率が上がる)
- AI コードレビューツールのバグ検出精度: Macroscope 48% / CodeRabbit 46% / Cursor BugBot 42% / Greptile 24%。CodeRabbit F1 51.5% recall 52.5%

**根拠**: 著者の実務経験 (本番バグ3件) + AI レビューツール比較データ (Macroscope/CodeRabbit/BugBot/Greptile)

**前提条件**: チーム開発の PR レビュー (CodeRabbit/Copilot 契約、2人ペアレビュー、チーム文化醸成)

## 重要な前提ミスマッチ

記事は完全にチーム開発 PR レビュー前提。一方 dotfiles は単一ユーザー × Claude Code harness の自己レビュー (Codex Review Gate + /review skill)。人間レビュアーは本人1人。多くの手法 (CodeRabbit/Copilot 導入、2人ペアレビュー、チーム文化、毎週30分の指摘削減) は構造的に N/A。

## Phase 1.5 Saturation Gate

- family: code-review-best-practices (実レポート N≥6: agents-md-review-skills, findy-readability, harness-engineering-human-review, code-review-graph, openclaw-autoreview, cursor-auto-review-run-mode)
- 判定: PASS (warning) — 飽和域だが採用率 ≥20% (openclaw 採用5+4, harness/findy integrated)。delta 計算不要
- Stale-Plan Audit: 直近3件すべて status 明示済 or 30日未満で skip

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 6段階の問題性質による段階分け | Already | reviewer-capability-scores.md:33,41 に Deterministic/Semi-deterministic/Subjective 分類が既存。「正解が一意か」軸は実質存在 |
| 2 | Format/Lint 分離 | Already | lefthook で biome/ruff format ⇄ oxlint/ruff lint 分離済 |
| 3 | Style 90% (AI 主導、人間が例外処理) | Already | /review skill + Codex Review Gate でカバー |
| 4 | 却下理由記録で次の精度向上 | Already | agent-memory (codex-reviewer/code-reviewer MEMORY) でフィードバックループ実装済 |
| 5 | 逆説運用ルール (AI 沈黙=危険信号) | Gap | /review に「PASS/指摘ゼロ→仕様・ADR を人間が深掘り」の逆向きルールが未実装 |
| 6 | 仕様由来エッジケースは AI に見えない | Already | Codex Spec/Plan Gate + edge-case-analysis を M/L で必須化済 |
| 7 | ADR を事前に書く | Already | docs/adr/ に template.md + 実 ADR 存在 |
| 8 | ADR↔実装整合の AI 機械チェック | Partial | docs/adr/template.md は Context/Decision/Consequences のみ。affected paths/invariants/verification command 等の機械照合フィールドがない |
| 9 | AI 検出率60%の限界認識 | Already | reviewer-capability-scores + failure-taxonomy + バイアス記述済 |
| — | ペアレビュー/CodeRabbit導入/チーム文化 | N/A | 単一ユーザー harness |

## Phase 2 + 2.5 判定テーブル (Codex 批評反映後)

| # | 手法 | 最終判定 | 根拠 |
|---|------|---------|------|
| 1 | 6段階の問題性質による段階分け | Already (強化不要) | Codex: reviewer-capability-scores.md:33,41 に Deterministic/Semi-deterministic/Subjective 分類が既存。「正解が一意か」軸は実質存在。新フレーム不要 (元 Partial から降格) |
| 5 | 逆説運用ルール (AI 沈黙=危険信号) | **採用 (S)** | 記事の真の核心。/review に「PASS/指摘ゼロ→仕様・ADR を人間が深掘り」の逆向きルールが未実装。個人 harness に直接効く (元 Gap小から昇格・最優先) |
| 8 | ADR↔実装整合の AI 機械チェック | **採用 (S)** | Codex: docs/adr/template.md は Context/Decision/Consequences のみ。affected paths/invariants/verification command 等の機械照合フィールドがない (元 Already から Partial/Gap小に降格) |
| 2 | Format/Lint 分離 | Already (強化不要) | lefthook で biome/ruff format ⇄ oxlint/ruff lint 分離済 |
| 4 | 却下理由記録で次の精度向上 | Already (強化不要) | agent-memory (codex-reviewer/code-reviewer MEMORY) でフィードバックループ実装済 |
| 6 | 仕様由来エッジケースは AI に見えない | Already (強化不要) | Codex Spec/Plan Gate + edge-case-analysis を M/L で必須化済 |
| 9 | AI 検出率60%の限界認識 | Already (強化不要) | reviewer-capability-scores + failure-taxonomy + バイアス記述済 |
| — | ペアレビュー/CodeRabbit導入/チーム文化 | N/A | 単一ユーザー harness。Codex も N/A 支持 |

## Phase 2.5 メモ

- Codex (gpt-5.5, exec): 採用1件が妥当と評価し、私 (Opus) の Pass 2 を2方向に補正 — 手法1は過大評価 (既存カバー見落とし)、手法8は過小評価 (ADR の存在で甘く見た)。最優先は手法5。根拠を file:line で提示。最終的に手法5+8 の2件採用に収束
- Gemini: QUOTA_EXHAUSTED (429, quota リセットまで約3h51m) で利用不可。周辺知識補完は欠落。bias mitigation の核 (異モデルファミリ批評) は Codex で成立

## Phase 3 Triage 結果

- 手法5: シンプル版で採用 (verdict は PASS のまま、新ステータス PASS_WITH_HUMAN_SPEC_PASS は作らず KISS)
- 手法8: 採用

## Phase 4 実装内容 (S規模, 実装済)

1. `.config/claude/skills/review/SKILL.md` Step 4 Synthesis に `### Negative Signal Review Rule（AI 沈黙 = 盲点シグナル）` を追加 (+22行)。条件: verdict=PASS かつ Critical/Important=0 かつ M/L かつ logic/security/API/harness を触る かつ (spec/ADR 存在 or comprehension_confidence<4) → `[NEGATIVE SIGNAL]` 推奨を出力。verdict は変えない
2. `docs/adr/template.md` Decision の後に `## Verification` セクションを追加 (+8行)。Affected paths / Invariants / Verification command の3フィールド

## 教訓

- チーム前提記事 → 単一ユーザー harness への翻訳では、表層手法 (ツール導入/ペアレビュー) は N/A だが、その背後の認知原則 (AI 沈黙=盲点、文章化=AI チェック可能性拡大) は個人版に翻訳可能。enterprise→個人 absorb の原則翻訳分離 (zero-trust absorb と同じパターン)
- Codex が Opus の Pass 2 を双方向補正 (過大評価と過小評価の両方) した好例。bias mitigation が機能
- Gemini quota 切れ時も Codex 単独で異モデルファミリ批評は成立 (Phase 2.5 の最低要件は満たせる)
