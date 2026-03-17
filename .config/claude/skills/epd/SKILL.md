---
name: epd
description: "EPD統合ワークフロー。Spec → Spike → Validate → Implement → Review の一連のフローを実行。Harrison Chase の Builder or Reviewer パラダイムに基づく。大きな機能開発で使用。"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, EnterWorktree, EnterPlanMode, ExitPlanMode
user-invocable: true
metadata:
  pattern: pipeline
---

# EPD: Engineering, Product & Design Workflow

アイデアから本番コードまでの一連のフローを EPD（Engineering, Product, Design）の3軸で実行する。

## Philosophy

Harrison Chase "How Coding Agents Are Reshaping EPD" に基づく:

- 実装コストはほぼゼロ → まずプロトタイプで検証
- ボトルネックはレビュー → 3軸で品質担保
- PRD は構造化プロンプト → agent にそのまま渡せる仕様書

## Full Workflow

```
/epd {idea}
  Phase 1: Spec       → /spec で Prompt-as-PRD を生成
  Phase 2: Spike      → /spike でプロトタイプ → /validate で検証
  Phase 3: Refine     → Spike 結果に基づき Spec を改善（2-3回反復可）
  Phase 4: Decide     → proceed / pivot / abandon
  Phase 5: Build      → /rpi で正式実装
  Phase 6: Review     → /review で3軸レビュー（eng + product + design）
  Phase 7: Ship       → /commit
```

## Phase 1: Spec (AI-DLC Inception)

spec スキルを呼び出して Prompt-as-PRD を生成する。
AI-DLC の Inception フェーズの要素を取り込み、構造化された要件定義を行う。

### 1.1 Intent 分析

ユーザーの意図を明確化する:

- アイデアを1文の Intent（意図宣言）に要約
- Greenfield（新規）か Brownfield（既存変更）かを判定
- Brownfield の場合: `references/brownfield-analysis-template.md` で既存コード分析

### 1.2 要件の構造化

`rules/common/overconfidence-prevention.md` の原則に従い、曖昧さを排除:

- 不明点は推測せず質問する
- 非機能要件（パフォーマンス、セキュリティ）を確認
- スコープ外を明示する

### 1.3 Deep Interview（L 規模推奨）

L 規模のプロジェクトでは、spec スキルの Deep Interview Protocol を使用して要件を深掘りする。

- AskUserQuestionTool で 20-40+ 問の体系的なインタビュー
- 技術実装、UI/UX、トレードオフ、エッジケース等を網羅
- `/interview` コマンドでも起動可能

**注意**: Deep Interview はコンテキストを大量に消費する。L 規模では Interview → spec 保存 → **新セッションで実行** を推奨。

### 1.4 PRD 生成

- `docs/specs/{feature}.prompt.md` に保存
- acceptance criteria を必ず含める
- AI-DLC 形式: 質問は選択肢を提示して聞く（オープンエンドより効率的）

## Phase 2: Spike

spike スキルを呼び出してプロトタイプを作成・検証する。

- worktree で隔離
- 最小実装 → validate で検証
- spike report を出力

## Phase 3: Refine (Inception Refining)

Spike の検証結果を Spec にフィードバックし、仕様を洗練する。
Gaudiy の α/β Construction パターンに基づく反復ループ。

### 反復判定

Spike 結果に以下が含まれる場合、Spec を修正して Phase 2 に戻る:

- acceptance criteria の不足や曖昧さが判明した場合
- 技術的制約により spec の変更が必要な場合
- ユーザーから追加要件や変更要求があった場合

### 反復の上限

- **最大3回**の反復（α → α' → β）
- 3回で収束しない場合は Decide フェーズで判断

### 反復時のアクション

1. Spike Report の「判明した課題」セクションを確認
2. `docs/specs/{feature}.prompt.md` の該当箇所を修正
3. 修正した spec で再度 `/spike` を実行
4. 修正履歴を spec ファイルの Changelog セクションに追記

## Phase 4: Decide

spike report に基づいてユーザーに判断を求める:

- **Proceed**: Phase 5 に進む
- **Pivot**: spec を修正して Phase 2 に戻る
- **Abandon**: ワークフロー終了

## Phase 5: Build

rpi スキル（Research → Plan → Implement）を呼び出して正式実装する。

- spike のコードは参考として参照可能
- テスト・lint・コード品質は通常基準で実施
- spec の Prompt セクションを実装指示として活用

## Phase 6: Review

review スキルを呼び出して3軸レビューを実行する。

- **Engineering**: code-reviewer + 言語専門 + codex-reviewer 等（従来通り）
- **Product**: product-reviewer（spec file 存在時に自動追加）
- **Design**: design-reviewer（UI 変更時に自動追加）

レビュー指摘がある場合は修正 → 再レビュー

## Phase 7: Ship

commit コマンドでコミットする。

## Shortcuts

全フェーズを実行する必要はない。状況に応じてスキップ可能:

| 状況                           | ショートカット                     |
| ------------------------------ | ---------------------------------- |
| spec が既にある                | Phase 1 をスキップ                 |
| プロトタイプ不要（確信がある） | Phase 2-3 をスキップ、直接 Phase 4 |
| 反復不要（1回の spike で十分）| Phase 3 をスキップ、直接 Phase 4 |
| 小さな変更                     | `/rpi` を直接使用（`/epd` 不要）   |
| Interview で spec を深掘りしたい | `/interview` → spec 保存 → 新セッション |

## Anti-Patterns

- spike のコードを本番に持ち込む（Phase 4 で正式実装する）
- Decide フェーズをスキップする（ユーザー判断は必須）
- spec なしで Build に進む（最低限 acceptance criteria が必要）
- 要件が曖昧なまま spike に入る（Phase 1 で明確化する）
- 反復（Phase 3）を面倒がってスキップする（手戻りコストの方が高い）

## Artifact Generation

L 規模の EPD ワークフローでは、構造化アーティファクトを生成する。
AI-DLC の `aidlc-docs/` パターンを `docs/specs/{feature}/` に適応。

### ディレクトリ構造（L 規模）

```
docs/specs/{feature}/
├── {feature}.prompt.md      # Prompt-as-PRD（Phase 1 出力）
├── requirements.md           # 要件分析結果（Phase 1 出力、L のみ）
├── spike-report.md           # Spike 検証レポート（Phase 2 出力）
└── changelog.md              # Spec の変更履歴（Phase 3 で更新）
```

### S/M 規模

- S: アーティファクトなし（直接 `/rpi`）
- M: `docs/specs/{feature}.prompt.md` のみ（フラットファイル）

### 生成ルール

- Phase 1 完了時: `{feature}.prompt.md` を必ず生成
- Phase 2 完了時: spike-report.md を生成（Spike のサマリー + 判明した課題）
- Phase 3 の反復時: changelog.md に変更履歴を追記
- L 規模のみ: requirements.md に構造化された要件を出力
