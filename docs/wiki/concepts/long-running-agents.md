---
title: 長時間自律エージェント
topics: [harness, agent]
sources: [2026-03-25-long-running-claude-scientific-computing-analysis.md, 2026-03-30-openforage-long-running-agents-analysis.md, 2026-03-25-harness-design-long-running-apps-analysis.md, 2026-04-06-agent-harness-anatomy-analysis.md, 2026-04-09-claude-managed-agents-analysis.md, 2026-04-17-claude-code-session-mgmt-analysis.md, 2026-04-21-harness-pipeline-absorb-analysis.md, 2026-04-29-symphony-clawsweeper-absorb-analysis.md, 2026-05-14-claude-code-routines-absorb-analysis.md, 2026-05-28-openclaw-autoreview-absorb-analysis.md, 2026-06-14-opik-self-repairing-harness-absorb-analysis.md, 2026-06-20-loop-engineering-essay-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 12
confidence: established
---

# 長時間自律エージェント

## 概要

長時間自律エージェントとは、数時間〜数日間にわたって人間介入なしに複雑なタスクを遂行するAIエージェントのパターンを指す。単一セッションを超えた作業継続を可能にするため、Living Documentation・失敗履歴・テストオラクル・Git連携の4本柱が基盤として機能する。長期タスクの失敗原因は「怠惰（corner-cutting）」と「混乱（stupidity）」の2種類に集約され、それぞれに構造的な対策が存在する。ハーネス設計の質がモデル選択より最終品質に大きく影響する。

## 主要な知見

- **CLAUDE.md as Living Documentation**: エージェントが作業中に自身の指示を編集・更新し、状態を維持する
- **CHANGELOG.md（ラボノート）**: 失敗アプローチと理由を記録し、セッション跨ぎのdead-end再試行を防止する
- **Ralph Loop**: 成功基準文字列（"DONE"）とmax-iterationsで「怠惰な停止」を検出・防止する制御構造
- **Generator-Evaluator分離**: 生成と評価を別エージェントに委譲し（GANインスパイア）、self-evaluation biasを軽減する
- **Context Reset vs Compaction**: モデルによりContext Anxiety感受性が異なり、長時間タスクでの戦略選択が品質に影響する
- **N個プラン生成 → 別エージェント選択**: 保守性・クリーンコード基準で別エージェントが最良プランを選択する
- **Pre-Task矛盾チェック**: 着手前に不完全・矛盾情報を体系的に検出し伝播を防止する
- **早期・頻繁な計画逸脱検証**: Lタスクで3ステップ完了ごとに計画突合を行い、カスケード障害（A→A'問題）を防ぐ
- **テストオラクル**: リファレンス実装との定量比較で進捗を測定し、明確な成功基準を設定する
- **blast radiusクリーンアップ**: セッション後にfresh contextエージェントで矛盾解消・デッドコード除去・ドキュメント同期を実施する
- **Brain/Hands/Session分離とマルチトリガーモデル**: ハーネス（脳）・ツール実行サンドボックス（手）・セッションログ（状態）を独立インタフェースに分け、Event-triggered/Scheduled/Fire-and-forget/Long-horizonの4パターンでトリガーを使い分けることで、単一障害点を排除しつつ長時間タスクに対応する [EXTRACTED, conf=75]
- **Hybrid Architecture（推論層と実行層の分離）**: クラウド管理エージェントを計画・推論層、ローカルの手作りハーネスを実行・検証層として併用することで、推論の堅実性とローカル検証の信頼性を両立させる [INFERRED, conf=65]
- **Context Rot閾値の実証値**: NIAH（単純検索）は1Mトークンまで性能維持するが、multi-hop推論は300-400kトークン付近で指数的に劣化する（NVIDIA RULER実証）。閾値を超えたらタスクの複雑度に応じてcompactかclearかを判断する目安になる [EXTRACTED, conf=80]
- **Every Turn Is a Branching Point**: 各ターンでContinue / Rewind / Clear / Compact（方向付き）/ Subagent委譲の5択を意識的に選ぶ規律。Rewindは今セッション内の汚染除去、Compact/Clearは次段階への引き継ぎという異なる粒度の修復手段である [EXTRACTED, conf=70]
- **Rewindの隠れコスト**: 直前ターンの訂正にRewindを使うとprompt cacheが全無効化され、副作用を伴う操作（ファイル書き込み等）の後に使うと実行済みの副作用と巻き戻ったコンテキストが乖離するリスクがある [EXTRACTED, conf=70]
- **Stateless Orchestrator（外部トラッカー＋ファイルシステムのみで状態復元）**: 永続DBを持たず、Issueトラッカーとファイルシステムからのみ状態を再構築することで、プロセスがどこで落ちても再開可能になる。長時間バッチをまたぐタスクキューイングの基盤パターン [EXTRACTED, conf=70]
- **Snapshot Hash + Drift Detection**: 適用前状態のハッシュを構造化エビデンスレコードに記録し、適用時に現在状態とズレていれば適用をスキップする。長時間の非同期実行で生じる「前提が古いまま適用してしまう」事故を防ぐ [EXTRACTED, conf=65]
- **Reproduce-First Attestation Gate**: 修正パッチを書く前に不具合を再現することを、助言ではなく強制ゲートとして扱う。長時間の自動修正ループほど「再現せず場当たり的に直す」コストが複利で効いてくる [EXTRACTED, conf=70]
- **Canonical Resume Anchor**: チェックポイント・再開状態を単一の正典的な置き場所に集約し、プランのSuccess Criteriaと直接リンクさせる。複数ファイルに分散すると、セッションをまたぐ間にsuccess_criteriaがドリフトする [INFERRED, conf=60]
- **Heartbeat耐性（長時間プロセスの生存判定）**: 長時間実行するレビュー/検証プロセスは、2-5分程度の無出力だけでkillしてはならない。wall-clockの沈黙ではなく明示的なheartbeat信号で生存を判定する [EXTRACTED, conf=65]
- **Bulletproof Prompt Rubric（無人実行エージェント向け6要素）**: role/task/process/output/error/constraintsの6要素でプロンプトを構造化する。スケジュール実行・無人実行のエージェントは途中で人間が軌道修正できないため、通常のプロンプトより厳密な構造が要る [EXTRACTED, conf=70]

## 実践的な適用

このリポジトリでは`completion-gate.py`がRalph Loopの役割を担い、`HANDOFF.md`テンプレートとセッション間の状態引き継ぎを実現している。`/autonomous`スキルが長時間タスクのオーケストレーションを担当し、`/checkpoint`でセッション状態を永続化する。`plan-lifecycle.py`と`golden-check.py`が計画逸脱の早期検知に使われ、`pre-compact-save.js`がコンテキスト圧縮時の状態保全を担う。`workflow-guide.md`にはLタスクの中間検証ポイントが明記されている。加えて`workflow-guide.md`のTurn Decision Tableが毎ターンのContinue/Rewind/Clear/Compact/Subagent選択を、`context-constitution.md`が300-400kトークンの閾値を明文化している。`references/managed-agents-hybrid.md`はクラウド管理エージェント（推論層）とローカルハーネス（実行層）の併用パターンを、`tools/codex-janitor`が外部トラッカー＋ファイルシステムのみで状態を復元するstateless orchestratorパターンを実装する。`references/routine-prompt-rubric.md`はスケジュール実行エージェント向けのBulletproof Prompt 6要素を定義する。

## 関連概念

- [harness-engineering](harness-engineering.md) — エージェントハーネスの設計原則と実装パターン
- [quality-gates](quality-gates.md) — 品質を保証するゲート機構の設計
- [context-management](context-management.md) — セッション跨ぎのコンテキスト管理戦略

## ソース

- [Long-Running Claude for Scientific Computing](../../research/2026-03-25-long-running-claude-scientific-computing-analysis.md) — CLAUDE.md・CHANGELOG・テストオラクル・Git・Ralph Loopの4本柱を科学計算事例で実証
- [OpenForage: Long-Running Autonomous Agents](../../research/2026-03-30-openforage-long-running-agents-analysis.md) — 7つの失敗パターンと3つの構造的対策、独立オーケストレーション層の必要性
- [Harness Design for Long-Running Apps](../../research/2026-03-25-harness-design-long-running-apps-analysis.md) — Generator-Evaluator分離・コンテキスト管理・主観的品質評価の12手法を3ケーススタディで実証
- [Agent Harness Anatomy Analysis](../../research/2026-04-06-agent-harness-anatomy-analysis.md) — harness simplification audit と12コンポーネント体系化。長時間タスクのハーネス設計を構造化する7アーキテクチャ決定
- [Claude Managed Agents 分析](../../research/2026-04-09-claude-managed-agents-analysis.md) — Brain/Hands/Session分離とマルチトリガーモデルによる長時間タスクのインフラ層解決、Hybrid Architecture採用
- [Claude Code Session Management & 1M Context 分析](../../research/2026-04-17-claude-code-session-mgmt-analysis.md) — Context Rot 300-400k閾値・Rewind/Compact/Clear/Subagentの5択規律を6手法全採用
- [Harness Pipeline (GitHub BAN体験記) 分析](../../research/2026-04-21-harness-pipeline-absorb-analysis.md) — reproduce-first attestation・resume anchor・load-bearing gateなど7件を部分採用
- [OpenAI Symphony/ClawSweeper Orchestration 分析](../../research/2026-04-29-symphony-clawsweeper-absorb-analysis.md) — stateless orchestrator・snapshot hash drift detection・keep-open biasを部分採用
- [Claude Code Routines 分析](../../research/2026-05-14-claude-code-routines-absorb-analysis.md) — Bulletproof Prompt 6要素rubricとRoutine Recipe Catalogを新規採用
- [OpenClaw autoreview SKILL.md 分析](../../research/2026-05-28-openclaw-autoreview-absorb-analysis.md) — PASS-exit lock・twin-rerun・30分SLA+heartbeat耐性など5件を採用、4件保留
- [Opik Self-Repairing Harness 分析](../../research/2026-06-14-opik-self-repairing-harness-absorb-analysis.md) — loop engineering・self-repair概念は全rehash（採用0）、検証で`/improve`退役済みorphanコードを発見・退役
- [Loop Engineering Essay 分析](../../research/2026-06-20-loop-engineering-essay-absorb-analysis.md) — loop engineering essayは全rehash（採用0）、副次的にstale planのkept判定を記録
