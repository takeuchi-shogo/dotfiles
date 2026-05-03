---
status: reference
last_reviewed: 2026-04-23
---

# Skill Design Patterns

5つの設計パターンで SKILL.md の内部ロジックを構造化する。

## Pattern Catalog

### Tool Wrapper

**Purpose**: ライブラリ/フレームワークの規約をオンデマンドでロードし適用する
**When to use**: 特定技術のベストプラクティスを適用したい時
**Key structure**:
1. キーワードトリガーで発火
2. `references/` から規約ドキュメントを読み込む
3. コードに対して規約を適用
**Required elements**: `references/` 内のドキュメント、description 内のキーワードトリガー
**Gate conditions**: なし（単純適用）
**Composability**: Generator/Reviewer の前段として使用可能

### Generator

**Purpose**: テンプレートから定型出力を一貫して生成する
**When to use**: 毎回同じ構造の出力が必要な時
**Key structure**:
1. テンプレート (`assets/` or inline) をロード
2. スタイルガイド (`references/`) をロード
3. ユーザーから変数を収集
4. テンプレートを充填して出力
**Required elements**: テンプレート (assets/ or inline)、出力フォーマット定義
**Gate conditions**: なし
**Composability**: Inversion の後段として変数収集後に実行可能

### Reviewer

**Purpose**: チェックリストに基づいてコードや成果物を体系的に評価する
**When to use**: 品質基準に照らした評価が必要な時
**Key structure**:
1. `references/` からチェックリストをロード
2. 対象を各項目に照らして検査
3. 発見を severity (error/warning/info) で分類
4. スコアと推奨事項を出力
**Required elements**: `references/` 内のチェックリスト、severity 分類
**Gate conditions**: なし
**Composability**: Pipeline の最終ステップとして、Tool Wrapper の後段として使用可能

### Inversion

**Purpose**: エージェントがユーザーにインタビューしてから行動する
**When to use**: 要件が曖昧で、先に収集が必要な時
**Key structure**:
1. フェーズを定義（Phase 1: 問題発見, Phase 2: 制約, Phase 3: 合成）
2. 各フェーズで1問ずつ質問、回答を待つ
3. 全フェーズ完了までゲート ("DO NOT proceed until all phases are complete")
4. 収集結果を合成して出力
**Required elements**: フェーズ分け、ゲート条件
**Gate conditions**: "DO NOT start building/designing until all phases are complete"
**Composability**: Generator の前段として使用可能（要件収集 → テンプレート出力）

### Pipeline

**Purpose**: 厳密な順序の多段ワークフローを保証する
**When to use**: ステップの省略や順序変更が許されない時
**Key structure**:
1. 番号付きステップ (`## Step N — 名前`)
2. 各ステップにゲート条件（ユーザー承認、テスト通過等）
3. ゲート未通過で次ステップへの進行を明示的に禁止
4. 失敗時の挙動を明記
**Required elements**: 番号付きステップ、各ステップのゲート条件、失敗時の挙動
**Gate conditions**: "Do NOT proceed to Step N+1 until [condition]"
**Composability**: 最終ステップに Reviewer を含めることが多い

## Decision Tree

スキルの主目的から最適パターンを選ぶ:

```
スキルの主目的は？
├─ 知識を適用 → Tool Wrapper
├─ 定型出力を生成 → Generator
├─ コードや成果物を評価 → Reviewer
├─ 要件を収集してから行動 → Inversion
└─ 複数ステップを順序保証 → Pipeline
```

**複合ケースの判定**: 主目的で1つ選び、副次的な機能を `+` で合成する。
例: 要件収集(主) + テンプレート出力(副) → `inversion+generator`

## Composition Patterns

パターンは合成可能。よくある組み合わせ:

- **Inversion + Generator**: 要件収集 → テンプレート出力 (例: /spec, /timekeeper)
- **Pipeline + Reviewer**: 多段処理の最終ステップで品質チェック (例: /audit)
- **Tool Wrapper + Reviewer**: 規約ロード → 規約に基づくレビュー (例: /review + review-checklists/)
- **Pipeline + Inversion**: 多段処理の初期ステップでインタビュー (例: /skill-creator, /init-project)

## Structure Quality Checklist

パターン別の必須要素。skill-creator の Stage 6 (Test) で検証に使用:

| Pattern | Required Elements |
|---------|-------------------|
| Tool Wrapper | `references/` 内のドキュメント、キーワードトリガー |
| Generator | テンプレート (`assets/` or inline)、出力フォーマット定義 |
| Reviewer | `references/` 内のチェックリスト、severity 分類 |
| Inversion | フェーズ分け、ゲート条件 ("DO NOT proceed until...") |
| Pipeline | 番号付きステップ、各ステップのゲート条件、失敗時の挙動 |

## Design Principles

### Implicit Assumption Pinning

**問題**: 反復タスクを都度自由文で指示すると、暗黙の前提（環境設定、出力フォーマット、前処理手順）がセッションごとにドリフトする。

**解決**: skill 化して前提を SKILL.md 内に固定する。

**skill 化の判断基準**:
- 同じタスクを **3回以上** 自由文で指示した
- 指示のたびに「前回と同じく」「いつものように」等の前提参照が発生する
- 実行結果のフォーマットや手順に **ブレ** が観測された

**固定すべき前提の例**:
- 環境（仮想環境のパス、Docker設定、API認証）
- 出力フォーマット（ログの構造、ファイル名規則）
- 前処理/後処理の手順
- 成功/失敗の判定基準

> 出典: Kaggle ヴェスヴィオ・チャレンジ金メダル事例（Recruit Data Blog, 2026-03）。
> submit 監視、コードレビュー、ディスカッション整形、notebook DL の4タスクを skill 化し、
> 都度指示の「暗黙の前提ズレ」を解消。

## Frontmatter Schema

SKILL.md の frontmatter に追加:

```yaml
metadata:
  pattern: pipeline                 # tool-wrapper | generator | reviewer | inversion | pipeline
  # pattern: inversion+generator    # 合成の場合は + で連結（主目的を先に）
  composable-with: [reviewer]       # optional: 組み合わせ可能なパターン
```
