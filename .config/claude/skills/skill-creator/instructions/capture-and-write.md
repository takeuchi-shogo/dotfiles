# Capture Intent, Quality Gate, Pattern Selection, Write SKILL.md

スキル作成の初期フェーズ: 意図の把握からSKILL.md初稿の完成まで。

---

## Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding to the next step.

1. What should this skill enable Claude to do?
2. **Which category?** Document & Asset Creation / Workflow Automation / MCP Enhancement — consult `references/planning-guide.md` for details on each category and their key techniques
3. **Problem-first or Tool-first?** Problem-first ("I need to set up a workspace") orchestrates tools for the user. Tool-first ("I have Notion MCP connected") teaches best practices for existing access.
4. When should this skill trigger? (what user phrases/contexts)
5. What's the expected output format?
6. **Success criteria?** Define upfront — e.g., "triggers on 90% of relevant queries", "completes in under 5 tool calls". See `references/planning-guide.md` for metrics guidance.
7. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

---

## Quality Gate

Evaluate the skill idea against 4 quality criteria (see `references/validation-checklist.md`
"Quality Gate" section). Walk through each with the user:

1. **Recurrence**: "Will you use this in multiple projects/contexts?"
   → If one-off, suggest a script instead
2. **Verification**: "Have you done this workflow manually at least once?"
   → If hypothetical, suggest `/spike` first
3. **Non-obviousness**: "Does Claude already do this well without a skill?"
   → If yes, run a quick baseline comparison first
4. **Generalizability**: "Could someone else use this skill with different inputs?"
   → If too specific, help extract the generalizable pattern

The user can override with explicit confirmation ("proceed anyway").

Reference: arXiv:2603.04448 SkillNet Extraction Quality Criteria

---

## Pattern Selection

After the Quality Gate, determine the skill's design pattern:

1. Load `references/skill-patterns.md` and review the Decision Tree
2. Based on the Capture Intent answers (especially Q1: purpose, Q2: category), recommend the best-fit pattern
3. Present the recommendation to the user:
   - "Based on your description, this skill fits the **[Pattern]** pattern: [1-sentence why]"
   - If composite: "This combines **[Pattern A]** (for [purpose]) with **[Pattern B]** (for [purpose])"
4. Ask the user to confirm or suggest a different pattern
5. Note the selected pattern's Required Elements from the Structure Quality Checklist — these will be verified in the Test stage

The pattern selection will be used in:
- **Write SKILL.md stage**: to add `metadata.pattern` to frontmatter and scaffold pattern-specific structure
- **Test stage**: to verify required elements are present

---

## Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs - if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

---

## Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: kebab-case only, must match folder name. No spaces, underscores, or capitals.
- **description**: The primary triggering mechanism. Structure as: `[What it does] + [When to use it] + [Key capabilities]`. Under 1024 characters. Include both what the skill does AND specific trigger phrases users would say. Claude tends to "undertrigger" skills, so make descriptions a bit "pushy" — include keywords and contexts where the skill applies, even if the user doesn't explicitly ask for it. Add "Do NOT use for..." when needed to prevent overtriggering.

  **Good:** `"Manages Linear project workflows including sprint planning, task creation, and status tracking. Use when user mentions 'sprint', 'Linear tasks', 'project planning', or asks to 'create tickets'."`
  **Bad:** `"Helps with projects."` (too vague, no triggers)
  **Bad:** `"Implements the Project entity model with hierarchical relationships."` (too technical, no user triggers)

- **origin**: Provenance classification — `self` (locally authored, default), `external` (installed from upstream repo, tracked in `skills-lock.json`), or `forked` (based on external skill but diverged). New skills default to `origin: self`.
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **the rest of the skill :)**

### Pattern-Aware Scaffolding

When writing the SKILL.md:
- Add `metadata.pattern` to the frontmatter (e.g., `metadata:\n  pattern: pipeline`)
- For composite patterns, use `+` notation (e.g., `inversion+generator`)
- Scaffold the pattern's required structure:
  - **Pipeline**: `## Step N — [Name]` sections with gate conditions
  - **Inversion**: `## Phase N — [Name]` sections with "DO NOT proceed until..." gate
  - **Reviewer**: Reference to checklist file + severity output format
  - **Generator**: Template reference + output format specification
  - **Tool Wrapper**: Reference to conventions file + trigger keywords in description

### Critical Rules (verify before finalizing)

- `SKILL.md` must be exact (case-sensitive) — not SKILL.MD, skill.md, etc.
- Folder name must be kebab-case — `my-skill` not `My Skill` or `my_skill`
- No XML angle brackets (`<` `>`) in frontmatter — security restriction
- No "claude" or "anthropic" in skill name — reserved
- No README.md inside the skill folder — all docs go in SKILL.md or references/
- See `references/validation-checklist.md` for the full checklist and YAML reference

---

## 5D Quality Check

SKILL.md 初稿を SkillNet の 5 次元で確認する（[arXiv:2603.04448](https://arxiv.org/abs/2603.04448)）。
いずれかが Poor の場合、修正してから Security Scan に進む。Average は注記のみ。

1. **Safety**: 破壊的操作にガードがあるか？allowed_tools が必要最小限か？
2. **Completeness**: 前提条件・入出力・失敗モードが明示されているか？
3. **Executability**: 手順が具体的か？指示のみスキルの場合、ガイダンスが明確か？
4. **Maintainability**: スコープが狭く、モジュール性があり、他スキルと低結合か？
5. **Cost-awareness**: トークン効率を意識しているか？無駄なループや大量読み込みがないか？

詳細な Good/Average/Poor の境界条件は `skill-audit` の Step 0: 5D Quality Scan を参照。

---

## Anti-Patterns セクション

SKILL.md に `## Anti-Patterns` セクションを含めることを推奨する。
1行1項目、段落説明不要。詳細は `references/skill-writing-principles.md` の「Anti-Patterns セクションの標準化」を参照。

---

## Security Scan

Before testing, run the security scanner on the skill directory:

```bash
python3 $HOME/.claude/scripts/policy/skill-security-scan.py <path-to-skill-folder>
```

If any CRITICAL or HIGH findings are reported, fix them before proceeding.
MEDIUM findings are advisory — review and address if appropriate.

The scanner checks:
- **G1 (Static)**: Dangerous code patterns (eval, exec, network access, fs destruction)
- **G2 (Semantic)**: Prompt injection vectors (zero-width chars, RTL override, hidden instructions)

Reference: arXiv:2603.04448 Four-Stage Verification Pipeline (G1-G4)
