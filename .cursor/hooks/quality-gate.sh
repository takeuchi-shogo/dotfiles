#!/usr/bin/env bash
# Quality Gate Hook — runs on agent stop
# Checks for lint issues in uncommitted changes and asks agent to fix them.
# Source: Cursor blog "Best practices for coding with agents" (2026-01-09)

set -euo pipefail

# Read context from stdin (Cursor passes agent context as JSON)
CONTEXT=$(cat)

# Counter file: use project root hash to isolate per-project
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
COUNTER_FILE="/tmp/cursor-quality-gate-$(echo "$REPO_ROOT" | md5sum | cut -c1-8)"

# Check if there are uncommitted changes
if ! git diff --quiet HEAD 2>/dev/null; then
  # Detect linter
  LINT_CMD=""
  if [ -f "package.json" ]; then
    if command -v npx &>/dev/null; then
      if npx biome --version &>/dev/null 2>&1; then
        LINT_CMD="npx biome check ."
      elif npx eslint --version &>/dev/null 2>&1; then
        LINT_CMD="npx eslint ."
      fi
    fi
  elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    if command -v ruff &>/dev/null; then
      LINT_CMD="ruff check ."
    fi
  elif [ -f "go.mod" ]; then
    if command -v golangci-lint &>/dev/null; then
      LINT_CMD="golangci-lint run"
    fi
  elif [ -f "Cargo.toml" ]; then
    LINT_CMD="cargo clippy --quiet"
  fi

  if [ -n "$LINT_CMD" ]; then
    # Run lint and capture output (no eval — safe execution)
    LINT_OUTPUT=$($LINT_CMD 2>&1) || true
    LINT_EXIT=$?

    if [ $LINT_EXIT -ne 0 ]; then
      # Track iteration count via persistent counter file
      COUNT=1
      if [ -f "$COUNTER_FILE" ]; then
        COUNT=$(( $(cat "$COUNTER_FILE") + 1 ))
      fi
      echo "$COUNT" > "$COUNTER_FILE"

      if [ "$COUNT" -ge 3 ]; then
        # Max iterations reached — clean up and stop
        rm -f "$COUNTER_FILE"
        echo '{"status": "stop", "message": "Quality gate: lint failed after 3 attempts. Manual intervention needed."}'
        exit 0
      fi

      # Ask agent to fix lint issues
      cat <<EOF
{
  "followup_message": "Lint check failed. Please fix the following issues:\n\n\`\`\`\n${LINT_OUTPUT}\n\`\`\`\n\nFix all lint errors and warnings, then verify by running the linter again."
}
EOF
      exit 0
    fi
  fi
fi

# All clear — clean up counter
rm -f "$COUNTER_FILE"

echo '{"status": "ok"}'
