---
status: active
last_reviewed: 2026-04-23
---

# Harness Engineering 記事ベース改善 実装計画

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 逆瀬川 Harness Engineering Best Practices 2026 記事の知見を dotfiles ハーネスに統合する（ADR, Lefthook, WHY/FIX lint, AI アンチパターン検出, references 強化）

**Architecture:** 5 つの独立した改善を順次実装。各タスクは既存ハーネスの拡張であり、新規の外部依存は Lefthook のみ。

**Tech Stack:** Lefthook (Go), Node.js (auto-format.js), Python (golden-check.py), Markdown (ADR/references)

---

## Chunk 1: ADR システム + Lefthook

### Task 1: ADR テンプレートと初期 ADR の作成

**Files:**
- Create: `docs/adr/README.md`
- Create: `docs/adr/template.md`
- Create: `docs/adr/0001-hook-four-layer-separation.md`
- Create: `docs/adr/0002-progressive-disclosure-design.md`
- Create: `docs/adr/0003-multi-model-orchestration.md`
- Create: `docs/adr/0004-linter-config-protection.md`
- Create: `docs/adr/0005-autoevolve-four-layer-loop.md`

- [ ] **Step 1: ADR ディレクトリと README 作成**

```bash
mkdir -p docs/adr
```

`docs/adr/README.md`:
```markdown
# Architecture Decision Records

本ディレクトリには ADR（Architecture Decision Records）を格納する。
Nygard 形式に従い、各 ADR は不変。状態変更は新しい ADR で Supersede する。

## ステータス

- **Accepted**: 現在有効な決定
- **Superseded by ADR-XXXX**: 新しい ADR に置き換え済み
- **Deprecated**: 非推奨（代替なし）

## 一覧

| ADR | タイトル | Status |
|-----|---------|--------|
| 0001 | Hook 4 層分離 | Accepted |
| 0002 | Progressive Disclosure 設計 | Accepted |
| 0003 | マルチモデルオーケストレーション | Accepted |
| 0004 | リンター設定保護 | Accepted |
| 0005 | AutoEvolve 4 層ループ | Accepted |
```

- [ ] **Step 2: ADR テンプレート作成**

`docs/adr/template.md`:
```markdown
# ADR-XXXX: [タイトル]

## Status

Accepted | Superseded by ADR-XXXX | Deprecated

## Context

[なぜこの決定が必要だったか]

## Decision

[何を決定したか]

## Consequences

### Positive
- [利点]

### Negative
- [トレードオフ]

### Neutral
- [その他の影響]
```

- [ ] **Step 3: ADR-0001 Hook 4 層分離**

`docs/adr/0001-hook-four-layer-separation.md`:
```markdown
# ADR-0001: Hook 4 層分離

## Status

Accepted

## Context

Claude Code の hook スクリプトが増加し、責務の混在が問題になった。
フォーマッター、ポリシーチェック、ライフサイクル管理、学習収集が
単一ディレクトリに混在すると、変更影響の把握が困難になる。

## Decision

hook スクリプトを 4 層に分離する:
- `scripts/runtime/` — セッションライフサイクル、フォーマッター（PostToolUse 高速パス）
- `scripts/policy/` — 品質ゲート、エラー検出、委譲判断（ブロッキング可）
- `scripts/lifecycle/` — プラン管理、メモリアーカイブ（非ブロッキング）
- `scripts/learner/` — イベント収集、学習永続化（Stop/SessionEnd）
- `scripts/lib/` — 共有ユーティリティ

## Consequences

### Positive
- 変更影響が層内に閉じる（runtime の変更が learner に影響しない）
- 新規 hook 追加時の配置が明確
- テストが層単位で独立実行可能

### Negative
- lib/ の共有モジュールが間接依存を生む
- ディレクトリ構造の学習コスト

### Neutral
- settings.json の hook 定義で各スクリプトのパスを明示する必要がある
```

- [ ] **Step 4: ADR-0002 Progressive Disclosure 設計**

