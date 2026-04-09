# Paper Analysis Prompts — 再利用可能テンプレート集

> 元ソース: James (@jamescoder12) Twitter スレッド, 2026-04-09
> 安全機構と委譲ポリシーを追加した改良版

## Prompt 1: Contradiction Finder

```
Across all papers in this corpus, identify every point where two or more
authors directly contradict each other.

For each contradiction:
- State both positions with paper references (author, year, section/page)
- Name the papers
- Explain WHY they likely disagree (methodology, dataset, era, definitions)
- Assess resolvability: can both be true under different conditions, or
  is this a fundamental disagreement?

Format as a table. Do NOT report contradictions without source references.
```

**Safety**: 原典照合必須。参照なしの矛盾報告は無効。
**委譲先**: Sonnet + Scite MCP

## Prompt 2: Citation Chain

```
Pick the 3-5 most-referenced concepts across these papers.

For each concept:
- Who introduced it first?
- Who challenged it? What was the challenge?
- Who refined it? How?
- What's the current consensus (if any)?

Show the intellectual lineage as a structured table, not prose.
Mark any citations that cannot be verified from the paper corpus as [unverified].
```

**Safety**: `[unverified]` タグで LLM 記憶由来の引用を明示。
**委譲先**: Scite MCP 優先、なければ Sonnet

## Prompt 3: Intake Protocol (Landscape Mapping)

```
I'm sharing {N} papers on {topic}.

Before any detailed analysis, do this:
1. List every paper by author + year + core claim in one sentence
2. Group them into clusters of shared assumptions
3. Identify axes of disagreement
4. Flag any paper that contradicts another

Don't summarize individual papers. Map the landscape.
Output as tables, not prose.
```

**委譲先**: Sonnet

## Prompt 4: Master Synthesis

```
You now have a full picture of this literature.

Write a synthesis that does NOT summarize individual papers. Instead:
- State what the field collectively believes (Consensus layer)
- State what remains contested, with evidence for each side (Contested layer)
- State what lacks sufficient evidence to conclude (Unresolved layer)
- End with the single most important unanswered question

Max 400 words. No filler. No hedging. No academic throat-clearing.

IMPORTANT: Do not "harmonize" contradictions from Step 2. If two papers
disagree, report it as Contested, not Consensus.
```

**Safety**: Sycophancy 防止ルール — 矛盾を Consensus に入れない。
**委譲先**: Opus（判断・統合タスク）

## Prompt 5: Gap Scanner

```
Based on all papers, identify the 5 research questions that NOBODY has
fully answered yet.

For each gap:
- Why does it exist? Classify as: too hard / too niche / overlooked
- Which existing paper came closest to answering it?
- What methodology would be needed to close it?
- What would the field gain if this gap were closed?

Format as a table.
```

**委譲先**: Opus

## Prompt 6: Methodology Audit

```
Compare the research methodologies used across all papers.

Group by: surveys, experiments, simulations, meta-analyses, case studies,
theoretical/conceptual.

Then:
- Show the distribution (count and %)
- Which methodology dominates this field and why?
- Which methodology is underused and what would it reveal?
- Which paper's methodology is weakest and why?

Format as tables.
```

**委譲先**: Sonnet

## Prompt 7: Knowledge Map Builder

```
Create a structured knowledge map of this entire literature.

Format (strict — do not deviate):
- Central Claim: the single claim the field orbits around
- Supporting Pillars (3-5): well-established sub-claims with paper references
- Contested Zones (2-3): active debates with both sides named
- Frontier Questions (1-2): questions nobody has solved yet
- Must-Read Papers (3): papers a newcomer MUST read first, with WHY

Output as a clean outline, not prose.
```

**委譲先**: Opus

## Prompt 8: "So What" Test

```
Pretend I have to explain this entire body of research to a smart
non-expert in 5 minutes.

Give me exactly 3 things:
1. The one-sentence version of what this field has proven
2. The one honest admission of what it still doesn't know
3. The single real-world implication that matters most

No jargon. No hedging. No academic throat-clearing.
Each point: max 2 sentences.
```

**委譲先**: Opus

## Prompt 9: Assumption Killer

```
List every assumption that the MAJORITY of these papers share but never
explicitly test or justify.

For each assumption:
- State it clearly in plain language
- Name 1-2 papers that rely on it most heavily
- Explain what would happen to the field's conclusions if this assumption
  turned out to be wrong (counterfactual analysis)
- Rate severity: if wrong, is this a minor correction or a paradigm shift?

Then: send this list to a second reviewer for independent critique.
```

**Safety**: Codex セカンドオピニオンで盲点を補完。
**委譲先**: Opus → Codex (批評)

## Prompt Ordering

推奨実行順序（各ステップの出力が次のステップの入力に依存）:

```
Intake (0) → Landscape (1) → Contradiction (2) → Citation (3)
                                    ↓
         So What (8) ← Knowledge Map (7) ← Synthesis (4) → Gap Scan (5)
                                    ↑                          ↓
                          Assumptions (9)              Method Audit (6)
```

クイックモード: `0 → 1 → 4 → 8`（最小4ステップで概要把握）
