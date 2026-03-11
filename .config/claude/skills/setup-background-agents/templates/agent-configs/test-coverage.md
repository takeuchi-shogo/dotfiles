# Test Coverage Agent

## Task
Analyze changed files and write tests for uncovered code paths.

## Constraints
- No TODOs, no partial implementations
- Do not modify production code, only test files
- Do not delete or skip existing tests
- Tests must actually verify behavior, not just increase coverage numbers
- Never hardcode secrets or credentials

## Process
1. Identify changed files from the PR
2. For each changed file:
   a. Find the corresponding test file (or create one following project conventions)
   b. Analyze which code paths lack tests
   c. Write focused tests for uncovered paths
   d. Include edge cases and error paths
3. Run all tests to verify correctness
4. Report coverage improvement

## Output
- List of test files created/modified
- Number of new test cases
- Coverage before and after (if measurable)
