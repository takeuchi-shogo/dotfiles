---
title: Zero Trust for AI Agents — 運用メタ層 3 タスク統合
date: 2026-05-31
status: active
scale: L
source: "Anthropic eBook — Zero Trust for AI Agents (2026-05-18)"
report: docs/research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md
gate: "Codex Spec/Plan Gate 完了 (2026-05-31, gpt-5.5 xhigh) — P1/P2 全反映済み"
---

# Zero Trust for AI Agents 統合プラン (実装版)

## 背景

Anthropic 公式 eBook『Zero Trust for AI Agents』の /absorb 分析。中核概念は
`agency-safety-framework.md` + `claude-code-threats.md` に **同等以上で実装済み**。
インフラ層 (X.509/mTLS/SPIFFE/TEE/ABAC/SOAR/AI-BOM 完全版) は単一ユーザー local
harness に **N/A**。Phase 2.5 で Codex が Opus の self-bias を修正し、**運用メタ層
(ops-meta)** の 3 タスクをユーザーが全採用。

> **YAGNI 警告 (Build to Delete)**: 単一信頼ユーザー harness では enterprise 脅威
> モデルは効かない。3 タスクとも限界価値が低い境界 YAGNI。実装後 30 日で
> 「session-bom.jsonl / security-guard.jsonl を一度も forensics に使わなかった」なら
> 撤退候補 (`references/harness-stability.md` の 30 日評価)。

## Research で確定した前提 (原 absorb プランからの修正)

1. **パス**: hook 実体は `.config/claude/scripts/` (= `~/.claude/scripts/`, symlink)。
   原プランの `scripts/...` は全て `.config/claude/scripts/...`。
2. **既存 helper** (`.config/claude/scripts/lib/hook_utils.py`):
   - `rotate_and_append(log_path, entry)` — 10MB rotation, `~/.claude/agent-memory/logs`
   - `guard_action(hook_name, pattern, detail) -> bool` — `HOOK_GUARD_MODE`(audit/warn/block)
     を適用し `security-guard.jsonl` に `{timestamp, hook, pattern, detail, mode}` 記録
3. **guard_action 利用状況**: `prompt-injection-detector` / `user-input-guard` は経由済。
   `mcp-audit` / `docker-safety` は **未経由** (block を `print+sys.exit(2)` 直書き、取りこぼし)。
4. **security-gate 分類**: `hook-failure-policy.md` で docker-safety / mcp-audit /
   prompt-injection は全て `fail_closed=True` の **security-gate**。
   → これらの hard block を `HOOK_GUARD_MODE` で緩めるのは policy 違反 (force_block 必須)。
5. **構成ファイル実位置**: `~/.claude/settings.json` は nix store symlink (home-manager)。
   `skills-lock.json`(skills=dict 64件) / `.mcp.json`(mcpServers 4件) は **dotfiles root のみ**、
   `~/.claude` に無い。`enabledMcpjsonServers`=3件 (context7/alphaxiv/code-review-graph) ≠
   `.mcp.json` 4件 (scite 含む)。`permissions.allow`=71件。

---

## Task 1: Agent-BOM-lite (S)

**目的**: per-SessionStart-event の実行時構成 snapshot を 1 行記録し、supply-chain 事故の
事後 forensics を可能にする。

**成果物**: 新規 `.config/claude/scripts/lifecycle/session-bom.py` (SessionStart hook)

- 出力: `~/.claude/agent-memory/logs/session-bom.jsonl` (rotate_and_append, **1 SessionStart event 1 行**)
- フィールド (Codex P2 反映):
  ```json
  {
    "ts": "ISO8601", "session_id": "...", "source": "startup|resume|clear|compact",
    "model": "...", "cwd": "...", "repo_trust": "<git root>|untracked",
    "allowed_tools_count": 71,                    // ~/.claude/settings.json permissions.allow
    "enabled_mcpjson_servers": ["context7", ...], // settings.json enabledMcpjsonServers
    "configured_mcp_servers": ["context7", ...],  // cwd/.mcp.json mcpServers keys (あれば)
    "active_skills_count": 64,                     // cwd/skills-lock.json skills (あれば、無ければ null)
    "present_instruction_surfaces": ["~/.claude/CLAUDE.md", "cwd/CLAUDE.md", ...], // 存在確認のみ
    "schema_version": 1
  }
  ```
- **root 解決 (Codex P2)**: SessionStart は任意 cwd で走る。`settings.json` は `~/.claude/settings.json`
  固定。`.mcp.json`/`skills-lock.json` は **cwd 直下を読む** (project 構成 = 実際にロードされ得るもの)、
  無ければ該当フィールド null。`Path.cwd()` 前提を曖昧にしない。
- **命名 (Codex P2)**: `present_instruction_surfaces` (存在確認のみ。hook から「実際に読まれた」は確定不能)。
- **stdout 厳禁 (Codex P1)**: SessionStart stdout は prompt/cache prefix に混入する。
  `run_hook` は使わず (例外時 `{}` を stdout 出力するため)、`main()` 全体を `try/except Exception: pass`
  で包む。標準出力には**何も書かない** (エラーは stderr のみ)。
