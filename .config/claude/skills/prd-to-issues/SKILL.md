---
name: prd-to-issues
description: >
  PRD（Prompt-as-PRD）を垂直スライス（Tracer Bullet）の独立 Issue 群に分解し、
  blocking 関係付きで GitHub に投稿する。並列エージェント実行の起点。
  Triggers: 'Issue 分解', 'PRD to issues', '垂直スライス', 'vertical slice',
  'タスク分解', 'PRD からタスク', 'Kanban', 'tracer bullet'.
  Do NOT use for: 単一 Issue 作成（use /create-issue）、仕様策定（use /spec）、
  実装込みフロー（use /epd）。
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
metadata:
  pattern: decomposition
  origin: mattpocock/skills/prd-to-issues + takeuchi adaptation
---

# /prd-to-issues — PRD → 垂直スライス Issue 分解

PRD を独立した垂直スライス（Tracer Bullet）に分解し、blocking 関係付きの GitHub Issue 群を生成する。

**核心**: 水平スライス（API層だけ、DB層だけ）ではなく、全レイヤーを貫く薄い垂直スライスに分解する。
unknown unknowns を早期に炙り出し、並列エージェント実行を可能にする。

## Workflow

```
/prd-to-issues {PRD path or issue URL}
  Step 1: PRD 取得     → ファイル or GitHub Issue から PRD を読み込む
  Step 2: コード探索   → 関連モジュール・依存関係を把握
  Step 3: 垂直分解     → Tracer Bullet 原則で Issue を設計
  Step 4: 確認         → ユーザーに分解案を提示
  Step 5: Issue 投稿   → gh issue create で一括投稿
```

## Step 1: PRD 取得

引数から PRD を特定する:

- ファイルパス → `Read` で読み込む（`docs/specs/*.prompt.md` が典型）
- GitHub Issue URL/番号 → `gh issue view` で取得
- 引数なし → `AskUserQuestion` で「どの PRD を分解しますか？」

## Step 2: コード探索

PRD に記載された機能領域に関連するコードを探索する:

1. PRD のユーザーストーリー / 要件からキーワードを抽出
2. `Grep` でコードベース内の関連ファイルを特定
3. 関連モジュールの依存関係・インターフェースを把握
4. **探索の目的**: 分解の粒度を決めるため。実装詳細に深入りしない

## Step 3: 垂直分解

### Tracer Bullet 原則

各 Issue は以下を満たす **垂直スライス** であること:

- **全レイヤーを貫通**: UI → API → ビジネスロジック → DB の全層を薄く通す
- **独立してデプロイ可能**: 他の Issue が未完了でも、単体で動作確認できる
- **unknown unknowns を炙り出す**: 統合リスクが高い箇所を優先的にスライスする
- **1 Issue = 1 PR**: マージ単位と一致させる

### 分解ルール

1. **最初の Issue は最もリスクの高い統合パスを選ぶ** — 技術的不確実性が最大の箇所
2. **Issue 間の blocking 関係を明示** — `blocked by #XX` で依存を記述
3. **並列実行可能な Issue を最大化** — blocking チェーンを短く保つ
4. **3-7 Issue を目安** — 少なすぎると垂直スライスにならず、多すぎると管理コストが上がる

### Issue テンプレート

各 Issue は以下の構造で記述する:

```markdown
## Summary
{このスライスが実現すること — 1-2文}

## User Story
{PRD のどのユーザーストーリーに対応するか}

## Vertical Slice
- [ ] {レイヤー1: 例 DB migration}
- [ ] {レイヤー2: 例 API endpoint}
- [ ] {レイヤー3: 例 UI component}
- [ ] {テスト: 各レイヤーの統合テスト}

## Acceptance Criteria
- {完了条件 1}
- {完了条件 2}

## Blocking
- blocked by: {なし or #XX}
- blocks: {#YY, #ZZ}
```

## Step 4: 確認

`AskUserQuestion` で分解案をユーザーに提示する:

```
## 分解案（{N} Issues）

1. [リスク高] {タイトル} — {概要}（blocking なし → 最初に着手可能）
2. {タイトル} — {概要}（blocked by #1）
3. {タイトル} — {概要}（blocking なし → #1 と並列可能）
...

この分解で進めますか？ / 調整したい点はありますか？
```

## Step 5: Issue 投稿

承認後、`gh issue create` で一括投稿する:

1. blocking 関係のない Issue から先に作成（番号を確定させるため）
2. blocking がある Issue は、依存先の番号を本文に記載して作成
3. ラベル付与: `vertical-slice`, 機能ラベル、優先度ラベル
4. 投稿完了後、Issue 一覧と blocking グラフをユーザーに提示

```
## 作成完了

| # | Issue | Blocked by | Status |
|---|-------|-----------|--------|
| 1 | #XX {タイトル} | — | 着手可能 |
| 2 | #YY {タイトル} | #XX | 待ち |
| 3 | #ZZ {タイトル} | — | 着手可能 |

並列着手可能: #XX, #ZZ
```

## Anti-Patterns

| NG | 理由 |
|----|------|
| 水平スライス（API だけ、DB だけ） | 統合リスクが後半に集中する |
| 1 Issue に全機能を詰め込む | レビュー不能、並列実行不可 |
| 10+ Issue に細分化 | 管理コストが Issue の価値を超える |
| blocking チェーンが直列 | 並列実行のメリットが消える |
| コード探索をスキップ | 既存コードとの整合性を見落とす |

## Chaining

- **前**: `/spec` → PRD 生成
- **後**: `/rpi` (個別 Issue 実装) or `/autonomous` (並列実行)
- **レビュー**: `/weekly-review` で Issue 進捗を棚卸し
