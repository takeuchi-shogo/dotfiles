---
title: "@damidefi Delete 90% of Your Obsidian Notes — absorb analysis (light-phase2)"
date: 2026-05-31
status: light-phase2-only
adopt_count: 0
validation_only_count: 1
family: obsidian-second-brain
family_entry: 17
author: "@damidefi (X creator)"
prior_absorb_count: 16 (obsidian-second-brain family) / 2 (damidefi author within family)
verdict: Reference-only (記事 tactic 採用 0) + validation-only 1 (MEMORY.md bloat 実施)
related:
  - 2026-05-30-cyrilxbt-notes-into-output-absorb-analysis.md (family 16, adopt 2)
  - 2026-05-25-cyrilxbt-organize-vault-absorb-analysis.md (family 15, adopt 2)
  - 2026-05-23-damidefi-claude-obsidian-second-brain-absorb-analysis.md (family 10, damidefi 1 件目, adopt 0)
---

# @damidefi 「Delete 90% of Your Obsidian Notes. The Vault Gets Smarter When You Do.」

## Source Summary

- 著者: @damidefi — obsidian-second-brain family **2 件目** (前回 2026-05-23 family 10、adopt 0)、X follower 100K 目標・Bookmark/Share 誘導あり
- 主張: vault は volume ではなく **signal density**。AI が reasoning するコンテキストとして noise が多いと signal が薄まる → 1,890/2,100 件 (90%) 削除したら daily brief の connection が鋭くなった (anecdotal)
- 手法: ①thinking ⊃ information の選別テスト ②30 秒再取得ルール ③KEEP/DELETE/REVIEW audit prompt (lean DELETE) ④archive-before-delete (2 週間) ⑤1 行データ point 保持 exception ⑥**「CLAUDE.md は bloat すると性能低下する。vault も同じ attention budget 問題」という明示的類推**
- 根拠: anecdotal only。empirical data なし

## Phase 1.5: Saturation Gate

- Family: `obsidian-second-brain` (キーワード hit: `obsidian` / `vault` / `second brain` / `notes` 全該当)
- N = 17 件目 (organize-vault が family_entry:15、cyril-notes が 16)。**damidefi は同一著者で 2026-05-23 に absorb 済み (adopt 0、reference-only)**
- delta 計算: 「90%削除 / signal-density pruning」角度は obsidian family 直近 3 件 (構築・整理・retrieval 中心) に未出 → 表面 delta≈2
- **致命的な前提不一致**: 記事は「AI が vault を daily brief で reasoning input として読む」前提。dotfiles の Vault は `memory→Vault 単方向同期スナップショット` (CLAUDE.md `<important if>`)。前回 damidefi absorb で「proactive vault 参照 = 0 件」確定済み → vault-specific tactic は Phase 2 で N/A 濃厚
- 判定: **SATURATED-but-novel (delta>=2) → light-phase2** (ユーザー選択)

## Phase 2 (light): signal-density 原則を dotfiles 自身への翻訳で検証

vault tactic ではなく「dotfiles が記事の主張を自分に適用する仕組みを既に持っているか」を Sonnet Explore + Opus で検証。

| # | 記事の手法 (signal-density 角度) | dotfiles の対応物 | 判定 |
|---|---|---|---|
| 1 | "thinking ⊃ information" 選別 | `compact-instructions.md` Derivability Test + `improve-policy.md` Tier 1-3 | **Already (instruction)** |
| 2 | 30 秒再取得ルール | Derivability Test「再導出可能なら保存しない」と意味的同等 | **Already** |
| 3 | MEMORY.md 索引 pruning | `memory-archive.py` (180行/23KB 閾値で archive 退避) **存在** | **Partial — mechanism あるが hooks 未登録で不発** |
| 4 | audit prompt (KEEP/DELETE/REVIEW) | `dead-weight-scan.py` あるが `/improve` retire で disconnected | **Partial (断線)** |
| 5 | archive-before-delete (2 週間) | `memory-archive.py` が `archive/YYYY-MM.md` に退避 | **Already (設計思想)** |
| 6 | docs/research pruning | `doc-status-audit.py` (90日+未参照→archive) あるが hooks 未登録、312 ファイル flat | **Partial (断線)** |
| 7 | CLAUDE.md bloat 類推 | `claudemd-size-check.py` (PostToolUse 稼働中), IFScale, `feedback_claudemd_length.md` | **Already (enforce 済)** |

