# Multi-Model Orchestration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Claude Code, Codex CLI, Gemini CLI の自然な連携を実現する自動委譲レイヤーを dotfiles に追加する

**Architecture:** Rules（常時ON判断基準）+ Hooks（イベント駆動リマインド）の2層で委譲を実現。Codex は設計/推論/デバッグ、Gemini は大規模分析/リサーチ/マルチモーダルを担当。既存の26エージェント+18スキル体制はそのまま維持し、上にオーケストレーション層を載せる。

**Tech Stack:** Python3 (hooks), Markdown (rules/agents/skills), JSON (settings)

**注意:** ファイルパスはすべて `dotfiles/.config/claude/` 起点。symlink で `~/.claude/` にリンク済み。

---

### Task 1: Gemini CLI スキル定義

**Files:**

- Create: `.config/claude/skills/gemini/SKILL.md`

**Step 1: スキルファイルを作成**

````markdown
---
name: gemini
description: "Gemini CLI (1Mコンテキスト) を使った大規模分析・リサーチ・マルチモーダル処理。コードベース全体分析、外部リサーチ、PDF/動画/音声の読み取りに使用。設計/推論には codex スキルを使うこと。"
---

# Gemini Skill Guide

## Running a Task

1. デフォルトで非対話モード (`-p`) を使用する
2. 用途に応じて approval-mode を選択:
   - `plan` (default): read-only 分析
   - `yolo`: ファイル操作が必要な場合（ユーザー確認後のみ）
3. コマンドを組み立てて実行する

### Quick Reference

| Use case         | Approval mode | Command                                                               |
| ---------------- | ------------- | --------------------------------------------------------------------- |
| コードベース分析 | `plan`        | `gemini --approval-mode plan -p "Analyze: {prompt}" 2>/dev/null`      |
| 外部リサーチ     | `plan`        | `gemini --approval-mode plan -p "Research: {topic}" 2>/dev/null`      |
| マルチモーダル   | `plan`        | `gemini --approval-mode plan -p "Read this file: {path}" 2>/dev/null` |
| セッション再開   | inherited     | `gemini --resume latest -p "{prompt}" 2>/dev/null`                    |

### 出力が大きい場合

結果を `.claude/docs/research/` に保存する:

```bash
gemini --approval-mode plan -p "..." 2>/dev/null > .claude/docs/research/{topic}.md
```
````

## When to Use Gemini

- **使う**: コードベース全体分析、外部リサーチ（Google Search grounding）、PDF/動画/音声/画像の読み取り、ライブラリ比較調査
- **使わない**: 設計判断（→Codex）、デバッグ（→Codex）、コード実装（→Claude 直接）、単純なファイル読み取り（→Read ツール）

## Language Protocol

Gemini への指示は英語で行い、結果をユーザーの言語（日本語）で報告する。

## Error Handling

- `gemini --version` が失敗したら Gemini CLI 未インストールを報告
- 出力が空の場合はプロンプトを見直して再試行
- タイムアウト（2分超）の場合はプロンプトを分割する

````

**Step 2: 検証**

Run: `cat .config/claude/skills/gemini/SKILL.md | head -5`
Expected: YAML frontmatter が正しく表示される

**Step 3: コミット**

