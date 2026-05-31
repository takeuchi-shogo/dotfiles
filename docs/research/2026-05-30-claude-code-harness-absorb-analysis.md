---
source: "How Claude Code Harness turns agent coding into a contract-first delivery loop (AlphaSignal, Chachamaru127/claude-code-harness)"
url: https://github.com/Chachamaru127/claude-code-harness
date: 2026-05-30
status: analyzed
family: harness-engineering
saturation: PASS (warning) — N>=5, focused absorb (Gap-driven escalation to Phase 2.5)
adopted: 4 (#3, #4, #5, #6) / dropped: 1 (#2 codegen) / N-A: 1 (#7)
---

## Source Summary

**主張**: claude-code-harness は MIT ライセンスの Claude Code プラグインで、エージェントのコーディングを
5 動詞ループ (setup/plan/work/review/release) でラップし、`spec.md` (製品契約) と `Plans.md` (タスク台帳)
の 2 ファイルを single source of truth とする。狙いは「チャット出力」から「デリバリ証拠」への移行。
README が flag しない 4 つの rough edge (version drift / TDD 未強制 / 狭い benchmark / doc drift) も AlphaSignal が指摘。

**手法** (本 absorb の比較対象):
- Go-native hook runtime (cold start 1-2ms vs bash+TS 40-60ms、modernc.org/sqlite pure-Go)
- `harness.toml` 単一ソース → `harness sync` で plugin.json/hooks.json/settings.json を再生成 (config codegen)
- R01-R13 ガードレールレジストリ (deny/ask/warn の 3 ティア、tool surface ごとに紐づけ)
- hook の fail-open on infrastructure errors (deterministic deny は block、plumbing 破損時は approve 優先)
- `doctor --migration-report` (stale cache/重複 skill/古い symlink を**削除せず inventory**)
- `deleted-concepts.yaml` (migration 後の概念 residue を追跡)
- host adapter capability matrix (証明できない parity を主張しない設計)
- spec.md + Plans.md の 2 ファイル SSoT / work verb の silent scope expansion 拒否
- "data the agent has not directly seen stays unknown" を spec に明記

**根拠**: ~1700 stars / 190 forks / v4.12.7 / 2025-12 created daily ship。Breezing benchmark は
14/15 (with validation) vs 3/15 (without)、ただし 3 tasks・1 model (GLM-4.5-air) と AlphaSignal 自身が限界を flag。

**前提条件**: OSS プラグイン (multi-host: Claude Code / Codex / OpenCode)、"vibecoders" (solo full-cycle contract dev) 向け。
配布・再現性・複数ホスト parity が設計ドライバ。→ 当方は **単一ユーザーの個人 config repo** であり前提が部分的にズレる。

## Saturation Gate (Phase 1.5)

- Family: `harness-engineering` (`harness` + `hook` + `agent platform` で 3+ hit)
- N >= 5 (Harnesses Are Everything / AlphaSignal Harness / Harness Pipeline BAN / Self-Healing / Cursor harness / Tan thin-harness)
- 全体採用率 >= 20% → **PASS (warning)**。ただし競合ツールの具体設計で手法 delta >> 2 → focused absorb で進行 (ユーザー選択)
- 「Already だから省略」はしない (ユーザー指摘 + skill anti-pattern「Already と判定して深掘りを止める」)。全 10 項目を Pass 2 強化分析の対象とした

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | Pass 1 判定 | 現状 (file:概要) |
|---|------|------|------|
| 1 | hook 性能計測/最適化 | exists | `scripts/runtime/sessionstart-audit.py` latency<3s target、Python 実装 |
| 2 | config codegen (単一ソース→sync) | partial | CLAUDE.md は build-claude で template 生成、settings.json/hooks.json は手書き |
| 3 | 番号付き deny/ask/warn レジストリ | partial | settings.json deny 102/ask 0/allow 71、`graded-guardrails.md` は scoring 設計で別物、injection-rule R1-R10 は攻撃分類 |
| 4 | hook fail-open/closed 方針 | exists | `scripts/lib/hook_utils.py` `run_hook(fail_closed=...)` per-hook 分岐 |
| 5 | doctor / migration-report | exists | `Taskfile.yml` doctor:binary/symlink/nix/hook/brew、stale inventory モードなし |
| 6 | deleted-concepts ドリフト追跡 | partial | `doc-gardener` agent + `scripts/lifecycle/doc-garden-check.py` は freshness のみ、退役概念 registry なし |
| 7 | release evidence packaging | partial | conventional-changelog ref / upgrade-claude あり、versioned plugin は ship せず |
| 8 | capability matrix / refuse parity | exists | `subagent-delegation-guide.md` 「parity 仮定せず」明記、形式 matrix はなし |
| 9 | spec + Plans 2 ファイル SSoT | exists | `PLANS.md` + `docs/specs/*.prompt.md`、product-reviewer が整合性検証 |
| 10 | scope creep 防止 | exists | CLAUDE.md「承認スライス」+ impeccable stop-and-ask |

## Pass 2 強化分析 + Phase 2.5 (Codex + Gemini) 修正

Phase 2 の判定を Codex (read-only 批評、2 回目で実批評取得) + Gemini (Google Search grounding) で補正。

| # | 項目 | Pass 2 | **Phase 2.5 修正後** | 根拠 |
|---|------|--------|------|------|
| 1 | hook 性能 (Go化) | Already(強化不要) | **N/A 確定** | Gemini: Python 50-100ms (編集容易) vs Go ~1ms (配布/コンパイルコスト)。個人 repo は編集容易性が勝つ。Go 化は KISS/YAGNI 違反 |
| 2 | config codegen | Gap | **Partial (採用見送り)** | Codex+Gemini 一致: projen/KCL の系譜で team-scale 価値、単一ユーザーには over-engineering + 生成物 black-box 化 + ネイティブ編集との deadlock リスク。「生成」より「監査可能性」が本体 |
| 3 | deny/ask/warn カタログ | Gap | **Gap (軽量化採用)** | Codex: 重いレジストリではなく id/tier/rationale の別ファイル切り出し |
| 4 | fail-open/closed | Already(強化可能 minor) | **Already(強化可能, 昇格採用)** | Codex 過小評価を指摘: 個人 repo でも「どの hook が fail-open か」一覧化すべき、事故りやすい |
| 5 | doctor:stale | Partial→Gap | **Gap (inventory-only 採用)** | Codex: 削除機能不要、棚卸しのみなら軽い。orphaned codex job state (app-*/dotfiles-* 実在) が対象 |
| 6 | deleted-concepts | Gap | **Gap (P1/最優先採用)** | Codex: 最安価×高ROI。Gemini: Negative Constraints パターン (≒eslint-plugin-deprecation)、hallucinated regression 防止 |
| 7 | release evidence | N/A | **N/A 確定** | 両者一致: versioned plugin を ship しない個人 repo には不適合 |
| 8 | capability matrix | Already(強化可能 minor) | **Already(強化不要)** | rules/{codex,gemini}-delegation で部分カバー済、形式 matrix は over-engineering |
| 9 | spec + PLANS SSoT | Already(強化不要) | Already(強化不要) | 変更なし |
| 10 | scope creep 防止 | Already(強化不要) | **Already (採用条件は #2 で注記)** | Codex: codegen 導入自体が scope creep になり得る、採用条件明文化 (本 absorb で #2 drop により充足) |

**統合の結論**: 実 Gap は「codegen ではなく auditability (既存状態を legible にする)」に収束。
#3 (deny カタログ) / #4 (fail-open 一覧) / #5 (stale inventory) / #6 (retired-concepts) は全て安価で単一ユーザーに適合。
#2 (codegen) だけが team-scale の異物 → drop。

## Integration Decisions

| # | 項目 | 判定 | 規模 | 優先度 |
|---|------|------|------|--------|
| 6 | deleted-concepts (retired-concepts registry + check) | **採用** | S | P1 |
| 5 | doctor:stale (inventory-only) | **採用** | S-M | P2 |
| 4 | fail-open/closed 一覧 + 選択原則 codify | **採用** | S | P3 |
| 3 | deny rules カタログ (id/tier/rationale) | **採用** | M | P4 |
| 2 | config codegen | スキップ (over-engineering) | — | — |
| 7 | release evidence | N/A (個人 repo) | — | — |

## Plan

### Task 1 (#6, P1/S): retired-concepts registry + doc-garden-check 連携
- **Files**: `.config/claude/references/retired-concepts.md` (新規、軽量 yaml/md), `scripts/lifecycle/doc-garden-check.py` (Edit)
- **Changes**: 退役した概念 (skill/command/agent/hook 等) を `id / retired-date / replacement / rationale` で列挙。doc-garden-check が新規/変更ファイル中の退役語彙参照を検出して flag (Negative Constraints パターン)。削除済み実体への先祖返り参照を防ぐ。
- **注意**: `/improve` は「command 廃止 (2026-05-03) vs improve skill 存在」の曖昧性あり → registry が disambiguate する最初の対象。断定せず status 列で曖昧性を記録。

### Task 2 (#5, P2/S-M): doctor:stale inventory モード
- **Files**: `Taskfile.yml` (doctor:stale 追加), 必要なら `scripts/lifecycle/doctor-stale.sh` (新規)
- **Changes**: orphaned codex job state (`~/.claude/plugins/data/codex-openai-codex/state/*`)、stale cache、古い backup path を**削除せず inventory 報告**。MEMORY 既記載「retention 機構なし」に対応。--report のみ、削除は別途手動。

### Task 3 (#4, P3/S): fail-open/closed 一覧 + 選択原則
- **Files**: `.config/claude/references/hook-failure-policy.md` (新規 or 既存 reference に追記)
- **Changes**: `hook_utils.run_hook(fail_closed=...)` の各 hook の値をカタログ化 (どの hook が fail-open/closed か)。「security/policy=fail_closed、advisory=fail_open」の選択原則を code から reference に codify。

### Task 4 (#3, P4/M): deny rules カタログ
- **Files**: `.config/claude/references/deny-rules-catalog.md` (新規)
- **Changes**: settings.json の 102 deny rules を `id / tier (deny/ask/warn) / pattern / rationale` で別ファイルにカタログ化。settings.json 自体は触らず (single source は settings.json のまま)、auditability 用の読み物。重いレジストリ化はしない。

## Phase 2.5 Tooling Notes (failure log)

- **Codex**: 1 回目は AGENTS.md に反応してプリアンブルのみ (399 bytes、実批評なし) = MEMORY 記載の既知失敗。2 回目「TASK: ... プロジェクトドキュメント読込不要、テーブルだけ批評」と明示フレーミングで実批評取得成功。→ **教訓: codex exec read-only への absorb 批評は「プロジェクト doc 読込不要」を prompt 冒頭で明示する**と swallow を回避できる。
- **Gemini**: 1 回目 quota 枯渇 retry 連発したが、最終的に 4095 bytes の有効 grounding を取得 (projen/KCL/eslint-plugin-deprecation の出典付き)。MEMORY 記載の quota flakiness は今回は最終回収成功。

## Validation-only Follow-up

なし (本 absorb は platform drift ではなく純粋な設計比較。ただし #6 の作業中に `/improve` command/skill の状態曖昧性が露出 → Task 1 の registry が解消対象)。
