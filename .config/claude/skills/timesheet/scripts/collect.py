#!/usr/bin/env python3
"""カレントの git repo での月次稼働を、ローカルのログと GitHub から集計する。

ソース: Claude Code のログ / git reflog とコミット / GitHub の自分の操作
出力: 時間帯 (30 分丸め) ごとの勤務時間と、メモ下書き用の発言・コミット件名

usage: collect.py [YYYY-MM] [--merge-gap 60] [--min-span 10] [--no-github]
       collect.py --self-test
"""

import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

JST = dt.timezone(dt.timedelta(hours=9))
CLAUDE_PROJECTS = os.path.expanduser("~/.claude/projects")


def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"{' '.join(cmd)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def parse_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(JST)


def repo_context():
    common = run("git", "rev-parse", "--path-format=absolute", "--git-common-dir")
    worktrees = [
        line.split(maxsplit=1)[1]
        for line in run("git", "worktree", "list", "--porcelain").splitlines()
        if line.startswith("worktree ")
    ]
    return {
        "git_dir": common,
        "worktrees": worktrees,
        "author": run("git", "config", "user.email"),
    }


def claude_project_dirs(worktrees):
    dirs = set()
    for path in worktrees:
        encoded = re.sub(r"[^A-Za-z0-9]", "-", path)
        dirs.add(os.path.join(CLAUDE_PROJECTS, encoded))
        dirs.update(
            glob.glob(os.path.join(CLAUDE_PROJECTS, encoded + "--claude-worktrees-*"))
        )
    return [d for d in dirs if os.path.isdir(d)]


def claude_events(dirs, start, end):
    """(時刻, ユーザー発言 or None) を返す。subagent のログは時刻のみ使う。"""
    out = []
    for path in (p for d in dirs for p in glob.glob(d + "/**/*.jsonl", recursive=True)):
        is_sub = "subagents" in path
        with open(path, errors="ignore") as f:
            for line in f:
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not o.get("timestamp"):
                    continue
                t = parse_iso(o["timestamp"])
                if start <= t < end:
                    out.append((t, None if is_sub else user_text(o)))
    return out


def user_text(o):
    if o.get("type") != "user":
        return None
    content = o.get("message", {}).get("content")
    if not isinstance(content, str) or content.startswith("<"):
        return None
    return content.replace("\n", " ")[:80]


def git_events(ctx, start, end):
    """reflog (main + worktree) とコミットの時刻。コミットは件名も返す。"""
    out = []
    logs = glob.glob(f"{ctx['git_dir']}/logs/**/*", recursive=True)
    logs += glob.glob(f"{ctx['git_dir']}/worktrees/*/logs/**/*", recursive=True)
    for path in filter(os.path.isfile, logs):
        with open(path, errors="ignore") as f:
            for line in f:
                head = line.split("\t", 1)[0].split()
                if len(head) < 2 or not head[-2].isdigit():
                    continue
                t = dt.datetime.fromtimestamp(int(head[-2]), JST)
                if start <= t < end:
                    out.append((t, None))
    log = run(
        "git",
        "log",
        "--all",
        f"--author={ctx['author']}",
        "--format=%at\t%s",
        f"--since={start.isoformat()}",
        f"--until={end.isoformat()}",
    )
    for line in filter(None, log.splitlines()):
        at, subject = line.split("\t", 1)
        out.append((dt.datetime.fromtimestamp(int(at), JST), "commit: " + subject[:70]))
    return out


def gh(path):
    pages = json.loads(run("gh", "api", "--paginate", "--slurp", path))
    if pages and isinstance(pages[0], dict) and "items" in pages[0]:
        return [i for p in pages for i in p["items"]]
    return [i for p in pages for i in p]


def github_events(start, end):
    """自分が関わった Issue/PR 上の、自分のコメント・レビュー・起票の時刻。"""
    repo = run("gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")
    me = run("gh", "api", "user", "-q", ".login")
    q = f"repo:{repo}+involves:{me}+updated:>={start:%Y-%m-%d}"
    out = []
    for it in gh(f"search/issues?q={q}&per_page=100"):
        n = it["number"]
        stamps = [it["created_at"]] if it["user"]["login"] == me else []
        paths = [f"repos/{repo}/issues/{n}/comments"]
        if "pull_request" in it:
            paths += [
                f"repos/{repo}/pulls/{n}/comments",
                f"repos/{repo}/pulls/{n}/reviews",
            ]
        for p in paths:
            for c in gh(p + "?per_page=100"):
                stamp = c.get("created_at") or c.get("submitted_at")
                if c["user"]["login"] == me and stamp:
                    stamps.append(stamp)
        out += [(t, None) for t in map(parse_iso, stamps) if start <= t < end]
    return out


