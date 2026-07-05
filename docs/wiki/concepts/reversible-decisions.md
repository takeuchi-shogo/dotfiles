---
title: 失敗できる意思決定 (Reversible Decisions)
topics: [decision, harness, agent]
sources: [2026-04-19-autogenesis-absorb-analysis.md, 2026-04-21-harness-pipeline-absorb-analysis.md, 2026-04-23-skill-graphs-2.0-absorb-analysis.md, 2026-04-23-team-harness-template-analysis.md, 2026-04-24-harness-engineering-absorb-analysis.md, 2026-04-26-workflow-trellis-absorb-analysis.md, 2026-04-30-learn-build-skip-2026-absorb-analysis.md, 2026-05-23-subagent-context-fork-revisit-analysis.md, 2026-05-31-zero-trust-ai-agents-absorb-analysis.md, 2026-06-02-typhoon-nix-mise-absorb-analysis.md, 2026-06-05-recursive-self-improvement-anthropic-absorb-analysis.md, 2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md, 2026-06-25-acrouter-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 15
confidence: established
---

# 失敗できる意思決定 (Reversible Decisions)

## 概要

正解を探すのではなく「失敗してもやり直せる状態」を先に設計することで素早く決める意思決定原則。情報を集めれば解ける「判断」と情報不足の中で選ぶ「決断」を区別し、決断にはやり直し可能・学習可能・素早く試せるの 3 要素を備えさせる。dotfiles では M/L プランの撤退条件テンプレート (`references/reversible-decisions.md`) として実装されている。

> 正解を探すのではなく、失敗してもやり直せる設計にすることで素早く意思決定する。

## 核心概念

### 判断 vs 決断

| | 判断 | 決断 |
|---|------|------|
| 定義 | 情報を集めれば理屈で答えが出せる | 情報不足の中で答えを出す |
| アクション | 調査タスクを先に実行 | 「失敗できる状態」を作って進む |
| 例 | ライブラリの API 仕様確認 | マイクロサービス vs モノリスの選択 |

### 失敗できる3要素

1. **やり直し可能**: ロールバック・代替案が存在する
2. **学べる**: 仮説が検証可能（観測可能）で結果を客観分析できる
3. **素早く試せる**: 結果がすぐ出る、投資リソースが少ない、影響範囲が明確

### 4段階アプローチ

1. 決断に必要な条件を整理する
2. 素早く開始し小さく失敗できるよう設計する
3. 社内外の知見を多く集める
4. それでも難しければ結論を先送りする

## 主要な知見（外部知見の統合）

- **機会費用フィルター**: 採用判断の5-testの一つ「6ヶ月スキップした場合のコストは？（通常ほぼゼロ）」は、既存のROIテーブル（コスト×効果）とは直交する軸。FOMOを機会費用の反転として使うことで「失敗できる」判断を後押しする
- **Reproduce-first attestation**: パッチを当てる前にバグを再現することをブロッキングゲート化する。「素早く小さく失敗できる」設計を実装レベルで具体化した形
- **Control Surface Override**: 規模が小さくても auth 変更・不可逆操作（DB migration/削除）・harness 変更・breaking change は「失敗できない決断」として一段階重いゲートを強制する。判断 vs 決断の区別を「規模」でなく「可逆性」で補正する
- **Stale-Plan Audit**: 過去に採用したタスクが期限（30日）を過ぎても未実施なら、implemented/superseded/narrowed/retired/kept のいずれかを強制的に再判断させる。`kept` を選ぶ場合は `kept-by: YYYY-MM-DD` を明示記録し、「決めたことにして放置する」という暗黙の先送りと区別する
- **ADRの記入例による着手コスト低減**: 空のADRテンプレートより、実例（採用理由付き）を1つ添えるほうが「最初の1行」を書く摩擦を大きく下げる。不可逆な変更（auth/payment）には2-sign-off（CODEOWNERS + branch protection）で人間承認を強制する
- **着手条件と撤退条件をセットで明文化する実例**: データ駆動のルーティング手法（ACRouterなど）を、ベンチマークの弱さでなく「自分のデータ体制が前提を満たさない」という理由で明確に却下しつつ、「将来これが揃えば着手する」条件を先に書いておくことで再検討のコストを下げる

## 関連パターン

### ゆっくり考えて素早く実行する

失敗プロジェクト = 素早く考えてゆっくり動く。成功プロジェクト = ゆっくり考えて素早く動く。プロジェクト期間が長いほどブラック・スワンのリスクが増大する。

- **参照クラス予測法**: 類似事例を参照し、悲観的に予測する
- **反証探索**: 確証バイアスを避け、自分の仮説が失敗する条件を積極的に探す
- **インチストーン**: WBS を「それだけで検証可能な最小単位」に分解する

### One change at a time

変数は少ないほうが仮説検証しやすい。1回の実験で1つの変数だけ変える。

### 後に変更可能な設計

コンテナ（実行環境分離）、REST（インターフェース変更可能性）、CQRS（責務分離）、認証/認可分離。

## dotfiles での適用

| 概念 | 適用先 |
|------|--------|
| 判断 vs 決断 | `references/reversible-decisions.md` の分類フレーム |
| 撤退条件 | Spec テンプレートの Exit Criteria セクション |
| 反証探索 | Plan 前チェックリスト（必須項目） |
| One change at a time | `references/experiment-discipline.md` の変数最小化原則 |
| Build to Delete | CLAUDE.md の core_principles（既存） |
| プロトタイプファースト | `/spike` スキル（既存） |
| 機会費用フィルター | `.claude/skills/absorb/references/triage-criteria.md` の Launch Filter (5-test) |
| Control Surface Override | `references/stage-transition-rules.md` |
| Stale-Plan Audit | `.claude/skills/absorb/references/topic-family-saturation.md` Step 7 |
| 着手条件/撤退条件の明文化 | `docs/plans/2026-04-11-routing-observability-closed-loop.md` の着手条件注記 |

## ソース

- 曽根壮大「失敗できる意思決定とソフトウェアとの正しい歩き方」([SpeakerDeck](https://speakerdeck.com/soudai/designing-for-reversible-decisions))
- 分析レポート: `docs/research/2026-04-04-reversible-decisions-analysis.md`
- [Autogenesis: A Self-Evolving Agent Protocol](../../research/2026-04-19-autogenesis-absorb-analysis.md) — 自己進化エージェント論文、一部の強化案のみ採用し統一リソース層は棄却
- [How I got banned from GitHub due to my harness pipeline](../../research/2026-04-21-harness-pipeline-absorb-analysis.md) — GitHub BAN体験記からreproduce-first等7件採用
- [Skill Graphs 2.0](../../research/2026-04-23-skill-graphs-2.0-absorb-analysis.md) — atoms/molecules/compounds 3層合成モデル、composition depth計測とADR追加を採用
- [claudecode-harness — Team Claude Code Harness Template](../../research/2026-04-23-team-harness-template-analysis.md) — チームharnessテンプレ記事、team-project雛形一式を新設
- [A Closer Look at Harness Engineering from Top AI Companies](../../research/2026-04-24-harness-engineering-absorb-analysis.md) — Harness Engineering記事、reasoning budget表等3タスクを追記
- [Workflow Trellis (2x2フレームワーク)](../../research/2026-04-26-workflow-trellis-absorb-analysis.md) — 2軸ワークフロー設計論、3件を既存参照に統合
- [What to Learn, Build, and Skip in AI Agents (2026)](../../research/2026-04-30-learn-build-skip-2026-absorb-analysis.md) — AIエージェント要点記事、機会費用フィルター1件のみ採用
- [Keep your Claude Code context clean with Subagents (revisit)](../../research/2026-05-23-subagent-context-fork-revisit-analysis.md) — 同一記事再読込で過去採用タスク停滞を検出、Stale-Plan Audit新設
- [Zero Trust for AI Agents](../../research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md) — Zero Trust eBook、暗号ID等はN/A、Agent-BOM-lite等3件をL規模で採用
- [私の最強のMac開発環境2026 (Nix+mise)](../../research/2026-06-02-typhoon-nix-mise-absorb-analysis.md) — Nix+mise記事を検証、mise未活用のランタイム二重管理事故を発見し統合
- [When AI builds itself (recursive self-improvement)](../../research/2026-06-05-recursive-self-improvement-anthropic-absorb-analysis.md) — Anthropic再帰的自己改善論考、判断計測とメタ安全層3件を採用予定
- [Claude Codeで自己改善ループを作った話](../../research/2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md) — sonicgarden自己改善ループ記事、publicity-reviewゲート等を採用実装
- [Agent-as-a-Router (ACRouter)](../../research/2026-06-25-acrouter-absorb-analysis.md) — ACRouterはdata regime不一致で却下、閉ループ着手条件のみcodify
