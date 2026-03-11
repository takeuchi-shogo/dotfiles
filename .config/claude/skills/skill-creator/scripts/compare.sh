#!/usr/bin/env bash
set -euo pipefail

# compare.sh — Blind A/B comparison of with_skill vs without_skill outputs
#
# Usage: compare.sh <eval-dir>
#
# The eval-dir must contain:
#   - eval_metadata.json  (with "prompt" and "assertions" fields)
#   - with_skill/outputs/response.md
#   - without_skill/outputs/response.md
#
# Randomly assigns outputs to "Output A" and "Output B" to prevent position
# bias, then sends both to claude -p as a blind grader. The grader evaluates
# each assertion, rates quality 1-10, and declares a winner or tie.
#
# Result is saved as grading.json in the eval directory.

##############################################################################
# Arguments
##############################################################################

if [[ $# -lt 1 ]]; then
  echo "Usage: compare.sh <eval-dir>" >&2
  exit 1
fi

EVAL_DIR="$1"

##############################################################################
# Validate required files
##############################################################################

if [[ ! -d "$EVAL_DIR" ]]; then
  echo "ERROR: Eval directory not found: ${EVAL_DIR}" >&2
  exit 1
fi

METADATA_FILE="${EVAL_DIR}/eval_metadata.json"
WITH_SKILL_FILE="${EVAL_DIR}/with_skill/outputs/response.md"
WITHOUT_SKILL_FILE="${EVAL_DIR}/without_skill/outputs/response.md"

if [[ ! -f "$METADATA_FILE" ]]; then
  echo "ERROR: eval_metadata.json not found in: ${EVAL_DIR}" >&2
  exit 1
fi

if [[ ! -f "$WITH_SKILL_FILE" ]]; then
  echo "ERROR: with_skill/outputs/response.md not found in: ${EVAL_DIR}" >&2
  exit 1
fi

if [[ ! -f "$WITHOUT_SKILL_FILE" ]]; then
  echo "ERROR: without_skill/outputs/response.md not found in: ${EVAL_DIR}" >&2
  exit 1
fi

##############################################################################
# Read metadata
##############################################################################

TASK_PROMPT=$(jq -r '.prompt // empty' "$METADATA_FILE")
if [[ -z "$TASK_PROMPT" ]]; then
  echo "ERROR: 'prompt' field is missing or empty in eval_metadata.json" >&2
  exit 1
fi

ASSERTIONS=$(jq -r '.assertions // [] | to_entries | map("  \(.key + 1). \(.value.text // .value)") | join("\n")' "$METADATA_FILE")
if [[ -z "$ASSERTIONS" ]]; then
  ASSERTIONS="  (No specific assertions provided — evaluate overall quality)"
fi

WITH_SKILL_OUTPUT=$(cat "$WITH_SKILL_FILE")
WITHOUT_SKILL_OUTPUT=$(cat "$WITHOUT_SKILL_FILE")

##############################################################################
# Randomize assignment to prevent position bias
##############################################################################

if (( RANDOM % 2 == 0 )); then
  OUTPUT_A="$WITH_SKILL_OUTPUT"
  OUTPUT_B="$WITHOUT_SKILL_OUTPUT"
  LABEL_A="with_skill"
  LABEL_B="without_skill"
else
  OUTPUT_A="$WITHOUT_SKILL_OUTPUT"
  OUTPUT_B="$WITH_SKILL_OUTPUT"
  LABEL_A="without_skill"
  LABEL_B="with_skill"
fi

echo "=== Blind A/B Comparison ==="
echo "  Eval dir: ${EVAL_DIR}"
echo "  A -> ${LABEL_A}, B -> ${LABEL_B} (hidden from grader)"
echo ""

##############################################################################
# Construct the grader prompt
##############################################################################

GRADER_PROMPT=$(cat <<'PROMPT_HEADER'
You are an expert evaluator performing a blind comparison of two outputs.
You do NOT know which output used a skill and which did not. Evaluate purely on quality.

## Original Task Prompt

PROMPT_HEADER
)

GRADER_PROMPT="${GRADER_PROMPT}
${TASK_PROMPT}

## Assertions to Check

${ASSERTIONS}

## Output A

${OUTPUT_A}

## Output B

${OUTPUT_B}

## Instructions

1. For each assertion listed above, check whether it is satisfied by Output A and Output B independently. Record evidence for each.
2. Rate the overall quality of each output on a scale of 1-10 (10 = excellent).
3. List strengths and weaknesses of each output.
4. Declare a winner: \"A\", \"B\", or \"tie\".

Respond with ONLY valid JSON in exactly this format (no markdown fences, no extra text):

{
  \"output_a\": {
    \"assertion_results\": [{\"text\": \"assertion text\", \"passed\": true, \"evidence\": \"why it passed or failed\"}],
    \"quality_score\": 8,
    \"strengths\": [\"strength 1\"],
    \"weaknesses\": [\"weakness 1\"]
  },
  \"output_b\": {
    \"assertion_results\": [{\"text\": \"assertion text\", \"passed\": true, \"evidence\": \"why it passed or failed\"}],
    \"quality_score\": 7,
    \"strengths\": [\"strength 1\"],
    \"weaknesses\": [\"weakness 1\"]
  },
  \"winner\": \"A\",
  \"reasoning\": \"Explanation of why A or B won, or why it is a tie\"
}"

