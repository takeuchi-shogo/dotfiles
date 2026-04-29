from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import tomllib
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any
from typing import TypedDict


USEFULNESS_RE = re.compile(r"Usefulness score:\s*(\d+)/10\b", re.IGNORECASE)
DIFF_STAT_INSERT_RE = re.compile(r"(\d+)\s+insertions?\(\+\)")
DIFF_STAT_DELETE_RE = re.compile(r"(\d+)\s+deletions?\(-\)")


class Decision(TypedDict, total=False):
    verdict: str
    reason: str | None


class EvidenceItem(TypedDict, total=False):
    kind: str
    ref: str | int | float | None


class SnapshotPayload(TypedDict, total=False):
    commit: str
    files_sha256: dict[str, str]


@dataclass(frozen=True)
class WorkflowPrompt:
    default: str
    user_template: str
    required: bool


@dataclass(frozen=True)
class StageDefinition:
    label: str
    prompt: str
    repeat: int | str
    stop_on_skip: bool
    stop_on_low_usefulness: bool


@dataclass(frozen=True)
class StopRulesConfig:
    no_op_diff_enabled: bool = False
    validation_enabled: bool = False
    validation_command: str | None = None
    validation_timeout: int = 300
    time_budget_enabled: bool = False
    time_budget_seconds: float = 1800.0
    snapshot_drift_enabled: bool = False
    snapshot_drift_apply_labels: tuple[str, ...] = ("implement",)
    destructive_enabled: bool = False
    destructive_deletion_threshold: int = 50
    destructive_total_threshold: int = 100
    destructive_usefulness_floor: int = 5


@dataclass(frozen=True)
class WorkflowDefinition:
    name: str
    description: str
    prompt: WorkflowPrompt
    counts: dict[str, int]
    usefulness_threshold: int
    stages: list[StageDefinition]
    stop_rules: StopRulesConfig = StopRulesConfig()


@dataclass(frozen=True)
class ExpandedStage:
    label: str
    prompt: str
    stop_on_skip: bool
    stop_on_low_usefulness: bool


@dataclass
class StageResult:
    label: str
    command: list[str]
    returncode: int
    stdout_path: str
    stderr_path: str
    last_message_path: str
    last_message: str
    usefulness_score: int | None
    stop_reason: str | None
    thread_id: str | None
    head_before: str | None = None
    head_after: str | None = None
    elapsed_seconds: float | None = None
    validation_summary: str | None = None
    decision: Decision | None = None
    evidence: list[EvidenceItem] | None = None


class JanitorError(RuntimeError):
    pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="codex-janitor")
    parser.add_argument(
        "--workflow",
        default="tools/codex-janitor/workflows/refactor-loop.toml",
        help="Path to workflow TOML",
    )
    parser.add_argument(
        "--prompt", help="Optional user guidance for the initial refactor stage"
    )
    parser.add_argument(
        "--improvements", type=int, help="Override improvement pass count"
    )
    parser.add_argument("--reviews", type=int, help="Override review pass count")
    parser.add_argument(
        "--target-dir", default=".", help="Target repository to operate on"
    )
    parser.add_argument(
        "--output-root", default="tmp/codex-janitor/runs", help="Run artifact root"
    )
    parser.add_argument(
        "--sessions-dir", default="~/.codex/sessions", help="Codex sessions root"
    )
    parser.add_argument("--codex-bin", default="codex", help="Codex CLI binary")
    parser.add_argument("--profile", default="fast", help="Codex profile to use")
    parser.add_argument(
        "--allow-dirty", action="store_true", help="Allow running in a dirty repository"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the expanded plan without invoking Codex",
    )
    return parser.parse_args(argv)


