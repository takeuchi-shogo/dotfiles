# Skill Troubleshooting Guide

## Skill Won't Upload

### Error: "Could not find SKILL.md in uploaded folder"

**Cause:** File not named exactly SKILL.md
**Fix:** Rename to `SKILL.md` (case-sensitive). Verify with `ls -la`.

### Error: "Invalid frontmatter"

**Cause:** YAML formatting issue
**Common mistakes:**

- Missing `---` delimiters
- Unclosed quotes in description
- Invalid YAML syntax
  **Fix:** Validate YAML separately, ensure `---` on its own line before and after.

### Error: "Invalid skill name"

**Cause:** Name has spaces or capitals
**Fix:** Use kebab-case only: `my-cool-skill` not `My Cool Skill`

---

## Skill Doesn't Trigger

**Symptom:** Skill never loads automatically.

**Fix:** Revise description field.

**Quick checklist:**

- Is it too generic? ("Helps with projects" won't work)
- Does it include trigger phrases users would actually say?
- Does it mention relevant file types if applicable?

**Debugging approach:** Ask Claude: "When would you use the [skill name] skill?" Claude will quote the description back. Adjust based on what's missing.

**Undertriggering signals:**

- Skill doesn't load when it should
- Users manually enabling it
- Support questions about when to use it

**Solution:** Add more detail and nuance to the description — include keywords particularly for technical terms.

---

## Skill Triggers Too Often

**Symptom:** Skill loads for unrelated queries.

**Solutions:**

1. **Add negative triggers:**

```yaml
description: Advanced data analysis for CSV files. Use for statistical
  modeling, regression, clustering. Do NOT use for simple data exploration
  (use data-viz skill instead).
```

2. **Be more specific:**

```yaml
# Too broad
description: Processes documents

# Better
description: Processes PDF legal documents for contract review
```

3. **Clarify scope:**

```yaml
description: PayFlow payment processing for e-commerce. Use specifically
  for online payment workflows, not for general financial queries.
```

**Overtriggering signals:**

- Skill loads for irrelevant queries
- Users disabling it
- Confusion about purpose

---

## Instructions Not Followed

**Symptom:** Skill loads but Claude doesn't follow instructions.

**Common causes and fixes:**

### 1. Instructions Too Verbose

- Keep instructions concise
- Use bullet points and numbered lists
- Move detailed reference to separate files in references/

### 2. Instructions Buried

- Put critical instructions at the top
- Use `## Important` or `## Critical` headers
- Repeat key points if needed

### 3. Ambiguous Language

```
# Bad
Make sure to validate things properly

# Good
CRITICAL: Before calling create_project, verify:
- Project name is non-empty
- At least one team member assigned
- Start date is not in the past
```

### 4. Model "Laziness"

Add explicit encouragement:

```markdown
## Performance Notes

- Take your time to do this thoroughly
- Quality is more important than speed
- Do not skip validation steps
```

Note: Adding this to user prompts is more effective than in SKILL.md.

### Advanced Technique

For critical validations, bundle a script that performs checks programmatically rather than relying on language instructions. Code is deterministic; language interpretation isn't.

---

## MCP Connection Issues

**Symptom:** Skill loads but MCP calls fail.

**Checklist:**

1. **Verify MCP server is connected**
   - Claude.ai: Settings > Extensions > [Your Service]
   - Should show "Connected" status
2. **Check authentication**
   - API keys valid and not expired
   - Proper permissions/scopes granted
   - OAuth tokens refreshed
3. **Test MCP independently**
   - Ask Claude to call MCP directly (without skill)
   - "Use [Service] MCP to fetch my projects"
   - If this fails, issue is MCP not skill
4. **Verify tool names**
   - Skill references correct MCP tool names
   - Check MCP server documentation
   - Tool names are case-sensitive

---

## Large Context Issues

**Symptom:** Skill seems slow or responses degraded.

**Causes:**

- Skill content too large
- Too many skills enabled simultaneously
- All content loaded instead of progressive disclosure

**Solutions:**

### 1. Optimize SKILL.md Size

- Move detailed docs to references/
- Link to references instead of inline
- Keep SKILL.md under 5,000 words

### 2. Reduce Enabled Skills

- Evaluate if you have more than 20-50 skills enabled simultaneously
- Recommend selective enablement
- Consider skill "packs" for related capabilities

### 3. Use Progressive Disclosure Properly

- Level 1 (frontmatter): ~100 words, always loaded
- Level 2 (SKILL.md body): Core instructions, loaded on trigger
- Level 3 (references/): Detail docs, loaded only when needed
