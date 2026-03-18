Fix all lint warnings and errors in the project.

1. Detect the linter:
   - TypeScript: eslint, biome, or tsc
   - Python: ruff, flake8, or mypy
   - Go: golangci-lint or go vet
   - Rust: cargo clippy
2. Run the linter and collect all warnings/errors
3. Classify each issue:
   - Auto-fixable: apply `--fix` flag
   - Manual fix needed: fix one by one
4. Apply auto-fixes first:
   - `npx eslint . --fix` or `npx biome check . --write`
   - `ruff check . --fix`
   - `cargo clippy --fix`
5. Fix remaining manual issues
6. Re-run linter to confirm all clear
7. Report: total fixed, any remaining issues
