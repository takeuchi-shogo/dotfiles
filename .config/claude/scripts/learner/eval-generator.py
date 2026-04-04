#!/usr/bin/env python3
"""Generate eval regression tuples from resolved failure clusters."""

from __future__ import annotations

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


def _build_code_snippet(instance: dict, fm_code: str) -> str:
    """instance から代表コードスニペットを構築する。"""
    msg = instance.get("message", "")
    file_path = instance.get("file", "")
    if msg:
        comment = (
            f"// Source: {file_path}" if file_path else "// Representative instance"
        )
        return f"{comment}\n// {msg[:200]}"
    return f"// No representative code available for {fm_code}"


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


def main() -> None:
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
                    "eval-generator: skipping already registered cluster %s", cluster_id
                )
                continue

            fm_code = cluster.get("fm_code", "FM-UNKNOWN")
            root_cause = cluster.get("root_cause", "Unknown")
            language = _detect_language(cluster)
            representative = _pick_representative_instance(cluster)
            code = _build_code_snippet(representative, fm_code)
            reviewer = REVIEWER_MAP.get(fm_code, "code-reviewer")
            severity = SEVERITY_MAP.get(fm_code, "medium")

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
                "language": language,
                "failure_mode": fm_code,
                "severity": severity,
                "expected_reviewer": reviewer,
                "description": description,
                "code": code,
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

        suite_path.write_text(
            json.dumps(suite, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info(
            "eval-generator: wrote %d new tuples to %s (total: %d)",
            generated,
            suite_path,
            len(suite["tuples"]),
        )

    except Exception as exc:
        logger.error("eval-generator: fatal error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
