#!/usr/bin/env python3
"""Generate a self-contained HTML dashboard for skill evolution loop monitoring.

Usage:
    python3 generate_dashboard.py <path-to-dashboard-state.json>

Reads dashboard-state.json and produces dashboard.html in the same directory.
"""

import json
import sys
from pathlib import Path


def build_html(data: dict | None) -> str:
    """Build a self-contained HTML dashboard string."""

    if data is None:
        return _build_waiting_html()

    skill_name = data.get("skill_name", "Unknown Skill")
    started_at = data.get("started_at", "N/A")
    target_score = data.get("target_score", 1.0)
    baseline_score = data.get("baseline_score", 0.0)
    rounds = data.get("rounds", [])
    status = data.get("status", "unknown")

    # Prepare chart data
    round_labels = [str(r.get("round", i + 1)) for i, r in enumerate(rounds)]
    pass_rates = [r.get("checklist_pass_rate", 0) for r in rounds]

    # Collect all unique checklist questions across rounds
    all_questions: list[str] = []
    seen: set[str] = set()
    for r in rounds:
        for item in r.get("checklist_breakdown", []):
            q = item.get("question", "")
            if q and q not in seen:
                all_questions.append(q)
                seen.add(q)

    # Build per-question pass/fail matrix
    checklist_matrix_rows = ""
    for q in all_questions:
        cells = ""
        for r in rounds:
            found = False
            for item in r.get("checklist_breakdown", []):
                if item.get("question") == q:
                    passed = item.get("passed", False)
                    icon = "&#10003;" if passed else "&#10007;"
                    cls = "pass" if passed else "fail"
                    cells += f'<td class="{cls}">{icon}</td>'
                    found = True
                    break
            if not found:
                cells += '<td class="na">&mdash;</td>'
        checklist_matrix_rows += (
            f"<tr><td class='q-label'>{_escape(q)}</td>{cells}</tr>\n"
        )

    # Build rounds log rows
    rounds_log_rows = ""
    for r in rounds:
        rnd = r.get("round", "?")
        hypothesis = _escape(r.get("hypothesis", ""))
        verdict = r.get("verdict", "unknown")
        delta = r.get("delta_pp", 0)
        quality = r.get("quality_score", "N/A")
        verdict_cls = (
            "verdict-keep"
            if verdict == "keep"
            else "verdict-revert"
            if verdict == "revert"
            else ""
        )
        delta_sign = f"+{delta}" if delta >= 0 else str(delta)
        rounds_log_rows += (
            f"<tr>"
            f"<td>{rnd}</td>"
            f"<td class='hypo'>{hypothesis}</td>"
            f"<td class='{verdict_cls}'>{verdict}</td>"
            f"<td>{delta_sign}pp</td>"
            f"<td>{quality}</td>"
            f"</tr>\n"
        )

    # Status badge
    if status == "running":
        badge_cls = "badge-running"
        badge_text = "Running"
    elif status == "completed":
        badge_cls = "badge-completed"
        badge_text = "Completed"
    else:
        badge_cls = "badge-stopped"
        badge_text = status.capitalize() if status else "Unknown"

    # Round headers for checklist matrix
    round_headers = "".join(
        f"<th>R{r.get('round', i + 1)}</th>" for i, r in enumerate(rounds)
    )

    latest_rate = pass_rates[-1] if pass_rates else baseline_score
    progress_pct = (
        min(
            100,
            max(
                0,
                int(
                    (latest_rate - baseline_score)
                    / (target_score - baseline_score)
                    * 100
                ),
            ),
        )
        if target_score != baseline_score
        else 100
    )

    # Pre-build font stack to keep template lines short
    font_stack = (
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
    )

    # Pre-build empty-state rows
    empty_checklist = (
        '<tr><td colspan="100" '
        'style="color:var(--text-muted);'
        'text-align:center;">'
        "No checklist data</td></tr>"
    )
    empty_rounds = (
        '<tr><td colspan="5" '
        'style="color:var(--text-muted);'
        'text-align:center;">'
        "No rounds yet</td></tr>"
    )
    checklist_body = checklist_matrix_rows if checklist_matrix_rows else empty_checklist
    rounds_body = rounds_log_rows if rounds_log_rows else empty_rounds

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="10">
<title>Skill Evolution Dashboard &mdash; {_escape(skill_name)}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --surface2: #1c2333;
    --border: #30363d;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --green: #3fb950;
    --red: #f85149;
    --yellow: #d29922;
    --blue: #58a6ff;
    --gray: #6e7681;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: {font_stack};
    background: var(--bg);
    color: var(--text);
    padding: 24px;
    line-height: 1.6;
  }}
  .dashboard {{
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto auto;
    gap: 20px;
  }}
  .header {{
    grid-column: 1 / -1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
  }}
  .header h1 {{
    font-size: 1.4rem;
    font-weight: 600;
  }}
  .header h1 span {{
    color: var(--accent);
  }}
  .meta {{
    text-align: right;
    color: var(--text-muted);
    font-size: 0.85rem;
  }}
  .badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .badge-running {{
    background: rgba(88, 166, 255, 0.15);
    color: var(--blue);
    animation: pulse 2s infinite;
  }}
  .badge-completed {{
    background: rgba(63, 185, 80, 0.15);
    color: var(--green);
  }}
  .badge-stopped {{
    background: rgba(110, 118, 129, 0.15);
    color: var(--gray);
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
  }}
  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
  }}
  .card h2 {{
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 16px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.75rem;
  }}
  .chart-card {{
    grid-column: 1 / -1;
  }}
  .chart-container {{
    position: relative;
    height: 300px;
  }}
  .stats-row {{
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }}
  .stat {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
  }}
  .stat .value {{
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
  }}
  .stat .label {{
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
  }}
  .progress-bar {{
    grid-column: 1 / -1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
  }}
  .progress-bar .track {{
    height: 8px;
    background: var(--surface2);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
  }}
  .progress-bar .fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--blue), var(--green));
    border-radius: 4px;
    transition: width 0.5s ease;
  }}
  .progress-label {{
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: var(--text-muted);
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
  }}
  th, td {{
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .pass {{ color: var(--green); text-align: center; font-weight: bold; }}
  .fail {{ color: var(--red); text-align: center; font-weight: bold; }}
  .na {{ color: var(--gray); text-align: center; }}
  .q-label {{
    max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .verdict-keep {{ color: var(--green); font-weight: 600; }}
  .verdict-revert {{ color: var(--red); font-weight: 600; }}
  .hypo {{
    max-width: 350px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .table-scroll {{
    overflow-x: auto;
  }}
  @media (max-width: 768px) {{
    .dashboard {{
      grid-template-columns: 1fr;
    }}
    .stats-row {{
      grid-template-columns: repeat(2, 1fr);
    }}
  }}
</style>
</head>
<body>

<div class="dashboard">
  <div class="header">
    <div>
      <h1>Skill Evolution &mdash; <span>{_escape(skill_name)}</span></h1>
      <div class="meta">Started: {_escape(started_at)}</div>
    </div>
    <div>
      <span class="badge {badge_cls}">{badge_text}</span>
    </div>
  </div>

  <div class="stats-row">
    <div class="stat">
      <div class="value">{len(rounds)}</div>
      <div class="label">Rounds</div>
    </div>
    <div class="stat">
      <div class="value">{baseline_score:.0%}</div>
      <div class="label">Baseline</div>
    </div>
    <div class="stat">
      <div class="value">{latest_rate:.0%}</div>
      <div class="label">Current</div>
    </div>
    <div class="stat">
      <div class="value">{target_score:.0%}</div>
      <div class="label">Target</div>
    </div>
  </div>

  <div class="progress-bar">
    <div class="progress-label">
      <span>Progress to target</span>
      <span>{progress_pct}%</span>
    </div>
    <div class="track">
      <div class="fill" style="width: {progress_pct}%"></div>
    </div>
  </div>

  <div class="card chart-card">
    <h2>Score Trend</h2>
    <div class="chart-container">
      <canvas id="scoreChart"></canvas>
    </div>
  </div>

  <div class="card">
    <h2>Checklist Pass/Fail Matrix</h2>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Checklist Item</th>
            {round_headers}
          </tr>
        </thead>
        <tbody>
          {checklist_body}
        </tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <h2>Rounds Log</h2>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Hypothesis</th>
            <th>Verdict</th>
            <th>Delta</th>
            <th>Quality</th>
          </tr>
        </thead>
        <tbody>
          {rounds_body}
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
const ctx = document.getElementById('scoreChart').getContext('2d');
new Chart(ctx, {{
  type: 'line',
  data: {{
    labels: {json.dumps(round_labels)},
    datasets: [
      {{
        label: 'Checklist Pass Rate',
        data: {json.dumps(pass_rates)},
        borderColor: '#58a6ff',
        backgroundColor: 'rgba(88, 166, 255, 0.1)',
        borderWidth: 2,
        pointBackgroundColor: '#58a6ff',
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: true,
        tension: 0.3
      }},
      {{
        label: 'Target ({target_score:.0%})',
        data: Array({len(rounds) or 1}).fill({target_score}),
        borderColor: '#3fb950',
        borderWidth: 2,
        borderDash: [8, 4],
        pointRadius: 0,
        fill: false
      }},
      {{
        label: 'Baseline ({baseline_score:.0%})',
        data: Array({len(rounds) or 1}).fill({baseline_score}),
        borderColor: '#6e7681',
        borderWidth: 2,
        borderDash: [3, 3],
        pointRadius: 0,
        fill: false
      }}
    ]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{
        labels: {{
          color: '#8b949e',
          usePointStyle: true,
          padding: 20
        }}
      }}
    }},
    scales: {{
      x: {{
        title: {{
          display: true,
          text: 'Round',
          color: '#8b949e'
        }},
        ticks: {{ color: '#8b949e' }},
        grid: {{ color: 'rgba(48, 54, 61, 0.5)' }}
      }},
      y: {{
        min: 0,
        max: 1,
        title: {{
          display: true,
          text: 'Pass Rate',
          color: '#8b949e'
        }},
        ticks: {{
          color: '#8b949e',
          callback: function(v) {{ return (v * 100) + '%'; }}
        }},
        grid: {{ color: 'rgba(48, 54, 61, 0.5)' }}
      }}
    }}
  }}
}});
</script>

</body>
</html>"""


def _build_waiting_html() -> str:
    """Build HTML for when no data is available yet."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="10">
<title>Skill Evolution Dashboard &mdash; Waiting</title>
<style>
  :root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --blue: #58a6ff;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family:
      -apple-system, BlinkMacSystemFont,
      'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
  }
  .waiting {
    text-align: center;
    padding: 48px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    max-width: 480px;
  }
  .spinner {
    width: 48px;
    height: 48px;
    border: 4px solid var(--border);
    border-top-color: var(--blue);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 24px;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  h1 {
    font-size: 1.3rem;
    margin-bottom: 12px;
  }
  p {
    color: var(--text-muted);
    font-size: 0.9rem;
  }
</style>
</head>
<body>
<div class="waiting">
  <div class="spinner"></div>
  <h1>Waiting for data&hellip;</h1>
  <p>The dashboard will auto-refresh every 10 seconds.<br>
  Ensure <code>dashboard-state.json</code> exists in this directory.</p>
</div>
</body>
</html>"""


def _escape(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python3 generate_dashboard.py <path-to-dashboard-state.json>",
            file=sys.stderr,
        )
        sys.exit(1)

    state_path = Path(sys.argv[1])
    output_dir = state_path.parent
    output_path = output_dir / "dashboard.html"

    data: dict | None = None
    if state_path.exists():
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to parse {state_path}: {e}", file=sys.stderr)
            data = None

    html = build_html(data)
    output_path.write_text(html, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
