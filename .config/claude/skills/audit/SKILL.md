---
name: audit
description: >
  コードベース全体の品質監査を実行し、優先度付き QUESTIONS.md を生成する。セキュリティ、アーキテクチャ、
  パフォーマンス、テスト、コード品質を網羅的にスキャンし、file:line 参照と Answer フィールド付きの
  構造化レポートを出力する。回答後は /spec や /epd に接続して改善を実装する。
  Triggers: 'コードベース監査', 'codebase audit', '全体レビュー', 'QUESTIONS.md', '品質監査',
  'コード監査', 'full audit', 'プロジェクト診断', '技術的負債の洗い出し', 'tech debt audit',
  'コードの健全性', 'codebase health'.
  Do NOT use for: 直近の差分レビュー (use /review)、ドキュメント鮮度チェック (use /check-health)、
  AI ワークフロー監査 (use /ai-workflow-audit)、skill 定義の health/衝突検出 (use skill-audit)、
  アーキテクチャ深化候補の診断 (use improve-codebase-architecture)。
origin: self
allowed-tools: Read, Bash, Grep, Glob, Agent
metadata:
  pattern: pipeline
---

# Codebase Audit

コードベース全体を監査し、優先度付き QUESTIONS.md を生成するパイプライン。
Gemini(1M) で俯瞰スキャン → カテゴリ別並列エージェントで深掘り → 統合レポート出力。

## 使い分け

| スキル | 対象 | タイミング |
|--------|------|-----------|
| `/audit` | コードベース全体 | 新プロジェクト参入時、定期品質監査 |
| `/review` | 直近の差分 | コード変更後 |
| `/check-health` | ドキュメント鮮度 | 調査開始時 |

## Step 1 — Orient Gate（アーキテクチャ理解の強制ゲート）

> **Tech-Debt-Skill (ksimback) の knowledge**: 監査の品質はアーキテクチャ理解で決まる。ファイル一覧+技術スタックだけでは「コードを読んだ」ではない。Orient できないなら Audit に進ませない。

プロジェクトの全体像と**構造的理解**を獲得する。ここを通過できないと以降のステップは表面的になる。

```bash
# プロジェクト構造
find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' | head -200

# 技術スタック検出
ls -la package.json Cargo.toml go.mod pyproject.toml Gemfile composer.json *.csproj Taskfile.yml Makefile 2>/dev/null

# git 統計（churn パターン）
git log --oneline -20
git shortlog -sn --no-merges | head -10
git log --format=format: --name-only --since="6 months ago" | grep -v '^$' | sort | uniq -c | sort -rg | head -20
```

### Orient 4要素（mandatory）

監査者は以下 4 要素を**自分の言葉で文章化**できるまで進んではならない。`docs/architecture.md` や README に既述されていれば引用 + 確認、なければ Read で構築する。

| 要素 | 質問 | 失敗時の対応 |
|------|------|-------------|
| **境界 (Boundaries)** | 主要モジュール/サービスは何か。それぞれの責務は？ | `/spike` で構造調査 |
| **主要 flow (Main Flows)** | 代表的なユースケース 2-3 個のデータ流（entry → core → exit） | エントリポイント Read |
| **不変条件 (Invariants)** | 壊してはいけないルール（例: トランザクション境界、データ整合性、認証順序） | コード/コメントから抽出 |
| **runtime surface** | 外部接点（HTTP/DB/queue/file/env）。trust boundary はどこか | config + entry point Read |

**Gate**: 上記 4 要素を**それぞれ 2-4 行で要約**できなければ進まない。要約できない要素は監査の **blind spot** として QUESTIONS.md の冒頭に明記する。

**スキップ可能ケース**: ファイル数 50 未満かつ単一エントリポイントの場合は要素を統合した 5-10 行の要約で代替可。

## Step 2 — Deep Scan（深層スキャン）

Gemini(1M コンテキスト) を使ってコードベース全体を一括分析する。
Claude の 200K では収まらない大規模コードベースでも対応可能。

### Step 2.0 — Structural Pre-filter（オプション、推奨）

> **2026 ベストプラクティス (Gemini 補完)**: SAST + LLM Triage hybrid。LLM が直接 grep するより、構造検索で疑わしいパターンを絞ってから triage する方が精度・コスト共に優位。

LLM 監査は hallucination リスクがある。決定論的な構造検索で**事前候補**を抽出してから LLM に渡すと信頼性が上がる。

