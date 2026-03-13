# Claude Code 設定

dotfiles リポジトリで管理する Claude Code のグローバル設定。
symlink 経由で `~/.claude/` に展開され、全プロジェクトで共有される。

## 運用入口

Claude Code の設定変更は、この README だけでなく以下も併せて参照する。

- repo 共通 contract: [../../AGENTS.md](../../AGENTS.md)
- plan contract: [../../PLANS.md](../../PLANS.md)
- Claude 固有指示: [CLAUDE.md](CLAUDE.md)
- 詳細 workflow: [references/workflow-guide.md](references/workflow-guide.md)
- skill inventory: [references/skill-inventory.md](references/skill-inventory.md)
- AI workflow 監査ガイド: [../../docs/guides/ai-workflow-audit.md](../../docs/guides/ai-workflow-audit.md)
- playbook: [../../docs/playbooks/claude-config-changes.md](../../docs/playbooks/claude-config-changes.md)

長時間タスクや複数ファイル変更では、`tmp/plans/` の一時 plan だけで終わらせず、
必要に応じて `docs/plans/` に永続 plan を残す。

---

## システム全体像

Claude Code は **3層マルチモデル連携** をオーケストレーションの中心に据え、
**Hooks** / **Skills** / **Agents** / **Plugins** が相互に連携する自律型開発ハーネスとして動作する。

```mermaid
graph TB
    User([ユーザー入力])

    subgraph orchestrator["Orchestrator Layer (Claude Opus)"]
        direction TB
        CC[Claude Code CLI]
        CLAUDE_MD["CLAUDE.md<br><small>コア原則 ~69行</small>"]
        SETTINGS["settings.json<br><small>hooks / permissions / model</small>"]
    end

    subgraph execution["Execution Layer"]
        direction TB
        subgraph hooks_box["Hooks (18 scripts)"]
            direction LR
            H_RT["Runtime<br><small>format, session, checkpoint</small>"]
            H_PO["Policy<br><small>golden-check, error-to-codex</small>"]
            H_LC["Lifecycle<br><small>plan-lifecycle, doc-garden</small>"]
            H_LR["Learner<br><small>session-learner</small>"]
        end

        subgraph skills_box["Skills (48+)"]
            direction LR
            SK_CORE["Core Workflow<br><small>/review, /rpi, /epd</small>"]
            SK_DOMAIN["Domain<br><small>frontend, backend, architect</small>"]
            SK_EXT["External Model<br><small>/codex, /gemini, /research</small>"]
            SK_OPS["DevOps<br><small>/morning, /kanban, /capture</small>"]
        end

        subgraph agents_box["Agents (28)"]
            direction LR
            AG_REV["Review<br><small>code-reviewer, codex-reviewer</small>"]
            AG_IMPL["Implement<br><small>debugger, build-fixer</small>"]
            AG_MAINT["Maintenance<br><small>doc-gardener, golden-cleanup</small>"]
            AG_EVOLVE["AutoEvolve<br><small>autoevolve-core</small>"]
        end

        PLUGINS["Plugins (7)<br><small>superpowers, pr-review-toolkit, etc.</small>"]
    end

    subgraph external["External CLI Tools"]
        direction LR
        CODEX["Codex CLI<br><small>gpt-5.4 / 深い推論</small>"]
        GEMINI["Gemini CLI<br><small>1M tokens / 大規模分析</small>"]
    end

    subgraph data["Data & Learning Layer"]
        direction LR
        LEARNINGS["learnings/*.jsonl<br><small>errors, quality, patterns</small>"]
        METRICS["metrics/<br><small>session-metrics.jsonl</small>"]
        INSIGHTS["insights/<br><small>analysis reports</small>"]
    end

    User --> CC
    CC --> hooks_box
    CC --> skills_box
    CC --> agents_box
    CC --> PLUGINS
    SK_EXT --> CODEX
    SK_EXT --> GEMINI
    AG_EVOLVE --> LEARNINGS
    H_LR --> LEARNINGS
    H_PO --> LEARNINGS
    LEARNINGS --> INSIGHTS
    METRICS --> INSIGHTS

    style orchestrator fill:#1a1a2e,stroke:#533483,color:#e0e0e0
    style execution fill:#16213e,stroke:#533483,color:#e0e0e0
    style external fill:#0f3460,stroke:#533483,color:#e0e0e0
    style data fill:#1b1b2f,stroke:#e94560,color:#e0e0e0
```

### 3層モデル連携

| 層 | モデル | コンテキスト | 役割 | 委譲ルール |
|----|--------|-------------|------|-----------|
| **Orchestrator** | Claude Opus | 200K | 全体制御、コード生成、レビュー統合 | - |
| **Deep Reasoning** | Codex CLI (gpt-5.4) | 400K | 設計・推論・複雑なデバッグ | `rules/codex-delegation.md` |
| **Large Context** | Gemini CLI | 1M | 大規模分析・外部リサーチ・マルチモーダル | `rules/gemini-delegation.md` |

---

## ディレクトリ構造

