#!/usr/bin/env bash
# scripts/lifecycle/resume-anchor-lint.sh — resume anchor content lint (read-only)
#
# Usage: resume-anchor-lint.sh [path ...]        (default: HANDOFF.md candidates)
# Output: per-section verdict + summary. Never edits.
# Exit:   0 = all present and non-hollow, 1 = at least one hollow/missing section,
#         2 = no anchor file found (nothing to lint).
#
# What this can and cannot prove
# ------------------------------
# resume-anchor-contract.md gives anchors a lifetime; doctor-stale.sh reports when
# one goes stale. Neither looks at whether the anchor SAYS enough to resume from.
# This lints content against whichever HANDOFF schema the file uses, focusing on
# the sections that hold knowledge the environment cannot supply: "What Didn't
# Work" (checkpoint schema) and dead ends / verified-vs-hypothesis (escalation
# schema). git already knows the branch and the diff; it does not know which
# approach was tried and abandoned.
#
# It CANNOT prove nothing was omitted. Whether an observation whose relevance
# surfaced only later was ever written down is not decidable from the file --
# a section can be present, non-empty and still miss the one fact that mattered.
# Treat a pass as "the shape is right", not "resumable".

set -uo pipefail

hollow=0
checked=0
missing_all=1

# Two HANDOFF schemas are live in this repo and they do not share headings.
# Linting the wrong one reports every section MISSING, so pick per file.
#   checkpoint  — skills/checkpoint/SKILL.md, what /checkpoint actually writes
#   escalation  — references/handoff-template.md, agent-to-human escalation
CHECKPOINT_SECTIONS=(
  "Goal|^#+ *Goal"
  "Progress|^#+ *Progress"
  "What Worked|^#+ *What Worked"
  "What Didn't Work|^#+ *What Didn.t Work"
  "Next Steps|^#+ *Next Steps"
  "Context Files|^#+ *Context Files"
)
ESCALATION_SECTIONS=(
  "コンテキスト|^#+ *1\.([^0-9]|$)"
  "進捗サマリ|^#+ *2\.([^0-9]|$)"
  "ブロッカー|^#+ *3\.([^0-9]|$)"
  "失敗したアプローチ (Dead Ends)|^#+ *3\.5"
  "検証済み事実 / 未検証仮説|^#+ *3\.7"
  "推奨アクション|^#+ *4\.([^0-9]|$)"
  "再開ガイド|^#+ *5\.([^0-9]|$)"
)

# A section body is hollow when it carries no content beyond the template's own
# scaffolding: bracketed placeholders, blockquote hints, and bare list bullets.
section_is_hollow() {
  local file="$1" start_pat="$2" body
  body=$(awk -v pat="$start_pat" '
    !found && $0 ~ pat {
      found = 1
      match($0, /^#+/); depth = RLENGTH
      next
    }
    found && /^#+ / {
      match($0, /^#+/)
      if (RLENGTH <= depth) exit
    }
    found { print }
  ' "$file")
  # strip placeholders like [...], quote lines, list markers, blank lines
  body=$(printf '%s\n' "$body" \
    | sed -e 's/\[[^]]*\]//g' -e 's/{[^}]*}//g' -e 's/^[[:space:]]*>.*$//' \
          -e 's/^[[:space:]]*- \[[ xX]\][[:space:]]*//' \
          -e 's/^[[:space:]]*[-*][[:space:]]*//' \
          -e 's/^[[:space:]]*[0-9][0-9]*[.)][[:space:]]*//' \
          -e 's/\*\*[^*]*\*\*//g' -e 's/^[[:space:]]*:[[:space:]]*//' \
          -e 's/[[:space:]]//g' -e 's/^://' \
    | grep -v '^$' \
    | grep -v '^_\?(.*)_\?$' || true)
  [[ -z "$body" ]]
}

lint_file() {
  local file="$1"
  missing_all=0
  local -a sections
  local schema
  if grep -qE '^#+ *(Goal|Next Steps)' "$file"; then
    schema=checkpoint
    sections=("${CHECKPOINT_SECTIONS[@]}")
  else
    schema=escalation
    sections=("${ESCALATION_SECTIONS[@]}")
  fi
  echo "[resume-anchor-lint] $file (schema: $schema)"
  local entry label pat
  for entry in "${sections[@]}"; do
    label="${entry%%|*}"
    pat="${entry#*|}"
    checked=$((checked + 1))
    if ! grep -qE "$pat" "$file"; then
      printf "  MISSING  %s\n" "$label"
      hollow=$((hollow + 1))
    elif section_is_hollow "$file" "$pat"; then
      printf "  HOLLOW   %s (見出しはあるが中身が placeholder のみ)\n" "$label"
      hollow=$((hollow + 1))
    else
      printf "  ok       %s\n" "$label"
    fi
  done
  echo ""
}

if [[ $# -gt 0 ]]; then
  for f in "$@"; do
    [[ -f "$f" ]] && lint_file "$f" || echo "  (not found — skipped): $f"
  done
else
  for f in "$PWD/HANDOFF.md" "$PWD/tmp/HANDOFF.md" "$HOME/dotfiles/tmp/HANDOFF.md"; do
    [[ -f "$f" ]] && lint_file "$f"
  done
fi

if [[ "$missing_all" -eq 1 ]]; then
  echo "[resume-anchor-lint] no anchor file found — nothing to lint."
  echo "  (HANDOFF.md は次の SessionStart で読まれた時点で retire される。"
  echo "   セッション途中、/checkpoint で生成した直後に実行すること)"
  exit 2
fi

echo "=== summary ==="
echo "  sections checked:        $checked"
echo "  missing or hollow:       $hollow"
if [[ "$hollow" -gt 0 ]]; then
  echo ""
  echo "  NOTE: 形が揃っていないだけで、揃っていても再開できる保証にはならない。"
  echo "        テンプレート: .config/claude/references/handoff-template.md"
  exit 1
fi
exit 0
