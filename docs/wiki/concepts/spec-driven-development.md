---
title: 仕様駆動開発
topics: [coding]
sources: [2026-03-18-spec-is-code-analysis.md, 2026-04-01-spec-and-verify-analysis.md, 2026-03-20-comprehension-debt-analysis.md, 2026-04-02-how-to-vibe-code-analysis.md, 2026-04-04-pocock-5-agent-skills-analysis.md, 2026-04-11-spec-driven-usable-validation-analysis.md, 2026-04-29-mattpocock-skills-absorb-analysis.md, 2026-05-27-sairahul-7agent-software-factory-absorb-analysis.md, 2026-05-30-claude-code-harness-absorb-analysis.md, 2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md]
updated: 2026-07-05
confidence: established
source_count: 10
last_validated: 2026-07-05
---

# 仕様駆動開発

## 概要

仕様駆動開発（Spec-Driven Development）は、AI エージェントへの実装委譲前に仕様書を人間がレビューし、コードではなく意図・制約・受け入れ基準を合意するアプローチである。「仕様書は労力節約ツールではなく思考整理ツール」という認識が重要であり、精密すぎる仕様はコードに収束するという逆説（Borges の地図問題）を踏まえた適切な粒度管理が求められる。AI 支援開発で生じる「Comprehension Debt（理解の負債）」を予防する主要な手段でもある。

## 主要な知見

