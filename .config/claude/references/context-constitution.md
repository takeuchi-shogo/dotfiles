# Context Constitution — コンテキスト管理の原則体系

> メモリはプラグインではない。メモリはハーネスそのものである。
> — Letta AI (MemGPT), 2026-04

コンテキスト管理はエージェントハーネスの中核責任。外部プラグインでは制御できない
不可視の意思決定（何をロードするか、何が圧縮を生き残るか、何を永続化するか）を
ハーネスが一貫した原則の下で行う。

---

## 7 Principles

### P1: Memory = Harness, not Plugin
コンテキスト管理を外部に委譲しない。CLAUDE.md のロード方法、compaction で何が残るか、
スキルメタデータの提示方法 — これらはすべてハーネスの設計決定。

### P2: Cheapest Layer First
安い層が高い層の発動を防ぐ。Tool Result Storage → Microcompaction → Session Memory →
Full Compaction の順に防御が escalate する。hook も Grep → Read → Agent の順。

### P3: Proactive > Reactive
コンテキスト消失を「検知してから対処」ではなく「消失前に退避」する。
PreCompact で key decisions を memory/ にフラッシュし、PostCompact で生存を検証する。

### P4: 4分類で保存先を決定
| 分類 | 問い | 保存先 |
|------|------|--------|
| Working | 今のタスクだけに必要？ | コンテキスト窓内 |
| Procedural | やり方・手順？ | Skills / references |
| Episodic | いつ何が起きた？ | learnings/*.jsonl (TTL付き) |
| Semantic | 変わりにくい事実？ | memory/*.md |

**Memory = "what"、Skill = "how"**。手順を memory に書かない。事実を skill に埋め込まない。

### P5: Mutual Exclusivity
メイン agent のメモリ書き込みと BG extraction は同時に走らない。
メイン agent の書き込みが優先。衝突を防ぐことで一貫性を保つ。

### P6: Compaction Survival Priorities
圧縮時の保持優先度は明示的に定義する（compact-instructions.md）:
1. アーキテクチャ決定と理由（絶対保持）
2. アクティブ Plan の未完了ステップ
3. 直近の変更ファイルと理由
4. 古いツール出力の詳細（削除可）

### P7: Build to Delete
ハーネスのメモリ管理機構は過渡的技術。次世代モデルの compaction 品質向上で
不要になりうる。軽量・モジュラーに保ち、削除コストを最小化する。

## P8: Task-Scoped Context Injection（タスク粒度のコンテキスト注入）

> 出典: Claude Code 内部アーキテクチャ — system-reminder タグによるキャッシュ安定なコンテキスト注入。

タスクごとに「何を・いつ・どの粒度で持ち込むか」を制御する:

| コンテキスト種別 | 注入タイミング | 粒度ガイド |
|----------------|-------------|-----------|
| **Plan/Spec** | タスク開始時 | 全文（短いなら）or 該当セクションのみ |
| **References** | 必要時に遅延ロード | Progressive Disclosure に従う |
| **Memory** | セッション開始時（自動） | MEMORY.md のインデックスのみ。詳細は Read |
| **Git状態** | 各ターン（自動） | CC が system-reminder で注入 |
| **ツール結果** | ツール実行後 | resource-bounds.md の Output Offload 閾値に従う |

**原則**: 静的コンテキスト（変わらない）はシステムプロンプト側に、動的コンテキスト（ターンごとに変わる）はユーザーメッセージ側に配置するとキャッシュ効率が最大化される。CC 内部ではこれを SYSTEM_PROMPT_DYNAMIC_BOUNDARY で実現している。

---

## Layer Architecture (7層)

詳細: `cc-7-layer-memory-model.md`

| Layer | 名称 | ハーネス介入 |
|-------|------|-------------|
| 1 | Tool Result Storage | 不可 (CC内蔵) |
| 2 | Microcompaction | 不可 (CC内蔵) |
| 3 | Session Memory | 間接的 (checkpoint で補完) |
| 4 | Full Compaction | **可能** — PreCompact/PostCompact hook |
| 5 | Auto Memory Extraction | **可能** — memory/ 構造管理 |
| 6 | Dreaming | 間接的 — memory/ 品質が効果を左右 |
| 7 | Cross-Agent Communication | **可能** — Agent 定義、worktree 隔離 |

---

## Policy Files (詳細実装)

| ポリシー | ファイル | 管轄 |
|----------|---------|------|
| 何を保存するか | `memory-safety-policy.md` | P4, P5 |
| 圧縮時の優先度 | `compact-instructions.md` | P2, P6 |
| 圧縮の監視と回復 | `context-compaction-policy.md` | P3 |
| 7層アーキテクチャ | `cc-7-layer-memory-model.md` | P2, 全体 |

---

## Anti-Patterns

| NG | なぜ |
|----|------|
| メモリを外部 RAG サービスに委譲 | P1 違反。ハーネスの不可視決定を制御できない |
| compaction 後の状態を検証しない | P3 違反。reactive のみでは消失を見逃す |
| 全情報を永続化する | P4 違反。Working memory まで永続化するとノイズが増大 |
| session 終了時にしかメモリを整理しない | P3 違反。長時間セッションで compaction 前に情報が消失 |
| メモリ管理の hook を重くする | P7 違反。15秒の hook は compaction を遅延させる |