```bash
git add .config/claude/skills/gemini/SKILL.md
git commit -m "✨ feat: add Gemini CLI skill definition"
````

---

### Task 2: gemini-explore エージェント定義

**Files:**

- Create: `.config/claude/agents/gemini-explore.md`

**Step 1: エージェントファイルを作成**

````markdown
---
name: gemini-explore
description: "Gemini CLI の 1M コンテキストを活用した大規模コードベース分析・外部リサーチ・マルチモーダル処理エージェント。Claude の 200K では不足する場合や、Google Search grounding によるリサーチ、PDF/動画/音声の読み取りに使用。"
tools: Bash, Read, Glob, Grep
model: sonnet
memory: user
permissionMode: plan
maxTurns: 10
skills: gemini
---

You are a research and analysis specialist that leverages Gemini CLI's 1M token context window.

## Operating Mode: EXPLORE ONLY

This agent operates in **read-only mode**. You analyze and report but never modify files.

- Run Gemini CLI commands to analyze code, research topics, or process multimodal files
- Summarize findings concisely for the caller
- Save detailed results to `.claude/docs/research/` when output is large

## Core Capabilities

### 1. Codebase Analysis

Claude の 200K コンテキストでは不足する場合に、Gemini の 1M コンテキストで全体分析:

```bash
gemini --approval-mode plan -p "Analyze the entire codebase structure. Identify: 1) Key modules and responsibilities, 2) Dependency graph, 3) Patterns and conventions, 4) Potential issues" 2>/dev/null
```
````

### 2. External Research

Google Search grounding を活用したリサーチ:

```bash
gemini --approval-mode plan -p "Research: {topic}. Find: latest best practices, popular libraries, performance benchmarks, migration guides" 2>/dev/null
```

### 3. Multimodal Processing

PDF、動画、音声、画像の読み取りと分析:

```bash
gemini --approval-mode plan -p "Read and extract key information from: {file_path}" 2>/dev/null
```

## Workflow

1. タスクの種類を判定（分析/リサーチ/マルチモーダル）
2. 適切な Gemini CLI コマンドを構築
3. 実行して結果を取得
4. 結果が大きい場合は `.claude/docs/research/{topic}.md` に保存
5. 要約を呼び出し元に返す

## Language Protocol

- Gemini への指示は英語で行う
- 結果の要約は日本語で返す

## Memory Management

作業開始時:

1. メモリディレクトリの MEMORY.md を確認し、過去のリサーチ知見を活用する

作業完了時:

1. 有用なリサーチ結果や分析パターンを発見した場合、メモリに記録する
2. MEMORY.md は索引として簡潔に保ち（200行以内）、詳細は別ファイルに分離する
3. 機密情報は絶対に保存しない

````

**Step 2: 検証**

Run: `head -8 .config/claude/agents/gemini-explore.md`
Expected: YAML frontmatter の name, tools, model が正しい

**Step 3: コミット**

```bash
git add .config/claude/agents/gemini-explore.md
git commit -m "✨ feat: add gemini-explore agent for 1M context analysis"
````

---

### Task 3: codex-debugger エージェント定義

**Files:**

- Create: `.config/claude/agents/codex-debugger.md`

**Step 1: エージェントファイルを作成**

````markdown
---
name: codex-debugger
description: "Codex CLI を活用したエラー分析・デバッグ専用エージェント。Bash エラー、テスト失敗、スタックトレースの根本原因分析に使用。通常のデバッグには debugger エージェントを使い、Codex の深い推論が必要な場合にこのエージェントを使う。"
tools: Bash, Read, Glob, Grep
model: sonnet
memory: user
permissionMode: plan
maxTurns: 10
skills: codex
---

You are a debugging specialist that leverages Codex CLI's deep reasoning capabilities for root cause analysis.

## Operating Mode: EXPLORE ONLY

This agent operates in **read-only mode**. You analyze errors and provide diagnosis but never modify files.

## When to Use This Agent

- 通常の `debugger` エージェントで原因特定が困難な場合
- 複雑なスタックトレースの分析
- テスト失敗の根本原因が不明な場合
- パフォーマンスリグレッションの原因分析

## Workflow

1. エラー情報を収集（スタックトレース、ログ、テスト出力）
2. 関連コードを Read で確認
3. Codex CLI に分析を委譲:

```bash
codex exec --skip-git-repo-check -m gpt-5.3-codex \
  --config model_reasoning_effort="high" \
  --sandbox read-only \
  "Analyze this error and identify the root cause:

Error: {error_output}

Related code context:
{code_context}

Provide:
1. Root cause analysis
2. Evidence from the code
3. Recommended fix (code diff)
4. Prevention strategy" 2>/dev/null
```
````

4. Codex の分析結果を要約して返す

## Language Protocol

- Codex への指示は英語で行う
- 結果の要約は日本語で返す

## Memory Management

作業開始時:

1. メモリディレクトリの MEMORY.md を確認し、過去のデバッグ知見を活用する

作業完了時:

1. 頻出するエラーパターンやデバッグ手法を発見した場合、メモリに記録する
2. MEMORY.md は索引として簡潔に保ち（200行以内）、詳細は別ファイルに分離する
3. 機密情報は絶対に保存しない

````

**Step 2: 検証**

