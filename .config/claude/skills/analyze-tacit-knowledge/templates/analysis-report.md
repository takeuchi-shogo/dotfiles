# Analysis Report - {date}

**Session(s):** {session_ids}
**Period:** {period}
**Analyzer version:** 1.0

---

## Stage 2: Detection Summary

| Signal Type | Count | Avg Confidence |
|------------|-------|----------------|
| {signal_type} | {count} | {avg_confidence} |

**Total detection points:** {total}

## Stage 3: Extracted Knowledge

{extracted_knowledge_list}

## Stage 4: Integration Results

| Verdict | Count | Details |
|---------|-------|---------|
| New | {count} | {brief} |
| Reinforce | {count} | {brief} |
| Contradict | {count} | {brief} |
| Promote | {count} | {brief} |

## Stage 5: Proposals

{proposals_list}

## Stage 6: Debate Results (if applicable)

{debate_summary}

## Stage 7: Applied Changes

| Action | Target | Status |
|--------|--------|--------|
| {action} | {file_path} | {approved/rejected} |

---

## Knowledge Base Statistics

- Total entries: {total_entries}
- Layer 2: {layer2_count}
- Layer 3: {layer3_count}
- Domains: {domain_list}
- Last promotion: {last_promotion_date}
