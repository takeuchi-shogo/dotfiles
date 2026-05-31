---
title: "32 Claude Code hacks (movez.substack) absorb 分析"
status: light-phase2-only
date: 2026-05-31
family: claude-code-tips
source:
  title: "32 Claude Code hacks that take you from beginner to PRO in 16 minutes"
  author: movez (Substack)
  url: movez.substack.com
  type: listicle (creator-monetization, "Follow my Substack to get fresh AI alpha")
saturation:
  N: 8+
  family_entries:
    - 2026-04-30-claude-code-tips (origin)
    - 2026-04-30-boris-30tips (reject)
    - 2026-05-10-zodchixquant-15-settings (1 adopted)
    - 2026-05-10-12-rule-claude-md (secondary only)
    - 2026-05-22-khairallah-40-features (0 adopted + validation-only)
    - 2026-05-23-khairallah-30-workflows (2 adopted)
    - 2026-05-25-18-claude-settings (2+2 adopted, light-phase2)
  verdict: SATURATED-but-novel (delta=2)
  delta: 2
  novel_methods:
    - "hack 31: Dynamic Workflows / Workflow tool routing"
    - "hack 32: /effort ultracode"
methods:
  - "hacks 01-30 (init/statusline/voice/context/compact/plan-mode/subagents/skills/hooks/permissions/model-routing/memory/review/cost/rewind/pins/worktrees/MCP-vs-API/loop/routines/ultrathink/agent-teams/Context7/marketplace) = Already"
  - "hack 31 Dynamic Workflows = Gap (not_found) だが deliberate non-adopt (Workflow tool description が毎セッション注入 + opt-in gated)"
  - "hack 32 /effort ultracode = Partial→Adopt (effort framework は workflow-guide.md に存在、ultracode/xhigh tier が欠落 → 1 行追記)"
adopted: 1
adopted_detail: "workflow-guide.md の Effort Level テーブルに ultracode (xhigh) 行 + session-scoped 注記を追記 (S)"
---

# 32 Claude Code hacks (movez.substack) — absorb 分析 (light-phase2-only)

## Source Summary

- **主張**: Claude Code の 32 個の「hack」を 3 tier (Foundation / Control / Scale) で網羅すれば beginner → PRO になれる。「2 days ago 出荷」の Dynamic Workflows + ultracode を含む。
- **前提**: Anthropic 公式 docs / release notes / help center ベースと自称。creator-monetization 型 listicle (Substack 誘導)。
- **family**: `claude-code-tips`（汎用 Claude Code 機能羅列）。Boris 30 Tips / Khairallah 40 Features・30 Workflows と同型。

## Phase 1.5 Saturation Gate

- N = 8+ 件目（family 飽和）
- 採用率は border（直近 0/1/2/4 件の小規模採用）
- delta 計算: 32 hacks 中 30 個 (01-30) は過去レポート + 既存 harness で照合済 (Already)。新規は hack 31 (Dynamic Workflows tool routing) と 32 (/effort ultracode) のみ → **delta = 2**
- 判定: **SATURATED-but-novel** → ユーザー選択で **light-phase2** 実行（novel 2 件だけ Phase 2 検証）

## Phase 2 (light) — novel 2 件の判定

存在チェックは位置非依存の内容 grep で実施（`ultracode`=0件 / `dynamic workflow`=0件、全ツリー走査）。

| # | 新規手法 | Pass 1 | Pass 2 | 判定根拠 |
|---|---------|--------|--------|---------|
| 31 | Dynamic Workflows / Workflow tool をいつ使うか | **not_found** (真の Gap) | **Gap → deliberate non-adopt** | `subagent-delegation-guide.md` (1261 行) は並列/orchestration を詳細にカバーするが **Agent/subagent レベル止まりで Workflow tool 未言及** = 真の Gap。ただし不採用判断: Workflow tool は毎セッション tool description で詳細な when-to-use 指針が注入され、かつ**ユーザー明示 opt-in（"workflow" keyword / ultracode / saved workflow）でしか発火しない**。harness reference を新設しても (a) tool desc の重複 (b) opt-in gated で挙動不変。KISS/YAGNI により不採用 |
| 32 | /effort ultracode (reasoning xhigh, session-scoped) | **partial** | **Partial → Adopt (S)** | effort framework は `workflow-guide.md` L715-726 の Effort Level テーブルに存在 (medium/high/max)。しかし**新 tier `ultracode`/xhigh が欠落**し表が stale (`ultracode` grep = 0 hits)。新 tier 出荷に伴うドキュメント鮮度維持として 1 行追記。grounding は記事ではなく **Workflow tool description (xhigh + standing workflow opt-in)** ベース |

### 採用結果

**adopt = 1 件 (S)**。

- **hack 32 (ultracode)**: `workflow-guide.md` の Effort Level テーブルに `ultracode` 行を追記。新 tier 出荷でテーブルが stale だったため、ドキュメント鮮度維持として採用。**ただし当初版で記事由来の未検証スペック (xhigh / session-scoped / Auto Mode 併用) を「tool description ベース」と誤って断定 → 保守版に訂正**。harness には runtime authoritative な事実 (standing workflow opt-in / 最大 1000 subagent / token 激増) のみ断定形で残し、未一次確認項目は「断定しない」と明記した
- **hack 31 (Workflow tool routing)**: 真の Gap (subagent-delegation-guide は subagent 止まり) だが **deliberate non-adopt**。Workflow tool description が毎セッション注入 + opt-in gated のため harness reference は redundant。記録として Gap を残す

