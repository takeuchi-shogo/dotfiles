# Health Check Report — {date}

## Overall Status: {HEALTHY / WARNING / CRITICAL}

## Code-Document Drift

| File | Last Code Change | Last Doc Update | Drift (days) | Status |
|------|-----------------|-----------------|-------------|--------|
| {file} | {code_date} | {doc_date} | {days} | {OK/STALE/DRIFT} |

## Document Staleness

| Document | Last Updated | Age (days) | Status |
|----------|-------------|-----------|--------|
| {doc} | {date} | {days} | {OK/STALE} |

## Broken References

| Source File | Line | Reference | Status |
|------------|------|-----------|--------|
| {file} | {line} | {ref_path} | {BROKEN/MOVED} |

## Skill Benchmark Staleness

| Skill | Last Benchmark | Age (days) | Status |
|-------|---------------|-----------|--------|
| {skill} | {date} | {days} | {OK/STALE/NEVER} |

## Undocumented Subsystems

| Module | Path | Recommendation |
|--------|------|---------------|
| {module} | {path} | {action} |

## Actions Required

- [ ] {action_item_1}
- [ ] {action_item_2}
