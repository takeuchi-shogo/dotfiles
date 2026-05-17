---
source: "https://github.com/giancarloerra/SocratiCode"
date: 2026-05-17
status: integrated
absorb_run: 3rd codebase-intelligence (1st=CRG adopted 2026-03-30, 2nd=graphify rejected 2026-04-27)
---

# SocratiCode absorb 分析 (2026-05-17)

## Source Summary

**主張**: Codebase intelligence MCP server (Docker 自動: Qdrant + Ollama)。VS Code 2.45M LOC bench (Opus 4.6) で grep-based AI に対し **61% less context / 84% fewer calls / 37x faster**。enterprise 40M+ LOC 対応。AGPL-3.0 + LICENSE-COMMERCIAL dual。2640⭐ / 348 forks / 2026-02-26 created。著者 Giancarlo Erra (Altaire Limited)、homepage socraticode.cloud (Cloud beta upsell)、sibling JanuScope (MCP policy proxy)。

**手法 (18 項目)**:

1. Search-Before-Reading 規律 (Goal → Tool 表を agent instruction に内蔵)
2. Hybrid semantic+BM25 RRF-fused search (Qdrant)
3. AST-aware chunking (ast-grep 18 言語)
4. Polyglot dependency graph + circular detection
5. Symbol-level impact analysis (blast radius) + transitive callers
6. Call-flow tracing forward (auto-detect entry points: main/routes/tests)
7. Symbol 360° view (definition + callers + callees + tests)
8. Context artifacts (DB schema/OpenAPI/proto/k8s/Terraform 横断 index)
9. Interactive HTML graph explorer (Cytoscape vendored offline)
10. Resumable indexing checkpoints
11. Multi-agent shared index with cross-process detection
12. File watcher 自動 incremental (@parcel/watcher)
13. AGENTS.md = CLAUDE.md = GEMINI.md triplicate (identical content)
14. Plugin format (.claude-plugin/marketplace.json + skills + agents + hooks 同梱)
15. Goal → Tool quick reference table in agent instructions
16. MCP duplicate detection SessionStart hook (plugin+standalone prefix collision)
17. Pre-computed expensive operations (smaller models が architectural query 可能)
18. Sibling JanuScope (MCP governance: tool blocking / SQL gate / PII redaction / audit / rate-limit)

**根拠**: README 4.5K LOC、benchmark セクション、stars history。

**前提条件**: Docker Desktop 必須、enterprise repo 想定、著者 vendor (socraticode.cloud Cloud beta + JanuScope パッケージ販売)。

## Phase 2: Gap Analysis (Pass 1 + Pass 2 統合)

### Gap / Partial / N/A 一次判定

| # | 手法 | 判定 | 現状 / Pruning-First 根拠 |
|---|------|------|------|
| 8 | Context artifacts (DB schema/OpenAPI/proto/k8s) | **Partial (Phase 2.5 で修正)** | CRG はコードのみ。dotfiles docs/research+specs+references で 478 files/4MB あり semantic 需要あるが、SocratiCode 方式は overkill。memory-vec 拡張で代替検討 |
| 9 | Interactive HTML graph explorer | N/A | `codebase-graph-benchmarks.md` L61 で vis.js 系 YAGNI 棄却済 (cosmograph.app 等を採用しない方針) |
| 10 | Resumable indexing checkpoints | N/A | CRG は SQLite local rebuild < 2s で resumable 不要 |
| 13 | AGENTS=CLAUDE=GEMINI triplicate (identical content) | N/A (意図的差別化) | scope 別: CLAUDE 29行 / AGENTS 100行 / .codex 154行 / .gemini/GEMINI 36行 で正解 (Codex 確認済み) |
| 14 | Plugin marketplace.json | N/A | dotfiles は配布対象でない、個人セットアップ |
| 16 | MCP duplicate prefix detection SessionStart hook | **Gap (XS、降格)** | SocratiCode を入れないなら YAGNI、audit checklist memo として保留 |
| 17 | Pre-computed expensive ops | N/A | CRG が既に提供 (cached blast radius) |
| 18 sub | JanuScope features (PII/SQL gate) | N/A | 個人 dotfiles で SQL/DB 触らない |

### Already 強化分析

