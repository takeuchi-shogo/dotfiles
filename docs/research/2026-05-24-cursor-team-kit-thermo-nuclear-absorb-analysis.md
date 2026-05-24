---
source: "Cursor cursor-team-kit / thermo-nuclear-code-quality-review skill"
url: "https://github.com/cursor/plugins/blob/b8f2564c2e8da66b331c1dd63c2a2925d6739961/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md"
marketplace: "https://cursor.com/ja/marketplace/cursor/cursor-team-kit"
license: "OSS (Cursor plugin marketplace)"
date: 2026-05-24
status: integrated
family: code-review-best-practices
family-position: 4
adoption: "3/11 (T1-T3 採用、8 件 saturated/吸収/N-A 棄却)"
codex-critique-applied: true
gemini-skipped-reason: "family saturated PASS-warning + 記事自己完結 + 直接の cursor CLI integration 質問は記事内容と独立"
---

## Source Summary

**主張**: コード品質レビューは「動作する」ことで満足せず、structural simplification (code judo = behavior-preserving restructuring) を ambitious に追求すべき。1k-line / spaghetti growth / canonical leak を presumptive blocker として扱う厳格な maintainability rubric。

**手法**:
1. 1k-line crossing rule (review-time presumptive blocker)
2. Code judo (behavior-preserving restructuring)
3. Ambitious simplification mindset (review tone)
4. Presumptive blocker list (6 個明示)
5. Good phrases collection (structural critique 用、9 個)
6. Spaghetti growth detection (ad-hoc conditional / random if statements)
7. Output priority ordering (structural > simplification > spaghetti > boundary > file-size > modularity > legibility, 7 段階)
8. Canonical layer leak / bespoke helper duplicate detection
9. Type cleanliness (any/unknown/cast/optional の濫用)
10. Sequential orchestration / non-atomic updates detection
11. Magic / generic mechanism 批判 (data shape を隠す汎用機構)

**根拠**: Cursor 開発チーム内部で実運用される review rubric。`thermo-nuclear` の命名通り「珍しく厳しい」レベルの maintainability audit を意図。

**前提条件**: 振る舞いを保ったまま構造を変える code judo path が見える場合に有効。複雑なドメイン logic や spec 不明瞭な状況ではトーンが過度に侵襲的になり得る。

## Phase 1.5 Saturation Gate

- Family: `code-review-best-practices`
- Position: 4 件目 (Findy 2026-03-26 + code-review-graph 2026-03-30 + Google eng-practices 2026-05-24 13 件採用 に続く)
- 判定: **PASS (warning)** — 採用率高、重複領域として Pruning-First で 2-3 件に絞る

## Gap Analysis (Phase 2 + 2.5 Codex 批評統合後)

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | 1k-line crossing rule | **Partial** | `structure-check.py:34` `MAX_FILE_LINES=300` (edit-time advisory) は存在。「diff で 1k 跨ぐ」review-time blocker は欠落 (Codex 訂正で Gap → Partial) |
| 2 | Code judo (review 文脈に統合) | **Gap** | `/simplify` `/challenge elegant` は近いが review gate 外。code-reviewer に未統合 |
| 3 | Ambitious simplification mindset | **Gap** | 既存は evidence-based + 保守的。「whole categories of complexity を delete」フレーミングなし |
| 4 | Presumptive blocker list | **Partial** | MUST/CONSIDER 既存だが「structural blocker 候補リスト」明示なし |
| 5 | Good phrases (structural 用) | **Partial→低優先** | `review-courtesy-examples.md` は courtesy 用 |
| 6 | Spaghetti growth detection | **Partial** | CC-9 で「大関数化」は検出するが、「random if 文 bolt-on」フレーミングは別 |
| 7 | Output priority ordering (7 段階) | **Gap** | Step 1.4 の 3 段階と別 (Codex 訂正で Partial → Gap) |
| 8 | Canonical layer leak | **Gap** | bespoke helper duplicate 検出ルール未整備、最薄カバレッジ |
| 9 | Type cleanliness | **Partial** | `review-checklists/typescript.md:17` で `any/as any` MUST 既存 (Codex 訂正で Already → Partial) |
| 10 | Sequential orchestration | **Partial** | TS checklist `Promise.all`、Python `asyncio.gather()` 既存。non-atomic update は完全 Gap (Codex 見落とし指摘) |
| 11 | Magic / generic mechanism 批判 | **Gap** | Codex 見落とし指摘。薄い wrapper だけでなく「data shape を隠す汎用機構」批判は別軸 |

## Phase 2.5 Codex 批評ハイライト

- #1 Gap → Partial: `structure-check.py:34` `MAX_FILE_LINES=300` の見落とし訂正
- #7 Partial → Gap: Step 1.4 の broad→specific→nit は読む順、Cursor の 7 段階 priority とは別
- #9 Partial 維持: 根拠を `rules/typescript.md` 単独ではなく `review-checklists/typescript.md:17` に補強
- 見落とし: non-atomic updates / magic mechanism / refactor-without-deletion / parent orchestration の 4 軸
- 推奨採用件数: 2 件、最大 3 件
- cursor CLI 常時統合: **反対**。opt-in pilot として Watch 扱いから