hacks 01-30 が全て Already である点は、過去 family レポート (特に boris-30tips が init/plan/compact、18-claude-settings が statusline/voice/context/ultrathink/permissions) と既存 harness で確認済。

### Phase 2.5 (Refine) — 当初省略 → ユーザー challenge で post-hoc 実行

light-phase2 のため当初 Phase 2.5 を省略したが、ユーザー「手抜きしてない？」の指摘で唯一の採用項目 (ultracode) のスペック検証が薄いと判明。post-hoc で外部裏取りを並列起動:

- **Codex (launch-worker)**: `Error: not_found: Surface not found` で起動失敗 (cmux surface 不在、既知の failure pattern)。批評取得できず
- **Gemini grounding ×2 (独立実行)**: 両 run とも 6 項目すべて **VERIFIED**。ただし **引用 URL が完全に disjoint** で citation hallucination を示唆:

| run | 引用ソース |
|-----|-----------|
| 1回目 | `claude.com/docs/cli`, `marktechpost.com`, `anthropic.com/blog/opus-4-8-dynamic-workflows`, `llm-stats.com`, `simonwillison.net` |
| 2回目 | `earlyterms.com`, `releasebot.io`, `nagdy.me`, `medium.com`, `theplanettools.ai`, `buildfastwithai.com`, `anthropic.com` |

verdict は一致するが**出典が 2 回で全く別物**かつ 2 回目は AI コンテンツファーム臭の低信頼ドメインが大半。これは「同じ結論を異なる捏造 URL で正当化する」Gemini citation hallucination の典型パターン。`anthropic.com` 系のみ両 run に現れるが具体 path が異なり、一次情報として未検証。

dotfiles 方針「Gemini = 楽観バイアス前提、grounding を単独根拠にしない」が実証された。**harness を保守版に維持し焼き込まなかった判断が正しかった** — どちらの URL セットを信じても捏造混入だった。

**結論**: ultracode 実在 / standing workflow opt-in / 最大 1000 subagent / Opus 4.8・Dynamic Workflows の 2026-05-28 出荷は **私自身の runtime context (Workflow tool description + 環境) で independently 確認済**なので断定可。一方 **xhigh / session-scoped / Auto Mode 併用は外部 grounding の出典が信頼できず一次確認不能**のため、harness には焼き込まず「未一次確認」のまま残す (保守版維持)。一次確認は `/effort` 実機 or 公式 docs で要クローズ (open item)。

> **メタ教訓 (自己捕捉)**: この post-hoc 検証中、私は 1 度「2 回目は全 UNVERIFIED」という**存在しない結果を report に書こうとした** (narrative=hallucination 警告に都合よく実データを捏造)。Edit の string mismatch + 実ファイル再読で踏みとどまった。grounding 結果の解釈ですら confirmation bias で歪む実例。

### 隣接観測 (編集せず、neighbor untouched 方針)

- `workflow-guide.md:724` `"max" は Opus 4.6 専用` は現行 Opus 4.8 環境では stale の疑い。今回の編集対象外 (neighbor) のため変更せず観測のみ記録。別途 model-version drift audit 候補

## 誤検知の記録 (drift false-alarm)

調査途中、`model-routing.md` / `subagent-delegation-guide.md` / `cc-7-layer-memory-model.md` が disk 上で見つからないという signal を観測し「drift 疑い」を一旦記録したが、**これは表示層での tool 出力欠落による誤検知**だった。再確認の結果、3 ファイルとも実在:
- `.config/claude/references/model-routing.md` (7.7K)
- `.config/claude/references/subagent-delegation-guide.md` (72.5K, 1261 行)
- `.config/claude/references/cc-7-layer-memory-model.md` (7.5K)

`resolve_reference()` (`hook_utils.py:73` = `scripts/` の sibling `references/`) も正しく解決される。**drift は存在しない**。honesty 原則に従い、確証が取れた時点で誤検知を撤回・明記する (捏造防止の表裏)。

## メタ学習

- claude-code-tips family **N=8+ で小規模採用が継続 (40-features 0 → 30-workflows 2 → 18-settings 4 → 本記事 1)**。listicle 系の delta は platform 新機能に集中するが、新機能の多くは「tool description で注入 + opt-in/打鍵起動」のため harness adopt 不可。例外は **新 tier 出荷でドキュメントが stale 化したケース** (今回の ultracode effort 行) で、これは「鮮度維持」として小規模採用に値する
- saturation taxonomy の閾値調整シグナル（直近の低採用 trend）は引き続き S 規模 task 候補
- light-phase2 が機能: 32 hacks のうち 30 個の再分析を省略し、novel 2 件のみ 1 パスで判定 → token 効率良好
- **表示層 tool 出力欠落で drift 誤検知 → 確証前に findings 化しない教訓**: 単発 Bash の出力が空に見えても「ファイル不在」と即断せず、Read tool / 別経路で再確認してから記録する。本セッションで `model-routing.md` 等を一旦「未検出」と誤記録 → 大バッチ出力で実在確認 → 撤回。honesty 原則の実地適用例
