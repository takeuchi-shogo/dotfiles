# Claude Code 内部アーキテクチャ分析

**日付**: 2026-04-01
**ソース**: https://github.com/instructkr/claude-code/tree/main/src
**status**: integrated
**概要**: Anthropic Claude Code CLI の npm ソースマップから抽出されたコード（~512K行 TypeScript, ~1,900ファイル）を分析し、サブエージェント構成・スキルシステム・ワークフロー・セキュリティ設計のパターンを抽出

## Integration Decisions (2026-04-01)

| タスク | 判定 | 実施 |
|--------|------|------|
| T1: omitClaudeMd | 実施 | 7 read-only agent に追加 |
| T2: disallowedTools | 実施 | 7 read-only agent に Edit/Write/NotebookEdit 禁止追加 |
| T3: Scoped rules paths | Already | 全ルールに paths: 既設定 |
| T4: Effort レベル | 実施 | 5 agent に effort 追加 (high/medium/low) |
| T5: Context control 原則 | 実施 | workflow-guide.md に追加 |
| T6: Synthesis ガード | 実施 | dispatch/SKILL.md に追加 |
| T7: Skill 品質チェック | 実施 | skill-creator/SKILL.md に skillify 6要素追加 |

---

## 1. サブエージェント構成

### 1.1 階層構造

```
メインエージェント (QueryEngine)
├── Built-in Agents (5種)
│   ├── general-purpose  — tools: ['*'], モデル: default
│   ├── Explore          — disallowedTools で Write/Edit 禁止, モデル: haiku
│   ├── Plan             — disallowedTools で Write/Edit 禁止
│   ├── claude-code-guide — ヘルプ特化
│   ├── statusline-setup — 設定特化
│   └── verification     — GrowthBook ゲート付き (tengu_hive_evidence)
├── Custom Agents (ユーザー定義 .md ファイル)
├── Plugin Agents (プラグイン提供)
├── Policy Agents (組織ポリシー)
└── Coordinator Mode Workers (特殊モード)
```

### 1.2 AgentDefinition 統一スキーマ (loadAgentsDir.ts:106-133)

```typescript
type BaseAgentDefinition = {
  agentType: string
  whenToUse: string           // LLMがエージェント選択に使う
  tools?: string[]            // ['*'] or 特定ツール名
  disallowedTools?: string[]  // 禁止ツール（Explore は Edit/Write 禁止）
  model?: string              // 'inherit' | 'haiku' | 具体モデル名
  effort?: EffortValue
  permissionMode?: PermissionMode
  maxTurns?: number
  mcpServers?: AgentMcpServerSpec[]  // エージェント固有 MCP
  hooks?: HooksSettings              // エージェント固有 hooks
  skills?: string[]                  // プリロードするスキル
  memory?: 'user' | 'project' | 'local'  // 永続メモリスコープ
  isolation?: 'worktree' | 'remote'
  omitClaudeMd?: boolean      // CLAUDE.md を省略してトークン節約
  background?: boolean
  initialPrompt?: string
  criticalSystemReminder_EXPERIMENTAL?: string  // 毎ターン再注入
  requiredMcpServers?: string[]  // 必須 MCP
}
```

**注目フィールド**:
- `disallowedTools`: ホワイトリストでなくブラックリスト。新ツール追加時に漏れない
- `omitClaudeMd`: read-only エージェントで CLAUDE.md を省略。**週34M+ Explore spawn で 5-15 Gtok 節約**
- `memory` スコープ: user/project/local の3層
- `hooks`: エージェント固有フックの登録（スキル内 hooks と同様）
- `criticalSystemReminder_EXPERIMENTAL`: 圧縮耐性のリマインダー

### 1.3 ツール制御: disallowedTools vs tools

```typescript
// Explore: ブラックリストで Write/Edit/Agent を明示的に禁止
EXPLORE_AGENT = {
  disallowedTools: [AGENT_TOOL_NAME, FILE_EDIT_TOOL_NAME, FILE_WRITE_TOOL_NAME, NOTEBOOK_EDIT_TOOL_NAME],
  // tools は指定しない → 禁止リスト以外すべて使える
}

// general-purpose: ホワイトリストで全ツール許可
GENERAL_PURPOSE_AGENT = {
  tools: ['*'],
}
```

### 1.4 Fork Subagent (forkSubagent.ts)

親の会話コンテキストを丸ごと子にフォークする新パターン:
- `subagent_type` を省略すると暗黙的にフォーク発動
- **プロンプトキャッシュ共有**: 全 fork child が byte-identical なプレフィックスを持つよう、tool_result をプレースホルダー `"Fork started — processing in background"` に置換
- 再帰フォーク防止: `FORK_BOILERPLATE_TAG` を会話履歴で検出
- Coordinator Mode と排他: `isCoordinatorMode()` なら fork 無効

```typescript
FORK_AGENT = {
  tools: ['*'],
  model: 'inherit',           // 親のモデルを維持
  permissionMode: 'bubble',   // 権限プロンプトを親に伝播
  maxTurns: 200,
}
```

---

## 2. Coordinator Mode（マルチエージェントオーケストレーション）

### 2.1 アーキテクチャ

`CLAUDE_CODE_COORDINATOR_MODE=1` で有効化。メインエージェントが Coordinator に変貌し、Worker エージェントを指揮する。

