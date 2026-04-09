#!/usr/bin/env python3
"""Claude Code トークン使用量分析スクリプト

セッション開始時にコンテキストウィンドウに注入されるファイル群を分析し、
トークン消費の「犯人」を特定する。

カテゴリ:
  - always-loaded: CLAUDE.md, MEMORY.md, settings.json (常時注入)
  - on-access:     個別メモリファイル (アクセス時のみ)
  - on-invoke:     skills, agents (呼び出し時のみ)
  - reference:     references/, rules/ (条件付きロード)

Usage:
  python3 scripts/runtime/token-audit.py [top_n]
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ── 定数 ──────────────────────────────────────────────

DOTFILES = Path(os.environ.get("DOTFILES", Path.home() / "dotfiles"))
CLAUDE_CONFIG = DOTFILES / ".config" / "claude"
CLAUDE_HOME = Path.home() / ".claude"
PROJECT_MEMORY = CLAUDE_HOME / "projects" / "-Users-takeuchishougo-dotfiles" / "memory"

# Claude の 1M context window (Opus 4.6)
CONTEXT_WINDOW = 1_000_000

# カラーコード
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
BAR = "\033[44m"  # blue bg


# ── トークン推定 ──────────────────────────────────────


def estimate_tokens(text: str) -> int:
    """CJK 混在テキストのトークン数を推定する。

    Claude の tokenizer (SentencePiece) の実測に基づく近似:
    - ASCII/ラテン文字: ~4 chars/token
    - CJK/日本語: ~1.5 chars/token
    - 記号・空白: ~2 chars/token
    """
    if not text:
        return 0

    cjk = 0
    ascii_chars = 0
    other = 0

    for ch in text:
        cp = ord(ch)
        if cp <= 127:
            ascii_chars += 1
        elif (
            (0x3000 <= cp <= 0x9FFF)
            or (0xF900 <= cp <= 0xFAFF)
            or (0xFF00 <= cp <= 0xFFEF)
        ):
            cjk += 1
        else:
            other += 1

    return int(ascii_chars / 4 + cjk / 1.5 + other / 2)


def file_tokens(path: Path) -> int:
    """ファイルのトークン数を推定する。読み取り不可の場合は 0 を返す。"""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return estimate_tokens(text)
    except OSError as e:
        print(f"  {DIM}[WARN] {path}: {e}{RESET}", file=sys.stderr)
        return 0


def file_bytes(path: Path) -> int:
    """ファイルサイズを取得する。取得不可の場合は 0 を返す。"""
    try:
        return path.stat().st_size
    except OSError as e:
        print(f"  {DIM}[WARN] {path}: {e}{RESET}", file=sys.stderr)
        return 0


# ── データ構造 ────────────────────────────────────────


@dataclass
class FileEntry:
    path: Path
    tokens: int
    bytes: int
    category: str

    @property
    def relative(self) -> str:
        try:
            return str(self.path.relative_to(DOTFILES))
        except ValueError:
            try:
                return str(self.path.relative_to(Path.home()))
            except ValueError:
                return str(self.path)


@dataclass
class Category:
    name: str
    label: str
    load_timing: str  # always / on-access / on-invoke / reference
    entries: list[FileEntry] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return sum(e.tokens for e in self.entries)

    @property
    def total_bytes(self) -> int:
        return sum(e.bytes for e in self.entries)

    @property
    def file_count(self) -> int:
        return len(self.entries)


# ── スキャナ ──────────────────────────────────────────


def scan_directory(
    directory: Path, pattern: str = "*.md"
) -> list[tuple[Path, int, int]]:
    """ディレクトリ内のファイルをスキャンし (path, tokens, bytes) を返す。"""
    results: list[tuple[Path, int, int]] = []
    if not directory.exists():
        return results
    for p in sorted(directory.rglob(pattern)):
        if p.is_file():
            tokens = file_tokens(p)
            size = file_bytes(p)
            results.append((p, tokens, size))
    return results


def build_categories() -> list[Category]:
    categories: list[Category] = []

    # 1. CLAUDE.md (常時ロード)
    claude_md = Category("claude-md", "CLAUDE.md (global + project)", "always")
    seen_paths: set[Path] = set()
    for path in [
        CLAUDE_CONFIG / "CLAUDE.md",
        DOTFILES / "CLAUDE.md",
        DOTFILES / ".claude" / "CLAUDE.md",
    ]:
        resolved = path.resolve()
        if resolved.exists() and resolved not in seen_paths:
            seen_paths.add(resolved)
            claude_md.entries.append(
                FileEntry(path, file_tokens(path), file_bytes(path), "claude-md")
            )
    # project-level CLAUDE.md
    for p in DOTFILES.rglob("CLAUDE.md"):
        resolved = p.resolve()
        if resolved not in seen_paths and ".git" not in str(p):
            seen_paths.add(resolved)
            claude_md.entries.append(
                FileEntry(p, file_tokens(p), file_bytes(p), "claude-md")
            )
    categories.append(claude_md)

    # 2. MEMORY.md + 個別メモリ
    memory_index = Category(
        "memory-index", "MEMORY.md (index, always loaded)", "always"
    )
    memory_md = PROJECT_MEMORY / "MEMORY.md"
    if memory_md.exists():
        memory_index.entries.append(
            FileEntry(
                memory_md, file_tokens(memory_md), file_bytes(memory_md), "memory-index"
            )
        )
    categories.append(memory_index)

    memory_files = Category("memory-files", "Memory files (on access)", "on-access")
    for p, tokens, size in scan_directory(PROJECT_MEMORY):
        if p.name != "MEMORY.md":
            memory_files.entries.append(FileEntry(p, tokens, size, "memory-files"))
    categories.append(memory_files)

    # 3. Skills
    skills = Category("skills", "Skills (on invoke)", "on-invoke")
    for p, tokens, size in scan_directory(CLAUDE_CONFIG / "skills", "*.md"):
        skills.entries.append(FileEntry(p, tokens, size, "skills"))
    categories.append(skills)

    # 4. Agents
    agents = Category("agents", "Agents (on invoke)", "on-invoke")
    for p, tokens, size in scan_directory(CLAUDE_CONFIG / "agents"):
        agents.entries.append(FileEntry(p, tokens, size, "agents"))
    categories.append(agents)

    # 5. References
    refs = Category("references", "References (conditional)", "reference")
    for p, tokens, size in scan_directory(CLAUDE_CONFIG / "references"):
        refs.entries.append(FileEntry(p, tokens, size, "references"))
    categories.append(refs)

    # 6. Rules
    rules = Category("rules", "Rules (conditional)", "reference")
    for p, tokens, size in scan_directory(CLAUDE_CONFIG / "rules"):
        rules.entries.append(FileEntry(p, tokens, size, "rules"))
    categories.append(rules)

    # 7. Settings.json (hooks 含む)
    settings = Category("settings", "settings.json + hooks", "always")
    for name in ("settings.json", "settings.local.json"):
        settings_path = CLAUDE_CONFIG / name
        if settings_path.exists():
            settings.entries.append(
                FileEntry(
                    settings_path,
                    file_tokens(settings_path),
                    file_bytes(settings_path),
                    "settings",
                )
            )
    categories.append(settings)

    # 8. Scripts (hooks から参照 — 実行されるが直接ロードはされない)
    hook_scripts = Category(
        "scripts", "Hook scripts (executed, not injected)", "reference"
    )
    for ext in ("*.py", "*.sh"):
        for p, tokens, size in scan_directory(CLAUDE_CONFIG / "scripts", ext):
            hook_scripts.entries.append(FileEntry(p, tokens, size, "scripts"))
    categories.append(hook_scripts)

    return categories


# ── レポート ──────────────────────────────────────────


def bar_chart(value: int, max_value: int, width: int = 40) -> str:
    if max_value == 0:
        return ""
    filled = int(value / max_value * width)
    return f"{BAR}{' ' * filled}{RESET}{'.' * (width - filled)}"


def format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_bytes(n: int) -> str:
    if n >= 1_048_576:
        return f"{n / 1_048_576:.1f}MB"
    if n >= 1024:
        return f"{n / 1024:.1f}KB"
    return f"{n}B"


def severity_color(tokens: int) -> str:
    if tokens >= 10_000:
        return RED
    if tokens >= 3_000:
        return YELLOW
    return GREEN


def print_report(categories: list[Category], top_n: int = 15) -> None:
    total_all = sum(c.total_tokens for c in categories)
    total_always = sum(c.total_tokens for c in categories if c.load_timing == "always")

    print(f"\n{BOLD}{'=' * 72}")
    print("  Claude Code Token Audit")
    print(f"{'=' * 72}{RESET}\n")

    # サマリ
    pct_always = total_always / CONTEXT_WINDOW * 100
    pct_all = total_all / CONTEXT_WINDOW * 100

    print(f"  {BOLD}常時ロード (セッション開始時){RESET}")
    c = severity_color(total_always)
    cw = format_tokens(CONTEXT_WINDOW)
    t = format_tokens(total_always)
    print(f"    トークン: {c}{t}{RESET} / {cw} ({pct_always:.2f}%)")
    print(f"    {bar_chart(total_always, CONTEXT_WINDOW, 50)}")
    print()
    print(f"  {BOLD}全リソース合計 (最大潜在消費){RESET}")
    c = severity_color(total_all)
    t = format_tokens(total_all)
    print(f"    トークン: {c}{t}{RESET} / {cw} ({pct_all:.1f}%)")
    print(f"    {bar_chart(total_all, CONTEXT_WINDOW, 50)}")
    print()

    # カテゴリ別
    print(f"  {BOLD}{'─' * 72}")
    print("  カテゴリ別内訳")
    print(f"  {'─' * 72}{RESET}")
    print()

    sorted_cats = sorted(categories, key=lambda c: c.total_tokens, reverse=True)
    max_cat_tokens = sorted_cats[0].total_tokens if sorted_cats else 1

    timing_labels = {
        "always": f"{RED}常時{RESET}",
        "on-access": f"{YELLOW}アクセス時{RESET}",
        "on-invoke": f"{CYAN}呼出時{RESET}",
        "reference": f"{DIM}参照時{RESET}",
    }

    for cat in sorted_cats:
        if cat.total_tokens == 0:
            continue
        color = severity_color(cat.total_tokens)
        timing = timing_labels.get(cat.load_timing, cat.load_timing)
        print(f"  {timing}  {cat.label}")
        tk = f"{format_tokens(cat.total_tokens):>8}"
        bk = format_bytes(cat.total_bytes)
        fc = cat.file_count
        print(f"    {color}{tk}{RESET} tokens  |  {fc} files  |  {bk}")
        print(f"    {bar_chart(cat.total_tokens, max_cat_tokens, 50)}")
        print()

    # Top N 犯人ファイル
    all_entries: list[FileEntry] = []
    for cat in categories:
        all_entries.extend(cat.entries)
    all_entries.sort(key=lambda e: e.tokens, reverse=True)

    print(f"  {BOLD}{'─' * 72}")
    print(f"  Top {top_n} 犯人ファイル")
    print(f"  {'─' * 72}{RESET}")
    print()
    print(f"  {'#':>3}  {'Tokens':>8}  {'Bytes':>8}  {'Category':<15}  Path")
    print(f"  {'─' * 3}  {'─' * 8}  {'─' * 8}  {'─' * 15}  {'─' * 30}")

    for i, entry in enumerate(all_entries[:top_n], 1):
        color = severity_color(entry.tokens)
        tk = f"{format_tokens(entry.tokens):>8}"
        bk = f"{format_bytes(entry.bytes):>8}"
        cat_name = f"{entry.category:<15}"
        print(
            f"  {color}{i:>3}{RESET}  {color}{tk}{RESET}"
            f"  {bk}  {cat_name}  {entry.relative}"
        )

    # カテゴリごと Top 3
    print(f"\n  {BOLD}{'─' * 72}")
    print("  カテゴリ別 Top 3")
    print(f"  {'─' * 72}{RESET}")

    for cat in sorted_cats:
        if cat.total_tokens == 0 or len(cat.entries) <= 1:
            continue
        top3 = sorted(cat.entries, key=lambda e: e.tokens, reverse=True)[:3]
        print(f"\n  {BOLD}{cat.label}{RESET}")
        for j, entry in enumerate(top3, 1):
            color = severity_color(entry.tokens)
            total = cat.total_tokens
            pct = entry.tokens / total * 100 if total > 0 else 0
            tk = f"{format_tokens(entry.tokens):>7}"
            rel = entry.relative
            print(f"    {j}. {color}{tk}{RESET} ({pct:4.1f}%)  {rel}")

    # 推奨アクション
    print(f"\n  {BOLD}{'─' * 72}")
    print("  推奨アクション")
    print(f"  {'─' * 72}{RESET}")

    recommendations: list[str] = []

    if total_always > 15_000:
        t = format_tokens(total_always)
        recommendations.append(
            f"{RED}[HIGH]{RESET} 常時ロード {t} — CLAUDE.md/MEMORY.md の圧縮を検討"
        )

    big_skills = [e for e in all_entries if e.category == "skills" and e.tokens > 3_000]
    if big_skills:
        names = ", ".join(e.path.parent.name for e in big_skills[:5])
        n = len(big_skills)
        recommendations.append(f"{YELLOW}[MED]{RESET}  大きいスキル ({n} 件): {names}")

    big_refs = [
        e for e in all_entries if e.category == "references" and e.tokens > 5_000
    ]
    if big_refs:
        names = ", ".join(e.path.name for e in big_refs[:5])
        n = len(big_refs)
        recommendations.append(
            f"{YELLOW}[MED]{RESET}  大きいリファレンス ({n} 件): {names}"
        )

    big_memory = [
        e for e in all_entries if e.category == "memory-files" and e.tokens > 1_000
    ]
    if big_memory:
        n = len(big_memory)
        recommendations.append(
            f"{YELLOW}[MED]{RESET}  大きいメモリ ({n} 件) — 整理・統合を検討"
        )

    memory_count = sum(1 for e in all_entries if e.category == "memory-files")
    if memory_count > 30:
        recommendations.append(
            f"{YELLOW}[MED]{RESET}  メモリ {memory_count} 件 — 陳腐化分の削除を検討"
        )

    if not recommendations:
        recommendations.append(
            f"{GREEN}[OK]{RESET}  特に問題なし — トークン使用量は健全です"
        )

    for rec in recommendations:
        print(f"    {rec}")

    # フッター
    print(f"\n  {DIM}推定方法: ASCII ~4chars/token, CJK ~1.5chars/token")
    print(f"  Context window: {format_tokens(CONTEXT_WINDOW)} (Opus 4.6){RESET}")
    print()


# ── メイン ────────────────────────────────────────────


def main() -> None:
    top_n = 15
    if len(sys.argv) > 1:
        try:
            top_n = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [top_n]", file=sys.stderr)
            sys.exit(1)

    categories = build_categories()
    print_report(categories, top_n)


if __name__ == "__main__":
    main()
