#!/bin/sh
# Collect inputs for morning briefing
# Usage: collect-morning-inputs.sh [YYYY-MM-DD]   (default: today)
# Output: JSON object on stdout with sections: friction, open_prs, open_issues, stale_plans, yesterday_report_path
#
# Design: pure read-only. No network calls except gh (already authenticated).
# Failure: each section degrades to empty array on error so jq downstream stays valid.

set -u

TODAY="${1:-$(date +%Y-%m-%d)}"
# Yesterday relative to TODAY. macOS BSD date.
YESTERDAY=$(date -j -v-1d -f "%Y-%m-%d" "$TODAY" "+%Y-%m-%d" 2>/dev/null || date -d "$TODAY -1 day" "+%Y-%m-%d")

FRICTION_FILE="$HOME/.claude/agent-memory/learnings/friction-events.jsonl"
PLANS_DIR="$HOME/dotfiles/docs/plans/active"
DAILY_REPORTS="$HOME/daily-reports"

# --- friction events: 昨日 17:00 (JST) 以降のイベントのみ ---
# friction-events.jsonl is UTC ISO8601 (with +00:00 offset). Convert JST cutoff to UTC.
# JST 17:00 = UTC 08:00. epoch 経由で確実に UTC 化する (BSD date は -j + -u + TZ の組み合わせが期待通り動かないため)。
CUTOFF_LOCAL="${YESTERDAY} 17:00:00"
EPOCH=$(TZ=Asia/Tokyo date -j -f "%Y-%m-%d %H:%M:%S" "$CUTOFF_LOCAL" +%s 2>/dev/null \
    || TZ=Asia/Tokyo date -d "$CUTOFF_LOCAL" +%s 2>/dev/null)

if [ -z "$EPOCH" ]; then
    echo "[collect-morning-inputs] ERROR: failed to compute epoch for $CUTOFF_LOCAL" >&2
    exit 1
fi

CUTOFF_UTC=$(date -u -r "$EPOCH" "+%Y-%m-%dT%H:%M:%SZ" 2>/dev/null \
    || date -u -d "@$EPOCH" "+%Y-%m-%dT%H:%M:%SZ" 2>/dev/null)

if [ -z "$CUTOFF_UTC" ]; then
    echo "[collect-morning-inputs] ERROR: failed to format CUTOFF_UTC from epoch $EPOCH" >&2
    exit 1
fi

if [ -f "$FRICTION_FILE" ]; then
    friction=$(jq -c --arg cutoff "$CUTOFF_UTC" '
        select(.timestamp >= $cutoff) |
        {timestamp, friction_class, severity, target_hint, evidence}
    ' "$FRICTION_FILE" 2>/dev/null | jq -s '.' 2>/dev/null || echo "[]")
else
    friction="[]"
fi

# --- open PRs involving me ---
if command -v gh >/dev/null 2>&1; then
    open_prs=$(gh pr list --search "involves:@me state:open" \
        --json number,title,url,headRepository,updatedAt,statusCheckRollup \
        --limit 20 2>/dev/null || echo "[]")
else
    open_prs="[]"
fi

# --- open issues assigned to me ---
if command -v gh >/dev/null 2>&1; then
    open_issues=$(gh issue list --assignee=@me --state=open \
        --json number,title,url,repository,updatedAt \
        --limit 20 2>/dev/null || echo "[]")
else
    open_issues="[]"
fi

# --- stale plans: docs/plans/active で mtime 7 日以上前 ---
# find -mtime +7 で 7 日以上前の mtime を抽出。stat 失敗行はスキップ (壊れた JSON line を作らない)。
if [ -d "$PLANS_DIR" ]; then
    stale_plans=$(find "$PLANS_DIR" -maxdepth 1 -name "*.md" -mtime +7 2>/dev/null | \
        while IFS= read -r f; do
            mtime=$(stat -f "%Sm" -t "%Y-%m-%d" "$f" 2>/dev/null || stat -c "%y" "$f" 2>/dev/null | cut -d' ' -f1)
            [ -z "$mtime" ] && continue
            name=$(basename "$f")
            printf '{"name":%s,"mtime":%s}\n' "$(jq -Rn --arg v "$name" '$v')" "$(jq -Rn --arg v "$mtime" '$v')"
        done | jq -s '.' 2>/dev/null || echo "[]")
else
    stale_plans="[]"
fi

# --- yesterday daily-report path (existence check only) ---
yesterday_report="$DAILY_REPORTS/${YESTERDAY}.md"
if [ -f "$yesterday_report" ]; then
    yesterday_report_path=$(jq -Rn --arg v "$yesterday_report" '$v')
else
    yesterday_report_path="null"
fi

# --- assemble ---
jq -n \
    --arg today "$TODAY" \
    --arg yesterday "$YESTERDAY" \
    --argjson friction "$friction" \
    --argjson open_prs "$open_prs" \
    --argjson open_issues "$open_issues" \
    --argjson stale_plans "$stale_plans" \
    --argjson yesterday_report_path "$yesterday_report_path" \
    '{
        today: $today,
        yesterday: $yesterday,
        friction_since_yesterday_17: $friction,
        open_prs: $open_prs,
        open_issues: $open_issues,
        stale_plans_over_7d: $stale_plans,
        yesterday_report_path: $yesterday_report_path
    }'
