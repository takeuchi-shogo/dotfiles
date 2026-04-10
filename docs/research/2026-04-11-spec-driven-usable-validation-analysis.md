---
source: "仕様通り動くの先へ。Claude Codeで「使える」を検証する — Gota (@gota_bara / @gotalab555)"
url: https://speakerdeck.com/gotalab555/shi-yang-tong-ridong-kunoxian-he-claude-codede-shi-eru-wojian-zheng-suru
date: 2026-04-11
status: integrated
---

## Source Summary

**主張**: 「動く」と「使える」は異なる。仕様通りの動作とユーザーの実使用可能性にはギャップが存在し、自律実行ハーネスと自動 UX 評価によってこのギャップを埋める必要がある。

**手法**:
1. **4段階パイプライン** — Planner (WHAT定義) → Builder (実装) → Evaluator (機能検証) → UX Reviewer (体験検証)。各軸「7/10以上」基準で反復
2. **Credo 5原則** — Core First, Polish Later / Wire Before You Decorate / No Dead Code / The Spec Is Law / Built to Grow
3. **uxaudit プラグイン** — スクショベース UX 評価。34項目共通ルール + ジャーニー評価 + iteration 差分ダッシュボード
4. **「動く vs 使える」フレーム** — CI 検出可能な領域の先「触らないと分からない層」を対象化
5. **Anthropic 事例** — 出荷物の7割以上 PRD なし、2週間以内は PM 非配置（Amol Avasare, Head of Growth 談）

**根拠**: cc-sdd (3000+⭐) / skillport の実装実績。音声入力からプロトタイプまで 1-3 時間の事例（Local Notion clone, symphony clone 等）。

**前提条件**: モデル進化で仕様が高速変化する環境。人手を最小化しつつ品質・速度・量を保つ必要がある個人または小規模チーム。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| M1 | 4段階パイプライン（UX Reviewer 含む） | Already (強化不要) | `/epd` (Spec→Spike→Validate→Implement→Review) + autoharness-patterns.md で Planner/Builder/Evaluator 3役割取り込み済み。UX Reviewer の独立ステージ化は過剰な形式化 |
| M2 | Credo 5原則 | Mostly N/A | 4/5 は golden-principles.md (GP-001〜011) と `<core_principles>` と重複。"Wire Before You Decorate" のみ新軸 |
| M3 | uxaudit（スクショ自動評価） | Partial | ui-observer + webapp-testing + ux-rules.md (205+ルール) でインフラは揃う。真の Gap は「iteration 間の定量差分比較 + `/validate` ゲート統合」 |
| M4 | 「動く vs 使える」フレーム | Already | product-reviewer + /validate + UI Quality 3-Layers（既存統合済み）でカバー |
| M5 | 2週間プロトタイプ文化 | N/A | 個人 dotfiles に組織文化を持ち込むと過設計 |
| NEW | 評価→Spec/Prompt 機械的フィードバック閉ループ | Partial | Skill Eval Loop / Friction Detection Loop と部分重複するが、UX スコア→validate gate→次 iteration への注入パスは未実装 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | ui-observer + ux-rules.md | iteration 間の定量差分比較が手動。baseline との乖離を自動検出できない | ui-observer に snapshot baseline 比較 + JSONL スコア履歴記録を追加 | 強化可能 |
| S2 | `/validate` スキル | UX 品質の閾値ゲートが未実装。機能検証のみで体験検証が抜ける | acceptance criteria 照合後に ui-observer の UX スコア閾値チェックを追加 | 強化可能 |
| S3 | golden-principles.md (GP-001〜011) | "Wire Before You Decorate"（試作順序強制）の明示がない | GP-012 として追加 | 強化可能 |

## Phase 2.5 Refine 結果

### Codex 批評の要点

- **本質**: "uxaudit 自体" より「評価結果を次 iteration の Spec/Prompt へ機械的に戻す閉ループ」の運用定義の有無が重要
- **過大評価**: M1/M4 は既存で相当被覆。新規性が薄い
- **真の Gap**: M3 の「反復差分の定量比較 + `/validate` へのゲート統合」
- **前提の誤り**: 2週間文化・PM不在は組織前提。個人 dotfiles では過設計
- **Credo**: 4/5 は重複。"Wire Before You Decorate"（試作順序強制）のみ新軸
- **優先度**: Wave1=UX差分レビュー定型化、Wave2=7/10 gate validate統合、Wave3=文化/役割原則の再定義

### Gemini 周辺知識

- cc-sdd / uxaudit の公開情報は確認できず → 著者独自フレームワーク
- 7/10 ゲートは著者独自設定
- **既存カバー済み類似概念**: Spec & Verify, PostHog Agent-First, SlopCodeBench, Better Harness, Universal Verifier, UI Quality 3-Layers（すべて MEMORY.md 統合済み）

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| M3 | UX 差分定量閉ループ | 採用 | ui-observer に snapshot baseline 比較 + JSONL スコア履歴。インフラ既存でコスト小 |
| NEW | /validate UX ゲート統合 | 採用 | Universal Verifier プラン Wave 2 に合流。既存プランとシナジー |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S3 | Wire Before You Decorate 原則追加 | 採用 | KISS/YAGNI と衝突しない補完軸。試作順序の意識化 |

### 却下

| # | 項目 | 理由 |
|---|------|------|
| M1 | 4段階パイプライン全体 | 既存 `/epd` で十分 |
| M2 (4/5) | Core First ほか4原則 | 既存原則と重複 |
| M4 | 「動く vs 使える」フレーム | product-reviewer + UI Quality 3-Layers でカバー済み |
| M5 | 2週間プロトタイプ文化 | 個人 dotfiles で過設計 |

## Plan

### Task 7: ui-observer に UX 差分スコアリング追加
- **Files**: `.config/claude/agents/ui-observer.md`
- **Changes**: baseline snapshot 比較 + JSONL でのスコア履歴記録機能を追記
- **Size**: S
- **統合先**: `docs/plans/2026-04-10-universal-verifier-integration.md` Wave 2

### Task 8: /validate に UX ゲート統合
- **Files**: `.config/claude/skills/validate/SKILL.md`
- **Changes**: acceptance criteria 照合後、ui-observer の UX スコア閾値チェックを追加
- **Size**: S
- **統合先**: `docs/plans/2026-04-10-universal-verifier-integration.md` Wave 2

### Task 9: Wire Before You Decorate 原則追加
- **Files**: `.config/claude/references/golden-principles.md`
- **Changes**: GP-012「Wire Before You Decorate（試作順序強制）」追加
- **Size**: S

## 撤退条件

- Task 7/8 (UX差分閉ループ): snapshot 比較が偽陽性を多発 → 閾値緩和 or 無効化
- Task 9 (Wire Before Decorate): 既存 KISS/YAGNI と衝突が実運用で発生 → 削除

---

## 参考

- 著者: Gota (@gota_bara / GitHub: @gotalab555) — cc-sdd (3000+⭐), skillport 開発者
- 既存プラン: `docs/plans/2026-04-10-universal-verifier-integration.md`（Task 7/8 合流先）
- 関連統合済み: UI Quality 3-Layers, Universal Verifier, Skill Eval Loop, Friction Detection Loop