| ツール | 対象 | 用途 |
|--------|------|------|
| `ast-grep` | 全言語 | パターンマッチ（例: `console.log`, `unwrap()`, raw SQL 文字列連結） |
| `madge --circular` | TS/JS | 循環参照検出 |
| `knip` | TS/JS | 未使用 export, dead code |
| `vulture` | Python | dead code |
| `ruff check` | Python | lint, complexity |
| `Semgrep` | 全言語 | OWASP/CWE rule pack |

**実行ルール**:
- ツールが利用可能な場合のみ実行（`command -v ast-grep` で確認）
- 結果は Step 2 の Gemini プロンプトに「**suspect_patterns**」として注入
- LLM は構造検索の hit を**そのまま finding にしない**（triage して妥当性検証）

**Gemini 起動**:

Agent ツールで `gemini-explore` エージェントを起動する:

```
You are a senior code auditor performing a comprehensive codebase review.

Analyze the entire codebase and identify issues in these categories:
1. **Security**: Auth bypass, XSS, CORS, rate limiting, secrets exposure, injection, file upload
2. **Architecture**: Missing scoping, unbounded queries, no transactions, hard deletes, missing indexes
3. **Frontend**: Route guards, XSS via template injection, memory leaks, race conditions, loading states
4. **Data Model & Business Logic**: Duplicate records, missing state machines, unclear ownership
5. **Testing & DevOps**: Test coverage gaps, CI/CD issues, risky DB operations
6. **Code Quality & DRY**: Duplicated logic, repetitive error handling, inefficient algorithms
7. **Performance**: Missing caching, N+1 queries, unnecessary full loads, sequential queries
8. **Miscellaneous**: Mixed languages, dev deps in prod, bundle bloat

For EACH issue found:
- Exact file path and line number (file:line format)
- Category and priority (P0=critical security/data loss, P1=important quality/performance, P2=improvement)
- Clear description of the problem
- Brief suggestion for fix

Output as structured JSON array:
[{"file": "src/auth.ts", "line": 42, "category": "Security", "priority": "P0", "title": "...", "description": "...", "suggestion": "..."}]
```

**小規模プロジェクト（ファイル50未満）の場合**: Gemini を使わず、直接 Glob + Read + Grep で分析する。
並列エージェント（Step 3）のみで十分な深さが得られる。

**Gate**: Gemini の結果が空または `gemini` コマンドが利用不可の場合、Step 3 の並列エージェントのみで進む。

## Step 3 — Category Deep-Dive（カテゴリ別深掘り）

Step 2 の結果を基に、カテゴリ別の専門エージェントを **1メッセージで並列起動** する。
プロジェクトに該当するカテゴリのみ起動する（全カテゴリ必須ではない）。

| カテゴリ | エージェント | フォーカス |
|----------|-------------|-----------|
| Security | `security-reviewer` | OWASP Top 10、認証・認可、秘密情報 |
| Architecture | `backend-architect` | DB設計、API境界、スケーラビリティ |
| Frontend | `frontend-developer` | コンポーネント設計、状態管理、a11y |
| Code Quality | `code-reviewer` | DRY違反、命名、エラーハンドリング |
| Performance | `code-reviewer` | N+1、キャッシュ、バンドルサイズ |
| Testing | `test-engineer` | カバレッジ、テスト戦略、CI/CD |

各エージェントのプロンプトに含めるもの:
- Step 2 の該当カテゴリの findings
- 対象ファイルのパス一覧
- 「file:line 形式で具体的な指摘を出力せよ」という指示

## Step 3.5 — Documentation Drift Crosswalk（オプション）

> `/check-health` は documentation drift 専門スキル。`/audit` は重複実装せず**結果を引用**する。

`/check-health` が直近で実行されている場合、その結果を **Documentation** カテゴリ findings として `/audit` の統合対象に含める。実行されていない場合、`/audit` の Step 5 末尾で「documentation drift は `/check-health` で別途確認推奨」と明記する。

## Step 4 — Synthesis & Prioritization（統合・優先度付け）

全エージェントの結果を統合し、重複排除・矛盾検出・優先度付けを行う。

### Severity × Effort の 2 軸

> **Tech-Debt-Skill knowledge**: severity だけでは Quick Wins が抽出できない。effort（修正コスト）と組み合わせる。

