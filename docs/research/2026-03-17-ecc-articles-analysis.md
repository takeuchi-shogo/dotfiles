# ECC (Everything Claude Code) 3部作 分析レポート

**日付**: 2026-03-17
**対象記事**: @affaanmustafa の 3部作
- Part 1: The Shorthand Guide to Everything Claude Code
- Part 2: The Longform Guide to Everything Claude Code
- Part 3: The Shorthand Guide to Everything Agentic Security

**比較対象**: dotfiles/.config/claude/ の現在の設定
**リポジトリ**: [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (★80,825, 2026-03-17時点)

---

## 0. リポジトリ (everything-claude-code) 概要

### スケール
- **90+ skills** (domain-specific 含む: logistics, customs, energy, investor-materials 等)
- **25+ agents** (言語別: go-reviewer, python-reviewer, cpp-reviewer, kotlin-reviewer, java-reviewer, rust-reviewer)
- **50+ commands** (slash commands)
- **マルチプラットフォーム**: `.codex/`, `.cursor/`, `.opencode/` 対応
- **Selective Install**: プロファイル (minimal/standard/strict) によるコンポーネント選択インストール

### 注目すべきパターン

#### 1. Hook Profile System (`run-with-flags.js`)
全 hook が `run-with-flags.js` 経由で `minimal`, `standard`, `strict` プロファイルで制御される。
```json
"command": "node scripts/hooks/run-with-flags.js \"pre:edit-write:suggest-compact\" \"scripts/hooks/suggest-compact.js\" \"standard,strict\""
```
- `minimal`: 最低限の hook のみ (session lifecycle)
- `standard`: 開発に有用な hook (format, lint, compact suggest)
- `strict`: 全 hook (security, quality gate 含む)
- **利点**: ユーザーが一括で hook 強度を切り替え可能。デバッグ時に hook を減らしたい場合に便利

#### 2. Cost Tracker (`cost-tracker.js`)
Stop hook でセッションごとのトークン・コストメトリクスを追跡。
- 当設定の `session_events.py` はイベントベースだがコスト追跡は含まない
- **採用価値**: トークン消費のトレンド分析、コスト最適化の意思決定に有用

#### 3. Continuous Learning v2 (Pre + Post observe)
Pre/Post の両方で observe hook を発火し、ツール使用パターンを学習。
```json
"matcher": "*",
"command": "bash skills/continuous-learning-v2/hooks/observe.sh",
"async": true
```
- 当設定の `session-learner.py` は Stop/SessionEnd のみ
- **差異**: ECC はリアルタイム観察、当設定は事後評価。事後評価の方が軽量

#### 4. Auto-tmux Dev Server (`auto-tmux-dev.js`)
PreToolUse/Bash で dev server 起動コマンドを検出し、自動的に tmux セッションで起動。
- 当設定にはない
- **採用判断**: 低優先。当設定は output-offload.py で大出力を退避しているので同等の効果

#### 5. InsAIts Security Monitor
オプションの AI セキュリティモニター。Bash/Edit/Write フローを監視。
```json
"command": "node scripts/hooks/insaits-security-wrapper.js",
"timeout": 15
```
- `ECC_ENABLE_INSAITS=1` で有効化。`pip install insa-its` が必要
- 当設定にはない（golden-check.py と protect-linter-config.py が部分的にカバー）

#### 6. Contexts (--system-prompt 用)
`contexts/dev.md`, `contexts/review.md`, `contexts/research.md` — モード別の簡潔なコンテキストファイル。
- dev: "Write code first, explain after"
- review: Security checklist, severity prioritization
- research: "Don't write code until understanding is clear"
- 当設定では rules/ と file-pattern-router.py で動的ルーティング。記事自身も marginal と認めている

### 当設定にあって ECC にないもの

| 当設定の機能 | ECC の状態 |
|---|---|
| **Rust バイナリ hook runner** | 全て Node.js |
| **Golden Principles 自動検出** (GP-001〜011) | quality-gate.js が部分的にカバーだが GP 体系なし |
| **Completion Gate + Ralph Loop** | session-end のみ、プラン完了チェックなし |
| **Linter Config 保護** | なし |
| **マルチモデル統合** (Codex/Gemini) | Codex 対応あり、Gemini なし |
| **AutoEvolve 4層ループ** | continuous-learning v2 は 2層 (Pre/Post observe + session evaluate) |
| **Progressive Disclosure** (CLAUDE.md → references → rules) | CLAUDE.md に情報集約 |
| **Output Offload** | なし |
| **ADR システム** | なし |
| **Eval 基盤** (reviewer-eval-tuples) | eval-harness スキルはあるが eval data なし |

---

## 1. 実装済みなもの (Already Implemented)

記事で推奨されている項目のうち、すでに同等以上の実装が存在するもの。

### Part 1 (Shorthand) — ほぼ全項目実装済み

| 記事の推奨 | 現在の実装 | 評価 |
|---|---|---|
| Skills/Commands 体系 | 40+ skills (`skills/`), slash commands | 記事の例 (8 skills) を大幅に超過 |
| Hook 6種 (Pre/Post/Submit/Stop/PreCompact/Notification) | 全6種 + SessionEnd。4層分離 (runtime/policy/lifecycle/learner) + Rust バイナリで高速化 | 記事を大幅に超過 |
| Subagents (9 agents) | 31 agents。マルチモデル (Codex/Gemini) 統合、言語特化 (golang-pro, typescript-pro) | 記事を大幅に超過 |
| Rules フォルダ (6 files) | 14 rule files + 5 common rules。言語別 + 委譲ルール | 記事を超過 |
| MCP 管理 (`enableAllProjectMcpServers: false`) | 設定済み。MCP は context7 のみ有効で非常に保守的 | 記事より厳格 |
| Deny rules (ssh, aws, env) | 記事の推奨 + .pem, credentials, token, secret, .key, sudo, chmod 777, --no-verify, wget, ncat, netcat, rm -rf, force push, hard reset, clean | 記事を大幅に超過 |
| Custom StatusLine | `statusline.sh` で実装済み | 同等 |
| Parallel workflows / Worktrees | autonomous スキル・spike スキルで worktree 分離をデフォルト化 | 記事と同等以上 |
| Plugin 管理 (4-5 有効) | 9 plugins 有効 (LSP 含む) | 同等 |
| PostToolUse auto-format | `auto-format.js` → Biome+Oxlint(TS/JS), Ruff(Python), gofmt(Go) | 記事の Prettier 単体より進化 |
| Notification hook | macOS 通知 + サウンド (`afplay Glass.aiff`) | 記事と同等 |

### Part 2 (Longform) — 大半が実装済み

| 記事の推奨 | 現在の実装 | 評価 |
|---|---|---|
| Session Memory Persistence (SessionStart/Stop/PreCompact) | session-load.js, session-save.js, pre-compact-save.js, checkpoint_recover.py | 完全実装 |
| Continuous Learning (Stop hook) | session-learner.py (Stop + SessionEnd)。AutoEvolve 4層ループ + skill_amender + tip_generalizer | 記事を大幅に超過 |
| Strategic Compact | suggest-compact.js + `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80` | 実装済み |
| Verification Loops | completion-gate.py (Stop hook)。Ralph Loop でアクティブプラン未完了検出 | 記事の checkpoint-based eval に相当 |
| Eval/Benchmarking | `scripts/eval/` に reviewer-eval-tuples.json, run_reviewer_eval.py, aggregate_benchmark.py | 記事の A/B worktree 手法とは異なるが eval は実装済み |
| Sub-Agent Context Problem 対策 | subagent-framing.md, subagent-delegation-guide.md, agent_teams_integration.md (memory) | フレーミング注入パターンで対応 |
| Orchestrator Sequential Phases | S/M/L ワークフロー: Plan → Risk Analysis → Implement → Test → Review → Verify → Security Check | 記事の 5 phase を 7 phase に拡張 |
| Half-Clone (PreCompact) | `half-clone.sh` が PreCompact で実行 | claude-code-tips 統合で実装済み |
| Output Offload | output-offload.py (150行/6000文字超を退避) | 記事の tmux アプローチとは異なるが同じ目的 |

### Part 3 (Security) — 多くが実装済み

| 記事の推奨 | 現在の実装 | 評価 |
|---|---|---|
| Secret-bearing path deny rules | .env, .pem, credentials, token, secret, .key, ~/.ssh, ~/.aws すべて deny | 記事の推奨を超過 |
| Network egress deny | curl, wget, ssh, scp, nc, ncat, netcat すべて deny | 記事の推奨を超過 |
| Destructive ops deny | rm -rf, force push, hard reset, clean, chmod 777, --no-verify | 記事の推奨を超過 |
| `enableAllProjectMcpServers: false` | 設定済み | 完全一致 |
| Memory 分離 (user/project/local) | 3層分離済み。memory-archive.py で古い memory をアーカイブ | 実装済み |
| Event logging | session_events.py, skill-tracker.py, trace_sampler.py | 部分的に実装 |
| Autonomous resource bounds | autonomous スキルに budget cap, max sessions | 実装済み |
| Linter config 保護 | protect-linter-config.py (PreToolUse) | 記事にない独自機能 |
| Golden Principles 自動検出 | golden-check.py (PostToolUse) + GP-001〜011 | 記事にない独自機能 |

---

## 2. 活かせるもの (Can Be Adopted)

記事で推奨されており、現在未実装だが導入価値があるもの。

### 優先度: 高

#### 2.1 mgrep プラグイン導入
- **記事の主張**: ripgrep の約半分のトークン消費。セマンティック検索 + Web 検索対応
- **現状**: 未インストール
- **導入効果**: 特に大規模コードベースでの探索時のトークン節約
- **工数**: S (プラグインインストールのみ)
- **アクション**: `claude plugin marketplace add https://github.com/mixedbread-ai/mgrep`

#### ~~2.2 サブエージェントのモデル指定最適化~~ → **実装済み**
- **記事の主張**: Haiku で十分なタスクに Opus を使うのは無駄。5x コスト差
- **現状**: ✅ 全 31 エージェントに model 指定済み
  - `haiku` (6): triage-router, codex-reviewer, codex-debugger, safe-git-inspector, doc-gardener, gemini-explore, db-reader, codex-risk-reviewer
  - `sonnet` (22): code-reviewer, build-fixer, frontend-developer, debugger 等
  - `opus` (1): security-reviewer
- **評価**: 記事の推奨を完全に実装済み。読み取り専用は haiku、通常作業は sonnet、セキュリティは opus の適切な配置

#### 2.3 Untrusted repo 向け Docker sandbox テンプレート
- **記事の主張**: 未信頼リポジトリは `--network=none` コンテナで分離
- **現状**: 未実装。ローカルマシンで直接実行
- **導入効果**: クローンした外部リポジトリのレビュー時の爆発半径を制限
- **工数**: M (devcontainer テンプレート + playbook 作成)
- **アクション**: `docs/playbooks/untrusted-repo-review.md` に手順を記載。`docker run --network=none` のワンライナーをスキル化

### 優先度: 中

#### 2.4 Unicode/Injection スキャン hook
- **記事の主張**: zero-width chars, bidi overrides, hidden HTML をスキャン
- **現状**: 未実装
- **導入効果**: 外部コンテンツ（PR, MCP 出力, WebFetch 結果）経由のプロンプトインジェクション検出
- **工数**: M (PostToolUse/Read に hook 追加)
- **アクション**: `scripts/policy/sanitize-input.py` を作成。Read/WebFetch の出力に zero-width / bidi / base64 パターンを検出して警告

#### 2.5 Kill Switch / Dead-Man Switch
- **記事の主張**: autonomous 実行にはハートビートベースの dead-man switch が必須
- **現状**: autonomous スキルに budget cap と max sessions はあるが、ハートビート監視なし
- **導入効果**: autonomous/ralph loop が暴走した場合のフェイルセーフ
- **工数**: M (supervisor スクリプト + heartbeat ファイル)
- **アクション**: `tools/deadman-switch.sh` — 30秒ハートビート監視、停止時にプロセスグループ SIGKILL

#### 2.6 構造化ツールコールログ
- **記事の主張**: tool name, input, files, approval, network attempts をログ
- **現状**: session_events.py はイベントベースだが、全ツールコールの構造化ログではない
- **導入効果**: セキュリティ監査、異常検出、パフォーマンス分析
- **工数**: M (PostToolUse catch-all hook の拡張)
- **アクション**: `post-any` hook（既存の Rust バイナリ）に JSONL ログ出力を追加

#### 2.6b Hook Profile System (run-with-flags パターン)
- **ECC の実装**: 全 hook が `minimal/standard/strict` プロファイルで制御可能
- **現状**: 全 hook が常時有効。デバッグ時に一部 hook を無効化する手段がない
- **導入効果**: hook が問題を起こした時の切り分け、重い hook の一時無効化
- **工数**: M (Rust バイナリに profile 判定を追加。env `ECC_HOOK_PROFILE=minimal|standard|strict`)
- **アクション**: `claude-hooks` バイナリに `--profile` フラグを追加。`settings.local.json` の env で切り替え

#### 2.6c Cost Tracker (セッションコスト追跡)
- **ECC の実装**: Stop hook でトークン・コストメトリクスを記録
- **現状**: session_events.py はイベントを記録するがコスト追跡なし
- **導入効果**: どのセッション/タスクがコストを消費しているかの可視化
- **工数**: S (session-learner.py にコストメトリクス追加、またはスタンドアロンスクリプト)
- **アクション**: Claude Code の statusline JSON からトークン数を取得し JSONL に記録

### 優先度: 低

#### 2.7 CLI Aliases (claude-dev / claude-review / claude-research)
- **記事の主張**: `--system-prompt` でモード別コンテキスト注入
- **現状**: rules/ と file-pattern-router.py で動的ルーティング済み
- **導入効果**: わずかなトークン節約（system prompt 階層 vs tool result 階層）
- **判定**: 既存の仕組みで十分。記事自身も「marginal」と認めている

#### 2.8 Codemap Updater
- **記事の主張**: チェックポイントごとにコードマップを更新して探索コスト削減
- **現状**: 未実装
- **導入効果**: 大規模プロジェクトでの探索トークン節約
- **判定**: dotfiles はコードベースではないので優先度低。他プロジェクト向けスキルとして将来検討

#### 2.9 Supply Chain Scanning (Snyk agent-scan / AgentShield)
- **記事の主張**: skills, hooks, MCP configs をサプライチェーン成果物としてスキャン
- **現状**: 未実装
- **導入効果**: 外部 skill/plugin の安全性検証
- **判定**: 現在のスキルはほぼ自作なのでリスク低。外部 skill を大量導入する場合に検討

---

## 3. 覚えておくもの (Key Insights to Remember)

### セキュリティ原則

1. **Simon Willison の Lethal Trifecta**: private data + untrusted content + external communication が同一ランタイムにあると致命的。現在の deny ルールはこの3つの交差を制限している
2. **Convenience layer ≤ Isolation layer**: 便利さが隔離層を追い越してはならない。autonomous 実行時は特に注意
3. **Memory は攻撃面**: Microsoft AI Recommendation Poisoning — ペイロードは1発で勝つ必要がなく、memory に断片を植え付けて後で組み立てられる。untrusted 実行後の memory rotation を意識する
4. **Skills はサプライチェーン成果物**: Snyk ToxicSkills で 3,984 public skills の 36% にプロンプトインジェクション。外部 skill 導入時は必ず内容を検証

### ワークフロー知見

5. **Agent Abstraction Tierlist**: Tier 1 (Subagents, Metaprompting) から始めて Tier 2 (Long-running, Parallel) は必要時のみ。現在の設定は Tier 1 が強固
6. **最小限の並列化で最大成果**: 並列インスタンスは 3-4 が上限。それ以上は mental overhead > productivity
7. **Sub-Agent Context Problem**: サブエージェントには query だけでなく objective (目的) も渡す。現在の subagent-framing.md がこれに対応
8. **Investment in patterns > Investment in model tricks**: モデルは進化するがワークフローパターンは移植可能 (@omarsar0)

### トークン経済学

9. **Modular codebase = cheaper tokens**: ファイルが短いほど Read 回数が減りトークン節約
10. **MCP lazy loading**: 最新の Claude Code では MCP のコンテキスト消費が改善。ただしトークンコストは CLI + skills アプローチの方が安い場合がある

### CVE 関連

11. **CVE-2025-59536** (CVSS 8.7): プロジェクト設定が trust dialog 前に実行される脆弱性。v1.0.111 で修正
12. **CVE-2026-21852**: `ANTHROPIC_BASE_URL` override による API キー漏洩。v2.0.65 で修正
13. **OWASP MCP Top 10**: tool poisoning, prompt injection via contextual payloads, command injection, shadow MCP servers, secret exposure

---

## 4. 改善すべきもの (Should Be Improved)

### 4.1 即座に改善すべき (Quick Wins)

| 項目 | 現状の問題 | 改善案 | 工数 |
|---|---|---|---|
| ~~エージェント model 未指定~~ | ✅ 全31エージェントに model 指定済み (haiku:8, sonnet:22, opus:1) | 対応不要 | — |
| curl deny の影響範囲 | `Bash(curl *)` が deny だが MCP は別経路なので影響なし | `codex exec` や `gemini` の内部 HTTP に影響しない事を確認済みか検証 | S |

### 4.2 中期的に改善すべき

| 項目 | 現状の問題 | 改善案 | 工数 |
|---|---|---|---|
| Untrusted repo 隔離なし | 外部リポジトリを直接ローカルで開いている | Docker sandbox テンプレート + playbook | M |
| Dead-man switch なし | autonomous 暴走時のフェイルセーフ不足 | heartbeat 監視スクリプト | M |
| 入力サニタイゼーション不足 | 外部コンテンツの Unicode/injection チェックなし | sanitize-input.py hook | M |
| ツールコール構造化ログ不足 | イベントベースだが全ツールの JSONL ログではない | post-any hook に JSONL 出力追加 | M |

### 4.3 長期的に検討

| 項目 | 現状の問題 | 改善案 | 工数 |
|---|---|---|---|
| Agent identity 分離 | 個人アカウントでエージェント実行 | Bot account + short-lived token | L |
| Memory rotation | untrusted 実行後の memory クリーンアップなし | untrusted session 後の自動 memory rotation | M |
| eval 体系拡充 | reviewer eval のみ | pass@k / pass^k メトリクス、grader 多様化 | L |

---

## 5. 記事 vs 現在の設定: サマリ比較

```
記事の推奨項目数 (重複排除): ~45
実装済み:                      ~31 (69%)
実装済み + 超過:               ~21 (47%) ← 記事より進んでいる
採用可能:                      ~9  (20%)
不要/低優先:                   ~5  (11%)
```

### 現在の設定が記事を超えている領域

1. **Hook 4層分離 + Rust バイナリ**: 記事は JSON 定義のみ。当設定は runtime/policy/lifecycle/learner + Rust 高速化
2. **AutoEvolve 自動改善ループ**: 記事の continuous learning は Stop hook 単体。当設定は 4層ループ (Session/Daily/Cron/OnDemand)
3. **マルチモデル統合**: 記事は Claude 単体。当設定は Codex (gpt-5.4) + Gemini CLI 統合
4. **Golden Principles 自動検出**: 記事にない独自機能 (GP-001〜011)
5. **Completion Gate + Ralph Loop**: 記事の verification は手動チェックポイント。当設定はプラン未完了の自動検出
6. **Linter Config 保護**: 記事にない独自機能
7. **Progressive Disclosure**: 記事は CLAUDE.md に全部入れる。当設定は CLAUDE.md (コア) → references/ (詳細) → rules/ (ドメイン) の3層

### 記事にあって不足している領域

1. **Docker/Container 隔離** (Part 3): untrusted repo 用の sandbox 環境がない
2. **入力サニタイゼーション** (Part 3): Unicode injection / hidden payload 検出がない
3. **Kill Switch** (Part 3): autonomous 実行の dead-man switch がない
4. **mgrep** (Part 1): トークン節約プラグイン未導入
5. **Hook Profile** (ECC repo): hook 強度の一括切り替え機構がない
6. **Cost Tracker** (ECC repo): セッションごとのコスト追跡がない

---

## 6. 推奨アクションプラン

### Phase 1: Quick Wins (今週)
1. [x] ~~サブエージェントに model 指定を追加~~ → 実装済み (haiku:8, sonnet:22, opus:1)
2. [ ] mgrep プラグインのインストールと検証
3. [ ] Cost tracker 追加 (session-learner.py 拡張 or standalone)

### Phase 2: Security Hardening (来週)
4. [ ] sanitize-input.py hook の作成 (Unicode/injection 検出)
5. [ ] untrusted-repo-review playbook + Docker テンプレート
6. [ ] dead-man switch スクリプト (autonomous 用)

### Phase 3: Observability & DX (〜月末)
7. [ ] 構造化ツールコールログ (JSONL 形式)
8. [ ] Hook Profile System (minimal/standard/strict) — Rust バイナリに統合
9. [ ] Memory rotation ポリシー (untrusted 実行後)

---

## 参考リポジトリ

- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — ECC 設定テンプレート、session examples、continuous-learning skill
- [affaan-m/agentshield](https://github.com/affaan-m/agentshield) — agent setup のセキュリティスキャンツール
