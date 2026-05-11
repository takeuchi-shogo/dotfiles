---
source: "I Tried 100+ Claude Code Skills. These 6 Are The Best"
author: "anonymous AI agency operator"
date: 2026-05-06
status: integrated
type: blog-post-vendor-bias
---

## Source Summary

**主張**: 400 時間の Claude Code 経験 (real estate / HVAC / coaches / marketing 業界向け automation 販売) から、業界横断で効果的な 6 + 1 個の skill/plugin を推薦。「フラッシーなデモ」ではなく退屈で単純で効果的なものこそ「businesses actually write checks for」。

**手法 (7 項目)**:
1. **Skill Creator** (`skill-creator@claude-plugins-official`): 自然言語で skill.md draft → test → package
2. **Superpowers** (公式 plugin): plan → test → review → repeat 強制
3. **GSD (Get Shit Done)** (`npx get-shit-done-cc --claude --global`): clean context + sub-agents、1 コマンド context handoff
4. **/ultrareview** (公式名、Claude Code built-in): cloud sandbox 並列 reviewer、bug 独立再現必須、Pro/Max 3 free → $5-20/run、**2026-05-05 で free 期間終了**
5. **Context Mode** (`mksglu/context-mode`): tool 出力 sandbox routing → 必要部分のみ context (56KB→299B)、session SQL DB + compact snapshot 再注入
6. **Claude Mem** (`thedotmack/claude-mem`): SQLite + vector search + Stop hook 連動 auto CLAUDE.md 生成
7. **Frontend Design** (bonus, `frontend-design@claude-plugins-official`)

**根拠**: 400 時間実戦、業界横断、Context Mode benchmark (56KB→299B, 315KB→5KB)、Claude Mem 10x token 節約 (3 層検索)

**前提条件**: AI workflow を中小企業に **販売する側** の視点 (個人 dotfiles 整備とは目的が異なる)。Claude Code 2.1.86+ for /ultrareview。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Skill Creator | Already (強化可能) | `.config/claude/skills/skill-creator/SKILL.md` 自製、Stage 6 eval 手動 2 ステップ |
| 2 | Superpowers | Already (強化不要) | `superpowers@claude-plugins-official` v5.0.7 完全インストール |
| 3 | GSD | Partial → 実質 N/A 寄り (Codex 修正) | `/dispatch` + `superpowers:dispatching-parallel-agents` で本質カバー、差分は 1 コマンド UX のみ |
| 4 | /ultrareview | Partial (公式実在 by Codex 確認) | `/review` 実装済み、`/ultrareview` 相当の独立再現は未実装。公式: https://code.claude.com/docs/en/ultrareview |
| 5 | Context Mode | Already → Partial 要実験 (Codex 修正) | `output-offload.py` + `pre/post-compact` hook + `context-constitution.md` あり、ただし routing/retrieval/reinjection の selector 未実装 |
| 6 | Claude Mem | Partial (棄却推奨も最終的に採用) | file-based MEMORY.md + `/memory-status`、vector search なし。`node-sqlite-vec` skill は既存 |
| 7 | Frontend Design | Already (強化不要) | `frontend-design@claude-code-plugins` v1.0.0 user scope + skill-suggest.py 自動提案 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `/skill-creator` skill (自製) | E2E パイプラインがワンコマンドで完結する点 | `task skill:e2e` で `run_eval.sh + aggregate.py` を 1 ステップ統合 | 強化可能 (採用) |
| S2 | superpowers v5.0.7 | なし | - | 強化不要 |
| S5 | output-offload + compact hook + context-constitution | tool 出力を SQL DB に格納し snapshot だけ再注入する routing 機構 | post-compact-verify.js に reinjection selector policy 関数追加 (SQLite 化はせず) | 強化可能 (採用) |
| S7 | frontend-design v1.0.0 + skill-suggest.py | なし | - | 強化不要 |

## Phase 2.5 Refine: Codex 批評の主要修正