def _load_stop_rules(raw: dict[str, Any]) -> StopRulesConfig:
    block = raw.get("stop_rules")
    if not isinstance(block, dict):
        return StopRulesConfig()

    def _get_section(key: str) -> dict[str, Any]:
        section = block.get(key)
        return section if isinstance(section, dict) else {}

    no_op = _get_section("no_op_diff")
    validation = _get_section("validation")
    time_budget = _get_section("time_budget")
    snapshot_drift = _get_section("snapshot_drift")
    destructive = _get_section("destructive_without_evidence")
    apply_labels_raw = snapshot_drift.get("apply_labels", ["implement"])
    if isinstance(apply_labels_raw, list):
        apply_labels = tuple(str(item) for item in apply_labels_raw)
    else:
        apply_labels = ("implement",)
    return StopRulesConfig(
        no_op_diff_enabled=bool(no_op.get("enabled", False)),
        validation_enabled=bool(validation.get("enabled", False)),
        validation_command=(
            str(validation["command"]) if "command" in validation else None
        ),
        validation_timeout=int(validation.get("timeout", 300)),
        time_budget_enabled=bool(time_budget.get("enabled", False)),
        time_budget_seconds=float(time_budget.get("seconds", 1800)),
        snapshot_drift_enabled=bool(snapshot_drift.get("enabled", False)),
        snapshot_drift_apply_labels=apply_labels,
        destructive_enabled=bool(destructive.get("enabled", False)),
        destructive_deletion_threshold=int(destructive.get("deletion_threshold", 50)),
        destructive_total_threshold=int(destructive.get("total_threshold", 100)),
        destructive_usefulness_floor=int(destructive.get("usefulness_floor", 5)),
    )


def load_workflow(path: Path) -> WorkflowDefinition:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    prompt_block = raw.get("prompt", {})
    counts_block = raw.get("counts", {})
    stopping_block = raw.get("stopping", {})
    stages_block = raw.get("stages")
    if not isinstance(stages_block, list) or not stages_block:
        raise JanitorError(f"workflow has no stages: {path}")
    stages: list[StageDefinition] = []
    for stage in stages_block:
        if not isinstance(stage, dict):
            raise JanitorError(f"invalid stage entry in {path}")
        stages.append(
            StageDefinition(
                label=str(stage["label"]),
                prompt=str(stage["prompt"]),
                repeat=stage.get("repeat", 1),
                stop_on_skip=bool(stage.get("stop_on_skip", False)),
                stop_on_low_usefulness=bool(stage.get("stop_on_low_usefulness", False)),
            )
        )
    return WorkflowDefinition(
        name=str(raw.get("name", path.stem)),
        description=str(raw.get("description", "")),
        prompt=WorkflowPrompt(
            default=str(prompt_block.get("default", "")),
            user_template=str(prompt_block.get("user_template", "{user_prompt}")),
            required=bool(prompt_block.get("required", False)),
        ),
        counts={str(key): int(value) for key, value in counts_block.items()},
        usefulness_threshold=int(stopping_block.get("usefulness_threshold", 3)),
        stages=stages,
        stop_rules=_load_stop_rules(raw),
    )


def resolve_initial_prompt(
    workflow: WorkflowDefinition, user_prompt: str | None
) -> str:
    if user_prompt:
        return workflow.prompt.user_template.format(user_prompt=user_prompt.strip())
    if workflow.prompt.default:
        return workflow.prompt.default
    if workflow.prompt.required:
        raise JanitorError("--prompt is required for this workflow")
    raise JanitorError("workflow is missing both prompt.default and --prompt")


def resolve_repeat(repeat: int | str, counts: dict[str, int]) -> int:
    if isinstance(repeat, int):
        value = repeat
    else:
        if repeat not in counts:
            raise JanitorError(f"unknown repeat key: {repeat}")
        value = counts[repeat]
    if value < 0:
        raise JanitorError(f"repeat count must be >= 0: {repeat}")
    return value


def expand_stages(
    workflow: WorkflowDefinition,
    *,
    initial_prompt: str,
    count_overrides: dict[str, int],
) -> list[ExpandedStage]:
    counts = dict(workflow.counts)
    counts.update(
        {key: value for key, value in count_overrides.items() if value is not None}
    )
    expanded: list[ExpandedStage] = []
    for stage in workflow.stages:
        repeat_count = resolve_repeat(stage.repeat, counts)
        if repeat_count == 0:
            continue
        for index in range(1, repeat_count + 1):
            label = stage.label if repeat_count == 1 else f"{stage.label}-{index}"
            expanded.append(
                ExpandedStage(
                    label=label,
                    prompt=stage.prompt.format(initial_prompt=initial_prompt),
                    stop_on_skip=stage.stop_on_skip,
                    stop_on_low_usefulness=stage.stop_on_low_usefulness,
                )
            )
    return expanded


