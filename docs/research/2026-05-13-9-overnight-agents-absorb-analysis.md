---
source: "The 9 Claude Agents That Work While You Sleep (Nav Toor / @heynavtoor, ECC framework distribution)"
date: 2026-05-13
status: skipped
---

## Source Summary

**主張**:
1. 9 つの "overnight agents" を `.claude/agents/<name>.md` に save し `crontab -e` で schedule すれば、$540K 相当 payroll を 7 AM までに代替できる
2. "Asynchronous Claude is 10x more valuable than synchronous Claude"
3. 3 install パス: Claude Code (`.claude/agents/` + cron) / Claude.ai (Sub-Agents + Scheduled Tasks) / Claude Desktop + Cowork

**手法 (9 agents)**: overnight-briefing (4 AM, Chief of Staff) / overnight-research (2 AM, Research Analyst) / inbox-triage (6 AM, EA) / numbers (3 AM, Financial Analyst) / overnight-code (1 AM, Junior Engineer) / competitive-watch (5 AM, Competitive Intel) / overnight-content (11 PM, Content Producer) / calendar-prep (5:30 AM, EA prep) / knowledge-distillery (midnight, Research Librarian)

**根拠**: なし。"$540K payroll"、"10x more valuable"、"smartest one-person operators... six months ago" は全て出典なし主張。各 agent 内訳の加算は実際 $855K で計算も合わない (article では $540K と記載)。

**前提条件**: founder/operator/freelancer role、MCP connector (Gmail/Outlook/Calendar/Slack/Stripe/Mixpanel/Pocket/Readwise/podcast)、Managed Agents API / Routines アクセス

**著者の正体 (Gemini grounding + gh api 独立検証)**:
- **Nav Toor (@heynavtoor)**: 実在のインフルエンサー、ECC ("Everything Claude Code") framework の普及者
- 記事 = ECC repo (`affaan-m/everything-claude-code`) の 9-agent slice + marketing narrative wrapping
- ECC repo 実体: MIT, 180,436 stars / 27,811 forks / 170+ contributors / created 2026-01-18 / 最新 push 2026-05-12 (=昨日)、README 記載は "140K+ stars" (数字に astroturf 疑念あり、ただし contributors 数と pushed_at から active 開発は確認)
- 記事の 9-agent は ECC `agents/chief-of-staff.md` 等の subset。Article は ECC 全体ではなく overnight night-shift narrative に slice した distribution material
- 商業文脈: ecc.tools サイト存在、`ecc-universal` / `ecc-agentshield` npm packages、150+ GitHub App installs、Anthropic Hackathon Winner 自称

**著者バイアス**:
- $540K / 10x / "smartest one-person operators six months ago" 出典なし → Skool/newsletter funnel pattern と整合
- ただし技術主張は Verified (Routines/`/schedule`/Cowork/`.claude/agents/*.md` は実機能)
- zodchixquant (2026-05-10) と同パターン: **集客記事だが技術主張は real**

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | overnight-briefing | N/A | role mismatch: solo dev 用途無し、`/timekeeper` skill (plan/midday/review) + `/daily-report` で覆われる |
| 2 | overnight-research | Already | `/research` skill (parallel multi-agent) + `task-registry.jsonl` + Managed Agents API pilot |
| 3 | inbox-triage | N/A | role mismatch: high-volume inbox 無し。Gmail MCP は deferred tools で存在するが未利用 |
| 4 | numbers | N/A | role mismatch: 監視 dashboard (Stripe/Mixpanel) 無し |
| 5 | overnight-code | Already | `/autonomous` + `gh-fix-ci` (mizchi/skills) + `/create-pr-wait`。dotfiles の lefthook + `protect-linter-config` ガードで overnight 自動 PR は逆に risky |
| 6 | competitive-watch | N/A | role mismatch: 監視対象競合無し (dotfiles project) |
| 7 | overnight-content | N/A | role mismatch: 定期 content cadence 無し。`mizchi-blog-style` で on-demand 対応 |
| 8 | calendar-prep | N/A | role mismatch: 外部ミーティング少。Calendar MCP は pilot |
| 9 | knowledge-distillery | Already | `/digest` (Literature Notes) + `/absorb` (article integration) + Obsidian Vault (`05-Literature/`) で完備 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `/research` skill | "Confidence: High/Medium/Low + 1 sentence why" の必須化 | 既に `templates/analysis-report.md` で confidence 記載慣行あり、新規追記不要 | 強化不要 |
| S2 | `/timekeeper` plan | "1-page brief、brevity is the product" の rule | 既に Obsidian Vault Daily Note format で brevity 制約あり | 強化不要 |
| S3 | `/autonomous` overnight code | flaky test/lint/dep auto-fix の draft PR pattern | `gh-fix-ci` + `/create-pr-wait` が on-demand 同等。schedule 自動化は dotfiles harness と incompatible | 強化不要 |
| S4 | `scheduling-decision-table.md` | "overnight artifact" 用途の例示無し | 1 行 recipe 例追加候補 (検討、本 absorb では実行せず) | 強化可能 (棚上げ) |

