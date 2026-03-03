---
paths:
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*_test.go"
---

# Test Rules

## AAA Pattern

Structure every test with clear separation:
1. **Arrange** — Set up test data, mocks, and preconditions
2. **Act** — Execute the function or action under test
3. **Assert** — Verify the expected outcome

```typescript
test("calculates total with tax", () => {
  // Arrange
  const items = [{ price: 100 }, { price: 200 }];
  const taxRate = 0.1;

  // Act
  const total = calculateTotal(items, taxRate);

  // Assert
  expect(total).toBe(330);
});
```

## Test Naming

- Include WHAT, WHEN, and EXPECTED RESULT in the name
- Use natural language — the name should read as a specification

```
// BAD
test("calc")
test("test error")

// GOOD
test("returns 0 when cart is empty")
test("throws ValidationError when email format is invalid")
```

## Mock Strategy

- Mock external dependencies: APIs, databases, file system, time
- NEVER mock internal logic — test the real implementation
- Use dependency injection to make mocking straightforward
- Reset mocks between tests to prevent state leakage

## Assertions

- One logical assertion per test — group related checks when testing a single behavior
- Assert on specific values, not just truthiness: `toBe(42)` not `toBeTruthy()`
- Always test error cases and edge cases alongside happy paths
- Prefer snapshot tests only for UI output — not for logic

## Test Data

- NO magic numbers or strings — use named constants or builders
- Use factory functions or fixtures for complex test objects
- Keep test data minimal — only include fields relevant to the test
- Use realistic but deterministic values (e.g. `"user@example.com"`, not `"aaa"`)
