---
date: 2026-06-20
source:
  title: "How to Build Your First Team of AI Agents Using Claude (Full Course)"
  author: "Khairallah (@eng_khairallah1)"
  url: "(twitter/x thread, posted by user)"
  type: "twitter-thread / listicle"
family: multi-agent-orchestration
saturation_gate: SATURATED-pure-rehash
prior_count: 30+
adoption_rate: ~10% (last 5 articles)
delta: 0
verdict: adopt 0 / continue selected by user / outcome unchanged
status: light-phase2-only
phase_2_5_status: partial (codex retry succeeded with bounded timeout, gemini failed)
phase_2_5_failures:
  - codex_first_attempt: silent exit / 0-byte output via Bash tool (known limitation, see feedback_codex_bash_tool_unreachable.md). Retry with shorter prompt + bounded timeout (480s) + tail -30 succeeded
  - gemini: IneligibleTierError (auth requires migration to Antigravity, runtime drift)
phase_2_5_substitute: blueprint-pattern.md grep + per-method ledger self-audit + Codex retry critique
---

# Khairallah "How to Build Your First Team of AI Agents Using Claude" — Absorb 分析

## Source Summary

著者 @eng_khairallah1 (Twitter/X) が投稿した agent team 入門 listicle (full course 形式)。
構成: mental model 切り替え → 3 roles (orchestrator/specialists/critic) → 5 stages (single agent → handoff → tools → automation → reliability) → content team の実例 → mistakes that kill agent teams。

主張: 単一 agent ではなく orchestrator + specialists + critic の team で組めば、20 分で 1 日分の仕事を automate できる。MCP/connectors で agent に道具を渡し、orchestrator で delegation を自動化、evaluation + memory + failure handling で reliable にする。

ベンダーバイアス: なし (フォロー誘導はあるが商用 product 推奨なし)。Anthropic 公式 doc (orchestrator-workers / MCP / sub-agents) の平易な再パッケージ。

## Phase 1.5: Saturation Gate

- **Family**: multi-agent-orchestration
- **過去件数 N**: 30+ (`docs/research/` の grep 結果、直近5件は 2026-05-25 〜 2026-06-20)
- **直近の同 tier 記事**: `2026-05-25-claude-agent-teams-7steps-absorb-analysis.md` (構造的に同型の「How to build agent team」入門 listicle)
- **採用率**: 直近5件平均 ~10% (Jey 2/20, Kimi 1/N borderline, 他)

判定: **SATURATED-pure-rehash** (台帳で delta=0 立証 → user に skip 推奨提示 → user が continue 選択)

## per-method 照合台帳 (全 current 手法、rehash の matched_prior 名指し済)

