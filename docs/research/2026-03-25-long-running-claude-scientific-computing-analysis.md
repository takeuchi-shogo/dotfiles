---
source: https://www.anthropic.com/research/long-running-Claude
date: 2026-03-25
status: integrated
---

## Source Summary

Anthropic 研究者による「Long-Running Claude for Scientific Computing」。AI エージェントが数日間の自律的科学計算を実行するためのアーキテクチャパターンを、微分可能ボルツマンソルバー（JAX 実装）の事例で実証。

### 主張
- モデルの長期タスク能力向上により、数日〜数週間かかる研究を数時間で自律完了できる
- CLAUDE.md + CHANGELOG.md + テストオラクル + Git の4本柱が長時間自律作業の基盤
- 「エージェントを動かさない夜は、潜在的な進捗を捨てている」

### 手法
1. **CLAUDE.md as Living Documentation** — エージェントが作業中に自身の指示を編集・更新
2. **CHANGELOG.md (Lab Notes)** — 失敗アプローチ+理由、精度テーブル、現状ステータスを記録。セッション跨ぎの dead-end 再試行を防止
3. **Test Oracle** — リファレンス実装との定量比較で進捗を測定。0.1% 精度ターゲットなど明確な成功基準
4. **Git as Coordination** — 意味のある単位ごとに commit & push。テスト通過前に commit しない
5. **Ralph Loop** — エージェントの「怠惰な停止」を防ぐ for ループ。成功基準文字列 ("DONE") + max-iterations で制御
6. **SLURM + tmux** — HPC 上での無人実行パターン

### 根拠
- 事例: 微分可能ボルツマンソルバーで CLASS リファレンスとの sub-percent agreement を数日で達成
- ただしプロダクション品質には未到達（全レジームでの精度未達）
- コミットログが「高速で超リテラルなポスドクのラボノート」のように読める

### 前提条件
- タスクが well-scoped で成功基準が明確
- 定量的な検証手段（リファレンス実装、テストスイート）が存在
- 人間の監視は occasional で十分
- 計算リソースが利用可能

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | CHANGELOG.md (失敗アプローチ付きラボノート) | **Partial** | `progress.log` + `HANDOFF.md` は存在。失敗アプローチの構造的記録が欠如 |
| 2 | テストオラクル (リファレンス実装による進捗測定) | **Partial** | `completion-gate.py` がテスト強制。定量的精度ターゲットの概念なし |
| 3 | SLURM/HPC デプロイパターン | **N/A** | ローカル macOS + cmux 環境。スコープ外 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|------------|-------------|--------|
| 1 | CLAUDE.md (Living Documentation) | Already (強化不要) | — |
| 2 | Ralph Loop (`completion-gate.py` L733-760) | 成功基準文字列判定と max-iterations が欠如 | `COMPLETION_PROMISE` + `MAX_RALPH_ITERATIONS` 追加 |
| 3 | Git 座標メカニズム (`/commit` + Lefthook) | autonomous 長時間実行で commit 間隔が開くリスク | executor-prompt に定期 commit ルール追加 |
| 4 | セッション跨ぎ自律実行 (`/autonomous`) | セッション再起動時のコンテキスト自動復元が弱い | executor-prompt に CHANGELOG.md 読み込み指示追加 |
| 5 | ハンズオフ進捗監視 (cmux-remote) | Already (強化不要) | — |
| 6 | サブエージェントスポーン (Agent tool) | Already (強化不要) | — |

## Integration Decisions

全 Gap/Partial + 全 Already (強化可能) を取り込み:

1. [Partial] 失敗アプローチ記録 → HANDOFF.md テンプレート + session-protocol.md 強化
2. [Partial] テストオラクル → plan frontmatter に `success_criteria` + completion-gate 判定ロジック
3. [強化] Ralph Loop 成功基準判定 → completion-gate.py に COMPLETION_PROMISE + MAX_RALPH_ITERATIONS
4. [強化] autonomous commit ルール → executor-prompt テンプレート更新
5. [強化] セッション再起動コンテキスト復元 → executor-prompt + session-protocol.md 更新

## Plan

### Task 1 (S): HANDOFF テンプレートに失敗アプローチセクション追加
- ファイル: `references/handoff-template.md`
- 変更: 「3. ブロッカー」の「試行した解決策」を「失敗したアプローチ（理由付き）」に拡張
- 記事の知見: "Without them, successive sessions will re-attempt the same dead ends"

### Task 2 (S): session-protocol.md に失敗アプローチ記録ルール追加
- ファイル: `references/session-protocol.md`
- 変更: State Persistence テーブルに「失敗アプローチ」の記録場所を明記
- HANDOFF.md の失敗アプローチセクションを「セッション跨ぎの必須引き継ぎ項目」に昇格

### Task 3 (M): completion-gate.py に Ralph Loop 成功基準判定追加
- ファイル: `scripts/policy/completion-gate.py`
- 変更:
  - Plan frontmatter の `success_criteria:` フィールド読み取り
  - `COMPLETION_PROMISE` 環境変数サポート（"DONE" 相当の完了宣言）
  - `MAX_RALPH_ITERATIONS` 環境変数サポート（デフォルト: 10）
  - Ralph Loop セクションに成功基準達成チェックを追加

### Task 4 (S): autonomous executor-prompt テンプレートに commit ルール + コンテキスト復元追加
- ファイル: `skills/autonomous/templates/` 内のテンプレート
- 変更:
  - 「30分ごと or 意味のある変更ごとに commit & push」ルール追加
  - 「セッション開始時に CHANGELOG.md / progress.log / HANDOFF.md を必ず読む」指示追加

### Task 5 (S): failure-taxonomy.md にエージェント怠惰停止パターン追記
- ファイル: `references/failure-taxonomy.md`
- 変更: 記事の "agentic laziness" パターンを FM-017 として追加（既存 Ralph Loop と関連付け）
