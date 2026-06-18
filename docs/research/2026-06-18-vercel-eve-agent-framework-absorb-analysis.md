---
name: vercel-eve-agent-framework-absorb-analysis
description: Vercel eve (OSS agent framework) の /absorb 分析。harness-engineering family N≈10 飽和 + TS production framework vs Claude Code CLI の scope mismatch。light-phase2 + Gemini 敵対レビューで adopt=0
type: reference
date: 2026-06-18
status: light-phase2-only
family: harness-engineering
adopted: 0
downstream-fix: gate-count-drift-check (validate_configs.sh に drift check 追加 + deny-rules-catalog.md 102→104 修正、branch chore/gate-count-drift-check)
source: https://vercel.com/blog/introducing-eve
---

# Vercel eve Agent Framework — /absorb 分析 (light-phase2 + Gemini review)

## Source Summary

**eve** は Vercel が公開した OSS エージェントフレームワーク。エージェントを「ディレクトリ構造のファイル群」(`agent/agent.ts`, `instructions.md`, `tools/`, `skills/`, `subagents/`, `channels/`, `schedules/`) として定義し、プロダクション運用インフラ (永続セッション・サンドボックス・Human-in-the-loop 承認・サブエージェント・Evals・マルチチャンネル) をビルトイン提供。「Next.js がウェブ開発を標準化したように、エージェント開発を標準化する」というポジショニング。TypeScript/Node.js + Vercel デプロイがファーストクラス。Vercel 社内で 100+ 本番エージェント運用中。2026-06 時点パブリックプレビュー。

## 判定: light-phase2, adopt=0 (Gemini 敵対レビュー通過後も維持)

**Phase 1.5 Saturation Gate**: family = `harness-engineering`、過去 absorb N≈10 (Tan thin-harness / 30-subagents / Cursor harness / dynamic-workflows / fable5-14steps / sonicgarden / Opik / coordination-patterns / Hermes 等)。採用率 ~60% で形式上 PASS (warning)。ただし **eve は「TS production agent framework 製品」で Claude Code CLI harness とは scope が根本的に異なる** ため、ユーザー選択で light-phase2 (翻訳余地のある 3 手法だけ検証) に絞り込み。

Stale-Plan Audit (Step 7): 直近 3 件 (Opik 6/14, fable5 6/12, dynamic-workflows 6/03) は全て 30 日未満 → audit skip。

## delta_methods 検証 (Pass 1 → Pass 2)

| # | 手法 | Pass1 | Pass2 | 根拠 |
|---|------|-------|-------|------|
| 1 | Durable Execution (各ステップ checkpoint化 + 自動再開) | exists | **Already (強化不要)** | production workflow runtime 固有。**Claude Code は全ターンを transcript JSONL に journaling し `--resume`/`--continue` で crash 後復元可 (platform 機能)**。加えて checkpoint skill + PreCompact hook + recall skill。手製の durable runtime は不要 |
| 2 | needsApproval (宣言的 tool-side 承認 field) | partial | **N/A (構造制約)** | Claude Code 組み込みツール定義を変更できず構造的に不可。settings.json `permissions.ask/deny/allow` が既に宣言的パターン承認層。Pass1 の「集中管理欠如」は eve と逆方向で強化にならない |
| 3 | Connections-as-File (MCP/OpenAPI + credential brokering) | partial | **Already (強化不要)** | MCP 接続は `.mcp.json` で定義済。OAuth ブラウザ認証は MCP/Claude Code runtime が担当。「モデルが認証情報を見ない」原則は env 注入 + redaction で達成。OpenAPI 直結は YAGNI |

**Gap ゼロ。** Pass 1 が出した 3 Gap (承認の集中管理欠如 / OpenAPI レイヤ / OAuth 自動更新) は全て CLI harness scope で N/A → Sonnet imagination として除外。

## Phase 2.5: Gemini 敵対レビュー (ユーザー要求で実施)

light-phase2 は Phase 2.5 省略可だが、ユーザー要求で Gemini を起動。Gemini は **adopt=2 を強く推奨** (durable session discipline + approval manifest)。全 4 提案を精査し却下:

