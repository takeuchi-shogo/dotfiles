---
source: "How to Set Up Claude Code Routines to Automate Any Workflow (Full Course) — @eng_khairallah1 (Khairallah)"
date: 2026-05-14
status: integrated
---

## Source Summary

**主張**: Claude Code Routines は cloud-based 永続エージェントで、/loop や /schedule (local) を置き換える新しい自動化レイヤーだ。CLI `/schedule <desc>` で routine を作成し、4 つの構成要素 (prompt / repo / connectors / trigger) を設定すれば、09:00 の日次 PR レビューから GitHub event 連動の Changelog 生成まであらゆるワークフローを自動化できる。

**手法**:
1. CLI `/schedule` → cloud routine 作成 (schedule trigger)
2. Web UI `claude.ai/code/routines` → API/GitHub trigger 設定
3. Bulletproof prompt 構造: role / task / process / output / error / constraints の 6 要素
4. 5 つの実用 Recipe: Daily PR Review / Weekly Dep Audit / Doc Drift / Changelog / Tech Debt Sweep
5. "Dreaming" feature: Routines が自律的に改善案を提案 (2026-05-06 発表主張)
6. 15 runs/day cap (research preview)
7. Default で `claude/` prefix branch のみ push 可

**根拠**: 定量根拠なし。出典なし。"almost nobody is talking about it" 希少性訴求 + "Bookmark & Save this :)" 煽り + Follow me CTA あり。

**前提条件**: Claude Code 有料プラン (research preview)。Claude.ai Routines は 2026-05 時点で research preview。

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| M1 | `/schedule` CLI での routine 作成 | Already | harness 組込 skill。description: "scheduled remote agents (routines)" として実在。Nav Toor absorb (2026-05-13) で Verified 済 |
| M2 | Web UI `claude.ai/code/routines` | Partial | CLI 経由は運用済みだが、Web UI から API/GitHub trigger を設定する操作手順を dotfiles に記録していない |
| M3 | Bulletproof prompt 6 要素 rubric | **Gap** | role/task/process/output/error/constraints の構造化 rubric は dotfiles に存在しない。記事の最大新規価値 |
| M4-R1 | Daily PR Review routine (09:00) | Already (強化可能) | `/daily-report` + `gh-fix-ci` skill で同等機能。Routine 化 recipe は未記録 |
| M4-R2 | Weekly Dep Audit routine (月曜) | Already (強化可能) | `dependency-auditor` skill 実在。weekly routine 化 recipe は未記録 |
| M4-R3 | Doc Drift Detection routine (金曜) | Partial | `check-health` に drift 検出 rubric はあるが、週次 routine 設定例なし |
| M4-R4 | Changelog from Release Tag (GitHub) | Partial | `conventional-changelog` skill 実在。GitHub event trigger の設定例なし |
| M4-R5 | Tech Debt Sweep routine (月初) | Already (強化可能) | `/audit` + `dependency-auditor` で対応可能。月次 routine 化 recipe は未記録 |
| M5 | "Dreaming" feature | **Inconclusive** | "Code with Claude on May 6, 2026" 発表主張。一次ソース未取得。Codex no output 2 連発 / Gemini rate limit で検証不可 |
| M6 | Routine スタック思考 (直列→並列) | **Gap** | 複数 routine を組み合わせる設計パターンが references に存在しない |
| M7 | 15 runs/day cap | Already (記録なし) | Nav Toor absorb で Verified 済。`managed-agents-scheduling.md` に制限記載なし |
| M8 | `claude/` prefix branch 制約 | Already | `managed-agents-scheduling.md` で branch 分離設計が既に言及済み |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `/schedule` skill + `managed-agents-scheduling.md` | Bulletproof prompt rubric が routine 設計時に参照できない | `references/routine-prompt-rubric.md` 新規作成 (6 要素 + Good/Bad 例 + Pre-flight Checklist) | **強化可能 → 採用** |
| S2 | `/timekeeper`, `/daily-report` skill | Routine 化の設定例 (R1: Daily PR Review) が管理ドキュメントにない | `managed-agents-scheduling.md` の Recipe Catalog に R1 追加 | **強化可能 → 採用** |
| S3 | `dependency-auditor` skill | Weekly routine 化の設定例 (R2: Dep Audit) がない | 同 Recipe Catalog に R2 追加 | **強化可能 → 採用** |
| S4 | `scheduling-decision-table.md` | Routine 設計フロー (rubric 参照 + 段階運用) が表にない | Step 6 追加: Recipe + Rubric + 段階運用パス、撤退条件追加 | **強化可能 → 採用** |

---

## Refine 経路 (Phase 2.5)

3 経路での交差検証を試みた:

- **Sonnet Explore (Pass 1+2)**: 既存 dotfiles 照合。M1 (harness 組込 /schedule) と M4-R1〜R5 の Already 判定を生成
- **Codex (codex:codex-rescue)**: 2 回起動、両方 no output (496s / 327s timeout)。外部一次ソース検証は失敗
- **Gemini (gemini-explore)**: API rate limit により外部 grounding 不可。限定的な回答のみ

**補完戦略**: Phase 2.5 が劣化したため、直前の Nav Toor absorb (2026-05-13) の事前検証データを一次補完源として使用。Claude.ai Routines / `/schedule` / Cowork の動作は Nav Toor 経由で Gemini grounding + `gh api` 独立検証によって Verified 済 (前提: Khairallah 記事は Nav Toor の subset/簡易版)。