利用可能ツール:
- `Agent` — Worker 生成
- `SendMessage` — 既存 Worker に追加指示
- `TaskStop` — Worker 停止

### 2.2 Coordinator のコア原則

| 原則 | 詳細 |
|------|------|
| **Synthesis が最重要の仕事** | リサーチ結果を自分で理解してから実装指示。「Based on your findings」は禁止 |
| **Continue vs Spawn の判断基準** | コンテキスト重複度で判断 |
| **並列がスーパーパワー** | Read-only は自由並列、Write は同一ファイルで直列 |
| **検証は独立** | 実装者と別 worker が検証。「コード存在」≠「動作」 |
| **Worker は会話が見えない** | プロンプトは自己完結（パス、行番号、型情報すべて含む） |

### 2.3 Continue vs Spawn 判断テーブル

| 状況 | 判断 | 理由 |
|------|------|------|
| リサーチが編集対象ファイルを探索済み | Continue | コンテキストに必要ファイルが既にある |
| リサーチは広範だが実装は狭い | Spawn fresh | 探索ノイズを持ち込まない |
| 失敗の修正・直近作業の延長 | Continue | エラーコンテキストがある |
| 別 worker が書いたコードの検証 | Spawn fresh | 実装の仮定を引き継がない |
| 最初の実装アプローチが完全に間違い | Spawn fresh | 失敗パスへのアンカリング回避 |

### 2.4 Worker プロンプトのアンチパターン vs ベストプラクティス

```typescript
// BAD — 怠慢な委任
"Based on your findings, fix the auth bug"
"The worker found an issue in the auth module. Please fix it."

// GOOD — 合成されたスペック
"Fix the null pointer in src/auth/validate.ts:42. The user field
on Session (src/auth/types.ts:15) is undefined when sessions expire
but the token remains cached. Add a null check before user.id
access — if null, return 401 with 'Session expired'.
Commit and report the hash."
```

### 2.5 Scratchpad パターン

Coordinator Mode では `.claude/scratchpad/` ディレクトリを共有ワークスペースとして使用。Worker 間でファイル経由で知識共有。権限プロンプトなしで読み書き可能。

---

## 3. Skills システム

### 3.1 ロード階層 (loadSkillsDir.ts)

```
sources (優先度順):
1. policySettings  — 組織管理者が配置 (managed path)
2. userSettings    — ~/.claude/skills/
3. projectSettings — .claude/skills/
4. plugin          — プラグイン提供
5. bundled         — ビルトイン
6. mcp             — MCP サーバー提供 (loadedFrom === 'mcp')
```

### 3.2 Skill の実行モデル

スキルは **forked sub-agent で実行**される（SkillTool.ts:122-150）:
1. スキルの `.md` から frontmatter + prompt を読み込み
2. `runAgent()` で isolated agent context を作成
3. 引数を `substituteArguments()` で展開
4. エージェントの完了結果をツール結果として返却

**重要**: スキルは「知識ベース」ではなく「実行可能なプロンプト」。

### 3.3 Skill Frontmatter フィールド

- `name`, `description` — LLM ルーティング用
- `tools` — 利用可能ツール制限
- `model` — モデルオーバーライド
- `effort` — reasoning effort
- `hooks` — スキル実行中のみ有効なフック
- `allowed_tools` — Bash パターンマッチ（例: `Bash(npm test:*)`）
- `shell` — シェルコマンド実行（frontmatter内で `$(command)` 展開可能）
- `arguments` — 名前付き引数（`$ARG_NAME` で置換）

### 3.4 Remote Skill Search (EXPERIMENTAL_SKILL_SEARCH)

Aki backend 経由でリモートスキルを検索・ロード。Skills Marketplace との統合。

### 3.5 Skill トークン見積もり

```typescript
// frontmatter のみでトークン見積もり（全文はロード時まで遅延）
function estimateSkillFrontmatterTokens(skill: Command): number {
  const frontmatterText = [skill.name, skill.description, skill.whenToUse]
    .filter(Boolean)
    .join(' ')
  return roughTokenCountEstimation(frontmatterText)
}
```

---

## 4. Agent Memory（永続メモリ）

### 4.1 3スコープアーキテクチャ (agentMemory.ts)

| スコープ | パス | VCS | 用途 |
|---------|------|-----|------|
| `user` | `~/.claude/agent-memory/<agentType>/` | No | ユーザー全体の学習 |
| `project` | `<cwd>/.claude/agent-memory/<agentType>/` | Yes | プロジェクト固有 |
| `local` | `<cwd>/.claude/agent-memory-local/<agentType>/` | No | 機密情報 |

リモート環境では `CLAUDE_CODE_REMOTE_MEMORY_DIR` でマウントポイントにリダイレクト。

### 4.2 Memory Snapshot (agentMemorySnapshot.ts)

- `.claude/agent-memory-snapshots/<agentType>/snapshot.json` にタイムスタンプ付きスナップショット
- プロジェクトを clone した人に初期メモリを提供（VCS に含められる）
- `.snapshot-synced.json` で `syncedFrom` timestamp を記録し、重複コピー防止
- agent 起動時に `checkAgentMemorySnapshot()` → `initializeFromSnapshot()` でスナップショットからローカルメモリを初期化

---

## 5. タスク管理

### 5.1 タスクタイプ

