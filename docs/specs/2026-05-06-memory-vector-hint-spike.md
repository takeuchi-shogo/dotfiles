---
date: 2026-05-06
task: Memory vector hint layer spike (B2 from Hermes Fleet absorb plan)
status: draft
scope: ~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/**/*.md
references:
  - docs/specs/2026-04-17-memory-schema-retention.md  # 親 spec
  - docs/research/2026-04-17-hermes-fleet-shared-memory-analysis.md  # 先行判断
  - docs/research/2026-05-06-100-skills-best6-absorb-analysis.md  # T5 取り込み元
  - docs/plans/2026-04-17-hermes-absorb-plan.md
---

# Memory Vector Hint Layer Spike

## 目的

`~/.claude/projects/.../memory/*.md` (file-based MEMORY.md 体系) を embedding index に投入し、
semantic retrieval が **既存の file grep より明確に勝るか** を最小実装で実証する。

これは親 spec `2026-04-17-memory-schema-retention.md` の `mem0 互換 interface (保留)` セクションに
対応する **B2 実験** であり、Hermes Fleet absorb 時 (2026-04-17) に「semantic search は小実験のみ、
file-based で機能中」と判定した結論を改めて検証する。

## 設計境界 (絶対遵守)

Codex 警告「最大の罠 = MEMORY.md を semantic layer で置換 → source of truth と hint の境界を壊す」
を踏まえ、以下の境界を spec で固定する。違反した時点で abandon。

| 層 | 役割 | 編集可否 |
|----|------|---------|
| **Source of truth** | `~/.claude/projects/.../memory/*.md` (file-based) | spike では一切変更しない |
| **Hint layer (新規)** | `~/.claude/skill-data/memory-vec/index.db` (SQLite + sqlite-vec) | spike で新規追加、削除可 |
| **Auto-injection** | SessionStart hook で MEMORY.md を context に流し込む既存経路 | 変更しない |

**禁止事項**:
- file-based MEMORY.md の書き換え (read-only)
- vector index 結果を `auto memory` の自動注入経路に組み込むこと (この spike では path 提示のみ)
- Source of truth を SQLite に移すこと

## Acceptance Criteria

| # | 基準 | 検証方法 |
|---|------|---------|
| AC1 | node-sqlite-vec を使い、`memory/*.md` を embed して SQLite に格納できる | `node-sqlite-vec` skill の reference を参照、sqlite-vec extension load で実装 |
| AC2 | 自然言語クエリで関連 .md ファイルの **path + 該当 chunk 抜粋** を top-K で返せる | 5 個の query で再現確認 |
| AC3 | file-based MEMORY.md / 他 .md は変更されない (read-only 確認) | spike 前後で `~/.claude/projects/.../memory/*.md` の mtime 不変 |
| AC4 | **比較ベンチマーク**: 同じ 5 query を `grep -r` でも実行し、(a) recall (人間判断で関連と思える entry の hit 率)、(b) latency、(c) 結果の noise (無関係 hit 率) を比較 | spike report に表で記録 |
| AC5 | Hermes Fleet 2026-04 判断 (「小実験のみ」「file-based で機能中」) を **覆す根拠が出るか** | AC4 の結果を踏まえて Recommendation セクションに明記 |

## Experiment Design (Step 3.5: 必須)

### 定常状態

- `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md` は読み書き可能、wc -l で 200 行前後 (現状)
- 同 dir 配下の `.md` ファイル群は read 可能
- `task validate-configs` PASS
- 既存 SessionStart hook が MEMORY.md を context に注入する (現行通り)

### 仮説

「`memory/*.md` を embed (sqlite-vec, all-MiniLM-L6-v2 相当 or OpenAI ada-002 相当) し、自然言語 query で
semantic 検索すると、同じ query を `grep -ri` で実行するより (a) recall が +30% 以上、または (b) noise
(無関係 hit) が 50% 以下、の少なくとも片方を実証できる。なぜなら memory/*.md には「同義の異表記」(例:
'subagent' vs 'sub-agent', 'Codex Review Gate' vs 'codex-reviewer') が多く、grep は表記ゆらぎに弱い。」

仮説が反証されたら abandon → Hermes Fleet 判断を維持する。

### Blast Radius

- **隔離**: worktree `spike/memory-vector` で実装
- **影響範囲制御**:
  - `~/.claude/projects/.../memory/` は **絶対に書き換えない** (worktree 外、グローバル領域だが read-only 運用で隔離)
  - 新規ファイルはすべて worktree 内 `tmp/spike-memory-vec/` または `~/.claude/skill-data/memory-vec/` (後者は abandon 時に rm -rf 可)
  - hook 設定 (settings.json) は **触らない** (Stop hook 統合は次フェーズ)
- **ロールバック手順**: `~/.claude/skill-data/memory-vec/` を rm -rf + worktree 削除 で完全戻し
- **依存追加**: `node-sqlite-vec` (既に dotfiles に skill 存在)、Node 24+ (既にインストール済)

### 観察ポイント

1. embedding 生成の latency (1 file あたり ms)
2. SQLite index 生成の peak memory (大量 markdown でも OOM しないか)
3. query latency (top-5 取得まで)
4. AC4 の比較表 (semantic vs grep の 5 query 結果)

## Out of Scope (この spike で **やらない** こと)

- Stop hook で増分 indexing を発火させること (次フェーズ)
- SessionStart で結果を auto-inject すること (次フェーズ)
- vector index を auto memory システムに統合すること (Codex 警告の中核、別 spike)
- mem0 / Qdrant への移行 (本実験で sqlite-vec が不十分と判明したら別途検討)

## 成功時の次ステップ

AC1-AC4 PASS + AC5 で「覆す根拠あり」判定なら:
1. Stop hook 統合の spec を別 PR で作成 (memory write 後に増分 index)
2. SessionStart で「クエリベース hint」(path のみ提示、auto-load しない) を追加する spec を別 PR

## 失敗時の撤退条件

以下のいずれかで abandon:
- AC4 で grep と semantic に有意な差が出ない (現状の file-based で十分)
- embedding 計算が `memory/*.md` 全 50 ファイル弱で 30 秒超 (運用 cost 過大)
- sqlite-vec extension load が macOS で安定しない (環境依存リスク)
- AC3 違反 (file-based MEMORY.md が誤って変更される)

## 関連

- 親 spec: `docs/specs/2026-04-17-memory-schema-retention.md`
- 先行分析: `docs/research/2026-04-17-hermes-fleet-shared-memory-analysis.md`
- T5 取り込み元: `docs/research/2026-05-06-100-skills-best6-absorb-analysis.md`
- 利用 skill: `mizchi/skills` の `node-sqlite-vec`