`docs/adr/0002-progressive-disclosure-design.md`:
```markdown
# ADR-0002: Progressive Disclosure 設計

## Status

Accepted

## Context

CLAUDE.md に全ルール・ワークフロー・リファレンスを記載すると、
毎ターンのコンテキスト消費が増大し、指示追従精度が低下する。
IFScale 研究により、指示数増加に伴う性能劣化が確認されている
（フロンティアモデルで 150+ 指示から線形劣化）。

## Decision

3 層の Progressive Disclosure を採用する:
1. **CLAUDE.md** — コア原則とポインタのみ。毎ターン読み込まれる
2. **references/** — 詳細ワークフロー、チェックリスト、ガイド。必要時のみ参照
3. **rules/** — 言語別・ドメイン別ルール。ファイルパターンに応じて自動ロード

## Consequences

### Positive
- 毎ターンのコンテキスト消費を最小化
- 必要な情報のみを必要な時にロード
- 信号対雑音比の向上

### Negative
- ポインタが壊れると情報が届かない（失敗が観測可能なのは利点でもある）
- 新規ルール追加時にどの層に置くかの判断が必要
```

- [ ] **Step 5: ADR-0003 マルチモデルオーケストレーション**

`docs/adr/0003-multi-model-orchestration.md`:
```markdown
# ADR-0003: マルチモデルオーケストレーション

## Status

Accepted

## Context

単一モデルでは、大規模コンテキスト分析（>200K）、深い推論、
高速フォーマットなど全要件を最適にカバーできない。

## Decision

3 層のマルチモデル構成を採用する:
- **Claude Code (Opus)** — オーケストレーター、計画、レビュー統合
- **Codex CLI (gpt-5.4)** — 設計・推論・デバッグ、reasoning effort 制御
- **Gemini CLI (2.5 Pro)** — 1M コンテキスト分析、リサーチ、マルチモーダル

委譲は hook（agent-router.py, error-to-codex.py, suggest-gemini.py）で自動提案し、
ルール（rules/codex-delegation.md, rules/gemini-delegation.md）で判断基準を定義する。

## Consequences

### Positive
- 各モデルの得意領域を活用
- 大規模コードベース分析が可能（Gemini 1M）
- 深い推論が必要な場合に Codex xhigh を利用

### Negative
- 3 ツールの管理・更新コスト
- CLI ツール間の出力形式の差異
- ネットワーク依存が増加
```

- [ ] **Step 6: ADR-0004 リンター設定保護**

`docs/adr/0004-linter-config-protection.md`:
```markdown
# ADR-0004: リンター設定保護

## Status

Accepted

## Context

AI エージェントは lint エラーを解消するために、コードではなく
リンター設定を変更する傾向がある（ルールの無効化、閾値の緩和）。
これにより品質ゲートが形骸化する。

Ref: Harness Engineering Best Practices 2026 — アンチパターン #2

## Decision

PreToolUse hook（protect-linter-config.py）でリンター設定ファイルの
編集をブロックする。対象:
- 純粋設定: .eslintrc*, biome.json, .prettierrc*, .oxlintrc.json, .golangci.yml 等
- 混合ファイル: pyproject.toml の [tool.ruff] セクション、Cargo.toml の [lints] セクション

原則: **Fix code, not rules.**

## Consequences

### Positive
- リンター設定の一貫性を保証
- 品質ゲートの形骸化を防止
- エラーは常にコード側で解決される

### Negative
- 正当な設定変更も一旦ブロックされる（人間が手動で変更する必要あり）
- 混合ファイルのセクション検出は完全ではない
```

- [ ] **Step 7: ADR-0005 AutoEvolve 4 層ループ**