| タイプ | 用途 |
|--------|------|
| `LocalShellTask` | BashTool のバックグラウンド実行 |
| `LocalAgentTask` | サブエージェントのライフサイクル管理 |
| `LocalMainSessionTask` | メインセッション追跡 |
| `InProcessTeammateTask` | tmux/split-pane チームメイト |
| `RemoteAgentTask` | CCR リモート実行 |
| `DreamTask` | 非同期バックグラウンド処理 |

### 5.2 非同期エージェントライフサイクル

```
spawn → register → run → progress_update* → complete/fail → notify
```

- `<task-notification>` XML でメインエージェントに結果通知
- `output_file` で進捗の中間読み取り可能
- `SendMessage` で実行中のエージェントに追加指示
- auto-background: 120秒後に自動バックグラウンド化（`CLAUDE_AUTO_BACKGROUND_TASKS`）

### 5.3 SendMessage の構造化メッセージ

```typescript
StructuredMessage = discriminatedUnion('type', [
  { type: 'shutdown_request', reason?: string },
  { type: 'shutdown_response', request_id, approve, reason? },
  { type: 'plan_approval_response', request_id, approve, feedback? },
])
```

---

## 6. セキュリティ設計

### 6.1 BashTool — 多層セキュリティ (bashSecurity.ts, ~31K tokens)

22種のセキュリティチェック:
- コマンド置換検出 (`$()`, バッククォート, プロセス置換, Zsh `=cmd`)
- Zsh 危険コマンド (`zmodload`, `ztcp`, `syswrite`, `zf_*` 等)
- Unicode/制御文字、IFS インジェクション、brace expansion
- tree-sitter AST 解析 + regex fallback
- heredoc-in-substitution の安全パターン検証

### 6.2 OAuth — PKCE S256 + state 検証

- `randomBytes(32)` + SHA-256 で code_verifier/challenge
- `ALLOWED_OAUTH_BASE_URLS` でエンドポイントホワイトリスト
- `CLAUDE_CODE_OAUTH_CLIENT_ID` による Client ID 上書き（ホワイトリストなし — 要注意）

### 6.3 MCP — チャネル権限リレー

- `channelPermissions.ts`: 侵害チャネルサーバーが承認を偽装可能 → "accepted risk" として文書化
- `recursivelySanitizeUnicode` でMCPコンテンツサニタイズ

### 6.4 GrowthBook — フィーチャーゲート

- 全ての新機能に `getFeatureValue_CACHED_MAY_BE_STALE()` でゲート
- A/B テスト基盤として活用
- SDK キー3種がハードコード（prod/dev/ant） — クライアントキーなのでリスクは低い

---

## 7. 我々のハーネスへの統合提案

| # | Claude Code パターン | ROI | 提案 |
|---|---------------------|-----|------|
| 1 | `omitClaudeMd` | **高** | read-only エージェント (Explore等) で CLAUDE.md 省略。即座にトークン節約 |
| 2 | Coordinator Synthesis 原則 | **高** | `/dispatch` に「合成ガード」を追加。worker プロンプトに "Based on" が含まれたら警告 |
| 3 | Memory Snapshot | **中** | `.claude/agent-memory-snapshots/` でチーム共有。clone 時の初期メモリ |
| 4 | `disallowedTools` | **中** | ブラックリスト追加。新ツール追加時の漏れ防止 |
| 5 | Fork subagent cache sharing | **中** | cfork で全 child のプレフィックスを同一化 → キャッシュヒット最大化 |
| 6 | Skill 内 hooks | **低** | frontmatter に `hooks:` フィールド。スキル実行中のみ有効なフック |
| 7 | `maxTurns` 制限 | **低** | エージェント暴走防止のターン上限。現在はなし |
| 8 | `criticalSystemReminder_EXPERIMENTAL` | **低** | 圧縮耐性リマインダー。core-invariants と併用可能 |

---

## 8. 注目すべきコード品質パターン

- **Analytics 型安全**: `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS` — ログにコード/ファイルパスが混入しないことを型で強制
- **Dead code elimination**: `feature('FEATURE_FLAG')` + `bun:bundle` でビルド時にデッドコード除去
- **Lazy schema**: `lazySchema(() => z.object(...))` で循環依存回避 + 初回アクセス時のみスキーマ構築
- **SettingSource**: `'policySettings' | 'userSettings' | 'projectSettings' | 'plugin'` — 設定の出自を追跡

---

## 9. システムプロンプト構築パイプライン (constants/prompts.ts)

### 9.1 プロンプトキャッシュ最適化の核心設計

```typescript
// 静的（cross-org キャッシュ可能）と動的コンテンツの境界マーカー
export const SYSTEM_PROMPT_DYNAMIC_BOUNDARY = '__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__'
```

**設計原則**: 境界マーカーより前 = `cacheScope: 'global'` でキャッシュ。後 = ユーザー/セッション固有でキャッシュ不可。

### 9.2 SystemPromptSection — キャッシュ安全なプロンプト構築

```typescript
// メモ化セクション: 1回計算、/clear か /compact までキャッシュ
function systemPromptSection(name: string, compute: () => string | null)

// 毎ターン再計算: プロンプトキャッシュを破壊する — 明示的理由が必要
function DANGEROUS_uncachedSystemPromptSection(name: string, compute, reason: string)
```

**学び**: セクションが変わるとキャッシュが壊れる。「なぜキャッシュを壊すのか」を強制的に文書化する `DANGEROUS_` プレフィックス。

