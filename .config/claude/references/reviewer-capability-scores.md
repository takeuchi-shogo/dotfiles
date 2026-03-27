# Reviewer Capability Scores

> HACRL (arXiv:2603.02604) の知見に基づく。
> 能力差を無視した等価重み付けは、特に困難なケースで大幅に劣化する (AIME2025 で -44%)。
> レビューアーのドメイン別 capability score を定義し、`/review` の Synthesis フェーズで重み付けに使用する。

---

## Score Table

各スコアは 0.0-1.0。レビューアーの設計意図・専門性に基づく手動キャリブレーション初期値。

| Reviewer | Logic | Security | Performance | Style | Architecture | UX | Documentation | Overall |
|---|---|---|---|---|---|---|---|---|
| code-reviewer | 0.80 | 0.75 | 0.75 | 0.90 | 0.70 | 0.30 | 0.60 | 0.80 |
| codex-reviewer | 0.90 | 0.70 | 0.80 | 0.55 | 0.75 | 0.20 | 0.50 | 0.74 |
| security-reviewer | 0.60 | 0.95 | 0.65 | 0.40 | 0.50 | 0.15 | 0.35 | 0.65 |
| edge-case-hunter | 0.85 | 0.60 | 0.70 | 0.40 | 0.40 | 0.20 | 0.25 | 0.64 |
| cross-file-reviewer | 0.75 | 0.65 | 0.70 | 0.60 | 0.85 | 0.25 | 0.45 | 0.68 |
| silent-failure-hunter | 0.80 | 0.70 | 0.60 | 0.35 | 0.35 | 0.15 | 0.25 | 0.61 |
| type-design-analyzer | 0.70 | 0.50 | 0.55 | 0.85 | 0.65 | 0.20 | 0.40 | 0.65 |
| golang-reviewer | 0.80 | 0.75 | 0.85 | 0.80 | 0.70 | 0.20 | 0.55 | 0.80 |
| comment-analyzer | 0.40 | 0.30 | 0.30 | 0.90 | 0.25 | 0.15 | 0.90 | 0.48 |
| test-analyzer | 0.75 | 0.50 | 0.60 | 0.70 | 0.40 | 0.15 | 0.50 | 0.64 |
| product-reviewer | 0.65 | 0.40 | 0.40 | 0.60 | 0.55 | 0.80 | 0.65 | 0.51 |
| design-reviewer | 0.60 | 0.45 | 0.50 | 0.85 | 0.45 | 0.95 | 0.50 | 0.60 |

### Domain Signal Trust

> Del et al. (arXiv:2603.19118): 不確実性信号の品質はドメインに強く依存する。
> 検証可能な（deterministic）タスクでは confidence score (VC) の識別力が高く、
> 主観的なタスクでは agreement rate (SC) の方が相対的に信頼できる。

レビュー合成時、タスクの性質に応じて confidence と agreement の信頼度を調整する:

| タスク性質 | 例 | confidence 信頼度 | agreement 信頼度 | 根拠 |
|-----------|-----|-------------------|------------------|------|
| **Deterministic** | 型チェック、ロジック検証、セキュリティ脆弱性 | 高 | 中 | 正解が一意。VC の AUROC が高い（数学: 81.4 @ K=8） |
| **Semi-deterministic** | パフォーマンス、テスト設計、エラーハンドリング | 中 | 中 | 複数の妥当解がある。VC/SC 同程度（STEM: 78.4/各タスク依存） |
| **Subjective** | 命名、コメント品質、デザイン、UX | 低 | 高 | 正解が文脈依存。VC の識別力が低い（人文: 72.6 @ K=8） |

**活用方法**: `review-consensus-policy.md` §6 SCVC Hybrid Signal の hybrid_score 判定時、
deterministic タスクでは confidence スコアの高い指摘をより信頼し、
subjective タスクでは agreement rate の高い指摘を優先する（λ の微調整ではなく、判定の解釈指針として）。

### Score Rationale

- **code-reviewer**: 汎用レビューア。Style が最も高い (言語チェックリスト注入により精度向上)。全ドメインで安定
- **codex-reviewer**: 深い推論 (reasoning effort: high/xhigh) により Logic が最高。Style は簡潔すぎる傾向
- **security-reviewer**: Security 特化。他ドメインは専門外
- **edge-case-hunter**: 境界値・異常系の Logic 検出に特化。Style/Security は専門外
- **cross-file-reviewer**: モジュール間整合性。Architecture が最高 (インターフェース不整合・依存方向の検出が本務)
- **silent-failure-hunter**: エラーハンドリングの Logic 検出。Style は専門外
- **type-design-analyzer**: 型設計 = Style + Logic の中間。Security/Performance は専門外
- **golang-reviewer**: Go 特化で全ドメインバランス良好。Performance が高い (Go の並行処理・メモリ)
- **comment-analyzer**: コメント品質 = Style + Documentation 特化。Documentation が最高 (コメント・ドキュメント品質が本務)
- **test-analyzer**: テスト設計の Logic。Security/Performance は間接的
- **product-reviewer**: 仕様整合性 + UX 判断 (0.80)。技術的ドメインのスコアは低いが UX/Documentation は高め
- **design-reviewer**: UI/UX 設計。UX が最高 (0.95)。Style も高い。Security/Performance は専門外

