---
paths:
  - "**/*.yaml"
  - "**/*.yml"
  - "**/*.json"
  - "**/.env*"
---

# Configuration File Rules

## Schema Validation

- Define JSON Schema / YAML schema for all config files
- Reference schemas with `$schema` field or IDE-specific comments
- Validate config at application startup — fail fast on invalid values

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": { ... }
}
```

## Secrets — NEVER in Config Files

- NEVER commit API keys, passwords, tokens, or certificates
- Use environment variables for secrets: `${DATABASE_URL}`
- Reference secrets via secret managers (Vault, AWS SSM, etc.)
- Add `.env*` to `.gitignore` — double check before every commit
- Use placeholder values in examples: `"YOUR_API_KEY_HERE"`

## Environment Variables

- Document all required env vars in `.env.example` (with dummy values)
- Validate required env vars at startup — fail with clear error messages
- Use prefixes to namespace: `APP_`, `DB_`, `AUTH_`
- Never use env vars for complex structured data — use config files instead

## Comments & Documentation

- Add comments explaining WHY, not WHAT — especially for non-obvious values
- Document constraints: valid ranges, allowed values, units
- Mark experimental or temporary config with `# EXPERIMENTAL` / `# TODO`

```yaml
# Max concurrent DB connections
# Increase beyond 20 only after load testing
max_connections: 10
```

## Safe Defaults

- Every config value should have a safe, restrictive default
- Timeouts: always set a finite default (never infinite)
- Feature flags: default to `false` (disabled) for new features
- Logging: default to `info` level — not `debug` in production
- Permissions: default to least privilege
