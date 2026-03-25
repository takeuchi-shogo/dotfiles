---
name: frontend-prompt-brief
description: Generate a deterministic frontend implementation brief and write it to a Markdown artifact. Use when you need a structured landing page or app/dashboard brief before implementation.
---

# Frontend Prompt Brief

Create a compact frontend implementation brief and save it as a Markdown artifact.

## When To Use

- You need a reusable frontend brief before coding
- You want a hosted-shell-friendly skill that produces one Markdown artifact
- You want to turn product context into a prompt-ready implementation brief

## Inputs

Prepare a JSON file with the following keys:

- `surface_type`
- `product`
- `audience`
- `goal`
- `primary_cta`
- `style`
- `palette`
- `mood`
- `implementation_target`

Optional keys:

- `brand`
- `references`
- `constraints`
- `sections`

## Output

- Markdown artifact written to `/mnt/data/frontend-prompt-brief.md`

## Workflow

1. If the user has not provided structured inputs, create a small JSON file first.
2. Run the script:

```sh
python3 scripts/build_brief.py \
  --input examples/sample_input.json \
  --output /mnt/data/frontend-prompt-brief.md
```

3. Read the artifact and summarize the key decisions for the user.

## Rules

- Keep the output deterministic and concise
- Prefer one dominant visual direction
- Keep section count small
- Do not assume network access
- Do not install dependencies

## Watchouts

- If a required field is missing, stop and fix the input JSON first
- Do not write artifacts outside `/mnt/data` in hosted shell mode
- Do not turn this into a full code generator; this skill is only for brief generation
