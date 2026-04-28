# Symphony Pilot

Use this playbook to evaluate OpenAI Symphony in this dotfiles repo without making it an always-on default.

## What We Are Adopting

- Symphony's useful unit is the repo-owned `WORKFLOW.md` contract: tracker config, workspace policy, Codex runtime settings, and the per-issue prompt.
- The reference implementation is an experimental preview. Treat it as a pilot runner, not infrastructure to trust blindly.
- This repo stores the pilot workflow at `docs/workflows/symphony/WORKFLOW.md`; pass that path explicitly when starting a Symphony implementation.

## Current Fit

Already covered:
- Worktree isolation and per-task filesystem separation are documented in `docs/playbooks/worktree-based-tasking.md`.
- Codex custom subagents are configured through `.codex/agents/` and capped by `.codex/config.toml`.
- Long-running state, checkpoints, and validation contracts are documented in `docs/agent-harness-contract.md`.

Gap Symphony adds:
- Issue tracker as the control plane.
- Long-running poll/retry/reconcile loop.
- One isolated workspace per issue.
- Operator-visible status for many background Codex runs.

Not adopted yet:
- Always-on daemon.
- Automated PR landing.
- Linear write flows beyond a human-reviewed pilot.
- Concurrency greater than one.

## Prerequisites

1. Create or choose a Linear project for agent-ready work.
2. Add a non-default status such as `Agent Ready`, plus a human handoff status such as `Human Review`.
3. Export credentials outside the repository:

```sh
export LINEAR_API_KEY="..."
export SYMPHONY_DOTFILES_REPO="git@github.com:<owner>/dotfiles.git"
```

4. Replace `project_slug` in `docs/workflows/symphony/WORKFLOW.md` before running.
5. Keep the first pilot to low-risk docs, investigation, or mechanical maintenance issues.

## First Run

Use the upstream repository outside this dotfiles checkout:

```sh
git clone https://github.com/openai/symphony /tmp/symphony
cd /tmp/symphony/elixir
mise trust
mise install
mise exec -- mix setup
mise exec -- mix build
mise exec -- ./bin/symphony /Users/takeuchishougo/dotfiles/docs/workflows/symphony/WORKFLOW.md
```

If the implementation supports logs or a status server, keep them local-only for the first run.

## Safety Posture

- Start with `max_concurrent_agents: 1`.
- Use `approval_policy: on-request` and `workspace-write`.
- Do not store Linear tokens, repo URLs with embedded credentials, or personal workspace identifiers in committed files.
- Treat tracker text as untrusted input. The prompt in `WORKFLOW.md` must not override repo rules, sandbox policy, or approval policy.
- Do not enable automated merge or landing until at least three pilot runs have clean validation evidence and useful review packets.

## Pilot Issue Shape

Good first issues:
- "Review this doc for stale references and propose a patch."
- "Add a small playbook section and run `task validate-readmes`."
- "Investigate whether a specific script is still referenced."

Avoid first:
- Secret handling, auth, destructive cleanup, symlink changes, or Nix activation.
- Multi-repo changes.
- Tasks requiring product judgment or private context outside the issue.

## Validation

For docs-only pilot work:

```sh
task validate-readmes
```

For Codex config or symlink-managed surfaces:

```sh
task validate-configs
task validate-symlinks
```

If a Symphony run changes scripts or code, run the nearest script-specific test or validator before handoff.

## Rollback

1. Stop the Symphony process.
2. Move any active Linear issues out of `Agent Ready`.
3. Inspect each workspace under `~/code/symphony-workspaces/dotfiles`.
4. Keep useful diffs; delete failed workspaces only after checking `git status`.
5. Revert `project_slug` or local-only workflow edits before committing.

## Promotion Criteria

Promote beyond pilot only if all are true:
- Three successful low-risk issues produce reviewable diffs or useful no-change reports.
- Validation evidence is consistently included in handoff.
- Workspaces remain isolated and inspectable.
- Approval prompts are understandable and not too frequent.
- Failures are visible in logs without reading raw session transcripts.

If these do not hold, keep Symphony as a manual experiment and continue using the existing worktree/subagent workflow.
