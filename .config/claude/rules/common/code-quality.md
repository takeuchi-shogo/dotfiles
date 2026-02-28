# Code Quality

## Immutability

ALWAYS create new objects, NEVER mutate existing ones:
- Use spread operator, `Object.assign`, or immutable update patterns
- Immutable data prevents hidden side effects and enables safe concurrency

## File Organization

MANY SMALL FILES > FEW LARGE FILES:
- 200-400 lines typical, 800 max
- Extract utilities from large modules
- Organize by feature/domain, not by type
- High cohesion, low coupling

## Function Size

- Functions: 50 lines max
- No deep nesting: 4 levels max
- Single responsibility per function

## Error Handling

ALWAYS handle errors explicitly:
- Handle errors at every level
- User-friendly messages in UI-facing code
- Detailed error context in server logs
- Never silently swallow errors

## Input Validation

ALWAYS validate at system boundaries:
- Validate all user input before processing
- Use schema-based validation (zod, pydantic, etc.)
- Fail fast with clear error messages
- Never trust external data

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable and well-named
- [ ] Functions are small (<50 lines)
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels)
- [ ] Proper error handling
- [ ] No hardcoded values (use constants or config)
- [ ] Immutable patterns used