| # | 既存仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|----------|-----------|--------|------|
| 1 | search-first workflow (CLAUDE.md L42 + `search-first-gate.py`) | agent instruction ごとの Goal→Tool 表が薄い | decision-tables-index.md 集中管理が DRY 上優位 | 強化不要 |
| 2 | memory-vec Phase D 実装済 (`memory-vec-hint-hook.py` + `index.db 1.7MB` + `reindex.ts`) | scope が memory/*.md のみ、docs/research/specs/references 未カバー | scope 拡張 eval spike (別 plan) | **強化可能 (eval-only)** |
| 3 | ast-grep skill (`ast-grep-practice/`) | — | カバー済 | 強化不要 |
| 4 | CRG 18言語 polyglot graph (`code-review-graph-guide.md`) | **循環依存検出独立ツール無し** (`flows.py` 内の無限ループ防止のみ) | guide に limitation 補足 + 回避策 (madge/pylint) | **強化可能 (S)** |
| 5-7 | CRG `get_impact_radius_tool` / `list_flows_tool` / `query_graph_tool` | — | カバー済 | 強化不要 |
| 11 | `multi-agent-coordination-patterns.md` Pattern 5 Shared State | cross-process detection は file-lock ベース | 個人利用想定で multi-process 衝突想定不要 | 強化不要 |
| 12 | CRG は auto-watch 不採用 (`code-review-graph-guide.md` L65、hook 衝突回避の意図) | SocratiCode は @parcel/watcher 自動 | 意図的判断、変更不要 | 強化不要 |
| 15 | `decision-tables-index.md` 集中索引 | 個別 agent 配置 | DRY 違反、現状の集中配置が優位 | 強化不要 |
| 18 main | `mcp-audit.py` scope enforcement + dangerous prefix block | prefix collision detection 未実装 | 即実装は YAGNI、checklist memo へ降格 | 降格 |

## Phase 2.5: Refine (Codex + Gemini 並列批評)

### Codex 批評 (212KB 出力)

**Codex 主要訂正:**
1. **見落とし 賛同**: branch-aware indexing / cross-project search / Cloud SSO/VPC が Phase 1 表に独立項目として欠落。dotfiles では worktree 分離が原則のため採用価値は低い
2. **#16 反対寄り**: SocratiCode 自体を入れないなら即実装は YAGNI、優先度 #4 より下
3. **#13 賛同**: scope 別が repo 設計、コピー同期は害
4. **#8 重要訂正**: N/A → **Partial/保留**。docs/research (60+ absorb)・docs/specs・references で **478 files / 4MB**、semantic query 需要あり。SocratiCode 方式ではなく既存 memory-vec hint の対象拡張を eval 付きで検討
5. **#2 重要訂正**: 「強化不要」は強すぎる。CRG `semantic_search_nodes_tool` は code-symbol 寄りで、absorb 履歴・設計メモの semantic 検索とは別問題。memory-vec Phase D (`memory-vec-hint-hook.py` + `~/.claude/skill-data/memory-vec/{index.db,reindex.ts}` 実装済) で対応すべき
6. **前提誤り 賛同**: CRG/SocratiCode の差は構造 graph ではなく conceptual semantic retrieval。memory-vec Phase B/D で「semantic が grep より勝つケース」が確認済、SessionStart hint まで実装済。「semantic 不要」は誤り、ただし「SocratiCode 必要」は飛躍
7. **ベンチ主張 反対寄り**: 61%/84%/37x は grep-only baseline で `codebase-graph-benchmarks.md` L34「一般コードベース 5-15x 収束」教訓と整合させ vendor claim 扱い
8. **Pruning-First 整合性**: 現案 `#16+#4` はやや違反。**最終アクション = #4 のみ採用、#16 は実害 or plugin 導入時まで待つのが妥当**

### Gemini 結果

**完全失敗** (quota 枯渇): `gemini-3-flash-preview` および `gemini-2.5-pro` の両方で 10 attempts max まで `RetryableQuotaError: You have exhausted your capacity on this model`。出力 5KB は全部 retry error log。

**Phase 2.5 limitation**: Codex 単独批評 (model-family diversity による bias mitigation が弱い)。Opus self-preference の可能性が残るが、Codex の指摘で **memory-vec Phase D 実装済の事実** + **#2/#8 の判定誤り** を補正できたため、決定的な見落としは無いと判断。

## Integration Decisions

### 採用項目

| # | 項目 | 規模 | アクション |
|---|------|------|----------|
| **#4** | CRG 循環依存検出の現状を `code-review-graph-guide.md` に補足 | S (1 ファイル、+15 行) | 編集完了 |
| **#16 降格版** | MCP plugin 導入時の prefix collision audit checklist memo | XS (mcp-audit.py + decision-tables-index.md 各 1-6 行) | 編集完了 |
| **#2+#8 統合 eval spike** | memory-vec scope を docs/research+specs+references に拡張する評価 spike | M (plan only) | plan 保存 |

### 棄却項目 (Pruning-First 違反)

- **#1 (Goal→Tool 表)**: 強化不要、`decision-tables-index.md` 集中管理が DRY 優位
- **#3 (AST-aware chunking)**: カバー済
- **#5-7 (impact/flow/symbol)**: CRG でカバー済
- **#8 broad (SocratiCode 方式の DB/API artifact)**: SocratiCode 本体採用不要、軽量代替で十分
- **#9 (HTML graph)**: graphify 棄却済の方針
- **#10 (resumable indexing)**: CRG 不要
- **#11 (multi-agent shared index)**: 個人利用想定外
- **#12 (file watcher 自動化)**: CRG 意図的 off
- **#13 (triplicate)**: scope 別差異が正解、同期は害
- **#14 (plugin format)**: 配布対象外
- **#15 (per-agent Goal→Tool 表)**: DRY 違反
- **#17 (pre-compute)**: CRG 提供済み
- **#18 sub (JanuScope features)**: 用途外
- **SocratiCode 本体採用**: AGPL-3.0 + Docker + Qdrant + Ollama の運用コストが CRG vs head-to-head ベンチ無しで正当化不能、Pruning-First 違反

## Plan

### Task 1: code-review-graph-guide.md に循環依存 limitation 追記 (#4)
- **Files**: `.config/claude/references/code-review-graph-guide.md` (+15 行、新 section「循環依存検出の取り扱い」追加)
- **Changes**: CRG `flows.py` 内 cycle 検出は flow traversal の無限ループ防止のみ、SocratiCode `codebase_graph_circular` 相当の独立ツールは未公開。回避策 (madge/pylint、CRG 上流 issue) を記録
- **Size**: S
- **Status**: 完了

### Task 2: mcp-audit.py + decision-tables-index.md に audit checklist memo (#16 降格版)
- **Files**: `.config/claude/scripts/policy/mcp-audit.py` (+6 行 inline comment near DANGEROUS_MCP_PREFIXES), `.config/claude/references/decision-tables-index.md` (+1 行 Evaluation/Gate 表に行追加)
- **Changes**: 次回 MCP plugin 導入時 `mcp__plugin_X_X__Y` と `mcp__X__Y` の重複登録チェックを実施する旨を memo
- **Size**: XS
- **Status**: 完了

### Task 3: memory-vec scope 拡張 eval spike plan
- **Files**: `docs/plans/2026-05-17-memory-vec-scope-extension-spike.md` (新規)
- **Changes**: memory-vec reindex 対象を docs/research+specs+references (478 files/4MB) に拡張した場合の indexing time / disk size / hint quality を計測する spike プラン (実装ではない)
- **Size**: M (plan)
- **Status**: 完了

### Task 4: MEMORY.md ポインタ追加
- **Files**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`
- **Changes**: 1 行ポインタ追記 (Pruning-First で 1 件採用 + 1 件降格 + 1 件 spike 保留、Codex 批評で削減)
- **Size**: XS
- **Status**: Phase 5 で実施

## Lessons Learned

1. **Codex CLI 仕様変更**: `codex exec -q` の `-q` フラグは廃止 (現行: `codex exec [OPTIONS] [PROMPT]` のみ)。`scripts/runtime/launch-worker.sh:112` に同じバグあり (修正は別タスク、本 absorb のスコープ外)
2. **cmux launch-worker.sh の surface:1 ハードコード**: 新規 workspace で `surface:1` は global surface ID と衝突。動的に `cmux list-panels --workspace WS` で resolve すべき (バグ報告のみ、本 absorb のスコープ外)
3. **Gemini quota fragility**: `gemini-3-flash-preview` / `gemini-2.5-pro` の両モデルで Phase 2.5 当日 (UTC 2026-05-17 早朝) に quota 完全枯渇。Phase 2.5 を Codex 単独で進める運用パターンが現実的に必要 (Codex stall パターンの 2026-05-16 Zed absorb と対称的な失敗モード)
4. **3 度目の同分野 absorb**: codebase intelligence は CRG 採用済・graphify 棄却済で、SocratiCode を含む新規ツールは Pruning-First で原則 reject。重要なのは「既存資産の弱点を具体的に強化する」観点 (今回は #4 limitation 記録 + #2 memory-vec scope eval)

## Sources

- SocratiCode: https://github.com/giancarloerra/SocratiCode (giancarloerra/Altaire Limited, AGPL-3.0)
- Sibling JanuScope: https://github.com/giancarloerra/januscope (MCP policy proxy)
- 既存 CRG ガイド: `.config/claude/references/code-review-graph-guide.md`
- ベンチ比較表: `.config/claude/references/codebase-graph-benchmarks.md`
- 過去 absorb: `docs/research/2026-03-30-code-review-graph-analysis.md` (CRG 採用) / `docs/research/2026-04-27-graphify-absorb-analysis.md` (graphify 棄却) / `docs/research/2026-04-17-hermes-fleet-shared-memory-analysis.md` (Hermes Qdrant 実験)