`docs/adr/0005-autoevolve-four-layer-loop.md`:
```markdown
# ADR-0005: AutoEvolve 4 層ループ

## Status

Accepted

## Context

セッション中のエラー・修正パターン・品質イベントを収集しても、
それを設定改善に繋げる仕組みがなければデータが腐敗する。
karpathy/autoresearch に着想を得て、自律的改善ループを設計した。

## Decision

4 層の改善ループを実装する:
1. **セッション層** (SessionEnd hook) — イベント収集・永続化
2. **日次層** (daily-report) — セッション横断のパターン分析
3. **バックグラウンド層** (cron) — 定期的な改善提案生成
4. **オンデマンド層** (/improve) — 人間起点の改善サイクル

安全機構: master 直接変更禁止、1 サイクル最大 3 ファイル、テスト通過必須、人間レビュー必須。

## Consequences

### Positive
- 設定が使用パターンに応じて自動改善
- エラーパターンの蓄積による fix guide の自動拡充
- ハーネスへの投資が複利で効く

### Negative
- 誤った改善提案が生成されるリスク（人間レビューで軽減）
- JSONL ストレージの肥大化（ローテーションで軽減）
```

- [ ] **Step 8: コミット**

```bash
git add docs/adr/
git commit -m "📝 docs: introduce ADR system with 5 initial architecture decisions"
```

---

### Task 2: Lefthook 導入

**Files:**
- Create: `lefthook.yml`
- Modify: `.config/claude/CLAUDE.md` — harness_guarantees に Lefthook 追記

- [ ] **Step 1: Lefthook インストール確認**

```bash
which lefthook || brew install lefthook
```

- [ ] **Step 2: lefthook.yml 作成**

`lefthook.yml`:
```yaml
# https://github.com/evilmartians/lefthook
# Pre-commit hooks for polyglot dotfiles repository
# Claude Code hooks (PostToolUse) handle per-edit linting;
# Lefthook handles per-commit batch validation.

pre-commit:
  parallel: true
  commands:
    biome-format:
      glob: "*.{ts,tsx,js,jsx,json,css}"
      run: biome format --write {staged_files} && git add {staged_files}
    oxlint:
      glob: "*.{ts,tsx,js,jsx}"
      run: oxlint {staged_files}
    ruff-format:
      glob: "*.py"
      run: ruff format {staged_files} && git add {staged_files}
    ruff-check:
      glob: "*.py"
      run: ruff check --fix {staged_files} && git add {staged_files}
    gofmt:
      glob: "*.go"
      run: gofmt -w {staged_files} && git add {staged_files}

commit-msg:
  commands:
    conventional-commit:
      run: |
        MSG=$(head -1 {1})
        if ! echo "$MSG" | grep -qE '^(✨|🐛|📝|♻️|🔧|🚀|⬆️|🔒|✅|🏗️|🗑️|🎨|⚡) (feat|fix|docs|refactor|chore|ci|perf|security|test|build|revert|style|perf)(\(.+\))?: .+'; then
          echo "❌ Commit message must follow: <emoji> <type>(<scope>): <description>"
          echo "   Example: ✨ feat: add new feature"
          exit 1
        fi
```

- [ ] **Step 3: Lefthook を Git hooks にインストール**

```bash
cd /Users/takeuchishougo/dotfiles && lefthook install
```

- [ ] **Step 4: 動作確認**

```bash
# テスト用ファイルで pre-commit が発火するか確認
echo "const x: any = 1;" > /tmp/test-lefthook.ts
# lefthook run pre-commit で dry-run
lefthook run pre-commit --dry-run
```

- [ ] **Step 5: コミット**

```bash
git add lefthook.yml
git commit -m "🔧 chore: introduce Lefthook for pre-commit quality gates"
```

---

## Chunk 2: Lint WHY/FIX 形式 + AI アンチパターン検出

### Task 3: auto-format.js に WHY/FIX コンテキスト注入

**Files:**
- Create: `.config/claude/references/lint-rule-guides.md`
- Modify: `.config/claude/scripts/runtime/auto-format.js:160-180`

- [ ] **Step 1: lint-rule-guides.md 作成**

