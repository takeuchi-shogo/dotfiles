# スキーマ設計 + Protovalidate によるフィールド検証

## Protobuf ベストプラクティス

**パッケージ命名**: `{organization}.{domain}.{version}` 形式を使う。

```protobuf
syntax = "proto3";
package acme.payment.v1;
```

**バージョニング戦略**: パッケージ名にバージョンを含める（v1, v2）。
既存のメッセージのフィールドを削除・型変更せず、新バージョンのパッケージを作る。

**フィールド設計のルール**:

| ルール | 理由 |
|--------|------|
| フィールド番号は削除しない | ワイヤフォーマットの互換性 |
| `reserved` で廃止番号を明示 | 将来の再利用事故を防止 |
| `optional` を意図的に使う | ゼロ値とフィールド未設定を区別 |
| `repeated` は空リストがデフォルト | nil チェック不要 |
| enum の 0 番は `UNSPECIFIED` にする | デフォルト値の意味を明確に |

```protobuf
enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  ORDER_STATUS_PENDING = 1;
  ORDER_STATUS_CONFIRMED = 2;
  ORDER_STATUS_SHIPPED = 3;
}

message Order {
  string order_id = 1;
  OrderStatus status = 2;
  repeated LineItem items = 3;
  reserved 4, 5;  // 廃止済みフィールド
  reserved "old_field_name";
}
```

## Protovalidate によるフィールド検証

Protovalidate を使うとスキーマ内に検証ルールを直接定義でき、
Bufstream のブローカーサイド検証や各言語のランタイム検証で活用できる。

```protobuf
syntax = "proto3";
package invoice.v1;

import "buf/validate/validate.proto";

message Invoice {
  string invoice_id = 1 [(buf.validate.field).string.uuid = true];
  string email = 2 [(buf.validate.field).string.email = true];
  uint32 quantity = 3 [
    (buf.validate.field).uint32.gt = 0,
    (buf.validate.field).uint32.lte = 10000
  ];
  repeated LineItem line_items = 4
    [(buf.validate.field).repeated.min_items = 1];
}

// CEL 式によるクロスフィールド検証
message DateRange {
  option (buf.validate.message).cel = {
    id: "end_after_start",
    message: "end_date must be after start_date",
    expression: "this.end_date > this.start_date"
  };
  google.protobuf.Timestamp start_date = 1;
  google.protobuf.Timestamp end_date = 2;
}
```

**主な検証ルール**:

| 型 | ルール例 | 説明 |
|----|---------|------|
| string | `.string.uuid = true` | UUID 形式 |
| string | `.string.email = true` | メールアドレス形式 |
| string | `.string.min_len = 1` | 最小文字数 |
| uint32 | `.uint32.gt = 0` | 0 より大きい |
| uint32 | `.uint32.gte = 0, .lte = 150` | 範囲指定 |
| repeated | `.repeated.min_items = 1` | 最低1要素 |
| field | `.required = true` | 必須フィールド |
| message | `.cel = {expression: "..."}` | CEL 式 |