### 9.3 プロンプトセクション構成（順序が重要）

```
[Static — cacheable globally]
1. Intro (role + CYBER_RISK_INSTRUCTION + URL制限)
2. System (markdown出力, 権限モード, system-reminder, hooks, 自動圧縮)
3. Doing Tasks (SWEタスク指針, コードスタイル, セキュリティ)
4. Executing Actions with Care (可逆性とblast radius)
5. Using Your Tools (専用ツール優先, 並列呼び出し指針)
6. Tone and Style (絵文字禁止, file:line参照, GitHub URL形式)
7. Output Efficiency / Communicating (ant vs external で大きく異なる)
--- SYSTEM_PROMPT_DYNAMIC_BOUNDARY ---
[Dynamic — session-specific]
8. Session-specific guidance (AskUserQuestion, Agent, Skills, Verification)
9. Language preference
10. Output style
11. MCP instructions
12. Memory prompt (auto-memory)
13. Environment details (OS, cwd, git, model info)
14. CLAUDE.md content (userContext)
```

### 9.4 ant (内部) vs external (一般) のプロンプト分岐

| 領域 | ant (Anthropic内部) | external (一般ユーザー) |
|------|---------------------|------------------------|
| コメント規則 | 「デフォルトはコメントなし。WHYが非自明な時のみ」4段落の詳細ガイダンス | なし |
| 完了報告 | 「テストを実行、スクリプトを実行、出力を確認。検証できない場合はその旨を明示」 | なし |
| 誠実性 | 「テスト失敗を成功と報告するな」「不確実性をヘッジするな」 | なし |
| コミュニケーション | 600語の散文スタイルガイド（逆ピラミッド、意味的バックトラック禁止） | 「簡潔に。要点を先に」 |
| バグ報告 | `/issue` と `/share` の案内 + Slack チャンネルへの投稿提案 | なし |
| Explore モデル | `inherit`（親と同じ） | `haiku`（速度重視） |

### 9.5 Verification Agent の強制実行契約

```
非自明な実装（3+ファイル編集、バックエンド/API変更、インフラ変更）後:
1. MUST: verification agent を spawn
2. 自分のチェックは検証の代替にならない
3. fork の自己チェックも代替にならない
4. verifier のみが判定を付与
5. FAIL → 修正 → verifier 再開 → PASS まで繰り返し
6. PASS → spot-check（2-3コマンドを再実行して確認）
7. PARTIAL → 何が通り何が検証不能かをユーザーに報告
```

### 9.6 DiscoverSkills — 動的スキルサーフェシング

毎ターン「Skills relevant to your task:」リマインダーで関連スキルを自動提示。カバーしきれない場合のみ `DiscoverSkillsTool` を手動呼び出し。

---

## 10. プロンプトエンジニアリングの実践パターン

### 10.1 「CRITICAL」「IMPORTANT」の使い分け

prompts.ts のパターン分析:
- `CRITICAL`: 1箇所のみ（「専用ツールを Bash の代わりに使え」）
- `IMPORTANT`: 3箇所（「簡潔に」「スキルはリストにあるもののみ」「URL生成禁止」）
- 通常の指示: バレットポイントで列挙

**学び**: 強調は極めて控えめ。本当に重要な1つだけ CRITICAL。

### 10.2 ネガティブ制約の具体化パターン

```
BAD:  「不要なことをするな」
GOOD: 「Don't add docstrings, comments, or type annotations to code you didn't change.
       Only add comments where the logic isn't self-evident.」
```

すべてのネガティブ制約に「代わりに何をすべきか」が対になっている。

### 10.3 blast radius を意識した指示設計

```
「A user approving an action (like a git push) once does NOT mean that they
approve it in all contexts, so unless actions are authorized in advance in
durable instructions like CLAUDE.md files, always confirm first. Authorization
stands for the scope specified, not beyond. Match the scope of your actions
to what was actually requested.」
```

承認のスコープを明示的に制限する。「一度許可された」≠「常に許可」。

### 10.4 Fork Subagent のプロンプト指針

```
「Calling Agent without a subagent_type creates a fork, which runs in the
background and keeps its tool output out of your context — so you can keep
chatting with the user while it works. If you ARE the fork — execute directly;
do not re-delegate.」
```

再帰委譲の防止を1文で。

---

## 11. ワークフロー設計パターン

### 11.1 ツール優先順位の強制

```
専用ツール > Bash
Read > cat/head/tail
Edit > sed/awk
Write > heredoc/echo
Glob > find/ls
Grep > grep/rg
```

**理由**: 「Using dedicated tools allows the user to better understand and review your work」— ユーザーのレビュー可能性が設計原理。

### 11.2 並列ツール呼び出しの最適化指示

```
「If you intend to call multiple tools and there are no dependencies between
them, make all independent tool calls in parallel. Maximize use of parallel
tool calls where possible to increase efficiency. However, if some tool calls
depend on previous calls to inform dependent values, do NOT call these tools
in parallel.」
```

### 11.3 Task ツールの使い方

```
「Break down and manage your work with the TaskCreate tool. Mark each task
as completed as soon as you are done with the task. Do not batch up multiple
tasks before marking them as completed.」
```

タスクの完了を即座にマークする — バッチ処理しない。

### 11.4 Feature Gate パターン (bun:bundle + GrowthBook)

