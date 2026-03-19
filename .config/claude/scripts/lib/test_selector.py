#!/usr/bin/env python3
"""Selective test runner — find and run only tests related to changed files.

Part of the Stripe Minions integration: instead of running the full test suite
every time, identify which tests are relevant to the changed files and run
those first for fast feedback.

Usage:
    python3 -m scripts.lib.test_selector          # standalone
    from scripts.lib.test_selector import select_tests  # as library
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

# ============================================================================
# Test file naming conventions (shared with completion-gate.py)
# ============================================================================

_TEST_FILE_MAPPINGS: dict[str, list[str]] = {
    ".ts": [".test.ts", ".spec.ts"],
    ".tsx": [".test.tsx", ".spec.tsx"],
    ".js": [".test.js", ".spec.js"],
    ".jsx": [".test.jsx", ".spec.jsx"],
    ".go": ["_test.go"],
    ".py": ["test_{name}.py", "{name}_test.py"],
    ".rs": [],  # Rust uses inline #[cfg(test)]
}

# Extensions that are never source code (skip when searching for related tests)
_SKIP_EXTENSIONS = frozenset(
    (".md", ".json", ".yaml", ".yml", ".toml", ".lock", ".css", ".html", ".svg", ".png")
)

# Patterns that mark a file as a test file itself
_TEST_SUFFIXES = (
    "_test.go",
    ".test.ts",
    ".test.tsx",
    ".test.js",
    ".test.jsx",
    ".spec.ts",
    ".spec.tsx",
    ".spec.js",
    ".spec.jsx",
    "_test.py",
)


def _log(msg: str) -> None:
    """Write a diagnostic message to stderr."""
    print(f"[test-selector] {msg}", file=sys.stderr)


# ============================================================================
# Changed file detection
# ============================================================================


def get_changed_files(cwd: str | None = None) -> list[str]:
    """Get deduplicated list of changed files (unstaged + staged).

    Uses ``git diff --name-only HEAD`` for unstaged changes and
    ``git diff --name-only --cached`` for staged changes.

    Returns:
        Sorted, deduplicated list of relative file paths.
    """
    work_dir = cwd or os.getcwd()
    files: set[str] = set()

    for cmd in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--name-only", "--cached"],
    ):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=work_dir,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if line:
                        files.add(line)
            else:
                _log(f"git command failed (rc={result.returncode}): {' '.join(cmd)}")
        except subprocess.TimeoutExpired:
            _log(f"git command timed out: {' '.join(cmd)}")
        except FileNotFoundError:
            _log("git not found on PATH")

    return sorted(files)


# ============================================================================
# Related test discovery
# ============================================================================


def _is_test_file(filepath: str) -> bool:
    """Return True if *filepath* looks like a test file."""
    basename = os.path.basename(filepath)
    if basename.startswith("test_") and filepath.endswith(".py"):
        return True
    return any(filepath.endswith(suffix) for suffix in _TEST_SUFFIXES)


def find_related_tests(
    changed_files: list[str],
    project_root: str | None = None,
) -> list[str]:
    """Find test files that correspond to the given changed source files.

    Strategy:
      1. If a changed file **is** a test file, include it directly.
      2. For each source file, look up ``_TEST_FILE_MAPPINGS`` by extension
         and check the same directory + ``__tests__/`` subdirectory.

    Args:
        changed_files: Relative paths (from repo root) of changed files.
        project_root: Absolute path to the project root.  Defaults to cwd.

    Returns:
        Sorted, deduplicated list of test file paths (relative) that exist
        on disk.
    """
    root = project_root or os.getcwd()
    tests: set[str] = set()

    for filepath in changed_files:
        # 1. Test file itself — include directly if it exists
        if _is_test_file(filepath):
            if os.path.exists(os.path.join(root, filepath)):
                tests.add(filepath)
            continue

        # 2. Skip non-source files
        _base, ext = os.path.splitext(filepath)
        if ext in _SKIP_EXTENSIONS:
            continue

        suffixes = _TEST_FILE_MAPPINGS.get(ext)
        if suffixes is None:
            continue

        name = os.path.basename(_base)
        dirpath = os.path.dirname(filepath)

        for suffix in suffixes:
            if "{name}" in suffix:
                test_name = suffix.replace("{name}", name)
            else:
                test_name = name + suffix

            # Same directory
            candidate = os.path.join(dirpath, test_name) if dirpath else test_name
            if os.path.exists(os.path.join(root, candidate)):
                tests.add(candidate)

            # __tests__/ subdirectory
            tests_subdir = (
                os.path.join(dirpath, "__tests__") if dirpath else "__tests__"
            )
            candidate_sub = os.path.join(tests_subdir, test_name)
            if os.path.exists(os.path.join(root, candidate_sub)):
                tests.add(candidate_sub)

    return sorted(tests)


# ============================================================================
# Test runner detection
# ============================================================================


def _read_package_json(project_root: str) -> dict | None:
    """Read and parse package.json, returning None on any error."""
    pkg_path = os.path.join(project_root, "package.json")
    if not os.path.exists(pkg_path):
        return None
    try:
        with open(pkg_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        _log(f"failed to read package.json: {exc}")
        return None


def _detect_node_runner(project_root: str) -> str | None:
    """Detect jest or vitest from package.json devDependencies / dependencies."""
    pkg = _read_package_json(project_root)
    if pkg is None:
        return None

    all_deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies"):
        all_deps.update(pkg.get(key, {}))

    if "vitest" in all_deps:
        return "vitest"
    if "jest" in all_deps:
        return "jest"

    # Fallback: check scripts.test
    test_script = pkg.get("scripts", {}).get("test", "")
    if "vitest" in test_script:
        return "vitest"
    if "jest" in test_script:
        return "jest"

    return None


def _detect_pkg_manager(project_root: str) -> str:
    """Detect package manager (bun / pnpm / npm)."""
    if os.path.exists(os.path.join(project_root, "bun.lockb")):
        return "bunx"
    if os.path.exists(os.path.join(project_root, "pnpm-lock.yaml")):
        return "pnpx"
    return "npx"


def _detect_full_test_command(project_root: str) -> str | None:
    """Detect the full-suite test command for the project.

    Mirrors the logic in completion-gate.py ``_detect_test_command``.
    """
    pkg = _read_package_json(project_root)
    if pkg is not None:
        if "test" in pkg.get("scripts", {}):
            if os.path.exists(os.path.join(project_root, "bun.lockb")):
                return "bun test"
            if os.path.exists(os.path.join(project_root, "pnpm-lock.yaml")):
                return "pnpm test"
            return "npm test"

    if os.path.exists(os.path.join(project_root, "go.mod")):
        return "go test ./..."

    if os.path.exists(os.path.join(project_root, "pyproject.toml")) or os.path.exists(
        os.path.join(project_root, "conftest.py")
    ):
        return "python3 -m pytest --tb=short -q"

    if os.path.exists(os.path.join(project_root, "Cargo.toml")):
        return "cargo test"

    return None


# ============================================================================
# Selective command building
# ============================================================================


def build_selective_test_command(
    test_files: list[str],
    project_root: str,
) -> str | None:
    """Build a test command that runs only the specified test files.

    Supported runners:
      - **Go**: ``go test ./path/to/package/...`` (deduplicated packages)
      - **Python**: ``python3 -m pytest path/to/test1.py ... --tb=short -q``
      - **Node.js (jest)**: ``npx jest --findRelatedTests path/to/file1.ts ...``
      - **Node.js (vitest)**: ``npx vitest run path/to/test1.ts ...``
      - **Rust**: ``cargo test --test test_name`` (extract test names)

    Args:
        test_files: Relative paths to the test files.
        project_root: Absolute path to the project root.

    Returns:
        Shell command string, or ``None`` if the runner can't be determined.
    """
    if not test_files:
        return None

    # Classify files by extension
    exts = {os.path.splitext(f)[1] for f in test_files}

    # Go
    if exts & {".go"}:
        go_files = [f for f in test_files if f.endswith(".go")]
        packages: set[str] = set()
        for f in go_files:
            pkg_dir = os.path.dirname(f) or "."
            packages.add(f"./{pkg_dir}/...")
        return "go test " + " ".join(sorted(packages))

    # Python
    if exts & {".py"}:
        py_files = [f for f in test_files if f.endswith(".py")]
        return "python3 -m pytest " + " ".join(py_files) + " --tb=short -q"

    # Node.js (TypeScript / JavaScript)
    if exts & {".ts", ".tsx", ".js", ".jsx"}:
        node_runner = _detect_node_runner(project_root)
        if node_runner is None:
            return None

        node_files = [
            f
            for f in test_files
            if os.path.splitext(f)[1] in (".ts", ".tsx", ".js", ".jsx")
        ]
        pkg_mgr = _detect_pkg_manager(project_root)

        if node_runner == "jest":
            return f"{pkg_mgr} jest --findRelatedTests " + " ".join(node_files)
        if node_runner == "vitest":
            return f"{pkg_mgr} vitest run " + " ".join(node_files)

    # Rust
    if exts & {".rs"}:
        rs_files = [f for f in test_files if f.endswith(".rs")]
        test_names: list[str] = []
        for f in rs_files:
            # tests/foo.rs  -> --test foo
            # tests/bar/mod.rs -> --test bar  (convention)
            basename = os.path.splitext(os.path.basename(f))[0]
            if basename == "mod":
                # Use parent directory name
                parent = os.path.basename(os.path.dirname(f))
                if parent and parent != "tests":
                    test_names.append(parent)
            elif basename not in ("lib", "main"):
                test_names.append(basename)
        if test_names:
            # cargo test supports multiple --test flags
            test_flags = " ".join(f"--test {name}" for name in sorted(set(test_names)))
            return f"cargo test {test_flags}"

    return None


# ============================================================================
# Main entry point
# ============================================================================


def select_tests(
    project_root: str | None = None,
) -> tuple[str | None, str | None]:
    """Determine selective and full test commands for the current project.

    This is the main entry point for the module.

    Args:
        project_root: Absolute path to the project root.  Defaults to cwd.

    Returns:
        A tuple ``(selective_cmd, full_cmd)`` where:

        - *selective_cmd* runs only tests related to changed files
          (``None`` if no related tests found or can't determine).
        - *full_cmd* runs the entire test suite as a fallback
          (``None`` if can't detect project type).
    """
    root = project_root or os.getcwd()

    full_cmd = _detect_full_test_command(root)

    changed = get_changed_files(cwd=root)
    if not changed:
        return (None, full_cmd)

    related = find_related_tests(changed, project_root=root)
    if not related:
        return (None, full_cmd)

    selective_cmd = build_selective_test_command(related, root)
    return (selective_cmd, full_cmd)


# ============================================================================
# CLI
# ============================================================================


def _main() -> None:
    """Standalone entry point for testing / debugging."""
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    print(f"Project root: {root}")
    print()

    changed = get_changed_files(cwd=root)
    print(f"Changed files ({len(changed)}):")
    for f in changed:
        print(f"  {f}")
    print()

    related = find_related_tests(changed, project_root=root)
    print(f"Related test files ({len(related)}):")
    for f in related:
        print(f"  {f}")
    print()

    selective_cmd, full_cmd = select_tests(project_root=root)
    print(f"Selective command: {selective_cmd or '(none)'}")
    print(f"Full command:      {full_cmd or '(none)'}")


if __name__ == "__main__":
    _main()
