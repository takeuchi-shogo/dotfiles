---
name: absorb
description: "外部記事・論文・リポジトリの知見を現在のセットアップに統合する。ギャップ分析→選別→統合プラン生成。記事を貼って「活かしたい」「考えて」と言われたときに使用。"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion, WebFetch
user-invocable: true
metadata:
  pattern: pipeline
---

# /absorb — 外部知見の統合

外部の記事・論文・リポジトリの知見を分析し、現在のセットアップに取り込む統合プランを生成する。

## Trigger

- 記事 URL やテキストを貼って「活かしたい」「考えて」「取り込みたい」と言われたとき
- 論文やリポジトリを分析して改善点を抽出したいとき
- 他人の Claude Code 設定やワークフローを参考にしたいとき

## Workflow

```
/absorb {URL or テキスト}
  Phase 1: Extract    → 記事の要点を構造化抽出
  Phase 2: Analyze    → 現状とのギャップ分析
  Phase 3: Triage     → ユーザーと「何を取り込むか」を選別
  Phase 4: Plan       → 統合プラン生成
  Phase 5: Handoff    → 実行（同一セッション or 新セッション）
```

## Phase 1: Extract（要点抽出）

1. インプットの取得:
   - URL → WebFetch で取得
   - 貼り付けテキスト → そのまま使用
   - リポジトリ → 主要ファイルを読む
2. 構造化抽出:
   - **主張**: 記事が提唱していること（1-3文）
   - **手法**: 具体的なテクニック・パターン（箇条書き）
   - **根拠**: なぜそれが有効か（データ、事例）
   - **前提条件**: どんなコンテキストで有効か

出力は内部用。ユーザーには要約のみ表示する。

## Phase 2: Analyze（ギャップ分析）

現在のセットアップと記事の知見を自動比較する。

1. 記事の手法に関連するファイルを特定:
   - `Glob` と `Grep` で関連ファイルを探す
   - skills/, scripts/, rules/, references/, agents/ を横断
   - CLAUDE.md, MEMORY.md も確認
2. 各手法について判定:

| 判定 | 意味 |
|------|------|
| **Already** | 既に実装済み（既存ファイルを特定） |
| **Partial** | 部分的に実装。差分を明示 |
| **Gap** | 未実装。取り込み価値あり |
| **N/A** | 当セットアップには不要（理由を添える） |

3. ユーザーに分析結果をテーブルで提示

## Phase 3: Triage（選別）

`AskUserQuestion` で取り込み対象を選別する。

質問形式:
```
以下の Gap/Partial 項目のうち、取り込みたいものを選んでください:

1. [Gap] ○○パターンの追加 — 効果: △△
2. [Partial] ○○の強化 — 現状: XX、記事推奨: YY
3. [Gap] ○○の導入 — 効果: △△

全部 / 番号選択 / なし（分析結果だけ保存）
```

- 「全部」を選ばれた場合、優先順位を確認
- 「なし」の場合は Phase 4 をスキップし、分析レポートだけ保存

## Phase 4: Plan（統合プラン生成）

選別された項目から統合プランを生成する。

### プランの成果物は記事次第

固定の出力先はない。記事の内容に応じて適切な成果物を提案する:

| 記事の種類 | 主な成果物例 |
|-----------|-------------|
| ベストプラクティス | rules/ 追加、references/ 追加、CLAUDE.md 修正 |
| 論文・研究 | 新スキル作成、エージェント追加、設計 spec |
| ツール・ライブラリ | scripts/ 追加、スキル改善、hook 追加 |
| セキュリティ | policy hook 追加、deny rules 追加 |
| ワークフロー | スキル修正、コマンド追加、settings.json 変更 |

### プラン生成ルール

1. 各タスクは具体的なファイルパスと変更内容を含む
2. タスク間の依存関係を明示
3. 規模を推定: S（1ファイル）/ M（2-5ファイル）/ L（6ファイル超）
4. L 規模の場合は `docs/plans/` にプランを保存

### 分析レポートの保存

`docs/research/YYYY-MM-DD-{slug}-analysis.md` に保存:

```markdown
---
source: {URL or title}
date: YYYY-MM-DD
status: analyzed | integrated | skipped
---

## Source Summary
{Phase 1 の構造化抽出}

## Gap Analysis
{Phase 2 のテーブル}

## Integration Decisions
{Phase 3 で選択/スキップした項目と理由}

## Plan
{Phase 4 のタスクリスト。なしの場合は省略}
```

### MEMORY.md への記録

MEMORY.md にはポインタ + 1行サマリのみ追記する。詳細は分析レポートに任せる。
既存のメモリエントリと重複する場合は更新で対応し、新規追加しない。

## Phase 5: Handoff（実行判断）

プランの規模に応じて実行方法を提案:

| 規模 | 提案 |
|------|------|
| S | その場で実行 |
| M | ユーザーに確認後、同一セッションで実行 |
| L | プラン保存 → 新セッションで `/rpi` or 手動実行 |

## Usage

```
/absorb https://example.com/article       # URL から
/absorb                                    # テキスト貼り付け後に実行
/absorb docs/research/existing-report.md   # 既存レポートの再分析
```

## Anti-Patterns

| NG | 理由 |
|----|------|
| ギャップ分析せずに全部取り込む | 既存と重複したり、不要な複雑さを招く |
| MEMORY.md に詳細を書く | ポインタのみ。詳細は分析レポートに |
| 分析せずにプランだけ作る | Already/N/A を見落とし無駄な作業が発生 |
| 記事の主張を無批判に受け入れる | 前提条件が合わない手法を導入してしまう |
| 1記事から10以上の変更を出す | 消化不良になる。優先度上位3-5個に絞る |

## Chaining

- **分析レポートから実装**: `/rpi docs/research/YYYY-MM-DD-{slug}-analysis.md`
- **大規模統合**: `/epd` の Phase 1 (Spec) に分析レポートを入力
- **深掘り調査**: 記事が不十分なら `/research` で補完調査
