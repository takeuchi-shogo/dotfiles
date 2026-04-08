---
name: obsidian-content
description: "Use when generating content (newsletters, blog posts, tweet threads) from your Obsidian Vault. Searches notes and follows your writing style. Triggers: 'ニュースレター書いて', 'ブログ記事', 'ツイート生成', 'Vault からコンテンツ'. Do NOT use for: ノート検索・整理のみ (use obsidian-knowledge), Vault 初期セットアップ (use obsidian-vault-setup). Markdown syntax/embeds/callouts → defer to obsidian plugin skills."
metadata:
  pattern: generator
---

# Obsidian Content Creator

Vault 全体のナレッジを活用して、ユーザーのライティングスタイルでコンテンツを生成する。

## 前提条件

- Claude Code が Obsidian Vault のルートで起動されていること
- CLAUDE.md が存在し、ライティングスタイルが定義されていること
- 04-Galaxy/ にパーマネントノートが存在すること

## 引数の解釈

引数なし → インタラクティブモード
引数あり → トピックとして解釈

例:
- `/obsidian-content 潜在意識についてのニュースレター`
- `/obsidian-content AIツールの比較ブログ記事`
- `/obsidian-content 朝のルーティンについてのツイートスレッド`

## Voice Guide（ライティングスタイル統一）

### 初回セットアップ
voice guide が未生成（`references/voice-guide.md` が存在しない）の場合:

1. Vault 内のユーザーが書いた記事を3本検索（`mcp__obsidian__search_notes` で author タグ or 手動指定）
2. 3本の記事から以下を分析:
   - 文の構造パターン（短文主体 / 複文主体）
   - 語彙の傾向（技術用語の使い方、カジュアル度）
   - トーンと性格（直接的 / 丁寧 / ユーモア）
   - フォーマット習慣（箇条書き多用 / 段落主体）
   - 絶対にやらないこと
3. 分析結果を200語以内の voice guide として `references/voice-guide.md` に保存

### コンテンツ生成時の適用
- `references/voice-guide.md` が存在する場合、コンテンツ生成前に Read して適用
- voice guide は200語上限を厳守（Context Rot 対策）
- `--no-voice` フラグでスキップ可能

## 処理手順

### Step 1: トピックとフォーマットの確定

引数からトピックを抽出する。フォーマットが指定されていない場合は AskUserQuestion で聞く:

- ニュースレター
- ブログ記事
- ツイートスレッド
- 自由形式（フォーマット指定）

### Step 2: Vault スキャン（並列）

Agent ツールを **3つ並列** で起動し、関連コンテンツを収集:

**Agent 1** (subagent_type: Explore):
「04-Galaxy/ 内で [トピック] に関連するパーマネントノートを検索し、各ノートのタイトル・要約・ファイルパスをリストで返してください」

**Agent 2** (subagent_type: Explore):
「05-Literature/ 内で [トピック] に関連する文献ノートを検索し、ハイライトとソース情報をリストで返してください」

**Agent 3** (subagent_type: Explore):
「01-Projects/ と 03-Resources/ 内で [トピック] に関連する過去のコンテンツやアウトラインを検索し、ファイルパスと概要をリストで返してください」

### Step 3: コンテキスト統合

3つのエージェントの結果を統合し、最も関連性の高いノートを選定する:
- Galaxy ノート: 核となるアイデアの素材
- Literature ノート: 引用・事例の素材
- 過去コンテンツ: スタイル・構成の参考

選定したノートを Read で読み込む（最大10ファイル）。

### Step 4: コンテンツ生成

CLAUDE.md の Writing Style セクションに従って生成する。

**フォーマット別の構成**:

#### ニュースレター
```markdown
---
title: ""
subject_lines:
  - ""
  - ""
  - ""
preview_text: ""
tags: [type/newsletter, topic/xxx]
date: YYYY-MM-DD
---

# [タイトル]

[導入: フックとなる文]

## [セクション1]
...

## [セクション2]
...

## まとめ
...

---
参考ノート: [[ノート1]], [[ノート2]]
```

#### ブログ記事
```markdown
---
title: ""
description: ""
tags: [type/blog, topic/xxx]
date: YYYY-MM-DD
status: draft
---

# [タイトル]

## はじめに
...

## [本文セクション x N]
...

## まとめ
...

---
参考ノート: [[ノート1]], [[ノート2]]
```

#### ツイートスレッド
```markdown
---
tags: [type/tweet-thread, topic/xxx]
date: YYYY-MM-DD
---

1/ [フック]

2/ [本文]

...

N/ [まとめ + CTA]

---
参考ノート: [[ノート1]], [[ノート2]]
```

### Step 5: プレビューと保存