```typescript
// ビルド時のデッドコード除去
import { feature } from 'bun:bundle'
const module = feature('FEATURE_NAME') ? require('./module.js') : null

// ランタイムの A/B テスト
getFeatureValue_CACHED_MAY_BE_STALE('tengu_flag_name', defaultValue)
```

2段階ゲート: ビルド時 (`feature()`) + ランタイム (`GrowthBook`)。

---

## 12. コンテキスト管理と最適化

### 12.1 SYSTEM_PROMPT_DYNAMIC_BOUNDARY

プロンプトキャッシュの2分割:
- **Before boundary**: 全ユーザー共通（グローバルキャッシュ）
- **After boundary**: セッション固有（キャッシュ不可）

条件分岐（`if ant`, `if fork enabled` 等）が境界前にあるとキャッシュ変種が 2^N に爆発。Session-specific な分岐は必ず境界後に配置。

### 12.2 omitClaudeMd による Gtok 節約

Explore agent で CLAUDE.md を省略:
```typescript
omitClaudeMd: true,  // Explore は read-only — commit/PR/lint ルール不要
```
**効果**: 週34M+ spawn × CLAUDE.md トークン → 5-15 Gtok/week 節約

### 12.3 Skill frontmatter のみのトークン見積もり

```typescript
// 全文はロード時まで遅延。frontmatter のみで見積もり
function estimateSkillFrontmatterTokens(skill): number {
  const text = [skill.name, skill.description, skill.whenToUse].join(' ')
  return roughTokenCountEstimation(text)
}
```

---

## 13. セキュリティ設計の深層

### 13.1 Analytics 型安全 — ログ汚染防止

```typescript
type AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS = string
```

ログに送信する文字列を「コードやファイルパスでないことを確認した」と型で宣言する。型名自体が確認プロセスの文書化。

### 13.2 コマンドパース二重化

bashSecurity.ts の検証は2段階:
1. **tree-sitter AST 解析** — 構造的に正確
2. **Regex fallback** — tree-sitter が使えない場合

```typescript
treeSitter?: TreeSitterAnalysis | null  // あれば使う、なければ regex
```

### 13.3 Permission ルールの型安全な分類

```typescript
type ToolPermissionContext = {
  mode: PermissionMode
  alwaysAllowRules: ToolPermissionRulesBySource
  alwaysDenyRules: ToolPermissionRulesBySource
  alwaysAskRules: ToolPermissionRulesBySource
  shouldAvoidPermissionPrompts?: boolean  // バックグラウンドエージェント用
  awaitAutomatedChecksBeforeDialog?: boolean  // coordinator worker用
}
```

---

## メタ情報

- **リポジトリ**: instructkr/claude-code（大学生によるソースマップ抽出アーカイブ、2026-03-31 発見）
- **コードベース規模**: ~512K行 TypeScript, ~1,900ファイル
- **分析範囲**: src/tools/AgentTool/, src/skills/, src/coordinator/, src/tasks/, src/services/oauth/, src/services/mcp/, src/tools/BashTool/, src/constants/, src/memdir/, src/services/, src/utils/
- **分析フェーズ**: Phase 1 (セキュリティ+アーキテクチャ) + Phase 2 (プロンプト+ワークフロー+実践パターン) + Phase 3 (Hook/Memory/Compact) + Phase 4 (X記事照合+未探索パターン)

---

## 18. CLAUDE.md 4層メモリ階層と @include (utils/claudemd.ts)

### 18.1 4層ロード順序（後ほどロード = 高優先度）

```
1. Managed memory  — /etc/claude-code/CLAUDE.md（組織管理者）
2. User memory     — ~/.claude/CLAUDE.md（ユーザー個人）
3. Project memory  — CLAUDE.md, .claude/CLAUDE.md, .claude/rules/*.md（VCS追跡）
4. Local memory    — CLAUDE.local.md（VCS非追跡、ローカル上書き）
```

**核心原理**: 「Files loaded later get higher priority because the model pays more attention to what appears later in the context window.」CWD に近いファイルが後にロードされ、上位を上書きする。

### 18.2 @include ディレクティブ

```markdown
@path               — 相対パス（@./path と同じ）
@./relative/path    — 明示的相対パス
@~/home/path        — ホームディレクトリ起点
@/absolute/path     — 絶対パス
```

- テキストファイルのみ（.md, .ts, .json, .yaml 等、バイナリ除外）
- 循環参照防止（処理済みファイル追跡）
- 存在しないファイルは silent skip
- コードブロック・コード文字列内では無効（leaf text nodes のみ）
- 含まれたファイルは**含む側のファイルの前に**挿入される

### 18.3 Scoped Rules with Glob Frontmatter

```markdown
# .claude/rules/api-rules.md
---
paths:
  - "src/api/**"
  - "src/services/**"
---
Always use dependency injection.
```

picomatch で glob パターンマッチ。Claude がマッチするファイルを触った時のみルールがアクティブ化。

### 18.4 HTML コメントの不可視化

CLAUDE.md 内の `<!-- comment -->` は agent に注入される際にストリップされる。人間用のメモ・TODO・ドキュメンテーションを agent に見せずに残せる。

### 18.5 MEMORY_INSTRUCTION_PROMPT

```typescript
const MEMORY_INSTRUCTION_PROMPT =
  'Codebase and user instructions are shown below. Be sure to adhere to these
   instructions. IMPORTANT: These instructions OVERRIDE any default behavior
   and you MUST follow them exactly as written.'
```

