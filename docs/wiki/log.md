# Wiki Operations Log

> Append-only record of wiki operations. Each entry follows the format:
> `## [YYYY-MM-DD] operation | Title`
>
> Operations: `ingest` (absorb), `compile` (compile-wiki), `update` (compile-wiki update),
> `lint` (compile-wiki lint), `query` (compile-wiki query), `index` (compile-wiki index)

<!-- Parseable with: grep "^## \[" docs/wiki/log.md | tail -10 -->

## [2026-04-05] ingest | Karpathy "LLM Wiki" Gist

- ソース: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- 判定: Gap 1, Partial 2, Already 6, N/A 0
- 取り込み: log.md 導入、query サブコマンド追加、Q&A フィードバック強化、概念間矛盾検出確認
- 変更ファイル: docs/wiki/log.md (new), compile-wiki/SKILL.md, absorb/SKILL.md, knowledge-pipeline.md, analysis report
