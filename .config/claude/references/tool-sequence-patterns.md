# ツールシーケンスパターン

> `/analyze-tacit-knowledge` が抽出し、5 回以上出現パターンのみ記録する。
> `/improve` が定期的に更新候補を提案する。
> AutoEvolve 改善対象: YES (append-only)

## パターン

| パターン名 | シーケンス | 用途 | 出現頻度 |
|-----------|-----------|------|----------|
| search-then-edit | Grep → Read → Edit | 既知のパターン修正。検索→確認→編集の基本フロー | 高 |
| parallel-search | Grep + Grep (並列) → Read | 複数キーワードの同時検索で効率化 | 中 |
| explore-then-plan | Glob → Read(複数) → EnterPlanMode | 未知の領域を調査してからプランニング | 中 |
| read-then-write | Read → Write | 新規ファイル作成。既存ファイルの構造を参考にしてから書く | 中 |
| verify-after-edit | Edit → Bash(test/lint) → Read(結果確認) | 変更後の即時検証ループ | 高 |
