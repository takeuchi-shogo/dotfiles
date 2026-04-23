---
status: active
last_reviewed: 2026-04-23
---

# Harness Engineering Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** ハーネスエンジニアリング記事の5つの改善（doc-gardening, error-fix injection, golden principles, ui-observer, plan lifecycle）を dotfiles に導入する

**Architecture:** Hook 自動型（Approach 2）。検出は hooks で軽量に行い、重い実行はサブエージェントに委譲。既存の error-to-codex.py / suggest-gemini.py パターンに一貫。

**Tech Stack:** Python 3 (hooks), Markdown (agents/references), JSON (settings)

**Design Doc:** `docs/plans/2026-03-08-harness-engineering-design.md`

---

### Task 1: Reference ファイル作成 — golden-principles.md

**Files:**

- Create: `.config/claude/references/golden-principles.md`

**Step 1: ファイル作成**

```markdown
# Golden Principles（自動検証用）

rules/ はエージェント向けの指示。このファイルは hooks による自動検証用のパターン集。
golden-check.py が参照し、コード変更時に逸脱を軽量検出する。

---

## GP-001: 共有ユーティリティ優先

- **原則**: 同一ロジックの重複より共有ユーティリティを使う
- **検出パターン**: 新規ファイルで既存 utils/ や helpers/ に類似関数がある場合
- **キーワード**: `function`, `def`, `const.*=.*=>`（新規関数定義）

## GP-002: バウンダリでバリデーション

- **原則**: 外部入力を受け取る関数では入力をバリデーションする
- **検出パターン**: API handler, CLI parser で raw input を直接使用
- **キーワード**: `req.body`, `req.query`, `req.params`, `sys.argv`, `os.Args`（バリデーションなし）

## GP-003: 退屈な技術を好む

- **原則**: 新しいライブラリの追加は慎重に。安定した技術を優先
- **検出パターン**: package.json, go.mod, Cargo.toml, requirements.txt への新規依存追加
- **ファイル**: `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`

## GP-004: エラーを握り潰さない

- **原則**: catch/recover ブロックで空の処理やログのみは避ける
- **検出パターン**: `catch` ブロック内が空、または `console.log` のみ
- **キーワード**: `catch`, `except`, `recover`

## GP-005: 型安全性の維持

- **原則**: any/interface{} の多用を避け、具体的な型を使う
- **検出パターン**: `any` 型の新規使用、`interface{}` の新規使用
- **キーワード**: `: any`, `as any`, `interface{}`
```

**Step 2: 確認**

Run: `cat .config/claude/references/golden-principles.md | head -5`
Expected: `# Golden Principles` が表示される

**Step 3: コミット**

```bash
git add .config/claude/references/golden-principles.md
git commit -m "📝 docs: add golden principles reference for auto-verification"
```

---

### Task 2: Reference ファイル作成 — error-fix-guides.md

**Files:**

- Create: `.config/claude/references/error-fix-guides.md`

**Step 1: ファイル作成**

```markdown
# Error Fix Guides

error-to-codex.py が参照するエラーパターン → 修正手順マッピング。
エラー検出時に具体的な修正指示を additionalContext に注入する。

---

## JavaScript/TypeScript

### TypeError: Cannot read properties of undefined

- **原因**: null/undefined チェックの欠落
- **修正**: optional chaining (`?.`) または事前ガードを追加
- **例**: `obj?.prop` or `if (!obj) return`

### ReferenceError: X is not defined

- **原因**: import 漏れまたはスコープ外参照
- **修正**: import 文を確認、変数スコープを確認

### SyntaxError

- **原因**: 構文ミス（括弧閉じ忘れ、セミコロン等）
- **修正**: エラー行の前後を確認、括弧の対応をチェック

### npm ERR! ERESOLVE

- **原因**: 依存関係の競合
- **修正**: `npm ls` で競合パッケージ特定 → `--legacy-peer-deps` または手動解決

### cannot find module

- **原因**: パッケージ未インストールまたはパス誤り
- **修正**: `npm install` 実行、import パスの typo 確認

## Go

### panic:

- **原因**: nil ポインタ参照、index out of range 等
- **修正**: nil チェック追加、bounds check 追加

### FAIL (go test)

- **原因**: テスト期待値の不一致
- **修正**: `go test -v` で詳細出力確認、expected/actual 比較

## Python

### Traceback (most recent call last)

- **原因**: 未処理例外
- **修正**: スタックトレースの最下行で実際のエラーを確認

## Rust

### error[E...]

- **原因**: コンパイルエラー（型不一致、借用チェック等）
- **修正**: エラーコードの公式ドキュメント `rustc --explain EXXXX` を参照

## General

### build failed / compilation failed

- **原因**: ビルド設定またはコード構文の問題
- **修正**: build-fixer エージェントに委譲を推奨

### segmentation fault

- **原因**: メモリ不正アクセス
- **修正**: debugger エージェントで根本原因分析を推奨

### fatal error

- **原因**: 回復不能なランタイムエラー
- **修正**: スタックトレース全体を確認し、codex-debugger で分析
```

