---
title: 自動コードレビュー
topics: [coding, evaluation]
sources: [2026-03-26-findy-code-review-readability-analysis.md, 2026-03-26-harness-engineering-human-review-analysis.md, 2026-03-30-code-review-graph-analysis.md, 2026-04-01-spec-and-verify-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 17
confidence: established
---

# 自動コードレビュー

## 概要

自動コードレビューは、AI エージェントとハーネスを組み合わせて、コード品質・可読性・仕様準拠を自動検証するプロセスである。意思決定を伴わない品質チェックは人間のレビューが不要であり、AI に完全委譲できる。一方で「Spec & Verify」パラダイムへの移行により、人間は仕様レビューに集中し、コード検証はエージェントが担うという役割分担が生まれつつある。

## 主要な知見

- **コードレビュー指摘の 42.2% は可読性に関するもの**: Linter でカバーできるのは 30% 未満であり、AI レビューが補完すべき領域が明確に存在する
- **3 層可読性モデル**: Legibility（表記）/ Readability（構造）/ Understandability（意味・意図）の 3 層で体系化することで、レビューの観点を網羅できる
- **Atoms of Confusion**: 誤読の最小単位（15 パターン）を定義することで、AI レビューの検出精度を向上させられる
- **5 ステップレビューループ**: Review → Triage → Fix → Validate → Commit のサイクルを max 6 回繰り返し、ゼロ指摘を終了条件とする
- **オシレーション検出**: commit diff から A→B→A パターン（振り子修正）を検出し、directive pinning で固定することで収束を促す
- **Blast radius 分析によるトークン削減**: Tree-sitter AST で構造グラフを構築し、変更の影響範囲（blast radius）のみを読ませることで平均 8.2x のトークン削減を実現
- **Spec & Verify パラダイム**: コードではなく仕様をレビューし、実装検証はエージェントに委譲する。Dual Spec（Product Spec + Tech Spec）の分離が効果的
- **バンドエイド修正検出**: 別セッションでの検証フェーズで「根本原因修正 vs 一時しのぎ」を明示的に判定する
- **AI 可読性の限界**: 全体抽象化の失敗・論理表現の誤認識の 3 パターンは AI レビューが苦手な領域であり、人間による補完が必要
- **Orient Gate と Non-Findings**: 監査・レビュー着手前に境界・主要フロー・invariants・runtime surface の把握を必須化する（Orient Gate）。あわせて「検討した上で問題なしと判断した箇所」を Non-Findings として明示すると、同じ箇所の再監査・再指摘を防げる `[EXTRACTED, conf=75]`
- **PASS 後の cosmetic 再レビュー禁止 (PASS-exit lock)**: helper/gate が exit 0 で findings ゼロになった時点で即座に停止し、「もっと綺麗な締め」「セカンドオピニオン」目的の追加レビューを走らせない。レビュー内から nested reviewer・reviewer panel を起動することも禁止する `[EXTRACTED, conf=80]`
- **逆説運用ルール（AI 沈黙 = 盲点シグナル）**: AI が指摘した箇所は AI に任せてよいが、AI が何も指摘しなかった PR こそ、仕様書・ADR を人間が深掘りする価値が高い。指摘の有無は「安全」の証明にならない `[EXTRACTED, conf=80]`
- **Evidence-based feedback と Design-first gate**: レビュー指摘は具体的な証拠（file:line や再現手順）の引用を義務とし、意見ではなく技術的事実として提示する。設計レベルの重大な問題は Logic/Style レベルの指摘を待たず即座に差し戻す `[EXTRACTED, conf=75]`
- **fix 後の twin-rerun**: レビュー指摘によるコード修正が発生したら、focused test と構造化レビューの両方を再実行する。片方のみの再実行は、修正が新たな問題を持ち込むリスクを見逃す `[EXTRACTED, conf=75]`
- **観点混在によるレビュー精度低下**: 1 回のレビューでアーキテクチャ・品質・安全性など複数観点を同時に見ると、注意が分散し精度が落ちる（実測でアーキ42%/品質36%/安全31%に分散）。観点ごとに独立してレビューを回す設計が精度を上げる `[EXTRACTED, conf=70]`
- **assertion 書き換えは tautological testing と別の失敗モード**: エージェントが実装の挙動を変えた後、テストの assertion をその挙動に合わせて書き換えると、テスト自体は「通る」が誤った挙動を encode してしまう。これは既存の tautological testing 検出（テスト単体の質を見る）では捕まらず、同一 diff 内の「非テスト挙動変更」と「既存 assertion 改変」の組み合わせを見る diff-delta 検証が必要 `[EXTRACTED, conf=75]`
- **公開差分の credential leak gate (publicity-review)**: 無人の自己改善ループや自動 PR 作成では、公開リポジトリへの push 前に staged の added-lines のみを対象とした credential leak 検査が要る。既存のパス・ユーザー識別子が意図的に露出しているリポジトリでは、hard block の対象を credential のみに絞りスコープを翻訳する必要がある `[EXTRACTED, conf=70]`

## 実践的な適用

dotfiles リポジトリでは `/review` スキルが Codex Review Gate（codex-reviewer + code-reviewer 並列）を自動起動する。`cross-file-reviewer` が Grep ベースの blast radius 分析を行い、`review-dimensions.md` が評価軸（maintainability 0.20 等）を定義している。`code-review-graph` MCP サーバーが構造グラフベースの影響分析（`get_impact_radius`）を提供し、Grep ベースでは見落とす間接依存（depth=2+）を補完する。`review-consensus-policy.md` §3.1 でコード振り子検出を定義している。`references/ci-fix-policy.md` が CI 修正の 3 hard rule を定義し、`test-analyzer` 4c がテスト assertion 書き換えを検出する。`skills/review/SKILL.md` の Negative Signal Review Rule が AI 沈黙時の人間深掘りを促し、`docs/adr/template.md` の Verification セクションが ADR と実装の機械照合を可能にする。`scripts/security/publicity-scan.py` が pre-commit で公開差分の credential leak を block する。`.config/claude/skills/audit/SKILL.md` が Orient Gate と Non-Findings を実装している。

## 関連概念

- [quality-gates](quality-gates.md) — レビューを品質ゲートとして組み込む仕組み
- [agent-evaluation](agent-evaluation.md) — エージェント自身の出力評価の方法論
- [spec-driven-development](spec-driven-development.md) — Spec & Verify パラダイムの前提となる仕様駆動開発
- [nrslib サーヴァントエンジニアリング (2026-06-12)](../../research/2026-06-12-servant-engineering-absorb-analysis.md) — 観点別並列レビュー (Faceted Prompting)・Review Tiering・Worker/Judge 分離によるレビュー速度改善

## ソース

- [コードレビューに効く読みやすさの処方箋](../../research/2026-03-26-findy-code-review-readability-analysis.md) — 3 層可読性モデル・Linguistic Anti-patterns・Atoms of Confusion の学術的体系化
- [意思決定を伴わないレビューの AI 完全委譲](../../research/2026-03-26-harness-engineering-human-review-analysis.md) — 5 ステップループ・オシレーション検出・ハーネス 4 役割（Constrain/Inform/Verify/Correct）
- [code-review-graph](../../research/2026-03-30-code-review-graph-analysis.md) — Tree-sitter AST グラフによる blast radius 分析と 8.2x トークン削減
- [Spec & Verify: What comes after human code review](../../research/2026-04-01-spec-and-verify-analysis.md) — Dual Spec パラダイム・Behavior Verification・Self-improving verification loops
- [Better Harness: Eval-Driven Hill-Climbing (LangChain/Z.ai)](../../research/2026-04-09-better-harness-eval-hill-climbing-analysis.md) — Eval駆動ハーネス改善記事、回帰保護など全項目採用
- [CREAO AI-First戦略記事 (CREAO CTO)](../../research/2026-04-14-creao-ai-first-analysis.md) — harness engineering手法から4原理のみ抽出し採用
- [Tech-Debt-Skill (ksimback) absorb分析](../../research/2026-04-26-tech-debt-skill-absorb-analysis.md) — 技術負債監査スキルを分析、/auditへ9項目統合
- [Warp oz-skills (15 skill) absorb分析](../../research/2026-05-07-warp-oz-skills-absorb-analysis.md) — CI-fix policy等6件採用
- [Cursor thermo-nuclear-code-quality-review skill](../../research/2026-05-24-cursor-team-kit-thermo-nuclear-absorb-analysis.md) — 厳格レビューrubricから構造的ブロッカー3件を統合
- [Google eng-practices Code Review Guide](../../research/2026-05-24-google-eng-practices-absorb-analysis.md) — 公式レビューガイドから18項目採用しレビュー強化
- [Google eng-practices 深部調査レポート (2nd pass)](../../research/2026-05-26-google-eng-practices-deep-dive.md) — 前回absorbの深掘り、developer視点指針の欠落を発見
- [OpenClaw autoreview SKILL.md (Peter Steinberger)](../../research/2026-05-28-openclaw-autoreview-absorb-analysis.md) — 自動コードレビュー記事、PASS後再レビュー禁止等5件採用
- [コードレビュー6段階とAI/人間の境界 (kenimo49)](../../research/2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md) — AI沈黙シグナルとADR検証欄の2件を実装採用
- [Claude Codeで自己改善ループを作った話 (sonicgarden)](../../research/2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md) — publicity-reviewゲート等を採用実装
- [nrslib サーヴァントエンジニアリング — レビュー速度改善](../../research/2026-06-12-servant-engineering-absorb-analysis.md) — 計測基盤・アサーション検出等8件を統合プラン化
- [Agentic Code Review essay (Sean Goedecke系)](../../research/2026-06-17-agentic-code-review-absorb-analysis.md) — テスト改変挙動ドリフト検出ルールをtest-analyzerに追加
- [How to Review AI-Generated Code Like a Senior Developer (Mari)](../../research/2026-06-20-review-ai-code-mari-absorb-analysis.md) — 実データ性能観点のrouting漏れのみ採用
