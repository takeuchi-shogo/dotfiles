#!/usr/bin/env python3
"""Skill security scanner — G1 (static) + G2 (semantic) pattern detection.

Scans skill directories for dangerous code patterns and prompt injection vectors.
Based on arXiv:2603.11808 Four-Stage Verification Pipeline (G1-G4).

Usage:
    python3 skill-security-scan.py <path-to-skill-directory>

Exit codes:
    0 = PASS (no CRITICAL/HIGH findings)
    1 = FAIL (CRITICAL or HIGH findings detected)
    2 = Error (invalid input, scan failure)
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

# ---------------------------------------------------------------------------
# G1: Static analysis patterns — dangerous code in scripts
# ---------------------------------------------------------------------------
G1_PATTERNS = [
    # CRITICAL: dynamic code execution
    (r"\beval\s*\(", "CRITICAL", "eval()", "動的コード実行 (eval)"),
    (r"\bexec\s*\(", "CRITICAL", "exec()", "動的コード実行 (exec)"),
    (r"\bos\.system\s*\(", "CRITICAL", "os.system()", "シェル実行 (os.system)"),
    (
        r"\bshutil\.rmtree\s*\(",
        "CRITICAL",
        "shutil.rmtree()",
        "再帰削除 (shutil.rmtree)",
    ),
    # HIGH: subprocess / network / fs destruction
    (r"\bsubprocess\.\w+\s*\(", "HIGH", "subprocess.*", "サブプロセス実行"),
    (r"\bos\.remove\s*\(", "HIGH", "os.remove()", "ファイル削除 (os.remove)"),
    (r"\bos\.unlink\s*\(", "HIGH", "os.unlink()", "ファイル削除 (os.unlink)"),
    (
        r"\burllib\.request\.\w+\s*\(",
        "HIGH",
        "urllib.request",
        "ネットワークアクセス (urllib)",
    ),
    (r"\brequests\.\w+\s*\(", "HIGH", "requests.*", "ネットワークアクセス (requests)"),
    (r"\bsocket\.\w+\s*\(", "HIGH", "socket.*", "ソケット通信 (socket)"),
    (
        r"""(?:subprocess|os\.system|os\.popen|`).*\bcurl\b""",
        "HIGH",
        "curl",
        "外部コマンド (curl)",
    ),
    (
        r"""(?:subprocess|os\.system|os\.popen|`).*\bwget\b""",
        "HIGH",
        "wget",
        "外部コマンド (wget)",
    ),
]

# G1 対象拡張子
G1_EXTENSIONS = {".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".rb", ".pl"}

# ---------------------------------------------------------------------------
# G2: Semantic classification patterns — prompt injection vectors
# ---------------------------------------------------------------------------
G2_PATTERNS = [
    # CRITICAL: invisible / deceptive characters
    (
        r"[\u200b\u200c\u200d\ufeff]",
        "CRITICAL",
        "zero-width-char",
        "ゼロ幅文字 (不可視テキスト注入)",
    ),
    (
        r"[\u202a-\u202e\u2066-\u2069]",
        "CRITICAL",
        "rtl-override",
        "RTL/LTR override (視覚的偽装)",
    ),
    (r"\x00", "CRITICAL", "null-byte", "Null バイト注入"),
    # HIGH: encoding tricks
    (
        r"\bbase64\.b64decode\s*\(",
        "HIGH",
        "base64-decode",
        "Base64 デコード (隠しペイロード)",
    ),
    (r"\x1b\[", "HIGH", "ansi-escape", "ANSI エスケープシーケンス"),
    # MEDIUM: hidden instruction tags in markdown
    (
        r"<!--\s*(system|assistant|user)\s*:",
        "MEDIUM",
        "hidden-instruction",
        "隠し命令タグ (HTML コメント)",
    ),
    (r"\[hidden\]", "MEDIUM", "hidden-tag", "隠しタグ ([hidden])"),
]

# G2 対象: すべてのテキストファイル
G2_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json", ".toml"} | G1_EXTENSIONS

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# Comment prefixes by extension — G1 patterns in comment lines are skipped
_COMMENT_PREFIXES = {
    ".py": ("#",),
    ".sh": ("#",),
    ".bash": ("#",),
    ".zsh": ("#",),
    ".rb": ("#",),
    ".pl": ("#",),
    ".js": ("//", "*"),
    ".ts": ("//", "*"),
}


def _is_comment_line(line, ext):
    """Return True if the line is a comment in the given language."""
    prefixes = _COMMENT_PREFIXES.get(ext)
    if not prefixes:
        return False
    stripped = line.lstrip()
    return any(stripped.startswith(p) for p in prefixes)


def scan_file(filepath, findings):
    """Scan a single file for G1/G2 patterns."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in G1_EXTENSIONS and ext not in G2_EXTENSIONS:
        return

    try:
        size = os.path.getsize(filepath)
        if size > MAX_FILE_SIZE:
            return
        with open(filepath, "rb") as f:
            raw = f.read(512)
            if b"\x00" in raw and ext not in G2_EXTENSIONS:
                return  # likely binary
    except OSError:
        return

    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return

    patterns = []
    if ext in G1_EXTENSIONS:
        patterns.extend(("G1", p) for p in G1_PATTERNS)
    if ext in G2_EXTENSIONS:
        patterns.extend(("G2", p) for p in G2_PATTERNS)

    for line_num, line in enumerate(lines, 1):
        is_comment = _is_comment_line(line, ext)
        for category, (regex, severity, pattern_name, message) in patterns:
            if category == "G1" and is_comment:
                continue
            if re.search(regex, line):
                findings.append(
                    {
                        "file": filepath,
                        "line": line_num,
                        "severity": severity,
                        "category": category,
                        "pattern": pattern_name,
                        "message": message,
                    }
                )


