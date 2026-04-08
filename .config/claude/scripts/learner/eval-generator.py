#!/usr/bin/env python3
"""Generate eval regression tuples from resolved failure clusters."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from storage import get_data_dir  # noqa: E402

# FM コード → expected_reviewer マッピング
REVIEWER_MAP: dict[str, str] = {
    "FM-001": "code-reviewer",
    "FM-002": "silent-failure-hunter",
    "FM-003": "code-reviewer",
    "FM-004": "type-design-analyzer",
    "FM-005": "security-reviewer",
    "FM-006": "code-reviewer",
    "FM-007": "code-reviewer",
    "FM-008": "build-fixer",
    "FM-009": "code-reviewer",
    "FM-010": "security-reviewer",
    "FM-011": "code-reviewer",
    "FM-012": "code-reviewer",
    "FM-013": "debugger",
    "FM-014": "product-reviewer",
    "FM-015": "code-reviewer",
    "FM-016": "codex-reviewer",
    "FM-017": "code-reviewer",
    "FM-UNKNOWN": "code-reviewer",
}

# FM コード → severity マッピング
SEVERITY_MAP: dict[str, str] = {
    "FM-001": "critical",
    "FM-002": "critical",
    "FM-003": "medium",
    "FM-004": "high",
    "FM-005": "high",
    "FM-006": "high",
    "FM-007": "medium",
    "FM-008": "high",
    "FM-009": "high",
    "FM-010": "critical",
    "FM-011": "high",
    "FM-012": "medium",
    "FM-013": "medium",
    "FM-014": "high",
    "FM-015": "critical",
    "FM-016": "critical",
    "FM-017": "medium",
    "FM-UNKNOWN": "medium",
}

_EXT_TO_LANG: dict[str, str] = {
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
    ".py": "python",
    ".rs": "rust",
    ".rb": "ruby",
    ".java": "java",
    ".kt": "kotlin",
    ".swift": "swift",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
}

logger = logging.getLogger("autoevolve")


def _setup_logger() -> None:
    if logger.handlers:
        return
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)


def _detect_language(cluster: dict) -> str:
    """クラスタの instances から言語を推論する。"""
    for inst in cluster.get("instances", []):
        file_path = inst.get("file", "")
        if file_path:
            ext = Path(file_path).suffix.lower()
            if ext in _EXT_TO_LANG:
                return _EXT_TO_LANG[ext]
    return "unknown"


def _pick_representative_instance(cluster: dict) -> dict:
    """最も詳細な message を持つ instance を代表として選ぶ。"""
    instances = cluster.get("instances", [])
    if not instances:
        return {}
    return max(instances, key=lambda i: len(i.get("message", "")))


def _build_failure_description(
    instance: dict, fm_code: str, root_cause: str, severity: str
) -> str:
    """instance から構造化された failure description を構築する。"""
    file_path = instance.get("file", "unknown")
    msg = instance.get("message", "No message available")

    lines = [
        f"# Regression: {fm_code}",
        f"# File: {file_path}",
        f"# Root cause: {root_cause}",
        f"# Error: {msg[:200]}",
        f"# Severity: {severity}",
    ]
    return "\n".join(lines)


def _load_clusters(clusters_path: Path) -> dict:
    """クラスタファイルを読み込む。エラー時は sys.exit(1)。"""
    try:
        return json.loads(clusters_path.read_text(encoding="utf-8"))
    except OSError as exc:
        logger.error("eval-generator: failed to read clusters file: %s", exc)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        logger.error("eval-generator: clusters file is not valid JSON: %s", exc)
        sys.exit(1)


def _load_regression_suite(suite_path: Path) -> dict:
    """既存の regression suite を読み込む。なければ空の構造を返す。"""
    if not suite_path.exists():
        return {"tuples": []}
    try:
        data = json.loads(suite_path.read_text(encoding="utf-8"))
        if "tuples" not in data:
            data["tuples"] = []
        return data
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(
            "eval-generator: failed to load regression suite, starting fresh: %s", exc
        )
        return {"tuples": []}


def _existing_source_clusters(suite: dict) -> set[str]:
    """既に suite に登録済みの source_cluster ID セットを返す。"""
    return {t.get("source_cluster", "") for t in suite.get("tuples", [])}


def _next_reg_id(suite: dict) -> str:
    """次の reg-NNN ID を生成する。"""
    existing_ids = [t.get("id", "") for t in suite.get("tuples", [])]
    nums = []
    for eid in existing_ids:
        if eid.startswith("reg-"):
            try:
                nums.append(int(eid[4:]))
            except ValueError:
                logger.debug("eval-generator: could not parse reg id: %s", eid)
    next_num = max(nums, default=0) + 1
    return f"reg-{next_num:03d}"


def import_external(
    external_path: Path,
    target_path: Path,
    max_tuples: int,
    dry_run: bool,
) -> None:
    """外部 JSON tuple を target にマージする。"""
    # 1. Load external file
    try:
        external_data = json.loads(external_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("import-external: failed to load %s: %s", external_path, exc)
        sys.exit(1)

    external_tuples = external_data.get("tuples", [])
    if not external_tuples:
        logger.info("import-external: no tuples in external file")
        return

    # 2. Load target file
    if target_path.exists():
        try:
            target_data = json.loads(target_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning(
                "import-external: failed to load target %s, starting fresh: %s",
                target_path,
                exc,
            )
            target_data = {"tuples": []}
    else:
        target_data = {"tuples": []}

    existing_tuples = target_data.get("tuples", [])

    # 3. Build fingerprint set for dedup
    existing_fingerprints = {
        (
            t.get("language", ""),
            t.get("failure_mode", ""),
            t.get("description", "")[:100],
            t.get("code", "")[:100],
        )
        for t in existing_tuples
    }

    # 4. Generate ext-NNN IDs
    existing_ext_nums = []
    for t in existing_tuples:
        tid = t.get("id", "")
        if tid.startswith("ext-"):
            try:
                existing_ext_nums.append(int(tid[4:]))
            except ValueError:
                logger.debug("import-external: could not parse ext id: %s", tid)
    next_ext_num = max(existing_ext_nums, default=0) + 1

    # 5. Merge
    added = 0
    for t in external_tuples:
        fp = (
            t.get("language", ""),
            t.get("failure_mode", ""),
            t.get("description", "")[:100],
            t.get("code", "")[:100],
        )
        if fp in existing_fingerprints:
            logger.debug(
                "import-external: skipping duplicate: %s", t.get("id", "unknown")
            )
            continue

        if len(existing_tuples) >= max_tuples:
            logger.warning(
                "import-external: max_tuples limit (%d) reached, stopping import",
                max_tuples,
            )
            break

        # Assign ext-NNN ID
        new_id = f"ext-{next_ext_num:03d}"
        next_ext_num += 1

        fm = t.get("failure_mode", "")
        imported_tuple = {
            "id": new_id,
            "language": t.get("language", "unknown"),
            "failure_mode": t.get("failure_mode", "FM-UNKNOWN"),
            "severity": t.get("severity", SEVERITY_MAP.get(fm, "medium")),
            "expected_reviewer": t.get(
                "expected_reviewer",
                REVIEWER_MAP.get(fm, "code-reviewer"),
            ),
            "description": t.get("description", f"Imported from {external_path.name}"),
            "code": t.get("code", ""),
        }
        existing_tuples.append(imported_tuple)
        existing_fingerprints.add(fp)
        added += 1
        logger.info("import-external: added %s from external", new_id)

    if added == 0:
        logger.info("import-external: no new tuples to import (all duplicates)")
        return

    target_data["tuples"] = existing_tuples

    if dry_run:
        print(
            f"[dry-run] import: would add {added} tuples to {target_path}"
            f" (total: {len(existing_tuples)})"
        )
    else:
        target_path.write_text(
            json.dumps(target_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            f"import: added {added} tuples to {target_path}"
            f" (total: {len(existing_tuples)})"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=("Generate eval regression tuples from resolved failure clusters")
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse clusters but do not write output",
    )
    parser.add_argument(
        "--import-external",
        metavar="PATH",
        help="Import external JSON tuples into reviewer-eval-tuples.json",
    )
    parser.add_argument(
        "--import-target",
        default=None,
        help="Target file for import (default: reviewer-eval-tuples.json)",
    )
    parser.add_argument(
        "--max-tuples",
        type=int,
        default=100,
        help="Max total tuples after import (default: 100)",
    )
    args = parser.parse_args()

    if args.import_external:
        _setup_logger()
        external_path = Path(args.import_external)
        if not external_path.exists():
            logger.error("import-external: file not found: %s", external_path)
            sys.exit(1)

        target_path = (
            Path(args.import_target)
            if args.import_target
            else (
                Path(__file__).resolve().parent.parent
                / "eval"
                / "reviewer-eval-tuples.json"
            )
        )
        import_external(external_path, target_path, args.max_tuples, args.dry_run)
        return

    _setup_logger()

    try:
        data_dir = get_data_dir()
        clusters_path = data_dir / "clusters" / "failure-clusters.json"

        # クラスタファイルがなければ正常終了
        if not clusters_path.exists():
            logger.info("eval-generator: no cluster file found, exiting")
            sys.exit(0)

        cluster_data = _load_clusters(clusters_path)
        all_clusters = cluster_data.get("clusters", [])

        # resolved クラスタのみ抽出
        resolved = [c for c in all_clusters if c.get("status") == "resolved"]
        if not resolved:
            logger.info("eval-generator: no resolved clusters found, exiting")
            sys.exit(0)

        # regression suite のパス
        suite_path = (
            Path(__file__).resolve().parent.parent / "eval" / "regression-suite.json"
        )
        os.makedirs(suite_path.parent, exist_ok=True)

        suite = _load_regression_suite(suite_path)
        already_registered = _existing_source_clusters(suite)

        generated = 0
        for cluster in resolved:
            cluster_id = cluster.get("id", "")
            if cluster_id in already_registered:
                logger.debug(
                    "eval-generator: skipping already registered cluster %s",
                    cluster_id,
                )
                continue

            fm_code = cluster.get("fm_code", "FM-UNKNOWN")
            root_cause = cluster.get("root_cause", "Unknown")
            severity = SEVERITY_MAP.get(fm_code, "medium")
            language = _detect_language(cluster)
            representative = _pick_representative_instance(cluster)
            description_text = _build_failure_description(
                representative, fm_code, root_cause, severity
            )
            reviewer = REVIEWER_MAP.get(fm_code, "code-reviewer")

            # resolved_date: last_seen またはクラスタから取得
            resolved_date = cluster.get("last_seen", "") or datetime.now(
                timezone.utc
            ).strftime("%Y-%m-%d")

            instances = cluster.get("instances", [{}])
            first_file = (
                instances[0].get("file", "unknown module")
                if instances
                else "unknown module"
            )
            description = (
                f"Regression test: {root_cause} in {first_file or 'unknown module'}"
            )

            reg_id = _next_reg_id(suite)
            tuple_entry = {
                "id": reg_id,
                "source_cluster": cluster_id,
                "tuple_type": "regression",
                "root_cause": root_cause,
                "language": language,
                "failure_mode": fm_code,
                "severity": severity,
                "expected_reviewer": reviewer,
                "description": description,
                "failure_description": description_text,
                "code": "",
                "resolved_date": resolved_date,
            }
            suite["tuples"].append(tuple_entry)
            already_registered.add(cluster_id)
            generated += 1
            logger.info(
                "eval-generator: generated %s from cluster %s (%s)",
                reg_id,
                cluster_id,
                fm_code,
            )

        if generated == 0:
            logger.info("eval-generator: no new tuples to generate")
            sys.exit(0)

        # 出力
        suite["description"] = (
            "Auto-generated regression suite from resolved failure clusters."
            " DO NOT edit manually."
        )
        suite["generated_at"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        if args.dry_run:
            logger.info(
                "eval-generator: --dry-run mode, skipping write"
                " (%d new tuples would be written)",
                generated,
            )
            print(
                f"[dry-run] regression-suite: {suite_path}"
                f" ({len(suite['tuples'])} tuples)"
            )
        else:
            suite_path.write_text(
                json.dumps(suite, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            logger.info(
                "eval-generator: wrote %d new tuples to %s (total: %d)",
                generated,
                suite_path,
                len(suite["tuples"]),
            )
            print(f"regression-suite: {suite_path} ({len(suite['tuples'])} tuples)")

    except Exception as exc:
        logger.error("eval-generator: fatal error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
