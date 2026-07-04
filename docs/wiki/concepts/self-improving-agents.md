---
title: 自己改善エージェント
topics: [agent, ml-rl]
sources: [2026-03-18-autocontext-recursive-improvement-analysis.md, 2026-03-19-compounding-agent-analysis.md, 2026-03-30-self-evolving-claude-code-analysis.md, 2026-03-26-hyperagents-analysis.md, 2026-04-06-asi-evolve-analysis.md, 2026-04-07-meta-agent-continual-learning-analysis.md, 2026-04-07-self-optimizing-dr-agents-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 35
confidence: established
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
- **DB の本質は保存でなく lineage**: 動機追跡DBは候補の記録だけでは不十分で、`parent_id` / `novelty_score` / `mutation_type` による系譜追跡があって初めて閉ループの基盤になる（ASI-Evolve を AutoEvolve に統合した際の Codex 批評）
- **Heartbeat 介入**: 停滞検知を反応的（閾値超過後）にとどめず、Reflect（毎評価）/ Consolidate（10回毎）/ Pivot（5回非改善）の定期介入を挟むと知識蓄積が進む。知識アーティファクトを除去すると性能が 18.6% 低下し、他エージェントの成果を再利用した試行は 36% にのぼる（CORAL）
- **「存在チェック」ではなく「機能チェック」**: 汎用ハーネスの構成要素は名目上揃っていても機能しているとは限らない。自己改善ループの評価は "実装済みか" ではなく "実際に効果を出しているか" で行うべき（The Great Convergence）
- **Grade outcome, not trajectory**: 経路（使ったツール数・retry 回数）を罰さず最終成果のみで評価する。スコアがあっても是正チケットに繋がらなければ意味がない — evaluator と engineering pipeline は一体で機能させる（Self-Healing Harness）
- **objective-lane / judgement-lane の入口分類**: 「正解キーで照合可能なタスク」と「判断タスク」を区別せずに自動最適化を適用すると false-positive を量産する。過去の `/improve` 全自動マージが retire した根本原因はここにあった（SkillOpt 分析）
- **learned は本質的に advisory**: 蓄積された学習ストアは経験からの判断材料であり、機械照合可能な mechanical な知見を原理的に含まない。全 139 件を分類しても mechanical は 0 件で、無人 PR 化ループは「燃料」が構造的に存在しなかった（sonicgarden 実装）
- **検証状態ラベルで数値と概念を分離**: 外部記事のベンチマーク数値が未検証（UNVERIFIED）でも、その背後にある構造（例: verified/hypothesis の区別）自体は採用できる。「不採用」と「未検証」を混同しない（Fable 5 14 steps 分析）
- **実行の自己改善と判断の計測は非対称**: dotfiles は「実行」の自己改善（AutoEvolve/tech-researcher）には重投資済みだが、「AI の方針判断が人間に追いついているかの計測」と「安全機構自体を進化ループが緩慢に侵食しないためのメタ安全層」は手薄なまま残っている（Anthropic recursive self-improvement 分析）

## 実践的な適用

dotfiles では AutoEvolve 4 層ループ（セッション→日次→BG→`/improve`）が自己改善の主幹機構として実装済みである。`session-learner.py` が playbook を `playbooks/{project}.md` に蓄積し、`autoevolve-core` が Phase 1（発見）→ Phase 2（検証・A/B）→ Phase 3（統合）を回す。`improve-policy.md` の 44 ルールがゲーティング条件を定義し、gaming-detector が Goodhart の法則（メトリクス操作）を検出する。meta-agent (Anthropic 2026) の知見から Rule 40-43 を追加: anti-overfit prompt technique、skill化優先ヒューリスティック、per-trace critique 方向性、holdout validation gate 方向性。Câmara+ 2026 の知見から Rule 44（タスクカテゴリ別ルーブリック評価）を追加し、`--evolve --pareto` モード（GEPA 的多候補パレート探索）と Phase 4 メタプロンプト自己改善を実装。`continuous-learning` スキルに trace-based rule extraction パスを接続済み。全自動マージ型の `/improve` は false-positive 多発で 2026-05-03 に退役済みで、その後継として「客観照合可能な objective-lane」と「判断が要る judgement-lane」を分離する eligibility classifier（`references/optimizer-eligibility.md`）と、held-out strict accept gate（tie は reject）が設計されている。`memory-schema.md` には `verification_status`（verified/hypothesis/stale/retracted）ラベルを追加し、`model-routing.md` には Haiku を非権威 cheap prefilter に限定する Model Safety Boundary を明記した。公開リポジトリへの credential leak を防ぐ `publicity-review` gate（`scripts/security/publicity-scan.py`）も pre-commit に組み込み済み。

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
- [ASI-Evolve: AI Accelerates AI](../../research/2026-04-08-asi-evolve-autoevolve-integration-analysis.md) — AI自己進化ループを分析、Analyzer/DB連携など5項目を段階採用
- [CORAL: Towards Autonomous Multi-Agent Evolution](../../research/2026-04-08-coral-autonomous-multi-agent-evolution-analysis.md) — 自律マルチエージェント進化を分析、heartbeat機構を優先採用
- [Environment-Driven Reinforcement Learning](../../research/2026-04-08-environment-driven-rl-analysis.md) — 環境駆動RL記事を分析、RL基盤をAutoEvolveへ接続採用
- [The Great Convergence](../../research/2026-04-09-great-convergence-analysis.md) — 汎用ハーネス収束論を分析、存在≠機能の検証課題を抽出
- [Skill Evaluation & Self-Improving Loop](../../research/2026-04-09-skill-eval-self-improving-loop-analysis.md) — スキル評価改善ループを分析、per-skillスコアリング修正等採用
- [pepabo「Claude Code 失敗学習ループ」吸収分析](../../research/2026-04-11-pepabo-failure-learning-loop-analysis.md) — pepabo記事、3層メモリの認知負荷是正とpruning優先方針を部分採用
- [Hermesパーソナルアナリスト活用体験記](../../research/2026-04-14-hermes-personal-analyst-analysis.md) — Hermesアナリスト記事分析、大半既存資産で充足、情報源拡張のみ追加
- [Autogenesis: A Self-Evolving Agent Protocol](../../research/2026-04-19-autogenesis-absorb-analysis.md) — 自己進化エージェント論文を分析、一部の強化案のみ採用し統一リソース層は棄却
- [The Self-Healing Agent Harness absorb分析](../../research/2026-04-29-self-healing-harness-absorb-analysis.md) — 自己修復ハーネス記事を分析、outcome-over-trajectory等3件採用
- [Claude Code Routines性能チューニング absorb分析](../../research/2026-04-29-yamadashy-routines-perf-tuning-absorb-analysis.md) — Routines性能チューニング記事を分析、AutoEvolveへ6タスク採用
- [育てるClaude Codeから勝手に育つClaude Codeへ](../../research/2026-05-13-grown-claude-code-metabolism-absorb-analysis.md) — skill代謝記事からGotchas欄と週次friction digestを採用
- [73% of my CLAUDE.md was lying to Claude — Dreaming local replica](../../research/2026-05-16-dreaming-local-replica-absorb-analysis.md) — Dreaming再現記事はAPI捏造と判明、既存Pruning-First優位確認
- [How To Fix AI Slop (Using Hermes)](../../research/2026-05-31-hermes-ai-slop-eval-loop-absorb-analysis.md) — Hermesのeval loop提案を分析、既存基盤が上回り自動closeループ不採用
- [How To Fix AI Slop (Using Hermes) — full-workflow 再分析](../../research/2026-05-31-hermes-eval-loop-absorb-analysis.md) — 同種Hermes eval loop記事を再分析、全Already/意図的retireで採用0
- [6 Workflows, 6 Lessons, 60 Days with Hermes Analyst](../../research/2026-06-02-hermes-60-days-6-lessons-absorb-analysis.md) — Hermes運用60日記事を分析、echo chamber対策を昇格ループ設計ノートに追記採用
- [Microsoft SkillOpt: 自己進化スキル](../../research/2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md) — SkillOptのテキスト最適化手法を分析、objective-lane gate等4件採用
- [生成AIトレンド自己進化型情報収集](../../research/2026-06-04-ai-tech-researcher-self-evolving-absorb-analysis.md) — AI技術情報収集の自己進化記事を分析、read-only MVPとdrift監視のみ採用
- [MUSE-Autoskill: Self-Evolving Agents via Skill Lifecycle](../../research/2026-06-05-muse-autoskill-self-evolving-agents-absorb-analysis.md) — MUSE論文のスキル生涯管理を分析、per-skill memoryなど新規性ゼロ採用0件
- [When AI builds itself (Anthropic Institute)](../../research/2026-06-05-recursive-self-improvement-anthropic-absorb-analysis.md) — Anthropic再帰的自己改善論考を分析、判断計測とメタ安全層3件を採用予定
- [Claude Codeで自己改善ループを作った話 (sonicgarden)](../../research/2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md) — sonicgarden自己改善ループ記事を分析、publicity-reviewゲート等を採用実装
- [Build self-improving agent system with Fable 5 in 14 steps](../../research/2026-06-12-fable5-14steps-absorb-analysis.md) — Fable5自己改善14ステップから検証状態ラベルとモデル安全境界を採用
- [Opik Self-Repairing Harness + Karpathy Loop Engineering](../../research/2026-06-14-opik-self-repairing-harness-absorb-analysis.md) — Opik記事は全rehash、検証で/improve退役済みorphanコードを発見し退役
- [Hermes VPS 24/7 OS Complete Guide](../../research/2026-06-17-hermes-vps-24-7-os-absorb-analysis.md) — Hermes VPS OS運用ガイドは全10手法rehash、採用0確定
- [How to Create Loops with Claude](../../research/2026-06-17-loops-with-claude-absorb-analysis.md) — loop engineering記事は既absorb済み一次資料の二次紹介、採用0
- [The Self-Improving Loop: 300-agent swarm on Kimi K2.6](../../research/2026-06-18-kimi-k26-self-improving-swarm-loop-absorb-analysis.md) — Kimi swarm記事はほぼrehash、Cost-Arbitrageのみbest-of-nガイドに採用
- [How to Make Claude's Prompt Update Itself After Every 100 User Decisions](../../research/2026-06-20-anthropic-100-decisions-self-updating-prompt-absorb-analysis.md) — プロンプト自己更新記事は全rehash、月次calibrationも見送り採用0
- [Loop Engineering 二重ソース](../../research/2026-06-20-loop-engineering-double-source-absorb-analysis.md) — loop engineering二重ソース記事は19手法全rehash、採用0
- [Loop Engineering essay](../../research/2026-06-20-loop-engineering-essay-absorb-analysis.md) — loop engineering essayは全rehash、副次的にstale plan1件kept判定
- [Automating SKILL.md Generation via Interaction Trajectory Mining](../../research/2026-06-20-skillmd-trajectory-mining-absorb-analysis.md) — trajectory mining論文は転移失敗を自報、YAGNI判断を学術的に裏付け
