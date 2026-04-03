---
name: compile-wiki
description: >
  docs/research/ の分析レポート群を概念ベースの wiki にコンパイルする。
  レポート横断で概念を抽出・統合し、docs/wiki/concepts/ に記事を生成、INDEX.md を自動更新する。
  Karpathy "LLM Knowledge Bases" アプローチに基づくナレッジベースパイプライン。
  Triggers: 'wiki コンパイル', 'compile-wiki', 'ナレッジベース', 'knowledge base', '概念抽出', 'wiki 更新', 'wiki 生成'.
  Do NOT use for: 単一記事の要約（直接回答で十分）、外部記事の統合（use /absorb）、Obsidian ナレッジ管理（use /obsidian-knowledge）。
allowed-tools: Read, Write, Edit, Bash(ls:*), Bash(wc:*), Bash(git diff:*), Glob, Grep, Agent, AskUserQuestion
argument-hint: compile | update | index
metadata:
  pattern: pipeline
---

# /compile-wiki — Research Wiki Compiler

docs/research/ の 130+ 分析レポートを概念ベースの wiki にコンパイルする。

## サブコマンド

| コマンド | 説明 |
|---------|------|
| `compile` (デフォルト) | 全件スキャン → 概念抽出 → 記事生成 → INDEX 生成 |
| `update` | git diff ベースの差分更新（変更/追加レポートのみ再処理） |
| `index` | INDEX.md のみ再生成（概念記事は触らない） |

## Phase 1: Scan & Extract

### 1.1 レポート一覧取得

```
Glob: docs/research/*.md
```

全件をリスト化し、総数をユーザーに報告する。
(`*-analysis.md` だけでなく `*-deep-survey.md`, `*-investigation.md` 等も含む)

`update` サブコマンドの場合:
```bash
# docs/wiki/INDEX.md の Last compiled 日付を基準にする（なければ全件）
git log --since="$(grep 'Last compiled' docs/wiki/INDEX.md | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' || echo '2020-01-01')" --name-only --pretty=format: -- docs/research/*.md | sort -u
```
変更/追加されたレポートのみを対象とする。変更がなければ「更新対象なし」で終了。

### 1.2 メタデータ抽出

Explore エージェントを並列起動し、各レポートからメタデータを抽出する。
1エージェントあたり最大 30 ファイルをバッチ処理（130 ファイルなら 5 エージェント）。

各レポートから抽出する情報:
- **title**: レポートのタイトル（H1 or frontmatter の source）
- **date**: 分析日（ファイル名 or frontmatter）
- **status**: integrated / analyzed / planned（frontmatter、なければ "unknown"）
- **topics**: トピック分類 1-3 個（`references/topic-taxonomy.md` に従う）
- **key_concepts**: キー概念リスト（3-8 個、名詞句で統一）
- **one_line_summary**: 1行サマリ（50文字以内）

### 1.3 概念マップ構築

抽出結果を集約し、概念マップを構築する:
1. 全レポートの key_concepts をフラット化
2. 同義語・類似概念をグルーピング（例: "サブエージェント" と "sub-agent" は同一）
3. 各概念に関連レポートを紐付け
4. 概念リストをユーザーにプレビュー表示

**Checkpoint**: 概念リスト（名前 + 関連レポート数）をユーザーに提示し、承認を得る。
不要な概念の除外や追加があればここで調整する。

## Phase 2: Compile

### 2.1 概念記事生成

承認された概念リストに基づき、各概念の記事を生成する。

各概念について:
1. 関連レポートの該当セクションを Read で取得
2. `templates/concept-article.md` のテンプレートに従って記事を生成
3. `docs/wiki/concepts/{concept-slug}.md` に Write

記事の品質基準:
- 概要は 2-4 文で概念の本質を捉える
- 主要な知見は箇条書き 5-10 項目
- ソースへの相対パスリンクが正しい（`../../research/YYYY-MM-DD-slug-analysis.md`）
- 関連概念への標準 markdown リンク（`[概念名](concept-slug.md)`）

### 2.2 バックリンク挿入

全概念記事を走査し、相互参照を挿入する:
- 概念 A の記事内で概念 B に言及している場合、B の「関連概念」セクションに A へのリンクを追加
- リンクは標準 markdown: `[概念名](concept-slug.md) — 関連の説明`

## Phase 3: Index

### 3.1 INDEX.md 生成

`templates/wiki-index.md` に従って `docs/wiki/INDEX.md` を生成する:
- トピック別に概念記事をグルーピング
- 全レポートの一覧テーブル（日付、タイトル、トピック、関連概念リンク）
- 統計サマリ（レポート数、概念数、トピック数）

### 3.2 完了報告

生成結果をユーザーに報告:
- 生成された概念記事数
- トピック別の概念分布
- 新規 vs 更新（update サブコマンドの場合）

## `index` サブコマンド

Phase 3 のみを実行する。`docs/wiki/concepts/` 内の既存記事を走査して INDEX.md を再生成する。
概念記事の内容は変更しない。

## Anti-Patterns

| NG | 理由 |
|----|------|
| 130 ファイルを1エージェントで処理 | トークン予算超過。必ずバッチ分割 |
| レポート本文をそのままコピー | 概念記事は複数レポートの統合。コピペは不可 |
| Obsidian wiki リンク `[[]]` を使用 | GitHub 表示で非対応。標準 markdown リンクを使う |
| 概念の粒度が細かすぎる | 1レポートにしか出ない概念は記事化しない（2+レポートで共有される概念のみ） |
| INDEX.md を手動編集 | 次回 compile/index で上書きされる |

## Gotchas

- 旧形式レポート（frontmatter なし）と新形式（YAML frontmatter あり）が混在する。両方をパースできるようにする
- ファイル名から日付を抽出する際は `YYYY-MM-DD` プレフィックスを使う
- `update` サブコマンドでは既存の概念記事を破壊せず、追記・更新のみ行う
- 概念スラッグは kebab-case で統一（例: `multi-agent-coordination`）
- バックリンク挿入は冪等であること。既に存在するリンクは重複追加しない。`compile`/`update` の繰り返し実行で同じリンクが増殖しないよう確認する
- `docs/research/` 内の非レポートファイル（README 等）が混入した場合、frontmatter やヘッダーがなければスキップする
