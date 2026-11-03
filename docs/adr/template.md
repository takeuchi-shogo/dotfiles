# ADR-XXXX: [タイトル]

## Status

Accepted | Superseded by ADR-XXXX | Deprecated

## Context

[なぜこの決定が必要だったか]

## Decision

[何を決定したか]

## Rejected Alternatives

採用しなかった選択肢と却下理由。ここが空だと、後から「なぜこれ以外を選ばなかったか」を復元できない。

| 代替案 | 却下理由 | 再検討の条件 |
|---|---|---|
| [案] | [理由] | [この状況になれば再検討する] |

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

## 経過

決定後に何がわかったか、どうなったかを定期的に追記する。

| 日時 | 状況（期待通り / 想定と違ってきた / 課題が出ている） | 観測（ログやメトリクスなど） | 評価（続ける / 見直す / 条件付けで様子見） |
|---|---|---|---|
| | | | |
