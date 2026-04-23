---
status: active
last_reviewed: 2026-04-23
---

# Skill Invocation Patterns

> 出典: Garry Tan "Thin Harness, Fat Skills" 原則 1 + 10（Recipes, Not Orders / Same Process, Different World）
> 紐付け: `skill-writing-principles.md` 原則 1, 3.5

同じ skill を異なる world（データ・制約・目的）で使い回すための設計と事例集。
skill は method call であり、固定部分（process）と差し替え部分（parameters）の境界を明示することで複利的に再利用できる。

## 設計原則

### 境界を明示せよ — 何が固定で、何が差し替えか

skill を書くときは以下の 3 つを分けて記述する:

| 層 | 内容 | 例 |
|----|------|------|
| **Process (固定)** | step の順序、判断基準、output 形式 | Phase 1→2→3 の構造、checklist |
| **Parameters (差し替え)** | 入力データ、対象、criteria、constraints | URL, 期間, 対象ファイル, 深さ |
| **Context (環境が供給)** | CLAUDE.md, MEMORY.md, 現在時刻, repo 状態 | 自動 inject される |

**判断基準:**
- Process を parameterize しない（process そのものが変わるなら別 skill）
- Parameters は skill 本文の上部で宣言する（frontmatter 拡張ではない — principle 1 に反する）
- Context は skill 本文に書かず、harness が供給する

## 事例集

### 事例 1: `/improve` — 同じ pipeline を異なる深度で回す

**Process (固定):** COLLECT → Analyze → Action → Refine

**Parameters:**
- `--deep`: 深度（quick / deep / forensic）
- `--evolve`: AutoEvolve 連携 (yes/no)
- `--iterations N`: 反復回数

**Worlds:**
| 用途 | 呼び出し | 差し替え |
|------|---------|---------|
| 週次ルーチン改善 | `/improve` | デフォルト（quick, 1 iteration） |
| 月次深掘り監査 | `/improve --deep` | learnings 全走査、5 iteration |
| 設定進化ループ | `/improve --evolve` | AutoEvolve へ接続、BG 実行 |

**境界の固定点:** COLLECT → Analyze → Action の順序と Convergence Check は差し替え不可。

---

### 事例 2: `/absorb` — 同じ統合フローを異なるソースで実行

**Process (固定):** Extract → Analyze → Refine → Triage → Plan → Handoff

**Parameters:**
- Source type: URL / テキスト / repo / 既存レポート
- Integration scope: skills / references / CLAUDE.md / MEMORY.md

**Worlds:**
| 用途 | 差し替え |
|------|---------|
| 外部記事の取り込み | URL または貼り付けテキスト、Extract を Haiku に委譲 |
| 論文の統合 | PDF、Extract を Gemini に委譲（1M コンテキスト） |
| 他人の dotfiles 分析 | repo path、Phase 1 を Gemini の全体スキャンに置換 |
| 既存レポートの再評価 | `docs/research/*.md`、Phase 1 スキップ |

**境界の固定点:** Triage → Plan → Handoff の user 対話フローは差し替え不可。

---

### 事例 3: `/research` — 同じ分解・統合構造を異なる問いで実行

**Process (固定):** 問いの分解 → 並列 dispatch → 結果統合 → レポート生成

**Parameters:**
- Question (主問い)
- Depth (shallow / medium / deep)
- Model routing (Claude / Gemini / Codex の配分)

**Worlds:**
| 用途 | 差し替え |
|------|---------|
| 技術比較調査 | 「A vs B」、各モデルに同じ比較軸を投げる |
| 文献レビュー | 論文リスト、Gemini に全論文を 1M で投げる |
| セカンドオピニオン | 設計判断、Codex/Gemini に独立批評を依頼 |

---

### 事例 4: モデル別ルーティング (CLAUDE.md `agent_delegation`)

**Process (固定):** 「Opus は判断、実作業は委譲」の判断フロー

**Parameters:**
- 作業性質（定型・深推論・大コンテキスト・マルチモデル）
- Blocking / Non-blocking

**Worlds:**
| 作業 | モデル | 固定要素 |
|------|-------|---------|
| ファイル探索・実装 | Sonnet | 委譲判断フロー |
| WebFetch + 要約 | Haiku | 同上 |
| 設計壁打ち・レビュー | Codex | 同上 |
| コードベース全体分析 | Gemini | 同上 |

**境界の固定点:** 「Opus が判断・統合に集中、実作業は委譲」のメタ原則は差し替え不可。

## アンチパターン

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | Process が変わるのに同じ skill 名で分岐 | 別 skill に split する |
| 2 | Parameters を frontmatter に仕様化して形式を太らせる | skill 本文の Usage セクションで宣言する |
| 3 | skill に context (user 属性・現在時刻) を埋め込む | harness が供給する（動的境界マーカー問題） |
| 4 | 1 skill が 10 以上の world を抱え込む | 3-5 world 超えたら split または pattern family に分ける |
| 5 | Parameter が存在するのに Usage 欄で例を示さない | 各 parameter に最小 1 事例の呼び出し例を付ける |

## 新 skill 作成時のチェック

- [ ] Process (固定) と Parameters (差し替え) の境界を明示したか
- [ ] 最低 2 つの異なる world で呼び出し例を示したか
- [ ] 3 つ以上の world を抱えるなら、それぞれが同じ process を本当に共有しているか
- [ ] Parameters が増えすぎて skill が「設定ファイル」化していないか
- [ ] context (user 属性等) を埋め込んでいないか（動的境界マーカー問題に注意）

## 関連文書

- `skill-writing-principles.md` — 原則 1 (指示を書け), 原則 3.5 (skill 化閾値)
- `determinism_boundary.md` — process と computation の分離
- `skill-conflict-resolution.md` — 衝突時の優先度と negative routing