| Gemini 提案 | 精査 | 判定 |
|---|---|---|
| ① `last-action.json` 常時書出し + SessionStart 自動 resume | Claude Code transcript JSONL + `--resume` が同等の crash 復元を**プラットフォームで提供済**。手製は再実装 | 却下 (platform 重複) |
| ② `approval-policy.yaml` 一元宣言 | settings.json `permissions` が既に宣言的パターン承認層。YAML 追加は第二の真実源で監査性悪化 | 却下 (premature abstraction) |
| ③ `credentials.yaml` + OAuth 能動認証 | MCP OAuth は Claude Code/MCP runtime の責務。harness 再実装は責務逸脱 | 却下 (responsibility 逸脱) |
| ④ Dynamic Skill Routing (必要時ロード) | Claude Code skill は元々 on-demand。dotfiles は `skillListingBudgetFraction`/`skillOverrides` で調整済 (PR #70) | 却下 (Already) |

**結論**: Gemini の 4 提案は全て「Claude Code platform が既に提供する機能の手作り再実装」または「宣言済みの物への config 追加」= 既知の Gemini 楽観/imagination バイアスの典型 (cf. log の 2026-06-17 Loops absorb でも同種を棄却)。**精査後 adopt=0 維持**。副産物として「Claude Code platform が production framework 機能 (transcript/resume・MCP OAuth・skill on-demand load) をカバー」という、当初の scope-mismatch より強い論拠を獲得。

## per-method 照合台帳 (全 11 手法)

検証した 3 手法 (上表) に加え、残り 8 手法は Already/N/A として名指し記録 (検証スキップ分の立証):

| Eve 手法 | verdict | matched_dotfiles (Already) / 理由 (N/A) |
|---------|---------|------------------|
| Agent-as-Directory (file=API) | **Already** | `.config/claude/agents/*.md` + `skills/*/SKILL.md` (Progressive Disclosure 設計) |
| Skills as Markdown | **Already** | `skills/*/SKILL.md` (frontmatter description + on-demand load も一致) |
| Subagents | **Already** | 33+ agents + superpowers:subagent-driven-development |
| Connections via MCP | **Already** | 手法3 で検証 (MCP + env 注入 + redaction) |
| Schedules (cron) | **Already** | launchd LaunchAgents + CronCreate tool + `/schedule` skill |
| Tracing + Evals | **Already/Partial** | skill-audit + Codex Review Gate + session-observer (OTel redactor) |
| Durable Execution | **Already** | 手法1 で検証 (Claude Code transcript/resume + checkpoint + PreCompact + recall) |
| needsApproval | **N/A** | 手法2 で検証 (Claude Code tool 定義変更不可) |
| Sandboxed compute | **N/A** | Vercel Sandbox / Docker / microsandbox。CLI は untrusted code 実行サンドボックス scope 外 |
| Multi-channel | **N/A** | CLI only。discord skill はあるが agent multi-channel deploy とは別物 |
| Git-based + preview deploy | **N/A** | Vercel deploy 前提。dotfiles は git+PR 運用だが「agent をデプロイ」対象ではない |

集計: **全 11 手法 Already or N/A、Gap 0**。

## Validation-only Follow-up

なし。Pass 1 調査で checkpoint/recall/careful/MCP/redaction は全て現役で正しく動作、stale fact / drift の露出なし (code-review-graph MCP の worktree 不可は既知 = Issue #54)。

## Post-absorb: 設計レンズ rally の結果 (adopt=0 を超えた実成果)

ユーザー要求で「機能照合 (adopt=0) を超えて設計原理レンズで深掘り → Gemini + Codex の意見を統合し Opus が judge」を実施。結果、eve の機能は不要でも **eve の "file=single source of truth" 思想が latent バグを露出** した。

- **発見**: gate 数を 3 者が別々に報告 (Opus 初回 109/17[破損] / Codex 71/104 / `deny-rules-catalog.md` 102/71)。実数は deny=104/allow=71/ask=0。**台帳は「102 deny (settings.json と一致)」と書きながら実際は 104 で手動同期が腐っていた**。
- **Codex + Gemini 収束**: gate 索引は「手書き doc」では腐る → **生成 + `--check` 必須**。私の当初案 (gate-inventory.md を手書き新設) は自分で誤りと判明 (7 本目の重複 doc + 腐敗)。
- **judge 判定**: ① 配線規約化 = 単独 reject (Rust dispatcher が集約済 + dir 化は実行順序を隠す)。② = adopt だが新 doc でなく **`--check`**。③ eval-driven 無人運用 = anchor のみ (既に codify 済、新設禁止)。優先順位 ②>③>①。
- **実装 (②, branch `chore/gate-count-drift-check`)**: `.bin/validate_configs.sh` に drift check 追加 (settings.json の deny/allow/ask 数と `deny-rules-catalog.md` の `## DENY/ALLOW (N)` ヘッダを照合、drift で fail)。catalog を 102→104 に修正 (破壊的 Bash カテゴリ 8→10、追加されていた `rm -r *`/`git commit -n` を反映)。pass/fail 両方向 + `task validate-configs` 全体 PASS を検証済。① の hook matcher drift は将来この check に内包可能。
- **③ の扱い**: `improve-policy.md` は deprecated のため anchor を置かず。eval 可能性境界は MEMORY (SkillOpt/sonicgarden) + learned-promotion-loop-design.md に既存 = Already。
- **meta 教訓**: 外部 framework の absorb は「機能を借りる」(adopt=0) ではなく「**設計思想で自 harness の腐敗を検出する**」価値がある。eve の正しい翻訳は「新ファイルを足す」でなく「**既存の手動同期を生成+検証に置換**」だった。

## 教訓 (family データポイント)

**production agent framework 製品 (Vercel eve / 将来の Mastra・LangGraph・CrewAI・AutoGen 等 TS/Node deploy 型) は Claude Code CLI harness と scope mismatch で構造的に採用 0 に収束する。** durable execution runtime / sandboxed compute / multi-channel deploy / git-based agent deploy は CLI に N/A、file-based agent / skills / subagents / MCP / schedules / evals は既に Already。さらに **Claude Code platform 自体が「production framework が外付けで提供する機能」(transcript/resume・MCP OAuth・skill on-demand load) を内蔵**しているため、framework パターンの大半が platform で吸収される。1 件目のため MEMORY.md 横断教訓には未昇格 (N>=3 で確立判断)。
