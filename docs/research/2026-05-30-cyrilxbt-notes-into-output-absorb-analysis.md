---
title: "@cyrilXBT Turn Every Note Into Something You Actually Use — absorb analysis (light-phase2)"
date: 2026-05-30
status: implemented
implemented_verified: 2026-07-05 (capture.md テンプレート + obsidian-knowledge SKILL.md の Decision Feeder 実在を grep 確認)
adopt_count: 2
family: obsidian-second-brain
family_entry: 16
author: "@cyrilXBT"
prior_absorb_count: 15 (obsidian-second-brain family) / 6 (cyrilXBT author within family)
verdict: Adopt (S 規模 2 件 — capture template 新設 + obsidian-knowledge Decision Feeder 機能追加)
related:
  - 2026-05-25-cyrilxbt-organize-vault-absorb-analysis.md (family 15、adopt=2)
  - 2026-05-22-cyril-one-folder-absorb-analysis.md (family 11、adopt=1)
  - 2026-05-19-cyril-obsidian-dashboard-absorb-analysis.md (family 12、adopt=2)
  - 2026-05-23-damidefi-claude-obsidian-second-brain-absorb-analysis.md (family 10、adopt=0)
---

# @cyrilXBT 「How to Build an Obsidian System That Turns Every Note You Take Into Something You Actually Use」

## Source Summary

- 著者: @cyrilXBT — obsidian-second-brain family で **6 件目**、`@cyrilXBT` follow 誘導で締める常連 listicle author
- 主張: capturing と using は別活動。ほとんどの note-taking は capture を最適化して using を無視している。本記事は「どう使うか」から逆算して vault を組む
- 形式: The Four Uses / Three Zones / Output フォルダ / CLAUDE.md テンプレート / Five Workflows (各 Claude プロンプト付き) / Three Capture Conventions / Weekly Note Audit / 90日 compound / contribution rate metric
- 根拠: anecdotal only。データ・出典なし

## Phase 1.5: Saturation Gate

- Family: `obsidian-second-brain` (キーワード hit: `obsidian`, `vault`, `PARA`, `second brain`)
- 過去事例 N=15 (ファイル名列挙で確認、`_index.md` grep は format 差で 3 件しか拾わずフォールバック適用)
- 採用率: 直近 obsidian-family は organize-vault(2) / one-folder(1) / dashboard(2) / cyril-vault(3) / damidefi(0) と adopt>0 多数 → **>= 20% (PASS-warning 圏)**。純粋 rehash ではない
- 手法 delta 計算:
  - 既知 6 手法 (Already/Reject 済): Three Zones=IPARAG 再パッケージ / Output フォルダ / CLAUDE.md テンプレート=One-Folder の 5コマンド系 / Weekly Note Audit=vault-maintenance.sh stale / Daily Processing=/timekeeper+morning / Connection Surface=obsidian-knowledge リンク発見 / Output Generator=/digest+obsidian-content
  - novel 2 手法: **Active Decision Feeder** / **Three Capture Conventions**
  - ambiguous 1 手法: The Four Uses / contribution rate metric (評価哲学、harness 化困難)
  - **delta = 2**
- 判定: **PASS-warning + delta=2 → light-phase2** (ユーザー選択)

## Phase 2 (light): Pass 1 + Pass 2 統合判定

novel 2 手法のみ検証。両手法とも記事に具体プロンプト/フォーマットが明記され、Sonnet imagination ではなく原文ベースと確認。

| # | 手法 | Pass 1 (Explore) | Pass 2 確定 | 根拠 |
|---|------|-----------------|------------|------|
| 1 | Active Decision Feeder | not_found | **Gap (条件付き)** | `/decision` は記録のみ・事前 vault scan なし。`/think decision` は thinking-context.md 仮説欄のみ参照。obsidian-knowledge はキーワード検索のみで decision-driven synthesis なし。空白実在。ただし新 skill 化は Pruning-First 違反 → obsidian-knowledge への機能追加が最小インパクト |
| 2 | Three Capture Conventions | not_found | **Gap** | `/note` は append のみ・template なし。`00-Inbox` は `.gitkeep` のみ。permanent-note の「関連ノート」/digest の「自分の考え」で partial だが CONNECTS TO/QUESTION/APPLICATION の構造化フィールドは未実装 |
| — | The Four Uses / contribution rate | — | **N/A** | アクセス追跡が必要で harness 化困難。YAGNI。ただし The Four Uses の4分類 (decision/writing/conversation/action) は capture template の `MIGHT USE FOR` hint として軽量に反映 |