Run: `head -8 .config/claude/agents/codex-debugger.md`
Expected: YAML frontmatter が正しい

**Step 3: コミット**

```bash
git add .config/claude/agents/codex-debugger.md
git commit -m "✨ feat: add codex-debugger agent for deep error analysis"
````

---

### Task 4: Delegation Rules（常時ON）

**Files:**

- Create: `.config/claude/rules/codex-delegation.md`
- Create: `.config/claude/rules/gemini-delegation.md`

**Step 1: Codex delegation rule を作成**

```markdown
# Codex CLI 委譲ルール

Codex CLI は設計判断、深い推論、複雑なデバッグを担当する。以下の場面で Codex への委譲を検討せよ。

## 委譲すべきケース

- **設計判断**: アーキテクチャ選定、モジュール構造、API設計、技術選定
- **トレードオフ分析**: 「AとBどちらが良いか」という比較・評価
- **複雑なデバッグ**: 通常の debugger エージェントで原因特定が困難な場合 → `codex-debugger` エージェント
- **コードレビュー（深い分析）**: 200行超の変更で `codex-review` スキルを使用
- **リファクタリング計画**: 大規模な構造変更の計画策定

## 委譲方法

- **分析・レビュー**: `codex-debugger` エージェント（read-only）
- **スキル実行**: `codex` スキル or `codex-review` スキル
- **直接呼び出し**: `codex exec --skip-git-repo-check -m gpt-5.3-codex --sandbox read-only "..." 2>/dev/null`

## 委譲しないケース

- 単純なコード編集、git操作、ファイル作成
- 大規模コードベース分析（→ Gemini）
- 外部リサーチ、ドキュメント検索（→ Gemini）
- マルチモーダル処理（→ Gemini）

## 言語プロトコル

Codex への指示は英語。結果はユーザーの言語（日本語）で報告。
```

**Step 2: Gemini delegation rule を作成**

```markdown
# Gemini CLI 委譲ルール

Gemini CLI は 1M コンテキストの大規模分析、Google Search grounding によるリサーチ、マルチモーダル処理を担当する。以下の場面で Gemini への委譲を検討せよ。

## 委譲すべきケース

- **コードベース全体分析**: Claude の 200K コンテキストでは不足する大規模な分析
- **外部リサーチ**: ライブラリ調査、ベストプラクティス検索、技術比較（Google Search grounding）
- **マルチモーダル処理**: PDF、動画（mp4/mov/avi）、音声（mp3/wav）、画像の読み取り・分析
- **ドキュメント分析**: 大量のドキュメントの横断的な検索・要約

## 自動トリガー

以下のファイル拡張子がタスクに含まれる場合、Gemini を自動提案:

- PDF: `.pdf`
- 動画: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`
- 音声: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`
- 画像: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`

## 委譲方法

- **サブエージェント**: `gemini-explore` エージェント（推奨 — 出力を要約して返す）
- **スキル実行**: `gemini` スキル
- **直接呼び出し**: `gemini --approval-mode plan -p "..." 2>/dev/null`
- **結果保存**: 大きな出力は `.claude/docs/research/{topic}.md` に保存

## 委譲しないケース

- 設計判断、アーキテクチャ選定（→ Codex）
- デバッグ、エラー分析（→ Codex / debugger）
- コード実装（→ Claude 直接）
- 単純なファイル読み取り（→ Read ツール）
- 数ファイルの分析（→ Claude 直接で十分）

## 言語プロトコル

Gemini への指示は英語。結果はユーザーの言語（日本語）で報告。
```

**Step 3: 検証**

Run: `ls -la .config/claude/rules/codex-delegation.md .config/claude/rules/gemini-delegation.md`
Expected: 両ファイルが存在する

**Step 4: コミット**

```bash
git add .config/claude/rules/codex-delegation.md .config/claude/rules/gemini-delegation.md
git commit -m "✨ feat: add always-on delegation rules for Codex and Gemini"
```

---

### Task 5: agent-router hook (UserPromptSubmit)

**Files:**

- Create: `.config/claude/scripts/agent-router.py`

**Step 1: スクリプトを作成**

