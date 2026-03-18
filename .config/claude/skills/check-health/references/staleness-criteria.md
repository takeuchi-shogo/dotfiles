# Staleness Criteria — 鮮度判定基準

## Document Staleness

| 閾値 | 判定 | アクション |
|------|------|-----------|
| 0-30日 | OK | なし |
| 31-60日 | STALE | レビュー推奨 |
| 61日以上 | CRITICAL | 即座に更新 or アーカイブ |

## Code-Document Drift

| 条件 | 判定 |
|------|------|
| コード変更後7日以内にドキュメント更新 | OK |
| コード変更後7-14日 | WARNING |
| コード変更後14日以上 | DRIFT |

## Skill Benchmark Staleness

| 閾値 | 判定 |
|------|------|
| 0-30日 | OK |
| 31-60日 | STALE → `/skill-audit` 推奨 |
| 未実施 | NEVER → `/skill-audit` 必須 |

## Reference Integrity

参照先ファイルが存在しない場合は **即 BROKEN** と判定。
ファイルが移動された場合は **MOVED** と判定し、新パスを提示。
