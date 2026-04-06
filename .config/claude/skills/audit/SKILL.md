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
  AI ワークフロー監査 (use /ai-workflow-audit)。
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

## Step 1 — Reconnaissance（偵察）

プロジェクトの全体像を把握する。ここで得た情報が以降のステップの品質を決める。

```bash
# プロジェクト構造
find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' | head -200

# 技術スタック検出
ls -la package.json Cargo.toml go.mod pyproject.toml Gemfile composer.json *.csproj Taskfile.yml Makefile 2>/dev/null

# git 統計
git log --oneline -20
git shortlog -sn --no-merges | head -10
```

以下を特定する:
- **言語・フレームワーク**: 主要技術スタック
- **規模**: ファイル数、コード行数の概算
- **構造**: モノレポ/単一アプリ、ディレクトリ構造のパターン
- **活発度**: 最終コミット日、コントリビューター数

**Gate**: 技術スタックが特定できない場合、ユーザーに確認してから進む。

## Step 2 — Deep Scan（深層スキャン）

Gemini(1M コンテキスト) を使ってコードベース全体を一括分析する。
Claude の 200K では収まらない大規模コードベースでも対応可能。

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

## Step 4 — Synthesis & Prioritization（統合・優先度付け）

全エージェントの結果を統合し、重複排除・優先度付けを行う。

### 優先度基準

| 優先度 | 基準 | 例 |
|--------|------|-----|
| **P0** | セキュリティ脆弱性、データ損失リスク、本番障害 | Auth bypass, SQL injection, no backup |
| **P1** | 品質・パフォーマンス・保守性の重要な問題 | N+1 queries, no error handling, DRY violation |
| **P2** | 改善推奨、ベストプラクティス逸脱 | Naming conventions, missing types, bundle size |

### 重複排除ルール

- 同一ファイル ±5行以内 + 同一カテゴリの指摘は1件に統合
- 複数エージェントが同じ問題を指摘した場合、優先度を1段階引き上げ

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

## Summary

| Category | Count | Key Issues |
|----------|-------|-----------|
| Security | {n} | {highlights} |
| Architecture | {n} | {highlights} |
| ... | ... | ... |

---

## Security

### Q1. [P0] Auth bypass via missing middleware — `src/auth/middleware.ts:42`

**Issue**: The `/api/admin` routes lack authentication middleware, allowing unauthenticated access.

**Suggestion**: Add `authMiddleware()` to the admin router before route handlers.

**Answer**:

---

### Q2. [P1] No rate limiting on login endpoint — `src/auth/login.ts:15`

...

## Architecture

### Q{n}. [P1] ...

...
```

**テンプレートルール**:
- 各質問に通し番号 (Q1, Q2, ...)
- 優先度ラベル `[P0]`, `[P1]`, `[P2]`
- file:line 参照
- Issue（何が問題か）と Suggestion（修正案）を分離
- 空の `**Answer**:` フィールド
- カテゴリ間は `---` で区切る

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