CLAUDE.md の内容はデフォルトの動作を**上書き**すると明示的に宣言される。

---

## 19. Effort システム (utils/effort.ts)

### 19.1 Effort レベル

```typescript
type EffortLevel = 'low' | 'medium' | 'high' | 'max'
// 数値指定も可能（EffortValue = EffortLevel | number）
```

- `max` effort は Opus 4.6 のみサポート
- `low` → 簡単なタスク、`high` → 設計判断
- `/effort auto` でリセット
- スピナーに現在レベル表示

### 19.2 モデル別 Effort サポート

```typescript
// opus-4-6, sonnet-4-6 → effort サポート
// haiku → 非サポート
// 不明なモデル: 1P → true, 3P → false
```

---

## 20. Undercover Mode (utils/undercover.ts)

### 20.1 動作原理

Anthropic 内部ユーザーが**公開リポジトリ**で作業する際の情報漏洩防止:

```
自動検出: リポジトリリモートが内部 allowlist にない → ON
強制ON: CLAUDE_CODE_UNDERCOVER=1
強制OFF: なし（安全側デフォルト）
```

### 20.2 Undercover 指示の内容

コミットメッセージ・PR に以下を**絶対含めない**:
- 内部モデルコードネーム（Capybara, Tengu 等の動物名）
- 未リリースモデルバージョン番号
- 内部リポジトリ・プロジェクト名
- Slack チャンネル、内部リンク
- 「Claude Code」の言及、AI であることの示唆
- Co-Authored-By 行

```
GOOD: "Fix race condition in file watcher initialization"
BAD:  "Fix bug found while testing with Claude Capybara"
BAD:  "1-shotted by claude-opus-4-6"
```

### 20.3 我々への学び

Undercover Mode 自体は不要だが、**コミットメッセージからの情報漏洩防止**パターンは参考になる。我々の `/commit` スキルに「秘密情報チェック」を追加できる。

---

## 21. 隠し機能: Kairos, Buddy, Auto Mode

### 21.1 Kairos (daemon mode)

`feature('KAIROS')` でゲート。未リリースの自律デーモンモード:
- バックグラウンドセッション
- BriefTool (短い報告ツール)
- プロアクティブなタスク提案
- メモリ統合

ソースコード内で `proactiveModule` として条件的にロードされている。

### 21.2 Buddy System

記事が言及する「18種、レアリティ、シャイニー」のペットシステム。`src/buddy/` ディレクトリに存在を確認。チームモラルやエンゲージメント用のイースターエッグ的機能。

### 21.3 Auto Mode の内部構造

記事の主張: 「Input-layer injection probe + output-layer transcript classifier」

2段構え:
1. **入力側**: プロンプトインジェクションプローブ（悪意ある入力の検出）
2. **出力側**: トランスクリプト分類器（安全な操作は自動承認、危険な操作はブロック）

`PermissionDenied` hook で分類器が拒否した場合にリトライ可能。

---

## 22. X 記事 (Kr$na) との照合結果

| 記事の主張 | ソースコード検証 | 正確性 |
|-----------|----------------|--------|
| 4層メモリ階層 | `claudemd.ts:1-26` で明確に文書化 | 正確 |
| 後にロードされたファイルが高優先 | `claudemd.ts:9` | 正確 |
| @include 5層深さ | `claudemd.ts:19-25` 循環参照防止あり | 正確 |
| HTML コメント不可視 | ストリップ処理確認 | 正確 |
| Scoped rules with glob | `picomatch` 使用確認 | 正確 |
| Effort レベル | `effort.ts` 4レベル + 数値 | 正確 |
| Undercover Mode の OFF スイッチなし | `undercover.ts:17` | 正確 |
| Kairos daemon mode | `feature('KAIROS')` 複数箇所 | 存在確認 |
| Buddy System 18種 | `src/buddy/` 確認 | 存在確認 |
| Auto mode 2段分類器 | 間接的に確認 | 概ね正確 |
| プロンプトキャッシュ 12x コスト削減 | `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` | 仕組みは確認 |

---

## 23. 統合提案（Phase 4 追加分）

| # | パターン | ROI | 我々への適用 |
|---|---------|-----|-------------|
| 15 | 4層 CLAUDE.md 優先度順序 | **高** | 我々も同様の仕組みだが「後=高優先」を意識的に設計しているか再確認 |
| 16 | @include ディレクティブ | **高** | CLAUDE.md から architecture doc や style guide を参照。既にファイル結合で似たことをしているが、native サポートに移行 |
| 17 | Scoped rules (glob frontmatter) | **高** | `.claude/rules/*.md` でファイルパスに応じたルール適用。Go/TS/Rust で異なるルールを自動切替 |
| 18 | MEMORY_INSTRUCTION_PROMPT | **中** | 「これらの指示はデフォルト動作を上書きする」の明示宣言 |
| 19 | Effort レベル活用 | **中** | エージェント定義に `effort: 'high'` を指定して推論品質を制御 |
| 20 | HTML コメント不可視化 | **低** | CLAUDE.md に人間用メモを残せる |

---

## 14. Hook システム (utils/hooks/)

### 14.1 Hook イベントタイプ

```typescript
type HookExecutionEvent =
  | HookStartedEvent   // hookId, hookName, hookEvent
  | HookProgressEvent  // + stdout, stderr, output
  | HookResponseEvent  // + exitCode, outcome: 'success' | 'error' | 'cancelled'
```

