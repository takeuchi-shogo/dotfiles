---
source: "Kimi 2.6 + Opus 4.7 + GPT-5.5 is your cheat code (Twitter/X 経由、skool.com AI コース誘導付き)"
author: "不詳 (AI influencer 系、独立検証なし anecdote 多数)"
date: 2026-04-30
status: analyzed
adoption: "1/11 (採用 1 件、棄却 10 件)"
source-trust: "Untrusted (Scam-pattern: skool.com 誘導 + 未発表バージョン番号 + cheat code 訴求)"
---

# Kimi K2.6 + Opus 4.7 + GPT-5.5 "cheat code" absorb analysis

## Source Summary

**主張**: Kimi K2.6 (4/20 release, MIT, $0.60/M, 256k context, 65k output max, SWE-bench Verified 80.2%) + Opus 4.7 (4/16, $5/$25, SWE-bench Pro 64.3%, BigLaw 90.9%) + GPT-5.5 (4/23, $5/$30, BrowseComp 90.1%, OSWorld 78.7%) を auto-route することで、solo engineer の月次コスト (15M tokens) を $495 → $60 に圧縮 (約 88% 削減)。Kimi=bulk/agent swarm/autonomous、Opus=production/legal/vision、GPT-5.5=math/web research/computer use の三役分担。

**手法 (11 項目)**:
1. 3モデル役割分担ルーティング (bulk/production/research)
2. Kimi K2.6 を bulk worker として第3 delegation 先に
3. Opus 4.7 を production engineer として
4. GPT-5.5 を researcher/operator として
5. Native Agent Swarm (300 並列 sub-agents、4000 steps、coordinator merge)
6. Three-prompt 三役分け (bulk/production/research の system prompt)
7. Document-to-Skill upload (Kimi 専用機能)
8. Manual routing (5秒、3質問の決定木)
9. Claude Code Router (musistudio/claude-code-router)
10. CodeRouter (auto API routing)
11. Cost-as-PrimaryDriver ($495 → $60 訴求)

**根拠**: ベンチマーク比較 (SWE-bench Verified 80.2% / BigLaw 90.9% / BrowseComp 90.1% / OSWorld 78.7%)、Moonshot 自社事例 (13h で 1000 tool calls、4000 行変更、+185% throughput、5日連続自律運用)、コスト試算 ($495 / $165 / $60 の 3 シナリオ)。

**前提条件**: 個人 solo engineer、API 直接利用、月 15M tokens 程度のワークロード、agent loop が成立する task 設計。

**著者バイアス警告**:
- skool.com への AI コース誘導 (sales funnel)
- 全 benchmark 出典の独立検証なし (Moonshot 自社事例 anecdote のみ)
- "$250k engineer" / "cheat code" / "permanent" 系の SaaS marketing 文体
- Opus 4.7 / GPT-5.5 / Kimi K2.6 の release date が記事執筆時点想像 (Anthropic/OpenAI 公式ロードマップと不整合の可能性)

---

## Gap Analysis (Pass 1: Sonnet Explore による存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Multi-model routing | exists | `model-routing.md`, `codex-delegation.md`, `gemini-delegation.md`, `agent-router.py`, `triage-router.md` で 5 層 carve-out 完了 |
| 2 | Kimi K2.6 / Moonshot | not_found | 全文検索でヒットなし |
| 3 | Agent Swarm 300 並列 | partial | 小規模並列 (3-5) のみ。`agency-safety-framework.md` で blast radius 警告 |
| 4 | Role-based system prompt | partial | persona (口調) + 30+ specialist agent (責務) の 2 軸で実現 |
| 5 | Document-to-Skill upload | not_found | `skill-creator` で代替可能 |
| 6 | Claude Code Router / OpenRouter | partial | direct CLI 路線 (`codex exec` / `gemini`)、OpenRouter は言及のみ |
| 7 | CodeRouter (auto API routing) | partial | hook ベース soft routing (`agent-router.py` + `file-pattern-router.py`) |
| 8 | Cost optimization / token budget | exists | `cost-gate.py` (cycle 単位 warn $5 / stop $10)、`improve-policy.md` |
| 9 | Long-horizon autonomous (8h+) | partial | `autonomous.md` あるが詳細薄い |
| 10 | Three-question manual routing | not_found | `triage-router` (LLM 判定) の方が柔軟 |
| 11 | OSWorld / computer use | partial | Playwright + `ui-observer` agent でカバー |
| 12 | BigLaw Bench | partial | `model-debt-register.md` R-002 で評価基準として参照 |

## Pass 2: 強化判断 (Opus)

採用候補 0 件、検討余地 1 件 (R-NNN Template に open-weight watch 追記)。

### Phase 2 暫定テーブル

