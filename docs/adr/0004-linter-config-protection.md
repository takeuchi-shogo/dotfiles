# ADR-0004: リンター設定保護

## Status

Accepted

## Context

AI エージェントは lint エラーを解消するために、コードではなく
リンター設定を変更する傾向がある（ルールの無効化、閾値の緩和）。
これにより品質ゲートが形骸化する。

Ref: Harness Engineering Best Practices 2026 — アンチパターン #2

## Decision

PreToolUse hook（protect-linter-config.py）でリンター設定ファイルの
編集をブロックする。対象:
- 純粋設定: .eslintrc*, biome.json, .prettierrc*, .oxlintrc.json, .golangci.yml 等
- 混合ファイル: pyproject.toml の [tool.ruff] セクション、Cargo.toml の [lints] セクション

原則: **Fix code, not rules.**

## Consequences

### Positive
- リンター設定の一貫性を保証
- 品質ゲートの形骸化を防止
- エラーは常にコード側で解決される

### Negative
- 正当な設定変更も一旦ブロックされる（人間が手動で変更する必要あり）
- 混合ファイルのセクション検出は完全ではない
