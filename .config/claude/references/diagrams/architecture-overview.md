# Architecture Overview: Harness 4-Layer + AutoEvolve

Claude Code ハーネスの4層 hook アーキテクチャと AutoEvolve 自己改善ループの全体構造。

**データソース**: `.config/claude/scripts/` 各ディレクトリ、`CLAUDE.md`、`references/workflow-guide.md`

```mermaid
graph TD
    CC["Claude Code 本体<br/>(Coordinator)"]

    subgraph hooks ["Hook 4-Layer"]
        direction TB
        RT["Runtime Layer<br/>scripts/runtime/"]
        PL["Policy Layer<br/>scripts/policy/"]
        LC["Lifecycle Layer<br/>scripts/lifecycle/"]
        LR["Learner Layer<br/>scripts/learner/"]
    end

    subgraph rt_hooks ["Runtime 代表"]
        RT1["auto-format.js"]
        RT2["output-offload.py"]
        RT3["session-load.js / session-save.js"]
    end

    subgraph pl_hooks ["Policy 代表"]
        PL1["golden-check.py"]
        PL2["completion-gate.py"]
        PL3["prompt-injection-detector.py"]
    end

    subgraph lc_hooks ["Lifecycle 代表"]
        LC1["plan-lifecycle.py"]
        LC2["doc-garden-check.py"]
        LC3["context-drift-check.py"]
    end

    subgraph lr_hooks ["Learner 代表"]
        LR1["session-learner.py"]
        LR2["edit-failure-tracker.py"]
        LR3["skill-usage-tracker.py"]
    end

    LIB["lib/ 共有基盤<br/>hook_utils.py, storage.py,<br/>session_events.py, rl_advantage.py"]

    CC --> RT
    CC --> PL
    CC --> LC
    CC --> LR
    RT --- rt_hooks
    PL --- pl_hooks
    LC --- lc_hooks
    LR --- lr_hooks
    RT -.->|import| LIB
    PL -.->|import| LIB
    LC -.->|import| LIB
    LR -.->|import| LIB

    subgraph autoevolve ["AutoEvolve Self-Improvement Loop"]
        direction LR
        AE1["Session<br/>セッション単位の学習"]
        AE2["Daily<br/>日次パターン集約"]
        AE3["Background<br/>バックグラウンド改善"]
        AE4["On-demand<br/>/improve 手動起動"]
        AE1 --> AE2 --> AE3 --> AE4 --> AE1
    end

    LR -->|feeds| AE1
    AE3 -.->|updates| hooks
```

## 補足

- **Runtime**: セッション開始/終了、フォーマット、出力管理など実行時の自動処理を担当
- **Policy**: コード品質ゲート、セキュリティ検査、完了条件の強制など品質ポリシーを担当
- **Lifecycle**: Plan の状態管理、ドキュメント鮮度チェック、コンテキストドリフト検出を担当
- **Learner**: セッションからの学習、失敗パターン追跡、スキル使用状況の記録を担当
- **lib/**: 全レイヤーが共有するユーティリティ。`hook_utils.py` のパス解決、`storage.py` の永続化など
- **AutoEvolve**: Learner 層が収集したデータを元に、Session -> Daily -> Background -> On-demand の4段階で自己改善を回す。1サイクルで最大3ファイルの変更に制限される安全機構あり
