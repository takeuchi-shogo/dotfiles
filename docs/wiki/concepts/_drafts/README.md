# `_drafts/` — Agent-Authored Wiki Concepts (Pre-Graduation)

このディレクトリは `docs/wiki/concepts/` の **draft layer** です。エージェントが `/research` / `/absorb` 等で生成した概念記事を一時的に保持し、人間のレビュー後に正式な concepts/ に昇格させます。

## 目的

**Agent 成果物 と 人間の思考 を明示的に分離する** ことで、自分の知的 artifact を agent の過剰な上書きから守ります。

- `docs/wiki/concepts/_drafts/*.md` — エージェントが書いた草稿。後続の research で自由に上書き可能
- `docs/wiki/concepts/*.md` — 人間がレビュー・承認した成熟した概念記事。エージェントは **上書き不可**

Karpathy の 3 層アーキテクチャ (raw / wiki / schema) を継承しつつ、Kevin's "Modified Karpathy Method" (2026-04) の **author 分離パターン** をディレクトリ方式で実装したもの。frontmatter 方式より堅牢 (grep / git mv / .gitignore で除外しやすい)。

## Graduation Workflow

```
agent 生成 (/research, /absorb)
  ↓
_drafts/{slug}.md に配置
  ↓
人間がレビュー
  ↓
内容が正確 + 自分の理解と一致
  ↓
git mv _drafts/{slug}.md concepts/{slug}.md
  ↓
concepts/ の protected layer に昇格
```

昇格は `compile-wiki promote-draft` サブコマンドで実行可能 (git mv + log.md への promote-draft エントリ追記を自動化)。

## Draft 作成ルール

- **必須**: `sources:` frontmatter フィールド (少なくとも 1 つの `docs/research/*.md` 参照)
- **必須**: `authored_by: agent` frontmatter (方向確認用、現状ディレクトリで区別しているが将来の監査用)
- **推奨**: `confidence: speculative`, `last_validated: YYYY-MM-DD`

## 滞留 Alert (Semantic Pollution 対策)

`compile-wiki lint` は `_drafts/` 内で **30 日以上経過** したファイルを alert します。滞留は以下のいずれかを示唆します:

- レビューのボトルネック → `compile-wiki promote-draft` で昇格判断
- 品質不足で昇格不適格 → 削除するか `docs/research/` に差し戻す
- トピックが陳腐化 → 削除

## 関連

- 分析レポート: [`docs/research/2026-04-14-karpathy-second-brain-modified-analysis.md`](../../../research/2026-04-14-karpathy-second-brain-modified-analysis.md)
- 実装プラン: [`docs/plans/2026-04-14-karpathy-second-brain-absorb-plan.md`](../../../plans/2026-04-14-karpathy-second-brain-absorb-plan.md)
- 親 skill: [`compile-wiki`](../../../../.config/claude/skills/compile-wiki/SKILL.md) — `promote-draft` サブコマンド
