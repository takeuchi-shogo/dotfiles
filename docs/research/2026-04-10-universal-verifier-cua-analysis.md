---
title: "The Art of Building Verifiers for Computer Use Agents"
source: https://arxiv.org/abs/2604.06240
authors: Corby Rosset, Pratyusha Sharma, Andrew Zhao, Ahmed Awadallah (Microsoft Research), Miguel Gonzalez-Fernandez (Browserbase)
date_analyzed: 2026-04-10
type: paper
tags: [cua, verification, evaluation, failure-taxonomy, scaffolding]
---

# Universal Verifier 論文分析レポート

## 主張

Microsoft Research が提案する Universal Verifier は、コンピュータ操作エージェント（CUA）のタスク成功判定を4つの設計原則に基づいて行い、既存手法（WebVoyager, WebJudge）を大幅に上回る精度（Cohen's κ = 0.64）と極低偽陽性率（0.01-0.08）を達成。アーキテクチャ設計がモデル能力以上に性能差を生むことを実証。

## 手法

1. **非重複ルーブリック生成** — タスク記述のみから評価基準を自動生成。確認バイアス・ファントム基準・カスケードエラーを防止
2. **プロセス報酬/アウトカム報酬の分離** — 実行品質（0.0-1.0）とタスク完了の二軸評価
3. **制御可能/不可能な失敗帰属分離** — エージェントミス vs 環境障害（CAPTCHA等）の明示的区別
4. **分割統治型コンテキスト管理** — スクリーンショットを基準ごとに関連性スコアリングして動的選別
5. **Two-pass scoring** — テキストアクション vs スクリーンショットの照合によるハルシネーション検出
6. **24失敗サブコード分類体系** — 構造化された診断レポート生成
7. **AI研究エージェント** — 1日で専門家の70%品質を達成。人間=基盤設計、AI=最適化の相補モデル
8. **アーキテクチャ > モデル能力** — GPT-5.2 アップグレードでは微改善。設計選択が主因

## 根拠

- Cohen's κ: 0.64（内部）/ 0.58（外部）— 人間アノテーター間一致率（0.53-0.57）と同等
- 偽陽性率: 0.01-0.08（WebVoyager: 45%+, WebJudge: 22%+）
- アノテーター学習効果: Verifier 推論参照後、一致率 κ=0.39 → 0.63（16.6%が判断変更）
- CUAVerifierBench: 標準化ベンチマーク公開

## 前提条件

- CUA（Web操作エージェント）のマルチモーダル軌跡が評価対象
- スクリーンショットベースの視覚的検証が中核
- GPT-5.2 レベルの LLM が検証器として利用可能

## ギャップ分析

### Gap
| # | 手法 | 現状 |
|---|------|------|
| 1 | 非重複ルーブリック生成 | 非重複原則はあるがタスク記述からの自動生成なし |
| 5 | Two-pass scoring | 該当する仕組みなし。post-compact-verify は別目的 |

### Partial
| # | 手法 | 現状 |
|---|------|------|
| 3 | 制御可能/不可能な失敗帰属 | recoveryType で間接区別。明示的二値分類なし |

### Already（強化可能）
| # | 手法 | 強化案 |
|---|------|--------|
| 2 | PRM/ORM分離 | process_correct + outcome_failed_uncontrollable ケース追加 |
| 4 | コンテキスト管理 | 長セッション向け動的関連性スコアリング概念追加 |
| 6 | 失敗分類 21 FM codes | controllability: agent/environment フィールド追加 |
| 7 | AutoEvolve | 構造レビューエスカレーション + alignment tipping 対策 |

### Already（強化不要）
| # | 手法 | 理由 |
|---|------|------|
| 8 | Scaffolding > Model | Morph 22:1, Meta-Harness 6x 等で確立済み |

## セカンドオピニオン

### Codex 批評
- 手法1・5: Partial → Gap に格上げ（本質的に異なる仕組み）
- 手法4: 動的関連性スコアリング概念は context decay 対策に価値あり
- 手法7: AutoEvolve との対応は不正確（論文は検証器設計プロセスへのAI活用）
- 優先度: 手法3（controllability帰属）が最優先 — 最小コスト・最大効果

### 周辺知識補完
- CUA検証: Computer Agent Arena（対戦評価）、WebTestBench（F1=26.4%の厳格基準）
- 自己改善: AgentEvolver ICE戦略（成功）vs alignment tipping process（崩壊リスク）
- 失敗帰属: 自動化は初期段階。RL分野で controllable/uncontrollable の潜在分離が進行中
- Confucius Code Agent: スキャフォールディング > モデル能力を実証

## 取り込み判断

全7項目を取り込み。統合プラン: `docs/plans/2026-04-10-universal-verifier-integration.md`
