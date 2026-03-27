#!/usr/bin/env python3
"""R-13: ハーネスコンポーネント陳腐化検出.

hook 発火率・advisory 採用率・reference 参照率を追跡し、
不要なコンポーネントを検出する。

Anthropic の核心原則:
  "ハーネスの各コンポーネントはモデルの限界への仮定をエンコードしている。
   仮定は陳腐化する。"

Usage:
    python staleness-detector.py [--days 30]

出力: 陳腐化レポート (stdout)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from storage import get_data_dir, read_jsonl

# 閾値
DEFAULT_DAYS = 30
STALE_HOOK_FIRE_COUNT = 0  # 期間内に 0 回発火で陳腐化候補
LOW_ADOPTION_RATE = 0.10  # advisory 採用率 10% 未満で警告

# hook-telemetry.jsonl のパス
TELEMETRY_FILENAME = "hook-telemetry.jsonl"


def get_telemetry_path() -> Path:
    """hook-telemetry.jsonl のパスを返す."""
    return get_data_dir() / "logs" / TELEMETRY_FILENAME


def load_telemetry(days: int) -> list[dict]:
    """指定期間内の hook テレメトリを読み込む."""
    path = get_telemetry_path()
    if not path.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.isoformat()

    entries = read_jsonl(path)
    return [e for e in entries if e.get("timestamp", "") >= cutoff_str]


def get_registered_hooks() -> list[str]:
    """settings.json から登録済み hook スクリプト名を抽出."""
    import json

    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.exists():
        return []

    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    hooks_config = settings.get("hooks", {})
    hook_names: set[str] = set()

    for _event, hook_list in hooks_config.items():
        if not isinstance(hook_list, list):
            continue
        for entry in hook_list:
            if isinstance(entry, dict):
                for hook in entry.get("hooks", []):
                    if isinstance(hook, dict):
                        cmd = hook.get("command", "")
                    else:
                        cmd = str(hook)
                    name = _extract_hook_name(cmd)
                    if name:
                        hook_names.add(name)

    return sorted(hook_names)


def _extract_hook_name(command: str) -> str:
    """コマンド文字列から hook スクリプト名を抽出."""
    if not command:
        return ""
    parts = command.split()
    for part in parts:
        if part.endswith(".py") or part.endswith(".sh"):
            return Path(part).stem
        if "/" in part and ("scripts/" in part or ".bin/" in part):
            return Path(part).stem
    return ""


def analyze_fire_rates(
    telemetry: list[dict], registered: list[str], days: int
) -> list[dict]:
    """hook 発火率を分析."""
    fire_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}

    for entry in telemetry:
        hook = entry.get("hook_name", "")
        if hook:
            fire_counts[hook] = fire_counts.get(hook, 0) + 1
            if entry.get("action_taken", False):
                action_counts[hook] = action_counts.get(hook, 0) + 1

    results = []
    for hook in registered:
        fires = fire_counts.get(hook, 0)
        actions = action_counts.get(hook, 0)
        adoption = round(actions / fires, 2) if fires > 0 else 0.0

        status = "active"
        if fires == STALE_HOOK_FIRE_COUNT:
            status = "stale"
        elif fires > 0 and adoption < LOW_ADOPTION_RATE:
            status = "low_adoption"

        results.append(
            {
                "hook": hook,
                "fire_count": fires,
                "action_count": actions,
                "adoption_rate": adoption,
                "status": status,
                "period_days": days,
            }
        )

    return results


def analyze_reference_usage(
    telemetry: list[dict],
) -> list[dict]:
    """reference 参照率を分析."""
    ref_counts: dict[str, int] = {}
    for entry in telemetry:
        if entry.get("type") == "reference_access":
            ref = entry.get("reference", "")
            if ref:
                ref_counts[ref] = ref_counts.get(ref, 0) + 1

    return [
        {"reference": ref, "access_count": count}
        for ref, count in sorted(ref_counts.items(), key=lambda x: x[1])
    ]


def generate_report(
    hook_analysis: list[dict],
    ref_usage: list[dict],
    days: int,
) -> str:
    """陳腐化レポートを生成."""
    stale = [h for h in hook_analysis if h["status"] == "stale"]
    low_adopt = [h for h in hook_analysis if h["status"] == "low_adoption"]
    active = [h for h in hook_analysis if h["status"] == "active"]

    lines = [
        f"[STALENESS_REPORT] Analysis period: {days} days",
        f"  Total hooks: {len(hook_analysis)}, "
        f"Active: {len(active)}, "
        f"Stale: {len(stale)}, "
        f"Low adoption: {len(low_adopt)}",
        "",
    ]

    if stale:
        lines.append("## Stale Hooks (除去候補)")
        for h in stale:
            lines.append(f"  - [STALE_HOOK] {h['hook']}: {days} 日間で 0 回発火")
        lines.append("")

    if low_adopt:
        lines.append("## Low Adoption Advisories")
        for h in low_adopt:
            lines.append(
                f"  - {h['hook']}: {h['fire_count']} fires, "
                f"adoption {h['adoption_rate']:.0%} "
                f"({h['action_count']}/{h['fire_count']})"
            )
            lines.append("    -> advisory が無視されている可能性")
        lines.append("")

    if active:
        lines.append("## Active Hooks")
        for h in sorted(active, key=lambda x: -x["fire_count"]):
            lines.append(
                f"  - {h['hook']}: {h['fire_count']} fires, "
                f"adoption {h['adoption_rate']:.0%}"
            )
        lines.append("")

    if not hook_analysis:
        lines.append("## No telemetry data found")
        lines.append("  hook-telemetry.jsonl が未作成または空です。")
        lines.append("  hooks が emit_telemetry() を呼ぶと データが蓄積されます。")
        lines.append("")

    if ref_usage:
        lines.append("## Reference Usage")
        for r in ref_usage:
            lines.append(f"  - {r['reference']}: {r['access_count']} accesses")

    return "\n".join(lines)


def emit_telemetry_entry(
    hook_name: str,
    fired: bool = True,
    action_taken: bool = False,
    entry_type: str = "hook_fire",
    extra: dict | None = None,
) -> None:
    """hook テレメトリエントリを hook-telemetry.jsonl に追記.

    他の hook スクリプトからインポートして使う共有関数。
    """
    import json
    from datetime import datetime, timezone

    path = get_telemetry_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": entry_type,
        "hook_name": hook_name,
        "fired": fired,
        "action_taken": action_taken,
        **(extra or {}),
    }

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def rotate_telemetry(days: int = 30) -> int:
    """指定日数より古いエントリを除去. 除去件数を返す."""
    path = get_telemetry_path()
    if not path.exists():
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.isoformat()

    entries = read_jsonl(path)
    kept = [e for e in entries if e.get("timestamp", "") >= cutoff_str]
    removed = len(entries) - len(kept)

    if removed > 0:
        import json

        with open(path, "w", encoding="utf-8") as f:
            for entry in kept:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description="R-13: Staleness detector")
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help="Analysis period in days",
    )
    parser.add_argument(
        "--rotate",
        action="store_true",
        help="Rotate old telemetry entries",
    )
    args = parser.parse_args()

    if args.rotate:
        removed = rotate_telemetry(args.days)
        print(f"[STALENESS] Rotated {removed} entries older than {args.days} days.")
        return

    telemetry = load_telemetry(args.days)
    registered = get_registered_hooks()
    hook_analysis = analyze_fire_rates(telemetry, registered, args.days)
    ref_usage = analyze_reference_usage(telemetry)

    report = generate_report(hook_analysis, ref_usage, args.days)
    print(report)


if __name__ == "__main__":
    main()