**"Dreaming" feature の扱い**: "Code with Claude on May 6, 2026" で発表という主張だが、一次ソース (code.claude.com) への到達が Phase 2.5 失敗で未確認。Inconclusive として棚上げ。ユーザー手動 follow-up 待ち。

---

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | M3 Bulletproof prompt 6 要素 rubric | **採用 (T1)** | 記事の最大新規価値。Routine prompt 品質は直接 Routine 成功率に効く。`routine-prompt-rubric.md` 新規作成 |
| 2 | M2 Web UI 操作手順 | スキップ | Web UI は変更頻度高く、references に固定すると陳腐化リスク大。Pruning-First |
| 3 | M5 "Dreaming" feature | 棚上げ (C1) | Inconclusive。一次ソース確認後に統合判断 |
| 4 | M6 Routine スタック設計パターン | スキップ | 現在 Routines 本格運用前。YAGNI。運用経験が積まれたら `/improve` 対象 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | routine-prompt-rubric.md 新規作成 | **採用 (T1)** | Gap M3 と統合。6 要素 + Good/Bad 例 + Pre-flight Checklist |
| S2 | managed-agents-scheduling.md に R1 追加 | **採用 (T2)** | Daily PR Review の Routine 化手順が参照可能になる |
| S3 | 同 R2 追加 (Weekly Dep Audit) | **採用 (T2)** | dependency-auditor の週次自動化を設計として明文化 |
| S4 | scheduling-decision-table.md Step 6 追加 | **採用 (T3)** | Routine 設計の判断フローに rubric 参照と撤退条件を統合 |

### 棚上げ / スキップ

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A2 | `/schedule` skill ファイル直接統合 | スキップ | harness 組込で skill ファイル無し。references 経路で代替済 |
| C1 | "Dreaming" 一次ソース確認 | 棚上げ | ユーザー手動 follow-up 待ち |

---

## Plan

### Task 1 (B1): routine-prompt-rubric.md 新規作成
- **Files**: `.config/claude/references/routine-prompt-rubric.md` (新規, ~80 行)
- **Changes**: Bulletproof prompt 6 要素 (role/task/process/output/error/constraints) の定義・説明、Good 例 (Daily PR Review)、Bad 例 (素朴な指示)、Pre-flight Checklist 7 項
- **Size**: S

### Task 2 (A1+B2+B3): managed-agents-scheduling.md 更新
- **Files**: `.config/claude/references/managed-agents-scheduling.md` (更新)
- **Changes**: Routine Recipe Catalog セクション追加。R1 (Daily PR Review) / R2 (Weekly Dep Audit) / R3 (Doc Drift) / R4 (Changelog) / R5 (Tech Debt Sweep) の設定例。15 runs/day cap 記載。routine-prompt-rubric.md 参照追記。"Dreaming" Inconclusive 注記
- **Size**: S

### Task 3: scheduling-decision-table.md 更新
- **Files**: `.config/claude/references/scheduling-decision-table.md` (更新)
- **Changes**: Step 6 追加: "Routine を設計する場合は routine-prompt-rubric.md を参照。Recipe Catalog から近いテンプレートを選択。段階運用 (dry-run → 1 日 1 回 → 増やす) を徹底。撤退条件: runs/day cap 超過 / branch conflict / connector 認証切れ"
- **Size**: S

### Task 4: decision-tables-index.md 更新
- **Files**: `.config/claude/references/decision-tables-index.md` (更新, 1 行)
- **Changes**: Mechanism 系に "Routine prompt 6 要素 → routine-prompt-rubric.md" を追記
- **Size**: S

### Task 5 (本レポート): 分析レポート保存
- **Files**: `docs/research/2026-05-14-claude-code-routines-absorb-analysis.md` (本ファイル, 新規)
- **Changes**: 本分析結果の永続化
- **Size**: S

### Task 6: MEMORY.md ポインタ追記
- **Files**: `MEMORY.md` (1 行追記)
- **Changes**: `## 外部知見索引` セクションに本レポートへの 1 行ポインタ
- **Size**: S

---

## 教訓

1. **content farm pattern 7 件目だが Nav Toor 経由で主要主張は Verified 済み**: Khairallah 記事は Nav Toor (absorb 直前) の subset/簡易版。zodchixquant 教訓「集客記事でも技術主張は検証する」を継続。事前検証データの再利用が Phase 2.5 劣化を補完した。

2. **新規価値の見極め = Pruning-First の実践**: Routines/Cowork 既知・既存スキル既知・Connectors も既知。残るは Bulletproof prompt rubric のみ。新規 1 ファイル + 既存 3 更新に絞ることで YAGNI を守りながら価値を抽出できた。

3. **Codex no output 2 連発は rescue subagent の信頼性課題**: Gemini rate limit と重なって Phase 2.5 が機能しなかった。代替として直前の absorb 記事の検証データを Phase 2.5 補完源として使う pattern を確立した (Nav Toor 結果を直接参照)。この「既存 absorb クロス参照」は今後の再現性ある手順として codify する価値がある。

4. **harness 組込 skill のスキャン限界**: `/schedule` や `/loop` は harness 組込で skill ファイルが存在しない。Sonnet Explore の Pass 1 が "not_found" を返すのは正常動作。`/skill description` 自体が一次ソース。この特性を知らずに Gap 誤判定を発生させるリスクが absorb フローに残っている。

5. **dotfiles の managed-agents-scheduling.md は既に Routines pilot 設計済み**: yamadashy (2026-04-29) + Boris (2026-04-30) absorb で設計が先行していた。大半が Already になったのはそのため。absorb 前の references 確認 (Step 0 相当) を徹底することで不要な Gap 登録を減らせる。
