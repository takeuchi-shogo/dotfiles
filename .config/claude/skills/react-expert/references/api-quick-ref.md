# React API Quick Reference

## Hooks

| Hook | Purpose | Common Pitfall |
|------|---------|---------------|
| useState | State management | Stale closure in callbacks |
| useEffect | Side effects | Missing dependencies |
| useRef | Mutable ref / DOM access | Don't read .current during render |
| useMemo | Expensive computation cache | Premature optimization |
| useCallback | Stable function reference | Overuse without memo'd children |
| useContext | Context consumption | Re-render on any context change |
| useReducer | Complex state logic | When useState suffices |
| useTransition | Non-urgent updates | Not for data fetching |
| useDeferredValue | Deferred rendering | Not a debounce replacement |
| useId | Unique IDs for SSR | Don't use for list keys |

## React 19 APIs

| API | Purpose |
|-----|---------|
| use() | Read promises/context in render |
| useActionState | Form action state |
| useFormStatus | Form submission status |
| useOptimistic | Optimistic UI updates |

## Patterns

| Pattern | When |
|---------|------|
| Composition over props | Boolean prop > 3 |
| Render props | Cross-cutting behavior |
| Compound components | Related UI elements |
| Controller/Uncontrolled | Form inputs |