Always-emitted events: `SessionStart`, `Setup` — これらは `includeHookEvents` オプションに関係なく常に発火。

### 14.2 Hook 関連ファイル群

| ファイル | 役割 |
|---------|------|
| `hookEvents.ts` | イベントバス（emit/register パターン） |
| `AsyncHookRegistry.ts` | 非同期 hook レジストリ |
| `execAgentHook.ts` | エージェント hook 実行 |
| `execHttpHook.ts` | HTTP hook 実行 |
| `execPromptHook.ts` | プロンプト hook 実行 |
| `hooksConfigManager.ts` | 設定管理 |
| `hooksConfigSnapshot.ts` | 設定スナップショット |
| `hooksSettings.ts` | 設定スキーマ |
| `registerFrontmatterHooks.ts` | frontmatter からの hook 登録 |
| `registerSkillHooks.ts` | スキル固有 hook 登録 |
| `sessionHooks.ts` | セッションスコープ hook |
| `postSamplingHooks.ts` | サンプリング後 hook |
| `ssrfGuard.ts` | SSRF 防止 |
| `skillImprovement.ts` | スキル改善 hook |
| `fileChangedWatcher.ts` | ファイル変更監視 |

### 14.3 Hook 実行タイプの多様性

3種の実行方式:
- **Shell hook** (`execPromptHook`): シェルコマンドを実行、stdout/stderr をキャプチャ
- **HTTP hook** (`execHttpHook`): HTTP リクエストを送信、レスポンスをパース
- **Agent hook** (`execAgentHook`): サブエージェントを spawn して実行

### 14.4 Frontmatter Hook 登録

エージェント・スキルの frontmatter に `hooks:` を定義すると、`registerFrontmatterHooks` がエージェント/スキル起動時にセッションスコープで登録し、終了時に解除する。

**学び**: 我々のハーネスと同等のライフサイクルだが、HTTP hook と Agent hook は新しい。特に Agent hook は「hook 内でサブエージェントを spawn する」パターン。

---

## 15. Auto-Memory システム (memdir/, services/extractMemories/)

### 15.1 メモリディレクトリ構造

```
~/.claude/projects/<sanitized-path>/memory/
├── MEMORY.md          # インデックス（200行 / 25KB 上限）
├── user_*.md          # ユーザーメモリ
├── feedback_*.md      # フィードバックメモリ
├── project_*.md       # プロジェクトメモリ
└── reference_*.md     # リファレンスメモリ
```

### 15.2 MEMORY.md トランケーション

```typescript
MAX_ENTRYPOINT_LINES = 200
MAX_ENTRYPOINT_BYTES = 25_000  // ~125 chars/line × 200 lines

// 行→バイト の順でトランケート
// 最後の改行で切断（mid-line 防止）
// 超過時に WARNING を自動追記
```

**学び**: 我々の MEMORY.md にも同様の上限がある。Claude Code の実装では行数+バイト数の二重チェック。「長い行」が行数チェックをすり抜けるケースを byte cap で捕捉。

### 15.3 Auto-Memory 抽出パイプライン

```
complete query loop (tool call なしの最終応答)
→ handleStopHooks
→ extractMemories
→ runForkedAgent (親のプロンプトキャッシュを共有)
→ Read/Write/Edit で memory/ に保存
```

重要な設計:
- **forked agent パターン**: 親の会話をフォークして実行。プロンプトキャッシュを共有
- **トリガー条件**: モデルが tool call なしの最終応答を出した時（=ターン完了時）
- **状態管理**: closure-scoped（モジュールレベルでなく initExtractMemories() 内）

### 15.4 メモリタイプ定義

`memoryTypes.ts` で4タイプを定義:
- `user` — ユーザーの役割・好み
- `feedback` — 作業アプローチへのフィードバック
- `project` — プロジェクト固有の情報
- `reference` — 外部リソースへのポインタ

各タイプに `when_to_save`, `how_to_use`, `body_structure`, `examples` が定義されている — これは我々のメモリシステムプロンプトとほぼ同一。

### 15.5 メモリ検索: Sonnet 関連性フィルタ

> Source: himanshustwts 記事 "Claude Code's Memory System Explained" (2026-04-01)

メモリ検索は以下のフローで行われる:

1. **MEMORY.md（インデックス）は常時ロード** — 200行 / 25KB 上限。全ターンのシステムプロンプトに含まれる
2. **個別メモリファイルはオンデマンドロード** — Sonnet（メインモデルが Opus でも）が関連性フィルタとして動作
3. **Sonnet の入力**: 全メモリファイルの frontmatter（最大200ファイル、新しい順）をマニフェストとして受信
   - フォーマット: `[type] filename (timestamp): description`
   - **description フィールドのみが判断材料** — 本文は読まれない
4. **出力**: top 5 のファイル名を返す → それらのみコンテキストにロード
5. **除外ルール**:
   - 前のターンで既に表示済みのファイルは除外（5枠を新鮮なメモリに使う）
   - 不確実なら含めない（"if you are unsure, do not include it"）
   - 使用中ツールのドキュメントは除外、ただし警告・注意点は含める

**Staleness warning**: 1日超のメモリには「この記憶は X 日前のものです。ファイルパスや関数名は古い可能性があります」が自動注入される。

