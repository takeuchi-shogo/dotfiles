---
source: "My Second Brain Setup: A Modified Karpathy Method"
author: "Kevin"
date_analyzed: 2026-04-14
status: integrated
topics: [knowledge-management, wiki, obsidian, authorship]
integration_tasks: 6
---

# My Second Brain Setup: A Modified Karpathy Method — 分析レポート

## Source Summary

**主張**: 個人の Second Brain は「Agent 全執筆→平均化された generic LLM-wiki」か「人間全執筆→静的腐敗 KB」の二択に陥る。`author: kevin` / `author: agent` の frontmatter 一フィールドで権限を分離し、graduation mechanism で agent 生成物を人間の承認で不可侵化することで両者の長所を得る。

**手法**:
1. Two-author pattern (`author: kevin` / `author: agent` frontmatter)
2. Graduation mechanism (agent → human authorship 昇格、同じ wiki 内で横方向)
3. 5 slash commands (`/research` 5-8 並列、`/ingest`, `/wiki-query` 3 depth, `/wiki-lint`, `/wiki-output`)
4. 3 sub-folder 構造 (concepts/ / entities/ / synthesis/、synthesis/ が思考の中核)
5. Karpathy 3 層アーキテクチャ継承 (raw / wiki / CLAUDE.md schema)
6. Mandatory citation + contradiction flagging for agent files

**根拠**: Agent 全所有 → LLM 平均視点の鏡、人間全所有 → 世界の変化速度に追いつけない、2 author 分離で両立

**前提条件**: Obsidian + Claude Code、個人の知的作業者、自分の思考と外部知識を明示分離したい人

## Gap Analysis (Phase 2.5 修正後)

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Two-author pattern | Gap + Enforcement Gap | memory scope はファイル所有権ではない。agent 保護ルールが未実装 |
| 2 | Graduation mechanism | Gap (類似機能あり) | `compile-wiki promote` は wiki→schema の縦方向で別物。記事は横方向 |
| 3-a | query 3 depth mode | Partial | `query` は Filing Loop 実装済みだが depth 契約が未実装 |
| 3-b | mandatory citation | Partial | `lint` に author 条件付き enforcement なし |
| 3-c | wiki-output | Partial | `/obsidian-content` で部分代替可能 |
| 3-d | research 5-angle | Already (強化可能) | research は 3-8 並列 + モデル別、5-angle preset 不在 |
| 3-e | ingest | Already (authorship 連携要) | `/absorb` が高機能版、authorship 概念なし |
| 4 | concepts/entities/synthesis/ | Gap (Strategic Fit) | concepts/ のみ 37 ページ、PARA Vault と別パラダイム |
| 6 | contradiction flagging | Already (author-aware 化要) | `lint` Check 1 は実装済み、agent-only 限定化は不在 |

## Codex + Gemini 批評サマリ (Phase 2.5)

### Codex (深い推論)
- #1 は Gap だけでなく **enforcement gap**: ingest/query/lint/write の保護ルール全てに対応必要
- #3-a/#3-b は実は Partial: depth 契約・author 条件付き enforcement が未成立
- #3-e/#6 は Already (強化不要) ではなく **authorship 連携強化必要**
- 最優先は #1: two-author enforcement なしでは他全部が曖昧

### Gemini (Google Search grounding)
- **Frontmatter author 方式は弱い。ディレクトリ分離方式 (`_drafts/`) の方が普及・堅牢**
- 実装例: Fabric (Daniel Miessler) `patterns/` で AI 出力管理、Obsidian + Cursor カスタム Git 運用
- **最大の落とし穴**: Graduation 停滞 (Semantic Pollution) — 人間レビューがボトルネック化、agent ページ滞留、RAG 精度低下
- 対策推奨: 滞留 TTL (30 日超 → alert) を hook 化

## Integration Decisions

### 採用 (Bundle A-alt + B1 + B3 + B4)

1. **A-alt**: `docs/wiki/concepts/_drafts/` ディレクトリ分離方式 (Gemini 推奨、frontmatter より堅牢)
2. **B1**: `compile-wiki lint` Check 6 — `_drafts/` で sources 不在を flag
3. **B3**: `compile-wiki query --depth=quick|standard|deep`
4. **B4**: `research` skill `--angles=academic,practitioner,contrarian,historical,empirical` preset
5. **Implicit (A3)**: `compile-wiki lint` Check 5 — `_drafts/` 30 日滞留 alert (Gemini Semantic Pollution 対策)
6. **promote-draft** subcommand: agent→human 横方向 graduation

### 棄却

- **A1/A2** (frontmatter authorship field): Gemini/Codex 両者がディレクトリ分離を推奨。frontmatter 方式より運用シンプル
- **B2** (authorship 別の contradiction 重み付け): lint Check 1 は既にトピック横断で十分、追加複雑性回避
- **C** (entities/synthesis/ sub-folders): 現状 concepts/ 37 ページで運用済み、Karpathy 元パターンの単純さを失うリスク、Obsidian Vault は PARA 構造で別パラダイム

## Tasks (Plan reference)

See `docs/plans/2026-04-14-karpathy-second-brain-absorb-plan.md`

## References

- Related prior integrations:
  - `docs/research/2026-04-03-karpathy-llm-knowledge-bases-analysis.md`
  - `docs/research/2026-04-05-karpathy-llm-wiki-gist-analysis.md`
  - `docs/research/2026-04-07-karpathy-kb-pattern-deep-analysis.md`
  - `docs/research/2026-04-07-karpathy-llm-kb-full-guide-analysis.md`
- Source article: pasted text, no canonical URL known
- Wiki: `docs/wiki/concepts/_drafts/README.md`