| # | current 手法 | verdict | matched_prior (ファイル名 + 引用句 + 同等性の理由) |
|---|---|---|---|
| 1 | 3 roles (Orchestrator / Specialists / Critic) | rehash | `docs/research/2026-04-11-multi-agent-coordination-patterns-analysis.md` の 5パターン統合ビュー (Orchestrator-Subagent / Agent Teams / Generator-Verifier) + `.config/claude/agents/code-reviewer.md` + `codex-reviewer.md` で Worker+Critic 配線済。同一概念 (delegation + assembly + standard-based review) |
| 2 | role/standard/format/boundaries の system instruction 構造 | rehash | `docs/research/2026-05-02-30-subagents-2026-absorb-analysis.md` で **Self-Rejection Rule pattern** + **single-purpose enforcement** 採用済 (`references/agent-design-lessons.md`)。全 33 subagent (`code-reviewer.md` 28KB / `security-reviewer.md` 17KB) が同フォーマット |
| 3 | Worker + Critic manual handoff loop | rehash | `CLAUDE.md` ワークフロー表 S/M/L 全規模で「Codex Review Gate (codex-reviewer + code-reviewer 並列)」を必須段階に codify。Spec/Plan Gate も同型の worker→critic 構造 |
| 4 | MCP / connectors (tools for agents) | rehash | `settings.json` に context7 / playwright / openaiDeveloperDocs / claude.ai (Gmail/Calendar/Drive) 配線済。`mcp-audit.py` の VeriGrey Tool Filter で **`sys.exit(2)` による hard block** enforcement (`docs/research/2026-06-17-agentic-code-review-absorb-analysis.md` 関連)。記事の「narrowest permissions + human in loop」は `careful` skill (本番操作ガード) + `freeze` skill で実装 |
| 5 | Sub-agent automated orchestration (in agentic tooling or API direct) | rehash | `Agent` tool (33 subagent registered) + `Workflow` tool (dynamic workflows, 12 パターン) + `delegate-implementation` skill。**Workflow tool 本体は `docs/research/2026-06-03-dynamic-workflows-absorb-analysis.md` で deliberate non-adopt 維持** (tool description 自動注入 + opt-in gated で harness reference 不要) |
| 6 | Evaluation set (10 test inputs, run after every change) | rehash | `scripts/eval/regression-gate.py` (retired, 2026-06-14 decommission-log で flag) + `skill-audit` skill (A/B benchmarking + health audit, 全 skill 横断) 既存。記事は具体的構造提案なし |
| 7 | Persistent memory (project memory + artifacts) | rehash | `references/cc-7-layer-memory-model.md` (7-layer model: working set / session / project / cross-project / vault / web / auto-memory) + MEMORY.md (user/project/local 3 スコープ) + auto-memory system 既存。記事の「project memory + artifacts」より深い |
| 8 | Failure handling + hard limit on critic-worker loops | rehash | `references/blueprint-pattern.md`: 「**エージェントノードは `max_iterations` で上限を設ける**」「`max_iterations` を超えた場合は自動的に `on_failure` アクションを実行する」を必須属性として codify。`blueprints/feature.yaml` / `bug-fix.yaml` / `refactor.yaml` / `autocover.yaml` で max_iterations: 2-5 設定済。`failure-escalation-protocol.md` + `careful` skill + completion-gate hook + silent-failure-hunter agent で escape hatch 完備 |

**delta_methods**: ∅ (verdict が novel または ambiguous の行なし)
**delta = 0** — 全 8 手法に matched_prior 3点セット (ファイル名 + 引用句/heading + 同等性の理由) を明示できた

## Phase 2.5: セカンドオピニオン (partial)

### Codex (success on retry)

初回呼び出し (Bash tool → `codex exec` 直接) は silent exit / 0-byte output で 5 分待機後タイムアウト (`memory/feedback_codex_bash_tool_unreachable.md` で既知)。retry を bounded timeout (480s) + `tail -30` + 短縮プロンプトで実行 → 成功 (gpt-5.5 / reasoning effort: high / 20,453 tokens)。

Codex の批評 (原文):

> 概ね `delta=0 / 採用0 skip` で妥当。ただし「10-case eval」が再現可能な評価セット、「role-standard-format-boundaries」が明文化済み契約なら別物。未文書なら差分候補。

Codex 指摘の事実確認:

1. **10-case eval として再現可能な評価セット contract**: **未文書 (drift 確認)**
   - `data/eval-cases*` 不在 (`find` で 0 hit)
   - `scripts/eval/regression-gate.py` は retired (`docs/decommission-log.md` に flag, regression-suite.json 未生成で silent-skip)
   - 代替: `skill-audit` skill (A/B benchmarking) + Codex Review Gate (S 規模以上必須) で実態として review/eval を回しているが、「input + golden output の固定 10 ケース」という形の reproducible eval contract は存在しない
   - 判定: **validation-only follow-up** (採用しない) — sonicgarden self-improving loop YAGNI 教訓 + regression-gate retirement の経緯から、新規に 10-case suite を構築する ROI 低。skill-audit + Review Gate の 2 段構えで replace 済

2. **role/standard/format/boundaries の明文化された agent contract template**: **未文書 (drift 確認)**
   - `agent-design-lessons.md` は Self-Rejection Rule pattern / Codified Context / Agent Sizing Guidelines / 設計チェックリスト / Requires Escalation Rubric を持つが、**Role + Standard + Format + Boundaries の 4 構造を一括テンプレートとして codify した箇所は欠落**
   - subagent frontmatter (`description / tools / model`) には Standard / Format / Boundaries フィールドなし
   - 実態は全 33 subagent で role + boundaries を散文で書いているが、Khairallah の 4 構造を明文化したものではない
   - 判定: **validation-only follow-up** (採用しない) — Sonnet imagination 罠回避: 既存の single-purpose enforcement + Self-Rejection Rule pattern + 設計チェックリストで agent quality は確保されており、別途 4 構造テンプレートを追加する ROI が既存仕組みより明確に高いとは言えない。記事の generic 4 構造は「契約を書け」という概念レベルの提案で、dotfiles の既存 agent-design-lessons.md より深いものではない

