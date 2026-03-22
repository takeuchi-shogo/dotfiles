# Context Lifecycle: Token Budget Management

セッション開始からコンテキスト圧縮・委譲・完了までのライフサイクルを示す。

**データソース**: `references/workflow-guide.md` (L397-443)

```mermaid
sequenceDiagram
    participant U as User
    participant CC as Claude Code
    participant MEM as CLAUDE.md + MEMORY.md
    participant SUB as Subagent
    participant CP as Checkpoint

    Note over CC: Session Start

    CC->>MEM: Load CLAUDE.md (instructions)
    CC->>MEM: Load MEMORY.md (persistent knowledge)
    MEM-->>CC: Context initialized

    U->>CC: Task request

    rect rgb(200, 230, 200)
        Note over CC: ~70% context usage<br/>Normal operation
        CC->>CC: Plan / Implement / Test
        CC->>CC: Read files, run commands
    end

    rect rgb(255, 240, 200)
        Note over CC: ~80% context usage<br/>WARNING zone
        CC->>CC: Compress unnecessary context
        CC->>CC: Use offset/limit for large files
        CC->>CC: Summarize investigation results
    end

    rect rgb(255, 210, 210)
        Note over CC: ~90% context usage<br/>CRITICAL zone
        alt Delegate to subagent
            CC->>SUB: Delegate remaining work<br/>(fresh context)
            SUB-->>CC: Return results (summarized)
        else Checkpoint and new session
            CC->>CP: Save state via /checkpoint
            CP-->>CC: State persisted
            Note over CC: Start new session
            CC->>MEM: Reload CLAUDE.md + MEMORY.md
            CC->>CP: Restore checkpoint
        end
    end

    CC->>CC: Verify completion
    CC-->>U: Task result

    Note over CC: Session End
    CC->>MEM: Update MEMORY.md<br/>(if new patterns found)
```

## 補足

- **Lost-in-the-middle 対策**: 重要情報はコンテキストの先頭と末尾に配置する。中間部に埋もれた情報は見落とされやすい
- **Context Placement Strategy**: サブエージェントへの指示は「目的 -> 制約 -> 入力データ -> 出力形式」の順で構造化する
- **セッション分離原則**: 1セッション1タスクが原則。無関係なタスクを混ぜると autocompact 後に前タスクの仮定が残留し、品質が低下する
- **Persistent Facts Block**: 圧縮されても残すべき事実は MEMORY.md に永続化する。Session -> MEMORY.md -> Skill の3層メモリ構造で知見を段階的に昇格させる
- **トークン節約テクニック**: 大きなファイルは必要部分だけ Read（offset/limit 指定）、長い出力は head/tail でフィルタ、独立タスクはサブエージェントに並列委譲
