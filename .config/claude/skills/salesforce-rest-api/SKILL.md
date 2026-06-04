---
name: salesforce-rest-api
description: "Salesforce REST API の開発・統合を支援する。sObject CRUD、SOQL/SOSL クエリ、Composite 系一括操作、OAuth 認証、エラー処理をカバー。公式『REST API 開発者ガイド』日本語版 (Spring '26) 全文を references に収録。Triggers: 'Salesforce API', 'Salesforce REST', 'Salesforce 連携', 'Salesforce 統合', 'sObject', 'SOQL', 'SOSL', 'Composite API', 'services/data', 'Salesforce からデータ取得'. Do NOT use for: Bulk API 2.0 / Metadata API / Connect REST API（本ガイドの対象外）、Apex 開発、Salesforce 管理画面の操作手順。"
origin: external
user-invocable: true
metadata:
  pattern: reference
---

# Salesforce REST API

公式『REST API 開発者ガイド』日本語版 (api_rest.pdf, 2026-03-31 生成, Spring '26 相当) のスキル化。
このファイルは要点の凝縮ガイド。詳細仕様・cURL 例・リクエスト/レスポンスボディの完全な定義は `references/` を参照する。

## URI 規約

```
https://MyDomainName.my.salesforce.com/services/data/vXX.X/resource/
```

- `MyDomainName`: 組織の My Domain サブドメイン（インスタンス URL をハードコードしない）
- `vXX.X`: API バージョン。利用可能バージョンは `GET /services/data/` で確認
- ID は**大文字小文字を区別する**。オブジェクト名・項目名は区別しない
- URI 長制限 16,384 バイト（超過で 414、ヘッダー込みで 431）
- 形式: JSON (デフォルト) / XML。`Accept` / `Content-Type` ヘッダーで指定

## 認証

接続アプリケーション (Connected App) + OAuth 2.0。全リクエストに `Authorization: Bearer <access_token>`。

- フロー選択・設定手順は Salesforce ヘルプ「OAuth 認証フロー」「接続アプリケーションの作成」を参照（本ガイドは概要のみ）
- 401 = トークン期限切れ/無効 → リフレッシュして再試行
- 開発・テストは Developer Edition / Sandbox / スクラッチ組織で行う（本番組織で試さない）
- ユーザープロファイルに「API の有効化」権限が必要。統合用途には Salesforce インテグレーションユーザーライセンスで API 限定アクセスにする

## 主要エンドポイント

URI は `https://MyDomainName.my.salesforce.com` からの相対パス。

| 操作 | メソッド + URI |
| --- | --- |
| API バージョン一覧 | `GET /services/data/` |
| 組織の制限・残量 | `GET /services/data/vXX.X/limits/` |
| 全オブジェクト一覧 | `GET /services/data/vXX.X/sobjects/` |
| オブジェクトの項目メタデータ | `GET /services/data/vXX.X/sobjects/{Object}/describe/` |
| レコード作成 | `POST /services/data/vXX.X/sobjects/{Object}/` |
| レコード取得 | `GET /services/data/vXX.X/sobjects/{Object}/{id}?fields=...` |
| レコード更新 | `PATCH /services/data/vXX.X/sobjects/{Object}/{id}` |
| レコード削除 | `DELETE /services/data/vXX.X/sobjects/{Object}/{id}` |
| 外部 ID で Upsert | `PATCH /services/data/vXX.X/sobjects/{Object}/{ExtIdField}/{value}` |
| SOQL クエリ | `GET /services/data/vXX.X/query?q={SOQL}` |
| SOQL 続きの取得 | `GET {nextRecordsUrl}` (レスポンス内の値をそのまま使う) |
| 削除済みを含む SOQL | `GET /services/data/vXX.X/queryAll?q={SOQL}` |
| SOSL 検索 | `GET /services/data/vXX.X/search/?q={SOSL}` |
| 複合リクエスト (連動・最大 25) | `POST /services/data/vXX.X/composite` |
| 一括 CRUD (最大 200 件/回, v43.0+) | `POST|PATCH|DELETE /services/data/vXX.X/composite/sobjects` |
| 一括取得 (ID 指定, v43.0+) | `GET /services/data/vXX.X/composite/sobjects/{Object}?ids=...&fields=...` |
| ネストレコード一括作成 | `POST /services/data/vXX.X/composite/tree/{Object}` |

## クエリのページング

- 同期クエリは一度に最大 2,000 レコード（サイズ・複雑さによりそれ未満になる）
- レスポンス: `totalSize` / `done` / `nextRecordsUrl` / `records`
- `done: false` の間は `nextRecordsUrl` を GET し続ける（自前でロケーター文字列を組み立てない）
- SOQL の URI 埋め込みではスペースを `+` または `%20` にエンコード

## エラー応答

ボディは `[{ "message", "errorCode", "fields"? }]` の配列。主要コード:

| HTTP | 意味 |
| --- | --- |
| 200 / 201 / 204 | 成功 (GET / POST=Created / DELETE=No Content) |
| 300 | 外部 ID が複数レコードに一致（一致リストが返る） |
| 304 / 412 | 条件付きリクエスト (If-Modified-Since 等) の結果 |
| 400 | リクエストボディ不正 (`MALFORMED_QUERY`, `MALFORMED_ID` 等) |
| 401 | トークン期限切れ・無効 |
| 403 | 権限不足。`REQUEST_LIMIT_EXCEEDED` なら API 制限超過 |
| 404 | リソースなし (`NOT_FOUND`)。URI ミス or 共有設定を疑う |
| 409 | 競合。API バージョンとリソースの対応を確認 |
| 500 / 502 / 503 | Salesforce 側エラー / メンテナンス |

## 運用上の要点

- **API 消費の監視**: レスポンスの `Sforce-Limit-Info: api-usage=used/total` ヘッダーを読む。詳細は `GET /services/data/vXX.X/limits/`
- **Salesforce 固有ヘッダー**: Assignment Rule（ToDo/ケースの割り当て）、重複ルール制御、条件付き要求 (ETag/If-Match)、Query Options (バッチサイズ) — 詳細は `references/overview.md`
- **`allOrNone`**: Composite / Collections でトランザクション的に全成功 or 全ロールバックを制御
- **Date/DateTime 書式**: date は `yyyy-MM-dd`（オフセット指定不可）。dateTime は `yyyy-MM-ddTHH:mm:ss.SSS+/-HH:mm` または `yyyy-MM-ddTHH:mm:ss.SSSZ`

## references ルーティング

| 知りたいこと | 参照先 |
| --- | --- |
| 認証・全ヘッダー仕様・CORS・エラー詳細・cURL 基礎 | `references/overview.md` |
| 実践例（CRUD / Blob / 承認プロセス / イベント監視 / 複合パターン） | `references/examples.md` |
| sObject 系全リソース仕様（Describe / Rows / External ID / レイアウト / クイックアクション 等） | `references/reference-sobject.md` |
| Query / QueryAll / Search / パラメーター化検索 / Scheduler / Lightning Usage | `references/reference-query-search.md` |
| Composite / Composite Graph / Batch / sObject Tree / sObject Collections | `references/reference-composite.md` |

各ファイル冒頭に「収録セクション」一覧あり。Grep で `===== PAGE n =====` マーカーを使うと PDF ページ単位で参照できる。

## Anti-Patterns

| NG | 代わりに |
| --- | --- |
| 大量レコードを 1 件ずつ CRUD | sObject Collections (200 件/回)。数十万件以上は Bulk API 2.0（本ガイド対象外） |
| `nextRecordsUrl` を無視して 2,000 件で打ち切る | `done: false` の間ページングを継続 |
| インスタンス URL (`naXX.salesforce.com`) のハードコード | My Domain URL を使用 |
| エラーボディを読まず HTTP コードだけで判定 | `errorCode` で分岐（403 でも原因は権限 / API 制限の 2 系統） |
| 本番組織で開発・検証 | Developer Edition / Sandbox / スクラッチ組織 |

## 動作確認

このスキルの検証: 「Account を外部 ID で upsert する cURL は？」「SOQL の 2,000 件超の取得方法は？」等の質問に、references を引いて URI・メソッド・ボディ例まで answer できれば OK。
