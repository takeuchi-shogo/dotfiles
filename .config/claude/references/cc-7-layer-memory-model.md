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