```
.config/claude/
├── CLAUDE.md                     # グローバル指示書 (毎ターン読み込み)
├── README.md                     # ← このファイル
├── settings.json                 # メイン設定 (hooks, permissions, model)
├── settings.local.json           # ローカルオーバーライド
├── statusline.sh                 # ステータスライン表示
│
├── agents/                       # サブエージェント定義 (28個)
├── commands/                     # カスタムコマンド (19個)
├── skills/                       # 再利用可能なスキル (48+)
├── rules/                        # 言語・ドメイン別ルール (13個)
├── references/                   # 参照ドキュメント (24個)
│   └── review-checklists/        # 言語別レビュー基準
├── scripts/                      # Hook スクリプト (18個)
│   ├── runtime/                  # セッション管理・フォーマット
│   ├── policy/                   # ポリシー強制・エラー検出
│   ├── lifecycle/                # 計画追跡・ドキュメント管理
│   ├── learner/                  # 学習データ収集
│   └── lib/                      # 共有ユーティリティ
└── docs/
    └── research/                 # 外部CLI出力の永続保存
```

### Symlink マッピング

dotfiles → home への個別 symlink で接続:

```
~/.claude/agents              → dotfiles/.config/claude/agents
~/.claude/commands            → dotfiles/.config/claude/commands
~/.claude/scripts             → dotfiles/.config/claude/scripts
~/.claude/settings.json       → dotfiles/.config/claude/settings.json
~/.claude/settings.local.json → dotfiles/.config/claude/settings.local.json
~/.claude/statusline.sh       → dotfiles/.config/claude/statusline.sh
~/.claude/CLAUDE.md           → dotfiles/.config/claude/CLAUDE.md
```

> **注意**: `references/` は個別 symlink されていない。スクリプトからは `Path(__file__).resolve().parent.parent / "references"` で参照する。

### 変更時の最小検証

- `task validate-configs`
- `task validate-symlinks`

symlink 管理まで変えた場合は `task symlink` も実行する。

### MCP デフォルト

- global default は保守的にし、常時有効は `context7` を基本とする
- `playwright` や `deepwiki` は trusted repo や task 固有の必要があるときに有効化する
- global で全 project MCP を自動有効化しない

---

## Hooks システム（自動イベント駆動）

Hooks は Claude Code のライフサイクルイベントに対して**自動的に**スクリプトを実行する仕組み。
4つのカテゴリに分離されている。

```mermaid
graph LR
    subgraph events["Claude Code Events"]
        E1["SessionStart"]
        E2["UserPromptSubmit"]
        E3["PreToolUse"]
        E4["PostToolUse"]
        E5["PreCompact"]
        E6["Stop / SessionEnd"]
        E7["Notification"]
    end

    subgraph runtime["runtime/ (基盤)"]
        R1["session-load.js<br><small>セッション復元</small>"]
        R2["auto-format.js<br><small>Biome/Ruff/gofmt</small>"]
        R3["output-offload.py<br><small>大出力→/tmp退避</small>"]
        R4["suggest-compact.js<br><small>コンパクト提案</small>"]
        R5["checkpoint_manager.py<br><small>自動チェックポイント</small>"]
        R6["session-save.js<br><small>状態保存</small>"]
        R7["pre-compact-save.js<br><small>圧縮前保存</small>"]
    end

    subgraph policy["policy/ (品質強制)"]
        P1["agent-router.py<br><small>最適エージェント推薦</small>"]
        P2["golden-check.py<br><small>GP違反検出</small>"]
        P3["error-to-codex.py<br><small>エラー→Codex提案</small>"]
        P4["protect-linter-config.py<br><small>lint設定保護</small>"]
        P5["search-first-gate.py<br><small>検索優先ガード</small>"]
        P6["suggest-gemini.py<br><small>Gemini提案</small>"]
        P7["completion-gate.py<br><small>テスト実行ゲート</small>"]
        P8["post-test-analysis.py<br><small>テスト結果分析</small>"]
    end

    subgraph lifecycle["lifecycle/ (計画管理)"]
        L1["plan-lifecycle.py<br><small>計画進捗追跡</small>"]
    end

    subgraph learner["learner/ (学習)"]
        LR1["session-learner.py<br><small>学習データ永続化</small>"]
    end

    E1 --> R1
    E2 --> P1
    E3 --> P4 & P5 & P6
    E4 --> R2 & R3 & R4 & R5 & P2 & P3 & P8 & L1
    E5 --> R7
    E6 --> R6 & P7 & LR1

    style events fill:#533483,stroke:#16213e,color:#e0e0e0
    style runtime fill:#0f3460,stroke:#16213e,color:#e0e0e0
    style policy fill:#e94560,stroke:#16213e,color:#ffffff
    style lifecycle fill:#1b998b,stroke:#16213e,color:#ffffff
    style learner fill:#f4a261,stroke:#16213e,color:#1a1a2e
```

### イベント → スクリプト対応表

