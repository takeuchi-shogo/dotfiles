# ADR-XXXX: [タイトル]

## Status

Accepted | Superseded by ADR-XXXX | Deprecated

## Context

[なぜこの決定が必要だったか]

## Decision

[何を決定したか]

## Verification

ADR↔実装の drift を AI レビュー / grep で機械照合できるようにする（任意だが、logic / security / API 境界を縛る決定では推奨）。文章化された決定ほど AI が機械的に整合チェックでき、人間が見るべき範囲が減る。

- **Affected paths**: [この決定が縛るファイル/ディレクトリの glob。例: `internal/service/**`]
- **Invariants**: [コードが満たすべき不変条件。例: Service 層は必ず tenant_id を引数で受け取る]
- **Verification command**: [整合を確認するコマンド + 期待結果。例: `grep -rL "tenant_id" internal/service/`（出力が空なら OK = 全ファイルが invariant を満たす）]

## Consequences

### Positive
- [利点]

### Negative
- [トレードオフ]

### Neutral
- [その他の影響]
