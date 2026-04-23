---
status: reference
last_reviewed: 2026-04-23
---

# Structured Output ガイド

Claude API で構造化出力を確実に得るための Architect-level パターン集。

---

## 1. tool_choice 設定の使い分け

| 設定 | 挙動 | ユースケース |
|------|------|-------------|
| `"auto"` | モデルがツール呼び出しかテキスト返却かを判断 | 一般的な操作。ツール不要な質問にも対応可能 |
| `"any"` | 必ずいずれかのツールを呼び出す | 複数スキーマから保証された構造化出力を得たい場合 |
| `{"type":"tool","name":"extract_metadata"}` | 特定ツールを強制 | パイプライン初段のメタデータ抽出等、必須ステップ |

**判断基準**: 「出力が常に JSON でなければ後続が壊れる」→ `"any"` or 指定。「テキスト回答も許容」→ `"auto"`。

## 2. JSON Schema 設計パターン

### required vs optional

- **required**: 必ず値が存在すべきフィールド。欠損時はモデルが推測してしまうリスクあり
- **optional**: ソースに存在しない可能性があるフィールド

### nullable で fabrication 防止

ソースデータに値がない場合、モデルが「もっともらしい値」を捏造する。`nullable: true` を指定し、見つからなければ `null` を返させる。

```json
{
  "expiry_date": { "type": ["string", "null"], "description": "ISO 8601 date. ソースに記載がなければ null" }
}
```

### enum + "unclear" / "other"

```json
{
  "category": {
    "type": "string",
    "enum": ["invoice", "receipt", "contract", "other"],
    "description": "文書種別。該当なしは other"
  },
  "category_detail": {
    "type": ["string", "null"],
    "description": "category が other の場合の自由記述"
  },
  "sentiment": {
    "type": "string",
    "enum": ["positive", "negative", "neutral", "unclear"]
  }
}
```

### Format normalisation rules

スキーマの `description` に正規化ルールを明記する:
- 日付: `"ISO 8601 (YYYY-MM-DD)"`
- 通貨: `"小数点以下2桁の数値。通貨記号は currency フィールドに分離"`
- 電話番号: `"E.164 形式 (+819012345678)"`

## 3. Validation-Retry Loop

```
抽出 → 検証 → (不合格) → エラーフィードバック付き再抽出 → 検証 → ...
```

### retry が有効なケース

- フォーマット不一致（日付が `MM/DD/YYYY` で返った → ISO 8601 に再変換指示）
- 値の配置ミス（shipping_address に billing_address が入った）
- JSON 構文エラー

### retry が無効なケース

- ソースに情報が存在しない（retry しても fabrication を誘発するだけ）
- モデルの知識外の事実（外部 API 参照が必要）

### E2E フロー例: 請求書メタデータ抽出

```
1. Extract: tool_choice で extract_invoice を強制 → {"vendor": "Acme", "total": "15,000", "date": "03/15/2026", "currency": null}
2. Validate: date が ISO 8601 でない → NG, total が数値でない → NG, currency が null → NG
3. Retry: エラーフィードバック付き再抽出
   → {"vendor": "Acme", "total": 15000, "date": "2026-03-15", "currency": "JPY"}
4. Validate: 全フィールド OK → Pass
5. Output: 正規化済みデータを下流パイプラインに送信
```

### 不一致検出パターン

```json
{
  "line_items": [...],
  "calculated_total": 15000,
  "stated_total": 14500,
  "conflict_detected": true,
  "conflict_note": "line_items 合計と記載額に ¥500 の差異"
}
```

`conflict_detected: true` の場合、下流で人間レビューにルーティングする。モデルに「正しい方を選べ」と指示しない。

## 4. Access Failure vs Valid Empty Result

| 状態 | 意味 | 対応 |
|------|------|------|
| **Access failure** | データソースに到達不可（timeout, 認証エラー等） | retry / fallback を検討 |
| **Valid empty result** | 正常にクエリし結果がゼロ件 | そのまま空結果を返す。retry 不要 |

```json
{
  "status": "access_failure",
  "error": "API returned 503",
  "results": null
}
```

```json
{
  "status": "success",
  "results": []
}
```

**混同すると**: 空結果を failure と誤判定 → 無限 retry。failure を空結果と誤判定 → データ欠損を見逃す。

## 5. Batch Processing (Message Batches API)

| 観点 | 同期 API | Batch API |
|------|----------|-----------|
| コスト | 標準 | **50% 削減** |
| レイテンシ | リアルタイム | 最大 24 時間（SLA なし） |
| multi-turn tool calling | 対応 | **非対応** |
| 用途 | pre-merge checks 等ブロッキング処理 | overnight reports 等レイテンシ許容処理 |

### custom_id による相関

```python
requests = [
    {"custom_id": f"doc-{doc.id}", "params": {"model": "...", "messages": [...]}}
    for doc in documents
]
batch = client.messages.batches.create(requests=requests)

# 結果取得時
for result in client.messages.batches.results(batch.id):
    doc_id = result.custom_id  # "doc-123" → 元ドキュメントと紐付け
    if result.result.type == "succeeded":
        process(result.result.message)
    else:
        failed_ids.append(doc_id)  # 修正して再送信
```

### 失敗リカバリ

1. `custom_id` で失敗リクエストを特定
2. プロンプトまたはデータを修正
3. 失敗分のみ新バッチとして再送信（全件再送しない）
