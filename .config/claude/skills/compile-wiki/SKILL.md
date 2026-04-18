---
name: compile-wiki
description: >
  docs/research/ の分析レポート群を概念ベースの wiki にコンパイルする。
  レポート横断で概念を抽出・統合し、docs/wiki/concepts/ に記事を生成、INDEX.md を自動更新する。
  Karpathy "LLM Knowledge Bases" アプローチに基づくナレッジベースパイプライン。
  Triggers: 'wiki コンパイル', 'compile-wiki', 'ナレッジベース', 'knowledge base', '概念抽出', 'wiki 更新', 'wiki 生成'.
  Do NOT use for: 単一記事の要約（直接回答で十分）、外部記事の統合（use /absorb）、Obsidian ナレッジ管理（use /obsidian-knowledge）。
origin: self
allowed-tools: Read, Write, Edit, Bash(ls:*), Bash(wc:*), Bash(git diff:*), Glob, Grep, Agent, AskUserQuestion
argument-hint: compile | update | index | lint | lint --fix | query | promote | promote-draft | generate-data
metadata:
  pattern: pipeline
disable-model-invocation: true
---

# /compile-wiki — Research Wiki Compiler

docs/research/ の 130+ 分析レポートを概念ベースの wiki にコンパイルする。

## サブコマンド

| コマンド | 説明 |
|---------|------|
| `compile` (デフォルト) | 全件スキャン → 概念抽出 → 記事生成 → INDEX 生成 |
| `update` | git diff ベースの差分更新（変更/追加レポートのみ再処理） |
| `index` | INDEX.md のみ再生成（概念記事は触らない） |
| `lint` | wiki の品質チェック（矛盾・欠損・接続・鮮度・confidence） |
| `lint --fix` | lint + 安全な自動修正（stub 生成・frontmatter 補完）+ suggested questions |
| `query` | wiki INDEX → 関連ページ読み → 合成回答。デフォルトで wiki 再投入を提案 |
| `promote` | wiki 知見を schema 層（CLAUDE.md / references/）に **縦方向**昇格 |
| `promote-draft` | `_drafts/{slug}.md` を `concepts/{slug}.md` に **横方向**昇格（agent → human authorship） |
| `generate-data` | wiki → QA ペア生成（eval / fine-tuning 用） |

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
- YAML frontmatter に以下を含む:
  - `confidence: established | emerging | speculative`
  - `last_validated: YYYY-MM-DD` — 最後に内容を検証した日付（生成時 = 当日）
  - `source_count: N` — 参照ソース数
  - 判定基準: source_count ≥ 3 かつ updated ≤ 30d → established、source_count ≤ 1 または updated > 90d → speculative、それ以外 → emerging

### 2.2 バックリンク挿入

全概念記事を走査し、相互参照を挿入する:
- 概念 A の記事内で概念 B に言及している場合、B の「関連概念」セクションに A へのリンクを追加
- リンクは標準 markdown: `[概念名](concept-slug.md) — 関連の説明`

## Phase 3: Index

### 3.1 INDEX.md 生成

`docs/wiki/INDEX.md` を生成する:
- トピック別に概念記事をグルーピング
- 各概念エントリに `source_count` と `confidence` を付記（例: `— ... | sources: 5 | established`）
- 各概念エントリに `related: [関連概念1, 関連概念2]` を付記（概念間ナビゲーション用）
- 全レポートの一覧テーブル（日付、タイトル、トピック、関連概念リンク）
- 統計サマリ（レポート数、概念数、トピック数、confidence 分布）

### 3.2 完了報告

生成結果をユーザーに報告:
- 生成された概念記事数
- トピック別の概念分布
- 新規 vs 更新（update サブコマンドの場合）

## `index` サブコマンド

Phase 3 のみを実行する。`docs/wiki/concepts/` 内の既存記事を走査して INDEX.md を再生成する。
概念記事の内容は変更しない。

## `lint` サブコマンド

`docs/wiki/concepts/*.md` を対象に 4 種類の品質チェックを実行し、レポートを出力する。
ファイルの書き換えは行わない（read-only）。

### Check 1: 矛盾検出

1. `Glob: docs/wiki/concepts/*.md` で全記事を取得する
2. 各記事から主張（断言文）をリスト化する
3. 同一トピックについて異なる記事が矛盾する主張をしていないか比較する
   - 例: 一方が「depth-1 が最適」と主張し、他方が「再帰的サブエージェントが必要」と主張する場合
4. 疑わしい矛盾を `file:section` 参照付きで列挙する

### Check 2: 欠損概念検出

1. 全記事本文を走査し、他の概念への言及（名詞句・専門用語）を収集する
2. `docs/wiki/concepts/` に対応する `{slug}.md` が存在しない概念をリストアップする
3. 3 記事以上で言及されているが記事が存在しない概念を「欠損候補」としてフラグする

