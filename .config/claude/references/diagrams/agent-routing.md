# Agent Routing: Triage-Router Decision Flow

ユーザータスク入力から専門エージェントへのルーティングフロー。hooks による自動推奨と triage-router による分類を示す。

**データソース**: `references/agent-orchestration-map.md`、`references/workflow-guide.md` (L246-286)

```mermaid
flowchart LR
    INPUT(["User Task Input"])

    subgraph hooks ["Auto-Detection Hooks"]
        AR["agent-router.py<br/>(keyword detection)"]
        FPR["file-pattern-router.py<br/>(file pattern detection)"]
        ETC["error-to-codex.py<br/>(Bash error)"]
        SG["suggest-gemini.py<br/>(large-scale analysis)"]
        PTA["post-test-analysis.py<br/>(test failure)"]
    end

    INPUT --> AR
    INPUT --> FPR
    INPUT --> ETC
    INPUT --> SG
    INPUT --> PTA

    CC["Claude Code<br/>(Coordinator)"]
    AR -->|"additionalContext<br/>(recommend)"| CC
    FPR -->|"additionalContext<br/>(recommend)"| CC
    ETC -->|"additionalContext"| CC
    SG -->|"additionalContext"| CC
    PTA -->|"additionalContext"| CC

    CC -->|"unclear task"| TR["triage-router<br/>(Classifier)"]
    CC -->|"clear task"| DIRECT["Direct Dispatch"]

    TR --> ARCH["backend-architect<br/>API/DB Design"]
    TR --> FE["frontend-developer<br/>React/UI"]
    TR --> TE["test-engineer<br/>Test Creation"]
    TR --> DBG["debugger<br/>Bug Investigation"]
    TR --> SEC["security-reviewer<br/>Vulnerability Scan"]
    TR --> BF["build-fixer<br/>Build Errors"]
    TR --> LANG["golang-pro / typescript-pro<br/>Language Specialists"]

    DIRECT --> ARCH
    DIRECT --> FE
    DIRECT --> TE
    DIRECT --> DBG

    ETC -.->|"error path"| CDXD["codex-debugger<br/>Deep Error Analysis"]
    SG -.->|"large analysis"| GEM["gemini-explore<br/>1M Context / Research"]
    PTA -.->|"test failure"| TA["test-analyzer<br/>Failure Analysis"]

    subgraph external ["External Model Delegation"]
        CDXD
        CDXR["codex-risk-reviewer<br/>Risk Analysis"]
        GEM
    end
```

## 補足

- **Implicit Coordinator Pattern**: 明示的な orchestrator は存在しない。Claude Code 本体が全ての意思決定権を持ち、hooks は「推奨」のみ行う（強制しない）
- **Hook の役割**: `agent-router.py` はタスクキーワードから、`file-pattern-router.py` はファイル拡張子パターンから最適なエージェントを推奨する。いずれも `additionalContext` でメインコンテキストに情報を追加するだけ
- **triage-router**: hooks で判断がつかない不明瞭なタスクに対して、種別を判定して最適エージェントにルーティングする Classifier エージェント
- **外部モデル委譲**: Codex（深い推論、リスク分析）と Gemini（1M コンテキスト分析、リサーチ）は、Claude Code 単体で処理が難しいタスクに対して起動される
- **全31エージェント**のうち、代表的なものだけを図示。完全なルーティングテーブルは `agent-orchestration-map.md` と `workflow-guide.md` を参照
