# Fix Routing Guide — レビューコメント修正の振り分け

レビューコメント（GitHub PR コメント、Codex レビュー指摘、ユーザー補完コメント）を受け取った後、
Claude Code と Codex のどちらに修正させるかを判断するガイド。

## ルーティングテーブル

| コメント種類 | 振り先 | reasoning_effort | 理由 |
|-------------|--------|-----------------|------|
| バグ修正・ロジック変更 | Claude Code | — | ファイル編集が必要。Claude が直接修正可能 |
| 命名・フォーマット | Claude Code | — | 単純な文字列置換。AI 推論不要 |
| ドキュメント不足 | Claude Code | — | ファイル追加/編集で対応 |
| テスト不足 | Claude Code | — | テストコード生成は Claude で十分 |
| 設計上の懸念・アーキ指摘 | Codex → Claude Code | high | まず Codex で設計代替案を分析、次に Claude が実装 |
| セキュリティ懸念 | Codex → Claude Code | xhigh | Codex で脆弱性の深掘り分析、Claude が修正適用 |
| パフォーマンス指摘 | Codex → Claude Code | high | Codex でボトルネック分析、Claude が最適化実装 |
| 根本的な設計変更要求 | Codex (Plan) → Claude Code | xhigh | Codex で新設計を Plan、Claude が実装 |

## 判断フローチャート

1. コメントが「ファイル編集だけで解決する」か？
   - Yes → Claude Code に直接修正させる
   - No → 2 へ
2. 「深い分析・推論」が必要か？
   - Yes → Codex で分析 → Claude Code で実装
   - No → Claude Code に直接修正させる
3. 「設計判断」が必要か？
   - Yes → Codex で代替案分析 → ユーザー判断 → Claude Code で実装
   - No → Claude Code に直接修正させる

## Codex 分析 → Claude Code 実装のパターン

Codex に振る場合の典型的なプロンプト構成:

### セキュリティ懸念の場合
Codex (read-only, xhigh):
  "Analyze this security concern: {comment}.
   Review the affected code at {file}:{line}.
   Recommend specific fixes with rationale."
→ 結果を Claude Code に渡して実装

### 設計指摘の場合
Codex (read-only, high):
  "This design concern was raised: {comment}.
   Analyze the current architecture at {files}.
   Propose 2-3 alternative approaches with trade-offs."
→ ユーザーが選択 → Claude Code が実装

## 既存ルールとの関係

- `rules/codex-delegation.md` のタスク性質別ルーティングと整合
- `references/reviewer-capability-scores.md` のスコアと連携可能
- `/github-pr` の review-response.md と組み合わせて使用

## Anti-Patterns

| NG | 理由 |
|----|------|
| 全コメントを Claude Code に投げる | セキュリティ・設計指摘は Codex の深い推論が必要 |
| 全コメントを Codex に投げる | 単純修正に Codex はオーバーヘッド大 |
| ユーザー判断なしに設計変更する | 設計判断はユーザーが行うべき |
| 1コメントに複数ステップの修正 | 修正は1コメント=1修正で追跡可能に |
