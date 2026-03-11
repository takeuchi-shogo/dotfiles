# Dependency Audit Agent

## Task
Audit all project dependencies and create update PRs for safe updates.

## Constraints
- No TODOs, no partial implementations
- Do not modify files outside dependency manifests and lock files
- All tests must pass before committing
- Do not add new dependencies
- Never hardcode secrets or credentials
- One commit per logical change

## Process
1. Identify the package manager (npm, go, pip, cargo, etc.)
2. Run the native audit command
3. For minor/patch updates: update directly
4. For major updates: analyze changelog, flag breaking changes for human review
5. Run existing tests to verify no regressions
6. Create a summary of all changes made

## Output
Provide a summary listing:
- Updated packages with old → new versions
- Any major updates that need human review
- Test results