```python
#!/usr/bin/env python3
"""Agent router hook — detects keywords in user input and suggests Codex/Gemini delegation.

Triggered by: hooks.UserPromptSubmit
Input: JSON with user prompt on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import json
import re
import sys


CODEX_KEYWORDS_JA = [
    "設計", "アーキテクチャ", "どう実装", "どうすべき",
    "トレードオフ", "比較して", "どちらがいい",
    "なぜ動かない", "原因", "バグ", "デバッグ",
    "リファクタ", "最適化", "パフォーマンス",
]

CODEX_KEYWORDS_EN = [
    "design", "architecture", "how to implement", "trade-off",
    "compare", "which is better", "why.*not working", "root cause",
    "bug", "debug", "refactor", "optimize", "performance",
]

GEMINI_KEYWORDS_JA = [
    "調べて", "リサーチ", "調査して", "検索して",
    "コードベース全体", "リポジトリ全体", "全体を分析",
    "ライブラリ", "ベストプラクティス", "ドキュメント",
    "読んで", "読み取って", "内容を確認",
]

GEMINI_KEYWORDS_EN = [
    "research", "investigate", "look up", "search for",
    "entire codebase", "whole repository", "analyze all",
    "library", "best practice", "documentation",
    "read this", "extract from",
]

MULTIMODAL_PATTERN = re.compile(
    r'\.(pdf|mp4|mov|avi|mkv|webm|mp3|wav|m4a|flac|ogg|png|jpe?g|gif|webp|svg)\b',
    re.IGNORECASE,
)


def detect_multimodal(text: str) -> list[str]:
    return list(set(MULTIMODAL_PATTERN.findall(text)))


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    prompt = data.get("user_prompt", "") or data.get("content", "")
    if not prompt or len(prompt) < 10:
        json.dump(data, sys.stdout)
        return

    # Priority 1: Multimodal files → Gemini
    mm_files = detect_multimodal(prompt)
    if mm_files:
        exts = ", ".join(f".{e}" for e in mm_files)
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"[Agent Router] マルチモーダルファイル ({exts}) が検出されました。"
                    "Gemini CLI (1Mコンテキスト) での処理を推奨します。"
                    "gemini-explore エージェントまたは gemini スキルを使用してください。"
                ),
            }
        }, sys.stdout)
        return

    # Priority 2: Codex keywords
    codex_matches = match_keywords(prompt, CODEX_KEYWORDS_JA + CODEX_KEYWORDS_EN)
    if codex_matches:
        keywords = ", ".join(codex_matches[:3])
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"[Agent Router] 設計/推論キーワード ({keywords}) が検出されました。"
                    "Codex CLI での深い分析を検討してください。"
                    "codex スキル、codex-debugger エージェント、または直接 codex exec で実行できます。"
                ),
            }
        }, sys.stdout)
        return

    # Priority 3: Gemini keywords
    gemini_matches = match_keywords(prompt, GEMINI_KEYWORDS_JA + GEMINI_KEYWORDS_EN)
    if gemini_matches:
        keywords = ", ".join(gemini_matches[:3])
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"[Agent Router] リサーチ/分析キーワード ({keywords}) が検出されました。"
                    "Gemini CLI (1Mコンテキスト + Google Search) での調査を検討してください。"
                    "gemini-explore エージェントまたは gemini スキルを使用できます。"
                ),
            }
        }, sys.stdout)
        return

    # No match — pass through
    json.dump(data, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Non-blocking — never prevent user input
        pass
```

**Step 2: 実行権限を付与して検証**

Run: `chmod +x .config/claude/scripts/agent-router.py && echo '{"user_prompt":"このアーキテクチャを設計して"}' | python3 .config/claude/scripts/agent-router.py | python3 -m json.tool`
Expected: `additionalContext` に Codex 提案が含まれる

**Step 3: コミット**

```bash
git add .config/claude/scripts/agent-router.py
git commit -m "✨ feat: add agent-router hook for auto-delegation suggestions"
```

---

### Task 6: error-to-codex hook (PostToolUse/Bash)

**Files:**

- Create: `.config/claude/scripts/error-to-codex.py`

**Step 1: スクリプトを作成**