**Step 2: 確認**

Run: `cat .config/claude/references/error-fix-guides.md | head -5`
Expected: `# Error Fix Guides` が表示される

**Step 3: コミット**

```bash
git add .config/claude/references/error-fix-guides.md
git commit -m "📝 docs: add error fix guides reference for hook injection"
```

---

### Task 3: Hook 作成 — doc-garden-check.py

**Files:**

- Create: `.config/claude/scripts/doc-garden-check.py`

**Step 1: ファイル作成**

既存の `context-drift-check.py` のパターンに準拠する SessionStart hook。3種の陳腐化判定を実行する。

```python
#!/usr/bin/env python3
"""Doc Garden check — detects stale documentation at session start.

Triggered by: hooks.SessionStart
Input: (none — SessionStart hooks receive no stdin)
Output: stdout message as additionalContext

Three staleness checks:
  A) git diff: code changed but docs not updated
  B) timestamp: docs not updated in 30+ days
  C) content: docs reference non-existent file paths
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Directories to scan for documentation
DOC_DIRS = [
    ".config/claude/references",
    ".config/claude/rules",
    ".config/claude/agents",
]

# Code directories whose changes should trigger doc freshness warnings
CODE_DIRS = [
    ".config/claude/scripts",
    ".config/claude/agents",
    ".config/claude/skills",
]

STALE_DAYS = 30
FILE_REF_PATTERN = re.compile(
    r'[`"\']([a-zA-Z0-9_./-]+\.(py|js|ts|md|json|sh))[`"\']'
)