| イベント | スクリプト | 役割 |
|---------|-----------|------|
| **SessionStart** | `session-load.js`, `checkpoint_recover.py` | セッション復元、前回チェックポイント回復 |
| **UserPromptSubmit** | `agent-router.py` | Codex/Gemini キーワード検出、最適エージェント推薦 |
| **PreToolUse** (Edit/Write) | `protect-linter-config.py`, `search-first-gate.py` | lint設定保護、検索優先ガード |
| **PreToolUse** (Bash) | `git add` 検証, `pre-commit-check.js` | `-A`/`--all` ブロック、コミットメッセージ検証 |
| **PreToolUse** (WebSearch) | `suggest-gemini.py` | 大規模リサーチ時に Gemini CLI を提案 |
| **PostToolUse** (Edit/Write) | `auto-format.js`, `golden-check.py`, `checkpoint_manager.py` | 自動整形、GP違反検出、チェックポイント |
| **PostToolUse** (Bash) | `output-offload.py`, `error-to-codex.py`, `post-test-analysis.py`, `plan-lifecycle.py` | 出力退避、エラー分析、テスト解析、計画追跡 |
| **PreCompact** | `pre-compact-save.js` | コンテキスト圧縮前にセッション状態保存 |
| **Stop/SessionEnd** | `completion-gate.py`, `session-save.js`, `session-learner.py` | テスト実行ゲート、状態保存、学習データ永続化 |

### 共有モジュール (scripts/lib/)

| モジュール | 役割 |
|-----------|------|
| `hook_utils.py` | JSON I/O、passthrough、コンテキスト注入 |
| `session_events.py` | イベントの emit / flush / 永続化の共通基盤 |
| `storage.py` | データディレクトリ解決 |
| `task_registry.py` | タスクレジストリ CRUD |
| `evaluator_metrics.py` | レビューアー精度メトリクス |
| `trace_sampler.py` | 大規模トレースのサンプリング |

### Plan / Checkpoint の役割分担

- plan: goal、scope、validation、decision を `PLANS.md` 契約で残す
- checkpoint: session 再開用の runtime state を保存する
- 長時間タスクでは両方を使う

---

## Skills カテゴリマップ (48+)

Skills は**知識ベース + ワークフロー定義**。コマンド(`/skill名`)で呼び出すか、エージェントが内部で参照する。

運用上は [references/skill-inventory.md](references/skill-inventory.md) の tier を優先する。

```mermaid
graph TB
    subgraph core["Core Workflow (開発の中核)"]
        direction LR
        review["/review<br>コードレビュー統合"]
        rpi["/rpi<br>Research→Plan→Implement"]
        epd["/epd<br>Spec→Spike→Validate→Build"]
        commit["/commit<br>conventional commit"]
        searchFirst["search-first<br>検索優先ワークフロー"]
        verify["verification-before-completion<br>完了前検証"]
        checkHealth["/check-health<br>ドキュメント健全性"]
    end

    subgraph product["Product Development (プロダクト開発)"]
        direction LR
        spec["/spec<br>Prompt-as-PRD 生成"]
        spike["/spike<br>プロトタイプ検証"]
        validate["/validate<br>受入基準検証"]
        edgeCaseAnalysis["edge-case-analysis<br>異常系洗い出し"]
        interviewIssues["/interviewing-issues<br>Issue 明確化"]
    end

    subgraph domain["Domain Specialist (専門知識)"]
        direction LR
        seniorArch["senior-architect<br>システム設計"]
        seniorBack["senior-backend<br>API/DB設計"]
        seniorFront["senior-frontend<br>React/Next.js"]
        reactBP["react-best-practices<br>React最適化"]
        frontDesign["frontend-design<br>UI デザイン"]
        graphql["graphql-expert<br>GraphQL設計"]
        buf["buf-protobuf<br>Protocol Buffers"]
        webDesign["web-design-guidelines<br>Web UI ガイドライン"]
        uiux["ui-ux-pro-max<br>UI/UX最適化"]
        vercel["vercel-composition-patterns<br>コンポジション"]
    end

    subgraph ext["External Model (外部モデル連携)"]
        direction LR
        codex["/codex<br>Codex CLI (gpt-5.4)"]
        codexReview["/codex-review<br>Codex レビュー"]
        gemini["/gemini<br>Gemini CLI (1M)"]
        research["/research<br>並列リサーチ"]
    end

    subgraph automation["Automation (自動化)"]
        direction LR
        autonomous["/autonomous<br>マルチセッション自律実行"]
        improve["/improve<br>AutoEvolve 改善"]
        createPRWait["/create-pr-wait<br>PR→CI監視→自動修正"]
        fixIssue["/fix-issue<br>Issue自動修正"]
        setupBG["setup-background-agents<br>BG エージェント基盤"]
    end

    subgraph devops["DevOps (日々の運用)"]
        direction LR
        morning["/morning<br>朝の計画"]
        kanban["/kanban<br>カンバン操作"]
        capture["/capture<br>GTD即時キャプチャ"]
        weeklyReview["/weekly-review<br>週次レビュー"]
        dailyReport["/daily-report<br>日報生成"]
        devInsights["/dev-insights<br>データ分析"]
    end

    subgraph knowledge["Knowledge (知識管理)"]
        direction LR
        obsSetup["obsidian-vault-setup<br>Vault セットアップ"]
        obsKnow["obsidian-knowledge<br>ナレッジ検索"]
        obsCont["obsidian-content<br>コンテンツ生成"]
        eureka["/eureka<br>ブレイクスルー記録"]
        contLearn["continuous-learning<br>継続学習"]
    end

    subgraph meta["Meta (スキル管理)"]
        direction LR
        skillCreator["skill-creator<br>スキル作成"]
        skillAudit["skill-audit<br>スキル監査"]
        aiAudit["ai-workflow-audit<br>AI workflow 監査"]
        initProject["init-project<br>プロジェクト初期化"]
        challenge["/challenge<br>変更への挑戦"]
        secReview["/security-review<br>セキュリティ"]
    end

    style core fill:#e94560,stroke:#16213e,color:#ffffff
    style product fill:#533483,stroke:#16213e,color:#e0e0e0
    style domain fill:#0f3460,stroke:#16213e,color:#e0e0e0
    style ext fill:#1b998b,stroke:#16213e,color:#ffffff
    style automation fill:#f4a261,stroke:#16213e,color:#1a1a2e
    style devops fill:#2d6a4f,stroke:#16213e,color:#e0e0e0
    style knowledge fill:#6c567b,stroke:#16213e,color:#e0e0e0
    style meta fill:#495057,stroke:#16213e,color:#e0e0e0
```

