---
source: "A good AGENTS.md is a model upgrade. A bad one is worse than no docs at all. (Slava Zhenylenko, Augment)"
date: 2026-04-23
status: analyzed
---

## Source

**タイトル**: "A good AGENTS.md is a model upgrade. A bad one is worse than no docs at all."
**著者**: Slava Zhenylenko (Augment, Member of Technical Staff)
**種別**: blog-post
**吸収日**: 2026-04-23
**URL**: unknown (text pasted)

## Source Summary

**主張**: AGENTS.md の quality delta は Haiku→Opus 品質ジャンプに相当。同一ファイルで routine bugfix +25%、complex feature -30% という非対称効果。「良い AGENTS.md はモデルアップグレード、悪い AGENTS.md はドキュメントなしより悪い」。

**測定手法**: AuggieBench による実証測定（~100-file modules での比較検証）。

**7つの working patterns**:
1. Progressive disclosure (100-150 lines + reference files) → 10-15% 全体改善
2. Procedural numbered workflows → 25% correctness, 20% completeness（6-step deploy: missing wiring 40%→10%）
3. Decision tables (2-3 way ambiguity) → 25% best_practices（React Query vs Zustand 例）
4. Real codebase snippets (3-10 lines) → reuse 改善、多すぎると wrong pattern matching
5. Domain rules when specific/enforceable → stacking 30-50 warnings で失敗
6. Pair every "don't" with "do" → warning-only が overexploration trap を誘発
7. Modular AGENTS.md (~100 files, 100-150 lines) → huge cross-cutting repo-root は逆効果

**Failure modes**:
- Overexploration trap（architecture overview + 30-50 warnings without dos）
- Surrounding doc sprawl（37 docs/500KB や 226 docs/2MB — AGENTS.md 削除しても行動変わらず）
- New patterns break old documentation（旧 doc が静かに腐る）

**Discovery rates（実測）**:
- AGENTS.md: 100% auto-loaded
- References from AGENTS.md: 90%+ on-demand
- Directory README.md: 80% (同ディレクトリ作業時)
- Nested README in other dirs: 40%
- Orphan docs in _docs/: <10%
- **~50% は grep/semantic search 経由（AGENTS.md references 経由ではない）**

**前提条件**:
- coding task + AGENTS auto-load 環境（Augment Agent 前提）
- 比較的シンプルな monorepo 構造
- 単一言語プロジェクトを主な対象

## Key Claims

1. AGENTS.md quality は "model upgrade vs model downgrade" 分岐点。品質は単調増加しない
2. **Search-result sprawl が本丸**: agent が grep/semantic search で拾う docs 全体を管理しないと AGENTS.md の改善は限定的
3. 100-150 行上限は「Progressive disclosure の入口」であり、それ以上は reference files に委譲
4. "don't" だけのルールは overexploration を招く → "don't + do" ペアが必須
5. Module-level AGENTS.md は ~100 files の粒度で効果、それ以上細分化は管理コスト増
6. 新パターン導入時に旧 docs を降格させないと、モデルは矛盾した信号を受け取る
7. Token-based upper bound (4KB sweet spot) が "Lost in the Middle" 問題に直結

## Gap Analysis

### 現状マッピング

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Progressive disclosure (100-150 lines) | **Already（強化可能）** | root AGENTS.md 149行, .codex/AGENTS.md 151行 — 上限ぎりぎり/超過 |
| 2 | Procedural numbered workflows | **Already（強化可能）** | 5-phase loop はあるが、タスク別 6-step のような具体テンプレが少ない |
| 3 | Decision tables (model-routing, cwd-routing, change-surface) | **Already（強化可能）** | 各 reference ファイルに分散、索引なし → 発見率が低い |
| 4 | Real codebase examples | **Partial** | rules/react.md は充実、Go/Python/Proto は一部のみ |
| 5 | Pair don't/do | **Partial** | 70% coverage。CLAUDE.md core_principles に "don't" 単独あり |
| 6 | Module-level AGENTS.md (scripts/docs/.github) | **N/A（棄却）** | Codex 指摘: 現 dotfiles には逆効果（sprawl 増大） |
| 7 | Search-result sprawl 監査 | **Gap** | docs/research 232 files, docs/plans 120 files, references 159 files — 検索面未監査 |
| 8 | Reference 10-15 上限ルール | **Already（強化可能）** | global CLAUDE.md = 5 links（範囲内）、だが上限ルール未明記 |
| 9 | Token-based size limit (4KB sweet spot) | **Gap（Gemini 新規）** | Lost in the Middle 問題。現状未計測、行数ベースのみ |
| 10 | Stale doc retirement | **Gap（Codex oversight）** | 新 pattern 導入時の旧 doc 降格プロセスなし |