高頻度の lint ルールに対する WHY/FIX マッピングを作成する。

`.config/claude/references/lint-rule-guides.md`:
```markdown
# Lint Rule Guides

auto-format.js が lint エラー検出時に WHY/FIX コンテキストを注入するための
ルール別ガイド。OpenAI の "Error Messages as Fix Instructions" パターンに基づく。

Ref: Harness Engineering Best Practices 2026

---

## TypeScript/JavaScript (Oxlint)

### no-explicit-any
- **WHY**: 型安全性の喪失 → GP-005 違反。コンパイル時の型チェックが無効化される
- **FIX**: `unknown` + type guard、ジェネリクス `<T>`、または具体型を使用

### no-unused-vars
- **WHY**: デッドコードは可読性を下げ、バンドルサイズを増加させる
- **FIX**: 使用していない変数・import を削除。意図的なら `_` プレフィックス

### no-console
- **WHY**: プロダクションコードに console.log を残すと情報漏洩リスク
- **FIX**: logger ライブラリを使用、またはデバッグ完了後に削除

### eqeqeq
- **WHY**: `==` は暗黙の型変換で予期しない真偽値を返す
- **FIX**: `===` (厳密等価) を使用

### no-var
- **WHY**: `var` はスコープが関数単位で意図しないホイスティングを起こす
- **FIX**: `const` (再代入なし) または `let` (再代入あり) に変更

## Python (Ruff)

### E501
- **WHY**: 長すぎる行は可読性を著しく下げる
- **FIX**: 変数抽出、改行、文字列の分割

### F401
- **WHY**: 未使用の import はモジュールロード時間とメモリを浪費する
- **FIX**: import 行を削除

### F841
- **WHY**: 未使用変数はデッドコードの兆候
- **FIX**: 変数を使用するか、`_` プレフィックスで明示的に破棄

### E711
- **WHY**: `== None` より `is None` が Python のイディオム（オブジェクト同一性テスト）
- **FIX**: `is None` / `is not None` を使用

### S101 (assert)
- **WHY**: プロダクションコードの assert は -O フラグで無効化される
- **FIX**: `if not condition: raise ValueError(...)` に変更

## Go (golangci-lint)

### errcheck
- **WHY**: Go のエラーは戻り値。無視すると silent failure — GP-004 違反
- **FIX**: `if err != nil { return fmt.Errorf("...: %w", err) }`

### govet
- **WHY**: コンパイラが検出しない論理的問題（printf フォーマット不一致等）
- **FIX**: govet の指摘に従い、フォーマット文字列と引数を一致させる

### staticcheck (SA)
- **WHY**: 静的解析による潜在バグ検出。誤検出率が非常に低い
- **FIX**: 各 SA コードに対応する修正を適用

### gosec (G)
- **WHY**: セキュリティ脆弱性の自動検出
- **FIX**: 指摘に従いセキュアな代替手段を使用（ADR-0004 参照）
```

- [ ] **Step 2: auto-format.js に WHY/FIX 注入ロジック追加**

`auto-format.js` の `process.stdin.on("end", ...)` 内の ctx 生成部分を修正。
lint-rule-guides.md をビルド時ではなく実行時に参照しない（パフォーマンスのため）。
代わりに、よく出るルール ID をインラインマップとして保持する。

変更箇所: `.config/claude/scripts/runtime/auto-format.js` の 174-180 行付近

