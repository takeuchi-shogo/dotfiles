---
status: reference
last_reviewed: 2026-04-23
---

# DB スキーマ変更 Archetype

> repair-routing.md からの修復先。このドメインで繰り返しミスが発生した場合に参照・更新する。

## 定義

- **スコープ**: DB スキーマの追加・変更・削除、インデックス操作、データ移行を伴う変更
- **典型的なファイルパス例**: `migration/`, `db/schema*.sql`, `*_migrate*.go`, `*.sql`, `internal/db/migrations/`

## 既知の落とし穴

| 落とし穴 | 症状 | 関連 FM | 防止策 |
|---------|------|---------|--------|
| 破壊的変更（カラム削除/リネーム） | 旧コードが参照したままデプロイするとエラー | FM-003 | expand-contract パターンを使い、古いカラムは段階的に廃止 |
| 大テーブルへの `ALTER TABLE` | ロック取得による本番ダウン | FM-009 | `pt-online-schema-change` や `gh-ost` 等のオンライン変更ツールを使う |
| NOT NULL 制約の後付け | 既存 NULL 行があるとマイグレーション失敗 | FM-001 | デフォルト値付きで追加し、バックフィル後に制約を追加 |
| rollback 不能なマイグレーション | `down` で元に戻せない | FM-003 | `down` スクリプトを必ず実装し、ローカルで実行確認する |
| idempotent でないマイグレーション | 再実行時に重複エラー | FM-003 | `IF NOT EXISTS` / `IF EXISTS` 等で冪等性を保証する |

## 不変条件

- すべてのマイグレーションに `up` と `down` を実装する（rollback 可能）
- expand-contract パターン: 追加→並走→削除の順で段階的に進める
- マイグレーションは冪等（複数回実行しても同じ結果）
- 本番 DB への直接 `ALTER TABLE` は避け、オンラインスキーマ変更ツールを使う
- マイグレーション間の依存関係を明示し、並列実行を防ぐ

## テスト戦略

| テスト種別 | 目的 | 優先度 |
|-----------|------|--------|
| migration up/down テスト | `up` 後に `down` で元に戻ることを確認 | Critical |
| 冪等性テスト | `up` を2回実行してもエラーにならないことを確認 | High |
| データ整合性テスト | マイグレーション前後でデータが壊れないことを確認 | High |
| 本番データ量でのドライラン | ステージング環境で実行時間・ロック影響を計測 | Medium |

## Change Surface 連携

- **対応する Change Surface**: 「DB Migration」(Critical)
- **推奨 preflight**: migration-guard エージェント起動（rollback 可能性・破壊的変更の検出）
- `change-surface-preflight.md` の `migration/`, `*_migrate*`, `schema*`, `*.sql` パターンに該当
