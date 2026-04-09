# Skill Writing Guide

スキル本文の構造・設計原則・書き方のガイド。

---

## Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

---

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (unlimited, scripts can execute without loading)

These word counts are approximate and you can feel free to go longer if needed.

**Key patterns:**

- Keep SKILL.md under 500 lines; if you're approaching this limit, add an additional layer of hierarchy along with clear pointers about where the model using the skill should go next to follow up.
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

---

## Skill Writing Principles

スキル本文の品質を高める 7 つの原則は `references/skill-writing-principles.md` を参照。
特に重要な 3 つ:
- **指示を書け、知恵を書くな** — 「なぜ重要か」より「何をすべきか」
- **一般知識を削れ** — エージェントが知っていることは省く
- **具体的に書け** — 曖昧な指示は無意味、Good/Bad 例を示す

### Atomic Skill Design Principles

スキルの構造品質を保証する 3 原則（[arXiv:2604.05013](https://arxiv.org/abs/2604.05013) に基づく）:

1. **Minimality（最小性）** — 1 つのスキルは 1 つの明確な能力に対応する。複数の責務を混ぜない
2. **Self-containment（自己完結性）** — スキル単体で実行可能。外部状態への暗黙の依存を排除する（`depend_on` 関係は skill-inventory で明示）
3. **Independent Evaluability（独立評価可能性）** — スキルの効果を他スキルと独立に測定できる。SKILL.md 作成時に「何をもって成功とするか」の eval 方法を必ず定義する

特に 3 の Independent Evaluability が最も見落とされやすい。eval 方法が定義されていないスキルは改善サイクルに乗せられない。

---

## Domain Organization

When a skill supports multiple domains/frameworks, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude reads only the relevant reference file.

---

## Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

---

## Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** - You can do it like this:

```markdown
## Report structure

ALWAYS use this exact template:

# [Title]

## Executive summary

## Key findings

## Recommendations
```

**Examples pattern** - It's useful to include examples. You can format them like this (but if "Input" and "Output" are in the examples you might want to deviate a little):

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

---

## Writing Style

Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs. Use theory of mind and try to make the skill general and not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.
