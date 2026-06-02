---
source: "https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/6a1611a04085d7cd3dadc924_Claude-eBook-Zero-Trust-for-AI-Agents-05182026.pdf"
date: 2026-05-31
status: integrated
scale: L
plan: "docs/plans/active/2026-05-31-zero-trust-absorb-plan.md"
---

## Source Summary

**ソース**: Anthropic eBook "Zero Trust for AI Agents" (2026-05-18) — PDF (Webflow CDN)
取得経路: Gemini CLI multimodal（curl 直 DL は permission denied、PDF のため Gemini 経路を選択）

**主張**: AI エージェントが human-in-the-loop から autonomous action へ移行する中、セキュリティは prompt 制約ベース ("vibes-based") から暗号的に強制される Zero Trust アーキテクチャへ移行すべき。中核原則は "Least Agency"（エージェントは設計タスクのみ実行可・全アクション検証・短命クレデンシャル）と "Can't beats shouldn't"（境界のアーキテクチャ強制こそ唯一スケールする防御）。

**章構成**: Intro(脅威ランドスケープ) / Part I 自律システムのセキュリティ考慮 / Part II 現在の脅威(direct+indirect prompt injection, tool pollution, identity/privilege abuse, memory poisoning, supply chain=悪意ある MCP) / Part III Zero Trust 適用(6 capability domains + Foundation/Enterprise/Advanced 成熟度ロードマップ) / Part IV 8-phase 実装ワークフロー("Design Test: Impossible vs Inconvenient") / Part V 自律脅威速度での防御運用(Agentic SOAR)

**手法**:
- 暗号 ID (X.509/HSM/TPM/attestation), mTLS, ABAC dynamic auth
- JIT/JEA 短命クレデンシャル, TEE/Confidential Computing
- Context Integrity Verification (memory hashing/signing)
- Agentic SOAR, identity-based segmentation
- 8-phase: requirements/supply-chain(AI-BOM)/boundaries/injection defense/tool access(default-deny)/credentials/memory safeguard/measure

**根拠**: vulnerability-to-exploit window の圧縮、自律エージェントには従来の境界防御が機能しない、human-centric→agent-centric security シフト。memory poisoning 0.1% 汚染で 80% 成功率。

**前提条件**: enterprise 組織 / AI インフラ提供者 / SaaS の agentic workflow。既存 Zero Trust ID 基盤 (SPIFFE/SPIRE, HSM/TPM) と "Least Agency" カルチャーシフトを要する。

---

## Gap Analysis (Pass 1: 存在チェック)

調査済み主要ファイル: `agency-safety-framework.md`, `claude-code-threats.md`, `prompt-injection-detector.py`, `mcp-response-inspector.py`, `mcp-audit.py`, `skill-security-scan.py`, `memory-integrity-check.py`, `settings.json` (88 allow/103 deny), `injection-rule-taxonomy.md`, `completion-gate.py`, `tool-scoping-guide.md`

| # | 手法(eBook) | 判定 | 現状 |
|---|-------------|------|------|
| 1 | X.509/HSM/TPM/mTLS/SPIFFE 暗号ID+ネットワーク認証 | N/A | 単一ユーザー local harness、agent 間ネットワーク認証の対象なし |
| 2 | JIT/JEA 短命クレデンシャル, ABAC dynamic auth | N/A | 配布クレデンシャル運用なし。.env chmod 600 + deny rules で代替 |
| 3 | TEE/Enclaves Confidential Computing | N/A | ホスト分離は個人 macOS に過剰 |
| 4 | Agent identity segmentation (per-instance 暗号ID) | N/A | マルチテナンシーなし |
| 5 | AI-BOM (model origin/dataset lineage) | N/A→Agent-BOM-lite 候補 | モデル訓練/デプロイをしない。per-session snapshot として翻訳可能 |
| 6 | Agentic SOAR | N/A | 個人 dotfiles に過剰。telemetry+friction loop で十分 |
| 7 | 8-phase deployment lifecycle | N/A→個人版 checklist 候補 | 本番デプロイの組織儀式。個人版として翻訳可能 |
| 8 | observability "why" の可視化 | Partial→Gap(ops層) | post-any hook + mcp-audit.jsonl あるが意図/理由可視化は基盤のみ。goal_id/task_phase/policy_reason 薄い |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | eBook が示す点 | 判定 |
|---|-------------|---------------|------|
| A | `agency-safety-framework.md` Affordances 柱(3本柱モデル) | "Least Agency" | 強化不要（既存が上位） |
| B | 「制限の強度」表(Hard block/Soft warning/Budget limit, 3段階) | "Impossible vs Inconvenient" design test(2段階) | 強化不要（3段階で包含） |
| C | `settings.json` allow-list (88 allow/103 deny) | default-deny/tool allow-listing | 強化不要 |
| D | `prompt-injection-detector.py` + `mcp-response-inspector.py` + `injection-rule-taxonomy.md` (AgentWatcher R1-R10) | indirect prompt injection/tool pollution | 強化不要 |
| E | `memory-integrity-check.py` + `agency-safety-framework.md` (Franklin et al. 2026) | memory poisoning (0.1%→80%) | 強化不要 |
| F | `mcp-audit.py` + `skill-security-scan.py` + `claude-code-threats` §8 (Snyk ToxicSkills) | supply chain (悪意ある MCP) | 強化不要 |

