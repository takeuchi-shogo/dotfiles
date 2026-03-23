# Model Expertise Map

> HACRL (arXiv:2603.02604) の Exponential IS に基づく。
> 出力分布が近いエージェントからの学習を優先する原理を、
> `/debate` のモデル意見集約における専門分野近接重み付けに適用する。

---

## Score Table

各スコアは 0.0-1.0。タスクドメインと各モデルの得意分野の近さを表す。

| Domain | Claude (Opus) | Codex (gpt-5.4) | Gemini (2.5) |
|---|---|---|---|
| System Design | 0.85 | 0.90 | 0.80 |
| Frontend/React | 0.90 | 0.75 | 0.70 |
| Security | 0.80 | 0.85 | 0.75 |
| Research/Analysis | 0.80 | 0.70 | 0.95 |
| Go/Backend | 0.80 | 0.90 | 0.75 |
| DevOps/Infra | 0.70 | 0.75 | 0.85 |
| Code Review | 0.85 | 0.90 | 0.75 |
| Documentation | 0.85 | 0.65 | 0.80 |

### Score Rationale

- **Claude (Opus)**: Frontend/React と Documentation が最も高い。幅広いバランス
- **Codex (gpt-5.4)**: System Design, Go/Backend, Code Review で最高。深い推論が強み
- **Gemini (2.5)**: Research/Analysis が突出。1M コンテキストによる大規模分析・Google grounding

---

## Domain Classification Guide

`/debate` の質問をどのドメインにマッピングするか:

| Domain | 対象 |
|---|---|
| **System Design** | アーキテクチャ選定、モジュール分割、スケーラビリティ |
| **Frontend/React** | UI コンポーネント、状態管理、レンダリング最適化 |
| **Security** | 認証/認可、脆弱性、暗号化、入力検証 |
| **Research/Analysis** | ライブラリ比較、技術調査、ベストプラクティス |
| **Go/Backend** | API 設計、DB 選定、並行処理、バックエンド全般 |
| **DevOps/Infra** | CI/CD、デプロイ、監視、IaC |
| **Code Review** | コード品質、リファクタリング方針 |
| **Documentation** | ドキュメント戦略、API ドキュメント設計 |

複数ドメインにまたがる場合は、最も近いドメインのスコアを使用する。

---

## Update Policy

- `reviewer-capability-scores.md` と同様に `/improve` サイクルで段階的に更新
- `/debate` の結果に対するユーザーの採用/不採用率をデータソースとする
- 変更上限: 1回の更新で最大 2 ドメインのスコアを変更

---

## Usage

`/debate` の Step 4 Synthesize で参照する。
`codex-delegation.md` / `gemini-delegation.md` からも参照される。
