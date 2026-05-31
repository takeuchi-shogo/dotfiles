---
title: Agent/Skill/Hook Deployment Checklist (個人 harness 版)
date: 2026-05-31
status: active
type: reference
source: "Anthropic eBook — Zero Trust for AI Agents (2026-05-18) の 8-phase deployment lifecycle を個人 harness に翻訳"
---

# Agent/Skill/Hook Deployment Checklist

新しい **agent / skill / hook** を harness に導入する前の self-check。
Anthropic eBook『Zero Trust for AI Agents』の 8-phase deployment lifecycle から、
enterprise の stakeholder/legal/compliance 儀式を削ぎ、単一ユーザー harness 文脈の
8 点に再構成したもの。

> **位置づけ (重要)**: これは **既存メカニズムへのポインタ集** であり、新しい統制
> ルールを増やすものではない。各 phase は「既にある仕組みのどれを確認するか」を示す。
> 独自ルールが増えて既存 reference と二重管理になり始めたら、このファイルは統合 or 削除
> する (`harness-stability.md` の 30 日評価 + 本 checklist 由来プランの撤退条件)。
> Codex は「Task 1/2 を 30 日運用し、実際に参照した観測項目だけを残す」defer 運用を推奨。

## 8-phase self-check

| # | eBook phase | harness での問い | 参照する既存メカ |
|---|-------------|------------------|------------------|
| 1 | Identify requirements | この skill/agent/hook は **何の capability gap** を埋めるか。何が改善されれば不要になるか (Build to Delete) | `core_principles` (CLAUDE.md) / `harness-stability.md` |
| 2 | Supply chain | 出所は信頼できるか。MCP/skill の中身を監査したか | `skill-security-scan.py` / `mcp-audit.py` / `claude-code-threats.md §8` (ToxicSkills) |
| 3 | Define boundaries | allowed-tools を宣言したか。blast radius (影響範囲) は把握したか | `tool-scoping-guide.md` / `settings.json permissions` |
| 4 | Defend prompt injection | 外部入力 (web/MCP応答/ファイル) を **untrusted** 扱いしているか | `injection-rule-taxonomy.md` / `prompt-injection-detector.py` / `mcp-response-inspector.py` |
| 5 | Secure tool access | default-deny + allow-list になっているか。security-gate は env で緩まないか | `settings.json` (allow/deny) / `hook-failure-policy.md` (security-gate / `force_block`) |
| 6 | Secure credentials | `.env`/秘密鍵は保護されているか (chmod 600 + deny rules) | `claude-code-threats.md §6.5` / `settings.json deny` (Read/Write/Edit の秘密ファイル群) |
| 7 | Safeguard memory | memory poisoning に備えているか。recalled memory を **background context** として扱うか | `memory-integrity-check.py` / `agency-safety-framework.md` (Franklin et al. 2026) |
| 8 | Measure | 導入後の **実行時構成と decision** を観測できるか | `session-bom.py` → `session-bom.jsonl` / `guard_action` → `security-guard.jsonl` |

## 各 phase の補足

- **Phase 1**: 新規ハーネスは過渡的技術。「何が改善されればこれは不要か?」を導入時に書き残す。
- **Phase 2**: plugin + standalone 重複導入による MCP prefix collision の手動確認も含む (`mcp-audit.py` 冒頭コメント参照)。
- **Phase 3-5**: 「Impossible vs Inconvenient」design test = 制限の強度 (Hard block / Soft warning / Budget limit, 3 段階) を選ぶ。`agency-safety-framework.md` の 3 段階モデルが上位概念。
- **Phase 5 注意**: security-gate hook (`docker-safety` / `mcp-audit` / `prompt-injection-detector`) の block は `force_block=True` で `HOOK_GUARD_MODE` から独立させる。観測用の soft hook のみ env で audit/warn に切替可。
- **Phase 8**: `session-bom.jsonl` は「実行時にロードされ得た構成」(model/skills/MCP/tools/memory surfaces/repo trust) の snapshot、`security-guard.jsonl` は「許可/ブロックの理由」の decision log。supply-chain 事故の事後 forensics はこの 2 つを起点にする。

## 関連

- 上位フレームワーク: [agency-safety-framework.md](agency-safety-framework.md) ("Least Agency" の 3 本柱 + 制限の強度モデル)
- 脅威カタログ: [claude-code-threats.md](claude-code-threats.md)
- 撤退判断: [harness-stability.md](harness-stability.md) (30 日評価)
- absorb 分析: `docs/research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md`
