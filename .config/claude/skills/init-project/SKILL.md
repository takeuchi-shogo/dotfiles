---
name: init-project
description: >
  プロジェクトに最適な Claude Code 構造を初期化・適応するオーケストレータ。プロジェクト分析 → 規模判定(S/M/L) →
  ファクトリエージェント委譲で CLAUDE.md, .claudeignore, references/, rules/, docs/, Local CLAUDE.md を段階的に生成。
  新プロジェクト初期化、既存プロジェクトへの Claude Code 導入、S→M→L の段階的アップグレードに使用。
  Use when: 'init project', 'setup claude', 'プロジェクト初期化', 'Claude Code 導入',
  'CLAUDE.md 作りたい', 'プロジェクト構造', 'scaffold', 'プロジェクトセットアップ'.
  Do NOT use for: 既存 CLAUDE.md の修正のみ（claude-md-management を使用）、
  背景エージェントのみ（setup-background-agents を使用）。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# Init Project

プロジェクトを分析し、最適な Claude Code 構造を段階的に構築するオーケストレータ。

## コンセプト

Pandey "Anatomy of a Claude Code Project" の5層構造を基盤に、既存ファクトリエージェントに委譲する。

**5層構造:**
1. **CLAUDE.md** — WHY / WHAT / HOW（短く）
2. **skills/** — 再利用可能なワークフロー
3. **hooks/** — 決定論的ガードレール
4. **docs/** — Progressive Context（architecture, ADRs, runbooks）
5. **Local CLAUDE.md** — リスキーモジュール近くの注意書き

## 引数

- 引数なし → フル初期化（自動検出）
- `--upgrade` → 既存構造の段階的アップグレード（Gap Analysis）
- `--level S|M|L` → レベル明示指定（自動検出をスキップ）
- `--dry-run` → 生成ファイルリストのみ表示

---

## Phase 1: Detect（プロジェクト分析）

プロジェクトの特性を分析し、推奨レベルを決定する。
詳細な検出ルールは `references/detection-rules.md` を参照。

### 1.1 基本情報収集

```bash
# ファイル数
find . -type f -not -path './.git/*' -not -path './node_modules/*' -not -path './vendor/*' -not -path './.venv/*' | wc -l

# 言語検出
ls -1 package.json pyproject.toml go.mod Cargo.toml Gemfile mix.exs 2>/dev/null

# CI 検出
ls .github/workflows/*.yml .gitlab-ci.yml 2>/dev/null

# Contributors
git shortlog -sn --no-merges 2>/dev/null | wc -l

# テスト検出
ls jest.config* vitest.config* pytest.ini conftest.py playwright.config* 2>/dev/null
find . -name '*_test.go' -o -name '*.test.ts' -o -name '*.spec.ts' | head -3

# docs 検出
ls -d docs/ 2>/dev/null

# 既存 Claude Code 構造
ls CLAUDE.md .claude/ .claudeignore 2>/dev/null
```

### 1.2 リスキーモジュール検出

以下のパターンにマッチするディレクトリを探す:

```bash
find . -maxdepth 3 -type d \( \
  -name 'auth' -o -name 'authentication' -o -name 'authorization' \
  -o -name 'billing' -o -name 'payment' -o -name 'stripe' \
  -o -name 'migration' -o -name 'migrations' \
  -o -name 'infra' -o -name 'infrastructure' -o -name 'terraform' -o -name 'pulumi' \
  -o -name 'security' -o -name 'crypto' \
  -o -name 'persistence' -o -name 'database' -o -name 'db' \
\) -not -path './.git/*' -not -path './node_modules/*' -not -path './vendor/*'
```

### 1.3 規模判定

`references/detection-rules.md` のスコアリングテーブルに基づいて S/M/L を決定。

### 1.4 ユーザーへの提示

検出結果を以下のフォーマットで提示し、確認を求める:

```
🔍 プロジェクト分析結果:
  - 言語: {languages}
  - フレームワーク: {frameworks}
  - CI: {ci_system or "なし"}
  - テスト: {test_frameworks or "なし"}
  - Contributors: {count}
  - リスキーモジュール: {modules or "なし"}

📊 推奨レベル: {S|M|L}
   理由: {reason}

(1) {recommended} で進める
(2) レベルを変更する
(3) --dry-run で生成物を確認する
```

`--level` が指定されていた場合は自動検出をスキップし、指定レベルで進める。

---

## Phase 2: Generate（ファクトリ委譲）

レベルに応じてファクトリエージェントに委譲する。
委譲プロンプト・並列実行マップ・直接生成テンプレートは `references/level-templates.md` を参照。

### 委譲先の概要

| レベル | 委譲先 | 実行方式 |
|---|---|---|
| **S** | constitution-factory（CLAUDE.md + .claudeignore） | 直列 |
| **M** | constitution-factory + context-factory（architecture.md） | 並列 → rules 直接生成（直列） |
| **L** | M + context-factory（Local CLAUDE.md, ADR） + setup-background-agents | 並列 → rules + hooks 直接生成（直列） |

### 委譲パターン

- **constitution-factory**: `subagent_type: constitution-factory` で Agent tool を使用
- **context-factory**: `subagent_type: context-factory` で Agent tool を使用
- **setup-background-agents**: Skill tool で `/setup-background-agents` を呼び出し（L レベル、CI 有りの場合のみ）
- **直接生成**: Agent tool を介さず、オーケストレータ自身が Write ツールで生成する。コンテキストが既にメモリ内にあり、サブエージェント起動のオーバーヘッドが不釣り合いな場合に選択

### hooks 設定（L のみ）

`.claude/settings.json` に基本的な hooks 設定を追加:
- PostToolUse (Edit|Write): auto-format（検出した言語に応じたフォーマッタ）
- 最小限の hooks のみ。過剰な自動化はしない

---

## Phase 3: Verify（整合性チェック）

生成完了後、以下を検証する:

1. **CLAUDE.md 行数**: レベルに応じた制約を確認（S: 50行以内 / M・L: 80行以内）
2. **.claudeignore**: 技術スタックに適合していることを確認
3. **参照整合性**: CLAUDE.md 内のファイル参照が実在することを確認
4. **Local CLAUDE.md**: リスキーモジュールの実際の内容を反映していることを確認

```bash
# 行数チェック
wc -l CLAUDE.md

# 参照整合性
grep -oE '`[^`]+\.(md|json|yml|yaml)`' CLAUDE.md | tr -d '`' | while read f; do
  [ ! -f "$f" ] && echo "BROKEN: $f"
done
```

### 結果提示

```
✅ プロジェクト初期化完了

生成ファイル:
  - CLAUDE.md ({lines} 行)
  - .claudeignore
  {M/L の場合: 追加ファイルリスト}

次のステップ:
  1. CLAUDE.md を確認し、プロジェクト固有のルールを追加
  2. {M/L の場合: references/ の内容を確認・調整}
  3. {L の場合: hooks の設定を確認}
```

---

## 既存プロジェクト適応（--upgrade）

既に Claude Code 構造がある場合の Gap Analysis フロー。
詳細は `references/gap-analysis.md` を参照。

### フロー

1. **現在のレベル判定**: 既存構造を分析し、S/M/L のどこに該当するか判定
2. **ギャップ分析**: Pandey 5層のどこが欠けているかチェック
3. **アップグレード提案**: 不足層のみリストアップ（既存を上書きしない）
4. **確認と実行**: ユーザーに提案を提示し、承認後に不足分のみ生成

### 現在レベルの判定

詳細は `references/gap-analysis.md` の「現在レベル判定」テーブルを参照。

### 上書き防止

- 既存の CLAUDE.md は**絶対に上書きしない**
- 既存ファイルがある場合は「追記提案」として差分を提示
- ユーザーが明示的に承認した場合のみマージ

---

## Anti-Patterns

- プロジェクト分析をスキップして直接テンプレートを適用する
- S レベルのプロジェクトに hooks や agents を強制する
- 既存の CLAUDE.md を確認せず上書きする
- ファクトリの出力を検証せずにそのまま書き込む
- references/ に CLAUDE.md と重複する内容を書く
