---
title: 自己改善エージェント
topics: [agent, ml-rl]
sources: [2026-03-18-autocontext-recursive-improvement-analysis.md, 2026-03-19-compounding-agent-analysis.md, 2026-03-30-self-evolving-claude-code-analysis.md, 2026-03-26-hyperagents-analysis.md, 2026-04-06-asi-evolve-analysis.md, 2026-04-07-meta-agent-continual-learning-analysis.md, 2026-04-07-self-optimizing-dr-agents-analysis.md]
updated: 2026-04-07
---

# 自己改善エージェント

## 概要

自己改善エージェントとは、実行ごとにコールドスタートするステートレスな LLM に対して「実行→評価→学習→永続化→再実行」のクローズドループを設け、世代を跨いだ知識蓄積と能力向上を実現するアーキテクチャである。autocontext（greyhaven-ai）はこのループで Grid CTF において 2 世代で 33 個のレッスンと 5,870 文字の actionable playbook を自動生成した。Hyperagents（arXiv: 2603.19461）は一歩進んで Task Agent と Meta Agent を分離し、改善手続き自体を改善する「メタ認知的自己修正」を実現しており、メタレベル改善がドメイン間で 60〜80% 転移することを示している。

## 主要な知見

- **ループが複利を生む**: スコアリングとフィードバックループを持つスキルが「スクリプト」との本質的な違い。スコアなしの改善は guesswork、スコアありなら systematic
- **Playbook abstraction**: 世代を跨いで成長する「生きたドキュメント」として成功戦略・失敗モード・ティア別ルールを蓄積する。1 回限りのタスクには不向き
- **Elo ベースの進化ゲーティング**: 改善しない戦略はロールバックし、検証済みの知識のみ永続化する。累積的品質指標による前進条件が品質保証の鍵
- **verify: 行付きルール**: "A rule without a verification check is a wish. A rule with a verification check is a guardrail." ルールには必ず機械検証手段を添付する
- **Task Agent / Meta Agent 分離**: タスク実行層と改善層を明示分離し、メタレベル修正手続き自体が編集可能な構造（Hyperagents DGM-H）
- **閾値ベースのルーティング**: スキル出力スコアが >=80 HIGH_SIGNAL / >=50 CONTEXTUAL / >=25 WATCHLIST / <25 NOISE に分類され、閾値以下は改善ループに入る
- **4 層自己進化スタック**: Cognitive core（CLAUDE.md）→ Specialized agents → Path-scoped rules → Evolution engine（corrections.jsonl → learned-rules.md → 自動昇格）
- **改善速度の急加速警告**: Hyperagents が示す加速的改善カーブは reward tampering リスクを伴う。improve-policy に速度監視ルールが必要
- **多次元ルブリック評価**: 単一メトリクスは搾取される。複数次元（accuracy / clarity / actionability）で独立評価し、最弱次元を狙い撃ち改善する
- **LLM Judge > Binary Labels**: meta-agent (Anthropic 2026) で LLM judge による自然言語批評が binary supervision を上回った（holdout 87% vs 80%）。「なぜ失敗したか」の critique が proposer により豊かな最適化シグナルを提供する
- **Skill化が最大改善**: ビジネスルールをシステムプロンプトから skill に分離した変更が最大の holdout 改善（→80%）を達成。プロンプトへのルール埋め込みはオーバーヘッドが大きい
- **Anti-overfit prompt**: 「提案をルールとして述べよ。特定トレースでしか正当化できないなら狭すぎる」の指示が proposer の汎化性能を改善。search accuracy は上がるが holdout が下がる過学習を防止
- **認知基盤による初期加速**: ASI-Evolveは先行知識をembedding索引化して各ラウンドに注入。認知基盤除去でコールドスタートが遅延し不安定化するが、最終的には生産的探索に到達（外部知識なしでもコア機構は機能）。初期加速と長期自律性の両立を示す
- **構造化フィードバック蓄積**: 分析器が生ログ→意思決定レポートを蒸留。分析器除去で長期プラトー — 構造化分析は継続的進化に不可欠。AutoEvolveのmeta-analyzerに相当するが、per-experiment粒度での即時蒸留が鍵
- **GEPA > TextGrad（多様探索 > 貪欲探索）**: プロンプト最適化で遺伝的パレート最適化（多候補並行・パレートフロンティア淘汰）が貪欲テキスト勾配降下を +0.051 上回った。改善方向が不明確な場合、population-based 探索が有効
- **タスク固有評価信号の重要性**: 汎用オプティマイザ（ルーブリック+実行トレースなし）は専門的最適化に大幅劣後（0.583 vs 0.705）。評価はタスクカテゴリ別に基準を生成すべき

## 実践的な適用

dotfiles では AutoEvolve 4 層ループ（セッション→日次→BG→`/improve`）が自己改善の主幹機構として実装済みである。`session-learner.py` が playbook を `playbooks/{project}.md` に蓄積し、`autoevolve-core` が Phase 1（発見）→ Phase 2（検証・A/B）→ Phase 3（統合）を回す。`improve-policy.md` の 44 ルールがゲーティング条件を定義し、gaming-detector が Goodhart の法則（メトリクス操作）を検出する。meta-agent (Anthropic 2026) の知見から Rule 40-43 を追加: anti-overfit prompt technique、skill化優先ヒューリスティック、per-trace critique 方向性、holdout validation gate 方向性。Câmara+ 2026 の知見から Rule 44（タスクカテゴリ別ルーブリック評価）を追加し、`--evolve --pareto` モード（GEPA 的多候補パレート探索）と Phase 4 メタプロンプト自己改善を実装。`continuous-learning` スキルに trace-based rule extraction パスを接続済み。

## 関連概念

- [meta-evolution](meta-evolution.md) — 改善手続き自体の改善とメタ認知的修正
- [agent-evaluation](agent-evaluation.md) — エージェント出力の多次元評価フレームワーク
- [trajectory-learning](trajectory-learning.md) — 軌跡データからの知識蒸留と昇格ロジック

## ソース

- [AutoContext Recursive Improvement Analysis](../../research/2026-03-18-autocontext-recursive-improvement-analysis.md) — 6 役マルチエージェントパイプライン + Elo ベース進化ゲーティング。CTF での 2 世代 playbook 自動生成
- [Compounding Agent Analysis](../../research/2026-03-19-compounding-agent-analysis.md) — 4 層スタック（Skills/Orchestration/Scoring/Optimizer）とスキルコントラクトによる自己改善設計
- [Self-Evolving Claude Code Analysis](../../research/2026-03-30-self-evolving-claude-code-analysis.md) — verify: 行付きルール・core-invariants・corrections.jsonl による 4 層自己進化実装ガイド
- [Hyperagents Analysis](../../research/2026-03-26-hyperagents-analysis.md) — DGM-H による Task/Meta Agent 分離とメタレベル改善の 60〜80% ドメイン間転移
- [ASI-Evolve Analysis](../../research/2026-04-06-asi-evolve-analysis.md) — 認知基盤+専門分析器+UCB1サンプリングでAIスタック全体（アーキテクチャ・データ・アルゴリズム）の自律的改善を実証
- [meta-agent Continual Learning Analysis](../../research/2026-04-07-meta-agent-continual-learning-analysis.md) — LLM judge + proposer + holdout validation で unlabeled traces からハーネスを自動改善（tau-bench 67→87%）
