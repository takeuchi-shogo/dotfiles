---
title: Zero Trust for AI Agents — 運用メタ層 3 タスク統合
date: 2026-05-31
status: active
scale: L
source: "Anthropic eBook — Zero Trust for AI Agents (2026-05-18)"
report: docs/research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md
gate: Codex Spec/Plan Gate 必須 (harness 変更)
---

# Zero Trust for AI Agents 統合プラン

## 背景

Anthropic 公式 eBook『Zero Trust for AI Agents』の /absorb 分析。中核概念
(Least Agency / default-deny / prompt injection / memory poisoning / supply chain) は
`agency-safety-framework.md` + `claude-code-threats.md` に **同等以上で実装済み**。
インフラ層 (X.509/mTLS/SPIFFE/TEE/ABAC/SOAR/AI-BOM 完全版) は単一ユーザー local
harness に **N/A**。

Phase 2.5 で **Codex が Opus の self-bias を修正**: 「中核概念は強化不要」は雑で、
**運用メタ層 (ops-meta)** に翻訳可能な原則が残る、と指摘。ユーザーが全採用を選択。

> **重要 — YAGNI 警告 (Build to Delete)**: この harness は単一信頼ユーザーであり、
> enterprise 脅威モデル (マルチテナント / 非信頼オペレーター / コンプライアンス監査) は
> 効かない。transcript + session_observer が既に行動理由を捕捉している。3 タスクとも
> **限界価値が低い境界 YAGNI** であることを Opus・Codex 双方が留保。実装後 30 日で
> 「session-bom.jsonl / decision-log を一度も参照しなかった」なら撤退候補とする
> (`references/harness-stability.md` の 30 日評価に従う)。

## タスク

### Task 1: Agent-BOM-lite (S)

**目的**: per-session 実行時構成 snapshot を 1 行記録し、supply-chain 事故の事後
forensics を可能にする。`skills-lock.json` / `.mcp.json` は「定義」、これは「実行時に
実際にロードされた構成」という別価値。

**成果物**:
- 新規 `scripts/lifecycle/session-bom.py` (SessionStart hook)
  - 出力: `~/.claude/agent-memory/logs/session-bom.jsonl` (append, 1 行/session)
  - 記録フィールド:
    ```json
    {
      "ts": "ISO8601", "session_id": "...", "model": "...",
      "cwd": "...", "repo_trust": "git root or 'untracked'",
      "active_skills_count": N,          // skills-lock.json から
      "mcp_servers": ["context7", ...],  // .mcp.json から
      "allowed_tools_count": N,          // settings.json permissions.allow 件数
      "memory_surfaces": ["MEMORY.md", "CLAUDE.md", ...]  // ロードされた指示層
    }
    ```
  - **fail_closed=False** (観測専用、セッション起動を絶対にブロックしない)
- `settings.json` SessionStart hooks 配列 (~L204) に配線
- retention: `session-bom.jsonl` は 30 日 (既存 log retention 機構に合わせる)

**検証**: `task validate-configs` + 新セッション起動 → jsonl に 1 行追記を確認

**依存**: なし (独立)

---

### Task 2: why observability — decision log 強化 (M)

**目的**: 既存 policy hook 群は "what happened" を stderr に出すが、構造化された
「許可/ブロックの理由」が残らない。`policy_reason` + `revocation_trigger` を
decision log に統一記録する。

**スコープの正直な限定** (Codex 提案の goal_id/task_phase は plumbing が無い):
- ✅ **達成可能**: `decision` (allow/block/warn) + `policy_reason` (どのルールが発火したか)
  + `hook_name` を構造化記録。既存 `mcp-audit.jsonl` の延長で実装。
- ⏸️ **deferred**: `goal_id` / `task_phase` は PreToolUse hook が plan context に
  アクセスできないため本タスクでは見送り。plan-lifecycle hook との連携が必要で
  別 spike として評価する (YAGNI 警告: 単一ユーザーでは ROI 不明)。