1. 生成したコンテンツをプレビュー表示
2. AskUserQuestion:「この内容で保存しますか？修正点はありますか？」
3. 修正がある場合は修正して再表示
4. 承認後、Write で適切なフォルダに保存:
   - ニュースレター → `01-Projects/newsletters/`
   - ブログ → `01-Projects/blog/`
   - ツイート → `01-Projects/tweets/`
   - その他 → `01-Projects/content/`
5. フォルダが存在しない場合は Bash で `mkdir -p` で作成

### Step 6: memory.md 更新

`.claude/memory.md` に以下を追記:
- 生成日時
- トピック
- フォーマット
- 使用したソースノート
- 保存先パス

## 品質チェック

生成前に以下を確認:
- CLAUDE.md の Writing Style に違反していないか
- `references/writing-anti-patterns.md` のチェックリストを適用し、AI臭い表現を排除したか
- ソースノートの内容を正確に反映しているか
- リンク切れがないか

## Self-Correction（コンテンツ品質ゲート）

コンテンツ生成後、ユーザーに提示する前に以下の4次元で自己評価を行う:

| 次元 | 基準 | 合格ライン |
|------|------|-----------|
| Accuracy | 事実・技術情報が正確か | 8/10 以上 |
| Completeness | トピックの重要ポイントを網羅しているか | 8/10 以上 |
| Clarity | スキミングで要点が掴めるか | 8/10 以上 |
| Actionability | 読者が具体的なアクションを取れるか | 8/10 以上 |

**手順:**
1. 生成したコンテンツを上記4次元で評価（内部処理、ユーザーには見せない）
2. 8未満の次元がある場合、その部分を修正して再評価
3. 全次元8以上になったらユーザーに提示
4. 最大2回の修正ループ。3回目でも8未満なら現状のまま提示し、低い次元を注記

> 根拠: Reflexion (Shinn et al., 2023) — 自己評価+修正ループで出力品質が大幅向上

## Thread Mode（`--thread`）

Twitter/X スレッドを体系的に作成する。

### 使い方
```
/obsidian-content --thread [トピック]
```

### 構造
- **ツイート1**: scroll-stop hook — 大胆な主張、驚きの事実、反直感的な洞察のいずれか。汎用的な書き出し禁止
- **本文ツイート**: 各ツイートが独立して読める AND 全体でナラティブを形成
- **エビデンス**: 具体的な数値、事例、根拠を含む。曖昧な主張禁止
- **最終ツイート**: 明確な CTA（call to action）
- **長さ**: 10-15ツイート
- Voice Guide 自動適用

## Outline Mode（`--outline`）

長文記事のアウトライン（設計図）を生成する。記事本文は書かない。

### 使い方
```
/obsidian-content --outline [トピック] --angle [独自の切り口] --audience [読者]
```

### 出力構造
1. **Hook**: 2つの書き出し案（大胆な主張 or 共感できる問題提起）
2. **Sections**: 5-7セクション、各セクションにヘッダー + 2文の要約
3. **Evidence Needed**: 各セクションに必要なデータ・事例・ケーススタディ
4. **Closing**: 読者が読後に取るべきアクション

### ルール
- アウトラインのみ生成。本文は書かない
- ユーザーがこの設計図から書く前提

## Repurpose Mode（`--repurpose`）

既存の記事・ノートを複数フォーマットに変換する。

### 使い方
```
/obsidian-content --repurpose [[ノート名]]
/obsidian-content --repurpose （テキスト貼り付け）
```

### 出力フォーマット（全て一括生成）

1. **Twitter/X Thread** (12-15ツイート)
   - ツイート1: scroll-stop hook（大胆な主張 or 驚きの事実）
   - 各ツイート: 独立して読めるが全体でナラティブを形成
   - 最終ツイート: 明確な CTA
   - ハッシュタグ不要。意味のある場合のみ絵文字

2. **LinkedIn Post** (200-300語)
   - よりプロフェッショナルなトーン
   - 冒頭で問題提起、末尾で洞察

3. **Standalone Tweets** x 5
   - 記事の核心的な洞察を1ツイートに凝縮
   - 各ツイートが独立したコンテンツとして機能

4. **Newsletter Intro** (100語)
   - 記事の核心をティーザーとして提示
   - 「続きを読む」への動機付け

5. **1文サマリー**
   - グループチャットでの共有用

### ルール
- Voice Guide（`references/voice-guide.md`）が存在する場合は自動適用
- 各フォーマットはプラットフォームネイティブなスタイルで生成（コピペ感を出さない）
- Self-Correction（4次元評価）を全出力に適用

## Skill Assets

- `templates/content-templates.md` — Content format templates for newsletter, blog post, and tweet thread
- `references/writing-anti-patterns.md` — AI臭い表現の Good/Bad 対比テーブルとセルフレビューチェックリスト