### スキル間の依存関係

```mermaid
flowchart TB
    epd["/epd"]
    spec["/spec"]
    spike["/spike"]
    validate["/validate"]
    rpi["/rpi"]
    review["/review"]
    commit["/commit"]
    improve["/improve"]
    research["/research"]
    autonomous["/autonomous"]

    epd -->|"Phase 1"| spec
    epd -->|"Phase 2"| spike
    spike -->|"内部呼出"| validate
    spike -->|"spec未存在時"| spec
    epd -->|"Phase 3: Decide"| decision{proceed?}
    decision -->|"yes"| rpi
    decision -->|"pivot"| spec
    epd -->|"Phase 5"| review
    review -->|"完了後"| commit

    improve -->|"分析"| autoevolveCore["autoevolve-core agent"]
    research -->|"並列実行"| claudeP["claude -p 子プロセス"]
    autonomous -->|"並列実行"| claudeP2["claude -p (worktree隔離)"]

    style epd fill:#e94560,stroke:#16213e,color:#ffffff
    style review fill:#533483,stroke:#16213e,color:#e0e0e0
    style improve fill:#1b998b,stroke:#16213e,color:#ffffff
```

---

## Agents カテゴリマップ (28)

Agents は**専門実行コンテキスト**。Skills が知識を提供し、Agents がそれを実行する。
`triage-router` が最適なエージェントを推薦する。

```mermaid
graph TB
    subgraph review_agents["Code Review (7)"]
        direction LR
        codeReviewer["code-reviewer<br><small>汎用レビュー + 言語チェックリスト注入</small>"]
        golangReviewer["golang-reviewer<br><small>Go 専門 (MA/MU スタイル)</small>"]
        codexReviewer["codex-reviewer<br><small>Codex深い推論 (~100行以上)</small>"]
        commentAnalyzer["comment-analyzer<br><small>コメント品質・正確性</small>"]
        silentFailure["silent-failure-hunter<br><small>サイレント障害検出</small>"]
        testAnalyzer["test-analyzer<br><small>テスト品質・エッジケース</small>"]
        securityReviewer["security-reviewer<br><small>OWASP Top 10</small>"]
    end

    subgraph arch_agents["Architecture & Design (4)"]
        direction LR
        backendArch["backend-architect<br><small>API/DB/スケーラビリティ</small>"]
        nextjsArch["nextjs-architecture-expert<br><small>App Router/RSC</small>"]
        docFactory["document-factory<br><small>ドキュメント生成</small>"]
        typeDesign["type-design-analyzer<br><small>型設計品質</small>"]
    end

    subgraph impl_agents["Implementation & Debug (6)"]
        direction LR
        buildFixer["build-fixer<br><small>ビルドエラー最小修正</small>"]
        debugger["debugger<br><small>体系的根本原因分析</small>"]
        codexDebugger["codex-debugger<br><small>Codex 深いデバッグ</small>"]
        frontDev["frontend-developer<br><small>React/レスポンシブ</small>"]
        golangPro["golang-pro<br><small>Go goroutine/channel</small>"]
        tsPro["typescript-pro<br><small>高度な型システム</small>"]
    end

    subgraph maint_agents["Maintenance (3)"]
        direction LR
        docGardener["doc-gardener<br><small>ドキュメント鮮度</small>"]
        goldenCleanup["golden-cleanup<br><small>GP違反スキャン</small>"]
        uiObserver["ui-observer<br><small>Playwright UI観察</small>"]
    end

    subgraph product_agents["Product & Design Review (2)"]
        direction LR
        productReviewer["product-reviewer<br><small>spec整合性・スコープ</small>"]
        designReviewer["design-reviewer<br><small>UI/UX・a11y</small>"]
    end

    subgraph routing_agents["Routing & Infra (4)"]
        direction LR
        triageRouter["triage-router<br><small>タスク分類・推薦</small>"]
        gitInspector["safe-git-inspector<br><small>Git履歴 読取専用</small>"]
        dbReader["db-reader<br><small>DB 読取専用</small>"]
        geminiExplore["gemini-explore<br><small>Gemini 1M分析</small>"]
    end

    subgraph evolve_agents["AutoEvolve (1)"]
        autoevolveCore["autoevolve-core<br><small>Analyze / Improve / Garden</small>"]
    end

    subgraph test_agents["Test (1)"]
        testEngineer["test-engineer<br><small>テスト戦略・カバレッジ</small>"]
    end

    style review_agents fill:#e94560,stroke:#16213e,color:#ffffff
    style arch_agents fill:#533483,stroke:#16213e,color:#e0e0e0
    style impl_agents fill:#0f3460,stroke:#16213e,color:#e0e0e0
    style maint_agents fill:#1b998b,stroke:#16213e,color:#ffffff
    style product_agents fill:#f4a261,stroke:#16213e,color:#1a1a2e
    style routing_agents fill:#495057,stroke:#16213e,color:#e0e0e0
    style evolve_agents fill:#6c567b,stroke:#16213e,color:#e0e0e0
    style test_agents fill:#2d6a4f,stroke:#16213e,color:#e0e0e0
```