### Check 3: 接続提案

1. 各記事のキーワード・トピックを抽出する
2. 記事ペアを比較し、共通キーワードが 2 つ以上あるにもかかわらず相互リンクがないペアを検出する
3. リンク追加を提案する（追加先の記事名と想定アンカーテキストを明示）

### Check 4: 鮮度チェック + Confidence 管理

1. 各記事の `Sources` セクションからリンク先レポートの日付（ファイル名プレフィックス `YYYY-MM-DD`）を収集する
2. 全ソースが現在日付から 30 日以上前の記事を「陳腐化候補」としてフラグする
3. `docs/research/` に同一トピックの新しいレポート（記事のソース日付より新しいもの）があれば、そのパスを添えて報告する
4. **Confidence 降格提案**: `source_count ≤ 1` かつ `last_validated > 90d` の記事を speculative に降格提案
5. **Confidence 昇格提案**: `source_count ≥ 3` かつ `last_validated ≤ 30d` の記事を established に昇格提案

### Check 5: Draft 滞留 Alert (Semantic Pollution 対策)

> 出典: Kevin's "Modified Karpathy Method" (2026-04) + Gemini 批評 (graduation 停滞は最大の落とし穴)。

1. `Glob: docs/wiki/concepts/_drafts/*.md` で全 draft を取得する (`README.md` は除外)
2. 各 draft の git 作成日時（`git log --diff-filter=A --format=%ai -- {path}`）を取得
3. 作成から **30 日以上経過** した draft を「滞留 alert」としてフラグする
4. 滞留 draft について以下の 3 アクションを提案:
   - `promote-draft` で昇格判断 (レビュー済みなら)
   - `docs/research/` 配下に差し戻し (品質不足)
   - 削除 (トピック陳腐化)

### Check 6: Draft Sources 不在チェック (Mandatory Citation)

> 出典: Kevin's "Modified Karpathy Method" (2026-04) — agent 生成コンテンツには mandatory citation を強制。

1. `Glob: docs/wiki/concepts/_drafts/*.md` で全 draft を取得する (`README.md` は除外)
2. 各 draft の frontmatter を Read し、`sources:` フィールドを検査する
3. 以下の条件で flag する:
   - `sources:` フィールドが存在しない
   - `sources:` が空リスト
   - `sources:` 内の参照パスが `docs/research/` 配下に実在しない (dead link)
4. flag された draft は **`promote-draft` の昇格対象外** として記録

### 出力フォーマット

```
## Wiki Lint Report

### 矛盾検出
- [contradiction] {file-a}.md vs {file-b}.md — {主張Aの要約} ↔ {主張Bの要約}

### 欠損概念
- [missing] "{概念名}" — {N} 記事で言及、専用記事なし

### 接続提案
- [link] {file-a}.md ↔ {file-b}.md — {共通キーワードの説明}

### 鮮度チェック
- [stale] {file}.md — 最新ソース {YYYY-MM-DD}、関連新規レポート: {path}

### Draft 滞留 Alert
- [aging-draft] _drafts/{slug}.md — 作成 {YYYY-MM-DD} から N 日経過。suggested: promote-draft | 差し戻し | 削除

### Draft Citation 不在
- [missing-sources] _drafts/{slug}.md — frontmatter に sources フィールドなし / 空 / dead link
```

各セクションに該当がない場合は `（問題なし）` と表示する。
レポート末尾に「チェック対象記事数・指摘総数・draft 数」のサマリ行を付ける。

## `lint --fix` サブコマンド

`lint` の全チェックを実行した上で、**安全な自動修正** を適用する。

### 自動修正（確認なしで適用）

1. **Stub 生成**: Check 2 で検出された欠損概念のうち、3 記事以上で言及されているものについてスタブページを自動生成する
   - frontmatter（title, confidence: speculative, source_count: 0, last_validated: 当日）+ 1行定義 + 言及元へのリンク
   - パス: `docs/wiki/concepts/{concept-slug}.md`
2. **Frontmatter 補完**: `confidence`, `last_validated`, `source_count` が欠損している記事に自動付与する
   - source_count はソースセクションのリンク数からカウント
   - confidence は判定基準に従い自動分類
   - last_validated は updated フィールドから継承（なければ当日）

### ユーザー確認後に適用

3. **Confidence 変更**: Check 4 の降格/昇格提案をまとめて提示し、承認されたもののみ適用

### 追加出力

4. **Suggested Questions**: wiki の知識ギャップから研究質問を 3-5 個提案する
   - 欠損概念の深掘り、矛盾の解消、陳腐化記事の更新に関する質問
   - query サブコマンドで辞退された質問があれば再提案の参考にする