- **精度天井の認識**: 仕様書に擬似コード・DB スキーマ・条件分岐の網羅的記述が入ったら、コードを直接書くべきサイン。仕様書とコードが 1:1 対応になる限界点（Borges の地図問題）を意識する
- **Spec slop の回避**: AI 生成の仕様書は「形式は整っているが中身が空虚」になりやすい。急いだ仕様書は slop になるため、/spec と /interview を使って質を担保する
- **Dual Spec 分離**: Product Spec（ユーザー行動ベース）+ Tech Spec（アーキテクチャレベル）を分離することで、チームレビューとエージェント実装の役割分担が明確になる
- **Comprehension Debt（理解の負債）**: AI 生成コードが増える速度が人間の理解速度を上回ることで生じる「存在するが誰も理解していないコード」の蓄積。Anthropic の研究では AI 利用者が非利用者比で 17% 低い理解度を示した
- **速度の非対称性**: AI の生成速度 >> 人間の評価速度。この非対称性を意識せずに進めるとレビューの表面的な確認が常態化する
- **仕様レビューゲート**: M・L 規模の変更では実装前に仕様レビューを必須とすることで、理解の負債発生を構造的に防ぐ
- **Intent / Constraints / Acceptance criteria の 3 柱**: 有効な仕様書の最小構成要素。この 3 つが揃えば one-shot 実装が可能になる
- **不確実なときはプロトタイプ先行**: 仕様が曖昧な場合は仕様書を精密化しようとするより `/spike` でプロトタイプを作り、発見した知識を仕様に落とし込む
- **垂直スライス分解（Tracer Bullet）**: PRD を水平スライス（API層だけ、DB層だけ）ではなく全レイヤーを貫く薄い垂直スライスに分解する。unknown unknowns を早期に炙り出し、blocking 関係を明示することで並列エージェント実行を可能にする
- **「動く」と「使える」は別次元というフレーム**: 仕様通りの機能検証（Evaluator）の先に、実際に使えるかを検証する UX Reviewer という第4の軸がある。dotfiles では product-reviewer と `/validate`・UI Quality 3-Layers で概ねカバー済みだったが、「iteration 間の UX スコアの定量差分比較」というギャップが残っていた `[EXTRACTED, conf=75]`
- **UX 差分の定量比較を検証ゲートに統合**: ui-observer に baseline snapshot 比較 + JSONL スコア履歴を追加し、`/validate` の acceptance criteria 照合後に UX スコア閾値チェックを組み込むことで、機能検証と体験検証を1つの検証ループに統合した `[EXTRACTED, conf=75]`
- **Wire Before You Decorate（配線してから装飾する）**: プロトタイプは先に動作確認（配線）を済ませ、磨き込み（装飾）は後回しにするという試作順序の原則。golden-principles.md に GP-012 として追加 `[EXTRACTED, conf=70]`
- **Issue の Execution Mode 明示 (HITL/AFK)**: PRD を垂直スライス Issue に分解する際、各 Issue に「人間承認が必要 (HITL)」か「自律進行可能 (AFK)」かのマーカーを付与することで、並列着手可否の誤認を防ぐ `[EXTRACTED, conf=80]`
- **設計インタビュー中の Auto Mode リスク**: grill-me 型の逐次質問インタビューで Auto Mode が AskUserQuestion によるポーズをスキップしてしまう実例が確認されている。設計決定木を1問ずつ人間に確認させる仕様インタビューでは Auto Mode を明示的に OFF にすべきという起動条件を明文化 `[EXTRACTED, conf=75]`
- **仕様プロセスを狭いスコープの process encoding に閉じる discipline**: grill-me / to-prd / to-issues のような各スキルは「何を考えるか」ではなく「どう考えるか」の手順だけを encode し、汎用知識のダンプを避ける。個人 artifact をむやみに一般化しないという姿勢が travel する仕様プロセスの条件になる `[EXTRACTED, conf=70]`
- **Acceptance test は user story に対して行う（unit test の代替ではない）**: 仕様駆動開発における検証は、実装の内部構造ではなくユーザーストーリー（受け入れ基準）に対して行うべきという整理。既存の test-engineer/test-analyzer の役割分担と同型と判定され新規採用はなし `[EXTRACTED, conf=60]`
- **アーキテクチャ前提の誤りは patch でなく discard**: 誤った前提で進んだ会話・実装は部分修正で辻褄を合わせず、会話ごと破棄して仕様に立ち返る方が良いという運用原則。「壊れたら即STOP・ごまかし禁止」の原則と同型と判定され新規性は低い `[INFERRED, conf=55]`
- **Contract-First Delivery というフレーミング**: 仕様書 (spec.md 相当) と Plans (タスク台帳) の2ファイルを Single Source of Truth とし、開発の重心を「チャット出力」から「デリバリ証拠」に移すという捉え方。dotfiles では `PLANS.md` + `docs/specs/*.prompt.md` + product-reviewer の整合性検証としてすでに同型の仕組みが存在する `[EXTRACTED, conf=70]`
- **エージェントが直接見ていないデータは未知のままにする**: 仕様に「未確認情報を確認済みとして扱わない」ことを明記する設計。Comprehension Debt の予防（理解の負債を仕様レビューで防ぐ）と同じ方向性の原則として位置づけられる `[EXTRACTED, conf=65]`
- **問題の性質（正解が一意か否か）が AI/人間の境界を決める**: Format 100%→Lint 100%→Style 90%→Logic 60%→Design 30%→Architecture 0% という段階モデル。一意に決まる領域は AI に委ね、方向性判断が要る領域は人間が担うという切り分けは、仕様レビューゲートの設計にも応用できる `[EXTRACTED, conf=75]`
- **仕様の明文化は AI のレビュー可能領域を広げる**: Architecture 層のような本来 AI 比率 0% の判断も、ADR として事前に文章化すればチェック可能な Design/Logic 層に降りてくる。「仕様書は思考整理ツール」という既存の認識を補強し、明文化そのものが AI 委譲可能性を拡大する効果を持つことを示す `[EXTRACTED, conf=80]`
- **AI 沈黙は盲点シグナル（逆説運用ルール）**: AI が指摘ゼロの変更ほど、仕様書由来のエッジケース（空配列スキップ・リトライ条件・ページネーション境界など、コードベース内整合性からは検出できない要件）を人間が仕様書を開いて念入りに確認すべきという運用ルール。`/review` skill の Synthesis に Negative Signal Review Rule として実装済み `[EXTRACTED, conf=80]`
- **ADR に Verification 欄を追加し仕様と実装の機械照合を可能にする**: Affected paths / Invariants / Verification command の3フィールドを ADR テンプレートに追加することで、Context/Decision/Consequences のみだった ADR が実装との整合性チェックに使えるようになる `[EXTRACTED, conf=75]`

