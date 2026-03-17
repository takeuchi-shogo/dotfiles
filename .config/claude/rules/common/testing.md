---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.go"
  - "**/*.py"
  - "**/*.rs"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*_test.*"
---

# Testing Requirements

## Test Coverage Target: 80%+

Test Types (all required for production code):
1. **Unit Tests** — Individual functions, utilities, components
2. **Integration Tests** — API endpoints, database operations
3. **E2E Tests** — Critical user flows

## Test-Driven Development

Preferred workflow:
1. Write test first (RED)
2. Run test — it should FAIL
3. Write minimal implementation (GREEN)
4. Run test — it should PASS
5. Refactor (IMPROVE)
6. Verify coverage

## Test Quality Rules

- Tests should be independent and isolated
- No shared mutable state between tests
- Use descriptive test names that explain the scenario
- Arrange-Act-Assert pattern
- Mock external dependencies, not internal logic
- Test edge cases and error paths

### Few-shot Examples

```typescript
// NG: 不明瞭なテスト名
test("test1", () => { ... });

// OK: シナリオを説明する名前
test("should return validation error when email is empty", () => { ... });
```

```typescript
// NG: Arrange-Act-Assert が混在し、複数の振る舞いを1テストに詰め込む
test("user creation", () => {
  const user = createUser("alice");
  expect(user.name).toBe("alice");
  user.activate();
  expect(user.isActive).toBe(true);
});

// OK: 1テスト1振る舞い、AAA を明確に分離
test("should create user with given name", () => {
  // Arrange
  const name = "alice";
  // Act
  const user = createUser(name);
  // Assert
  expect(user.name).toBe("alice");
});

test("should activate user", () => {
  const user = createUser("alice");
  user.activate();
  expect(user.isActive).toBe(true);
});
```

## Troubleshooting Test Failures

1. Use **test-engineer** agent for test strategy
2. Use **debugger** agent for root cause analysis
3. Fix implementation, not tests (unless tests are wrong)
4. Check test isolation — failing in CI but passing locally?
