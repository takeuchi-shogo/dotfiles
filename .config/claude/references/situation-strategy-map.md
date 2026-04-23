---
status: reference
last_reviewed: 2026-04-23
---

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
| 難易度の高いタスク（推定成功率 < 0.5） | best-of-n の N を増やす（N≥3）、VS-Multi で候補生成、敗者パターンも学習対象にする | SSD: Hard 問題で +15.3pp / Pass@5 改善が Pass@1 より大（+18.1pp vs +12.9pp）。高探索度のリターンが難問ほど大きい | SSD (arXiv:2604.01193) |
| タスク内に精度重視ステップと探索重視ステップが混在 | Lock（構文・型・パス等の決定的ステップ）は単一エージェントで精密実行、Fork（設計・アルゴリズム選択）は `/debate` や VS-CoT で探索してから決定 | SSD の Precision-Exploration Conflict: 全ステップに同一戦略を適用すると妥協が生じる。ステップの性質に応じて戦略を切り替える | SSD (arXiv:2604.01193) |
| 新プロジェクトでの改善サイクル立ち上げ | Warm-starts: 他リポ/他プロジェクトの成功パターンを situation-strategy-map フォーマットで取り込む。`/init-project` 後に既存マップをシードとして注入 | ゼロからの探索は非効率。過去の経験を構造化して転用する | meta-harness |

## Warm-starts（外部経験の構造化取り込み）

新プロジェクトや新ドメインで改善サイクルを立ち上げる際、既存の経験を取り込むことで探索を高速化する。

### 取り込みフォーマット

外部コーパス（他リポのマップ、成功ハーネスのパターン）は以下の形式に変換してから追加する:

```
| 状況 | 推奨戦略 | 根拠 | 学習元 |
|------|----------|------|--------|
| {コンテキスト} | {アクション} | {なぜ有効か} | {出典: リポ名/記事/論文} |
```

### 取り込みルール

- 取り込み前に現プロジェクトとの **前提条件の一致** を確認する（言語、フレームワーク、チーム規模）
- 前提が異なるエントリには `[要検証]` タグを付与し、実際に有効かを確認してからタグを外す
- 最大 50 エントリの制約は warm-starts 分も含む

> 根拠: Meta-Harness (Lee+ 2026) 実装 Tips — "If offline experience exists, convert it into the same directory structure to warm-start exploration"