## 実践的な適用

dotfiles リポジトリでは `/spec` スキルが Prompt-as-PRD を生成し、`/interview` が仕様のための深いインタビューを実施する。`/prd-to-issues` が PRD を垂直スライスの独立 Issue 群に分解し、`/autonomous` や `/rpi` による並列実行の起点となる。`overconfidence-prevention.md` が仕様なし実装への抑制ガイドラインを定義している。EPD ワークフロー（`/spec` → `/spike` → `/validate` → `/epd`）が不確実性の高いタスクの標準プロセスとなっており、`Codex Spec/Plan Gate`（M 規模以上必須）が仕様書を人間に代わって機械的にレビューする。`/prd-to-issues` の Issue テンプレートには Execution Mode (HITL/AFK) が明示され、実行可否の誤認を防ぐ。`ui-observer` は baseline snapshot 比較を備え、`/validate` の acceptance criteria 照合後に UX スコア閾値ゲートを通す。`docs/adr/template.md` には Verification セクション（Affected paths / Invariants / Verification command）が追加され、`/review` skill には AI 指摘ゼロ時に仕様書を人間が深掘りする Negative Signal Review Rule が実装されている。

## 関連概念

- [automated-code-review](automated-code-review.md) — 仕様に基づいた実装検証を自動化するパターン
- [quality-gates](quality-gates.md) — 仕様レビューを品質ゲートに組み込む仕組み
- [workflow-optimization](workflow-optimization.md) — 仕様駆動を含む開発ワークフロー全体の最適化

## ソース

- [A Sufficiently Detailed Spec Is Code](../../research/2026-03-18-spec-is-code-analysis.md) — 仕様書の精度天井・Borges の地図問題・Spec slop の概念と精度管理ガイドライン
- [Spec & Verify: What comes after human code review](../../research/2026-04-01-spec-and-verify-analysis.md) — Dual Spec パラダイム・仕様チームレビューへの移行・Self-improving verification loops
- [Comprehension Debt](../../research/2026-03-20-comprehension-debt-analysis.md) — AI 生成コードによる理解の負債の定量化と仕様レビューゲートによる予防策
- [How to Vibe Code: A Developer's Playbook](../../research/2026-04-02-how-to-vibe-code-analysis.md) — Spec before prompt の 3 柱・Context engineering・Plan→Execute→Verify ループの実践ガイド
- [5 Agent Skills I Use Every Day](../../research/2026-04-04-pocock-5-agent-skills-analysis.md) — PRD→垂直スライス Issue 分解（Tracer Bullet）・Deep Modules によるエージェントフレンドリーなコードベース改善
- [仕様通り動くの先へ。Claude Codeで「使える」を検証する](../../research/2026-04-11-spec-driven-usable-validation-analysis.md) — UX Reviewer 段階と Wire Before You Decorate 原則のみ採用、他は既存カバー済み
- [AlphaSignal: Skills For Real Engineering (mattpocock/skills)](../../research/2026-04-29-mattpocock-skills-absorb-analysis.md) — 5-skill chain の大半は既存実装済み、Issue の HITL/AFK マーカーと Auto Mode 警告の2件を採用
- [How to Build a Software Factory with Claude Code (Sai Rahul, 7-agent)](../../research/2026-05-27-sairahul-7agent-software-factory-absorb-analysis.md) — 7エージェント分業は既存 `/epd`+`/rpi` と同型と判定、folder scoping/API summary handoff は前提不一致で不採用
- [How Claude Code Harness turns agent coding into a contract-first delivery loop](../../research/2026-05-30-claude-code-harness-absorb-analysis.md) — spec+Plans の2ファイル SSoT フレームは既存と同型、retired-concepts registry 等ハーネス寄りの4件を別途採用
- [コードレビュー6段階と AI/人間の境界](../../research/2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md) — AI沈黙=盲点シグナルの逆説運用ルールと ADR Verification 欄の2件を採用
