# Skill Planning Guide

## Skill Categories

Before writing, identify which category your skill falls into. This determines the design approach.

### Category 1: Document & Asset Creation

Creating consistent, high-quality output — documents, presentations, apps, designs, code.

**Key techniques:**

- Embedded style guides and brand standards
- Template structures for consistent output
- Quality checklists before finalizing
- No external tools required — uses Claude's built-in capabilities

**Example:** frontend-design skill — "Create distinctive, production-grade frontend interfaces with high design quality."

### Category 2: Workflow Automation

Multi-step processes that benefit from consistent methodology, including coordination across multiple MCP servers.

**Key techniques:**

- Step-by-step workflow with validation gates
- Templates for common structures
- Built-in review and improvement suggestions
- Iterative refinement loops

**Example:** skill-creator skill — "Interactive guide for creating new skills. Walks the user through use case definition, frontmatter generation, instruction writing, and validation."

### Category 3: MCP Enhancement

Workflow guidance to enhance the tool access an MCP server provides.

**Key techniques:**

- Coordinates multiple MCP calls in sequence
- Embeds domain expertise
- Provides context users would otherwise need to specify
- Error handling for common MCP issues

**Example:** sentry-code-review skill — "Automatically analyzes and fixes detected bugs in GitHub Pull Requests using Sentry's error monitoring data via their MCP server."

---

## Problem-first vs Tool-first

Think of it like Home Depot. You might walk in with a problem — "I need to fix a kitchen cabinet" — and an employee points you to the right tools. Or you might pick out a new drill and ask how to use it for your specific job.

- **Problem-first:** "I need to set up a project workspace" → Your skill orchestrates the right MCP calls in the right sequence. Users describe outcomes; the skill handles the tools.
- **Tool-first:** "I have Notion MCP connected" → Your skill teaches Claude the optimal workflows and best practices. Users have access; the skill provides expertise.

Most skills lean one direction. Knowing which framing fits your use case helps choose the right design pattern.

---

## Description Formula

The description is the primary triggering mechanism. Structure it as:

```
[What it does] + [When to use it] + [Key capabilities]
```

### Good Examples

```yaml
# Specific and actionable
description: Analyzes Figma design files and generates developer handoff
  documentation. Use when user uploads .fig files, asks for "design specs",
  "component documentation", or "design-to-code handoff".

# Includes trigger phrases
description: Manages Linear project workflows including sprint planning,
  task creation, and status tracking. Use when user mentions "sprint",
  "Linear tasks", "project planning", or asks to "create tickets".

# Clear value proposition
description: End-to-end customer onboarding workflow for PayFlow. Handles
  account creation, payment setup, and subscription management. Use when
  user says "onboard new customer", "set up subscription", or "create
  PayFlow account".
```

### Bad Examples

```yaml
# Too vague — won't trigger on anything specific
description: Helps with projects.

# Missing triggers — no "when to use" info
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.
```

### Negative Triggers (for overtriggering)

When a skill triggers too often, add explicit exclusions:

```yaml
description: Advanced data analysis for CSV files. Use for statistical
  modeling, regression, clustering. Do NOT use for simple data exploration
  (use data-viz skill instead).
```

---

## Design Patterns

### Pattern 1: Sequential Workflow Orchestration

**Use when:** Multi-step processes in a specific order.

```markdown
## Workflow: Onboard New Customer

### Step 1: Create Account

Call MCP tool: `create_customer`
Parameters: name, email, company

### Step 2: Setup Payment

Call MCP tool: `setup_payment_method`
Wait for: payment method verification

### Step 3: Create Subscription

Call MCP tool: `create_subscription`
Parameters: plan_id, customer_id (from Step 1)
```

**Key techniques:** Explicit step ordering, dependencies between steps, validation at each stage, rollback instructions for failures.

### Pattern 2: Multi-MCP Coordination

**Use when:** Workflows span multiple services.

```markdown
### Phase 1: Design Export (Figma MCP)

1. Export design assets
2. Generate design specifications

### Phase 2: Asset Storage (Drive MCP)

1. Create project folder
2. Upload all assets

### Phase 3: Task Creation (Linear MCP)

1. Create development tasks
2. Attach asset links to tasks
```

**Key techniques:** Clear phase separation, data passing between MCPs, validation before moving to next phase.

### Pattern 3: Iterative Refinement

**Use when:** Output quality improves with iteration.

```markdown
### Initial Draft

1. Fetch data via MCP
2. Generate first draft report

### Quality Check

1. Run validation script: `scripts/check_report.py`
2. Identify issues

### Refinement Loop

1. Address each identified issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met
```

**Key techniques:** Explicit quality criteria, validation scripts, know when to stop iterating.

### Pattern 4: Context-aware Tool Selection

**Use when:** Same outcome, different tools depending on context.

```markdown
### Decision Tree

1. Check file type and size
2. Determine best storage location:
   - Large files (>10MB): Use cloud storage MCP
   - Collaborative docs: Use Notion/Docs MCP
   - Code files: Use GitHub MCP
   - Temporary files: Use local storage

### Provide Context to User

Explain why that storage was chosen
```

**Key techniques:** Clear decision criteria, fallback options, transparency about choices.

### Pattern 5: Domain-specific Intelligence

**Use when:** Your skill adds specialized knowledge beyond tool access.

```markdown
### Before Processing (Compliance Check)

1. Fetch transaction details via MCP
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction allowances
   - Assess risk level
3. Document compliance decision

### Processing

IF compliance passed:

- Process transaction
  ELSE:
- Flag for review

### Audit Trail

- Log all compliance checks
- Record processing decisions
```

**Key techniques:** Domain expertise embedded in logic, compliance before action, comprehensive documentation.

---

## Success Criteria

Define these before writing the skill. They guide testing and iteration.

## Design Patterns

See `references/skill-patterns.md` for the complete pattern catalog.

Quick reference for pattern selection during Capture Intent:

| If the skill primarily... | Pattern |
|---------------------------|---------|
| Teaches library/framework conventions | Tool Wrapper |
| Produces structured documents from templates | Generator |
| Evaluates code/artifacts against criteria | Reviewer |
| Interviews the user before acting | Inversion |
| Enforces a strict multi-step workflow | Pipeline |

---

### Quantitative Metrics

- **Trigger accuracy:** Skill triggers on 90% of relevant queries
  - _Measure:_ Run 10-20 test queries. Track auto vs. explicit invocation.
- **Workflow efficiency:** Completes workflow in X tool calls
  - _Measure:_ Compare same task with and without skill. Count tool calls and tokens.
- **Reliability:** 0 failed API calls per workflow
  - _Measure:_ Monitor MCP server logs during test runs. Track retry rates and error codes.

### Qualitative Metrics

- Users don't need to prompt Claude about next steps
- Workflows complete without user correction
- Consistent results across sessions
- New users can accomplish the task on first try with minimal guidance
