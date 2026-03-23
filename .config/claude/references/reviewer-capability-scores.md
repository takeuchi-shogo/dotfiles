# Reviewer Capability Scores

> HACRL (arXiv:2603.02604) の知見に基づく。
> 能力差を無視した等価重み付けは、特に困難なケースで大幅に劣化する (AIME2025 で -44%)。
> レビューアーのドメイン別 capability score を定義し、`/review` の Synthesis フェーズで重み付けに使用する。

---

## Score Table

各スコアは 0.0-1.0。レビューアーの設計意図・専門性に基づく手動キャリブレーション初期値。

| Reviewer | Logic | Security | Performance | Style | Overall |
|---|---|---|---|---|---|
| code-reviewer | 0.80 | 0.75 | 0.75 | 0.90 | 0.80 |
| codex-reviewer | 0.90 | 0.70 | 0.80 | 0.55 | 0.74 |
| security-reviewer | 0.60 | 0.95 | 0.65 | 0.40 | 0.65 |
| edge-case-hunter | 0.85 | 0.60 | 0.70 | 0.40 | 0.64 |
| cross-file-reviewer | 0.75 | 0.65 | 0.70 | 0.60 | 0.68 |
| silent-failure-hunter | 0.80 | 0.70 | 0.60 | 0.35 | 0.61 |
| type-design-analyzer | 0.70 | 0.50 | 0.55 | 0.85 | 0.65 |
| golang-reviewer | 0.80 | 0.75 | 0.85 | 0.80 | 0.80 |
| comment-analyzer | 0.40 | 0.30 | 0.30 | 0.90 | 0.48 |
| test-analyzer | 0.75 | 0.50 | 0.60 | 0.70 | 0.64 |
| product-reviewer | 0.65 | 0.40 | 0.40 | 0.60 | 0.51 |
| design-reviewer | 0.60 | 0.45 | 0.50 | 0.85 | 0.60 |

### Score Rationale

- **code-reviewer**: 汎用レビューア。Style が最も高い (言語チェックリスト注入により精度向上)。全ドメインで安定
- **codex-reviewer**: 深い推論 (reasoning effort: high/xhigh) により Logic が最高。Style は簡潔すぎる傾向
- **security-reviewer**: Security 特化。他ドメインは専門外
- **edge-case-hunter**: 境界値・異常系の Logic 検出に特化。Style/Security は専門外
- **cross-file-reviewer**: モジュール間整合性。特定ドメインに偏らない中間スコア
- **silent-failure-hunter**: エラーハンドリングの Logic 検出。Style は専門外
- **type-design-analyzer**: 型設計 = Style + Logic の中間。Security/Performance は専門外
- **golang-reviewer**: Go 特化で全ドメインバランス良好。Performance が高い (Go の並行処理・メモリ)
- **comment-analyzer**: コメント品質 = Style 特化。他ドメインのスコアは低い
- **test-analyzer**: テスト設計の Logic。Security/Performance は間接的
- **product-reviewer**: 仕様整合性。技術的ドメインのスコアは低い
- **design-reviewer**: UI/UX 設計。Style が高い。Security/Performance は専門外

---

## Domain Classification Guide

指摘をどのドメインにマッピングするか:

| Domain | 対象 |
|---|---|
| **Logic** | バグ、ロジックエラー、境界条件、nil/null 安全性、競合状態 |
| **Security** | 脆弱性、認証/認可、入力検証、依存関係リスク、OWASP |
| **Performance** | 計算量、メモリ使用、I/O、並行処理、キャッシュ |
| **Style** | 命名、構造、可読性、慣用的パターン、型設計 |

**Overall** は加重平均ではなく、ドメインが特定できない指摘に使用する。

---

## Update Policy

- **更新サイクル**: `/improve` サイクルで段階的に更新
- **データソース**: `review-findings.jsonl` の accept/reject 率を基にレビューアー別・ドメイン別の精度を算出
- **更新ルール**:
  - accept 率が高い (>80%) ドメイン: スコアを +0.05 (上限 0.95)
  - reject 率が高い (>50%) ドメイン: スコアを -0.05 (下限 0.20)
  - データ不足 (<10 findings) のドメイン: 変更しない
- **変更上限**: 1回の `/improve` で最大 2 レビューアーのスコアを変更
- **監査**: スコア変更時は git commit メッセージに変更理由を記載

---

## Usage

`/review` の Step 4 Synthesis で参照する。詳細な合成ルールは `review-consensus-policy.md` Section 6 を参照。