### ギャップ重要度

- **Critical Gap**: Search-result sprawl 監査（#7）— agent の実際の情報取得経路の約 50% が grep/search 経由
- **High Gap**: Stale doc retirement（#10）— 新 absorb のたびに旧 docs が腐る問題が累積
- **Medium Gap**: Token-based limit（#9）— 行数より token ベースの方が実態に近い

## Refinement

### Codex 批評（主要指摘）

**Oversight（見落とし）**:
- 「新パターンが旧 docs を壊す」「README trim」「50% は grep/semantic search 経由」を記事は軽視。**search-result sprawl が本丸**
- 記事の "auto-load sprawl" 再定義が必要: 478 md / 4.6MB は AGENTS.md auto-load ではない（限定 link のみ auto）→「search-result sprawl」

**Overrated（過大評価）**:
- #7 sprawl の定義: 記事は auto-load 前提で語るが、dotfiles の docs 蓄積は主に search 経由の問題

**Underrated（過小評価）**:
- root AGENTS.md 149行 / .codex/AGENTS.md 151行: 記事推奨上限ぎりぎり/超過。Mandatory Skill Usage と Change Surface Matrix が重複気味 → 圧縮余地あり
- root CLAUDE.md の "No features/abstractions/Don't refactor": do が抽象的（萎縮リスクは低いが Pair don't/do 原則に照らすと改善余地）

**Premise mismatch（前提不一致）**:
- Augment は coding task + AGENTS auto-load 前提。dotfiles は harness engineering で skills/hooks/MCP が分担 → 「AGENTS.md を増やせ」は直輸入不可
- **優先順位**: module-level AGENTS 追加が FIRST ではない（逆効果）。先に docs/research, docs/plans, references の検索面を監査し、active/reference/archive 境界 + 検索除外・索引を決める → 次に root AGENTS.md を 120 行程度へ圧縮

### Gemini 周辺知識

**Token cost**:
- >4KB / ~4000 tokens で "Lost in the Middle" 現象。「100-150 行」より token ベース上限が実態に近い
- AGENTS.md + inline reference の合計 token を定期計測すべき

**Alternatives（already in dotfiles）**:
- MCP servers: prose を tool 実装に移す（既存の MCP 活用）
- JIT context injection (RAG): on-demand reference が 90%+ 発見率を担保
- **Skills/Slash Commands: "don't + do" より強い（skip 不能）** ← 既に dotfiles で実装済み（Codex が最も重要な点として指摘）

**3-tier hierarchy**:
- global / project / module で selective load → dotfiles の `<important if>` conditional tags と整合

**Living Instructions**:
- CLAUDE.md を static rulebook から learning memory layer へ → MEMORY.md で部分実装済みだが、AGENTS.md 側の老朽化対応が未整備

## Triage Decision

ユーザー選択: **全採択（P1 + P2 + P3 = 7 tasks）**

### P1 最優先（search-result sprawl 解消）

**Task 1: Search-result sprawl 監査**
- docs/research, docs/plans, references の全 md ファイルを active/reference/archive/trash に分類
- 検索除外設定（.gitignore 的な .searchignore または front-matter status フィールド）
- 目標: agent の grep/semantic search ヒット数を現在の推定 50% 削減
- **根拠**: 50% の情報取得が search 経由という実測値 + 矛盾 docs が silent failure を生む

**Task 2: root AGENTS.md / .codex/AGENTS.md 圧縮**
- 149行 → ~120行（10-20% 削減）
- Mandatory Skill Usage と Change Surface Matrix の重複除去
- 圧縮した内容は既存 references に委譲（新規 doc 作成不要）
- **根拠**: 150行上限を超えると progressive disclosure の効果が反転

### P2 中優先

**Task 3: Pair don't/do 強化**
- CLAUDE.md core_principles の "don't" 単独箇所に対応する "do" を追加
- 対象: "No features beyond what was asked", "Don't refactor things that aren't broken" 等
- 形式: 既存箇条書きに1行追記（大規模リライト不要）

**Task 4: Stale doc retirement playbook**
- `docs/playbooks/stale-doc-retirement.md` 作成（新 absorb 時の旧 doc 降格フロー）
- front-matter に `status: active/reference/archived` を標準化
- 新パターン導入時のチェックリスト: 「何の旧 doc がこれに矛盾するか？」