| 軸 | 値 | 基準 |
|----|------|------|
| **Severity** | P0 | セキュリティ脆弱性、データ損失リスク、本番障害（Auth bypass, SQL injection） |
| | P1 | 品質・パフォーマンス・保守性の重要問題（N+1, missing error handling） |
| | P2 | 改善推奨、ベストプラクティス逸脱（命名、型不足） |
| **Effort** | S | 1ファイル / 数十行 / 30分以内 |
| | M | 2-5ファイル / 数百行 / 数時間 |
| | L | 6ファイル超 / 大規模 / 数日 |

**Quick Wins** = High severity (P0/P1) × Low effort (S) — Top 5 priorities とは別に抽出する。

### 重複排除ルール

- 同一ファイル ±5行以内 + 同一カテゴリの指摘は1件に統合
- 複数エージェントが同じ問題を指摘した場合、優先度を1段階引き上げ

### Conflict Detection（矛盾検出）

複数エージェント間で **judgement が分かれた finding** は merge せず両論併記する。

- 同一 file:line で「A=問題」「B=ok / 意図的」と判定が割れる場合
- 同一パターンに対して優先度が 2 段以上ずれる場合（P0 vs P2）

これらは `## Conflicts` セクションに **両方の主張 + 各々の根拠** を併記し、ユーザーの判断に委ねる。

### Hallucination Defense（虚偽 line 検出）

LLM 監査は file:line を捏造することがある。以下を検証する:

- 同一 finding を 2エージェントが**異なる line** で指摘している場合 → 必ず Read で正確な行を確認
- 該当ファイルが存在しない / 行範囲外 → finding を破棄
- file:line specificity 閾値: 「`src/auth/` ディレクトリ全体」「`config.ts` 全体」のような**範囲指摘は禁止**。最低 1 関数 / 1 ブロック / ±10 行レンジまで絞る

## Step 4.5 — Tool Usage Audit（ツール使用頻度監査）

> Vercel は v0 のツールを 80% 削除して性能向上を達成。ツールは多いほど良いわけではない。

コードベース監査と併せて、エージェントのツール使用効率も監査する（該当する場合のみ）。

**対象**: `.config/claude/settings.json` の allowedTools、`agents/*.md`、`skills/*/SKILL.md` の allowed-tools

**チェック項目**:
1. **未使用ツール検出**: 直近30セッションのトランスクリプトで一度も呼ばれていないツール/MCP
2. **低使用エージェント検出**: 定義はあるが直近30日で起動実績のないエージェント
3. **重複スコープ検出**: 類似の description を持つ複数エージェント/スキルの特定

**データソース**:
- `~/.claude/projects/*/` 配下のセッションログ（存在する場合）
- `git log --all --grep="Agent(" --since="30 days ago"` でエージェント起動履歴を推定
- OTel セッションデータ（`tools/otel-session-analyzer/` が利用可能な場合）

**出力**: QUESTIONS.md の末尾に `## Tool & Agent Hygiene` セクションとして追加。

## Step 5 — Generate QUESTIONS.md

以下のテンプレートで `QUESTIONS.md` を生成する。出力先はプロジェクトルート。

```markdown
# Codebase Audit — QUESTIONS.md

> Generated: {date}
> Project: {project_name}
> Files scanned: {count}
> Total findings: {count} (P0: {n}, P1: {n}, P2: {n})

## Orient Summary

- **Boundaries**: {2-4行}
- **Main Flows**: {2-4行}
- **Invariants**: {2-4行}
- **Runtime Surface**: {2-4行}
- **Blind Spots**: {Orient で要約できなかった要素、なければ "なし"}

## Findings Summary

| Category | P0 | P1 | P2 | Quick Wins |
|----------|-----|-----|-----|-----------|
| Security | {n} | {n} | {n} | {n} |
| Architecture | {n} | {n} | {n} | {n} |
| ... | ... | ... | ... | ... |

## Top 5 Priorities

優先度順に最重要 5 件を抽出（severity と影響範囲で判断）。

1. [P0] {title} — `file:line` (effort: S/M/L)
2. ...

## Quick Wins

High severity (P0/P1) × Low effort (S) のみ。修正コストが低く効果が高いもの。

| # | Severity | Effort | Title | file:line |
|---|----------|--------|-------|-----------|
| 1 | P0 | S | ... | ... |

---

## Security

### Q1. [P0] [effort: S] Auth bypass via missing middleware — `src/auth/middleware.ts:42-58`

**Issue**: The `/api/admin` routes lack authentication middleware, allowing unauthenticated access.

**Suggestion**: Add `authMiddleware()` to the admin router before route handlers.

**Answer**:

---

### Q2. [P1] [effort: M] No rate limiting on login endpoint — `src/auth/login.ts:15-34`

...

## Architecture

### Q{n}. [P1] [effort: L] ...

...

---

## Conflicts (Inter-Agent Disagreements)

複数エージェントで判定が割れた findings。両論併記。

### C1. `src/api/handler.ts:120` — error handling

- **A (code-reviewer)**: P1, "swallowed exception, no retry"
- **B (backend-architect)**: ok, "意図的な fail-fast。upstream で再試行"
- **判断材料**: 上位呼び出し元の retry policy を確認 (`src/scheduler.ts:50`)

**Answer**:

---

## Non-Findings (Looks bad but is fine)

> **Tech-Debt-Skill (ksimback) の knowledge**: 監査者が**検討して却下**した指摘を可視化する。再実行時の同じ疑似 Gap 再発掘を防ぐ。

意図的な設計判断や、表面的に問題に見えるが正当な理由があるパターンを記録する。

| # | パターン | file:line | 検討した理由 | 却下理由 |
|---|----------|-----------|------------|---------|
| N1 | `unwrap()` 多用 | `src/cli.rs:30-50` | エラー時 panic は CLI として正常 | initialization phase のみ。runtime path は `?` に統一済み |
| N2 | God object 風の `Context` struct | `src/context.go:10-200` | DI コンテナとして意図的 | refactor 提案あったが Go の慣用句として許容 |
```

