---
tracker:
  kind: linear
  api_key: "$LINEAR_API_KEY"
  # Replace before running the service. Do not commit personal project slugs if
  # they expose private workspace structure.
  project_slug: "replace-with-linear-project-slug"
  active_states:
    - "Agent Ready"
  terminal_states:
    - "Done"
    - "Closed"
    - "Cancelled"
    - "Canceled"
    - "Duplicate"
    - "Won't Do"

polling:
  interval_ms: 60000

workspace:
  root: "~/code/symphony-workspaces/dotfiles"

hooks:
  timeout_ms: 60000
  after_create: |
    test -n "${SYMPHONY_DOTFILES_REPO:-}" || {
      echo "SYMPHONY_DOTFILES_REPO must point at a readable dotfiles repository URL or local path" >&2
      exit 1
    }
    git clone "$SYMPHONY_DOTFILES_REPO" .
  before_run: |
    test -f AGENTS.md
    git status --short
  after_run: |
    git status --short

agent:
  max_concurrent_agents: 1
  max_turns: 8
  max_retry_backoff_ms: 300000
  max_concurrent_agents_by_state:
    Agent Ready: 1

codex:
  command: "codex app-server"
  approval_policy: "on-request"
  thread_sandbox: "workspace-write"
  turn_timeout_ms: 3600000
  read_timeout_ms: 5000
  stall_timeout_ms: 300000
---

You are running as a Symphony-managed Codex agent for the dotfiles repository.

Issue:
- Identifier: {{ issue.identifier }}
- Title: {{ issue.title }}
- Description: {{ issue.description }}
- State: {{ issue.state }}
- Labels: {{ issue.labels }}
- Attempt: {{ attempt }}

Operate conservatively:
- Read `AGENTS.md`, `PLANS.md`, `docs/agent-harness-contract.md`, and the nearest relevant playbook before editing.
- Keep changes narrow and compatible with the existing dotfiles harness.
- Do not change linter configuration files.
- Do not run destructive git commands.
- Do not commit or push unless the issue explicitly asks for it and the operator approval policy allows it.
- If the task is ambiguous, produce a plan or investigation result instead of guessing.
- Before declaring completion, run the smallest relevant validation command and report the command plus result.

Completion handoff:
- Leave the workspace with inspectable diffs or a clear no-change investigation report.
- Summarize changed files, validation evidence, unresolved risks, and any follow-up issue candidates.
- If a Linear tool is available in the runtime, add the summary as an issue comment and move the issue to `Human Review`; otherwise leave the summary in the final Codex response.
