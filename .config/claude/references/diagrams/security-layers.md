---
status: reference
last_reviewed: 2026-04-23
---

# Security Layers: Hook Chain + MCP Audit

入力から実行までのセキュリティ hook チェーンと MCP 監査パスを示す。

**データソース**: `scripts/policy/` ディレクトリ一覧、`references/workflow-guide.md`

```mermaid
flowchart TD
    INPUT(["User / Agent Input"])

    INPUT --> PID["prompt-injection-detector.py<br/>Prompt Injection Detection"]

    PID -->|"Clean"| ASF["agentshield-filter.py<br/>Agent Shield Filtering"]
    PID -->|"Injection detected"| BLOCK1["BLOCKED<br/>Notify user"]

    ASF -->|"Pass"| PLC["protect-linter-config.py<br/>Lint Config Protection"]
    ASF -->|"Suspicious"| BLOCK2["BLOCKED<br/>Notify user"]

    PLC -->|"Not lint config"| SFG["search-first-gate.py<br/>Search Before Implement"]
    PLC -->|"Lint config edit"| BLOCK3["BLOCKED<br/>Fix code, not config"]

    SFG --> GC["golden-check.py<br/>Golden Principles Check"]

    GC --> FPG["file-proliferation-guard.py<br/>File Creation Limit"]

    FPG --> TSE["tool-scope-enforcer.py<br/>Tool Scope Enforcement"]

    TSE --> DS["docker-safety.py<br/>Docker Safety Check"]

    DS --> EXEC{{"Execution"}}

    EXEC --> CG["completion-gate.py<br/>Completion Verification Gate"]

    CG -->|"Verified"| DONE(["Safe Output"])
    CG -->|"Not verified"| BACK["Return to Implementation"]

    INPUT --> MCP["mcp-audit.py<br/>MCP Server Audit"]
    MCP -->|"Safe"| EXEC
    MCP -->|"Suspicious"| BLOCK4["BLOCKED<br/>MCP violation logged"]

    INPUT --> SSS["skill-security-scan.py<br/>Skill Security Scan"]
    SSS -->|"Clean"| EXEC
    SSS -->|"Risk found"| BLOCK5["BLOCKED<br/>Skill risk flagged"]

    subgraph post_exec ["Post-Execution Checks"]
        RFT["review-feedback-tracker.py<br/>Review Feedback Tracking"]
        GD["gaming-detector.py<br/>Gaming Detection"]
        SD["stagnation-detector.py<br/>Stagnation Detection"]
    end

    EXEC --> post_exec

    style BLOCK1 fill:#ff6b6b,color:#fff
    style BLOCK2 fill:#ff6b6b,color:#fff
    style BLOCK3 fill:#ff6b6b,color:#fff
    style BLOCK4 fill:#ff6b6b,color:#fff
    style BLOCK5 fill:#ff6b6b,color:#fff
    style DONE fill:#51cf66,color:#fff
```

## 補足

- **多層防御**: 単一の hook に依存せず、入力段階（injection detection）-> 実行段階（scope enforcement）-> 完了段階（completion gate）の3段階でセキュリティを担保
- **Policy hooks の全体像**: `scripts/policy/` には21個の hook が存在。図では主要なセキュリティ関連 hook を抜粋
- **MCP 監査**: `mcp-audit.py` はメインチェーンとは並列に動作し、MCP サーバーとの通信を監査する。OWASP MCP Top 10 に基づく検査
- **protect-linter-config**: `.eslintrc*`, `biome.json`, `.prettierrc*` 等の lint 設定ファイルへの変更をブロックする。設定ではなくコードを修正させる方針
- **completion-gate**: タスク完了宣言時に、実際にビルド・テスト・lint が通っているか検証を強制するゲート。仮定に基づく「問題ありません」を防止
- **gaming-detector**: AutoEvolve の自己改善ループにおいて、メトリクスを不正に操作するパターンを検出する
- **Post-Execution**: 実行後もフィードバック追跡、ゲーミング検出、膠着検出が継続的に動作する
