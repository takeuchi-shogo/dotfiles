from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any


USEFULNESS_RE = re.compile(r"Usefulness score:\s*(\d+)/10\b", re.IGNORECASE)


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
class WorkflowDefinition:
    name: str
    description: str
    prompt: WorkflowPrompt
    counts: dict[str, int]
    usefulness_threshold: int
    stages: list[StageDefinition]


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


def decide_stop_reason(
    stage: ExpandedStage,
    *,
    last_message: str,
    usefulness_score: int | None,
    usefulness_threshold: int,
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
) -> StageResult:
    stage_slug = stage.label.replace("/", "-")
    stage_dir = run_dir / "stages" / f"{stage_index:02d}-{stage_slug}"
    stage_last_message_path = stage_dir / "last-message.txt"
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
    stdout_path = stage_dir / "stdout.jsonl"
    stderr_path = stage_dir / "stderr.log"
    write_text(stdout_path, completed.stdout)
    write_text(stderr_path, completed.stderr)
    last_message = ""
    if stage_last_message_path.exists():
        last_message = stage_last_message_path.read_text(encoding="utf-8")
    usefulness_score = parse_usefulness_score(last_message)
    stop_reason = None
    if completed.returncode == 0:
        stop_reason = decide_stop_reason(
            stage,
            last_message=last_message,
            usefulness_score=usefulness_score,
            usefulness_threshold=usefulness_threshold,
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
    )


def build_run_id(workflow_name: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = workflow_name.lower().replace(" ", "-")
    return f"{timestamp}-{slug}"


def print_dry_run(stages: list[ExpandedStage]) -> None:
    for index, stage in enumerate(stages, start=1):
        print(f"{index:02d}. {stage.label}")
        print(stage.prompt)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    workflow_path = Path(args.workflow)
    target_dir = Path(args.target_dir).resolve()
    output_root = Path(args.output_root)
    sessions_dir = Path(args.sessions_dir).expanduser()
    workflow = load_workflow(workflow_path)
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
    for index, stage in enumerate(stages, start=1):
        result = run_stage(
            codex_bin=args.codex_bin,
            stage=stage,
            stage_index=index,
            target_dir=target_dir,
            run_dir=run_dir,
            session_id=session_id,
            profile=args.profile,
            usefulness_threshold=workflow.usefulness_threshold,
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
    manifest = {
        "workflow": workflow.name,
        "workflow_path": str(workflow_path),
        "target_dir": str(target_dir),
        "session_id": session_id,
        "session_file": str(session_file) if session_file else None,
        "profile": args.profile,
        "stop_reason": stop_reason or "completed",
        "stages": [asdict(result) for result in stage_results],
    }
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