def ensure_clean_repo(target_dir: Path) -> None:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=target_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    if status.returncode != 0:
        raise JanitorError(f"failed to inspect git status in {target_dir}")
    if status.stdout.strip():
        raise JanitorError(
            "target repository has pre-existing changes; "
            "use a clean worktree or pass --allow-dirty"
        )


def snapshot_session_files(sessions_dir: Path) -> dict[Path, float]:
    if not sessions_dir.exists():
        return {}
    return {path: path.stat().st_mtime for path in sessions_dir.rglob("*.jsonl")}


def discover_session_file(before: dict[Path, float], sessions_dir: Path) -> Path:
    after = snapshot_session_files(sessions_dir)
    new_paths = [path for path in after if path not in before]
    if new_paths:
        return max(new_paths, key=lambda path: after[path])
    changed_paths = [
        path for path, mtime in after.items() if before.get(path, 0.0) < mtime
    ]
    if changed_paths:
        return max(changed_paths, key=lambda path: after[path])
    raise JanitorError(
        "could not discover a new Codex session file after the initial stage"
    )


def read_session_id(session_file: Path) -> str:
    with session_file.open("r", encoding="utf-8") as handle:
        first_line = handle.readline()
    payload = json.loads(first_line)
    if payload.get("type") != "session_meta":
        raise JanitorError(f"unexpected session file header: {session_file}")
    session_id = payload.get("payload", {}).get("id")
    if not isinstance(session_id, str) or not session_id:
        raise JanitorError(f"session file did not contain payload.id: {session_file}")
    return session_id


def parse_usefulness_score(text: str) -> int | None:
    match = USEFULNESS_RE.search(text)
    if not match:
        return None
    return int(match.group(1))


def parse_thread_id(stdout_text: str) -> str | None:
    for line in stdout_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("type") == "thread.started":
            thread_id = payload.get("thread_id")
            if isinstance(thread_id, str):
                return thread_id
    return None