### Gemini (failed, runtime drift)

`gemini -p` を著者調査 + 周辺知識補完で起動 → **IneligibleTierError** で死亡。Gemini Code Assist for individuals は 2026-06 時点で sunset、Antigravity 移行要求が出るようになった。Phase 2.5 で Gemini 役を `gemini -p` で常用できなくなったのは運用 drift (`reference_gemini_cli_sunset.md` 等の new memory が必要)。

### 代替検証

両 critic 一方失敗の補強として:
1. **blueprint-pattern.md grep による #8 検証**: 唯一「もしかして Gap」だった critic-worker loop の hard limit が `max_iterations` 必須属性で codify 済と確認 (eyeballed grep hit: `references/blueprints/feature.yaml` `bug-fix.yaml` `refactor.yaml` `autocover.yaml` で `max_iterations: 2-5` 設定済)
2. **per-method 照合台帳の self-audit**: 全 8 手法に matched_prior の 3 点セットが揃ったことを確認

### degraded のリスク評価

Gemini-only failure のため model-family diversity による self-preference bias 補正は Codex 1 model のみで提供。ただし本記事は Anthropic 公式 doc の平易な再パッケージで、dotfiles 側にこの分野で 30+ 件の prior absorb が蓄積。Codex は条件付きで 2 件の drift を指摘 (eval contract / agent contract template) し、両方とも事実確認で「未文書だが ROI 低」と validation-only に降格できたため、judgement は十分強い。

## Phase 3: 判定

- **Gap / Partial / N/A**: なし
- **Already (強化可能)**: なし — Pass 2 で全項目について「記事の具体例で既存仕組みを強化できる点」を探したが、本記事は generic listicle で具体例なし。Sonnet imagination 罠 (generic feature noun からの想像追加) は回避

**採用 0 件確定**

## Phase 4: 統合プラン

なし (採用 0 件のため `tmp/plans/` / `docs/plans/` への保存不要)

## Validation-only Follow-up

なし — 記事 framing が dotfiles 内の stale fact / drift を露出するパターンも見つからず。Khairallah の主張する 5 stages は全て dotfiles で stage 5+ を超えて実装済 (evaluation: skill-audit / memory: 7-layer model / failure: silent-failure-hunter + completion-gate + max_iterations) で、記事が想定する読者層 (stage 0 → stage 1 の入門者) を完全に超えている。

## 教訓

1. **Phase 1.5 Saturation Gate は機能している** — N=30+ family の N+1 件目に対し台帳で delta=0 を立証して skip 推奨を提示。User の「continue」選択も尊重しつつ adopt 0 の outcome は変わらず、コストは最小限 (mini report のみ)。
2. **Codex via Bash tool は依然として到達不能** — `feedback_codex_bash_tool_unreachable.md` の知見が再現確認された。Phase 2.5 で Codex を呼ぶ際は cmux Worker (`launch-worker.sh`) が正規パスだが、Auto Mode + permission storm を避けるなら user に明示的にお願いするか、最初から fallback (degraded mode) を選ぶ判断もある。
3. **Gemini Code Assist for individuals は sunset** — Antigravity 移行要求が出るようになり、`gemini -p` が Phase 2.5 で常用できなくなった。Phase 2.5 の Gemini 役は WebSearch + WebFetch + Codex のみで代替する設計に切り替える必要がある (これは別 absorb の対象になり得る運用 drift)。
4. **入門 listicle は SATURATED family で台帳照合の練習素材として価値あり** — 採用は 0 でも、(a) Phase 1.5 台帳の name-pointing 立証フローの validation (b) blueprint-pattern.md の loop limit が再認識される副次効果 (c) Codex/Gemini 両 critic 失敗の運用 drift 露出 という 3 つの副産物が出た。