**設計への示唆**:
- description の品質 = 検索精度。具体的なキーワード・使用場面を含めるべき
- 200行のインデックス予算は貴重。各行は常にトークンを消費する
- top 5 制限があるため、1ファイル=1トピックの粒度が最適

### 15.6 AutoDream 統合プロセス

> Source: 同記事

`autoDream` は定期的なメモリ統合バックグラウンドプロセス:

- **トリガー条件**: 24時間 + 5セッション経過（前回統合から）
- **ゲート**: `tengu_onyx_plover` フラグ（未リリースの可能性あり）
- **4フェーズ**:
  1. **Read**: MEMORY.md + 既存トピックファイルを読み込み
  2. **Gather**: 直近のデイリーログ・セッショントランスクリプトから narrow grep でシグナル収集（全文読みはしない）
  3. **Merge**: 新情報を既存ファイルにマージ。相対日付→絶対日付変換。コードベースと矛盾する事実を削除
  4. **Prune**: 古いポインタ削除、冗長エントリ短縮、ファイル間の矛盾解消（"2ファイルが矛盾したら間違っている方を修正"）
- **実行形式**: forked subagent（read/write ツール + ロックファイルで並行実行防止）
- **削除ポリシー**: 自動期限なし。エージェントの判断でのみ削除（矛盾・無関連化時）

**我々の `/improve` との対比**: AutoDream ≈ 我々の AutoEvolve 日次ループ。ただし AutoDream はメモリ専用で、我々は設定全体を対象とする点が異なる。

### 15.7 重複防止メカニズム

- `hasMemoryWritesSince()`: メイン会話中にメモリ書き込みがあった場合、バックグラウンド抽出エージェントはスキップ
- メインエージェントとバックグラウンドエージェントは相互排他（同一ターンウィンドウで二重書き込みしない）

### 15.8 メモリパスセキュリティ

- `autoMemoryDirectory` は **グローバル settings.json のみ** で設定可能（プロジェクトレベル設定は拒否）
- 理由: 悪意あるリポジトリが `~/.ssh` 等にパスを設定すると機密ファイルへの書き込みアクセスを得られる
- パス検証: `..` セグメント、ルートパス、null バイトに対するトラバーサル攻撃防止
- 抽出エージェントのサンドボックス: `isAutoMemPath()` を通過するパスのみ書き込み許可

### 15.9 Team Memory

`feature('TEAMMEM')` ゲート付きで、チーム間メモリ共有機能が実装途中:
- `teamMemPaths.ts` — チームメモリパス
- `teamMemPrompts.ts` — チームメモリプロンプト

---

## 16. Context Compaction (services/compact/)

### 16.1 Auto-Compact トリガー

```typescript
AUTOCOMPACT_BUFFER_TOKENS = 13_000
WARNING_THRESHOLD_BUFFER_TOKENS = 20_000
MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3  // circuit breaker

threshold = effectiveContextWindow - AUTOCOMPACT_BUFFER_TOKENS
// effectiveContextWindow = contextWindow - MAX_OUTPUT_TOKENS_FOR_SUMMARY(20K)
```

### 16.2 Compaction 関連ファイル

| ファイル | 役割 |
|---------|------|
| `autoCompact.ts` | 自動圧縮トリガー判定 |
| `compact.ts` | 圧縮実行ロジック |
| `microCompact.ts` | マイクロ圧縮（軽量版） |
| `apiMicrocompact.ts` | API経由マイクロ圧縮 |
| `grouping.ts` | メッセージグルーピング |
| `postCompactCleanup.ts` | 圧縮後クリーンアップ |
| `sessionMemoryCompact.ts` | セッションメモリ圧縮 |
| `compactWarningHook.ts` | 圧縮警告 hook |
| `prompt.ts` | 圧縮プロンプト |
| `timeBasedMCConfig.ts` | 時間ベース設定 |

### 16.3 Circuit Breaker パターン

```
autocompact 失敗 → consecutiveFailures++
3回連続失敗 → autocompact 停止
// BQ: 1,279セッションで50+連続失敗（最大3,272回）→ ~250K API calls/day 無駄
```

**学び**: 我々の compaction にも circuit breaker が必要。Claude Code は3回で停止。

### 16.4 Post-Compact Cleanup

圧縮後に `postCompactCleanup.ts` と `sessionMemoryCompact.ts` が実行される。セッションメモリの重要情報を圧縮版に引き継ぐ仕組み。

---

## 17. 統合提案（Phase 3 追加分）

| # | パターン | ROI | 我々への適用 |
|---|---------|-----|-------------|
| 9 | Auto-memory forked agent | **高** | 現在の memory 保存は inline。forked agent にすればメインコンテキストを消費しない |
| 10 | MEMORY.md 行+バイト二重上限 | **中** | 行数チェックだけでなくバイト数チェック追加（長い行のすり抜け防止） |
| 11 | Compact circuit breaker | **中** | 3回連続失敗で停止。250K calls/day の無駄を防止 |
| 12 | Agent hook / HTTP hook | **中** | hook 内で subagent spawn や HTTP 通知。現在の shell hook のみから拡張 |
| 13 | Frontmatter hook lifecycle | **低** | スキル/エージェント起動時に登録、終了時に解除。既に我々も実装済みだが明示化 |
| 14 | Team Memory | **将来** | チーム間メモリ共有。`feature('TEAMMEM')` で実装途中 |