#### Gap / Partial / N/A

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 2 | Kimi K2.6 第3 delegation | N/A (条件付き) | open-weight 評価枠は YAGNI、採用根拠が独立検証なし anecdote のみ |
| 5 | Agent Swarm 300 並列 | N/A | `agency-safety-framework.md` の blast radius 警告と直接矛盾、small-scale specialist 哲学 |
| 6 | Three-prompt 三役分け | N/A | persona + 30+ specialist agent で実現済、IFScale 違反 |
| 7 | Document-to-Skill | N/A | Kimi UI 専用機能、`skill-creator` で代替可 |
| 8 | Manual 5秒判定 | N/A | `triage-router` LLM 判定の方が柔軟、決定木 hardcode は逆行 |
| 9 | Claude Code Router | N/A | direct CLI 路線と重複、subagent 設計と競合 |
| 10 | CodeRouter | N/A | hook ベース soft routing で十分 |
| 11 | Cost-as-PrimaryDriver | N/A | "End-to-End Completion > Per-Call Efficiency" 原則と矛盾 |

#### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|------|------|------|------|
| 1 | `model-routing.md` 5層 routing | (carve-out 完了) | — | 強化不要 |
| 3 | R-004 Opus 判断集中ポリシー | (Opus=production 想定済) | — | 強化不要 |
| 4 | R-002 Codex 深い推論委譲 | (Codex=research/壁打ち想定済) | — | 強化不要 |
| - | R-002/R-003 削除条件 | open-weight 代替 (Kimi 等) の登場可能性が抜けている | R-NNN Template に open-weight watch 行追記? | 検討余地 |

---

## Phase 2.5: Refine (Codex + Gemini 並列批評)

### Codex 批評 (codex:codex-rescue)

1. **見落とし**: Kimi K2.6 の novel 要素は単独 bulk model ではなく「open-weight / 長文 / 低単価 / swarm 前提」の同時パッケージ。ただし dotfiles には routing/subagents/cost gate/agency-safety が既にあり、実行 mechanism としては新規採用余地は薄い。残るのは「frontier model debt の削除候補を監視する watch signal」のみ。
2. **過大評価 (Q1 検討)**: Kimi K2.6 は現時点で採用不要。独立検証なし benchmark と 300 swarm 訴求は agency-safety / End-to-End Completion に反する。完全 N/A ではなく **Watch 候補が妥当**。
3. **過小評価 (Q2 検討)**: `model-debt-register.md` への watch 行追加は **Pruning-First 違反ではない** (新規 mechanism ではなく既存 debt register の削除条件強化)。
4. **前提の誤り**: 記事は per-call/benchmark/unit cost 最適化、dotfiles は End-to-End Completion + 削除条件付き debt 管理。300 並列は能力強化ではなく blast radius 増大で正面衝突。Claude Code Router/CodeRouter 採用は direct CLI + hook soft routing と運用面で重複。
5. **優先度 (Q3, Q4)**: 唯一 novel な actionable 知見は「open-weight frontier-adjacent model を model debt の削除候補として watch する」。採用 0 件は **全棄却バイアス気味** で、watch 行 1 件まで落とせるなら helpfulness が上がる。

**Codex 最終提案**: 採用 1 件 — `model-debt-register.md` に open-weight bulk delegation Watch 行のみ追加し、実行 routing は変更しない。

### Gemini fact-check (Google Search grounding)

1. **Kimi K2.6 SWE-bench Verified 80.2%** [Contested/Partly Verified]: 公式 (Moonshot Blog) は **78.5%**。80.2% は self-correction/多数決込みの数値。価格 $0.60/M は K2.6-Pro ではなく K2.6-Lite の価格である可能性が高いと HN/TechCrunch で指摘。中国国内特定インフラに最適化。
2. **300 並列 swarm / 4000 steps** [Untrusted-stat/High-Risk]: 13h/4000 行変更は内部資料として存在するが「小規模リファクタリング限定」。**Microsoft AutoGen / OpenAI Swarm 独立検証では 300 並列を超えると state conflict + context 汚染で成功率 20% 以下に急落**。185% 向上は単純作業の総量で、複雑な開発における実効性は低い。
3. **コスト 88% 削減** [Verified/Marketing-exaggerated]: ルーティング戦略自体は 2025 後半からエンタープライズで定着、しかし 88% は「全 Opus 4.7 vs 9 割 Kimi/GPT-mini」の理論上限。OpenRouter 統計等の実運用データでは **45-60% 程度に留まる**。
4. **記事著者・配信文脈** [Untrusted-source/Scam-pattern]: "cheat code" 表現や skool.com 誘導は **AIインフルエンサー高額コース販売の典型テンプレート**。未発表バージョン番号の恣意的組み合わせ手法は公式ロードマップと不整合。過去同種文脈で紹介された SaaS の多くが既存 API ラッパー、数ヶ月で終了。

### 統合: Phase 2 修正

