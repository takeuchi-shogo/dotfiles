# Boundary Pattern Catalog

edge-case-analysis スキルが参照するパターンカタログ。
Claude は必要に応じてこのファイルを Read する。

## 数値境界

| パターン | チェック項目 |
|---------|------------|
| ゼロ値 | 0, 0.0, -0 |
| 最大/最小値 | INT_MAX, INT_MIN, MAX_SAFE_INTEGER |
| オーバーフロー | 加算・乗算の結果が型の範囲を超える |
| 浮動小数点精度 | 0.1 + 0.2 !== 0.3 |

## 文字列境界

| パターン | チェック項目 |
|---------|------------|
| 空文字列 | "", null, undefined の区別 |
| Unicode | 絵文字, ZWJ シーケンス, RTL テキスト |
| 超長文字列 | バッファ制限, 表示崩れ |
| 特殊文字 | SQL/HTML/Shell メタ文字 |

## コレクション境界

| パターン | チェック項目 |
|---------|------------|
| 空コレクション | [], {}, nil map |
| 単一要素 | off-by-one の温床 |
| 大量要素 | メモリ, ページネーション |
| 重複要素 | Set vs List の挙動差 |

## 時間・状態境界

| パターン | チェック項目 |
|---------|------------|
| タイムゾーン | UTC ↔ JST 変換, DST |
| 日付境界 | 月末, 閏年, 年末 |
| 同時実行 | race condition, deadlock |
| 状態遷移 | 無効な遷移パス, 再入可能性 |

## nil/null パス

| パターン | チェック項目 |
|---------|------------|
| Optional unwrap | nil dereference |
| Map lookup miss | zero value vs not found |
| JSON null | null vs missing key vs "" |
| DB NULL | NULL vs empty string vs default |
