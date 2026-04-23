---
status: active
last_reviewed: 2026-04-23
---

# Advisor Strategy リファレンス

> 出典: Anthropic "The Advisor Strategy" (2026-04-09)
> 補足: FrugalGPT (Stanford), AutoMix (NeurIPS 2024), RouteLLM (ICLR 2025)

## 概要

大規模モデル（Advisor）を小規模モデル（Executor）の戦略的相談役として使うパターン。
Executor がタスクを主体的に実行し、困難な判断に直面した場合のみ Advisor に相談する。

**現行ハーネスとの関係**: 現行は Opus がトップダウンで委譲する設計。Advisor Strategy は **ボトムアップ escalation**（Executor が自発的に相談）を追加する補完パターン。

## Response Types

Advisor の返却は以下の3型に分類する:

| Type | 用途 | 例 |
|------|------|-----|
| **plan** | 戦略的方向性の提示 | 「このリファクタは X パターンで進めるべき。理由は Y」 |
| **correction** | Executor の誤りの修正 | 「そのアプローチは Z の制約を見落としている。代わりに W を検討」 |
| **stop** | 安全弁。Executor の続行を停止 | 「この変更は破壊的影響がある。親エージェントに escalate せよ」 |

`stop` は Executor に作業中断を強制する唯一のシグナル。Advisor がリスクを検知した場合に発行する。

## Role-Specific 制約

Advisor 役割には以下の制約を適用する:

| 制約 | 値 | 根拠 |
|------|-----|------|
| **max_tokens** | 400-700 | 戦略的指針に特化。詳細な実装指示は Executor の責務 |
| **max_uses** | 3 / task | advisor 依存の防止。Anthropic 推奨値 |
| **tools** | なし | Advisor はツール呼び出しを行わない。判断と助言のみ |
| **user-facing output** | なし | Advisor の出力は Executor のみが消費する |

## 中間相談プロトコル

### Executor → Advisor 相談の判断基準

```
アーキテクチャ判断が必要?              → 相談する
セキュリティ影響が不明?                → 相談する
2つ以上の妥当なアプローチで迷っている? → 相談する
定型的な実装作業?                      → 相談しない
既存パターンの踏襲?                    → 相談しない
迷ったら?                              → 1回目は相談、同種の判断は学習して自走
```

### 相談時の最小入力

Executor が Advisor に渡す情報:

| # | 項目 | 内容 |
|---|------|------|
| 1 | **状況** | 何をしていて、どこで詰まったか（2-3文） |
| 2 | **選択肢** | 検討した選択肢とそれぞれのトレードオフ |
| 3 | **制約** | 判断に影響する制約（既存コード、パフォーマンス要件等） |

## 既知の制約・トレードオフ

### Unknown Unknowns 問題

Executor が「わからないことをわかっていない」場合、Advisor に相談できない。
FrugalGPT, AutoMix, RouteLLM で共通の未解決課題。

**緩和策**:
- 既存の hook ベースの検出（`error-to-codex.py`, `suggest-gemini.py`）で補完
- Advisor 相談と hook ベース検出の二重安全網として機能させる

### レイテンシ不均一

動的相談はネットワーク往復 + 大モデル推論時間が加算される。
85% コスト削減はトークン・API 料金ベースであり、wall clock time は別問題。

### Same-Stack vs Heterogeneous

記事の実証は Claude family 内の same-stack 連携。
当セットアップの異種モデル（Codex/Gemini）連携とは前提が異なる。
Advisor パターンは Claude-Claude 間で適用し、異種モデル連携は既存の委譲パターンを維持する。

### Executor のフレーミングバイアス

Executor が「何を問題と認識しているか」のフレーミングが Advisor の回答品質を規定する。
Executor の認識が誤っていれば、Advisor のアドバイスも的外れになる。

## 適用スコープ

| 適用する | 適用しない |
|---------|-----------|
| Sonnet サブエージェントの長時間実装タスク | 短命な Explore / 軽量 Haiku タスク |
| アーキテクチャ判断を含む委譲 | 定型的な検索・フォーマット変換 |
| Claude-Claude（same-stack）連携 | Codex / Gemini への異種モデル委譲 |

## 先行研究

| 手法 | 出典 | アプローチ | 制約 |
|------|------|-----------|------|
| FrugalGPT | Stanford, TMLR | 安いモデルから順に試し、品質不足なら昇格 | stop judger の精度がドメイン依存 |
| AutoMix | NeurIPS 2024 | few-shot self-verification で確信度推定 | 自己検証ノイズの累積 |
| RouteLLM | ICLR 2025 | 人間嗜好データでルーター学習 | 分布シフトで未見ドメイン劣化 |
| xRouter | arxiv 2025 | RL でパレートフロンティア最適化 | 学習パイプライン必要 |
| MasRouter | ACL 2025 | マルチエージェント向けルーティング | チーム全体のコンテキスト考慮 |
