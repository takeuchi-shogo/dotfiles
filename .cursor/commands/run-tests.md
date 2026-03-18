Run all project tests, analyze failures, and fix them.

1. Detect the test framework:
   - Check `package.json` for jest/vitest/mocha
   - Check `pyproject.toml` or `pytest.ini` for pytest
   - Check `go.mod` for Go
   - Check `Cargo.toml` for Rust
2. Run the full test suite
3. If all tests pass, report success
4. If tests fail:
   a. Analyze each failure's root cause
   b. Classify: type error, logic error, runtime error, or flaky
   c. Fix the implementation (not the test) to make it pass
   d. Re-run tests to verify
5. Repeat up to 3 times if needed
6. Report final results with any remaining failures
