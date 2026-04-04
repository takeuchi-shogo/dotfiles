---
source: https://zenn.dev/aicon_kato/articles/harness-engineering-startup
date: 2026-04-04
status: integrated
---

# Harness Engineering Startup 分析レポート

> 「ハーネスエンジニアリングを極めたら、IssueからAIエージェントが動き、人間の役割は要件定義だけになった」
> 著者: 加藤（株式会社Aicon PM）, 2026-04-01

## Source Summary

### 主張

1. 開発プロセスの極度な細分化（要求→要件→設計→詳細設計→実装→マージ）でAIエージェントが各段階を確実に実行
2. GitHub中心の運用モデル: ローカル開発への依存を排除し、全作業をGitHub上で完結
3. ラベル駆動のバトンリレーシステム: 21体のエージェントがラベル付与で連鎖起動
4. コンテキスト供給がエンジニアリングの本質: コードを書く → 環境を設計する への転換
5. 初期投資（2週間の機能停止）が後の加速度を決定: 80件/半月 → 681件/半月

### 手法

- **ラベル駆動エージェント**: GitHub Actions + Claude API。ラベル付与 → workflow発火 → タスク実行 → 次ラベル自動付与
- **21体のエージェント**: 要件定義、詳細設計、タスク分割、自動実装、レビュー、CI修正、コンフリクト解消、停滞監視等
- **PR分割計画**: 詳細設計の出力に含め、実装フェーズの並列化を可能にする
- **6観点品質スコアリング**: アーキテクチャ/コード品質/テスト/セキュリティ/パフォーマンス/運用性
- **ワークフロー健全性スコア**: `priority = complexity × (100 - stability) / 100`
- **Golden Principles**: `.mdc` 形式のアーキテクチャルール
- **プレビュー環境**: Terraform でPR単位に自動構築・破棄

### 根拠

- マージPR数: 80件 → 681件/半月（8.5倍）, 57万行モノレポ
- OpenAI記事引用: 100万行・1,500PR を3人5ヶ月で達成
- Martin Fowler整理: Context Engineering + Architectural Constraints + Garbage Collection

### 前提条件

- GitHub Actions + Claude API が利用可能なモノレポ
- 意思決定が少人数で完結する組織
- 初期2週間の機能開発停止を許容できる経営判断

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | ラベル駆動バトンリレー（21体） | N/A | dotfiles はローカルハーネス。テンプレートは setup-background-agents に既存 |
| 2 | プレビュー環境自動構築（Terraform） | N/A | dotfiles には不要 |
| 3 | ワークフロー健全性スコアリング | Partial | scoring-audit.yml はLLM定性のみ。定量アルゴリズム未実装 |
| 4 | PR分割計画を設計に組み込む | Gap | /spec に PR 分割セクションなし |

### Already 項目の強化分析

| # | 既存の仕組み | 強化判定 |
|---|-------------|---------|
| A | Golden Principles + golden-check.py | 強化不要 — 言語横断的で記事より成熟 |
| B | migration-guard エージェント | 強化不要 — API/依存変更も含むより広いスコープ |
| C | AutoEvolve 4層ループ | 強化不要 — 記事は「未成熟」と自認 |
| D | EPD ワークフロー | 強化可能 — PR分割計画をSpecに追加 |
| E | Progressive Disclosure ドキュメント | 強化不要 |
| F | pipeline-health.yml テンプレート | 強化可能 — ブロッカー依存解消パターン追加 |

## Integration Decisions

全3件を統合:
1. **spec skill に PR Split Plan セクション追加** — L規模タスクの並列実装を構造化
2. **scoring-audit に定量メトリクス収集ステップ追加** — complexity/stability/priority の数式ベーススコアリング
3. **pipeline-health にブロッカー解消リレー追加** — unblock-relay ジョブで依存解消時の自動通知

## Plan

### Task 1: spec skill 強化 (S)
- `skills/spec/skill.md` の Output Format に「PR Split Plan（L規模で必須）」セクション追加
- PR一覧、依存グラフ、マージ順序、並列実行可能PRの明示

### Task 2: scoring-audit 定量化 (S)
- `templates/scoring-audit.yml` に `Collect quantitative metrics` ステップ追加
- LOC/分岐数/外部API呼び出しから complexity、CI成功率から stability、掛け算で priority を算出
- 既存のLLM 6観点評価の前段に配置

### Task 3: pipeline-health 強化 (S)
- `templates/pipeline-health.yml` に `unblock-relay` ジョブ追加
- 直近4h以内にクローズされた Issue のブロッカー解消を検出し、依存先に自動通知