## Phase 2.5 Refine (Codex + Gemini 並列批評)

**Codex (codex:codex-rescue)**: deep reasoning 起動成功も forwarder 制約で resume summary 取得失敗。中間結果は破棄。

**Gemini (1M grounding)**: 6 主張中 Verified 5 / Partial(Likely Fabricated) 1
- ✅ Claude.ai Routines (`/schedule` skill 経由、min 1h interval)
- ✅ Cowork (Desktop からローカル env access agent)
- ✅ `.claude/agents/*.md` YAML frontmatter 標準
- ✅ Nav Toor / ECC framework 実在
- ⚠ $540K = Agix Tech 系試算流用 (Likely Fabricated)
- ✅ akira_papa_AI / ksimback / mizchi async workflows 実在

**独立検証 (gh api)**:
- `affaan-m/everything-claude-code` 実在、MIT、180K stars、`agents/chief-of-staff.md` を含む 50+ agent files、`commands/evolve.md` / `cost-report.md` 等の独自コマンド多数、cross-harness 対応 (Claude Code / Codex / Cursor / OpenCode / Gemini)

**修正されたバイアス**:
- 初期評価 "6 件目の content farm Reject" → **過剰 Reject**
- 正しい評価: "技術 = Verified、数値 = Fabricated、role = mismatch" の三層分離
- zodchixquant 系列 (5 件目) と同型: 集客記事だが技術主張は検証する価値あり

**記事の technical install 手順の誤導**:
- "Save as `<name>.md` in `.claude/agents/`. Schedule with cron: `crontab -e`" は半分嘘
- subagent 定義 (`.claude/agents/*.md`) は Task tool 経由でしか fire されない
- cron で動かすには `claude -p` wrapper か `/schedule` (Managed Agent routine) が必要
- 記事はこの中間層を曖昧化している

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1-9 | 全 agent | スキップ | role mismatch (solo dev) + Already covered の組み合わせで一律スキップ |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1-S3 | `/research`, `/timekeeper`, `/autonomous` | スキップ | 強化不要 |
| S4 | `scheduling-decision-table.md` overnight recipe | 棚上げ | 別途必要時に検討、本 absorb では実行せず |

### 副次的 meta 発見

| # | 発見 | 採用 |
|---|------|------|
| M1 | ECC framework (`affaan-m/everything-claude-code`) の存在 | **MEMORY.md に 1 行 reference 追記** (将来 `/absorb` 候補として認識) |

## Plan

### Task 1: MEMORY.md に ECC framework reference 追加

- **Files**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`
- **Changes**: 「外部知見索引」セクションに本 absorb レポートへのリンク + ECC framework が deeper audit 候補である旨を 1 行記載
- **Size**: S (1 line)

### Task 2 (棚上げ): ECC framework 全体 deep audit

- **対象**: `affaan-m/everything-claude-code` の skills/agents/hooks/commands/rules
- **規模**: L (30-60 分の `/absorb` 別セッション)
- **判断保留理由**: ユーザー決定通り、今回は別 audit として後回し
- **トリガー**: ECC の特定 pattern が dotfiles で必要になった時、または定期 audit ローテーション

## 教訓 (本セッション)

1. **Content farm signal だけで Reject すると見落とす**: zodchixquant (2026-05-10) に続く 2 件目の "集客記事だが技術主張は real" パターン。`feedback_absorb_thoroughness.md` の鉄則 (「見落としは問題すぎる、手を抜かない」) が改めて有効
2. **`gh api` 独立検証は必須**: Gemini grounding も hallucinate しうるため、GitHub repo 存在検証は `gh api` で直接取る
3. **Codex forwarder 制約**: `codex:codex-rescue` subagent は単一 `task` 呼び出しのみ許可。deep reasoning resume には別 invocation が必要、または cmux Worker 経由を検討
4. **role mismatch は Reject の primary 根拠になる**: founder 向け recipe を solo dev に適用しても価値希薄。MEMORY.md の user role profile を absorb 判定に必ず参照すべき
5. **180K star は astroturf 疑念あり**: GitHub `stargazers_count == watchers_count` の数字膨張は星 botting の典型 signal。MIT + contributors 数 + commit history の active 度で別途評価する