**テンプレートルール**:
- 各質問に通し番号 (Q1, Q2, ...)
- 優先度ラベル `[P0]`, `[P1]`, `[P2]`
- effort ラベル `[effort: S/M/L]`
- file:line 参照（**最低 1 関数 / 1 ブロック / ±10 行レンジ**まで絞ること）
- Issue（何が問題か）と Suggestion（修正案）を分離
- 空の `**Answer**:` フィールド
- カテゴリ間は `---` で区切る
- **Output Contract（曖昧表現禁止）**: "consider refactoring", "might be improved", "could potentially" のような根拠なし中和表現を使わない。問題と判断したなら理由 + 修正案を、却下したなら Non-Findings に書く

### Repeat-Run Tracking（軽量版）

再実行時、前回の `QUESTIONS-{date}.md` または最新の `QUESTIONS.md` を `git log` から特定し、以下を比較して新 QUESTIONS.md の冒頭に記録する:

| タグ | 意味 |
|------|------|
| **NEW** | 今回新規 |
| **RESOLVED** | 前回あったが今回見つからない（修正済 or 該当ファイル削除） |
| **PERSISTING** | 前回も今回もある（経過日数を併記） |

**実装**: 専用 state ファイルは作らない。`git log -- QUESTIONS*.md` で履歴取得 → 直近版と diff で十分。

## Step 6 — Answer Loop（回答ループ）

QUESTIONS.md をユーザーに提示し、回答を待つ。

ユーザーが回答を記入して戻ってきたら:

1. **回答を読み取る**: QUESTIONS.md の Answer フィールドを解析
2. **アクション分類**:
   - 「バグ / 修正する」→ 修正タスクとしてまとめる
   - 「意図的な仕様」→ 除外（必要なら ADR として記録を提案）
   - 「後で対応」→ backlog に記録を提案
   - 「わからない / 要調査」→ `/spike` を提案
3. **ワークフロー接続**:
   - P0 修正が3件以上 → `/epd` で体系的に対応することを提案
   - P1 修正が個別に完結 → 個別に実装
   - 大規模リファクタリングが必要 → `/spec` で仕様を固めることを提案

## Anti-Patterns

- `/review` で対応できる差分レビューにこのスキルを使う
- Gemini の結果をそのまま QUESTIONS.md に流す（必ず統合・重複排除する）
- 全カテゴリのエージェントを無条件に起動する（該当するものだけ）
- Answer なしでいきなり修正を始める（ユーザーの判断を待つ）
- P2 の問題を P0 に格上げして恐怖を煽る

## Gotchas

- **大規模モノレポ**: ファイル数が1000を超える場合、Step 1 でスコープを絞る（特定サブディレクトリに限定）
- **Gemini 未インストール**: `gemini --version` が失敗したら Step 3 の並列エージェントのみで進む
- **QUESTIONS.md の肥大化**: 100問を超える場合、P0/P1 のみ出力し、P2 は別ファイル `QUESTIONS-P2.md` に分離
- **既存 QUESTIONS.md の上書き**: 既存ファイルがある場合は `QUESTIONS-{date}.md` で出力
