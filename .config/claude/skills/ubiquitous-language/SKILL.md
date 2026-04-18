---
name: ubiquitous-language
description: >
  会話・コード・PRD・Issue から DDD ubiquitous language (用語集) を抽出し、
  語彙 drift を検出して docs/glossary.md に整備する。
  Triggers: '用語集', 'glossary', 'ubiquitous language', '語彙 drift', 'ドメイン用語',
  'term extraction', '同義語チェック'.
  Do NOT use for: 一般的な英単語翻訳、コメント生成（use comment-analyzer agent）、
  コンテンツ生成（use obsidian-content）。
origin: self
allowed-tools: "Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion"
metadata:
  pattern: extractor+curator
  version: 1.0.0
  category: knowledge
---

# Ubiquitous Language — DDD 用語集ビルダー

会話・コード・PRD・Issue から固有名詞・ドメイン動詞句を抽出し、
`docs/glossary.md` の ubiquitous language を育てる。**語彙 drift (同じ概念に複数の呼び名)
が発生する前に検出する** ことが目的。

## Philosophy

- **言葉は設計である**: コード・PRD・会話で同じ概念を別名で呼ぶと、モデルは silent に歪む
- **抽出ではなく合意**: glossary は単なる辞書ではなく、チームの合意の artifact
- **drift 検出が第一**: 新規登録よりも、既存語との衝突 (同義語・曖昧語) を可視化することに価値がある

## Workflow

### Phase 1: Extract (Haiku 委譲)

入力ソースから候補語を抽出する:

1. **現在の会話**: 最近のユーザー発話と assistant 応答
2. **指定ソース** (ユーザー指定): コード (`src/`, `pkg/`), PRD (`docs/specs/*.md`), Issue (gh issue list), Obsidian ノート

抽出対象:
- 固有名詞 (エンティティ、値オブジェクト名)
- ドメイン動詞句 (「注文を確定する」「在庫を引き当てる」等)
- 略語・頭字語 (展開形とセットで)

**除外**: 一般プログラミング用語 (function, class, array 等)、言語キーワード、UI ラベル。

### Phase 2: Normalize (Opus)

既存 `docs/glossary.md` (存在しなければ初回作成) を Read し、候補語と突き合わせる:

- **完全一致**: スキップ
- **同義語候補**: 既存語と意味が近いか判定 (例: 「注文」vs「オーダー」)
- **曖昧語**: 複数の意味で使われている語を検出 (例: 「ユーザー」がエンドユーザーと管理者の両方を指す)
- **新規候補**: 既存と重複しないもの

抽出ヒューリスティクスの詳細は `references/extraction-heuristics.md` を参照。

### Phase 3: Propose

AskUserQuestion で以下を確認:

- 新規候補を glossary に追加するか (各候補について Yes/No/Skip)
- 同義語候補をどう解決するか (A) 正規形に統一 B) 両方を alias として記録 C) Skip)
- 曖昧語の定義分離が必要か (Yes → context 別エントリを作成)

ユーザー応答に基づき提案を確定する。

### Phase 4: Persist

確定したエントリを書き込む:

1. **`docs/glossary.md`** (存在しなければ新規作成): `templates/glossary-entry.md` フォーマットで追記
2. **Obsidian** (optional): `05-Literature/glossary-{domain}.md` に同期。ドメイン名はユーザーに確認

ファイル冒頭の `## Log` セクションに `YYYY-MM-DD: added N entries, resolved M synonyms` 形式で追記する。

## Output

```markdown
✅ Glossary updated: docs/glossary.md

📋 追加: N entries
🔁 統合: M synonyms resolved
⚠️  Drift 検出: K conflicts (要レビュー)

次のアクション:
- ADR に用語変更を記録する場合 → /decision
- チーム共有の場合 → Obsidian Vault sync
```

## Initial Glossary Bootstrap

`docs/glossary.md` が存在しない初回実行時:

```markdown
# Ubiquitous Language Glossary

プロジェクトのドメイン用語集。**語彙 drift 防止**のため、新規語はこのファイルで合意する。

## Log
<!-- YYYY-MM-DD: 変更サマリ -->

## Terms
<!-- アルファベット順。各エントリは templates/glossary-entry.md フォーマット -->
```

を書き込んでから Phase 4 に進む。

## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | 一般プログラミング語 (function, method) を入れる | ドメイン固有語のみ |
| 2 | context なしで追加 (「注文」だけ) | 定義文と利用例を必須にする |
| 3 | 既存語との衝突を無視 | Phase 2 で必ず drift 検出 |
| 4 | 一度に 50+ 語を一括登録 | 1 セッションで最大 10 語を推奨 (consensus cost) |
| 5 | コードに出現しない語を glossary に入れる | 実際の artifact に根拠がある語のみ |

## Skill Assets

- `templates/glossary-entry.md` — 用語エントリのフォーマット
- `references/extraction-heuristics.md` — 候補語抽出のヒューリスティクス

## Related Workflows

- ADR で用語変更を記録 → `/decision`
- コメント整合性チェック → `comment-analyzer` agent
- 仕様書の用語統一 → `/spec` (Phase 0 interview で glossary 参照)
