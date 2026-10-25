#!/usr/bin/env bash
# CI 用。home-manager 適用後の $HOME は見ない。
#
# リンク定義の正本は nix/home/default.nix の
#   ".home/path" = outLink "repo/relative/path";
# validate_symlinks.sh の一覧へ同じ path を写すと二重管理になるので、ここは nix を読む。
# HOME 側の symlink が正しいかは validate_symlinks.sh の仕事で、そちらの挙動は変えていない。
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
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


def parse_targets(nix_text: str) -> tuple[list[str], str | None]:
    """quoted outLink の repo 相対パスを返す。未知の書き方が残れば失敗させる。"""
    targets = OUTLINK_CALL.findall(nix_text)
    remaining = OUTLINK_DEF.sub("", OUTLINK_CALL.sub("", nix_text))
    # コメントや別構文に outLink が残ると、黙って見落として緑になる。
    if OUTLINK_WORD.search(remaining):
        return [], "outLink call is not a quoted assignment; refusing to ignore it"
    if not targets:
        return [], 'no outLink "..." targets'
    return targets, None


def target_error(root: pathlib.Path, rel: str) -> str | None:
    """実在しない、または repo の外へ出るパスならメッセージを返す。"""
    pure = pathlib.PurePosixPath(rel)
    if rel == "" or pure.is_absolute() or ".." in pure.parts:
        return f"validate_symlink_targets: refusing path outside repo: {rel!r}"
    target = root / rel
    if not target.exists():
        return f"validate_symlink_targets: missing target {rel}: {target}"
    return None


def main() -> None:
    root = pathlib.Path.cwd()
    nix_path = root / "nix/home/default.nix"
    try:
        nix_text = nix_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"validate_symlink_targets: cannot read {nix_path}: {exc}")
        sys.exit(1)

    targets, parse_error = parse_targets(nix_text)
    if parse_error:
        print(f"validate_symlink_targets: {nix_path}: {parse_error}")
        sys.exit(1)

    errors: list[str] = []
    for rel in targets:
        message = target_error(root, rel)
        if message:
            errors.append(message)
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    for rel in targets:
        print(f"ok  {rel}")
    print(f"checked {len(targets)} symlink targets from {nix_path}")


if __name__ == "__main__":
    main()
PY
