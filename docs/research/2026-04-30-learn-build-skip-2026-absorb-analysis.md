---
source: "What to Learn, Build, and Skip in AI Agents (2026)"
date: 2026-04-30
status: integrated
adopted: 1
---

## Source Summary

**主張**: 週次ローンチを追うのをやめ、「フィルター」を育てよ。フレームワーク乗り換えではなく、モデル/フレームワークをまたいで複利的に効く PRIMITIVES（コンテキスト設計・ツール設計・オーケストレーター-サブエージェント・evals・ファイルシステム-as-state・MCP・サンドボックス）に集中せよ。

**手法**:
- 5-test filter: 採用前に「2年後も有効か / 実績ある人が postmortem 書いたか / 既存スタックを壊すか / 6ヶ月スキップのコストは？ / 計測できるか」を問う
- Move sequence: 1 outcome を決める → tracing+evals を先に → single-agent loop → product mindset → boring infra → unit economics
- Friday 30min habit: Anthropic eng blog / Simon Willison / Latent Space / postmortem 1-2 件
- "Credential is the artifact" — 出荷が唯一の資格

**根拠**: 著者は匿名（"$250k+ offers, running technical at company in stealth"）。引用統計（Spotify 25% veto / 40% retry 削減 / Claude Code 47% regression / LangGraph シェア 1/3）は Gemini fact-check で全件 NOT VERIFIED — 例示として扱う。

**前提条件**: 生産エージェントを個人または小チームで運用する文脈。LangGraph/Mastra/Pydantic AI / Langfuse / E2B 等の具体的スタック推奨は production agent 前提であり、個人 dotfiles harness とは直交する。

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 既存メカニズム |
|---|------|------|------|
| L1 | Context engineering / window assembly / cache discipline / context rot | Already | references/context-constitution.md, cc-7-layer-memory-model.md, context-compaction-policy.md, PreCompact/PostCompact hooks |
| L2 | Tool design / actionable error messages | Already | aci-tool-design.md #3 に "Error: ファイルが見つかりません: /src/main.ts. 提案: 絶対パスを使用してください" 形式が明示 |
| L3 | Orchestrator-subagent / single-agent default / parallel caution | Already | references/subagent-delegation-guide.md, multi-agent-coordination-patterns.md, agency-safety-framework.md, Task Parallelizability Gate |
| L4 | Evals + golden datasets / regression set | Already | scripts/eval/split_holdout.py, golden-check.py hook, gaming-detector.py, AutoEvolve, friction-events.jsonl |
| L5 | File-system-as-state / harness > model / checkpointing / resumability | Already | checkpoint skill, HANDOFF.md, RUNNING_BRIEF.md, resume-anchor-contract.md, SessionStart/Stop hooks; CLAUDE.md core_principles "Scaffolding > Model" |
| L6 | MCP 概念分離 / registry 利用 | Already | mcp-toolshed.md, mcp-audit.py hook, claude-code-threats.md, 5-min audit checklist |
| B2 | Model swappability / quarterly re-eval | Already | references/model-routing.md, model-debt-register.md, cross-model-insights.md, TELOS quarterly cycle |
| F1 | 5-test filter（採用判断の機会費用フレーム） | **Partial** | triage-criteria.md に ROI table 有り。Test 4「6ヶ月スキップのコスト？」の機会費用反転は未コード化 |
| F2 | 6ヶ月 defer habit | N/A | harness-stability 30日評価と重複。6ヶ月は個人 dotfiles には遅すぎる |
| M2 | Friday 30min reading habit + source list | N/A | weekly-review SKILL.md は GTD 寄り (GitHub Issue + Obsidian Inbox)。docs/research/_index.md が系統的取り込みとして機能しており別管理で十分 |
| B1 | LangGraph / Langfuse / E2B adoption | N/A | Production agent stack; 個人 harness とは直交 |
| M1 | Unit economics ($-per-action) 計装 | N/A | $50K/month スケール前提; 個人 dev 不要 |
| S1 | 明示的スキップリスト文書 | N/A | Pruning-First 違反。docs/research/ 散在参照で役割を果たしている |
| W1 | Consolidated watch list | N/A | docs/research/_index.md が実質 watch list として機能 |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| L2 | aci-tool-design.md #3 でエラーメッセージ形式を明示 | 記事の "Max tokens 500 exceeded, try summarizing first" と同一原則 | 不要 | **強化不要** |
| F1 | triage-criteria.md ROI table | Test 4「機会費用の反転」—「採用しなかった場合の損失」ではなく「スキップした場合のコスト≒ほぼゼロ」という視点が欠落 | 5-test section (~20行) を triage-criteria.md に追記 | **採用** |
| M2 | weekly-review SKILL.md (GTD フォーカス) | 業界シグナルトリアージには wrong fit | docs/research/_index.md で代替可 | **N/A に格下げ** |