### 言語別レビューチェックリスト

`code-reviewer` のプロンプトに拡張子に応じて自動注入される:

| ファイル | 対象拡張子 | 観点 |
|---------|-----------|------|
| `references/review-checklists/typescript.md` | `.ts/.tsx/.js/.jsx` | 型安全性・React パターン・Node.js |
| `references/review-checklists/python.md` | `.py` | 型ヒント・Pythonic イディオム・例外設計 |
| `references/review-checklists/go.md` | `.go` | Effective Go・エラーハンドリング・並行処理 |
| `references/review-checklists/rust.md` | `.rs` | 所有権・ライフタイム・unsafe 最小化 |

---

## Skills ↔ Agents ↔ Hooks 連携フロー

Skills が「何をするか」を定義し、Agents が「どう実行するか」を担い、Hooks が「いつ発火するか」を制御する。

```mermaid
sequenceDiagram
    actor User
    participant CC as Claude Code
    participant Hook as Hooks
    participant Skill as Skills
    participant Agent as Agents
    participant CLI as External CLI
    participant Data as Learning Data

    Note over CC: SessionStart
    Hook->>CC: session-load.js (状態復元)

    User->>CC: タスク入力
    Hook->>CC: agent-router.py (最適エージェント推薦)

    CC->>Skill: /rpi (Research→Plan→Implement)

    Note over Skill: Research Phase
    Skill->>Agent: gemini-explore (大規模分析)
    Agent->>CLI: Gemini CLI (1M context)
    CLI-->>Agent: 分析結果
    Agent-->>Skill: リサーチ結果

    Note over Skill: Plan Phase
    Skill->>CC: 計画策定

    Note over Skill: Implement Phase
    CC->>CC: コード編集 (Edit/Write)
    Hook->>CC: auto-format.js (自動整形)
    Hook->>CC: golden-check.py (GP違反検出)
    Hook->>Data: emit_event(quality)

    CC->>CC: Bash (テスト実行)
    Hook->>CC: post-test-analysis.py (結果分析)
    Hook->>Data: emit_event(pattern)

    Note over CC: エラー発生時
    Hook->>CC: error-to-codex.py (Codex提案)
    CC->>Agent: codex-debugger
    Agent->>CLI: Codex CLI (gpt-5.4)
    CLI-->>Agent: デバッグ結果
    Agent-->>CC: 修正案

    Note over CC: レビュー (/review)
    CC->>Skill: /review
    Skill->>Agent: code-reviewer (並列起動)
    Skill->>Agent: codex-reviewer (並列起動)
    Skill->>Agent: product-reviewer (spec存在時)
    Agent-->>Skill: レビュー結果
    Skill->>CC: 統合レポート
    Skill->>Data: emit_review_finding()

    Note over CC: Stop/SessionEnd
    Hook->>CC: completion-gate.py (テストゲート)
    Hook->>Data: session-learner.py (学習永続化)
```

---

## EPD ワークフロー（フル開発サイクル）

大きな機能開発で使用する Spec → Spike → Validate → Build → Review の統合フロー。
Harrison Chase の "How Coding Agents Are Reshaping EPD" に基づく。

```mermaid
flowchart TB
    Start([ユーザーのアイデア])

    subgraph phase1["Phase 1: Spec"]
        spec_gen["仕様書生成<br>/spec"]
        spec_out["docs/specs/{feature}.prompt.md"]
        spec_gen --> spec_out
    end

    subgraph phase2["Phase 2: Spike"]
        worktree["Worktree 隔離<br>spike/{feature}"]
        proto["最小実装<br>(テスト/lint 不要)"]
        validate_spike["/validate<br>受入基準チェック"]
        worktree --> proto --> validate_spike
    end

    subgraph phase3["Phase 3: Decide"]
        decision{ユーザー判断}
        proceed["Proceed"]
        pivot["Pivot"]
        abandon["Abandon"]
    end

    subgraph phase4["Phase 4: Build"]
        rpi_exec["/rpi<br>Research→Plan→Implement"]
        full_impl["本格実装<br>(テスト/lint 必須)"]
        rpi_exec --> full_impl
    end

    subgraph phase5["Phase 5: Review"]
        eng_review["Engineering Review<br>code-reviewer + codex-reviewer"]
        prod_review["Product Review<br>product-reviewer"]
        design_review["Design Review<br>design-reviewer"]
    end

    phase6["Phase 6: Ship<br>/commit"]

    Start --> phase1
    phase1 --> phase2
    phase2 --> phase3
    decision --> proceed & pivot & abandon
    proceed --> phase4
    pivot -->|"spec 更新"| phase1
    abandon -->|"中止"| End2([終了])
    phase4 --> phase5
    eng_review & prod_review & design_review --> phase6

    style phase1 fill:#533483,stroke:#16213e,color:#e0e0e0
    style phase2 fill:#0f3460,stroke:#16213e,color:#e0e0e0
    style phase3 fill:#f4a261,stroke:#16213e,color:#1a1a2e
    style phase4 fill:#1b998b,stroke:#16213e,color:#ffffff
    style phase5 fill:#e94560,stroke:#16213e,color:#ffffff
```

