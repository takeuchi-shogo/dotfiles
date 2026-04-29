---
status: reference
last_reviewed: 2026-04-29
---

# Proposal Schema (autoevolve)

AutoEvolve Phase 2.5 が書き出す `runs/YYYY-MM-DD/proposals.jsonl` の完全 schema。

## 完全スキーマ

```jsonc
{
  // --- 識別 ---
  "id": "IMP-YYYY-MM-DD-NNN",
  "created_at": "YYYY-MM-DDTHH:MM:SS",
  "category": "errors|quality|agents|skills|evaluators|comprehension|review-comments|output-diff",

  // --- 動機と内容 ---
  "motivation": "なぜこの改善を提案したか",
  "change_summary": "何を変えたか（1文）",
  "tags": ["keyword1", "keyword2"],

  // --- Co-evolution 操作空間 (T2 で追加) ---
  "resource_targets": ["prompt", "config", "strategy"],  // 1-2 個まで
  "interaction_hypothesis": "resource 間の相互作用仮説 (2 個同時変更時は必須)",

  // --- Lineage (既存) ---
  "parent_id": "IMP-YYYY-MM-DD-NNN | null",
  "novelty_score": 0.0,                                  // 0.0-1.0
  "similar_proposal_ids": [],
  "mutation_type": "refine | pivot | novel",             // lineage 分類。resource_targets と直交

  // --- Principle Traceability (Rule 43) ---
  "serves_principles": ["どの core principle を推進するか"],
  "tension_with": ["どの principle と緊張関係にあるか"],
  "pre_mortem": "この提案が失敗する場合の最も可能性が高い原因",
  "blast_radius": {
    "direct": ["変更対象ファイル"],
    "indirect": ["間接的に影響を受けるファイル/システム"]
  },
  "evidence_chain": {
    "data_points": 0,
    "confidence": 0.0,
    "specific_refs": ["session-xxx:line42"],
    "reasoning": "根拠",
    "counter_evidence": "反証",
    "hypothesis_refs": ["HYP-YYYY-MM-DD-NNN"]            // T1: hypotheses.jsonl 相互参照
  },
  "rollback_plan": "復旧手順",

  // --- Improvement Vectors (yamadashy Routines absorb 2026-04-29) ---
  "improvement_vectors": ["clarity"],                     // 1-3 個必須。標準 5 軸 (clarity/brevity/accuracy/coverage/consistency) または custom:<tag>。null は既存エントリ後方互換のみ。詳細: improve-policy.md "Improvement Vectors"

  // --- Gate/Outcome ---
  "eval_health": "ok | warning | skipped",
  "gate_verdict": "ROBUST | VULNERABLE | FATAL_FLAW",
  "outcome": "pending | merged | reverted | declined",
  "outcome_delta": null,                                  // 例: "+2.3pp" | "neutral" | "-1.1pp"
  "analysis_snippet": null                                // Micro-Analysis で自動記録
}
```

## resource_targets (T2)

Strategy Co-evolution (AFlow / ADAS / GPTSwarm) に基づく操作空間の拡張。

### 3 次元

| target | 対象ファイル | 例 |
|--------|-------------|-----|
| `prompt` | `agents/*.md`, `skills/*/SKILL.md` のドメイン知識セクション | Symptom-Cause-Fix テーブル追加、失敗パターン記述 |
| `config` | `references/*.md`, `rules/*.md`, `settings.json` | error-fix-guides 追記、hook 閾値調整、golden principle 更新 |
| `strategy` | `agents/*.md` の行動指示、scripts/ のロジック | Critic→Refiner 順序変更、新しいサブロール追加、retry 戦略 |

### 制約

1. **1 候補内で最大 2 resource** — dotfiles blast radius 対策。3 次元同時変更は分割する
2. **2 個同時変更時は `interaction_hypothesis` 必須** — なぜ同時に変える必要があるかを明示
3. **Debate プロンプトで ablation 意識** — 候補ごとに「prompt-only / strategy-only / both」の比較観点を促す
4. **mutation_type と直交** — `refine` で `[prompt, strategy]` などの組み合わせが許容される

### 失敗モード 2 対策

`resource_targets` が毎回 `[prompt, config, strategy]` (全部入り) になる退化を防ぐ:

- Debate プロンプトに「最小変更原則」を明示
- 3 要素全てを持つ候補は Phase 2.5 で VULNERABLE 判定 (blast_radius 過大)
- 単一 resource 候補と複数 resource 候補の両方を Debate に含める

### Ablation Design (参考)

Phase 2.5 で Codex が以下を検査する (提案が複数 resource を変更する場合):

1. `prompt-only` 版の簡易実装が存在するか
2. `strategy-only` 版の簡易実装が存在するか
3. なぜ `both` が必要か (interaction_hypothesis)
4. 各 resource の独立貢献を将来測定できる設計か

## 候補生成ルール (Phase 2.0)

`improve-policy.md` 候補生成ルールから参照される制約:

- 3 候補生成時、全候補が同一 `resource_targets` にならないよう多様性を担保
- 少なくとも 1 候補は単一 resource (single-resource baseline) とする
- `interaction_hypothesis` が欠落した 2 resource 候補は自動的に `VULNERABLE` 扱い