##############################################################################
# Run the grader via claude -p (no tools — pure reasoning)
##############################################################################

echo "Running blind grader via claude -p..."
echo ""

GRADER_OUTPUT=$(claude -p "$GRADER_PROMPT" --allowedTools "" 2>/dev/null) || {
  echo "ERROR: claude -p grader failed" >&2
  exit 1
}

##############################################################################
# Parse grader output, map A/B back to real labels, and save grading.json
##############################################################################

python3 - "$GRADER_OUTPUT" "$LABEL_A" "$LABEL_B" "$EVAL_DIR" <<'PYTHON_EOF'
import json
import re
import sys

raw_output = sys.argv[1]
label_a = sys.argv[2]
label_b = sys.argv[3]
eval_dir = sys.argv[4]

# Strip markdown fences if present (```json ... ``` or ``` ... ```)
cleaned = raw_output.strip()
cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
cleaned = re.sub(r'\n?```\s*$', '', cleaned)
cleaned = cleaned.strip()

# Try to extract JSON object if there's surrounding text
json_match = re.search(r'\{[\s\S]*\}', cleaned)
if json_match:
    cleaned = json_match.group(0)

try:
    result = json.loads(cleaned)
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse grader JSON: {e}", file=sys.stderr)
    print(f"Raw output (first 500 chars): {raw_output[:500]}", file=sys.stderr)
    sys.exit(1)

# Validate required fields
for key in ("output_a", "output_b", "winner", "reasoning"):
    if key not in result:
        print(f"ERROR: Missing required field '{key}' in grader output", file=sys.stderr)
        sys.exit(1)

# Map A/B back to real labels
grading = {
    label_a: result["output_a"],
    label_b: result["output_b"],
    "mapping": {"A": label_a, "B": label_b},
    "winner_label": result["winner"],
    "winner": label_a if result["winner"] == "A" else (label_b if result["winner"] == "B" else "tie"),
    "reasoning": result["reasoning"],
}

# Save grading.json
output_path = f"{eval_dir}/grading.json"
with open(output_path, "w") as f:
    json.dump(grading, f, indent=2, ensure_ascii=False)

print(f"Grading saved to: {output_path}")

# Print summary
score_a = result["output_a"].get("quality_score", "?")
score_b = result["output_b"].get("quality_score", "?")
reasoning_short = result["reasoning"][:100]
if len(result["reasoning"]) > 100:
    reasoning_short += "..."

print()
print("=== Comparison Result ===")
print(f"  A ({label_a}): score {score_a}")
print(f"  B ({label_b}): score {score_b}")
print(f"  Winner: {grading['winner']}")
print(f"  Reasoning: {reasoning_short}")
PYTHON_EOF

echo ""
echo "Done."