### ワークフロー使い分け

| シナリオ | 推奨コマンド |
|---------|-------------|
| 不確実なアイデア | `/epd` (フル6フェーズ) |
| 仕様が明確 | `/rpi` (Research→Plan→Implement) |
| 素早い検証 | `/spike` (worktree隔離プロトタイプ) |
| 仕様書のみ作成 | `/spec` |

---

## Review パイプライン

コードレビューは変更規模と内容シグナルに応じて**レビューアー数を自動スケール**する。

```mermaid
flowchart LR
    diff["git diff<br>変更分析"]

    subgraph scaling["スケーリング判定"]
        s10["~10行<br>省略"]
        s50["~50行<br>2並列"]
        s200["~200行<br>3並列"]
        s200plus["200行超<br>4-5並列"]
    end

    subgraph always["常時起動"]
        cr["code-reviewer<br>+ 言語チェックリスト"]
    end

    subgraph conditional["条件起動"]
        cxr["codex-reviewer<br>(50行以上)"]
        gr["golang-reviewer<br>(.go ファイル)"]
        pr["product-reviewer<br>(spec 存在時)"]
        dr["design-reviewer<br>(.tsx/.css 変更時)"]
    end

    subgraph content_signal["内容シグナル起動"]
        sfh["silent-failure-hunter<br>(catch/recover/fallback)"]
        ta["test-analyzer<br>(_test.go, .test.ts)"]
        ca["comment-analyzer<br>(10行以上のコメント)"]
        tda["type-design-analyzer<br>(type/interface 追加)"]
    end

    subgraph synthesis["統合"]
        dedup["重複排除"]
        filter["confidence < 80 除外"]
        priority["Critical → Important → Suggestion"]
        report["統合レポート"]
    end

    diff --> scaling
    scaling --> always & conditional & content_signal
    always & conditional & content_signal --> synthesis

    style scaling fill:#533483,stroke:#16213e,color:#e0e0e0
    style always fill:#e94560,stroke:#16213e,color:#ffffff
    style conditional fill:#0f3460,stroke:#16213e,color:#e0e0e0
    style content_signal fill:#1b998b,stroke:#16213e,color:#ffffff
    style synthesis fill:#f4a261,stroke:#16213e,color:#1a1a2e
```

### レビュースケール表

| 変更行数 | レビューアー | 言語チェックリスト |
|---------|-------------|------------------|
| ~10行 | 省略 (Verify のみ) | - |
| ~50行 | code-reviewer + codex-reviewer | 拡張子で自動注入 |
| ~200行 | 上記 + golang-reviewer (Go時) | 同上 |
| 200行超 | 上記 + コンテンツベース専門家 | 同上 |

---

## AutoEvolve システム（自律改善ループ）

