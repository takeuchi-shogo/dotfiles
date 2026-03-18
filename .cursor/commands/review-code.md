Review the current code changes for quality and security issues.

1. Run `git diff` to see all current changes (staged and unstaged)
2. For each changed file, read the original code to understand context
3. Check for quality issues:
   - Functions exceeding 50 lines
   - Nesting deeper than 4 levels
   - Files exceeding 400 lines
   - Duplicate code patterns
   - Poor naming or unclear logic
4. Check for security issues:
   - Hardcoded secrets (API keys, passwords, tokens)
   - Unvalidated user input
   - SQL injection patterns
   - XSS vulnerabilities
5. Check test coverage:
   - Are there tests for the changed code?
   - Do existing tests still pass?
6. Report findings with severity:
   - 🔴 Critical: Must fix before commit
   - 🟡 Warning: Should fix
   - 🔵 Info: Suggestion for improvement
