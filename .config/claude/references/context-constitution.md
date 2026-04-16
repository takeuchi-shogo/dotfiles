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

#### Context Rot の実測目安（タスク複雑度依存）

> 出典: Anthropic "Using Claude Code: Session Management & 1M Context" (2026-04) + NVIDIA RULER (arXiv:2404.06654)

1M context window でも実効的な有効帯域はタスクによって大きく変動する:

| タスク特性 | 実効有効帯域（目安） | 根拠 |
|-----------|-------------------|------|
| **単純抽出 / Needle-in-Haystack** | ~1M までほぼ劣化なし | RULER NIAH ベンチマークで実証 |
| **Multi-hop 推論 / 複雑なコードレビュー** | **~300-400k** で劣化が顕著化 | Anthropic 公式の observation、RULER multi-hop で指数的劣化 |
| **長期タスクの一貫性維持** | compaction 2-3 回目以降で急速に劣化 | Reset > Compaction 原則の実証根拠 |

**運用上の帰結:**

- `/check-context` が Edit 数 (20/30/50) で間接的に監視している閾値は、上記の multi-hop 帯域 (~300-400k) に対応する経験則
- Debug / refactor / architecture 判断のような multi-hop タスクは 300k 超で品質が落ちる前提で設計する
- 単純な情報抽出（grep 結果の分類、ドキュメント要約）は 1M 近くまで使い切ってよい
- **タスクの複雑度を測らずに「1M あるから大丈夫」と判断しない**

#### 動的関連性スコアリング（将来課題）

> Universal Verifier (Rosset et al., 2026): 分割統治型コンテキスト管理 — スクリーンショットを
> 基準ごとに関連性スコアリングして動的選別。

長セッション（compaction 2回以上）で context decay が発生した際、現在のタスク基準に対する
コンテキストの関連性を動的に再評価し、低関連性のコンテキストを優先的に刈り込む概念。

- **現状**: ルールベース4分類（Plan/Spec, References, Memory, Git状態）で十分に機能
- **将来の発動条件**: compaction 2回以上 + タスク切り替えが発生したセッション
- **実装方針**: 各コンテキストブロックにタスク関連性スコア (0.0-1.0) を付与し、閾値以下を圧縮対象とする
- **注意**: 実装は context decay の実データ蓄積後。現時点では概念定義のみ

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
