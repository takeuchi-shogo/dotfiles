# 状況→戦略マップ

> `/improve` が候補を提案し、人間が承認して追記する。最大 50 エントリ。
> AutoEvolve 改善対象: YES (append-only)

## マップ

| 状況 | 推奨戦略 | 根拠 | 学習元 |
|------|----------|------|--------|
| 10ファイル未満の変更調査 | Grep 1回 → ヒットファイルのみ Read（個別ディレクトリ走査しない） | Read 爆発防止。不要なファイル読み込みでコンテキスト消費 | absorb skill |
| 複数の独立したコード変更 | worktree で隔離して並列実行 | 共有状態の破損防止 | workflow-guide |
| hook regex で日本語混在テキスト | `\b` ではなく `(?=[^a-zA-Z0-9]\|$)` を使用 | `\b` は日本語で誤動作する | lessons-learned |
| 大規模ファイル（200行超）の部分変更 | offset/limit で対象範囲のみ Read してから Edit | 全体読み込みはコンテキスト浪費 | workflow-guide |
| エラー発生後のデバッグ | 生のエラーログ・スタックトレースを直接分析。ユーザーの解釈より生データ優先 | 解釈バイアス回避 | core-principles |
| 同じ修正を2回以上説明 | spec/reference に codify する | セッション横断の知識ロスを防止 | core-principles |
| M/L 規模タスクの開始 | EnterPlanMode でプラン策定してから実装 | 手戻り防止。Plan → Implement の分離 | workflow-guide |
| CI/テスト失敗時の修正 | 根本原因を特定してから修正。`--no-verify` は絶対に使わない | hook 体系の無効化防止 | lessons-learned |
| 反復的な仮説検証・改善ループ | 1仮説1パッチ1実行 + Promotion ゲート + Wave 並列。`references/experiment-discipline.md` に従う | 複数変更の同時投入は因果帰属不能。worktree 隔離で並列実行 | autoresearch-lab |
