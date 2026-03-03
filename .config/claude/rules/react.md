---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
---

# React Rules

## Hooks Rules

- NEVER call hooks inside conditions, loops, or nested functions
- Specify dependency arrays accurately — include all referenced values
- Use `useRef` for values that should not trigger re-renders
- Extract complex logic into custom hooks with `use` prefix

```typescript
// BAD: conditional hook
if (isAuth) { useEffect(() => { ... }, []); }

// GOOD: condition inside hook
useEffect(() => { if (isAuth) { ... } }, [isAuth]);
```

## Composition Over Props Drilling

- Use children and render props to avoid passing data through many layers
- Prefer component composition: split into Container + Presentational
- Use context sparingly — only for truly global state (theme, auth, locale)
- For deep data sharing, consider co-locating state closer to consumers

## Server Components (Next.js App Router)

- Default to Server Components — add `"use client"` only when needed
- Keep `"use client"` boundaries as low as possible in the component tree
- Fetch data on the server — pass serializable props to client components
- Never import server-only code in client components

## Memoization

- Do NOT add `useMemo` / `useCallback` by default — measure first
- Memoize only when: expensive computation, stable reference for deps, or preventing child re-renders
- Use React Compiler (React 19+) when available instead of manual memoization
- `React.memo()` for components that re-render with same props frequently

## Keys & Lists

- NEVER use array index as `key` for dynamic lists
- Use a stable, unique identifier from your data (e.g. `id`, `slug`)
- If no natural key exists, generate one at data creation time — not at render

```typescript
// BAD
items.map((item, i) => <Item key={i} {...item} />)

// GOOD
items.map((item) => <Item key={item.id} {...item} />)
```