```javascript
// --- Lint rule WHY/FIX guides (inline for speed) ---
// Ref: references/lint-rule-guides.md (full version)
const LINT_GUIDES = {
	// TypeScript/JavaScript (Oxlint)
	"no-explicit-any": {
		why: "型安全性の喪失 → GP-005 違反",
		fix: "unknown + type guard、ジェネリクス <T>、または具体型を使用",
	},
	"no-unused-vars": {
		why: "デッドコードは可読性低下とバンドルサイズ増加",
		fix: "未使用の変数・import を削除。意図的なら _ プレフィックス",
	},
	"no-console": {
		why: "プロダクションコードの console.log は情報漏洩リスク",
		fix: "logger を使用、またはデバッグ完了後に削除",
	},
	eqeqeq: {
		why: "== は暗黙の型変換で予期しない真偽値を返す",
		fix: "=== (厳密等価) を使用",
	},
	// Python (Ruff)
	E501: { why: "長すぎる行は可読性を著しく下げる", fix: "変数抽出、改行、文字列の分割" },
	F401: {
		why: "未使用 import はロード時間とメモリを浪費",
		fix: "import 行を削除",
	},
	F841: { why: "未使用変数はデッドコードの兆候", fix: "変数を使用するか _ で破棄" },
	E711: {
		why: "== None より is None が Python イディオム",
		fix: "is None / is not None を使用",
	},
	// Go (golangci-lint)
	errcheck: {
		why: "エラー戻り値の無視は silent failure — GP-004 違反",
		fix: 'if err != nil { return fmt.Errorf("...: %w", err) }',
	},
	gosec: {
		why: "セキュリティ脆弱性の自動検出",
		fix: "指摘に従いセキュアな代替手段を使用",
	},
};

function enrichWithGuide(errorLine) {
	for (const [rule, guide] of Object.entries(LINT_GUIDES)) {
		if (errorLine.includes(rule)) {
			return `${errorLine}\n    WHY: ${guide.why}\n    FIX: ${guide.fix}`;
		}
	}
	return errorLine;
}
```

ctx 生成を修正:
```javascript
const ctx = [
	`[Auto-Lint] ${tool} が ${path.basename(filePath)} で問題を検出:`,
	"",
	...errors.map((e) => `  ${enrichWithGuide(e)}`),
	"",
	"上記の lint エラーを修正してください。リンター設定は変更せず、コードを修正すること。",
].join("\n");
```

- [ ] **Step 3: 動作確認**

```bash
# auto-format.js の構文チェック
node -c .config/claude/scripts/runtime/auto-format.js
```

- [ ] **Step 4: コミット**

```bash
git add .config/claude/references/lint-rule-guides.md .config/claude/scripts/runtime/auto-format.js
git commit -m "✨ feat: add WHY/FIX context injection to auto-format lint errors"
```

---

### Task 4: AI コード特有のアンチパターン検出

**Files:**
- Modify: `.config/claude/scripts/policy/golden-check.py`
- Modify: `.config/claude/references/golden-principles.md`

- [ ] **Step 1: golden-principles.md に GP-009, GP-010 追加**

`.config/claude/references/golden-principles.md` の末尾に追加:

```markdown
## GP-009: ゴーストファイル防止

- **原則**: 既存ファイルを修正せず、同名・類似名の新規ファイルを作成しない
- **検出パターン**: Write ツールでの新規ファイル作成時、同ディレクトリに類似ファイルが存在
- **キーワード**: 新規ファイル作成（Write ツール、`file_path` が既存ファイルと名前が似ている）
- **背景**: OX Security/Snyk 調査で AI 生成コードの主要アンチパターンとして報告

## GP-010: コメント過多防止

- **原則**: コメントはコードが「なぜ」そうなっているかを説明する。「何を」しているかはコード自体で表現する
- **検出パターン**: ファイル内のコメント行比率が 40% を超える場合に警告
- **キーワード**: `//`, `#`, `/* */`, `"""`（コメント行が多すぎる）
- **背景**: AI リポジトリの 90-100% で "Comments Everywhere" パターンが報告（OX Security）
```

- [ ] **Step 2: golden-check.py にゴーストファイル検出を追加**

`golden-check.py` の `check_unsafe_types` 関数の後に追加:

```python
import glob as globmod
from difflib import SequenceMatcher