1. **公式名**: `/ultra-review` → `/ultrareview` (Codex 確認、docs.claude.com で実在)
2. **GSD は過大評価気味**: 既存 `/dispatch` + parallel agents + checkpoint で本質カバー、差分は 1 コマンド UX
3. **Context Mode は Already → Partial 要実験**: SQL DB 自体ではなく「何を再注入するか selector」が本質
4. **最大の罠**: file-based MEMORY.md を semantic layer で置換 → source of truth と hint の境界を壊す
5. **/ultrareview 価格**: Pro/Max 3 free runs は **2026-05-05 まで → 2026-05-06 (今日) から有料 ($5-20/run)**
6. **優先度**: 最優先は `/ultrareview` 内製ではなく、既存 Codex Review Gate に「独立再現フェーズ」を足すこと

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| T1 | Codex Review Gate に独立再現フェーズ追加 | 採用 | Codex 推奨最優先、低コスト高効果 |
| T2 | Skill Creator E2E 化 | 採用 | Codex 次点優先 |
| T3 | Context Mode reinjection selector (Already 強化と統合) | 採用 | SQLite 化はせず policy だけ |
| T4 | GSD 相当 context handoff 強化 (最小版) | 採用 | Codex 警告: 過大評価気味 → 最小変更に留める |
| T5 | Claude Mem vector search | **採用 (with リスク annotation)** | Codex「最大の罠」警告。MEMORY.md は置換せず併設、semantic layer は hint-only。Spike 必須 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | Skill Creator E2E | 採用 (T2 と統合) | - |
| S5 | Context Mode reinjection selector | 採用 (T3 と統合) | - |

## Plan

### Task T1: Codex Review Gate に独立再現フェーズ追加
- **Files**: `.config/claude/agents/codex-reviewer.md`
- **Changes**: bug 報告前に「独立再現したか」を必須セクション化する prompt 追加。`/ultrareview` の核心価値 (independent verification, no false positives) を内製で取り込む
- **Size**: S
- **Why first**: Codex 推奨最優先、`/ultrareview` 有料化 (2026-05-06〜) の代替

### Task T2: Skill Creator eval E2E 化
- **Files**: `Taskfile.yml`, `.config/claude/skills/skill-creator/SKILL.md`
- **Changes**: `task skill:e2e <skill-name>` で `run_eval.sh + aggregate.py` を 1 サブコマンドで連結
- **Size**: S

### Task T3: Context Mode reinjection selector 追加
- **Files**: `.config/claude/scripts/runtime/post-compact-verify.js`
- **Changes**: 「active plans / open files / TodoList を最優先で再注入する」selector policy 関数を追加。SQLite 化はせず、まず policy だけ
- **Size**: S
- **Codex 指摘**: 「output-offload は退避だけ、本質は『何を再注入するかの selector』」

### Task T4: GSD 相当 context handoff 強化 (最小版)
- **Files**: `.config/claude/skills/checkpoint/SKILL.md` (既存)
- **Changes**: HANDOFF.md auto-generate を 1 friction 削る方向。新規 skill は作らない
- **Size**: S
- **Codex 警告**: 過大評価気味、最小変更に留める

### Task T5: Claude Mem vector search Spike (リスク高)
- **Files**: 新規 `.config/claude/scripts/runtime/memory-vector-index.ts`, Stop hook 設定
- **Changes**: `node-sqlite-vec` で MEMORY.md を embed、Stop hook で増分更新、SessionStart で関連 entry 注入
- **Size**: M-L
- **Risk Annotations**:
  - ⚠️ Codex「最大の罠 = source of truth と hint の境界を壊す」
  - ⚠️ Hermes Fleet 2026-04 分析で「semantic search は小実験のみ」と判定済み → spike で再評価必須
  - ⚠️ MEMORY.md は **置換せず併設**、semantic layer は **hint-only** で運用
  - ⚠️ Spike 段階で「既存 file-based 運用より明確に勝る」根拠が出なければ棄却
- **推奨**: 新セッションで `/spike` (worktree 隔離)

## Risks / Notes

- 著者バイアス: AI workflow を販売する agency operator 視点 → 「business owner に売れる」根拠は個人 dotfiles では判断材料にならない
- `/ultrareview` 公式機能で 2026-05-05 まで Pro/Max 3 free runs。**今日 (2026-05-06) から有料**
- Hermes Fleet 分析 (2026-04-17) と T5 (Claude Mem vector) は再評価関係。Spike 結果次第で別 plan 化

## Source URL

(記事 URL は提供されず、テキスト直接貼付)
