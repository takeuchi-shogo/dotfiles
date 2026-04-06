---
source: "https://mtx2s.hatenablog.com/entry/2026/04/06/061511"
date: 2026-04-07
status: analyzed
---

# 分析レポート: SDLC品質分散 — コードレビュー依存からの脱却

## メタデータ
- ソース: https://mtx2s.hatenablog.com/entry/2026/04/06/061511
- 著者: mtx2s
- 分析日: 2026-04-07
- 判定: Gap 0, Partial 3, Already 17 (うち強化可能 4), N/A 6

## 記事の主張
AIコーディングエージェントの普及でコードレビューがボトルネック化。コードレビューの機能（変更容易性・品質保証・緊急対応・説明責任）をSDLC 4層（生成→レビュー→パイプライン→本番）に分散して再設計すべき。

## 手法一覧（25項目を4層に構造化）

### 層1: 生成段階で品質を作る（自工程完結）
1. コンテキスト強化（AST解析, MCP統合）
2. 規範の機械可読化（コーディング規約, 設計ガイドライン明文化）
3. 生成粒度の最適化（INVEST, Stacked PRs）
4. ペアプロ・モブプロ活用（複数エージェント協働）
5. 要求の構造化（Spec-first, PLANモード）
6. 検証条件の構造化（EARS, Gherkin, BDD）
7. テスト駆動修正ループ（TDD, テスト自動生成）
8. 生成直後の自己検証（マルチロールAI, 検証観点分離）

### 層2: レビュー工程で品質を補強する
9. リスクベースのレビュー切り分け（ティア分類）
10. 専門領域別のレビュー分離
11. 多視点検証（マルチモデル評価）
12. 反復型レビュー
13. 指摘トリアージ（信頼度スコア, 重大度フィルタ）
14. 修正までの完全自動化

### 層3: パイプラインで品質を保証する
15. 静的解析
16. 自動テスト（振る舞い）
17. 自動テスト（構造）— ArchUnit相当
18. 依存関係・ライセンス検証
19. 非機能要件検証

### 層4: 本番で品質を回復する
20. 事後学習サイクル
21-25. デプロイ・運用系（カナリア, 可観測性, ロールバック, 多層防御等）

## ギャップ分析結果

### 前提のフレーミング
記事は「チーム開発で人間レビューアーがボトルネック」を前提。本ハーネスはソロ+AI構成でその課題を既にバイパスしている。記事の手法の半分は人間レビューアーのスケーラビリティ問題への解であり、本ハーネスには直接は当てはまらない。ただし「品質を構造で担保する」という設計思想は共通。

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 3 | 生成粒度の最適化 | Partial | PR Split Plan・3ファイル制限あり。INVEST的Story分解ガイド未定義 |
| 6 | 検証条件の構造化（Gherkin） | N/A | 実行基盤なし。acceptance_criteria必須で十分 |
| 14 | 修正までの完全自動化 | Partial | NEEDS_FIXは自動修正。BLOCK時のユーザー判断は安全弁 |
| 17 | 自動テスト（構造） | Partial | edge-case-hunterにハーネス構造チェックあり。対象限定的 |
| 21-25 | デプロイ・運用系 | N/A | dotfiles/ハーネス文脈でスコープ外 |

### Already（強化可能）

| # | 既存の仕組み | 強化案 |
|---|-------------|--------|
| 7 | completion-gate + tdd-guard | テスト失敗パターン別修正ヒューリスティクス追加 |
| 11 | review並列起動 + debate skill | 高リスク変更時にdebate的多モデル検証をreviewに自動統合 |
| 15 | PostToolUse lint + golden-check.py | GP-006〜008用AST軽量チェッカー新設 |
| 18 | security-reviewer（npm audit/govulncheck） | OSSライセンスチェック追加 |

### Already（強化不要）— 12項目
#1(MCP統合), #2(golden-principles/lessons-learned/review-checklists), #4(agent_delegation/debate), #5(spec/epd/interview), #8(codex-reviewer/Adversarial Gate), #9(Scaling Decision/Fβ), #10(10種以上専門エージェント), #12(最大3回再レビューループ), #13(confidence+5段階ラベル), #16(completion-gate Stop), #19(4層セキュリティフック), #20(AutoEvolve自動閉ループ)

## セカンドオピニオン

### Codex 批評
- #6 Gherkin → N/A（実行基盤なし）
- #11 多視点検証 → 強化可能（debate が review に未統合）
- #15 静的解析 → 強化可能（GP-006〜008 自動検出困難）
- 前提のズレ: チーム開発 vs ソロ+AI
- 優先度: #14 → #15 の順。#3, #17 は見送り推奨

### Gemini 補完
- AI レビュー偽陰性率 8-15%（セキュリティ・並行処理で特に弱い）
- false positive 率 18-22%（vs 人間 5-8%）
- 次世代手法: Outcome-Based Review Minimization, In-Editor Real-Time Feedback
- 適用範囲: スタートアップ=高、規制産業=低

## 統合プラン

### 選択結果
全6件を取り込み。

### タスクリスト

| # | タスク | 対象ファイル | 規模 | 優先度 |
|---|--------|------------|------|--------|
| T1 | completion-gate にテスト失敗パターン分類+修正ヒューリスティクス追加 (#14+#7) | scripts/policy/completion-gate.py | M | 1 |
| T2 | GP-006〜008用AST軽量構造チェッカー新設 (#15) | scripts/policy/structure-check.py（新規）+ settings.json | M | 2 |
| T3 | review SKILL.md に高リスク変更時の多モデル検証自動組み込み (#11) | skills/review/SKILL.md | S | 3 |
| T4 | INVESTベースのタスク分解ガイドライン追加 (#3) | references/task-decomposition-guide.md（新規） | S | 4 |
| T5 | security-reviewer にライセンスチェック手順追加 (#18) | agents/security-reviewer.md | S | 5 |

全体規模: M（5タスク、6-7ファイル、すべて並列実行可能）

## 根拠と前提条件
- 記事は成熟した CI/CD + 可観測性基盤を前提とする Web サービス開発チームを想定
- 本ハーネスはソロ+AI のエージェント設定リポジトリであり、適用文脈が異なる
- 「品質を構造で担保する」という設計思想は共通であり、層1・層2の手法に高い親和性がある