def check_ghost_file(file_path: str, tool_name: str) -> str | None:
    """Detect creation of new files when similar files already exist (GP-009).

    Only triggers for Write tool (new file creation).
    """
    if tool_name != "Write":
        return None
    if os.path.exists(file_path):
        return None  # Overwrite of existing file, not ghost

    dir_path = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(basename)[0].lower()

    if not dir_path or not os.path.isdir(dir_path):
        return None

    try:
        existing = os.listdir(dir_path)
    except OSError:
        return None

    for existing_file in existing:
        existing_name = os.path.splitext(existing_file)[0].lower()
        ratio = SequenceMatcher(None, name_without_ext, existing_name).ratio()
        if ratio > 0.7 and existing_file != basename:
            return (
                f"[GP-009] 類似名のファイル `{existing_file}` が同ディレクトリに存在します。"
                "新規作成ではなく既存ファイルの修正を検討してください。"
            )
    return None
```

- [ ] **Step 3: golden-check.py にコメント比率検出を追加**

```python
def check_comment_ratio(content: str, file_path: str = "") -> str | None:
    """Detect excessive comment-to-code ratio (GP-010).

    Warns when comment lines exceed 40% of total non-empty lines.
    Skips files under 20 lines (too small to judge).
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".md", ".txt", ".json", ".yaml", ".yml", ".toml"):
        return None  # Non-code files

    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if len(lines) < 20:
        return None

    comment_markers = {
        ".py": ("#",),
        ".ts": ("//",),
        ".tsx": ("//",),
        ".js": ("//",),
        ".jsx": ("//",),
        ".go": ("//",),
        ".rs": ("//",),
        ".sh": ("#",),
        ".bash": ("#",),
    }
    markers = comment_markers.get(ext, ("//", "#"))
    comment_count = sum(1 for l in lines if any(l.startswith(m) for m in markers))
    ratio = comment_count / len(lines)

    if ratio > 0.4:
        pct = int(ratio * 100)
        return (
            f"[GP-010] コメント比率が {pct}% と高すぎます（閾値: 40%）。"
            "コードが自己文書化されるよう、冗長なコメントを削除してください。"
        )
    return None
```

- [ ] **Step 4: main() の checks リストに新規チェックを追加**

`golden-check.py` の `checks` リストを修正:

```python
    checks: list[tuple[str, str | None]] = [
        ("GP-002", check_boundary_validation(content, file_path)),
        ("GP-003", check_dependency_file(file_path)),
        ("GP-004", check_empty_catch(content)),
        ("GP-005", check_unsafe_types(content, file_path)),
        ("GP-009", check_ghost_file(file_path, tool_name)),
        ("GP-010", check_comment_ratio(content, file_path)),
    ]
```

- [ ] **Step 5: テスト実行**

```bash
cd /Users/takeuchishougo/dotfiles && python -m pytest .config/claude/scripts/tests/ -v -k "golden" 2>/dev/null || echo "No existing golden tests"
# 構文チェック
python -c "import ast; ast.parse(open('.config/claude/scripts/policy/golden-check.py').read()); print('OK')"
```

- [ ] **Step 6: コミット**

```bash
git add .config/claude/scripts/policy/golden-check.py .config/claude/references/golden-principles.md
git commit -m "✨ feat: add ghost file (GP-009) and comment ratio (GP-010) detection"
```

---

## Chunk 3: References 強化

### Task 5: harness-rationale.md 作成

**Files:**
- Create: `.config/claude/references/harness-rationale.md`
- Modify: `.config/claude/references/e2e-tool-selection.md` — Hurl 追記

- [ ] **Step 1: harness-rationale.md 作成**

`.config/claude/references/harness-rationale.md`:
```markdown
# Harness Engineering Rationale

ハーネス設計の定量的根拠と設計分類。
なぜハーネスに投資するのかを判断する際に参照する。

Ref: Harness Engineering Best Practices 2026 (逆瀬川)

---

## Morph 22:1 比率

> 「モデル選択はパフォーマンスを 1 ポイント変える。ハーネス設計は 22 ポイント変える」
> — Morph 分析

**意味**: 同一モデルでもハーネスの違いで 22 点の性能差が生じる。
モデルをアップグレードするより、ハーネスを改善する方が ROI が高い。

**適用場面**: 新機能追加やツール選定で「より賢いモデルを使えば解決する」と
考えたとき、まずハーネス（hook, lint, test）の強化を検討する。

---

## Factory.ai カスタムリンター 4 分類

カスタム lint ルールを設計する際の分類フレームワーク:

### 1. Grep-ability（検索可能性）
- named exports を強制
- 一貫したエラー型を強制
- 明示的な DTO を強制
- **目的**: エージェントが Grep でコードを発見できるようにする

### 2. Glob-ability（ファイル発見可能性）
- 予測可能なファイル構造を強制
- 命名規則の統一（kebab-case, PascalCase 等）
- **目的**: エージェントが Glob でファイルを確実に発見・作成・リファクタできるようにする

### 3. Architecture Boundaries（アーキテクチャ境界）
- レイヤー間 import の allowlist/denylist
- 依存方向の強制（上位 → 下位のみ）
- **目的**: 暗黙の結合を防ぎ、変更影響を限定する

### 4. Security/Privacy（セキュリティ・プライバシー）
- plaintext secrets のブロック
- 入力バリデーションの強制
- `eval` / `new Function` の禁止
- **目的**: セキュリティ脆弱性の自動防止

---

## フィードバック速度の階層

| 層 | 速度 | 実装 |
|---|---|---|
| PostToolUse | ms | auto-format.js (Biome, Oxlint, Ruff, gofmt) |
| Pre-commit | s | Lefthook (lefthook.yml) |
| CI | min | GitHub Actions (テストスイート) |
| Human Review | h | /review スキル |

**原則**: チェックを可能な限り左（速い層）に移動する。
PostToolUse で検出できるものを CI まで待たない。

---

## AI 生成コードの主要アンチパターン（OX Security/Snyk）

| パターン | 発生率 | 対策 |
|---------|--------|------|
| `any` 乱用 | 高 | GP-005 + `no-explicit-any: error` |
| コード重複 | 高 | GP-001 (共有ユーティリティ優先) |
| ゴーストファイル | 中 | GP-009 (golden-check.py) |
| コメント過多 | 90-100% | GP-010 (golden-check.py) |
| セキュリティ脆弱性 | 36-40% | gosec, eslint-plugin-security, Ruff S-rules |
```

- [ ] **Step 2: e2e-tool-selection.md に Hurl 追記**

`.config/claude/references/e2e-tool-selection.md` の末尾に追加:

```markdown

## API/バックエンド E2E: Hurl

プレーンテキスト形式の HTTP テストツール。エージェントが読み書きしやすい。

```hurl
POST http://localhost:3000/api/users
Content-Type: application/json
{
  "name": "Test User",
  "email": "test@example.com"
}
HTTP 201
[Asserts]
jsonpath "$.id" exists
```

| 特徴 | 詳細 |
|------|------|
| 形式 | プレーンテキスト（Rust バイナリ、libcurl ベース） |
| CI 統合 | ネイティブ対応、JUnit XML 出力 |
| 変数 | `--variable` でリクエスト間の状態引き継ぎ |
| 推奨用途 | REST API のスモークテスト、契約テスト |
```

- [ ] **Step 3: コミット**

```bash
git add .config/claude/references/harness-rationale.md .config/claude/references/e2e-tool-selection.md
git commit -m "📝 docs: add harness rationale (Morph 22:1, Factory.ai) and Hurl to e2e guide"
```

---

## 完了後チェックリスト

- [ ] 全コミットが conventional commit 形式に準拠
- [ ] `python -c "import ast; ast.parse(...)"` で golden-check.py の構文 OK
- [ ] `node -c auto-format.js` で構文 OK
- [ ] `lefthook run pre-commit --dry-run` が正常動作
- [ ] MEMORY.md を更新（記事ベース改善の実施記録）
