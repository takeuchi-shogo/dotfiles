#!/usr/bin/env python3
"""task-lint.py — Obsidian Vault の task note (type: task) を決定論的に検証する。

チェック:
  (a) schema: status/due/priority の値検証
  (b) 重複: task note 間で title が重複
  (c) 二重管理: 07-Daily/*.md のリスト行に task note の title がプレーンテキストで出現
      (LayerX absorb — 決定論チェックはスクリプトに寄せる)

Usage:
  OBSIDIAN_VAULT_PATH=/path/to/vault python3 task-lint.py
  python3 task-lint.py --self-test   # 実 Vault に触れず fixture で自己検証

# ponytail: frontmatter は先頭 --- ... --- の flat key: value のみ対応。ネストした
#   mapping/list (例: tags:\n  - foo) は非対応 — 本スクリプトの対象キー
#   (type/status/due/priority/title) はすべて flat scalar のため実害なし。
# ponytail: title のプレーンテキスト一致は部分文字列一致。短い title は誤検知しうる
#   既知の制約 (厳密な単語境界判定はしない)。
"""

import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

TARGET_DIRS = ["00-Inbox", "01-Projects", "02-Areas", "07-Daily"]
VALID_STATUS = {"open", "complete"}
VALID_PRIORITY = {"high", "medium", "low"}
DUE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKILINK_RE = re.compile(r"\[\[.*?\]\]")
LIST_LINE_RE = re.compile(r"^\s*(?:[-*]\s*\[[ xX]\]|\d+\.|[-*])\s+")
MIN_DOUBLE_MGMT_TITLE_LEN = 4


def _valid_due(due: str) -> bool:
    if not DUE_RE.match(due):
        return False
    try:
        date.fromisoformat(due)
    except ValueError:
        return False
    return True


def parse_frontmatter(text: str) -> dict | None:
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return None  # closing --- が見つからない = frontmatter として不完全


def find_task_notes(vault_path: Path) -> list[tuple[Path, dict]]:
    notes = []
    for d in TARGET_DIRS:
        base = vault_path / d
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            fm = parse_frontmatter(text)
            if fm and fm.get("type") == "task":
                notes.append((path, fm))
    return notes


def title_of(path: Path, fm: dict) -> str:
    return fm.get("title") or path.stem


def rel(path: Path, vault_path: Path) -> str:
    try:
        return str(path.relative_to(vault_path))
    except ValueError:
        return str(path)


def check_schema(notes, vault_path: Path) -> list[str]:
    findings = []
    for path, fm in notes:
        p = rel(path, vault_path)
        status = fm.get("status")
        if status not in VALID_STATUS:
            findings.append(
                f"[schema] {p}: status='{status}' は open|complete のいずれでもない"
            )
        due = fm.get("due")
        if due and not _valid_due(due):
            findings.append(f"[schema] {p}: due='{due}' は YYYY-MM-DD 形式でない")
        priority = fm.get("priority")
        if priority and priority not in VALID_PRIORITY:
            findings.append(
                f"[schema] {p}: priority='{priority}' は不正な値 (high|medium|low)"
            )
    return findings


def check_duplicates(notes, vault_path: Path) -> list[str]:
    by_title: dict[str, list[Path]] = {}
    for path, fm in notes:
        by_title.setdefault(title_of(path, fm), []).append(path)
    findings = []
    for title, paths in by_title.items():
        if len(paths) > 1:
            file_list = ", ".join(rel(p, vault_path) for p in paths)
            findings.append(
                f"[duplicate] title='{title}' が複数 task note に出現: {file_list}"
            )
    return findings


