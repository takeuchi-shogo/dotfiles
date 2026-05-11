# Skill Validation Checklist

## Critical Rules

### SKILL.md Naming

- Must be exactly `SKILL.md` (case-sensitive)
- No variations: SKILL.MD, skill.md, Skill.md — none of these work
- Verify with: `ls -la` should show `SKILL.md`

### Skill Folder Naming

- kebab-case only: `notion-project-setup`
- No spaces: ~~`Notion Project Setup`~~
- No underscores: ~~`notion_project_setup`~~
- No capitals: ~~`NotionProjectSetup`~~

### YAML Frontmatter

- Must use `---` delimiters (not ``` or other markers)
- `name` field: kebab-case, no spaces, no capitals, should match folder name
- `description` field: under 1024 characters, includes WHAT and WHEN

### Security Restrictions

- No XML angle brackets (`<` or `>`) anywhere in frontmatter — could inject instructions
- No "claude" or "anthropic" in the skill name — reserved prefixes
- No code execution in YAML (uses safe YAML parsing)

### No README.md Inside Skill Folder

- All documentation goes in SKILL.md or references/
- README.md is for the GitHub repo level (for human visitors), not inside the skill folder

---

## Quality Gate (arXiv:2603.11808)

Before investing in writing a skill, evaluate against these 4 extraction quality criteria.
All 4 should be "Yes" to proceed. If any is "No", consider the alternative.

- [ ] **Recurrence** — Does this pattern appear in 3+ different contexts/projects?
  - No → Consider a one-off script in `~/.claude/scripts/` instead
- [ ] **Verification** — Is the procedural knowledge verified by real usage?
  - No → Run `/spike` first to validate the approach before codifying
- [ ] **Non-obviousness** — Does this exceed the model's baseline knowledge?
  - No → Test with `skill-audit` Batch 1 methodology before investing
- [ ] **Generalizability** — Can it be parameterized for different contexts?
  - No → Extract the generalizable core; leave specifics as parameters

---

## Before You Start

- [ ] Identified 2-3 concrete use cases
- [ ] Tools identified (built-in or MCP?)
- [ ] Reviewed example skills for your category
- [ ] Planned folder structure (scripts/, references/, assets/ needed?)
- [ ] Decided: Problem-first or Tool-first approach?

## During Development

- [ ] Folder named in kebab-case
- [ ] SKILL.md file exists (exact spelling)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name` field: kebab-case, no spaces, no capitals
- [ ] `description` includes WHAT and WHEN
- [ ] `description` under 1024 characters
- [ ] Trigger phrases include 3 near-miss negative examples (similar requests that should NOT trigger this skill)
- [ ] No XML tags (`<` or `>`) in frontmatter
- [ ] Instructions are clear and actionable (imperative form)
- [ ] Error handling included
- [ ] Examples provided
- [ ] References clearly linked with guidance on when to read them

## Before Upload / Distribution

- [ ] Tested triggering on obvious tasks
- [ ] Tested triggering on paraphrased requests
- [ ] Verified doesn't trigger on unrelated topics
- [ ] Functional tests pass
- [ ] Tool integration works (if applicable)

## After Upload

- [ ] Test in real conversations
- [ ] Monitor for under/over-triggering
- [ ] Collect user feedback
- [ ] Iterate on description and instructions
- [ ] Update version in metadata

---

## YAML Frontmatter Reference

### Required Fields

```yaml
---
name: skill-name-in-kebab-case
description: What it does and when to use it. Include specific trigger phrases.
---
```

### All Optional Fields

```yaml
name: skill-name
description: [required description]
license: MIT # Optional: License for open-source
allowed-tools: "Bash(python:*) Bash(npm:*) WebFetch" # Optional: Restrict tool access
metadata: # Optional: Custom fields
  author: Company Name
  version: 1.0.0
  mcp-server: server-name
  category: productivity
  tags: [project-management, automation]
  documentation: https://example.com/docs
  support: support@example.com
```

### Common Frontmatter Mistakes

```yaml
# Wrong - missing delimiters
name: my-skill
description: Does things

# Wrong - unclosed quotes
name: my-skill
description: "Does things

# Correct
---
name: my-skill
description: Does things
---
```