def capture_head_sha(target_dir: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=target_dir,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def has_working_tree_changes(target_dir: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=target_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def run_validation_command(
    target_dir: Path, command: str, timeout: int
) -> tuple[bool, str]:
    """Execute a validation command and return (success, summary)."""
    try:
        result = subprocess.run(
            command,
            cwd=target_dir,
            check=False,
            capture_output=True,
            text=True,
            shell=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s: {command}"
    if result.returncode == 0:
        return True, ""
    summary_lines = (result.stdout + result.stderr).splitlines()
    tail = "\n".join(summary_lines[-20:])
    return False, f"non-zero exit ({result.returncode}): {tail}"


def list_changed_files(target_dir: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=target_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def compute_snapshot(
    target_dir: Path, files: list[str] | None = None
) -> SnapshotPayload:
    """Compute a snapshot of HEAD + sha256 of changed files (or explicit list)."""
    head_sha = capture_head_sha(target_dir) or ""
    if files is None:
        files = list_changed_files(target_dir)
    files_sha256: dict[str, str] = {}
    for rel in files:
        path = target_dir / rel
        if path.exists() and path.is_file():
            files_sha256[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            files_sha256[rel] = "<missing>"
    return {"commit": head_sha, "files_sha256": files_sha256}


def detect_snapshot_drift(
    start: SnapshotPayload, current: SnapshotPayload
) -> str | None:
    if start.get("commit") != current.get("commit"):
        return f"commit_changed:{start.get('commit')}->{current.get('commit')}"
    start_files = start.get("files_sha256", {}) or {}
    current_files = current.get("files_sha256", {}) or {}
    for path, sha in start_files.items():
        if current_files.get(path) != sha:
            return f"file_changed:{path}"
    return None


def analyze_destructive_change(
    target_dir: Path, head_before: str | None
) -> dict[str, int]:
    stat = {"insertions": 0, "deletions": 0}
    if not head_before:
        return stat
    parts: list[str] = []
    diff_committed = subprocess.run(
        ["git", "diff", "--shortstat", f"{head_before}..HEAD"],
        cwd=target_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    if diff_committed.returncode == 0:
        parts.append(diff_committed.stdout)
    diff_working = subprocess.run(
        ["git", "diff", "--shortstat", "HEAD"],
        cwd=target_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    if diff_working.returncode == 0:
        parts.append(diff_working.stdout)
    text = "\n".join(parts)
    stat["insertions"] = sum(
        int(m.group(1)) for m in DIFF_STAT_INSERT_RE.finditer(text)
    )
    stat["deletions"] = sum(int(m.group(1)) for m in DIFF_STAT_DELETE_RE.finditer(text))
    return stat


def decide_stop_reason(
    stage: ExpandedStage,
    *,
    last_message: str,
    usefulness_score: int | None,
    usefulness_threshold: int,
    no_op_diff_enabled: bool = False,
    diff_changed: bool | None = None,
    validation_failed: bool | None = None,
    validation_summary: str | None = None,
    elapsed_seconds: float | None = None,
    time_budget_seconds: float | None = None,
    destructive_enabled: bool = False,
    destructive_stat: dict[str, int] | None = None,
    destructive_deletion_threshold: int = 50,
    destructive_total_threshold: int = 100,
    destructive_usefulness_floor: int = 5,
) -> str | None:
    normalized = last_message.strip()
    if stage.stop_on_skip and normalized == "skip":
        return "assistant_returned_skip"
    if (
        stage.stop_on_low_usefulness
        and usefulness_score is not None
        and usefulness_score <= usefulness_threshold
    ):
        return f"usefulness_below_threshold:{usefulness_score}"
    if no_op_diff_enabled and diff_changed is False:
        return "no_op_diff"
    if validation_failed is True:
        tail = ""
        if validation_summary:
            tail_line = (
                validation_summary.splitlines()[-1]
                if validation_summary.splitlines()
                else validation_summary
            )
            tail = tail_line[:80]
        return f"validation_failed:{tail}" if tail else "validation_failed"
    if (
        time_budget_seconds is not None
        and elapsed_seconds is not None
        and elapsed_seconds > time_budget_seconds
    ):
        return f"time_budget_exceeded:{elapsed_seconds:.1f}s"
    if destructive_enabled and destructive_stat is not None:
        ins = int(destructive_stat.get("insertions", 0))
        dele = int(destructive_stat.get("deletions", 0))
        is_destructive = (
            dele > destructive_deletion_threshold
            or (ins + dele) > destructive_total_threshold
        )
        low_confidence = (
            usefulness_score is None or usefulness_score <= destructive_usefulness_floor
        )
        if is_destructive and low_confidence:
            return f"destructive_without_evidence:deletions={dele},insertions={ins}"
    return None


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def build_command(
    *,
    codex_bin: str,
    stage: ExpandedStage,
    stage_last_message_path: Path,
    target_dir: Path,
    session_id: str | None,
    profile: str | None,
) -> list[str]:
    command = [codex_bin, "exec"]
    if session_id is None:
        command.extend(["-C", str(target_dir)])
    else:
        command.extend(["resume", session_id])
    if profile:
        command.extend(["-p", profile])
    command.extend(
        [
            "--json",
            "-o",
            str(stage_last_message_path),
            "-c",
            'approval_policy="never"',
            "-c",
            "suppress_unstable_features_warning=true",
        ]
    )
    command.append(stage.prompt)
    return command


def run_stage(
    *,
    codex_bin: str,
    stage: ExpandedStage,
    stage_index: int,
    target_dir: Path,
    run_dir: Path,
    session_id: str | None,
    profile: str | None,
    usefulness_threshold: int,
    stop_rules: StopRulesConfig = StopRulesConfig(),
    run_started_at: float | None = None,
) -> StageResult:
    stage_slug = stage.label.replace("/", "-")
    stage_dir = run_dir / "stages" / f"{stage_index:02d}-{stage_slug}"
    stage_last_message_path = stage_dir / "last-message.txt"
    head_before = capture_head_sha(target_dir)
    stage_started_at = time.monotonic()
    command = build_command(
        codex_bin=codex_bin,
        stage=stage,
        stage_last_message_path=stage_last_message_path,
        target_dir=target_dir,
        session_id=session_id,
        profile=profile,
    )
    completed = subprocess.run(
        command,
        cwd=target_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    head_after = capture_head_sha(target_dir)
    elapsed_total = (
        time.monotonic() - run_started_at
        if run_started_at is not None
        else time.monotonic() - stage_started_at
    )
    stdout_path = stage_dir / "stdout.jsonl"
    stderr_path = stage_dir / "stderr.log"
    write_text(stdout_path, completed.stdout)
    write_text(stderr_path, completed.stderr)
    last_message = ""
    if stage_last_message_path.exists():
        last_message = stage_last_message_path.read_text(encoding="utf-8")
    usefulness_score = parse_usefulness_score(last_message)

    diff_changed: bool | None = None
    if stop_rules.no_op_diff_enabled:
        diff_changed = (
            head_before is not None
            and head_after is not None
            and head_before != head_after
        ) or has_working_tree_changes(target_dir)

    validation_failed: bool | None = None
    validation_summary: str | None = None
    if stop_rules.validation_enabled and stop_rules.validation_command:
        success, summary = run_validation_command(
            target_dir,
            stop_rules.validation_command,
            stop_rules.validation_timeout,
        )
        validation_failed = not success
        validation_summary = summary if not success else None

    destructive_stat: dict[str, int] | None = None
    if stop_rules.destructive_enabled and head_before is not None:
        destructive_stat = analyze_destructive_change(target_dir, head_before)

    stop_reason: str | None = None
    if completed.returncode == 0:
        stop_reason = decide_stop_reason(
            stage,
            last_message=last_message,
            usefulness_score=usefulness_score,
            usefulness_threshold=usefulness_threshold,
            no_op_diff_enabled=stop_rules.no_op_diff_enabled,
            diff_changed=diff_changed,
            validation_failed=validation_failed,
            validation_summary=validation_summary,
            elapsed_seconds=elapsed_total,
            time_budget_seconds=(
                stop_rules.time_budget_seconds
                if stop_rules.time_budget_enabled
                else None
            ),
            destructive_enabled=stop_rules.destructive_enabled,
            destructive_stat=destructive_stat,
            destructive_deletion_threshold=stop_rules.destructive_deletion_threshold,
            destructive_total_threshold=stop_rules.destructive_total_threshold,
            destructive_usefulness_floor=stop_rules.destructive_usefulness_floor,
        )

    decision: Decision = {
        "verdict": "stop" if stop_reason else "proceed",
        "reason": stop_reason,
    }
    evidence: list[EvidenceItem] = [
        {"kind": "stdout", "ref": str(stdout_path)},
        {"kind": "elapsed_seconds", "ref": round(elapsed_total, 3)},
    ]
    if usefulness_score is not None:
        evidence.append({"kind": "usefulness_score", "ref": usefulness_score})
    if destructive_stat is not None:
        ins = destructive_stat["insertions"]
        dele = destructive_stat["deletions"]
        evidence.append({"kind": "diff_stat", "ref": f"+{ins} -{dele}"})
    if validation_failed is not None:
        evidence.append(
            {
                "kind": "validation",
                "ref": "passed" if not validation_failed else "failed",
            }
        )

    return StageResult(
        label=stage.label,
        command=command,
        returncode=completed.returncode,
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        last_message_path=str(stage_last_message_path),
        last_message=last_message,
        usefulness_score=usefulness_score,
        stop_reason=stop_reason,
        thread_id=parse_thread_id(completed.stdout),
        head_before=head_before,
        head_after=head_after,
        elapsed_seconds=round(elapsed_total, 3),
        validation_summary=validation_summary,
        decision=decision,
        evidence=evidence,
    )


def build_run_id(workflow_name: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = workflow_name.lower().replace(" ", "-")
    return f"{timestamp}-{slug}"


def print_dry_run(stages: list[ExpandedStage]) -> None:
    for index, stage in enumerate(stages, start=1):
        print(f"{index:02d}. {stage.label}")
        print(stage.prompt)


def _is_apply_stage(label: str, apply_labels: tuple[str, ...]) -> bool:
    lowered = label.lower()
    return any(token in lowered for token in apply_labels)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    workflow_path = Path(args.workflow)
    target_dir = Path(args.target_dir).resolve()
    output_root = Path(args.output_root)
    sessions_dir = Path(args.sessions_dir).expanduser()
    workflow = load_workflow(workflow_path)
    stop_rules = workflow.stop_rules
    initial_prompt = resolve_initial_prompt(workflow, args.prompt)
    stages = expand_stages(
        workflow,
        initial_prompt=initial_prompt,
        count_overrides={"improvements": args.improvements, "reviews": args.reviews},
    )
    if args.dry_run:
        print_dry_run(stages)
        return 0
    if not args.allow_dirty:
        ensure_clean_repo(target_dir)
    run_dir = output_root / build_run_id(workflow.name)
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "manifest.json"
    session_snapshot = snapshot_session_files(sessions_dir)
    stage_results: list[StageResult] = []
    session_id: str | None = None
    session_file: Path | None = None
    stop_reason: str | None = None
    run_started_at = time.monotonic()
    snapshot_start: SnapshotPayload | None = None
    snapshot_pre_apply: SnapshotPayload | None = None
    if stop_rules.snapshot_drift_enabled:
        snapshot_start = compute_snapshot(target_dir, files=[])
    for index, stage in enumerate(stages, start=1):
        skip_due_to_drift: str | None = None
        if (
            stop_rules.snapshot_drift_enabled
            and snapshot_start is not None
            and _is_apply_stage(stage.label, stop_rules.snapshot_drift_apply_labels)
        ):
            current_snapshot = compute_snapshot(target_dir, files=[])
            snapshot_pre_apply = current_snapshot
            drift = detect_snapshot_drift(snapshot_start, current_snapshot)
            if drift:
                skip_due_to_drift = drift
        if skip_due_to_drift:
            stage_dir = (
                run_dir / "stages" / f"{index:02d}-{stage.label.replace('/', '-')}"
            )
            stage_dir.mkdir(parents=True, exist_ok=True)
            decision: Decision = {
                "verdict": "skip",
                "reason": f"snapshot_drift:{skip_due_to_drift}",
            }
            evidence: list[EvidenceItem] = [
                {"kind": "snapshot_drift", "ref": skip_due_to_drift},
            ]
            stage_results.append(
                StageResult(
                    label=stage.label,
                    command=[],
                    returncode=0,
                    stdout_path="",
                    stderr_path="",
                    last_message_path="",
                    last_message="",
                    usefulness_score=None,
                    stop_reason=f"snapshot_drift:{skip_due_to_drift}",
                    thread_id=None,
                    head_before=capture_head_sha(target_dir),
                    head_after=capture_head_sha(target_dir),
                    elapsed_seconds=0.0,
                    validation_summary=None,
                    decision=decision,
                    evidence=evidence,
                )
            )
            stop_reason = f"stopped:{stage.label}:snapshot_drift:{skip_due_to_drift}"
            break
        result = run_stage(
            codex_bin=args.codex_bin,
            stage=stage,
            stage_index=index,
            target_dir=target_dir,
            run_dir=run_dir,
            session_id=session_id,
            profile=args.profile,
            usefulness_threshold=workflow.usefulness_threshold,
            stop_rules=stop_rules,
            run_started_at=run_started_at,
        )
        stage_results.append(result)
        if result.returncode != 0:
            stop_reason = f"stage_failed:{stage.label}"
            break
        if session_id is None:
            session_file = discover_session_file(session_snapshot, sessions_dir)
            session_id = read_session_id(session_file)
        if result.stop_reason is not None:
            stop_reason = f"stopped:{stage.label}:{result.stop_reason}"
            break
    manifest: dict[str, Any] = {
        "workflow": workflow.name,
        "workflow_path": str(workflow_path),
        "target_dir": str(target_dir),
        "session_id": session_id,
        "session_file": str(session_file) if session_file else None,
        "profile": args.profile,
        "stop_reason": stop_reason or "completed",
        "run_elapsed_seconds": round(time.monotonic() - run_started_at, 3),
        "stages": [asdict(result) for result in stage_results],
    }
    if snapshot_start is not None:
        manifest["snapshot_start"] = snapshot_start
    if snapshot_pre_apply is not None:
        manifest["snapshot_pre_apply"] = snapshot_pre_apply
    write_json(manifest_path, manifest)
    print(str(manifest_path))
    if stop_reason and stop_reason.startswith("stage_failed:"):
        return 1
    return 0


def main() -> int:
    try:
        return run()
    except JanitorError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
