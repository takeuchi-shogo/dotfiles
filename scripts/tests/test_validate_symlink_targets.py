"""validate_symlink_targets.sh の赤ケース。

CI では harness-tests の `uvx pytest scripts/tests/ -v` がこのファイルを 1 回実行する。
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / ".bin" / "validate_symlink_targets.sh"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def write_nix(root: Path, relative: str, body: str) -> None:
    path = root / "nix" / "home" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def assignment(home_key: str, repo_path: str) -> str:
    return f'"{home_key}" = outLink "{repo_path}";\n'


_INTERNAL_NAMES = (
    "duplicate_key_errors",
    "parse_targets",
    "read_nix",
    "nix_files",
)


def assert_user_facing(stderr: str) -> None:
    for name in _INTERNAL_NAMES:
        assert name not in stderr, stderr


def test_directory_missing_is_red() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_nix(root, "default.nix", assignment("home", "missing-dir"))
        missing = run(root)
        assert missing.returncode == 1, missing.stdout + missing.stderr
        assert "missing target" in missing.stderr
        assert "missing-dir" in missing.stderr
        assert "'home'" in missing.stderr
        assert "default.nix" in missing.stderr

        # outLink は種別を持たない。ディレクトリが実在すれば通す。
        (root / "missing-dir").mkdir()
        present = run(root)
        assert present.returncode == 0, present.stderr
        assert "checked 1 symlink targets" in present.stdout


def test_unparseable_outlink_is_red() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_nix(
            root,
            "default.nix",
            "let\n  outLink = path: path;\nin {\n  x = outLink ./not-quoted;\n}\n",
        )
        result = run(root)
        assert result.returncode == 1, result.stdout
        assert "default.nix" in result.stderr
        assert "refusing to ignore it" in result.stderr
        assert "not-quoted" in result.stderr
        assert result.stdout == ""
        assert_user_facing(result.stderr)


def test_outside_repo_is_red() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_nix(
            root,
            "default.nix",
            assignment("a", "../outside") + assignment("b", "/etc/passwd"),
        )
        result = run(root)
        assert result.returncode == 1, result.stdout
        assert "refusing path outside repo" in result.stderr
        assert "'../outside'" in result.stderr
        assert "'/etc/passwd'" in result.stderr
        assert result.stdout == ""
        assert_user_facing(result.stderr)


def test_zero_outlinks_is_red() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_nix(root, "default.nix", "outLink = path: { source = path; };\n")
        defined = run(root)
        assert defined.returncode == 1, defined.stdout
        assert 'no outLink "..." targets' in defined.stderr
        assert defined.stdout == ""
        assert_user_facing(defined.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_nix(root, "default.nix", '# ".h" = outLink "missing";\n')
        commented = run(root)
        assert commented.returncode == 1, commented.stdout
        assert 'no outLink "..." targets' in commented.stderr
        assert "missing target" not in commented.stderr
        assert_user_facing(commented.stderr)


def test_comment_line_is_ignored() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "present").write_text("x", encoding="utf-8")
        write_nix(
            root,
            "default.nix",
            '# ".skip" = outLink "not-a-real-target";\n'
            "# note outLink in a full-line comment\n"
            '"home" = outLink "present";  # kept\n',
        )
        result = run(root)
        assert result.returncode == 0, result.stderr
        assert "not-a-real-target" not in result.stdout
        assert "not-a-real-target" not in result.stderr
        assert "ok  present" in result.stdout
        assert "checked 1 symlink targets" in result.stdout


def test_errors_are_on_stderr() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_nix(root, "default.nix", assignment("home", "missing-file"))
        result = run(root)
        assert result.returncode == 1, result.stdout
        assert result.stdout == ""
        assert "missing target" in result.stderr
        assert "missing-file" in result.stderr
        assert "'home'" in result.stderr
        assert "default.nix" in result.stderr
        assert_user_facing(result.stderr)


def test_reads_nix_files_under_home() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "from-default").write_text("a", encoding="utf-8")
        (root / "from-extra").mkdir()
        write_nix(root, "default.nix", assignment("a", "from-default"))
        write_nix(root, "modules/extra.nix", assignment("b", "from-extra"))
        result = run(root)
        assert result.returncode == 0, result.stderr
        assert "ok  from-default" in result.stdout
        assert "ok  from-extra" in result.stdout
        assert "checked 2 symlink targets" in result.stdout
        assert "modules/extra.nix" in result.stdout


def test_duplicate_home_key_is_red() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "one").write_text("a", encoding="utf-8")
        (root / "two").write_text("b", encoding="utf-8")
        write_nix(
            root,
            "default.nix",
            assignment("same", "one") + assignment("same", "two"),
        )
        result = run(root)
        assert result.returncode == 1, result.stdout
        assert "duplicate home key" in result.stderr
        assert "'same'" in result.stderr
        assert "default.nix" in result.stderr
        assert result.stdout == ""
        assert_user_facing(result.stderr)


def test_same_repo_path_from_two_keys_is_ok() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "shared").write_text("s", encoding="utf-8")
        write_nix(
            root,
            "default.nix",
            assignment("a", "shared") + assignment("b", "shared"),
        )
        result = run(root)
        assert result.returncode == 0, result.stderr
        assert "checked 2 symlink targets" in result.stdout


def test_same_home_key_in_separate_files_is_ok() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "one").write_text("a", encoding="utf-8")
        (root / "two").write_text("b", encoding="utf-8")
        write_nix(root, "default.nix", assignment("same", "one"))
        write_nix(root, "wsl.nix", assignment("same", "two"))
        result = run(root)
        assert result.returncode == 0, result.stderr
        assert "duplicate" not in result.stderr
        assert "checked 2 symlink targets" in result.stdout


def test_cross_file_same_key_reports_missing_not_duplicate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "one").write_text("a", encoding="utf-8")
        write_nix(root, "default.nix", assignment("same", "one"))
        write_nix(root, "wsl.nix", assignment("same", "missing-file"))
        result = run(root)
        assert result.returncode == 1, result.stdout
        assert "missing target" in result.stderr
        assert "missing-file" in result.stderr
        assert "'same'" in result.stderr
        assert "wsl.nix" in result.stderr
        assert "default.nix" not in result.stderr
        assert "duplicate" not in result.stderr
        assert_user_facing(result.stderr)


def test_trailing_comment_outlink_is_ignored() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "present#keep").write_text("x", encoding="utf-8")
        write_nix(
            root,
            "default.nix",
            '"home" = outLink "present#keep";  # outLink in trailing comment\n',
        )
        result = run(root)
        assert result.returncode == 0, result.stderr
        assert "ok  present#keep" in result.stdout
        assert "checked 1 symlink targets" in result.stdout


def test_trailing_comment_does_not_hide_unparsed_call() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_nix(
            root,
            "default.nix",
            "x = outLink ./not-quoted;  # outLink\n",
        )
        result = run(root)
        assert result.returncode == 1, result.stdout
        assert "default.nix" in result.stderr
        assert "not-quoted" in result.stderr
        assert "refusing to ignore" in result.stderr
        assert_user_facing(result.stderr)


def test_no_nix_files_under_home_is_red() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        home = root / "nix" / "home"
        home.mkdir(parents=True)
        (home / "notes.txt").write_text("not nix", encoding="utf-8")
        result = run(root)
        assert result.returncode == 1, result.stdout + result.stderr
        assert "no *.nix under" in result.stderr
        assert str(home) in result.stderr
        assert result.stdout == ""
        assert_user_facing(result.stderr)


def test_nix_read_failure_is_red() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / "nix" / "home" / "default.nix"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"\xff\xfe not utf-8")
        result = run(root)
        assert result.returncode == 1, result.stdout + result.stderr
        assert "cannot read" in result.stderr
        assert "default.nix" in result.stderr
        assert result.stdout == ""
        assert_user_facing(result.stderr)


def test_extra_args_exit_2() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "one", "two"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "usage: validate_symlink_targets.sh" in result.stderr
    assert result.stdout == ""


def test_no_args_uses_script_repo() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
        cwd=tempfile.gettempdir(),
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert "nix/home/default.nix" in result.stdout
    assert "checked " in result.stdout


CASES = (
    ("ディレクトリ欠落", test_directory_missing_is_red),
    ("解析拒否", test_unparseable_outlink_is_red),
    ("repo 外", test_outside_repo_is_red),
    ("0 件", test_zero_outlinks_is_red),
    ("コメント行無視", test_comment_line_is_ignored),
    ("stderr", test_errors_are_on_stderr),
    ("分割ファイル", test_reads_nix_files_under_home),
    ("重複定義", test_duplicate_home_key_is_red),
    ("同一パスは重複にしない", test_same_repo_path_from_two_keys_is_ok),
    ("別ファイルの同一キー", test_same_home_key_in_separate_files_is_ok),
    ("別ファイルの欠落", test_cross_file_same_key_reports_missing_not_duplicate),
    ("行末コメント", test_trailing_comment_outlink_is_ignored),
    ("行末コメントは不正を隠さない", test_trailing_comment_does_not_hide_unparsed_call),
    ("nix が 0 本", test_no_nix_files_under_home_is_red),
    ("読み込み失敗", test_nix_read_failure_is_red),
    ("引数が多すぎる", test_extra_args_exit_2),
    ("引数なし", test_no_args_uses_script_repo),
)


def main() -> int:
    failed = False
    for label, fn in CASES:
        try:
            fn()
        except AssertionError as exc:
            failed = True
            print(f"fail {label}: {exc}", file=sys.stderr)
        else:
            print(f"pass {label}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
