---
name: grill-interview
description: >
  プラン・設計を容赦なくストレステストする事前インタビュー。決定木を1分岐ずつ走破し、
  各質問にAI推奨回答を添えてユーザーの意思決定を加速する。
  Triggers: 'grill', 'ストレステスト', '詰めて', '穴がないか', 'grill me', 'stress test my plan',
  '設計を詰めたい', 'プランに穴がないか'.
  Do NOT use for: spec 策定インタビュー（use /interview）、実装済みコードの防御的質問（use /challenge grill）、
  思考の壁打ち（use /think）。
origin: self
allowed-tools: Read, Glob, Grep, AskUserQuestion
disable-model-invocation: true
metadata:
  pattern: inversion
  origin: mattpocock/skills/grill-me
---

# /grill-interview — プラン・設計のストレステスト

プランや設計の全側面を容赦なく問い詰め、共有理解に到達するまで質問を続ける。

**核心**: 「実装前に穴を潰す」。コードを書く前が最もコストが安い。

## 対象

- 実装前のプラン・設計・アーキテクチャ
- spec ドラフト、PRD、技術選定
- ワークフロー変更、ハーネス改修の方針

## Protocol

### Step 1: 対象の把握

引数またはコンテキストからプラン・設計を特定する。

- 引数がファイルパス → Read で読み込む
- 引数がテキスト → そのまま使用
- 引数なし → `AskUserQuestion` で「何をストレステストしますか？」

コードベースに関連するファイルがあれば Grep/Glob で探索し、現状を把握する。

### Step 2: 決定木の構築

プランを分析し、意思決定が必要なポイント（分岐）を洗い出す。
分岐間の依存関係を特定し、依存元から順に解決する順序を決める。

### Step 3: 逐次質問

`AskUserQuestion` で **1問ずつ** 質問する。以下のルールに従う:

1. **AI推奨回答を添える** — 「私の推奨: ○○。理由: △△」の形式で、質問と一緒に提示する
2. **コードベースで答えられるなら先に自分で調べる** — ユーザーに聞く前に Grep/Read で確認
3. **依存関係順に進む** — 後続の決定に影響する分岐から先に解決
4. **回答を踏まえて次の質問を調整** — 回答で新たな分岐が生まれたら追加する

質問の観点:
- なぜこのアプローチか？ 代替案との比較は？
- この決定が壊しうるシナリオは？
- スケーラビリティ・メンテナビリティへの影響は？
- 暗黙の前提は何か？ その前提が崩れたら？
- エッジケース・異常系の扱いは？

### Step 4: 共有理解の確認

全分岐を走破したら、決定事項を箇条書きでまとめてユーザーに提示する。

```
## 決定事項
- [分岐1]: ○○ を採用（理由: △△）
- [分岐2]: ○○ を採用（理由: △△）
- ...

## 未解決・要検討
- [あれば]
```

## Usage

```
/grill-interview docs/plans/my-plan.md    # プランファイルを対象に
/grill-interview                           # 対象を聞く
/grill-interview "Redis をキャッシュに使う設計"  # テキストで直接
```

## Chaining

- **ストレステスト後に仕様化**: `/grill-interview` → `/spec`
- **ストレステスト後に実装**: `/grill-interview` → `/rpi`
- **実装後の防御的レビュー**: `/challenge grill`（別スキル）
