---
status: pending
type: spike (eval-only, no implementation)
created: 2026-05-17
origin: SocratiCode absorb (docs/research/2026-05-17-socraticode-absorb-analysis.md)
size: M
---

# memory-vec scope 拡張 spike (eval-only)

## 動機 (Why)

SocratiCode absorb (2026-05-17) の Phase 2.5 Codex 批評で発見:

- `memory-vec` Phase D は実装済 (`~/.claude/skill-data/memory-vec/{index.db,reindex.ts}` + `memory-vec-hint-hook.py`)
- 対象 scope は **`~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/*.md`** のみ
- `docs/research` (60+ absorb)・`docs/specs`・`.config/claude/references` で **478 files / 約 4MB** あるが、semantic 検索の対象外
- 用途例: 「過去の似た absorb はあるか」「authentication 設計の決定経緯メモ」「circular dependency が出た過去のレビュー」を自然言語で問い合わせ

CRG (tree-sitter) は code-symbol 中心で、自然文ドキュメントの semantic retrieval をカバーしない。SocratiCode 本体を入れずとも、既存 memory-vec の reindex 対象拡張で需要を満たせる可能性がある。

## 重要前提 (Critical Constraint)

**本 plan は eval-only。実装には移行しない**:

- spike が pass しても、本実装は別途 `/spec` → `/spike` → `/validate` の EPD ワークフローを経る
- 採用判断は Codex Review Gate を独立に通す
- Pruning-First: 既存 memory-vec の挙動を破壊しないため、scope 拡張は別ファイルパスでの A/B 実験のみ

## Scope

### In scope

1. `~/.claude/skill-data/memory-vec/reindex.ts` を fork して `reindex-extended.ts` を作成 (本体不変)
2. 対象 scope を以下に拡張する評価:
   - `docs/research/*.md` (60+ absorb 履歴、平均 ~10KB)
   - `docs/specs/*.md` (PRD 一覧)
   - `.config/claude/references/*.md` (decision tables, guides)
3. 別 DB ファイル (`index-extended.db`) に出力、既存 `index.db` は touch しない
4. 計測項目:
   - **Indexing time**: 478 files / 4MB の reindex 所要時間 (`@xenova/transformers` の MiniLM-L6-v2、384 dim)
   - **Disk size**: `index-extended.db` の最終サイズ
   - **Hint quality**: 5 個のクエリで top-K precision を手動評価
     - Q1: "How did past absorbs reject vendor benchmark claims?"
     - Q2: "memory-vec implementation Phase D decisions"
     - Q3: "circular dependency detection 関連の過去 review"
     - Q4: "Codex stall pattern と対処方針"
     - Q5: "Pruning-First applied to codebase-intelligence tools"
   - **Cost**: 拡張時の追加 indexing wall-time (1 回あたり)、SessionStart hint レイテンシ影響

### Out of scope

- 本実装 (`memory-vec-hint-hook.py` の改修、`reindex.ts` 本体への scope merge)
- LLM-as-judge による hint quality 評価 (手動評価のみ)
- 別 embedding model の評価 (MiniLM-L6-v2 固定)
- Stop hook の trigger 改修 (現状 memory/*.md mtime 検出のみ、docs/* 検出は eval 外)

## Steps

1. **Day 1**: `reindex-extended.ts` 作成。`MEMORY_DIR` を拡張パス配列に置換、glob 範囲を `**/*.md` に変更 (frontmatter parse でも `<!-- -->` skip でも、本実装と共通の sanitizer を流用)
2. **Day 1**: 初回 reindex 実行、indexing time と disk size を記録
3. **Day 2**: 5 クエリで top-5 result を手動評価、precision を 5 段階で記す
4. **Day 2**: 既存 `memory/*.md` のみ scope と head-to-head 比較 (同じ 5 クエリ)
5. **Day 3**: 評価レポートを `docs/research/2026-05-XX-memory-vec-scope-eval.md` に書き出す
6. **Day 3**: 採用判断
   - **Pass 条件**: indexing time < 30s, disk size < 50MB, hint precision がベースを上回る or 同等
   - **Fail 条件**: noise が増えて従来クエリの precision が悪化、または scope 拡張で hint が長くなりすぎ token budget 違反

## Risks & Mitigation

| Risk | Mitigation |
|---|---|
| 本体 `index.db` を誤って上書き | spike では別 path (`index-extended.db`) 固定、reindex-extended.ts のみ別ファイル |
| `@xenova/transformers` モデルのメモリ過負荷 (4MB 文書) | バッチサイズを reindex.ts と同じに維持、1 ファイル単位 try/catch |
| SessionStart hint が冗長になり token budget 超過 | spike 段階では hint hook を改修せず、CLI 経由でクエリのみ実行 |
| Codex/Gemini 評価未実施で self-preference bias | eval レポート時に Codex Review Gate 通過を必須化 |
| 既存 absorb 履歴の semantic overlap で hit が偏る | 5 クエリは異なるカテゴリ (vendor評価/実装決定/設計レビュー/失敗パターン/Pruning原則) を意図的に分散 |

## Decision Trigger

以下のいずれかで本 spike を起動する:

1. ユーザーが「過去の absorb で同じ議論あった気がする」と何度か質問する観測 (≥ 3 回 / 月)
2. dotfiles `docs/research/_index.md` が 100 件超え (現在 60+)
3. CRG `semantic_search_nodes_tool` で「code 以外を semantic 検索したい」需要が顕在化

それまでは backlog 待機。

## Out (撤退条件)

- Indexing が 60s 超え → MiniLM では役不足、`bge-small-en` 等の評価が必要 → 別 spike
- disk size > 200MB → scope 絞り込み必要 (specs/ のみ、research/ は除外)
- precision 改善 < 10% → ROI 低、撤退

## Sources

- SocratiCode absorb 分析: `docs/research/2026-05-17-socraticode-absorb-analysis.md`
- 既存 memory-vec 実装: `~/.claude/skill-data/memory-vec/reindex.ts` (Phase C/D, post-review hardened)
- SessionStart hint: `.config/claude/scripts/runtime/memory-vec-hint-hook.py`
- Stop hook: `.config/claude/scripts/runtime/memory-vec-stop-hook.py`
- Codex 批評全文: cmux Worker run (2026-05-17 早朝)、`tokens used: 115,077`