def round30(t):
    t = t + dt.timedelta(minutes=15)
    return t.replace(minute=t.minute // 30 * 30, second=0, microsecond=0)


def rounded_span(first, last):
    s, e = round30(first), round30(last)
    return s, max(e, s + dt.timedelta(minutes=30))


def sheet_time(t, base_day):
    """日をまたぐ時刻は 25:30 形式。勤務表は D-C で計算するので 1:30 だと負になる。"""
    h = t.hour + 24 * (t.date() - base_day).days
    return f"{h}:{t.minute:02d}"


def spans(events, merge_gap, min_span):
    events.sort(key=lambda e: e[0])
    groups = [[events[0]]]
    for e in events[1:]:
        if e[0] - groups[-1][-1][0] <= merge_gap:
            groups[-1].append(e)
        else:
            groups.append([e])
    return [g for g in groups if g[-1][0] - g[0][0] >= min_span]


def month_range(month):
    y, m = map(int, month.split("-"))
    start = dt.datetime(y, m, 1, tzinfo=JST)
    end = dt.datetime(y + m // 12, m % 12 + 1, 1, tzinfo=JST)
    today = dt.datetime.now(JST).replace(hour=0, minute=0, second=0, microsecond=0)
    return start, min(end, today)


def report(groups):
    total = 0.0
    per_day = defaultdict(float)
    for g in groups:
        s, e = rounded_span(g[0][0], g[-1][0])
        hours = (e - s).total_seconds() / 3600
        hours -= 1 if hours > 6 else 0
        day = g[0][0].date()
        total += hours
        per_day[day] += hours
        span = f"{sheet_time(s, day)}-{sheet_time(e, day)}"
        raw = f"{g[0][0]:%H:%M}-{g[-1][0]:%H:%M}"
        print(f"## {day:%Y/%m/%d} {span} ({hours:.1f}h)  raw {raw}")
        for t, text in g:
            if text:
                print(f"  {t:%H:%M} {text}")
    print("\n# 日別")
    for d in sorted(per_day):
        print(f"{d:%m/%d} {per_day[d]:.1f}h")
    print(f"合計 {total:.1f}h")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("month", nargs="?", default=dt.datetime.now(JST).strftime("%Y-%m"))
    ap.add_argument(
        "--merge-gap", type=int, default=60, help="この分数以内の空きはつなぐ"
    )
    ap.add_argument(
        "--min-span", type=int, default=10, help="この分数未満の時間帯は捨てる"
    )
    ap.add_argument("--no-github", action="store_true", help="gh を使わない")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    start, end = month_range(a.month)
    ctx = repo_context()
    events = claude_events(claude_project_dirs(ctx["worktrees"]), start, end)
    events += git_events(ctx, start, end)
    if not a.no_github:
        events += github_events(start, end)
    if not events:
        sys.exit(f"no events in {a.month}")
    gap, min_span = dt.timedelta(minutes=a.merge_gap), dt.timedelta(minutes=a.min_span)
    report(spans(events, gap, min_span))


def self_test():
    def t(h, mi, d=1):
        return dt.datetime(2026, 10, d, h, mi, tzinfo=JST)

    assert round30(t(7, 14)) == t(7, 0) and round30(t(7, 15)) == t(7, 30)
    assert round30(t(23, 50)) == t(0, 0, 2)
    assert rounded_span(t(10, 59), t(11, 31)) == (t(11, 0), t(11, 30))
    assert rounded_span(t(22, 15), t(22, 25)) == (t(22, 30), t(23, 0))
    assert sheet_time(t(1, 30, 2), t(0, 0).date()) == "25:30"
    ev = [
        (t(h, m), None) for h, m in [(7, 0), (7, 50), (9, 0), (9, 5), (12, 0), (12, 20)]
    ]
    got = [
        (g[0][0], g[-1][0])
        for g in spans(ev, dt.timedelta(minutes=60), dt.timedelta(minutes=10))
    ]
    assert got == [(t(7, 0), t(7, 50)), (t(12, 0), t(12, 20))], got
    assert (
        re.sub(r"[^A-Za-z0-9]", "-", "/Users/a/dev-app/x/app")
        == "-Users-a-dev-app-x-app"
    )
    print("ok")


if __name__ == "__main__":
    main()