---

## Domain Classification Guide

指摘をどのドメインにマッピングするか:

| Domain | 対象 |
|---|---|
| **Logic** | バグ、ロジックエラー、境界条件、nil/null 安全性、競合状態 |
| **Security** | 脆弱性、認証/認可、入力検証、依存関係リスク、OWASP |
| **Performance** | 計算量、メモリ使用、I/O、並行処理、キャッシュ |
| **Style** | 命名、構造、可読性、慣用的パターン、型設計 |
| **Architecture** | モジュール間整合性、結合度/凝集度、インターフェース設計、依存方向 |
| **UX** | UI 直感性、アクセシビリティ、状態遷移、エラー表示、レスポンシブ |
| **Documentation** | コメント品質、API ドキュメント、README 鮮度、コードとの乖離 |

**Overall** は加重平均ではなく、ドメインが特定できない指摘に使用する。

### Error Mode Orthogonality (設計原則)

> Tu (2026): エラーモード直交性は固定特性ではなく**建築設計選択**。
> レビューアー追加の価値は「精度」ではなく「補完的能力」で決まる。

レビューアー追加時の判断基準:
1. 既存レビューアーと**異なる失敗モード**をキャッチするか？
2. 既存レビューアーと**異なる情報ソース**を使うか？（diff のみ vs コンテキスト込み vs ツール出力）
3. 既存レビューアーと**異なるモデル**か？

3つ全て「はい」→ rho が低く追加価値が高い。全て「いいえ」→ 同種の追加で m_eff への寄与は逓減。
詳細: `references/structured-test-time-scaling.md` §8

---

## Update Policy

- **更新サイクル**: `/improve` サイクルで段階的に更新
- **詳細ルール**: [Score Calibration Feedback Loop](#score-calibration-feedback-loop) を参照
- **変更上限**: 1回の `/improve` で最大 2 レビューアーのスコアを変更
- **データ不足**: <10 findings のドメインは変更しない
- **監査**: スコア変更時は git commit メッセージに変更理由を記載

---

## Usage

`/review` の Step 4 Synthesis で参照する。詳細な合成ルールは `review-consensus-policy.md` Section 6 を参照。

---

## Score Calibration Feedback Loop

> Qoder: 各 Expert が独立してスキル抽出 — reviewer ごとの精度追跡

### フィードバック収集

レビュー結果に対するユーザーの ACCEPT/REJECT を `review-findings.jsonl` に記録する。

| フィールド | 説明 |
|---|---|
| `reviewer` | レビューアー名（例: `code-reviewer`） |
| `domain` | 指摘のドメイン（Logic/Security/Performance/Style/Architecture/UX/Documentation） |
| `finding_id` | 指摘の一意 ID |
| `human_verdict` | `AGREE`（正しい指摘）/ `DISAGREE`（誤検知）/ `UNKNOWN`（未判定、初期値） |
| `timestamp` | ISO 8601 |

### スコア更新ルール

| イベント | スコア変動 | 根拠 |
|---|---|---|
| ACCEPT | +0.02 | 正しい指摘は緩やかに評価向上 |
| FALSE_POSITIVE | -0.05 | 誤検知は保守的に評価低下（信頼回復にはACCEPT 2.5回分必要） |

**制約**:
- スコア範囲: 0.20 - 0.95
- 1回の `/improve` サイクルで最大 2 レビューアーのスコアを変更
- データ不足（<10 findings）のドメインは変更しない

### 更新タイミング

`/improve` サイクル時に `review-findings.jsonl` を集計し、上記ルールに基づいてスコアを更新する。
手動更新は git commit メッセージに変更理由を記載すること（Update Policy 参照）。

### QA チューニング提案（R-12 連携）

`qa-tuning-analyzer.py` が蓄積データから以下を検出し、スコア更新提案を生成する:

| 検出パターン | スコアへの影響 | 提案内容 |
|---|---|---|
| **見逃し** (DISAGREE rate ≥ 30%) | 該当ドメインのスコア -0.05 | チェックリストへの failure_mode 明示追加 |
| **過検出** (watch ratio ≥ 70%) | Style スコア -0.05 | style weight の引き下げ |
| **Rationalization** (warning ≥ 5) | スコア変更なし（プロンプト改善推奨） | 懐疑的ペルソナの強化 |

提案は `/improve` 実行時に advisory として出力。自動適用はしない（Rule 10 準拠）。