[karpathy/autoresearch](https://github.com/karpathy/autoresearch) に着想を得た自律改善システム。
セッションデータを自動収集・分析し、設定自体を改善する提案を生成する。

```mermaid
flowchart TB
    subgraph session["セッション中 (自動)"]
        direction TB
        errHook["error-to-codex.py<br>エラー検出"]
        gpHook["golden-check.py<br>GP違反検出"]
        testHook["post-test-analysis.py<br>テスト分析"]
        reviewHook["review-feedback-tracker.py<br>レビュー追跡"]

        emit["emit_event()<br>session_events.py"]
        tmpFile["current-session.jsonl<br>(一時ファイル)"]

        errHook & gpHook & testHook & reviewHook --> emit --> tmpFile
    end

    subgraph flush["セッション終了 (自動)"]
        learner["session-learner.py<br>flush_session()"]
        errors["errors.jsonl"]
        quality["quality.jsonl"]
        patterns["patterns.jsonl"]
        reviewFindings["review-findings.jsonl"]
        metrics["session-metrics.jsonl"]

        learner --> errors & quality & patterns & reviewFindings & metrics
    end

    subgraph analysis["分析 (/improve 手動)"]
        direction TB
        analyze["Phase 1: Analyze<br>4カテゴリ並列分析"]
        garden["Phase 2: Garden<br>重複排除・陳腐化除去"]
        improvePhase["Phase 3: Improve<br>設定改善提案"]
        branch["autoevolve/* ブランチ<br>max 3ファイル/サイクル"]

        analyze --> garden --> improvePhase --> branch
    end

    tmpFile --> learner
    errors & quality & patterns --> analyze

    subgraph safety["安全機構"]
        s1["master 直接変更禁止"]
        s2["1サイクル max 3ファイル"]
        s3["テスト通過必須"]
        s4["人間レビュー必須"]
    end

    branch --> safety

    style session fill:#0f3460,stroke:#16213e,color:#e0e0e0
    style flush fill:#533483,stroke:#16213e,color:#e0e0e0
    style analysis fill:#1b998b,stroke:#16213e,color:#ffffff
    style safety fill:#e94560,stroke:#16213e,color:#ffffff
```

### 4層ループ

| 層 | トリガー | やること |
|----|---------|---------|
| **セッション** | Stop / SessionEnd hook | エラー・品質指摘を jsonl に自動記録 |
| **日次** | `/daily-report` | 「今日の学び」セクションで振り返り |
| **オンデマンド** | `/improve` コマンド | 分析 → 整理 → 設定改善提案 |
| **バックグラウンド** | `autoevolve-runner.sh` (cron) | 深夜に自律改善、朝レビュー |

### データフロー

```
生データ (jsonl)
  → 3回以上出現 → insights/ に整理 (autoevolve-core)
  → 確信度高 → MEMORY.md に追記 (autoevolve-core が提案)
  → 汎用性高 → skill / rule に昇格 (人間が承認)
```

### セキュリティ境界

| Git 管理 (公開OK) | ローカルのみ (非公開) |
|------------------|---------------------|
| エージェント定義、スキル、ルール | `learnings/*.jsonl` (生ログ) |
| hook ロジック、`improve-policy.md` | `metrics/` (セッション統計) |
| autoevolve の diff・履歴 | `logs/` (実行ログ) |
| `settings.json` (permissions) | `settings.local.json` (環境固有) |

---

## タスク規模別ワークフロー

| 規模 | 例 | 必須段階 |
|------|------|---------|
| **S** | typo修正、1行変更 | Implement → Verify |
| **M** | 関数追加、バグ修正 | Plan → Implement → Test → Verify |
| **L** | 新機能、リファクタリング | Plan → Implement → Test → Review → Verify → Security Check |

```mermaid
flowchart LR
    Plan["Plan"] --> Implement["Implement"]
    Implement --> Test["Test"]
    Test --> Review["Review"]
    Review --> Verify["Verify"]
    Verify --> Security["Security Check"]
    Security --> Commit["Commit"]

    Test -->|"失敗"| Implement
    Review -->|"指摘"| Implement
    Verify -->|"失敗"| Implement
    Security -->|"脆弱性"| Implement

    style Plan fill:#533483,stroke:#16213e,color:#e0e0e0
    style Implement fill:#0f3460,stroke:#16213e,color:#e0e0e0
    style Test fill:#1b998b,stroke:#16213e,color:#ffffff
    style Review fill:#e94560,stroke:#16213e,color:#ffffff
    style Verify fill:#f4a261,stroke:#16213e,color:#1a1a2e
    style Security fill:#495057,stroke:#16213e,color:#e0e0e0
    style Commit fill:#2d6a4f,stroke:#16213e,color:#e0e0e0
```

---

## Progressive Disclosure 設計

コンテキストウィンドウを効率的に使うための階層型設計:

```mermaid
graph TB
    subgraph always["常時読み込み (~69行)"]
        claudeMd["CLAUDE.md<br>コア原則・ワークフロー概要"]
    end

    subgraph conditional["条件付き読み込み (各20-50行)"]
        rules["rules/<br>言語別コーディング規則"]
        rulesCommon["rules/common/<br>セキュリティ・品質・テスト"]
    end

    subgraph onDemand["必要時のみ (各100-300行)"]
        refs["references/<br>ワークフロー詳細・GP・エラーガイド"]
        checklists["review-checklists/<br>言語別レビュー基準"]
    end

    subgraph invoked["コマンド実行時 (各50-200行)"]
        skills["skills/<br>ワークフロー定義・知識ベース"]
    end

    always -->|"対象言語のコード変更時"| conditional
    conditional -->|"明示的参照・複雑な判断時"| onDemand
    onDemand -->|"/ コマンド実行時"| invoked

    style always fill:#e94560,stroke:#16213e,color:#ffffff
    style conditional fill:#f4a261,stroke:#16213e,color:#1a1a2e
    style onDemand fill:#0f3460,stroke:#16213e,color:#e0e0e0
    style invoked fill:#495057,stroke:#16213e,color:#e0e0e0
```

---

## ルール (13個)

`rules/` 配下のルールは Claude Code が自動的に条件に応じて読み込む。

### 共通ルール

| ファイル | 適用場面 |
|---------|---------|
| `common/code-quality.md` | DRY, SOLID, 保守性 |
| `common/error-handling.md` | エラーハンドリングパターン |
| `common/security.md` | セキュリティベストプラクティス |
| `common/testing.md` | テスト戦略・カバレッジ |
| `common/overconfidence-prevention.md` | 不確実性の認知 |

### 言語別ルール

| ファイル | 対象 |
|---------|------|
| `typescript.md` | TypeScript 型安全性、React パターン |
| `react.md` | React コンポーネント設計、hooks |
| `go.md` | Go イディオム、エラーハンドリング、並行処理 |
| `rust.md` | Rust 所有権、ライフタイム、安全性 |
| `test.md` | テスト構造・命名規則 |
| `proto.md` | Protocol Buffers |

### モデル委譲ルール

| ファイル | 役割 |
|---------|------|
| `codex-delegation.md` | Codex CLI に委譲するタイミングと方法 |
| `gemini-delegation.md` | Gemini CLI に委譲するタイミングと方法 |
| `config.md` | 設定管理ルール |

---

## リファレンス (24個)

`references/` は詳細ドキュメント。必要時にのみ参照される (Progressive Disclosure)。

| ファイル | 内容 |
|---------|------|
| `workflow-guide.md` | 6段階ワークフロー詳細、エージェントルーティング、トークン予算 |
| `golden-principles.md` | GP-001〜008: 品質・設計原則の自動検出パターン |
| `improve-policy.md` | AutoEvolve の改善方針・制約・禁止事項 |
| `error-fix-guides.md` | エラーパターン→根本原因→修正のマッピング |
| `constraints-library.md` | C-001〜C-010 ソフト制約テンプレート |
| `subagent-delegation-guide.md` | 3委譲パターン (Sync, Async, Queue) |
| `subagent-framing.md` | サブエージェントへのフレーミング注入 |
| `agent-design-lessons.md` | エージェント設計パターンと教訓 |
| `failure-taxonomy.md` | FM-001〜FM-010 障害モード分類 |
| `research-checklist.md` | 構造化リサーチプロトコル |
| `scoring-rules.md` | レビュースコア計算ルール |
| `readability-principles.md` | コード可読性の原則 |
| `skill-inventory.md` | スキルカタログと使用ガイド |
| `task-registry-schema.md` | タスクレジストリ JSON スキーマ |
| `context-profiles.md` | コンテキスト切替パターン |
| `brownfield-analysis-template.md` | 大規模コードベース分析テンプレート |
| `e2e-tool-selection.md` | E2E テストツール選定マトリクス |
| `claudeignore-template.md` | .claudeignore テンプレート |
| `claude-code-threats.md` | セキュリティ脅威モデル |
| `mcp-server-template/` | MCP サーバー実装テンプレート |
| `review-checklists/typescript.md` | TypeScript レビュー基準 |
| `review-checklists/python.md` | Python レビュー基準 |
| `review-checklists/go.md` | Go レビュー基準 |
| `review-checklists/rust.md` | Rust レビュー基準 |

---

## Plugins (7個)

| プラグイン | 提供元 | 機能 |
|-----------|--------|------|
| `superpowers` | superpowers-marketplace | worktree, 並列エージェント, TDD 等のワークフロー |
| `frontend-design` | claude-code-plugins | 高品質 UI デザイン生成 |
| `pr-review-toolkit` | claude-code-plugins | PR レビュー用の専門エージェント群 |
| `code-simplifier` | claude-plugins-official | コードの簡素化・リファクタリング |
| `playground` | claude-plugins-official | インタラクティブ HTML プレイグラウンド |
| `gopls-lsp` | claude-plugins-official | Go LSP サポート |
| `datadog` | kw-marketplace | Datadog 連携 |

---

## MCP サーバー (3個)

| サーバー | 用途 |
|---------|------|
| `context7` | ライブラリの最新ドキュメント・コード例の取得 |
| `playwright` | Web アプリのブラウザ操作・スクリーンショット・テスト |
| `deepwiki` | DeepWiki からのナレッジ検索 |

---

## カスタムコマンド (19個)

`/command` で呼び出すスラッシュコマンド。

| コマンド | 説明 | タスク規模 |
|---------|------|-----------|
| `/commit` | conventional commit + 絵文字プレフィックスでコミット作成 | S |
| `/review` | 変更規模に応じてレビューアーを自動選択・並列起動 | M-L |
| `/pull-request` | PR 作成 (ブランチ push + タイトル/本文自動生成) | S |
| `/rpi` | Research → Plan → Implement の3フェーズ体系的実行 | L |
| `/epd` | Full EPD: Spec → Spike → Validate → Decide → Build | L |
| `/spec` | Prompt-as-PRD 仕様書生成 | M |
| `/spike` | Worktree 隔離プロトタイプ検証 | M |
| `/validate` | spec の受入基準に対する検証 | S |
| `/improve` | AutoEvolve 改善サイクルの手動実行 | L |
| `/research` | マルチエージェント並列リサーチ | M-L |
| `/autonomous` | マルチセッション自律実行 | L |
| `/fix-issue` | GitHub Issue を起点にした自動修正 | M-L |
| `/security-review` | OWASP Top 10 セキュリティレビュー | M |
| `/challenge` | 直前の変更を分析し、エレガント版再設計 | M |
| `/eureka` | 技術ブレイクスルーの構造化記録 | S |
| `/checkpoint` | セッション状態の手動チェックポイント | S |
| `/check-context` | コンテキストウィンドウ使用率確認 | S |
| `/memory-status` | メモリシステム状態サマリー | S |
| `/daily-report` | 全プロジェクト横断の日報生成 | M |

---

## 使い方

```bash
# 改善サイクルを手動で回す
/improve

# 改善の方向性を変える
vim ~/.claude/references/improve-policy.md

# バックグラウンドで実行
~/.claude/scripts/autoevolve-runner.sh

# cron で毎日自動実行
# crontab -e
# 0 3 * * * ~/.claude/scripts/autoevolve-runner.sh

# 提案されたブランチを確認
git branch --list "autoevolve/*"
git diff master..autoevolve/YYYY-MM-DD

# ログを確認
cat ~/.claude/agent-memory/logs/autoevolve.log
```
