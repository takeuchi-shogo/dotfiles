---
status: reference
last_reviewed: 2026-04-23
---

# Claude Code 7層メモリモデル

> 出典: "How Anthropic Built 7 Layers of Memory" (2026-04) — CC 内部アーキテクチャのリバースエンジニアリング

CC のコンテキスト管理は7層の階層的防御で構成される。**安い層が高い層の発動を防ぐ**設計。

## 7層の概要

| Layer | 名称 | コスト | トリガー | ハーネス介入 |
|-------|------|--------|---------|-------------|
| 1 | Tool Result Storage | Disk I/O のみ | 毎ツール結果 | **不可** (CC 内蔵) |
| 2 | Microcompaction | ゼロ〜極小 | 毎ターン（API呼び出し前） | **不可** (CC 内蔵) |
| 3 | Session Memory | Fork 1回 | 定期的（トークン成長+ツール呼び出し閾値） | **間接的** — テンプレート構造に影響なし。checkpoint スキルで補完 |
| 4 | Full Compaction | API 1回 | autocompact 閾値超過 + SM compaction 不可 | **可能** — PreCompact hook で状態保存。compact-instructions.md で優先度制御 |
| 5 | Auto Memory Extraction | Fork 1回 | クエリループ終了時 | **可能** — MEMORY.md / memory/ で永続知識管理 |
| 6 | Dreaming | Fork 1回（複数ターン） | バックグラウンド（時間+セッション蓄積） | **間接的** — memory/ の構造品質が Dreaming の効果を左右 |
| 7 | Cross-Agent Communication | 可変 | Agent spawn, BG task | **可能** — Agent 定義、SendMessage、worktree 隔離 |

## ハーネスの介入ポイント

### Layer 4: Full Compaction（最も介入効果が高い）

- **PreCompact hook** (`pre-compact-save.js`): compaction 直前に git 状態を保存
- **compact-instructions.md**: 圧縮時の保留優先度を定義。CC の summarizer がこれを参照
- **Re-grounding ルール** (`resource-bounds.md`): compaction 後の再読み込み手順

### Layer 5: Auto Memory Extraction

- **memory/ ディレクトリ構造**: 4種のメモリタイプ (user/feedback/project/reference)
- **MEMORY.md**: 200行/25KB の索引。Dreaming (Layer 6) も参照
- **メイン agent との相互排他**: メイン agent がメモリを書いたターンでは extraction がスキップされる → メイン agent でメモリを書く方が優先度が高い

### Layer 6: Dreaming

- **memory/ の品質**: Dreaming は memory/ を整理する。入力品質（=ハーネスが管理する memory/）が出力品質を決定
- **MEMORY.md の 200行制限**: 超過すると truncate される。索引を簡潔に保つことで Dreaming の効果を最大化

### Layer 7: Cross-Agent Communication

- **Agent 定義** (agents/*.md): omitClaudeMd, disallowedTools, effort 等で fork のコスト制御
- **CacheSafeParams**: fork は親のプロンプトキャッシュを共有。CLAUDE.md/settings.json のセッション途中変更はキャッシュを破壊
- **worktree 隔離**: 並列 agent で filesystem 競合を防止

#### Concurrent Write Constraints

> 出典: Anthropic "Multi-agent coordination patterns" (2026-04-10) §Shared State — 中央コーディネーター不在で複数エージェントが永続ストアに同時書き込みする際の collision リスク。
>
> 関連: `references/multi-agent-coordination-patterns.md § Pattern 5 Shared State`

Layer 7 で複数エージェントが同一の永続ストアに書き込む場合、以下のリスクが顕在化する。

| リスク | 発生条件 | 現状の影響度 |
|---|---|---|
| **Last-Write-Wins**: `agent-memory/<agent>/` 配下への複数エージェント同時書き込みで前の書き込みが上書きされる | 並列度 N=2 以上で同じファイルに append しない write を行う | 低 — 各 agent が自身の subdirectory に partition されているため通常は衝突しない |
| **Append 競合**: `task-registry.jsonl` への並列 append | 並列度 N=2 以上で同じ jsonl に書く | 低 — 現状は `/autonomous` の単一ランナーのみが書き込む。複数 async 起動で発火させる場合は file lock が必要 |
| **Obsidian Vault 同期ドリフト**: `sync-memory-to-vault.sh` の実行中に source 側が書き換わる | sync 中に並列で memory 書き込み | 低 — 単方向・非同期同期でデフォルトは race window が短い |

#### 現在の Mitigation

dotfiles の Layer 7 が現状 race condition で実害を出していない理由は以下の構造的制約によるもの:

1. **書き込み先の partition**: agent-memory は `<agent_name>/` でディレクトリ分離、ほぼ衝突しない
2. **単一ランナー前提**: task-registry.jsonl への書き込みは現状 `/autonomous` 経由のみ
3. **並列度 N ≤ 3**: 通常運用で並列サブエージェントは 3 以下（`subagent-delegation-guide.md § Coordinator Context Budget` の Safe zone）
4. **単方向同期**: agent-memory → Vault は単方向、Vault → agent-memory への書き戻しなし

#### 並列度上昇時の再評価ポイント

以下のいずれかを満たした場合、Concurrent Write Constraints を再評価する必要がある:

- 並列サブエージェントが常に 5+ で稼働する運用に変わる
- 複数の async ランナーが同時に `task-registry.jsonl` に register するワークフローを追加する
- agent-memory への書き込みが ディレクトリ partition を超える（複数 agent が同じファイルを更新）
- Obsidian Vault → agent-memory の **書き戻し** を実装する

#### 将来の CRDT 検討

記事は LangGraph state graph 等の CRDT 採用例に言及しているが、dotfiles では**現状採用しない**:

- 採用条件: 並列度 5+ が常態化し、上記いずれかの mitigation が破綻した場合
- 候補: jsonl への lock-free append + 外部 reducer での conflict 解消、ファイルベース CRDT（automerge 等）
- それまでは「並列度を抑える」「書き込み先を partition する」のシンプルな mitigation で十分

#### 関連参照

- `references/multi-agent-coordination-patterns.md § Pattern 5 Shared State` — 5-Pattern View での位置づけ
- `references/task-registry-schema.md § agent-invocations.jsonl との棲み分け` — task-registry.jsonl の write 経路
- `references/subagent-delegation-guide.md § Coordinator Context Budget` — 並列度の運用ガイド

## 設計原則（ハーネス設計への含意）

| CC の原則 | ハーネスへの適用 |
|-----------|----------------|
| **Cheapest First** | hook は軽量チェック→重いチェックの順。Grep/Glob → Read → Agent |
| **Circuit Breaker** | 3回連続失敗で停止。stagnation-detector が部分実装 |
| **Graceful Degradation** | hook 失敗は警告のみ。タスク全体を止めない |
| **Mutual Exclusivity** | Main writes ↔ BG extraction。同時書き込みを防ぐ |
| **Prompt Cache Preservation** | CLAUDE.md/settings.json のセッション途中変更を避ける |

## 参照

- `compact-instructions.md` — Layer 4 の圧縮戦略
- `resource-bounds.md` — 閾値と CC 内部定数
- `improve-policy.md` — Layer 6 Dreaming → /improve の対応
- `failure-taxonomy.md` — Circuit Breaker パターン