- **fail-open**: 観測専用。例外は握りつぶしセッション起動を絶対ブロックしない。
- settings.json SessionStart 配列に新規 hook ブロック追加 (**`timeout: 3` 明示** — fail-open でも timeout まで遅延)。
- retention: rotate_and_append の 10MB rotation に委譲 (既存機構)。

**検証**: `task validate-configs` + `python3 ~/.claude/scripts/runtime/sessionstart-audit.py`
(stdout 0B・低 latency 確認) + 新セッション起動 → jsonl に 1 行追記を確認。

**依存**: なし (独立)

---

## Task 2: why observability — guard_action 拡張 [案A'] (M→実質 S)

**設計判断**: 原プランの `decisions.jsonl` 新設は既存 `guard_action`/`security-guard.jsonl`
と二重管理 (DRY 違反)。**案A' = security-guard.jsonl 集約 + optional metadata + force_block**
を採用 (ユーザー承認 + Codex 推奨)。

**成果物**:

1. `hook_utils.guard_action` シグネチャ拡張 (後方互換):
   ```python
   def guard_action(hook_name, pattern, detail, *,
                    revocation_trigger=None, metadata=None, force_block=False) -> bool:
   ```
   - `force_block=True` → `HOOK_GUARD_MODE` を**無視して常に block** (security-gate 用、Codex P1)
   - entry に追加: `decision`(=effective mode), `configured_mode`(=env 値),
     `revocation_trigger`(任意), `schema_version`, および `metadata` 展開 (session_id/tool_name 等)
   - 既存呼び出し (prompt-injection/user-input-guard) は引数増えても**挙動不変** (mode 可変のまま)
2. `mcp-audit.py`: 2 block 箇所 (DANGEROUS_MCP_PREFIXES マッチ / skill MCP scope violation) を
   `if guard_action("mcp-audit", pattern, detail, force_block=True, metadata={...}): sys.exit(2)` に置換
3. `docker-safety.py`: 2 block 箇所 (docker run without --rm / --privileged) を同様に置換
4. **decisions.jsonl は新設しない** (security-guard.jsonl に集約)

**検証**: 
- 危険コマンド dry (`rm -rf` 等 → prompt-injection) で security-guard.jsonl 記録継続を確認
- **synthetic test (Codex P3)**: `HOOK_GUARD_MODE=audit` 環境でも migrated block (force_block=True) が
  `exit 2` することを確認 (security-gate が env で緩まない回帰防止)
- 既存 hook の block/warn 挙動が回帰していないことを `tests/` で確認

**依存**: なし (Task 1 と独立、jsonl は別ファイルだが命名規約を揃える)

---

## Task 3: 個人版 8-phase deployment checklist (S) — Codex defer 推奨あり

> **Codex P3**: 「Task 1/2 を 30 日使い、実際に参照した観測項目だけを後で checklist 化する方が
> YAGNI 整合」。ユーザーは全採用を明示済みのため**含める**が、**既存メカへのポインタ集に厳密に留め、
> 新規ルールを一切増やさない** (二重管理回避)。不要ならこのタスクのみ却下可。

**成果物**: 新規 `.config/claude/references/agent-deployment-checklist.md`

- eBook 8-phase → harness self-check 翻訳マッピング表 (各 phase は既存メカへのポインタ主体):
  1. Identify requirements → capability gap (Build to Delete の自問)
  2. Supply chain → `skill-security-scan` / `mcp-audit` / 5 分監査チェックリスト
  3. Define boundaries → `tool-scoping-guide` (allowed-tools 宣言) + blast radius
  4. Defend prompt injection → `injection-rule-taxonomy` (外部入力 untrusted 扱い)
  5. Secure tool access → default-deny / allow-list (`settings.json`)
  6. Secure credentials → `.env` chmod 600 + deny rules (`claude-code-threats §6.5`)
  7. Safeguard memory → `memory-integrity-check` + recalled=background context
  8. Measure → session-bom (Task 1) + security-guard.jsonl decision log (Task 2)
- `agency-safety-framework.md` から相互リンク

**検証**: `task validate-symlinks` + reference 相互リンク整合

**依存**: Task 1 + Task 2 (phase 8 が参照)

---

## 実行順序

1. **Task 1** (session-bom) — 独立・最小・stdout 厳禁を厳守
2. **Task 2 案A'** (guard_action 拡張 + force_block) — Codex 実利最優先
3. **Task 3** (checklist) — Task 1+2 完成後にポインタ確定 (defer 可)

各タスク実装後に **Codex Review Gate** (S 規模以上)。

## 撤退条件 (reversible-decisions)

- Task 1/2 の jsonl を 30 日で forensics/debug に未使用 → hook 撤去・`_archive` へ (Build to Delete)
- guard_action 改修が既存 block 挙動に回帰 (特に security-gate が env で緩む) → 即 revert
- checklist が「ポインタ集」を超え独自ルールで既存 reference と二重管理化 → 統合 or 削除

## 非実装 (明示的に N/A)

暗号 ID (X.509/HSM/TPM/SPIFFE) / mTLS / ABAC / JIT-JEA / TEE / agent identity segmentation /
AI-BOM 完全版 / Agentic SOAR → 単一ユーザー local harness に構造的に不要 (Codex + Gemini 一致)。