**成果物**:
- `scripts/lib/` に decision-log helper (例 `decision_log.py`) — 各 policy hook が
  `record_decision(hook, tool, decision, policy_reason, revocation_trigger)` を呼ぶ
- `mcp-audit.py` / `prompt-injection-detector.py` / `docker-safety.py` の block/warn
  箇所から helper を呼ぶよう最小改修
  - `revocation_trigger`: そのルールが「今後どの条件で再ブロックするか」の短い文字列
- 出力: `~/.claude/agent-memory/logs/decisions.jsonl`
- **fail_closed は既存挙動を変えない** (記録の追加のみ。block するものは block のまま)

**検証**: 危険コマンド (例 `rm -rf` dry) を試行 → decisions.jsonl に
`{decision: "block", policy_reason: "...", hook: "prompt-injection-detector"}` 記録を確認。
既存 hook の block/warn 挙動が回帰していないことを `tests/` で確認。

**依存**: なし (Task 1 と独立だが、両者の jsonl schema は揃える)

---

### Task 3: 個人版 8-phase deployment checklist (S)

**目的**: eBook の 8-phase deployment lifecycle を「個人 harness で新しい
agent/skill/hook を導入する時の self-check」に翻訳。enterprise の stakeholder/legal/
compliance を削ぎ、harness 文脈の 8 点に再構成。

**成果物**:
- 新規 `references/agent-deployment-checklist.md`
  - eBook 8 phase → harness 翻訳マッピング表:
    1. Identify requirements → そのスキル/エージェントは何の capability gap を埋めるか
    2. Supply chain → 出所確認 (skill-security-scan / mcp-audit / 5 分監査チェックリスト)
    3. Define boundaries → allowed-tools 宣言 (tool-scoping-guide) + blast radius
    4. Defend prompt injection → 外部入力を untrusted 扱い (injection-rule-taxonomy)
    5. Secure tool access → default-deny / allow-list (settings.json)
    6. Secure credentials → .env chmod 600 + deny rules
    7. Safeguard memory → memory-integrity-check + recalled=background context
    8. Measure → session-bom (Task 1) + decision log (Task 2)
  - 各 phase は **既存メカニズムへのポインタ** を主とし、新規負担を増やさない
- `agency-safety-framework.md` の「新規コントロール追加のガイドライン」から相互リンク

**検証**: `task validate-symlinks` + reference 相互リンクの整合

**依存**: Task 1 + Task 2 (phase 8 がそれらを参照)

---

## 実行順序

1. Task 1 (Agent-BOM-lite) — 独立、最小、まず動かす
2. Task 2 (decision log) — Task 1 の jsonl schema 規約を踏襲
3. Task 3 (checklist) — Task 1+2 完成後にポインタを確定

## Gate

- **Codex Spec/Plan Gate**: harness 変更 (新規 hook + settings.json + 既存 policy hook 改修)
  のため CLAUDE.md 規定により必須。実装前に `codex exec --sandbox read-only` で
  Plan 批評を受ける。
- **Codex Review Gate**: 各タスク実装後 (S 規模以上)。
- 最低検証: `task validate-configs`, `task validate-symlinks`

## 撤退条件 (reversible-decisions)

- Task 1/2 の jsonl を **実装後 30 日で一度も forensics/debug に使わなかった** →
  hook を撤去し jsonl を `_archive` へ (Build to Delete)。
- decision log が既存 hook の block 挙動に回帰を起こした → 即 revert (記録は観測専用が大前提)。
- checklist が「ポインタ集」を超えて独自ルールを増やし、既存 reference と二重管理に
  なり始めたら統合 or 削除。

## 非実装 (明示的に N/A)

暗号 ID (X.509/HSM/TPM/SPIFFE) / mTLS / ABAC dynamic auth / JIT-JEA 配布クレデンシャル /
TEE-Confidential Computing / agent identity segmentation / AI-BOM 完全版 / Agentic SOAR。
→ 単一ユーザー local harness に構造的に不要 (Codex + Gemini 一致)。