## `query` サブコマンド

wiki を起点にした Q&A を実行し、回答を wiki に再投入するオプション付き。

### Depth モード (`--depth`)

> 出典: Kevin's "Modified Karpathy Method" (2026-04) — `/wiki-query` の quick / standard / deep 3-mode の移植。

`--depth=quick|standard|deep` フラグで調査深度を制御する (optional、デフォルトは `standard`)。

| mode | Step 1-3 の挙動 | 用途 |
|------|---------------|------|
| `quick` | INDEX.md のみ読み + 上位 3 関連ページの要約 (frontmatter + H2) を取得 | 速度優先、ファクトチェック |
| `standard` (default) | INDEX → 3-5 関連ページを full Read → 合成 | 通常の Q&A |
| `deep` | standard + 各ページの sources 先 (`docs/research/*.md`) を辿る + 必要なら `/research` で補完 | 設計判断、トレードオフ分析 |

#### 使用例

- `/compile-wiki query --depth=quick "observability-signals の owner は誰？"`
- `/compile-wiki query "multi-agent 協調パターンの比較"` — デフォルト standard
- `/compile-wiki query --depth=deep "harness 設計の代替案"` — research 補完込み

deep モードは時間がかかるため、自動で `AskUserQuestion` で「research 補完を許可しますか？」と確認する。

### Step 1: INDEX 読み込み

`docs/wiki/INDEX.md` を Read し、全概念記事のリストを取得する。

### Step 2: 関連ページ特定

ユーザーの質問に基づき、INDEX からキーワードマッチで関連する概念記事を 3-5 個特定する。

### Step 3: ドリルダウン

特定した概念記事を Read し、内容を取得する。
必要に応じて記事内のソースリンク（`docs/research/` 内のレポート）も参照する。

### Step 4: 合成回答

読み取った wiki ページの知見を統合し、質問に対する回答を生成する。
回答にはソースとなった概念記事へのパスを citation として含める。

### Step 5: 再投入（デフォルト提案）

回答完了後、**常に** wiki への再投入を提案する（Filing Loop の複利効果を駆動するため）:
1. 「この回答を wiki に追加しますか？（推奨: 知識の複利効果のため）」とユーザーに確認
2. 承認されたら最も関連する概念記事に追記、または新規概念記事を生成
3. 辞退されたら理由を簡潔に記録（lint の suggested questions に活用）
4. `docs/wiki/log.md` に query エントリを追記（再投入の有無を記録）

## `promote` サブコマンド

wiki の知見を schema 層（CLAUDE.md / references/）に昇格させる。知識の3層構造（raw → wiki → schema）を完結させるパス。

### 昇格基準

以下の **すべて** を満たす概念記事が昇格候補:
1. `confidence: established`（source_count ≥ 3、last_validated ≤ 30d）
2. 3 セッション以上で参照されている（log.md の query エントリで確認）
3. エージェントの行動規範・判断基準に直結する知見を含む

### 昇格先の判定

| 知見の種類 | 昇格先 | 例 |
|-----------|--------|-----|
| 行動ルール・禁止事項 | `CLAUDE.md` の core_principles | 「テストモック禁止」→ core_principles に追記 |
| 参照用ガイドライン | `references/{topic}.md` | レビューチェックリスト → references/review-checklists/ |
| ワークフロー改善 | 関連スキルの SKILL.md | Filing loop 改善 → compile-wiki/SKILL.md |

### 実行フロー

1. `docs/wiki/concepts/` を走査し、昇格基準を満たす記事を候補リストとして提示
2. ユーザーが昇格する記事と昇格先を選択
3. 昇格先ファイルへの変更差分をプレビュー表示
4. 承認後に適用、`docs/wiki/log.md` に `promote` エントリを追記
5. 昇格元の概念記事に `promoted_to: {path}` を frontmatter に追記

### `/improve` との連携

`/improve` が policy 更新を提案する際、wiki の established 概念を根拠として参照できる。
`promote` は wiki → schema の明示的なパス、`/improve` は session data → schema の暗黙的なパス。両者は補完関係。

## `promote-draft` サブコマンド

`docs/wiki/concepts/_drafts/{slug}.md` を `docs/wiki/concepts/{slug}.md` に **横方向**昇格させる（agent authorship → human authorship）。

> 出典: Kevin's "Modified Karpathy Method" (2026-04) の graduation mechanism。frontmatter 方式ではなく **ディレクトリ分離方式** で実装（Gemini 推奨、grep / git mv / .gitignore で堅牢）。`_drafts/` については [`docs/wiki/concepts/_drafts/README.md`](../../../../docs/wiki/concepts/_drafts/README.md) を参照。

### `promote` との関係

