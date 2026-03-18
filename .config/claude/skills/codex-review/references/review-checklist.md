# Codex Review Checklist

## Standard Review (6 items)

1. **Correctness** — Does the code do what it claims?
2. **Edge Cases** — Are boundary conditions handled?
3. **Security** — Any injection, XSS, or auth issues?
4. **Performance** — Any N+1, unnecessary allocations, or blocking calls?
5. **Readability** — Is the code clear and well-named?
6. **Tests** — Are changes covered by tests?

## Security-Focused Review

- Input validation on all user-facing endpoints
- No hardcoded secrets
- SQL parameterization
- CSRF/XSS protection
- Auth checks on protected routes