```python
#!/usr/bin/env python3
"""Error-to-Codex hook — suggests codex-debugger when Bash errors are detected.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import json
import re
import sys


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
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"[Error-to-Codex] エラーが検出されました: {error_match}\n"
                    "codex-debugger エージェントを使用してこのエラーの根本原因を分析できます。\n"
                    "コマンド: " + command[:100]
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

**Step 2: 検証**

Run: `echo '{"tool_name":"Bash","tool_input":{"command":"python3 app.py"},"tool_output":"Traceback (most recent call last):\n  File \"app.py\", line 1\nSyntaxError: invalid syntax"}' | python3 .config/claude/scripts/error-to-codex.py | python3 -m json.tool`
Expected: `additionalContext` に codex-debugger 提案

**Step 3: コミット**

```bash
git add .config/claude/scripts/error-to-codex.py
git commit -m "✨ feat: add error-to-codex hook for auto debug suggestions"
```

---

### Task 7: suggest-gemini hook (PreToolUse/WebSearch)

**Files:**

- Create: `.config/claude/scripts/suggest-gemini.py`

**Step 1: スクリプトを作成**

```python
#!/usr/bin/env python3
"""Suggest Gemini hook — recommends Gemini CLI for complex research before WebSearch.

Triggered by: hooks.PreToolUse (WebSearch)
Input: JSON with tool_name, tool_input on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import json
import sys


SIMPLE_QUERIES = [
    "error message", "version", "changelog", "release notes",
    "stackoverflow", "github issue", "npm package",
    "エラーメッセージ", "バージョン", "リリースノート",
]

RESEARCH_KEYWORDS = [
    "documentation", "best practice", "comparison", "vs",
    "library", "framework", "tutorial", "guide",
    "architecture", "migration", "upgrade", "pattern",
    "api reference", "specification", "benchmark",
    "ドキュメント", "ベストプラクティス", "比較",
    "ライブラリ", "フレームワーク", "チュートリアル",
    "アーキテクチャ", "マイグレーション", "パターン",
]


def is_simple_query(query: str) -> bool:
    query_lower = query.lower()
    return any(sq in query_lower for sq in SIMPLE_QUERIES)


def is_research_query(query: str) -> bool:
    query_lower = query.lower()
    if any(rk in query_lower for rk in RESEARCH_KEYWORDS):
        return True
    # Complex queries (long) are likely research
    if len(query) > 100:
        return True
    return False


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    query = data.get("tool_input", {}).get("query", "") or ""

    if not query or is_simple_query(query):
        json.dump(data, sys.stdout)
        return

    if is_research_query(query):
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    "[Suggest-Gemini] 複雑なリサーチが検出されました。"
                    "Gemini CLI (1Mコンテキスト + Google Search grounding) の方が"
                    "より包括的な結果を得られる可能性があります。\n"
                    "gemini-explore エージェントまたは gemini スキルの使用を検討してください。\n"
                    "結果は .claude/docs/research/ に保存できます。"
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

**Step 2: 検証**

Run: `echo '{"tool_input":{"query":"best practices for microservice architecture patterns comparison 2026"}}' | python3 .config/claude/scripts/suggest-gemini.py | python3 -m json.tool`
Expected: Gemini 提案の `additionalContext`

**Step 3: コミット**

```bash
git add .config/claude/scripts/suggest-gemini.py
git commit -m "✨ feat: add suggest-gemini hook for complex research detection"
```

---

### Task 8: post-test-analysis hook (PostToolUse/Bash)

**Files:**

- Create: `.config/claude/scripts/post-test-analysis.py`

**Step 1: スクリプトを作成**

```python
#!/usr/bin/env python3
"""Post-test analysis hook — suggests Codex analysis when tests fail.