| サブコマンド | 方向 | 対象 | 昇格先 |
|-------------|------|------|--------|
| `promote` | **縦方向** (raw/wiki → schema) | `concepts/{slug}.md` | `CLAUDE.md` / `references/` |
| `promote-draft` | **横方向** (agent authorship → human authorship) | `concepts/_drafts/{slug}.md` | `concepts/{slug}.md` |

両者は直交する。`promote-draft` で昇格した concept は後から `promote` で schema 層へさらに縦方向昇格できる。

### 昇格基準

`promote-draft` の昇格候補は以下 **すべて** を満たす draft:

1. **sources**: `sources:` frontmatter に少なくとも 1 つの `docs/research/*.md` 参照がある (mandatory citation)
2. **レビュー完了**: 人間が内容を読み、「自分の理解と一致している」と判断した
3. **腐敗していない**: 最後に書かれた docs/research/ ソースが 30 日以内に更新されている (Optional)

### 実行フロー

1. `Glob: docs/wiki/concepts/_drafts/*.md` で全 draft を取得
2. `AskUserQuestion` で昇格対象の draft を選択（複数選択可）
3. 各 draft について昇格前プレビューを表示:
   - frontmatter の `sources:` 確認
   - 既存 `concepts/{slug}.md` との衝突確認（同名があれば上書きか diff 統合か選択）
4. 承認後、`git mv docs/wiki/concepts/_drafts/{slug}.md docs/wiki/concepts/{slug}.md` を実行
5. 昇格された concept の frontmatter に `authored_by: human`, `graduated_from: draft`, `graduated_at: {YYYY-MM-DD}` を追記
6. `docs/wiki/log.md` に `promote-draft` エントリを追記:
   ```markdown
   ## [YYYY-MM-DD] promote-draft | {slug}
   - from: _drafts/{slug}.md
   - to: concepts/{slug}.md
   - sources: {count} reports
   ```
7. 必要に応じて `INDEX.md` を `index` サブコマンドで再生成

### Anti-Patterns

| NG | 理由 |
|----|------|
| sources 不在の draft を昇格 | mandatory citation 原則違反。`lint` Check 6 で flag される |
| 同名の `concepts/{slug}.md` が既存の状態で無確認上書き | 人間が書いた既存内容を失うリスク。必ず diff プレビューを確認 |
| 全 draft を一括昇格 | レビューなしの bulk promote は graduation mechanism の本質を破壊する |

## `generate-data` サブコマンド

wiki の概念記事から QA ペアを生成し、eval データや fine-tuning 用データセットとして出力する。

### 生成ルール

各概念記事について以下の QA ペアを生成する:
- **事実質問** 2 個（who/what/when — 記事から直接回答可能）
- **推論質問** 2 個（why/how/compare — 記事の知見を組み合わせて回答）
- **統合質問** 1 個（他の概念記事と接続して回答が必要）

### 出力フォーマット

```json
[
  {
    "question": "質問文",
    "answer": "回答文",
    "type": "factual | reasoning | synthesis",
    "source_concepts": ["concept-slug-1", "concept-slug-2"],
    "difficulty": "easy | medium | hard"
  }
]
```

### 出力先

- `docs/wiki/outputs/qa-dataset-{YYYY-MM-DD}.json`
- 統計サマリをユーザーに報告（総数、タイプ別分布、概念カバレッジ）
- `docs/wiki/log.md` に `generate-data` エントリを追記

### 品質基準

- 回答は wiki の内容に基づき、ハルシネーションを含まない
- 統合質問は実際に概念間リンクが存在するペアからのみ生成
- `confidence: speculative` の記事からは事実質問を生成しない

## Log 記録

全サブコマンド完了時に `docs/wiki/log.md` に操作エントリを追記する。

```markdown
## [YYYY-MM-DD] {operation} | {title or summary}

- 対象: {処理した概念数 or レポート数}
- 結果: {生成/更新/指摘の概要}
```

`compile`/`update`/`index`/`lint`/`query` いずれの操作でも記録する。

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

## フィードバック連携

以下のスキルから wiki への自動フィードバックをサポートする:

### /research → wiki
`/research` 完了後、出力レポートが `docs/research/` に保存された場合:
- `/compile-wiki update` で差分更新を提案
- 新しい概念が既存記事に関連する場合、関連概念セクションへのリンク追加を提案

### /eureka → wiki
`/eureka` で発見記録が `breakthroughs/` に保存された場合:
- 関連する概念記事の「主要な知見」セクションへの追記を提案
- 該当する概念がない場合は新規概念候補としてフラグ

### セッション Q&A → wiki
セッション中に wiki にない重要知見が得られた場合:
- 「この知見を wiki に追加しますか？」と提案
- 承認されたら最も関連する概念記事に追記、または新規概念記事を生成
