# 12 Claude Patterns 分析レポート

**ソース**: "12 things Claude can do for you that you've never tried" (@sharbel)
**分析日**: 2026-04-09
**カテゴリ**: プロンプトパターン / ユーザーインタラクション設計

## 記事概要

Claude を Q&A ツールではなくプロセス設計ツールとして使うべきという主張。12の高度な使い方を紹介。ターゲットは Claude.ai の一般ユーザー（$20/月サブスクリプション）。

### 主張

ほとんどのユーザーは Claude の能力の10%しか使っていない。反論生成、インタビュー駆動、ペルソナシミュレーション、メタプロセス構築などの手法で、ツールの潜在力を引き出せる。

### 12の手法

| # | 手法 | カテゴリ | 概要 |
|---|------|---------|------|
| 1 | 反論生成 (Steelmanning) | 思考支援 | 自分の判断に対する最強の反論を生成 |
| 2 | インタビュー駆動の出力 | 入力品質 | 先に質問してから出力。テンプレ回避 |
| 3 | ペルソナシミュレーション | 評価 | 特定読者の視点で成果物を評価 |
| 4 | ボイスマッチング | パーソナライゼーション | 文体学習・再現 |
| 5 | 意思決定フレームワーク構築 | 思考支援 | 構造化判断マトリクス生成 |
| 6 | 大量文書の圧縮 | 情報処理 | 長文書をアクショナブルブリーフに |
| 7 | レッドチーム | 検証 | 戦略の破綻シナリオ生成 |
| 8 | コードなしデータ分析 | データ | CSV/スプレッドシート自動分析 |
| 9 | Running Brief | 永続化 | セッション横断の生きたドキュメント |
| 10 | 会話ロールプレイ | 練習 | 難しい会話のシミュレーション |
| 11 | コンテキスト別リライト | 変換 | 1コンテンツ→多フォーマット |
| 12 | メタプロセス構築 | メタ | 答えではなくプロセスを構築 |

## ギャップ分析結果

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 | 既存ファイル |
|---|------|------|------|-------------|
| 3 | ペルソナシミュレーション | **Partial** | debate-personas(5ペルソナ)はあるが任意ステークホルダー視点の評価は未実装 | `skills/analyze-tacit-knowledge/references/debate-personas.md` |
| 4 | ボイスマッチング | **Partial** | persona + tone 学習が部分的に存在。永続的文体学習は未実装 | `skills/persona/SKILL.md` |
| 5 | 意思決定フレームワーク | **Partial** | /debate に重み付き比較あり。スコアリングルーブリック + 隠れた問い生成は未実装 | `skills/debate/SKILL.md`, `skills/grill-interview/SKILL.md` |
| 8 | コードなしデータ分析 | **N/A** | dotfiles ハーネスには不要。JSONL 集計基盤はあるが用途が異なる | — |
| 10 | 会話ロールプレイ | **Partial** | /think + /interview + debate-personas で近似可能 | `skills/think/SKILL.md` |
| 11 | コンテキスト別リライト | **Gap** | マルチフォーマット変換なし | — |

### Already 項目

| # | 手法 | 判定 | 既存の仕組み |
|---|------|------|-------------|
| 1 | 反論生成 | Already (強化不要) | `/think` Step 4 + `/challenge` + `/debate` adversarial |
| 2 | インタビュー駆動 | Already (強化不要) | `/interview` + `/spec` Deep Interview + `/grill-interview` |
| 6 | 大量文書圧縮 | Already (強化可能) | `/digest`(NotebookLM特化), `/absorb`(統合特化) — 汎用圧縮パス弱い |
| 7 | レッドチーム | Already (強化不要) | `/improve` Adversarial Gate + pre_mortem + `/grill-interview` |
| 9 | Running Brief | Already (強化可能) | `/checkpoint` + HANDOFF + `/recall` — 横断UX未完成 |
| 12 | メタプロセス構築 | Already (強化不要) | `/skill-creator` + `/analyze-tacit-knowledge` + `/improve` |

## セカンドオピニオン（Phase 2.5）

### Codex 批評

- #4 を Gap → Partial に修正（persona + tone 学習が部分的に存在）
- #10 を Gap → Partial に修正（/think 等で近似可能）
- #6 の「強化不要」は甘い → 強化可能に変更
- #9 も横断UXが未完成で強化価値あり
- 優先度推奨: #11 > #5 > #6

### Gemini 周辺知識

- LLM 自己評価バイアスは構造的問題（Anthropic 実証）。ボイスマッチング/ペルソナの限界
- 2026年トレンド: ハーネス簡素化が主流。プロセス追加より既存最適化
- Generator-Evaluator → Context Compaction + Effort Controls への進化

## 取り込み判断

ユーザー選択: **全項目取り込み + Already 両方強化**

## 統合プラン

`docs/plans/2026-04-09-12-claude-patterns-integration.md` 参照。

3 Wave 構成:
- Wave 1 (High ROI): #11 rewrite skill, #5 /think decision mode, #6 /digest summarize mode
- Wave 2 (既存拡張): #3 /challenge persona, #10 /think roleplay, #9 /checkpoint brief
- Wave 3 (Light touch): #4 voice guide, #8 data analysis patterns