---

## Integration Decisions

### 採用: F1 — 5-test filter (Launch Filter section 追記)

**採用理由**:
- 既存 triage-criteria.md の ROI table はコスト×効果の掛け算。記事の 5 tests は「時間軸 / 著者バイアス / スタック破壊 / 機会費用 / 計測可能性」—直交するフレーム
- 特に Test 4「6ヶ月スキップのコストは？(通常ゼロ)」は FOMO を機会費用に反転する視点であり、Pruning-First を補強する
- コスト: ~20行追記のみ (S size)
- リスク: 低（既存 ROI table と競合しない加算的変更）

### スキップ一覧

| # | 項目 | 理由 |
|---|------|------|
| L2 | Tool error message 強化 | Already: aci-tool-design.md #3 が同一原則をカバー |
| F2 | 6ヶ月 defer habit | harness-stability 30日評価と重複; 6ヶ月は個人 dotfiles には過剰 |
| M2 | Friday reading habit | weekly-review SKILL.md は GTD 用途; _index.md で代替 |
| B1 | Production stack adoption | 個人 harness ユースケースと直交 |
| M1 | Unit economics 計装 | スケール前提が異なる |
| S1 | スキップリスト文書 | Pruning-First 違反 |
| W1 | Watch list 文書 | _index.md が既に機能 |

---

## Plan

### T1 (DONE): triage-criteria.md に Launch Filter (5 tests) セクション追記

- **Files**: `/Users/takeuchishougo/dotfiles/.config/claude/skills/absorb/references/triage-criteria.md`
- **Changes**: `## Launch Filter (5-test)` セクション追記 (~20行)。内容: 5 tests 箇条書き + 既存 ROI table との使い分け注記
- **Size**: S

### T2 (本ファイル): Analysis report 作成

- **Files**: `/Users/takeuchishougo/dotfiles/docs/research/2026-04-30-learn-build-skip-2026-absorb-analysis.md`
- **Size**: S

### T3: MEMORY.md インデックスエントリ追加

- **Files**: `/Users/takeuchishougo/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`
- **Changes**: 外部知見索引セクションに本記事の1行エントリを追加
- **Size**: S

---

## Lessons / Reflections

**記事の品質評価**: メタレベルの業界ガイド。実質的な主張の ~80% が既存の 40+ /absorb ランで取り込んだメカニズムとマッピングした — 過去の蓄積が正しく複利化していることの確認。

**最も新規性の高い貢献**: Test 4「6ヶ月スキップのコスト？」—採用意思決定を機会費用フレームに反転する。FOMO を積極的に逆転するツールとして triage-criteria.md に追記する価値がある。

**著者バイアス警告**:
- 匿名 + 金銭的 humblebrag ("$250k+ offers") — 信頼性係数は中程度
- 引用統計 (25% / 40% / 47%) は Gemini fact-check で全件 NOT VERIFIED — 例示として扱い、mechanism 採用の根拠にしない
- "credentials is the artifact" フレーズ: 刺激的だが、dotfiles harness の設計原則 ("Build to Delete" / "Scaffolding > Model") と概念的に整合する

**Pruning-First 適用結果**:
- 検討した 14 手法中、採用 1 件 / Already 7 件 / N/A 6 件
- Codex critic は BG kill で使用不可。代替として aci-tool-design.md / weekly-review SKILL.md を直接読んで同等の格下げ判定を実施 — file-direct verification は Codex 代替として有効

**プロセス知見**: メタレベル記事は「既存メカニズムが存在するか？」の構造的検証で大半が処理できる。Codex/Gemini の second-opinion よりファイル直読みの方が速い場合がある。採用リスクは "Already を helpful-bias でもう一度採用してしまう" こと — 必ず既存ファイルを読んで確認せよ。
