---
date: 2026-04-17
experiment: Hermes absorb Plan B2 — Semantic search feasibility
status: scaffolded (not yet executed)
scope: ~/.claude/agent-memory/{learnings,traces,metrics}/**/*.jsonl
references:
  - docs/plans/2026-04-17-hermes-absorb-plan.md
  - docs/research/2026-04-17-hermes-fleet-shared-memory-analysis.md
  - docs/specs/2026-04-17-memory-schema-retention.md
---

# Semantic Search Experiment Report

## 現状

**セットアップ未実行**。本ディレクトリのスクリプトは雛形で、以下の実行が必要:

1. `bash setup.sh` — Ollama (brew install) + nomic-embed-text pull + Qdrant Docker
2. `python3 index.py --limit 2000` — JSONL → Qdrant (redactor 適用済み)
3. `python3 eval.py` — 10 クエリ recall@5 + latency 計測 → `eval-results.json`
4. 本 `report.md` の「結果」「判定」セクションを更新

## 構成

| コンポーネント | 役割 | 備考 |
|-------------|------|------|
| Qdrant (Docker, port 6333) | vector store | `qdrant-data/` に bind-mount |
| Ollama (brew, port 11434) | local embedding | `nomic-embed-text` (768 dim) |
| `index.py` | JSONL → vectors → Qdrant upsert | A2 redactor で embed 前にマスク |
| `eval.py` | 10 クエリ検索 + recall@5 計測 | `queries/queries.json` 参照 |

## クエリ設計 (10 件)

`queries/queries.json` に格納。3 カテゴリから構成:

- エラーパターン (TypeError, Permission denied, Go nil pointer)
- スキル・レビュー (invocation outcome, review-finding silent failure, Codex risk flag)
- AutoEvolve/telemetry (hook latency, improvement proposal, session recovery)

## 評価基準

- **Recall@5**: 上位 5 件の payload (file / category / type_hint) に期待キーワードが含まれる割合
  - 手書きラベル不在のためヒューリスティック判定 (`judge()` 関数)
  - 本番導入判断前に手動レビューで true recall を確認する想定

- **Latency**: embed + search の合計時間 (per-query), p50 / p95

## 撤退条件 (plan 準拠)

| 条件 | 閾値 | 判定 |
|------|------|-----|
| Recall@5 が低い | < 0.5 | 実験クローズ (`docs/research/` へ移動) |
| Query latency | p50 > 500ms | 実用性なし、撤退 |
| Setup 時間 | > 4h | インフラコスト過大、撤退 |

## 結果 (TBD)

<!-- eval.py 実行後に下記を更新 -->

| 指標 | 値 | 閾値 | 判定 |
|------|----|------|-----|
| Recall@5 | TBD | ≥ 0.5 | TBD |
| Latency p50 | TBD ms | ≤ 500 | TBD |
| Latency p95 | TBD ms | — | — |
| Index size | TBD entries | — | — |

### クエリ別結果

<!-- `eval-results.json` の results 配列を転記 -->

## 観察と判断 (TBD)

- 誤検知/取りこぼしパターン
- nomic-embed-text と日本語混在 JSONL の相性
- redactor 適用後の embedding 品質への影響

## 継続/撤退判定 (TBD)

- [ ] 継続 (production 組込み計画)
- [ ] 限定継続 (特定カテゴリのみ)
- [ ] 撤退 (実験クローズ、`docs/research/` へ移動)

**判断根拠**: TBD

## 次のステップ (継続時)

1. schema spec (B1) 準拠で `id`, `type`, `source` を JSONL に付与
2. Stop hook から差分 upsert (index.py を日次化)
3. mem0 abstraction 導入可否の再検討
4. Query インターフェース (CLI / skill) の設計

## 次のステップ (撤退時)

1. 本ディレクトリを `docs/research/2026-04-hermes-semantic-search-retreat.md` として移動
2. `setup.sh` 実行で生成した Qdrant Docker container / volume / ollama model を破棄
3. 学びを `docs/research/_index.md` に短縮索引化
