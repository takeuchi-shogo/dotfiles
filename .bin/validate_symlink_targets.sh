#!/usr/bin/env bash
# CI 用。home-manager 適用後の $HOME は見ない。
#
# リンク定義の正本は nix/home/ 配下（再帰）の *.nix の
#   ".home/path" = outLink "repo/relative/path";
# default.nix だけを読むと、分割したファイルの outLink が黙って漏れる。
# validate_symlinks.sh の一覧へ同じ path を写すと二重管理になるので、ここは nix を読む。
# HOME 側の symlink が正しいかは validate_symlinks.sh の仕事で、そちらの挙動は変えていない。
#
# 引数なしはこのスクリプトのリポジトリ根を見る。第1引数があればそのディレクトリを根にする。
set -euo pipefail

if [[ $# -gt 1 ]]; then
  echo "validate_symlink_targets: usage: validate_symlink_targets.sh [repo_root]" >&2
  exit 2
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [[ $# -eq 1 ]]; then
  ROOT_DIR="$(cd "$1" && pwd)"
fi
cd "$ROOT_DIR"

python3 - <<'PY'
from __future__ import annotations

import pathlib
import re
import sys

# 代入形式だけをリンク定義とみなす。関数定義 `outLink = path:` は対象外。
OUTLINK_CALL = re.compile(r'=\s*outLink\s+"([^"]+)"')
OUTLINK_DEF = re.compile(r"\boutLink\s*=")
OUTLINK_WORD = re.compile(r"\boutLink\b")
# 重複は home 側のキー。同じ repo path を複数キーから指すのは正当なので見ない。
OUTLINK_KEY = re.compile(r'"([^"]+)"\s*=\s*outLink\s+"([^"]+)"')


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def strip_unquoted_hash_comment(line: str) -> str:
    """文字列の外にある `#` 以降を落とす。`"foo#bar"` の中の `#` は残す。"""
    in_string = False
    index = 0
    while index < len(line):
        char = line[index]
        if in_string:
            if char == "\\" and index + 1 < len(line):
                index += 2
                continue
            if char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            index += 1
            continue
        if char == "#":
            return line[:index]
        index += 1
    return line


def without_hash_comments(nix_text: str) -> str:
    """`#` コメントは代入にも未知構文にも数えない。行頭でも行末でも同じ。"""
    kept: list[str] = []
    for line in nix_text.splitlines():
        code = strip_unquoted_hash_comment(line).rstrip()
        if code == "":
            continue
        kept.append(code)
    return "\n".join(kept)


def parse_targets(
    nix_text: str,
) -> tuple[list[str], list[tuple[str, str]], str | None]:
    """quoted outLink のパスと home キーを返す。未知の書き方が残れば失敗させる。

    ファイル単体で 0 件でもエラーにしない。分割後の空ファイルと、合計 0 件は別。
    """
    body = without_hash_comments(nix_text)
    targets = OUTLINK_CALL.findall(body)
    keys = OUTLINK_KEY.findall(body)
    remaining = OUTLINK_DEF.sub("", OUTLINK_CALL.sub("", body))
    for line in remaining.splitlines():
        if OUTLINK_WORD.search(line):
            return [], [], (
                "outLink call is not a quoted assignment; "
                f"refusing to ignore it: {line.strip()}"
            )
    return targets, keys, None


def target_error(
    root: pathlib.Path,
    rel: str,
    owners: list[tuple[str, str]],
) -> str | None:
    """実在しない、または repo の外へ出るパスならメッセージを返す。

    outLink は file / directory を区別しないので、実在するどちらも通す。
    欠落時は定義元のファイルと home key を含める。
    """
    pure = pathlib.PurePosixPath(rel)
    if rel == "" or pure.is_absolute() or ".." in pure.parts:
        return f"validate_symlink_targets: refusing path outside repo: {rel!r}"
    target = root / rel
    if not target.exists():
        where = ", ".join(f"{key!r} in {source}" for source, key in owners)
        defined = f" ({where})" if where else ""
        return f"validate_symlink_targets: missing target {rel}{defined}: {target}"
    return None


def duplicate_key_errors(keys: list[tuple[str, str, str]]) -> list[str]:
    """同一ファイル内の home key 重複だけを赤にする。

    `import ./home` は default.nix だけを読む。別ファイルの同じキーは
    同時に一つの attrset になるとは限らない。
    """
    seen: dict[tuple[str, str], str] = {}
    errors: list[str] = []
    for source, key, rel in keys:
        previous = seen.get((source, key))
        if previous is not None:
            errors.append(
                "validate_symlink_targets: duplicate home key "
                f"{key!r} in {source} (targets {previous!r} and {rel!r})"
            )
            continue
        seen[(source, key)] = rel
    return errors


def nix_files(root: pathlib.Path) -> list[pathlib.Path]:
    """nix/home 配下の *.nix。サブディレクトリへ分けても対象から落とさない。"""
    home = root / "nix" / "home"
    if not home.is_dir():
        return []
    return sorted(path for path in home.rglob("*.nix") if path.is_file())


def read_nix(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        eprint(f"validate_symlink_targets: cannot read {path}: {exc}")
        sys.exit(1)


def format_sources(files: list[pathlib.Path]) -> str:
    return ", ".join(str(path) for path in files)


def collect(
    root: pathlib.Path,
) -> tuple[list[str], list[tuple[str, str, str]], list[pathlib.Path]]:
    files = nix_files(root)
    if not files:
        eprint(
            "validate_symlink_targets: no *.nix under "
            f"{root / 'nix' / 'home'}"
        )
        sys.exit(1)

    targets: list[str] = []
    keys: list[tuple[str, str, str]] = []
    for path in files:
        file_targets, file_keys, parse_error = parse_targets(read_nix(path))
        if parse_error:
            eprint(f"validate_symlink_targets: {path}: {parse_error}")
            sys.exit(1)
        source = str(path)
        targets.extend(file_targets)
        keys.extend((source, key, rel) for key, rel in file_keys)
    return targets, keys, files


def main() -> None:
    root = pathlib.Path.cwd()
    targets, keys, files = collect(root)
    if not targets:
        eprint(
            "validate_symlink_targets: "
            f'no outLink "..." targets in {format_sources(files)}'
        )
        sys.exit(1)

    errors = duplicate_key_errors(keys)
    for rel in targets:
        owners = [
            (source, key) for source, key, key_rel in keys if key_rel == rel
        ]
        message = target_error(root, rel, owners)
        if message:
            errors.append(message)
    if errors:
        for error in errors:
            eprint(error)
        sys.exit(1)

    for rel in targets:
        print(f"ok  {rel}")
    print(
        f"checked {len(targets)} symlink targets from {format_sources(files)}"
    )


if __name__ == "__main__":
    main()
PY