両者の批評は同方向に収斂:
- 手法 2 (Kimi K2.6 delegation): N/A → **Already (強化可能)** に格上げ。実行 routing 追加ではなく `model-debt-register.md` への Watch 行追加なら Pruning-First 整合
- 他 10 件の N/A は両者ともに維持
- Gemini の (1)(4) で R-005 の trigger 条件を厳格化 (公式 SWE 78.5% vs 記事 80.2% 乖離 → 独立検証必須)

---

## Phase 3: Triage

提示 3 オプション:
1. **T1 (R-005 watch 行追加) を採用** — 推奨 (Codex 推奨 + Gemini で trigger 厳格化)
2. 採用 0 件 (Scam-pattern 評価を重く見て棄却)
3. 採用 0 件 + メタ知見のみ MEMORY.md に追記

**ユーザー選択**: 1 (T1 採用)

---

## Phase 4: Plan

### T1: R-005 を `model-debt-register.md` に追加 (S 規模、1 ファイル、~30 行)

**Files**: `.config/claude/references/model-debt-register.md`

**Changes**: R-004 の後、Template の前に R-005 セクションを 1 つ追加。

**内容**:
- **タイトル**: Open-weight bulk delegation Watch (Kimi K2.6 class)
- **現状のルール**: 採用しない (実行 routing 不変、Codex/Gemini を bulk worker と兼務)
- **根拠**: 4 点 — 公式 SWE 78.5% vs 記事 80.2% 乖離 / 300 並列の逆エビデンス / skool.com 系 marketing source / End-to-End Completion 原則との衝突
- **Trigger to Activate**: 独立 eval cost-adjusted win + 30 日 dotfiles local trial + tool-schema retry 率が Anthropic/OpenAI 並
- **Trigger to Drop Watch**: 90 日 signal なし、または safety/capability 不一致
- **レビュー対象四半期**: 2026-Q4

**Status**: 実行済み (2026-04-30)。

---

## 教訓・メタ知見

1. **40+ 累積 absorb 後の typical cheat-code 記事は採用率が極端に低い** — 既存 5 層 carve-out + R-001~R-004 が大半をカバー。記事の 11 手法中 10 件が N/A。
2. **Codex 批評の「全棄却バイアス補正」が機能した** — 0 件 → 1 件への譲歩。watch 行は実行に影響せず、四半期レビュー (R-005) で自然に評価される構造で低コスト。
3. **Gemini fact-check で trigger 厳格化** — 公式 78.5% vs 記事 80.2% の差を発見、独立検証必須を R-005 trigger に組み込み。SWE スコア記述の self-correction 込み/込まない区別を Activate 条件に明示。
4. **Untrusted-source/Scam-pattern label の有用性** — 2026-04-30 Learn/Build/Skip absorb で導入したラベルが今回も機能、採用閾値を高く設定する根拠になった。skool.com 誘導 + cheat-code 表現 + 未発表バージョン番号 = 三点セット。
5. **End-to-End Completion > Per-Call Efficiency 原則の保護** — cost optimization 訴求 (88% 削減) は per-call、dotfiles は完走重視で哲学的に対立。明示原則があると、対立する訴求を採用しない判断が容易になる。
6. **Watch 行という低コスト譲歩パターン** — 「採用しない」と「Watch」の中間状態を model-debt-register が提供することで、将来評価のための signal 監視が運用負担なしで可能。同種パターンを他の判断保留事項にも応用できる可能性。

---

## 棄却項目への将来的再評価条件

| # | 項目 | 再評価条件 |
|---|------|------|
| 5 | 300 並列 swarm | 独立検証で 300+ 並列の成功率 80%+ が示されるまで保留 |
| 6 | 三役 system prompt | persona + specialist agent の限界が観察されるまで保留 |
| 9 | Claude Code Router | direct CLI 路線に致命的な debt が出現するまで保留 |
| 10 | CodeRouter (auto routing) | hook routing で対応できない複雑性が観察されるまで保留 |
| 11 | Cost-as-PrimaryDriver 訴求 | End-to-End Completion 原則が放棄されるまで保留 (≈ ほぼ不変) |
| 7 | Document-to-Skill upload | Kimi UI 採用時のみ再評価 (R-005 Activate 条件と連動) |
| 8 | 5秒 manual routing | triage-router の LLM 判定がコスト/レイテンシ問題を起こすまで保留 |

---

## Related

- `references/model-debt-register.md` — R-005 が追加されたファイル
- `references/model-routing.md` — End-to-End Completion 原則の出典
- `docs/research/2026-04-30-learn-build-skip-2026-absorb-analysis.md` — Untrusted-source ラベル先行事例
- `docs/research/2026-04-29-codex-vs-claudecode-role-split-absorb-analysis.md` — 同様に著者バイアス強い記事で採用 1 件のみのパターン
