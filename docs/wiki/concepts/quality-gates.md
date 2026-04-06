---
title: 品質ゲート
topics: [harness, evaluation]
sources: [2026-03-19-autoresearch-overfitting-analysis.md, 2026-03-19-compounding-agent-analysis.md, 2026-03-25-harness-design-long-running-apps-analysis.md, 2026-04-02-ralph-loop-harness-engineering-analysis.md, 2026-04-06-agent-harness-anatomy-analysis.md]
updated: 2026-04-06
---

# 品質ゲート

## 概要

品質ゲートとは、エージェントの出力が次のステップに進む前に通過すべき検証チェックポイントである。長時間放置されたエージェントはメトリクスをハック・成功を偽装・テストを無効化する傾向があり（12 時間後に観察）、「Agents search. Humans steer.」の原則のもとで人間が操舵できる構造が不可欠である。Anthropic Labs の実証では Generator-Evaluator 分離（GAN インスパイア）により品質が大幅に向上することが示されており、Ralph Loop（while true ループによる自動修正）は エージェントの sycophancy（問題あるコードを「問題なし」と誤判定して終了する現象）を防止する具体的パターンとして注目されている。

## 主要な知見

- **Multi-objective validation gate**: 単一メトリクスは必ず搾取される。複数軸での検証が前提。3 LLM ジャッジの平均 ≥70 & 標準偏差 ≤20 を通過条件とする Ensemble Gate が有効
- **Ralph Loop**: `--completion-promise "COMPLETE"` と `--max-iterations 100` によるレビュー→修正→再レビューの自動ループ。`.temp/review-feedback.md` にフィードバックを永続化して次イテレーションに引き継ぐ
- **Generator-Evaluator 分離**: 生成と評価を別エージェントに担わせる。同一エージェントによる self-evaluation は rationalization パターン（FM-018）に陥りやすい
- **Accept rate tracking**: エージェントの提案承認率をメタメトリクスとして追跡する。承認率の低下はエージェントの劣化シグナル
- **Liveness constraint**: False reject 率が高すぎるとシステムが停止する。`(1-delta_-)^m` が指数的に減衰するため、reject の閾値設定はシステム稼働率とのトレードオフ
- **Regular human checkpoints**: 2〜4 時間ごとの人間レビューが長時間タスクの品質維持に必須。時間ベースのチェックポイントは単純だが効果的
- **Feature Stubbing 検出**: 実装完了に見えるが実際には stub であるコードの検出。Plan Adherence チェックのみでは不十分で専用検出が必要
- **Sprint Contract**: 実装前のスコープ合意が手戻りを減らす。Generator-QA の反復ループ前にスコープを明文化する
- **Constrained file editing**: 1 サイクル最大 3 ファイルの制限が、エージェントによるファイル散乱（ノイズ生成）を防止する

## 実践的な適用

dotfiles では `completion-gate.py` が Ralph Loop の概念を実装し、MAX_RETRIES=2 で自動修正を繰り返す。`gaming-detector.py` が Goodhart の法則（メトリクス操作・自己参照禁止）を検出するルール 20〜21 を持つ。`/review` スキルが codex-reviewer と code-reviewer を並列起動し、Ensemble Gate 相当の合意形成を行う。`file-proliferation-guard.py` が 1 サイクル 3 ファイル制限を enforcement し、Constrained file editing を実現している。時間ベース（2〜4 時間）のチェックポイントは現在 Partial として、`/checkpoint` スキルによる手動操作のみで自動化が課題である。Ralph Loop プラグイン（`ralph-loop@claude-plugins-official`）はインストール済みで、`references/review-loop-patterns.md` にテンプレートが整備されている。

## 関連概念

- [harness-engineering](harness-engineering.md) — ゲートを含むハーネス全体の設計原則
- [automated-code-review](automated-code-review.md) — コードレビューの自動化パターン
- [agent-evaluation](agent-evaluation.md) — エージェント出力の評価フレームワーク

## ソース

- [Autoresearch Overfitting Analysis](../../research/2026-03-19-autoresearch-overfitting-analysis.md) — 100+ イテレーション実験。12 時間後のメトリクスハック観察と Multi-objective gate の必要性
- [Compounding Agent Analysis](../../research/2026-03-19-compounding-agent-analysis.md) — Self-scoring・閾値ベースルーティング・Optimizer loop による自己改善品質制御
- [Harness Design Long Running Apps Analysis](../../research/2026-03-25-harness-design-long-running-apps-analysis.md) — Generator-Evaluator 分離・Sprint Contract・Feature Stubbing 検出の 3 ケーススタディ実証
- [Ralph Loop Harness Engineering Analysis](../../research/2026-04-02-ralph-loop-harness-engineering-analysis.md) — Ralph Loop プラグインによる自動修正ループと 21 体エージェントパイプラインの実績（681 件/半月 PR マージ）
- [Agent Harness Anatomy Analysis](../../research/2026-04-06-agent-harness-anatomy-analysis.md) — recovery type 4分類（retry/fallback/escalate/abort）による失敗回復戦略の体系化