def check_double_management(notes, vault_path: Path) -> list[str]:
    titles = sorted(
        t
        for t in {title_of(path, fm) for path, fm in notes}
        if len(t) >= MIN_DOUBLE_MGMT_TITLE_LEN
    )
    daily_dir = vault_path / "07-Daily"
    findings = []
    if not daily_dir.is_dir():
        return findings
    for path in sorted(daily_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not LIST_LINE_RE.match(line):
                continue
            plain = WIKILINK_RE.sub("", line)  # [[...]] リンク内は除外して判定
            for title in titles:
                if title and title in plain:
                    findings.append(
                        f"[double-management] {rel(path, vault_path)}:{lineno}: "
                        f"task note title '{title}' がプレーンテキストで出現"
                    )
    return findings


def run_lint(vault_path: Path) -> dict[str, list[str]]:
    notes = find_task_notes(vault_path)
    return {
        "schema": check_schema(notes, vault_path),
        "duplicate": check_duplicates(notes, vault_path),
        "double-management": check_double_management(notes, vault_path),
    }


def write_report(vault_path: Path, findings: dict[str, list[str]], today: str) -> Path:
    report_dir = vault_path / "00-Inbox"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"task-lint-report-{today}.md"
    lines = [
        "---",
        f'created: "{today}"',
        "tags:",
        "  - type/task-lint-report",
        "  - status/needs-action",
        "---",
        "",
        f"# Task Lint Report — {today}",
        "",
        "## サマリー",
        "",
        "| チェック項目 | 件数 |",
        "| --- | --- |",
        f"| Schema 違反 | {len(findings['schema'])} |",
        f"| 重複 | {len(findings['duplicate'])} |",
        f"| 二重管理 | {len(findings['double-management'])} |",
        "",
    ]
    for label, key in (
        ("Schema 違反", "schema"),
        ("重複", "duplicate"),
        ("二重管理", "double-management"),
    ):
        if findings[key]:
            lines.append(f"## {label}")
            lines.append("")
            lines.extend(f"- {item}" for item in findings[key])
            lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


VIOLATION_KEYS = ("schema", "duplicate")
WARNING_KEYS = ("double-management",)


def count_violations(findings: dict[str, list[str]]) -> int:
    return sum(len(findings[k]) for k in VIOLATION_KEYS)


def print_findings(findings: dict[str, list[str]]) -> int:
    total = sum(len(v) for v in findings.values())
    if total == 0:
        print("clean")
        return 0
    for items in findings.values():
        for item in items:
            print(item)
    return total


def _fixture_note(status: str, title: str, extra: str = "") -> str:
    body = "## 目的\nテスト用\n\n## 完了条件\nテスト用\n"
    return f"---\ntype: task\nstatus: {status}\ntitle: {title}\n{extra}---\n\n{body}"


def _make_fixtures(vault_path: Path) -> None:
    proj = vault_path / "01-Projects" / "proj-foo"
    proj.mkdir(parents=True)
    (vault_path / "07-Daily").mkdir(parents=True)

    fixtures = {
        "task-normal.md": _fixture_note(
            "open", "SSoTタスク", "due: 2026-08-01\npriority: medium\n"
        ),
        "task-linked.md": _fixture_note("open", "リンクのみタスク"),
        "task-badstatus.md": _fixture_note("pending", "不正ステータスタスク"),
        "task-baddue.md": _fixture_note("open", "不正期日タスク", "due: 2026/08/01\n"),
        "task-badcal.md": _fixture_note("open", "非実在日タスク", "due: 2026-13-40\n"),
        "task-badprio.md": _fixture_note(
            "open", "不正優先度タスク", "priority: urgent\n"
        ),
        "task-dup1.md": _fixture_note("open", "重複タスク"),
        "task-dup2.md": _fixture_note("open", "重複タスク"),
    }
    for filename, content in fixtures.items():
        (proj / filename).write_text(content, encoding="utf-8")

    (proj / "task-bom.md").write_text(
        "﻿" + _fixture_note("open", "BOM付きタスク", "priority: urgentbom\n"),
        encoding="utf-8",
    )
    (proj / "task-shorttitle.md").write_text(
        _fixture_note("open", "AI"), encoding="utf-8"
    )

    (vault_path / "07-Daily" / "2026-07-11.md").write_text(
        "# 2026-07-11\n\n### やることリスト\n"
        "- [ ] SSoTタスク の続きをやる\n"
        "- [ ] [[リンクのみタスク]] を確認\n"
        "- [ ] AI で調べる\n",
        encoding="utf-8",
    )


def _assert_fixture_findings(findings: dict[str, list[str]]) -> None:
    schema, dup, dm = (
        findings["schema"],
        findings["duplicate"],
        findings["double-management"],
    )
    assert any("status='pending'" in m for m in schema), "status violation not detected"
    assert any("due='2026/08/01'" in m for m in schema), (
        "due format violation not detected"
    )
    assert any("due='2026-13-40'" in m for m in schema), (
        "invalid calendar date not detected"
    )
    assert any("priority='urgent'" in m for m in schema), (
        "priority violation not detected"
    )
    assert not any("task-normal.md" in m for m in schema), (
        "false positive on valid note"
    )
    assert not any("task-linked.md" in m for m in schema), (
        "false positive on valid note"
    )
    assert any("task-bom.md" in m and "priority" in m for m in schema), (
        "BOM note must be scanned (its priority violation must surface)"
    )
    assert len(dup) == 1 and "重複タスク" in dup[0], "duplicate title not detected"
    assert any("SSoTタスク" in m for m in dm), (
        "plain-text double-management occurrence not detected"
    )
    assert not any("リンクのみタスク" in m for m in dm), (
        "wikilink-only occurrence must not be flagged"
    )
    assert not any("'AI'" in m for m in dm), (
        "short title must be guarded from double-management noise"
    )


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        vault_path = Path(tmp)
        _make_fixtures(vault_path)
        _assert_fixture_findings(run_lint(vault_path))
    print("self-test OK")


def main() -> None:
    if "--self-test" in sys.argv[1:]:
        self_test()
        return

    vault = os.environ.get("OBSIDIAN_VAULT_PATH")
    if not vault:
        print("[task-lint] OBSIDIAN_VAULT_PATH not set", file=sys.stderr)
        sys.exit(2)

    vault_path = Path(vault)
    if not vault_path.is_dir():
        print(
            f"[task-lint] OBSIDIAN_VAULT_PATH is not a directory: {vault}",
            file=sys.stderr,
        )
        sys.exit(2)

    findings = run_lint(vault_path)
    total = print_findings(findings)
    if total > 0:
        today = date.today().isoformat()
        report_path = write_report(vault_path, findings, today)
        print(f"[task-lint] Report saved: {report_path}", file=sys.stderr)
    sys.exit(1 if count_violations(findings) > 0 else 0)


if __name__ == "__main__":
    main()