## Phase 2.5 Refine

- **Codex 批評**: 省略 (light-phase2、両 Gap とも S 規模で実装場所明確・不確実性低)
- **Gemini grounding**: 省略 (family saturated)

## adopted / rejected decisions

### Adopted (2 件 / S 規模)

| # | 採用 | 対象ファイル | 変更内容 |
|---|------|-------------|----------|
| A1 | Three Capture Conventions | `templates/obsidian-vault/00-Inbox/_templates/capture.md` (新設) | CONNECTS TO / MIGHT USE FOR / RAISES THE QUESTION / COULD APPLY TO / ACTION IF TRUE を **optional** な Capture Context セクションとして提示。全欄強制せず「該当する欄だけ 30 秒で」。`/note` の即時性は変えず template のみ用意。The Four Uses を MIGHT USE FOR の選択肢に埋め込み |
| A2 | Active Decision Feeder | `.config/claude/skills/obsidian-knowledge/SKILL.md` | 機能8「意思決定フィード」追加。決定内容 → vault scan (Explore) → Supports/Challenges/Adds nuance 分類 → decision brief。**vault 外情報を加えない**制約 (記事核心) を明記。記録は /decision、構造化は /think decision に委譲し収集に特化。description trigger + negative routing も更新 |

### Rejected (6 件)

| # | 手法 | 理由 |
|---|------|------|
| R1 | Three Zones (Capture/Active/Archive) | IPARAG 9-folder 既採用、Design Rationale 文書化済 (2026-05-22 A2) |
| R2 | Output フォルダを vault に含める | dotfiles では成果物は docs/ + git 管理。vault に finished work を置く需要薄 |
| R3 | CLAUDE.md テンプレート (What I Use Notes For 等) | `templates/obsidian-vault/CLAUDE.md` に Identity/Architecture/Conventions 既存。One-Folder の 5コマンド系で Reject 済 |
| R4 | Weekly Note Audit (14日→REVIEW→archive) | `vault-maintenance.sh` の stale 検出 + `#status/seed` 30日で代替済 |
| R5 | Five Workflows のうち Daily Processing / Connection Surface / Output Generator | /timekeeper + auto-morning-briefing / obsidian-knowledge リンク発見 / /digest+obsidian-content で代替済 |
| R6 | contribution rate metric | アクセス追跡 harness が必要で実装コスト過大。YAGNI |

## Meta-findings

1. **Cyril 6 件目で「small but real adopt」継続**: 過去 adopt は Vault(3)→Dashboard(2)→One-Folder(1)→18-Steps(0/別family)→organize-vault(2)→本記事(2)。vault-maintenance.sh 拡張系から **skill 機能追加 + template 新設** に質的に少し移行。ただし依然サブシステム改善の rein は維持
2. **delta=2 が2件とも真の Gap**: organize-vault (delta=1) に続き、saturation 16 件目でも novel が実在した。Five Workflows の表面的「5つのプロンプト」を rehash と切らず、1つ1つ既存 skill と照合した結果 Decision Feeder / Capture Conventions の2つだけ空白として確定。Pass 1 Explore の not_found 報告を Pass 2 で記事原文照合し imagination 罠を回避
3. **新 skill を作らず既存 skill 拡張に倒した**: Active Decision Feeder は単独 skill 化も可能だったが、obsidian-knowledge (検索/リンク/合成の既存 skill) の機能8として追加。/decision・/think decision との責務境界を description に明記し routing 衝突を予防

## Phase 5 Handoff

- **規模**: S (2 file: 1 新設 + 1 機能追加 ~40 行)
- **検証**: `task validate-configs` (skill 定義変更の最低検証)
- **log.md 追記**: `ingest (light Phase 2)`、本体に「採用 2 件」明記
- **MEMORY.md 索引**: obsidian-second-brain family entry に 1 行追記 (family_entry: 16)
- **Wiki/Obsidian 連携**: light-phase2 のため省略 (family saturated)