Triggered by: hooks.PostToolUse (Bash)
Input: JSON with tool_name, tool_input, tool_output on stdin
Output: JSON with additionalContext suggestion on stdout
"""
import json
import re
import sys


TEST_COMMANDS = [
    re.compile(r"(?:go\s+test|pytest|npm\s+test|npx\s+jest|npx\s+vitest|bun\s+test|cargo\s+test|pnpm\s+test)"),
    re.compile(r"(?:npm|pnpm|bun|yarn)\s+run\s+test"),
]

FAILURE_PATTERNS = [
    re.compile(r"FAIL", re.IGNORECASE),
    re.compile(r"FAILED"),
    re.compile(r"failures?:\s*[1-9]", re.IGNORECASE),
    re.compile(r"errors?:\s*[1-9]", re.IGNORECASE),
    re.compile(r"AssertionError"),
    re.compile(r"AssertionError"),  # Common typo variant
    re.compile(r"AssertError"),
    re.compile(r"assert.*failed", re.IGNORECASE),
    re.compile(r"expected.*but\s+(?:got|received)", re.IGNORECASE),
    re.compile(r"panic:\s"),
    re.compile(r"--- FAIL:"),  # Go test
    re.compile(r"FAILURES!"),  # Python unittest
]


def is_test_command(command: str) -> bool:
    return any(p.search(command) for p in TEST_COMMANDS)


def has_test_failure(output: str) -> bool:
    return any(p.search(output) for p in FAILURE_PATTERNS)


def count_failures(output: str) -> int:
    # Try to extract failure count
    match = re.search(r"(\d+)\s+(?:failed|failures?|errors?)", output, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Count FAIL lines
    return len(re.findall(r"(?:FAIL|--- FAIL:)", output))


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

    if not is_test_command(command):
        json.dump(data, sys.stdout)
        return

    if has_test_failure(output):
        count = count_failures(output)
        count_str = f"{count}件の" if count > 0 else ""
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"[Post-Test] {count_str}テスト失敗が検出されました。\n"
                    "codex-debugger エージェントで根本原因を分析できます。\n"
                    "または debugger エージェントで体系的にデバッグすることも可能です。"
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

**Step 2: 検証**

Run: `echo '{"tool_name":"Bash","tool_input":{"command":"go test ./..."},"tool_output":"--- FAIL: TestSomething (0.00s)\nFAIL\nexit status 1"}' | python3 .config/claude/scripts/post-test-analysis.py | python3 -m json.tool`
Expected: テスト失敗分析提案の `additionalContext`

**Step 3: コミット**

```bash
git add .config/claude/scripts/post-test-analysis.py
git commit -m "✨ feat: add post-test-analysis hook for test failure detection"
```

---

### Task 9: Knowledge Base ディレクトリ作成

**Files:**

- Create: `.config/claude/docs/research/.gitkeep`

**Step 1: ディレクトリと .gitkeep を作成**

```bash
mkdir -p .config/claude/docs/research
touch .config/claude/docs/research/.gitkeep
```

**Step 2: コミット**

```bash
git add .config/claude/docs/research/.gitkeep
git commit -m "🔧 chore: add knowledge base directory for research results"
```

---

### Task 10: settings.json を更新

**Files:**

- Modify: `.config/claude/settings.json`

**Step 1: 以下の変更を適用**

1. `permissions.allow` に `"Bash(gemini *)"` を追加
2. `hooks.UserPromptSubmit` を追加（agent-router.py）
3. `hooks.PreToolUse` に WebSearch matcher を追加（suggest-gemini.py）
4. `hooks.PostToolUse` に Bash matcher を追加（error-to-codex.py, post-test-analysis.py）

変更後の hooks セクション:

```jsonc
{
  "permissions": {
    "allow": [
      // ... 既存のエントリ ...
      "Bash(gemini *)", // ← 追加
    ],
  },
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/.claude/scripts/agent-router.py",
          },
        ],
      },
    ],
    "SessionStart": [
      // ... 既存のまま ...
    ],
    "PreToolUse": [
      {
        "matcher": "Bash(git commit *)",
        "hooks": [
          {
            "type": "command",
            "command": "node $HOME/.claude/scripts/pre-commit-check.js",
          },
        ],
      },
      {
        "matcher": "WebSearch",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/.claude/scripts/suggest-gemini.py",
          },
        ],
      },
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "node $HOME/.claude/scripts/auto-format.js",
          },
          {
            "type": "command",
            "command": "node $HOME/.claude/scripts/suggest-compact.js",
          },
        ],
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/.claude/scripts/error-to-codex.py",
          },
          {
            "type": "command",
            "command": "python3 $HOME/.claude/scripts/post-test-analysis.py",
          },
        ],
      },
    ],
    // ... Stop, SessionEnd, PreCompact, Notification は既存のまま ...
  },
}
```

**Step 2: JSON 構文検証**

Run: `python3 -c "import json; json.load(open('.config/claude/settings.json'))"`
Expected: エラーなし

**Step 3: コミット**

```bash
git add .config/claude/settings.json
git commit -m "🔧 chore: add multi-model hooks and gemini permission to settings"
```

---

### Task 11: workflow-guide.md を更新

**Files:**

- Modify: `.config/claude/references/workflow-guide.md`

**Step 1: エージェントルーティング表に追加**

エージェントルーティング表（`## エージェントルーティング` セクション）に以下を追加:

```markdown
| Gemini リサーチ | `gemini-explore` | 1Mコンテキスト分析、外部リサーチ、マルチモーダル |
| Codex デバッグ | `codex-debugger` | Codex による深いエラー分析・根本原因特定 |
```

ルーティングルールの末尾に追加:

```markdown
6. 大規模コードベース分析・外部リサーチ・マルチモーダル処理は `gemini-explore` に委譲
7. 通常の `debugger` で困難なエラー分析は `codex-debugger` に委譲（Codex の深い推論を活用）
```

**Step 2: コミット**

```bash
git add .config/claude/references/workflow-guide.md
git commit -m "📝 docs: add gemini-explore and codex-debugger to routing table"
```

---

### Task 12: session-load.js に Gemini 検出を追加

**Files:**

- Modify: `.config/claude/scripts/session-load.js`

**Step 1: detectTools の AI tools セクションに gemini を追加**

`'AI tools': ['codex']` → `'AI tools': ['codex', 'gemini']` に変更。

**Step 2: コミット**

```bash
git add .config/claude/scripts/session-load.js
git commit -m "🔧 chore: detect gemini CLI in session-load"
```

---

### Task 13: 統合テスト

**Step 1: 全 hook スクリプトの動作確認**

```bash
# agent-router: Codex keyword
echo '{"user_prompt":"このモジュールのアーキテクチャを設計したい"}' | python3 .config/claude/scripts/agent-router.py | python3 -m json.tool

# agent-router: Gemini keyword
echo '{"user_prompt":"このライブラリについて調べてほしい"}' | python3 .config/claude/scripts/agent-router.py | python3 -m json.tool

# agent-router: Multimodal
echo '{"user_prompt":"この設計書.pdfを読んで要約して"}' | python3 .config/claude/scripts/agent-router.py | python3 -m json.tool

# agent-router: No match (pass through)
echo '{"user_prompt":"hello"}' | python3 .config/claude/scripts/agent-router.py | python3 -m json.tool

# error-to-codex
echo '{"tool_name":"Bash","tool_input":{"command":"npm run build"},"tool_output":"npm ERR! Failed to compile"}' | python3 .config/claude/scripts/error-to-codex.py | python3 -m json.tool

# suggest-gemini
echo '{"tool_input":{"query":"React vs Vue comparison best practices 2026"}}' | python3 .config/claude/scripts/suggest-gemini.py | python3 -m json.tool

# post-test-analysis
echo '{"tool_name":"Bash","tool_input":{"command":"pytest"},"tool_output":"FAILED tests/test_main.py::test_something - AssertionError"}' | python3 .config/claude/scripts/post-test-analysis.py | python3 -m json.tool
```

Expected: 全コマンドが正常な JSON を出力し、適切な `additionalContext` が含まれる

**Step 2: settings.json 構文確認**

```bash
python3 -c "import json; json.load(open('.config/claude/settings.json')); print('OK')"
```

**Step 3: 全ファイルの存在確認**

```bash
ls -la .config/claude/skills/gemini/SKILL.md \
       .config/claude/agents/gemini-explore.md \
       .config/claude/agents/codex-debugger.md \
       .config/claude/rules/codex-delegation.md \
       .config/claude/rules/gemini-delegation.md \
       .config/claude/scripts/agent-router.py \
       .config/claude/scripts/error-to-codex.py \
       .config/claude/scripts/suggest-gemini.py \
       .config/claude/scripts/post-test-analysis.py \
       .config/claude/docs/research/.gitkeep
```

Expected: 10ファイルすべてが存在

**Step 4: 最終コミット（全体タグ）**

全タスクが個別コミット済みの場合はスキップ。まとめコミットが必要な場合:

```bash
git add -A
git commit -m "✨ feat: complete multi-model orchestration layer (Codex + Gemini)"
```