## Integration Decisions

### 採用 (Tier 1, 3 件、すべて S 規模)

| # | 採用案 | 配置 | Status |
|---|--------|------|--------|
| **T1** | Presumptive structural blockers リスト (code-judo / spaghetti / wrapper-cast / feature leak / refactor-without-deletion の 5 観点 + Review Phrases 4 件) | `references/review-checklists/cross-cutting.md` CC-11 | ✅ 実装済 |
| **T2** | 1k-crossing review-time check (300 行 edit-time advisory と別軸の review-time presumptive blocker) | `references/review-checklists/cross-cutting.md` CC-12 | ✅ 実装済 |
| **T3** | Canonical helper / layer leak check (bespoke helper duplicate / layer 誤配置検出) | `references/review-checklists/cross-cutting.md` CC-13 | ✅ 実装済 |

### 棄却 (Tier 2, 8 件)

| # | 棄却理由 |
|---|----------|
| #2 code judo (独立採用) | T1 (CC-11) に吸収済、独立採用しない |
| #3 ambitious simplification mindset | 既存トーンを大きく変えるリスク、Pruning-First で棄却。`/challenge` `/simplify` 経由で必要時に呼ぶ |
| #5 good phrases (独立ファイル化) | T1 (CC-11) 内に 4 件最小吸収、独立 phrase ファイル化しない |
| #6 spaghetti detection (独立) | T1 (CC-11) に吸収済 |
| #7 output priority 7 段階 (独立) | T1 (CC-11) の Severity 判定で十分、7 段階明示は冗長 |
| #9 type cleanliness 強化 | `review-checklists/typescript.md:17` で既存、加筆不要 |
| #10 sequential orchestration 強化 | TS / Python checklist 既存、加筆不要。non-atomic update は将来別議論 |
| #11 magic mechanism 批判 | T1 (CC-11) に「データ shape を隠す汎用機構」として吸収 |

### Cursor CLI 統合の判断

**採用 0 件** (今回は別議論)。

- 常時 4th reviewer 統合は **棄却**: 既存 reviewer 群 (code-reviewer + codex-reviewer + cross-file + edge + Gemini) で十分。model 多様性より Cursor rubric 内容自体が価値、embed の方が安価
- 将来 opt-in pilot 検討: `strict-maintainability` reviewer として独立化、verdict 計算に入れず Watch 扱いから 10 回ログ取得 → capability score 化 → 組み込み判断
- 既存 `skills/cursor/SKILL.md` (Cursor Agent CLI ヘッドレス wrapper) は流用可能

## Plan (実装ログ)

### T1: CC-11 Presumptive Structural Blockers ✅

- **Files**: `references/review-checklists/cross-cutting.md`
- **Changes**: CC-11 セクション追加 (must 3 / consider 2 + Review Phrases 4 件 + 参照)
- **Size**: S (1 ファイル、~30 行)

### T2: CC-12 File Size Crossing Threshold ✅

- **Files**: `references/review-checklists/cross-cutting.md`
- **Changes**: CC-12 セクション追加 (must 1 / consider 1 + 既存仕組みとの関係 + 参照)
- **Size**: S (~15 行)

### T3: CC-13 Canonical Helper / Layer Leak ✅

- **Files**: `references/review-checklists/cross-cutting.md`
- **Changes**: CC-13 セクション追加 (must 2 / consider 1 + 検出方法 + Review Phrases 2 件 + 参照)
- **Size**: S (~20 行)

## Validation-only Follow-up

該当なし (記事 framing による dotfiles 内 stale fact 露出は今回なし)。Codex 批評で `structure-check.py:34` の line-count threshold (300 行) の存在を私が見落としていたが、これは drift ではなく私の調査不足。

## Meta-findings

1. **Codex 批評の効果**: Opus Phase 2 で 4 件の判定誤り (#1 #7 過大/過小評価、#9 #10 根拠補強) を訂正。bias mitigation 実証。
2. **Saturation gate 機能**: 同 family 4 件目で「PASS-warning」発火、Pruning-First で 11 候補 → 3 採用に圧縮できた。
3. **cursor CLI 質問の分離**: ユーザーの「CLI 呼び出しで使えるか?」質問は rubric 採用 (intellectual property) と CLI integration (mechanism choice) を別問題として扱うべき。今回は前者のみ採用、後者は将来 opt-in pilot 候補。
4. **Cursor 公式 OSS rubric の thoroughness**: `thermo-nuclear` 命名が示すように、Cursor 内部レビューは「不必要な complexity を残す PR を block する」傾向が強い。Google eng-practices の「courtesy / pushback」とは違う axis (structural simplification 優先) を持ち、code-review-best-practices family 内でも distinct positioning。

## 参照

- 出典: `github.com/cursor/plugins/blob/b8f2564c2e8da66b331c1dd63c2a2925d6739961/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md`
- 関連 absorb: `2026-05-24-google-eng-practices-absorb-analysis.md` (family 3 件目、13 件採用)
- 既存 cursor skill: `.config/claude/skills/cursor/SKILL.md` (CLI wrapper、流用候補)
- 関連 hook: `scripts/policy/structure-check.py:34` `MAX_FILE_LINES=300` (edit-time advisory)