### P3 低優先

**Task 5: Token-based size limit**
- AGENTS.md + references の token 合計を計測するスクリプト追加
- 目安: 合計 4000 tokens (4KB) 以内を sweet spot として明文化
- `scripts/` 配下の token-counter.sh として実装

**Task 6: Workflow playbooks（タスク別 numbered workflow）**
- 現 5-phase loop を補完する具体タスクテンプレ追加
- 対象: "fix-issue", "new-feature", "hook-change" の 3 パターン（最小限）
- 既存 `docs/playbooks/` に追記形式

**Task 7: Decision-tables index**
- 既存 model-routing / cwd-routing / change-surface の索引を AGENTS.md に追加
- 形式: 2-3 行の参照テーブル（新規 doc 不要、AGENTS.md 内に inline）

### 棄却

- **scripts/docs/.github への module-level AGENTS.md 追加**: Codex 指摘で逆効果（sprawl 増大）。dotfiles は harness engineering 構造で "more AGENTS.md" は premise mismatch
- **単一ファイル AGENTS.md への記事手法の直輸入全般**: Augment の coding task 前提 ≠ dotfiles の harness engineering 前提

## Alignment with Existing Setup

| 採択タスク | 既存設計との整合性 |
|-----------|-------------------|
| Search-result sprawl 監査 | MEMORY.md 方針変更（2026-04-11）「常時コンテキスト用の knowledge のみ」の延長線上 |
| root AGENTS.md 圧縮 | ADR-0007「Thin CLAUDE.md + Thick rules」の AGENTS.md 版適用 |
| Pair don't/do 強化 | golden-check hook + CLAUDE.md ゴールデンプリンシプルと相補的 |
| Stale doc retirement | Build to Delete 原則（CLAUDE.md）の docs 版実装 |
| Token-based limit | IFScale（指示数重要）の token 版具体化 |
| Workflow playbooks | Karpathy LLM Coding Framework「Goal-Driven Execution」との整合 |
| Decision-tables index | cwd-routing-matrix（2026-04-23 新規追加）との連携 |

**Skills/Slash Commands の優位性（Gemini 指摘）**: "don't + do" よりも skip 不能なメカニズムとして既存の skills/hooks が上位互換。新規ルール追加前に「これは skill/hook で機械的に強制できるか？」を問う（`Static-checkable rules は mechanism に寄せる` 原則と完全整合）。

## Next Steps

実装プラン: `docs/plans/active/2026-04-23-agents-md-absorb-plan.md`（別途生成予定）

タスク優先順:
1. Search-result sprawl 監査（Task 1）— 最大 ROI、他のタスクの前提
2. AGENTS.md 圧縮（Task 2）— Task 1 完了後に実施（削除候補が判明してから）
3. Pair don't/do（Task 3）— 小さい変更、任意のタイミング
4. Stale doc retirement playbook（Task 4）— Task 1 の知見をドキュメント化
5. Token-based limit スクリプト（Task 5）— Task 2 完了後に計測
6. Workflow playbooks（Task 6）— 実際の摩擦が蓄積したタイミングで
7. Decision-tables index（Task 7）— Task 2 の圧縮作業に含めて実施

## Related

- **ADR-0007**: `docs/adr/0007-thin-claudemd-thick-rules.md` — Thin CLAUDE.md + Thick rules 設計原則
- **MEMORY.md 方針変更（2026-04-11）**: `.claude/projects/.../memory/MEMORY.md` — 「常時コンテキスト用の knowledge のみ」Pruning-First 運用
- **Karpathy LLM Coding Framework**: `docs/research/2026-04-20-karpathy-skills-absorb-analysis.md` / `references/` — Goal-Driven Execution、wrong assumptions パターン
- **Life Audit Protocol（Anti-vision）**: `docs/research/2026-04-17-life-audit-protocol-absorb.md` — Stop-doing リスト、不要な complexity の積極的棄却
- **Obsidian × Claude Code absorb**: `docs/research/2026-04-21-obsidian-claudecode-absorb-analysis.md` — cwd routing matrix、skill-writing-principles、禁止より推奨原則（本記事 Pair don't/do と整合）
- **Harness Pipeline absorb**: `docs/research/2026-04-21-harness-pipeline-absorb-analysis.md` — reproduce-first, search-result sprawl の文脈的先行研究
- **improve-policy**: `.config/claude/references/improve-policy.md` — Pruning-First 運用方針