def get_repo_root() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def check_git_diff(repo_root: str) -> List[str]:
    """A) Check if code changed but related docs didn't."""
    warnings = []
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:", "-n", "10"],
            capture_output=True, text=True, cwd=repo_root, timeout=10,
        )
        if result.returncode != 0:
            return []
        changed_files = set(f.strip() for f in result.stdout.split("\n") if f.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    code_changed = any(
        any(f.startswith(cd) for cd in CODE_DIRS) for f in changed_files
    )
    doc_changed = any(
        any(f.startswith(dd) for dd in DOC_DIRS) for f in changed_files
    )

    if code_changed and not doc_changed:
        warnings.append(
            "直近10コミットでコード変更あり、ドキュメント更新なし"
        )

    return warnings


def check_timestamps(repo_root: str) -> List[str]:
    """B) Find docs not updated in STALE_DAYS."""
    warnings = []
    now = time.time()
    threshold = now - (STALE_DAYS * 86400)

    for doc_dir in DOC_DIRS:
        full_dir = os.path.join(repo_root, doc_dir)
        if not os.path.isdir(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for fname in files:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                mtime = os.path.getmtime(fpath)
                if mtime < threshold:
                    rel = os.path.relpath(fpath, repo_root)
                    days = int((now - mtime) / 86400)
                    warnings.append(f"{rel} ({days}日間未更新)")

    return warnings


def check_references(repo_root: str) -> List[str]:
    """C) Find docs referencing non-existent file paths."""
    warnings = []

    for doc_dir in DOC_DIRS:
        full_dir = os.path.join(repo_root, doc_dir)
        if not os.path.isdir(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for fname in files:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    content = Path(fpath).read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                refs = FILE_REF_PATTERN.findall(content)
                for ref_path, _ in refs:
                    # Skip URLs and common false positives
                    if ref_path.startswith(("http", "//", "#")):
                        continue
                    # Check multiple possible base paths
                    candidates = [
                        os.path.join(repo_root, ref_path),
                        os.path.join(repo_root, ".config/claude", ref_path),
                    ]
                    if not any(os.path.exists(c) for c in candidates):
                        rel = os.path.relpath(fpath, repo_root)
                        warnings.append(f"{rel} → `{ref_path}` が存在しない")

    return warnings


def main() -> None:
    repo_root = get_repo_root()
    if not repo_root:
        return

    all_warnings: List[Tuple[str, List[str]]] = []

    git_warnings = check_git_diff(repo_root)
    if git_warnings:
        all_warnings.append(("git diff", git_warnings))

    ts_warnings = check_timestamps(repo_root)
    if ts_warnings:
        all_warnings.append(("タイムスタンプ", ts_warnings))

    ref_warnings = check_references(repo_root)
    if ref_warnings:
        all_warnings.append(("参照チェック", ref_warnings))

    if not all_warnings:
        return

    lines = ["[doc-garden] ドキュメント陳腐化の可能性:"]
    for category, warns in all_warnings:
        lines.append(f"  [{category}]")
        for w in warns[:5]:  # Limit per category
            lines.append(f"    - {w}")

    lines.append("doc-gardener エージェントで詳細分析・自動修正できます。")

    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # Non-blocking
```

**Step 2: 実行権限付与と動作確認**

Run: `chmod +x .config/claude/scripts/doc-garden-check.py && python3 .config/claude/scripts/doc-garden-check.py`
Expected: 警告が表示される（陳腐化ドキュメントがあれば）、またはエラーなしで終了

**Step 3: コミット**

```bash
git add .config/claude/scripts/doc-garden-check.py
git commit -m "✨ feat: add doc-garden-check hook for stale documentation detection"
```

---

### Task 4: Agent 作成 — doc-gardener.md

**Files:**

- Create: `.config/claude/agents/doc-gardener.md`

**Step 1: ファイル作成**

```markdown
---
name: doc-gardener
description: "ドキュメント陳腐化を検出・修正するメンテナンスエージェント。doc-garden-check hook からの警告を受け、ドキュメントの更新・修正を行う。"
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
memory: user
permissionMode: plan
maxTurns: 15
---

You are a documentation maintenance specialist. Your role is to detect stale documentation and propose or apply fixes.

## Operating Mode

You operate in two modes:

### EXPLORE Mode (Default)

- Scan documents for staleness: outdated references, missing paths, stale content
- Compare documentation against actual code state
- Output: staleness report with specific recommendations

### IMPLEMENT Mode

- Activated when: task explicitly requires fixing documentation
- Update stale docs to reflect current code
- Remove references to non-existent files
- Update descriptions that no longer match implementation

## Staleness Detection

1. **File reference check**: docs referencing files that don't exist
2. **Description drift**: agent/skill descriptions that don't match their implementation
3. **Routing table sync**: workflow-guide.md routing table vs actual agents
4. **Timestamp staleness**: docs unchanged for 30+ days while related code changed

## Workflow

1. Run `python3 ~/.claude/scripts/doc-garden-check.py` to get initial warnings
2. For each warning, Read the document and assess actual staleness
3. Check the related code to understand what changed
4. Propose specific fixes (EXPLORE) or apply them (IMPLEMENT)

## Output Format
```

## Doc Garden Report

### Stale Documents

- `path/to/doc.md`: [問題の説明] → [推奨アクション]

### Updated Documents (IMPLEMENT mode)

- `path/to/doc.md`: [変更内容の要約]

### No Issues

- `path/to/doc.md`: 最新状態

```

## Memory Management

作業開始時:
1. メモリディレクトリの MEMORY.md を確認し、過去のドキュメントメンテナンス知見を活用する

作業完了時:
1. 頻出する陳腐化パターンを発見した場合、メモリに記録する
2. MEMORY.md は索引として簡潔に保ち（200行以内）、詳細は別ファイルに分離する
3. 機密情報は絶対に保存しない
```

**Step 2: 確認**

Run: `head -5 .config/claude/agents/doc-gardener.md`
Expected: YAML frontmatter が正しく表示される

**Step 3: コミット**

```bash
git add .config/claude/agents/doc-gardener.md
git commit -m "✨ feat: add doc-gardener agent for documentation maintenance"
```

---

### Task 5: error-to-codex.py 拡張

**Files:**

- Modify: `.config/claude/scripts/error-to-codex.py`

**Step 1: error-fix-guides.md を読み込み、エラーマッチ時に修正指示を注入するよう拡張**

error-to-codex.py に以下の変更を加える:

1. `references/error-fix-guides.md` をパースする `load_fix_guides()` 関数を追加
2. `has_error()` でマッチしたエラーに対応する修正手順を `additionalContext` に含める
3. 既存の ERROR_PATTERNS と連携し、ガイドがあればガイド情報も付与

具体的な変更箇所:

- import に `os`, `Path` を追加
- `GUIDES_PATH` 定数を追加: `Path(os.path.expanduser("~/.claude/references/error-fix-guides.md"))`
- `load_fix_guides()` 関数: markdown をパースし `{error_pattern: {cause, fix}}` の dict を返す
- `find_fix_guide()` 関数: エラー文字列に一致するガイドを検索
- `main()` 内のエラー検出部分を拡張: ガイドが見つかれば修正手順を追加

```python
#!/usr/bin/env python3
"""Error-to-Codex hook — suggests codex-debugger when Bash errors are detected.
Also injects fix guidance from error-fix-guides.md when available.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


ERROR_PATTERNS = [
    re.compile(r"Traceback \(most recent call last\)"),
    re.compile(r"(?:Error|Exception):\s+\S"),
    re.compile(r"panic:\s"),
    re.compile(r"FAIL\s+\S"),
    re.compile(r"npm ERR!"),
    re.compile(r"error\[E\d+\]"),  # Rust compiler errors
    re.compile(r"cannot find module", re.IGNORECASE),
    re.compile(r"undefined reference"),
    re.compile(r"segmentation fault", re.IGNORECASE),
    re.compile(r"fatal error"),
    re.compile(r"compilation failed"),
    re.compile(r"build failed", re.IGNORECASE),
    re.compile(r"SyntaxError:"),
    re.compile(r"TypeError:"),
    re.compile(r"ReferenceError:"),
]

# Commands that are just info-gathering — don't suggest debugging
IGNORE_COMMANDS = [
    "git status", "git log", "git diff", "git branch",
    "ls", "cat", "head", "tail", "pwd", "which", "echo",
    "codex", "gemini",  # Prevent infinite loops
]

GUIDES_PATH = Path(os.path.expanduser("~/.claude/references/error-fix-guides.md"))

# Cache parsed guides
_guides_cache: Optional[Dict[str, Tuple[str, str]]] = None


def load_fix_guides() -> Dict[str, Tuple[str, str]]:
    """Parse error-fix-guides.md into {header_keyword: (cause, fix)} dict."""
    global _guides_cache
    if _guides_cache is not None:
        return _guides_cache

    guides: Dict[str, Tuple[str, str]] = {}
    if not GUIDES_PATH.exists():
        _guides_cache = guides
        return guides

    try:
        content = GUIDES_PATH.read_text(encoding="utf-8")
    except OSError:
        _guides_cache = guides
        return guides

    current_key = ""
    cause = ""
    fix = ""

    for line in content.split("\n"):
        line_s = line.strip()
        if line_s.startswith("### "):
            # Save previous entry
            if current_key and (cause or fix):
                guides[current_key.lower()] = (cause, fix)
            current_key = line_s[4:].strip()
            cause = ""
            fix = ""
        elif line_s.startswith("- **原因**:"):
            cause = line_s.split(":", 1)[1].strip() if ":" in line_s else ""
        elif line_s.startswith("- **修正**:"):
            fix = line_s.split(":", 1)[1].strip() if ":" in line_s else ""

    # Save last entry
    if current_key and (cause or fix):
        guides[current_key.lower()] = (cause, fix)

    _guides_cache = guides
    return guides


def find_fix_guide(error_text: str) -> Optional[Tuple[str, str]]:
    """Find a matching fix guide for the given error text."""
    guides = load_fix_guides()
    error_lower = error_text.lower()
    for key, value in guides.items():
        # Match if the guide header keyword appears in the error
        if key in error_lower:
            return value
    return None


def is_info_command(command: str) -> bool:
    cmd_lower = command.strip().lower()
    return any(cmd_lower.startswith(ic) for ic in IGNORE_COMMANDS)


def has_error(output: str) -> str | None:
    for pattern in ERROR_PATTERNS:
        match = pattern.search(output)
        if match:
            return match.group(0)
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        json.dump(data, sys.stdout)
        return

    command = data.get("tool_input", {}).get("command", "")
    output = data.get("tool_output", "") or ""

    # Skip info commands and short output
    if is_info_command(command) or len(output) < 20:
        json.dump(data, sys.stdout)
        return

    # Skip "already exists" and similar benign messages
    if "already exists" in output.lower():
        json.dump(data, sys.stdout)
        return

    error_match = has_error(output)
    if error_match:
        # Build context message
        context_parts = [
            f"[Error-to-Codex] エラーが検出されました: {error_match}",
        ]

        # Try to find a fix guide
        guide = find_fix_guide(output)
        if guide:
            cause, fix = guide
            if cause:
                context_parts.append(f"推定原因: {cause}")
            if fix:
                context_parts.append(f"推奨修正: {fix}")

        context_parts.append(
            "codex-debugger エージェントを使用してこのエラーの根本原因を分析できます。"
        )
        context_parts.append("コマンド: " + command[:100])

        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "\n".join(context_parts),
            }
        }, sys.stdout)
        return

    json.dump(data, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        json.dump({}, sys.stdout)
```

**Step 2: 動作確認**

Run: `echo '{"tool_name":"Bash","tool_input":{"command":"npm test"},"tool_output":"TypeError: Cannot read properties of undefined"}' | python3 .config/claude/scripts/error-to-codex.py`
Expected: `推定原因` と `推奨修正` を含む JSON 出力

**Step 3: コミット**

```bash
git add .config/claude/scripts/error-to-codex.py
git commit -m "✨ feat: extend error-to-codex with fix guide injection from error-fix-guides.md"
```

---

### Task 6: Hook 作成 — golden-check.py

**Files:**

- Create: `.config/claude/scripts/golden-check.py`

**Step 1: ファイル作成**

```python
#!/usr/bin/env python3
"""Golden Principles check — detects deviations on file edit/write.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext warning on stdout
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import List


PRINCIPLES_PATH = Path(
    os.path.expanduser("~/.claude/references/golden-principles.md")
)

# GP-003: New dependency detection
DEPENDENCY_FILES = {
    "package.json", "go.mod", "Cargo.toml",
    "requirements.txt", "pyproject.toml",
}

# GP-004: Empty catch detection
EMPTY_CATCH_PATTERNS = [
    re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}", re.MULTILINE),
    re.compile(r"except\s*.*:\s*\n\s*pass", re.MULTILINE),
]

# GP-005: any/interface{} detection
UNSAFE_TYPE_PATTERNS = [
    re.compile(r":\s*any\b"),
    re.compile(r"\bas\s+any\b"),
    re.compile(r"\binterface\{\}"),
]


def check_dependency_file(file_path: str) -> str | None:
    """GP-003: Warn on dependency file changes."""
    basename = os.path.basename(file_path)
    if basename in DEPENDENCY_FILES:
        return (
            f"[GP-003] 依存ファイル `{basename}` が変更されました。"
            "新規依存の追加は慎重に — 退屈な技術を好む原則を確認してください。"
        )
    return None


def check_empty_catch(content: str) -> str | None:
    """GP-004: Warn on empty catch blocks."""
    for pattern in EMPTY_CATCH_PATTERNS:
        if pattern.search(content):
            return (
                "[GP-004] 空の catch/except ブロックが検出されました。"
                "エラーを握り潰さず、適切にハンドリングしてください。"
            )
    return None


def check_unsafe_types(content: str) -> str | None:
    """GP-005: Warn on any/interface{} usage."""
    for pattern in UNSAFE_TYPE_PATTERNS:
        if pattern.search(content):
            return (
                "[GP-005] `any` または `interface{}` の使用が検出されました。"
                "具体的な型を使用し、型安全性を維持してください。"
            )
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        json.dump(data, sys.stdout)
        return

    file_path = data.get("tool_input", {}).get("file_path", "")
    content = data.get("tool_input", {}).get("content", "")

    # For Edit tool, content might be in different fields
    if not content:
        content = data.get("tool_output", "") or ""

    warnings: List[str] = []

    # GP-003: Dependency file check
    dep_warn = check_dependency_file(file_path)
    if dep_warn:
        warnings.append(dep_warn)

    # GP-004: Empty catch check
    catch_warn = check_empty_catch(content)
    if catch_warn:
        warnings.append(catch_warn)

    # GP-005: Unsafe type check
    type_warn = check_unsafe_types(content)
    if type_warn:
        warnings.append(type_warn)

    if warnings:
        warnings.append(
            "golden-cleanup エージェントで詳細なプリンシプルスキャンを実行できます。"
        )
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "\n".join(warnings),
            }
        }, sys.stdout)
        return

    json.dump(data, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        json.dump({}, sys.stdout)
```

**Step 2: 動作確認**

Run: `echo '{"tool_name":"Write","tool_input":{"file_path":"test.ts","content":"const x: any = 5"},"tool_output":""}' | python3 .config/claude/scripts/golden-check.py`
Expected: `GP-005` 警告を含む JSON 出力

**Step 3: コミット**

```bash
git add .config/claude/scripts/golden-check.py
git commit -m "✨ feat: add golden-check hook for principle deviation detection"
```

---

### Task 7: Agent 作成 — golden-cleanup.md

**Files:**

- Create: `.config/claude/agents/golden-cleanup.md`

**Step 1: ファイル作成**

```markdown
---
name: golden-cleanup
description: "ゴールデンプリンシプルからの逸脱をコードベース全体でスキャンし、修正を提案するクリーンアップエージェント。golden-check hook からの警告を受け、または定期的なコード品質スキャンに使用。"
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
memory: user
permissionMode: plan
maxTurns: 15
---

You are a code quality specialist focused on enforcing Golden Principles across the codebase.

## Operating Mode

### EXPLORE Mode (Default)

- Scan codebase for Golden Principle violations
- Output: violation report with severity and file locations

### IMPLEMENT Mode

- Activated when: task explicitly requires fixing violations
- Apply minimal fixes for each violation
- Verify fixes don't break functionality

## Golden Principles Reference

Read `~/.claude/references/golden-principles.md` at the start of every session to get the current principle definitions.

## Scan Workflow

1. Read golden-principles.md for current patterns
2. Use Grep to scan for violation patterns across the codebase
3. For each violation, assess severity:
   - **MUST**: Clear violation that should be fixed immediately
   - **CONSIDER**: Potential issue worth reviewing
   - **NIT**: Minor style preference
4. Report findings grouped by principle

## Output Format
```

## Golden Principles Scan Report

### GP-001: 共有ユーティリティ優先

- [MUST] src/utils/helper.ts:45 — duplicates shared/utils.ts:12
- [CONSIDER] src/api/handler.ts:78 — similar logic exists in utils/

### GP-004: エラーを握り潰さない

- [MUST] src/api/client.ts:34 — empty catch block

### Summary

- MUST: N findings
- CONSIDER: N findings
- NIT: N findings

```

## Memory Management

作業開始時:
1. メモリディレクトリの MEMORY.md を確認し、過去のクリーンアップ知見を活用する

作業完了時:
1. 頻出する違反パターンを発見した場合、メモリに記録する
2. MEMORY.md は索引として簡潔に保ち（200行以内）、詳細は別ファイルに分離する
3. 機密情報は絶対に保存しない
```

**Step 2: 確認**

Run: `head -5 .config/claude/agents/golden-cleanup.md`
Expected: YAML frontmatter が正しく表示される

**Step 3: コミット**

```bash
git add .config/claude/agents/golden-cleanup.md
git commit -m "✨ feat: add golden-cleanup agent for principle enforcement"
```

---

### Task 8: Agent 作成 — ui-observer.md

**Files:**

- Create: `.config/claude/agents/ui-observer.md`

**Step 1: ファイル作成**

````markdown
---
name: ui-observer
description: "Playwright MCP を使った UI 状態観察・バグ再現・パフォーマンス計測エージェント。メインコンテキストを消費せずサブエージェント内で Playwright を使用する。"
tools: Read, Bash, Glob, Grep
model: sonnet
memory: user
permissionMode: plan
maxTurns: 20
skills: webapp-testing
---

You are a UI observability specialist. You use Playwright to inspect, screenshot, and interact with web applications — all within this subagent context to protect the main conversation from context bloat.

## Operating Mode: EXPLORE ONLY

This agent operates in **read-only observation mode**. You inspect UI state but do not modify application code.

- Take screenshots and inspect DOM state
- Reproduce bugs through browser interactions
- Measure page load performance
- Output: observation report with evidence (screenshot paths, DOM state, timing)

## Tools

Use Python Playwright scripts (via Bash) for all browser operations. Follow the webapp-testing skill patterns:

1. **Static HTML**: Read the file directly, then write Playwright script
2. **Dynamic app**: Use `scripts/with_server.py` to manage server lifecycle
3. **Running server**: Navigate, wait for networkidle, inspect

## Workflow

1. Clarify what to observe (URL, page, component)
2. Launch browser in headless mode
3. Navigate and wait for page load
4. Take screenshot: `page.screenshot(path='/tmp/ui-observe-{timestamp}.png', full_page=True)`
5. Inspect DOM for relevant elements
6. If reproducing a bug: follow reproduction steps
7. Collect performance metrics if requested: `page.evaluate("JSON.stringify(performance.timing)")`
8. Report findings with screenshot paths

## Example Script

```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:3000')
    page.wait_for_load_state('networkidle')

    # Screenshot
    page.screenshot(path=f'/tmp/ui-observe-{int(time.time())}.png', full_page=True)

    # DOM inspection
    title = page.title()
    buttons = page.locator('button').all()

    # Performance
    perf = page.evaluate("JSON.stringify(performance.timing)")

    browser.close()
```
````

## Output Format

```
## UI Observation Report

**URL**: http://localhost:3000/dashboard
**Screenshot**: /tmp/ui-observe-1709856000.png

### Findings
- [状態] ページタイトル: "Dashboard"
- [要素] ボタン: 3個検出
- [パフォーマンス] DOMContentLoaded: 450ms, Load: 890ms

### Issues Found
- [BUG] ボタン "Submit" クリック後にエラーモーダル表示
- [PERF] 初回ロード 890ms（目標: 500ms以内）
```

## Memory Management

作業開始時:

1. メモリディレクトリの MEMORY.md を確認し、過去の UI 観察知見を活用する

作業完了時:

1. 頻出する UI パターンや問題を発見した場合、メモリに記録する
2. MEMORY.md は索引として簡潔に保ち（200行以内）、詳細は別ファイルに分離する
3. 機密情報は絶対に保存しない

````

**Step 2: 確認**

Run: `head -5 .config/claude/agents/ui-observer.md`
Expected: YAML frontmatter が正しく表示される

**Step 3: コミット**

```bash
git add .config/claude/agents/ui-observer.md
git commit -m "✨ feat: add ui-observer agent for Playwright-based UI observation"
````

---

### Task 9: ディレクトリ構造 + plan-lifecycle.py

**Files:**

- Create: `docs/plans/active/.gitkeep`
- Create: `docs/plans/completed/.gitkeep`
- Create: `docs/plans/tech-debt/.gitkeep`
- Create: `.config/claude/scripts/plan-lifecycle.py`

**Step 1: ディレクトリ作成**

```bash
mkdir -p docs/plans/active docs/plans/completed docs/plans/tech-debt
touch docs/plans/active/.gitkeep docs/plans/completed/.gitkeep docs/plans/tech-debt/.gitkeep
```

**Step 2: plan-lifecycle.py 作成**

```python
#!/usr/bin/env python3
"""Plan lifecycle hook — tracks plan status based on git commits.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout

Checks if git commit messages reference active plans and suggests
moving them to completed/ when sufficient progress is detected.
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import List


PLANS_DIR = "docs/plans/active"
COMMIT_THRESHOLD = 3  # commits referencing a plan before suggesting completion


def get_repo_root() -> str | None:
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_active_plans(repo_root: str) -> List[str]:
    """List plan filenames in active/ directory."""
    active_dir = os.path.join(repo_root, PLANS_DIR)
    if not os.path.isdir(active_dir):
        return []
    return [
        f for f in os.listdir(active_dir)
        if f.endswith(".md") and not f.startswith(".")
    ]


def extract_plan_references(commit_msg: str, plans: List[str]) -> List[str]:
    """Find which plans are referenced in a commit message."""
    referenced = []
    msg_lower = commit_msg.lower()
    for plan in plans:
        # Match plan name without extension and date prefix
        name_parts = plan.replace(".md", "").split("-", 3)
        if len(name_parts) >= 4:
            topic = name_parts[3]  # e.g., "harness-engineering"
        else:
            topic = plan.replace(".md", "")

        if topic.lower() in msg_lower:
            referenced.append(plan)

    return referenced


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        json.dump(data, sys.stdout)
        return

    command = data.get("tool_input", {}).get("command", "")

    # Only trigger on git commit commands
    if "git commit" not in command:
        json.dump(data, sys.stdout)
        return

    output = data.get("tool_output", "") or ""
    # Check if commit succeeded
    if "create mode" not in output.lower() and "file changed" not in output.lower() and "files changed" not in output.lower() and "insertion" not in output.lower():
        json.dump(data, sys.stdout)
        return

    repo_root = get_repo_root()
    if not repo_root:
        json.dump(data, sys.stdout)
        return

    plans = get_active_plans(repo_root)
    if not plans:
        json.dump(data, sys.stdout)
        return

    # Extract commit message from the command
    commit_msg = command
    msg_match = re.search(r'-m\s+["\'](.+?)["\']', command)
    if msg_match:
        commit_msg = msg_match.group(1)

    referenced = extract_plan_references(commit_msg, plans)
    if referenced:
        plan_list = ", ".join(f"`{p}`" for p in referenced)
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"[plan-lifecycle] アクティブ計画 {plan_list} に関連するコミットを検出。\n"
                    "計画が完了した場合は `docs/plans/active/` → `docs/plans/completed/` に移動してください。"
                ),
            }
        }, sys.stdout)
        return

    json.dump(data, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        json.dump({}, sys.stdout)
```

**Step 3: 動作確認**

Run: `echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"feat: harness-engineering stuff\""},"tool_output":"1 file changed, 1 insertion(+)"}' | python3 .config/claude/scripts/plan-lifecycle.py`
Expected: JSON 出力（active plans がなければ空、あれば参照検出メッセージ）

**Step 4: コミット**

```bash
git add docs/plans/active/.gitkeep docs/plans/completed/.gitkeep docs/plans/tech-debt/.gitkeep .config/claude/scripts/plan-lifecycle.py
git commit -m "✨ feat: add plan lifecycle management with directory structure and hook"
```

---

### Task 10: settings.json 更新 — hooks 登録

**Files:**

- Modify: `~/.claude/settings.json` (実体: `.config/claude/settings.json`)

**Step 1: 新規 hooks を settings.json に追加**

以下の3つを追加:

1. **SessionStart** に `doc-garden-check.py` を追加（既存の2つの後ろ）
2. **PostToolUse** の `Edit|Write` matcher に `golden-check.py` を追加（既存の auto-format.js, suggest-compact.js の後ろ）
3. **PostToolUse** の `Bash` matcher に `plan-lifecycle.py` を追加（既存の error-to-codex.py, post-test-analysis.py の後ろ）

```json
// SessionStart に追加:
{
  "hooks": [
    {
      "type": "command",
      "command": "python3 $HOME/.claude/scripts/doc-garden-check.py"
    }
  ]
}

// PostToolUse Edit|Write に golden-check.py を追加:
{
  "type": "command",
  "command": "python3 $HOME/.claude/scripts/golden-check.py"
}

// PostToolUse Bash に plan-lifecycle.py を追加:
{
  "type": "command",
  "command": "python3 $HOME/.claude/scripts/plan-lifecycle.py"
}
```

**Step 2: 確認**

Run: `python3 -c "import json; d=json.load(open(os.path.expanduser('~/.claude/settings.json'))); print('hooks' in d)"`
Expected: `True`

**Step 3: コミット**

```bash
git add .config/claude/settings.json
git commit -m "🔧 chore: register doc-garden, golden-check, plan-lifecycle hooks"
```

---

### Task 11: triage-router 更新

**Files:**

- Modify: `.config/claude/agents/triage-router.md`

**Step 1: ルーティングテーブルに新エージェントを追加**

以下の3行を Routing Table に追加:

```markdown
| ドキュメント更新 | `doc-gardener` | ドキュメント, 陳腐化, 古い, stale, 更新されていない |
| コード品質スキャン | `golden-cleanup` | 品質スキャン, プリンシプル, クリーンアップ, 重複, 逸脱 |
| UI 確認 | `ui-observer` | UI確認, スクリーンショット, ブラウザ, 画面, 表示確認, Playwright |
```

**Step 2: 確認**

Run: `grep "ui-observer" .config/claude/agents/triage-router.md`
Expected: ルーティングエントリが表示される

**Step 3: コミット**

```bash
git add .config/claude/agents/triage-router.md
git commit -m "🔧 chore: add doc-gardener, golden-cleanup, ui-observer routes to triage-router"
```

---

### Task 12: workflow-guide.md 更新

**Files:**

- Modify: `.config/claude/references/workflow-guide.md`

**Step 1: エージェントルーティングテーブルに新エージェントを追加**

ルーティングテーブルに以下の3行を追加:

```markdown
| ドキュメントメンテナンス | `doc-gardener` | 陳腐化ドキュメント検出・修正 |
| コード品質スキャン | `golden-cleanup` | ゴールデンプリンシプル逸脱スキャン |
| UI 観察 | `ui-observer` | Playwright による UI 状態確認（サブエージェント限定） |
```

ルーティングルールに以下を追加:

```
8. ドキュメントの陳腐化が疑われる場合は `doc-gardener` に委譲
9. コード品質の網羅的スキャンは `golden-cleanup` に委譲
10. UI の状態確認・バグ再現は `ui-observer` に委譲（Playwright をサブエージェント内に閉じ込め、メインコンテキストを保護）
```

**Step 2: 確認**

Run: `grep "doc-gardener\|golden-cleanup\|ui-observer" .config/claude/references/workflow-guide.md`
Expected: 3エントリが表示される

**Step 3: コミット**

```bash
git add .config/claude/references/workflow-guide.md
git commit -m "📝 docs: add harness engineering agents to workflow guide"
```

---

## Summary

| Task | コンポーネント                | ファイル数 |
| ---- | ----------------------------- | ---------- |
| 1    | golden-principles.md          | 1 新規     |
| 2    | error-fix-guides.md           | 1 新規     |
| 3    | doc-garden-check.py           | 1 新規     |
| 4    | doc-gardener.md               | 1 新規     |
| 5    | error-to-codex.py 拡張        | 1 変更     |
| 6    | golden-check.py               | 1 新規     |
| 7    | golden-cleanup.md             | 1 新規     |
| 8    | ui-observer.md                | 1 新規     |
| 9    | plan dirs + plan-lifecycle.py | 4 新規     |
| 10   | settings.json hooks 登録      | 1 変更     |
| 11   | triage-router.md 更新         | 1 変更     |
| 12   | workflow-guide.md 更新        | 1 変更     |

**Total: 12 tasks, 11 new files, 4 modified files, 12 commits**