---

## Phase 2.5 Refine (Codex + Gemini 並列批評)

**Gemini (grounding、API クォータ枯渇のため推論ベース)**:
- "Least Agency"/"Can't beats shouldn't" は Anthropic 新造語だが概念は NIST least-privilege + OWASP Agentic の延長で novel ではない
- Least Agency 過剰適用リスク(ランタイム新ツール非対応/「制約追加→再設定」ループで開発速度低下)を eBook は未記載
- 競合: OWASP Agentic Security Initiative / NIST AI RMF / Google SAIF / MITRE ATLAS

**Codex (gpt-5.5, xhigh) — Opus の self-bias を修正**:
1. 「インフラ実装は採用ゼロ」は妥当。だが「中核概念は同等以上、強化不要」は self-bias 気味。eBook の novelty は個別脅威でなく成熟度・ライフサイクル・運用速度の枠組み側
2. N/A を技術名で正しく弾いたが原則まで N/A は雑。短命 identity/task-scoped permission/assume-breach/agent action audit は翻訳可能
3. observability "why" は採用価値あり(ROI 高): permission/decision log に goal_id/task_phase/policy_reason/revocation_trigger が薄い
4. AI-BOM 完全版は過剰だが "Agent-BOM-lite"(per-session の model/skills/MCP/tools/memory surfaces/repo trust snapshot) なら翻訳可能
5. 最優先: why observability、次点 8-phase 個人版 checklist

**修正結果**: #8 observability Partial→Gap(ops層優先) / AI-BOM N/A→Agent-BOM-lite 候補 / #7 8-phase N/A→個人版 checklist 候補。暗号系/SOAR は N/A 維持(Codex+Gemini 一致)。

---

## Integration Decisions

ユーザー選択: **全採用 (L)** — Agent-BOM-lite + why observability + 8-phase 個人 checklist。
Opus・Codex 双方が「単一ユーザー harness では境界 YAGNI、限界価値が低い」と留保。ユーザーは承知の上で全採用を明示判断。

### Gap / Partial 採用判定

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 5 | Agent-BOM-lite | 採用 (S) | per-session model/skills/MCP/tools/memory surfaces/repo trust snapshot。enterprise AI-BOM の個人翻訳 |
| 7 | 8-phase 個人版 checklist | 採用 (S) | 既存メカニズムへのポインタ主体の参照チェックリスト。`references/agent-deployment-checklist.md` 新設 |
| 8 | why observability | 採用 (M) | decision log helper + mcp-audit/prompt-injection-detector 改修。goal_id/task_phase は plumbing 不在で deferred、policy_reason/revocation_trigger のみ達成 |

### 棄却(N/A 維持)

| # | 項目 | 理由 |
|---|------|------|
| 1 | 暗号 ID/mTLS/SPIFFE | 単一ユーザー local harness に対象なし |
| 2 | JIT-JEA/ABAC | クレデンシャル配布運用なし |
| 3 | TEE/Enclaves | 個人 macOS に過剰 |
| 4 | Agent identity segmentation | マルチテナンシーなし |
| 5 | AI-BOM 完全版 | モデル訓練/デプロイ対象外 |
| 6 | Agentic SOAR | 個人 dotfiles に過剰 |

---

## Plan

プラン: `docs/plans/active/2026-05-31-zero-trust-absorb-plan.md`
Codex Spec/Plan Gate 必須。新セッションで `/rpi docs/plans/active/2026-05-31-zero-trust-absorb-plan.md` 推奨。

### Task 1: Agent-BOM-lite (S)
- **Files**: `scripts/lifecycle/session-bom.py`, SessionStart hook 配線, `session-bom.jsonl`
- **Changes**: per-session の model/skills/MCP/tools/memory surfaces/repo trust snapshot を生成・記録
- **Size**: S

### Task 2: why observability (M)
- **Files**: decision log helper 新設, `scripts/policy/mcp-audit.py`, `scripts/policy/prompt-injection-detector.py`
- **Changes**: policy_reason/revocation_trigger フィールド追加。goal_id/task_phase は plumbing 不在で deferred
- **Size**: M

### Task 3: 個人版 8-phase checklist (S)
- **Files**: `references/agent-deployment-checklist.md` 新設
- **Changes**: 既存メカニズムへのポインタ主体。企業儀式部分は個人文脈に翻訳
- **Size**: S

---

## Meta-findings

1. **Phase 2.5 が self-bias を実証修正**: 1st-party 公式ソース(Anthropic eBook)に対し Opus は「自分の harness の方が上」で過小評価する逆バイアスを示し、Codex がこれを ops-meta 層の翻訳可能性として修正した。bias mitigation の効果実証。
2. **N/A 判定の粒度問題**: 技術名(mTLS 等)で N/A は正しいが、その背後の原則(短命 identity/assume-breach/action audit)まで N/A にすると翻訳機会を取りこぼす。今後の enterprise→個人 absorb で「技術名 N/A ≠ 原則 N/A」を分離する。
3. **境界 YAGNI の明示記録**: 単一信頼ユーザー harness では enterprise 脅威モデルが効かず、採用しても限界価値が低い。30 日撤退条件を plan に明記(Build to Delete)。
