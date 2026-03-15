# ADR-0001: Hook 4 層分離

## Status

Accepted

## Context

Claude Code の hook スクリプトが増加し、責務の混在が問題になった。
フォーマッター、ポリシーチェック、ライフサイクル管理、学習収集が
単一ディレクトリに混在すると、変更影響の把握が困難になる。

## Decision

hook スクリプトを 4 層に分離する:
- `scripts/runtime/` — セッションライフサイクル、フォーマッター（PostToolUse 高速パス）
- `scripts/policy/` — 品質ゲート、エラー検出、委譲判断（ブロッキング可）
- `scripts/lifecycle/` — プラン管理、メモリアーカイブ（非ブロッキング）
- `scripts/learner/` — イベント収集、学習永続化（Stop/SessionEnd）
- `scripts/lib/` — 共有ユーティリティ

## Consequences

### Positive
- 変更影響が層内に閉じる（runtime の変更が learner に影響しない）
- 新規 hook 追加時の配置が明確
- テストが層単位で独立実行可能

### Negative
- lib/ の共有モジュールが間接依存を生む
- ディレクトリ構造の学習コスト

### Neutral
- settings.json の hook 定義で各スクリプトのパスを明示する必要がある
