# CLAUDE.md (project overrides)

User CLAUDE.md covers KISS/YAGNI/DRY, search-first, and harness rules. This file adds project-specific concrete checks not in the global guide.

## Think before coding

- If something is unclear, stop. Name what's confusing. Ask.
- If multiple interpretations exist, surface them — don't pick silently.
- Propose scope extensions separately — don't implement them.

## Sanity check

- If you write 200 lines and it could be 50, rewrite it.
- Ask: "Would a senior engineer say this is overcomplicated?"
- Every changed line must trace directly to the user's request.

## Editing rules

- Don't refactor things that aren't broken — make the minimum change that satisfies the request.
- Don't "improve" adjacent code, comments, or formatting — leave neighbors untouched and mention observations in the final report.
- Don't remove pre-existing dead code unless asked — flag it so the user can decide.
- Match existing style, even if you'd do it differently.
- Remove imports/variables/functions that YOUR changes made unused; don't touch others.

## Goal-driven examples

- "Add validation" → write tests for invalid inputs, then make them pass.
- "Fix the bug" → write a test that reproduces it, then make it pass.
- "Refactor X" → ensure tests pass before and after.
