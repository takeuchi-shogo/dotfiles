#!/usr/bin/env python3
"""R-13: ハーネスコンポーネント陳腐化検出.

hook 発火率・advisory 採用率・reference 参照率を追跡し、
不要なコンポーネントを検出する。

Anthropic の核心原則:
  "ハーネスの各コンポーネントはモデルの限界への仮定をエンコードしている。
   仮定は陳腐化する。"

Usage:
    python staleness-detector.py [--days 30]
    python staleness-detector.py --memory [--days 30]

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


# メモリファイルの重要度ウェイト（type フィールドに対応）
IMPORTANCE_WEIGHTS: dict[str, float] = {
    "feedback": 1.0,
    "user": 0.8,
    "project": 0.6,
    "reference": 0.5,
}
DEFAULT_IMPORTANCE = 0.5


def parse_memory_index(memory_md_path: Path) -> dict[str, list[str]]:
    """MEMORY.md を読み込み、各行のリンク構造を解析する.

    MEMORY.md 内の `[Title](file.md)` 形式リンクを行単位で抽出し、
    各メモリファイルが参照しているファイル名のリストを返す。

    Returns:
        {"file.md": ["referenced_file1.md", ...]} の形式。
        キーは行内で最初に出現したリンク先ファイル名（その行の「主体」）、
        値はその行内で他に参照されているファイル名のリスト。
    """
    import re

    if not memory_md_path.exists():
        return {}

    link_pattern = re.compile(r"\[.*?\]\((.*?\.md)\)")
    index: dict[str, list[str]] = {}

    for line in memory_md_path.read_text(encoding="utf-8").splitlines():
        matches = link_pattern.findall(line)
        if not matches:
            continue
        # 行内の先頭リンクを「主体」、残りをその参照先とみなす
        subject = matches[0]
        refs = matches[1:]
        if refs:
            index.setdefault(subject, []).extend(refs)

    return index


def analyze_memory_staleness(memory_dir: Path, days: int = 30) -> list[dict]:
    """memory_dir 内の全 .md ファイルの鮮度を分析する.

    MEMORY.md を除いた各ファイルについて:
    - git 最終更新日を取得（失敗時は days_old=999）
    - freshness_score = exp(-0.1 * days_since_update) を計算
    - frontmatter の type フィールドから importance_weight を決定
    - effective_score = freshness_score * importance_weight

    Returns:
        各ファイルの分析結果 dict のリスト。
    """
    import math
    import subprocess

    results = []
    now = datetime.now(timezone.utc)

    for md_file in sorted(memory_dir.glob("*.md")):
        # MEMORY.md 自体はスキップ
        if md_file.name == "MEMORY.md":
            continue

        # git で最終コミット日時を取得
        try:
            proc = subprocess.run(
                ["git", "log", "-1", "--format=%aI", "--", str(md_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            git_date_str = proc.stdout.strip()
            if git_date_str:
                git_date = datetime.fromisoformat(git_date_str)
                # タイムゾーン情報がない場合は UTC とみなす
                if git_date.tzinfo is None:
                    git_date = git_date.replace(tzinfo=timezone.utc)
                days_old = (now - git_date).days
            else:
                # git 履歴になければファイル更新日時をフォールバックに使う
                mtime = md_file.stat().st_mtime
                days_old = int((now.timestamp() - mtime) / 86400)
        except Exception:
            days_old = 999

        # freshness スコアを指数減衰で計算
        freshness_score = math.exp(-0.1 * days_old)

        # frontmatter から type フィールドを簡易抽出（PyYAML 不使用）
        file_type = _extract_frontmatter_type(md_file)
        importance_weight = IMPORTANCE_WEIGHTS.get(file_type, DEFAULT_IMPORTANCE)

        # 実効スコア
        effective_score = freshness_score * importance_weight

        # ステータス判定
        if effective_score >= 0.50:
            status = "fresh"
        elif effective_score >= 0.05:
            status = "aging"
        else:
            status = "stale"

        results.append(
            {
                "file": md_file.name,
                "days_old": days_old,
                "freshness": round(freshness_score, 4),
                "importance": importance_weight,
                "effective_score": round(effective_score, 4),
                "type": file_type,
                "status": status,
            }
        )

    return results


def _extract_frontmatter_type(md_file: Path) -> str:
    """markdown ファイルの frontmatter から type フィールドを抽出する.

    `---` で囲まれた YAML ブロック内の `type: value` を正規表現で読み取る。
    frontmatter がない場合や type フィールドがない場合は空文字を返す。
    """
    import re

    type_pattern = re.compile(r"^type:\s*(.+)$", re.MULTILINE)
    try:
        content = md_file.read_text(encoding="utf-8")
    except OSError:
        return ""

    # frontmatter ブロック（先頭 --- から次の --- まで）を抽出
    if not content.startswith("---"):
        return ""

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return ""

    frontmatter = content[3:end_idx]
    match = type_pattern.search(frontmatter)
    return match.group(1).strip() if match else ""


def propagate_staleness(file_scores: list[dict], memory_md_path: Path) -> list[dict]:
    """stale なファイルを参照するファイルにカスケード警告を付与する.

    parse_memory_index() で MEMORY.md のリンク構造を取得し、
    stale なファイルを参照しているファイルに cascading_warning=True と
    stale_refs リストを追加する。

    Returns:
        cascading_warning / stale_refs フィールドを追加した file_scores のコピー。
    """
    index = parse_memory_index(memory_md_path)

    # stale なファイル名のセットを作成
    stale_files: set[str] = {
        entry["file"] for entry in file_scores if entry["status"] == "stale"
    }

    # file_scores を dict に変換して更新しやすくする
    scores_by_name: dict[str, dict] = {
        entry["file"]: dict(entry) for entry in file_scores
    }

    for subject, refs in index.items():
        # MEMORY.md のリンク構造に存在するファイルのみ対象
        if subject not in scores_by_name:
            continue
        stale_ref_list = [r for r in refs if r in stale_files]
        if stale_ref_list:
            scores_by_name[subject]["cascading_warning"] = True
            existing = scores_by_name[subject].get("stale_refs", [])
            scores_by_name[subject]["stale_refs"] = list(
                dict.fromkeys(existing + stale_ref_list)
            )

    return list(scores_by_name.values())


def generate_memory_report(results: list[dict], days: int) -> str:
    """メモリファイルの鮮度レポートを生成する.

    セクション: Stale Memories, Cascading Warnings, Aging Memories, Fresh Memories。
    形式は既存の generate_report() に合わせ
    [MEMORY_STALENESS_REPORT] プレフィックスを使用。
    """
    stale = [r for r in results if r["status"] == "stale"]
    aging = [r for r in results if r["status"] == "aging"]
    fresh = [r for r in results if r["status"] == "fresh"]
    cascading = [r for r in results if r.get("cascading_warning")]

    lines = [
        f"[MEMORY_STALENESS_REPORT] Analysis period: {days} days",
        f"  Total files: {len(results)}, "
        f"Fresh: {len(fresh)}, "
        f"Aging: {len(aging)}, "
        f"Stale: {len(stale)}, "
        f"Cascading warnings: {len(cascading)}",
        "",
    ]

    if stale:
        lines.append("## Stale Memories (更新候補)")
        for r in sorted(stale, key=lambda x: -x["days_old"]):
            lines.append(
                f"  - [STALE] {r['file']}: "
                f"{r['days_old']} 日更新なし "
                f"(effective={r['effective_score']:.4f}, type={r['type'] or 'unknown'})"
            )
        lines.append("")

    if cascading:
        lines.append("## Cascading Warnings (stale 参照あり)")
        for r in cascading:
            stale_refs = ", ".join(r.get("stale_refs", []))
            lines.append(f"  - [CASCADE] {r['file']}: stale な参照先 -> {stale_refs}")
        lines.append("")

    if aging:
        lines.append("## Aging Memories (経過観察)")
        for r in sorted(aging, key=lambda x: -x["days_old"]):
            lines.append(
                f"  - {r['file']}: "
                f"{r['days_old']} 日更新なし "
                f"(effective={r['effective_score']:.4f}, type={r['type'] or 'unknown'})"
            )
        lines.append("")

    if fresh:
        lines.append("## Fresh Memories")
        for r in sorted(fresh, key=lambda x: x["days_old"]):
            lines.append(
                f"  - {r['file']}: "
                f"{r['days_old']} 日前更新 "
                f"(effective={r['effective_score']:.4f})"
            )
        lines.append("")

    if not results:
        lines.append("## No memory files found")
        lines.append("  分析対象の .md ファイルが見つかりませんでした。")
        lines.append("")

    return "\n".join(lines)


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
    parser.add_argument(
        "--memory",
        action="store_true",
        help="Analyze memory file staleness",
    )
    args = parser.parse_args()

    if args.rotate:
        removed = rotate_telemetry(args.days)
        print(f"[STALENESS] Rotated {removed} entries older than {args.days} days.")
        return

    if args.memory:
        # ~/.claude/projects/*/memory/MEMORY.md を全て検索して分析
        projects_dir = Path.home() / ".claude" / "projects"
        memory_dirs = [p.parent for p in projects_dir.glob("*/memory/MEMORY.md")]
        if not memory_dirs:
            print("[MEMORY_STALENESS] No memory directories found.")
            return
        for memory_dir in sorted(memory_dirs):
            memory_md = memory_dir / "MEMORY.md"
            file_scores = analyze_memory_staleness(memory_dir, args.days)
            file_scores = propagate_staleness(file_scores, memory_md)
            report = generate_memory_report(file_scores, args.days)
            print(f"# {memory_dir}")
            print(report)
        return

    telemetry = load_telemetry(args.days)
    registered = get_registered_hooks()
    hook_analysis = analyze_fire_rates(telemetry, registered, args.days)
    ref_usage = analyze_reference_usage(telemetry)

    report = generate_report(hook_analysis, ref_usage, args.days)
    print(report)


if __name__ == "__main__":
    main()
