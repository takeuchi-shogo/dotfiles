---
date: 2026-04-17
source: "Building a Hermes Fleet Zero To Hero! Reproducing Moshe's Self-Hosted Agent Stack"
author: Weekend blog (reproducing @Mosescreates / Hermes)
type: integration-analysis
status: plan-generated
---

# Hermes Fleet 共有メモリ統合分析

## TL;DR
Qdrant + Ollama + mem0 + Claude Code Stop hook で「共有自己ホストメモリ」を構築する記事の分析結果。
dotfiles の既存資産（Stop hook → session-learner、OTel redactor、AutoEvolve）と重なる部分が多く、
Qdrant/Ollama/mem0 の「即導入」は不要と判定。代わりに (1) 既存 JSONL の secret 監査 (2) redactor 統合
(3) memory schema/retention 策定 (4) semantic search 小実験 の 4 タスクを取り込む。

## Phase 1: 記事の要点
### 主張
共有自己ホスト memory layer（Qdrant vector store + Ollama local embedding + mem0 abstraction）を
Claude Code の Stop hook から毎ターン書き込むことで、エージェント間（Telegram agent + Claude Code coder）で
コンテキストをシームレスに共有する。所有権ファースト > プラットフォームロックイン回避。

### 10 手法（キーワード付き）
1. Qdrant vector store（Docker bind-mount） — shared memory
2. Ollama local embeddings（nomic-embed-text） — offline embedding
3. mem0 as memory abstraction — unified API
4. Claude Code Stop hook → mem_broadcast.py — transcript 書き込み
5. Secret redactor（sk-/ghp_/Bearer） — write 前マスク
6. Native-only provider routing（allow_fallbacks: false） — silent fallback 禁止
7. Local fallback model（gemma2:9b） — 停止時継続
8. Idempotency keys（session_id + turn_index） — retry 重複防止
9. Happy Eyeballs IPv4 強制 — macOS mixed v4/v6 hang 回避
10. OLLAMA_NUM_PARALLEL / MAX_LOADED_MODELS チューニング — embedding starvation 回避

### 前提条件
- 自己ホストインフラが持てる（Docker + Ollama）
- セッション跨ぎ / エージェント跨ぎの context 共有が欲しい
- 2-6 agent profiles の小規模運用
- プラットフォーム依存を避けたい

## Phase 2: ギャップ分析（Pass 1 + Pass 2、Phase 2.5 で修正済み）

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Qdrant vector store | Gap（小実験のみ） | JSONL 記録のみ、semantic search なし |
| 2 | Ollama embeddings | Gap（#1 とセット） | 埋め込み層なし |
| 3 | mem0 abstraction | Partial | file-based memory で機能中、interface 評価価値あり |
| 6 | Provider pinning | Partial | Anthropic 固定。hook 内 LLM 等に思想適用余地 |
| 7 | Local fallback | Gap | 劣化運転設計（queueing/summary 継続）に ROI |
| 9 | IPv4 force | N/A | 現状接続問題なし |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 4 | Stop hook → session-learner.py / session-trace-store.py | レイテンシ・secret 素通り | レイテンシ計測、redactor 統合、schema/TTL 追加 |
| 5 | OTel redactor（redactor.go） | Claude hook 経路未統合 | Python ポート + session-learner 統合 |
| 8 | event_hash dedup | API retry 層は別 | 外部 store 連携時に備えて保留 |
| 10 | AutoEvolve proposal-pool.jsonl | 学習提案共有止まり | transcript 検索可能化 + schema/retention |

## Phase 2.5: Codex 批評統合

Codex の批評により以下を修正:
- #3 mem0: N/A → Partial（interface 評価として価値）
- #6 Provider pinning: N/A → Partial（思想として hook 内 LLM に適用）
- #7 Local fallback: 低優先 → Gap（劣化運転設計で ROI）

Codex 追加論点（4 項目、全て Phase 3 で Yes 選択）:
1. 🚨 既存 JSONL の secret 監査（最優先）
2. Memory schema + retention 方針策定
3. Semantic search は read-only 小実験に留める
4. mem0 は導入せず interface 評価（本レポートでは E 案として保留）

Gemini 周辺知識補完は応答取得に失敗したため、スキップ。

## Phase 3: ユーザー選別結果

| 項目 | 判定 |
|------|------|
| 🚨 既存 JSONL の secret 監査 | ✅ Yes |
| Secret redactor を Stop hook に統合 | ✅ Yes |
| Memory schema / retention 策定 | ✅ Yes |
| Semantic search 小実験 | ✅ Yes |

## Phase 4: 統合プラン

### 依存関係
- Track A: Task 1 (secret 監査) → Task 2 (redactor 統合)
- Track B: Task 3 (schema 策定) → Task 4 (semantic search 実験)
- A と B は並行可能

### Task 1: 既存 JSONL の secret 監査【S】
成果物: scripts/security/scan-jsonl-secrets.py + docs/security/2026-04-17-jsonl-secret-audit.md
対象: .config/claude/scripts/learner/ 配下の JSONL + ~/.claude/projects/*/**.jsonl
パターン: OTel redactor.go から移植（sk-*, ghp_*, Bearer *, 独自）

### Task 2: Secret redactor を Stop hook に統合【M】
前提: Task 1 完了
成果物:
- .config/claude/scripts/lib/redactor.py
- session-learner.py / session-trace-store.py 修正
検証: 適用前後 diff、hook レイテンシ < 300ms

### Task 3: Memory schema / retention 方針策定【M】
成果物:
- docs/specs/2026-04-17-memory-schema-retention.md
- .config/claude/references/memory-schema.md
- MEMORY.md 1 行ポインタ
区分: event(30日) / learning(永続) / proposal(7日) / summary(永続)

### Task 4: Semantic search 小実験【L】
前提: Task 3 完了
成果物: docs/experiments/2026-04-hermes-semantic-search/
- setup.sh（Qdrant Docker + Ollama）
- index.py（既存 JSONL → Qdrant read-only）
- eval.py（10 クエリ recall@5 計測）
- report.md
撤退条件: recall@5 < 0.5、latency > 500ms/q、setup > 4h

### 取り込まなかった項目（保留理由付き）
- #3 mem0 abstraction 導入: 現行 file-based で機能中。必要 API リストのみを Task 3 の schema 仕様に含める
- #6 Provider pinning: Anthropic 固定で即適用先なし。将来 hook 内 LLM 導入時に参照
- #9 IPv4 force: 現状問題なし

## 次のステップ
`docs/plans/2026-04-17-hermes-absorb-plan.md` を参照して `/rpi` or 手動実行。
