---
source: |
  - https://zenn.dev/explaza/articles/100d753df57fa7 (_mkazutaka, エクスプラザ)
  - https://zenn.dev/aicon_kato/articles/harness-engineering-startup (加藤, Aicon)
date: 2026-04-02
status: integrated
---

## Source Summary

### 記事1: Ralph Loop からはじめるハーネスエンジニアリング

**主張**: AIエージェントを while true ループで反復実行し、レビューア Agent が品質基準を満たすまで自動修正させるパターン（Ralph Loop）が、エージェントの早期終了・誤判定問題を解決する。

**手法**:
- `ralph-loop@claude-plugins-official` プラグインによるループ実行
- Agent + Command の組み合わせでレビュー→修正→再レビューの自動ループ
- `--completion-promise "COMPLETE"` による完了条件制御
- `--max-iterations 100` による上限制御
- `.temp/review-feedback.md` にフィードバックを永続化して次イテレーションに引き継ぎ

**根拠**: エージェントが問題のあるコードを「問題なし」と誤判定して終了する問題（Sycophancy / false completion）を防止。

**前提条件**: Claude Code プラグイン環境、レビュー基準の明文化。

### 記事2: Issue から AI が動き、人間の役割は要件定義だけになった

**主張**: 開発プロセスを細粒度に分解し、ラベル駆動で Agent 間バトンリレーを構成すれば、Issue→マージ準備完了 PR まで完全自動化できる。

**手法**:
- 21体のエージェントによる完全自動パイプライン（要件定義→設計→実装→レビュー→マージ）
- GitHub Actions + ラベル駆動の Agent 間バトンリレー
- 要件定義壁打ち Agent（AI が質問→人間が回答で要件を詰める）
- 定期スコアリング（6観点: アーキテクチャ/コード品質/テスト/セキュリティ/パフォーマンス/運用性）& 自動リファクタ Issue 化
- DB スキーマ破壊的変更チェック（DROP COLUMN 自動検出）
- パイプライン停滞監視 & 自動回復
- PR 変更の影響分析、マージコンフリクト自動解消

**根拠**: 681件/半月の PR マージ実績。2ヶ月間の専念で構築。57万行モノレポ。

**前提条件**: GitHub Actions 基盤、モノレポ構成、Claude API 利用、専任ハーネスエンジニアの投資。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | ralph-loop プラグイン | Partial→統合済 | completion-gate.py に概念はあったがプラグイン未インストール → インストール完了 |
| 2 | Agent + Command レビューループ | Partial→統合済 | パターンを references/review-loop-patterns.md にテンプレート化 |
| 3 | ラベル駆動バトンリレー | N/A | dotfiles リポジトリには不要。テンプレートとして提供 |
| 4 | 21体 Agent パイプライン | N/A | プロダクト向け。テンプレートカタログとして参考化 |
| 5 | 定期スコアリング & Issue 化 | Gap→統合済 | setup-background-agents/templates/scoring-audit.yml 新設 |
| 6 | 停滞監視 & 自動回復 | N/A | 概念は既存。テンプレートとして提供 |
| 7 | DB 破壊的変更チェック | N/A | dotfiles に DB なし。migration-guard Agent が存在 |
| 8 | コンフリクト自動解消 | N/A | 単一開発者。テンプレートとして提供 |

### Already 項目の強化分析

| # | 既存の仕組み | 強化判定 |
|---|-------------|---------|
| A1 | completion-gate.py Ralph Loop | 強化不要 — env 変数方式で十分 |
| A2 | /interviewing-issues | 強化不要 — 同等機能 |
| A3 | cross-file-reviewer + code-review-graph | 強化不要 — blast radius 算出済み |
| A4 | /dev-cycle | 強化済 — ラベル駆動パターンを参考情報として追加 |
| A5 | setup-background-agents テンプレート | 強化済 — 3テンプレート追加（scoring-audit, design-pipeline, pipeline-health） |

## Integration Decisions

全5項目を取り込み:
1. ralph-loop プラグインインストール
2. references/review-loop-patterns.md 新設（レビューループ + 定期スコアリング + バトンリレーパターン）
3. setup-background-agents テンプレート3種追加（scoring-audit, design-pipeline, pipeline-health）
4. 分析レポート保存 + MEMORY.md 更新

## 統合成果物

| ファイル | 変更種別 |
|---------|---------|
| ralph-loop プラグイン | インストール |
| `references/review-loop-patterns.md` | 新設 |
| `setup-background-agents/templates/scoring-audit.yml` | 新設 |
| `setup-background-agents/templates/design-pipeline.yml` | 新設 |
| `setup-background-agents/templates/pipeline-health.yml` | 新設 |
