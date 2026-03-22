---
source: "Can AI Agents Agree?" (arXiv:2603.01213v2) - Berdoz, Rugli, Wattenhofer (ETH Zurich)
date: 2026-03-23
status: integrated
---

## Source Summary

### Main Claims
- LLM エージェント群は、no-stake（利害なし）の Byzantine 合意タスクですら信頼可能な合意に到達できない
- 失敗の支配的モードは value corruption ではなく liveness 喪失（timeout/停滞）
- 1体の Byzantine エージェントだけで合意成功率が大幅に低下する

### Techniques
- A2A-Sim: 同期 all-to-all ネットワーク上の Byzantine 合意シミュレータ
- 合意結果の3分類: valid consensus / invalid consensus / no consensus (timeout)
- プロンプト変種による影響測定: "May Exist" vs "None Exist"
- ラウンドベースの収束トラジェクトリ分析

### Evidence
- Qwen3-8B/14B、N={4,8,16}、B={0,1,2,3,4}、各構成25試行（合計600+）
- Benign: valid consensus 41.6%（全構成平均）。Qwen3-14B: 67.4%, Qwen3-8B: 15.8%
- N増加で劣化: N=4 で 46.6% -> N=16 で 33.3%
- B=1 で約25%低下、B>=3 で 0%
- "May Exist" プロンプトが "None Exist" より 59.1% vs 75.4% と劣化

### Assumptions
- Qwen3 ファミリー（8B/14B）のみ。GPT-4/Claude/Llama 未テスト
- 制限付き Byzantine モデル（equivocation 不可）
- 同期 all-to-all ネットワーク（非同期・パーシャルメッシュ未検証）
- 8,192 トークンコンテキスト、サマリ圧縮あり

## Gap Analysis

| # | Knowledge | Status | Current State | Delta |
|---|-----------|--------|---------------|-------|
| 1 | Liveness loss as dominant failure mode | Partial | stagnation-detector.py + resource-bounds.md for single-agent stalls | No detection for multi-reviewer convergence stalls |
| 2 | Group size degrades consensus | Partial | /review scales reviewers by change size (2-8 agents) | No upper bound or diminishing-returns awareness |
| 3 | Single Byzantine collapses consensus | Partial | agency-safety-framework.md + gaming-detector.py | No outlier detection for reviewer outputs |
| 4 | Threat-aware prompts hurt performance | Gap | adversarial framing used in security reviewers | No documentation of side-effect trade-offs |
| 5 | Formal consensus outcome classification | Gap | synthesis-report.md has Agreement Rate placeholder | No computation guide or convergence quality metrics |
| 6 | A2A-Sim protocol | N/A | Hub-and-spoke coordinator pattern, not P2P | Not applicable to current architecture |
| 7 | Small open model limitations | N/A | Uses Opus/Sonnet + Codex (gpt-5.4) + Gemini | Results directionally informative but not directly transferable |

## Integration Decisions

All 5 Gap/Partial items selected for integration (priority order):
1. Review synthesis convergence stall detection
2. Outlier review output detection/isolation
3. Reviewer scaling upper bound policy
4. Agreement rate metrics computation
5. Adversarial framing side-effect awareness

## Plan

See below. Scope: M (4 existing files modified + 1 new reference file).

### Task 1: Review Consensus Policy (new reference)
- **File**: `references/review-consensus-policy.md` (new)
- **Content**: Convergence stall detection criteria, outlier detection rules, scaling upper bound rationale, agreement rate computation formula
- **Depends on**: None

### Task 2: Review SKILL.md - Step 2 scaling upper bound
- **File**: `skills/review/SKILL.md`
- **Change**: Add upper bound note to Step 2 scaling table + reference to consensus policy
- **Depends on**: Task 1

### Task 3: Review SKILL.md - Step 4 synthesis with consensus checks
- **File**: `skills/review/SKILL.md`
- **Change**: Add convergence stall detection, outlier isolation, agreement rate computation to Step 4
- **Depends on**: Task 1

### Task 4: Synthesis report template - agreement rate computation guide
- **File**: `skills/review/templates/synthesis-report.md`
- **Change**: Add computation instructions for Agreement Rate field and Conflicts section
- **Depends on**: Task 1

### Task 5: Agency Safety Framework - adversarial framing trade-offs
- **File**: `references/agency-safety-framework.md`
- **Change**: Add section on adversarial framing side-effects with citation
- **Depends on**: None
