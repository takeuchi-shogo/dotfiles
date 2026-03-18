# Pattern Detection Signals

| Signal Type | Detection Method | Example |
|------------|-----------------|---------|
| User correction | "no not that", "instead do", "don't" | "don't mock the database" |
| Repeated fix | Same fix applied 2+ times in session | Identical Edit patterns |
| New convention | Consistent pattern in 3+ files | Import ordering, naming |
| Debug insight | Root cause found after investigation | "The issue was actually..." |
| Anti-pattern | User explicitly flags bad practice | "never do X because Y" |

## Classification Rules

1. **correction** → User explicitly corrects behavior
2. **convention** → Consistent pattern observed in codebase
3. **debug-pattern** → Reusable debugging technique
4. **anti-pattern** → Explicitly flagged bad practice

## Duplicate Detection

Before saving, check existing memories for:
- Same rule with different wording → update existing
- Contradicting rule → flag for user resolution
- Already codified in CLAUDE.md/rules → skip