def scan_directory(skill_dir):
    """Scan entire skill directory and return findings."""
    findings = []
    files_scanned = 0

    for root, _dirs, files in os.walk(skill_dir):
        # skip hidden directories
        _dirs[:] = [d for d in _dirs if not d.startswith(".")]
        for fname in files:
            if fname.startswith("."):
                continue
            filepath = os.path.join(root, fname)
            scan_file(filepath, findings)
            files_scanned += 1

    return findings, files_scanned


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <skill-directory>", file=sys.stderr)
        sys.exit(2)

    skill_dir = sys.argv[1]
    if not os.path.isdir(skill_dir):
        print(f"Error: {skill_dir} is not a directory", file=sys.stderr)
        sys.exit(2)

    findings, files_scanned = scan_directory(skill_dir)

    # Severity counts
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    has_blocking = counts["CRITICAL"] > 0 or counts["HIGH"] > 0
    verdict = "FAIL" if has_blocking else "PASS"

    # Make paths relative to skill_dir for readability
    for f in findings:
        f["file"] = os.path.relpath(f["file"], skill_dir)

    result = {
        "verdict": verdict,
        "skill_dir": os.path.abspath(skill_dir),
        "summary": {
            "files_scanned": files_scanned,
            "critical": counts["CRITICAL"],
            "high": counts["HIGH"],
            "medium": counts["MEDIUM"],
        },
        "findings": findings,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Emit event for AutoEvolve tracking
    try:
        from session_events import emit_event

        emit_event(
            "pattern",
            {
                "type": "skill_security_scan",
                "verdict": verdict,
                "skill_dir": os.path.basename(skill_dir),
                "critical": counts["CRITICAL"],
                "high": counts["HIGH"],
            },
        )
    except ImportError:
        sys.stderr.write(
            "skill-security-scan: session_events not available, skipping emit\n"
        )

    sys.exit(1 if has_blocking else 0)


if __name__ == "__main__":
    main()