**記事 vault tactic の採用 = 0 件** (全 Already/Partial + 前提不一致)。純粋な Gap なし → Phase 2.5 (Codex+Gemini) は light flag + Gap=0 で省略。

## Validation-only Follow-up (今回の真の収穫)

記事の signal-density lens が dotfiles 自身の bloat と mechanism drift を露出させた。

### 1. MEMORY.md bloat 実態 (記事の主張がそのまま当てはまる)

| 計測 | absorb 前 | 閾値 | 状態 |
|---|---|---|---|
| MEMORY.md 行数 | 223 行 | 180 (`memory-archive.py`) / 200 (`improve-policy`) | 超過、warning 発火中 |
| MEMORY.md サイズ | 48K | 23KB | 2 倍超過 |
| memory ファイル数 | 67 件 | 60 (`memory-eviction.py`) | 超過 |
| 外部知見索引エントリ | 108 件 | — | bloat 主因 |

### 2. `memory-archive.py` のロジック不整合 (実行前シミュレーションで検出)

`memory-archive.py` は `keep_sections = max(3, len(sections)//2)` で **ファイル後半半分を残し前半を archive** する (「ファイル順=古さ」前提)。
しかし実際の MEMORY.md は **前半=コア恒久知識 / 後半=肥大化する外部知見索引** という構造。24 セクションで実行すると:
- archive 対象 = 行3〜72 (コア知識: エージェント設定/ハーネス/AutoEvolve/Brevity 等 12 セクション)
- MEMORY.md に残置 = 外部知見索引 (行84〜163、約80行 = bloat 主因) + TELOS 以降
- → **signal を捨てて noise を残す逆効果**。CLAUDE.md core principle「壊れたら即STOP」に従い盲目実行を中止

### 3. 実施した手動 pruning (記事の archive-before-delete を忠実適用)

- バックアップ: `MEMORY.md.bak-2026-05-31` 作成 (~/.claude/projects/ は git 管理外のため)
- archive 退避: 外部知見索引 70+ エントリを `memory/archive/2026-05.md` に全文退避 (削除せず保持)
- MEMORY.md 圧縮: 外部知見索引 (行84-162, 79行) を family レベル横断教訓 12 行に圧縮。個別 absorb 要約は本体 `docs/research/*-absorb-analysis.md` (source of truth) と `_index.md` に委譲
- 結果: **MEMORY.md 223行/48K → 154行/16K** (閾値 180/23KB を下回る)

### 4. 別タスク候補 (今回 scope 外、記録のみ)

- pruning mechanism 群 (`memory-archive.py` / `memory-eviction.py` / `dead-weight-scan.py` / `doc-status-audit.py`) が全て disconnected (hooks 未登録 or `/improve` retire)。再接続は M 規模 harness 変更で別セッション /rpi 推奨
- `memory-archive.py` のロジックを「外部知見索引セクションの古いエントリ優先 archive」に修正 (M 規模、Codex Review Gate 必須)
- `_index.md` が最近の absorb (2026-05-24 以降) を取りこぼし、MEMORY.md と二重管理 drift。本体 analysis.md が source of truth なので情報損失はないが索引の完全性は別途要整理

## 最終判定

| 軸 | 判定 |
|----|------|
| 記事 tactic 採用件数 | **0 件** (全 Already/Partial + 前提不一致) |
| Family entry | 17 件目 |
| Classification | reference-only + validation-only 1 |
| validation 実施 | MEMORY.md 223→154行 pruning (archive-before-delete 適用) |
| Phase 2.5 | 省略 (light flag, Gap=0) |

## Meta-finding

記事の核心メカニズム (signal density / attention budget / pruning-first) は dotfiles が IFScale / `feedback_claudemd_length.md` / Pruning-First で**既に internalize 済み**。にも関わらず MEMORY.md が閾値超過していたのは「**原則は codify したが enforcement mechanism を connect していない**」典型。記事の最大価値は新規 tactic ではなく「自分が既に知っている原則を自分に適用できていない drift」の可視化だった。前回 damidefi (family 10) で確立した validation-only follow-up パターンの 2 例目。
