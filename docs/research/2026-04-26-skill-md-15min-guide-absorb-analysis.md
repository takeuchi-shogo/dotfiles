# Absorb Analysis: Claude Code + SKILL.md: build your first auto-invoking AI workflow in 15 minutes

- **著者**: Nyk (@nyk_builderz, community power user, Anthropic 公式ではない)
- **種類**: SKILL.md オーサリング初級ガイド (7 セクション)
- **分析日**: 2026-04-26

---

## Phase 1: 構造化抽出

**主張**: SKILL.md は markdown ファイルで auto-invocation する。description が trigger。allowed-tools で安全網。<50 行で始め、必要なら @reference で分割。

**7 手法**:

| # | 手法 | 説明 |
|---|------|------|
| 1 | SKILL.md frontmatter | `name`, `description`, `allowed-tools`, `paths` |
| 2 | Description as trigger | trigger の具体性が肝 |
| 3 | allowed-tools restriction | 最小権限 |
| 4 | paths field | `paths: ["src/api/**/*.ts"]` でスコープ制限 |
| 5 | @FILENAME.md reference | supporting files で分割 |
| 6 | 5 beginner skill types | review / debugging / documentation / test-first / deploy |
| 7 | 5 mistakes | broad description / >200 lines / no examples / skip allowed-tools / multi-file too early |

**根拠**: 公式 docs + superpowers (96K⭐) + gstack (20K⭐) + 著者の x-article-factory pipeline 経験

**前提**: SKILL.md オーサリング初心者向け

---

## Phase 2: ギャップ分析

### 判定表

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | `paths:` field (path-scoped activation) | **N/A (by design)** | rules/ レベルで paths 実装済み (typescript.md, go.md 等)。skill=task intent / rules=file/cwd constraint の分離を維持 |
| 2 | 5 beginner skill types | **Already** | 6 pattern (tool-wrapper/generator/reviewer/pipeline/inversion/composite) でカバー済み |
| 3 | <50 行 SKILL.md 原則 | **Already** | <500 行 + DBS (Direction/Blueprints/Solutions) 三層が確立。Progressive Disclosure 設計 |
| 4 | examples/ ディレクトリ慣例 | **Partial** | references/ に混在。skill-audit での「examples 有無」検証は未実装 |
| 5 | allowed-tools 最小権限 | **Already** | 68/68 スキル適用済み (mcp-audit.py で実行時 enforcement) |
| 6 | description trigger 具体化 | **Already** | 90/90 Triggers/Do NOT use 記述済み |
| 7 | personal vs project scope | **Already** | cwd-routing-matrix.md が分離設計を管理 |

### Already 項目の強化分析

| 既存の仕組み | 記事の観点 | 強化判定 |
|-------------|-----------|---------|
| allowed-tools 100% 適用済み | 安全網の最小権限 | **強化不要** |
| description 100% Triggers/Do NOT use 記述 | trigger 具体化 | **強化不要 (継続検証必要)** — 記述率 ≠ 誤発火率最適化 |
| <500 行 + DBS (skill-writing-principles.md) | <50 行 + @reference | **強化不要** — DBS の方が成熟 |
| references/ に examples 混在 | Show don't tell | **微強化可** — skill-audit 5D Quality Check に「examples 有無」追加余地 |
| cwd-routing-matrix.md | ~/.claude vs .claude scope | **強化不要** — より緻密な設計 |

---

## Phase 2.5: Refine (Codex + Gemini 並列批評)

### Codex 批評 (主要指摘)

1. **「100% description coverage ≠ 品質」**: 記述率は Already だが、誤発火率・negative trigger の品質保証は別軸。skill-audit が継続検証を担う
2. **paths field の N/A by design 判定は妥当**: skill=task intent / rules=file/cwd constraint の分離を崩すべきでない。SKILL.md レベルの path-scoped activation を導入すると cwd matrix / rules paths / soft guidance と三重化する
3. **記事の build-first は Pruning-First と逆向き**: 90 skills 環境では「増やしすぎないか」「発火境界が壊れていないか」が問題
4. **唯一の P1**: skill-audit に supporting file/examples の discoverability チェックを追加 (新規概念ではなく既存 Partial の監査強化、Pruning-First と整合)

### Gemini 補完 (Google Search grounding)

- **著者 Nyk**: 実在の community power user、Telegram channel 実在 (~400-1000 members)、Anthropic 公式ではない
- **superpowers (96K⭐) / gstack (20K⭐)**: 実在確認、widely-used
- **paths field の実装状況**: rules/typescript.md で `paths: ["**/*.ts", "**/*.tsx"]` が稼働中 — ただし **rules layer であり SKILL.md layer ではない** (Codex の判断と整合)
- **「15 分」タイムライン**: 過大宣伝の可能性 (現実は production skill 1-2 時間)
- **vendor bias リスク**: Telegram channel への誘導 (community echo chamber)

### Codex vs Gemini の食い違い解消

Gemini は当初「paths field は real」と表現したが、実態は rules ファイル稼働分。SKILL.md frontmatter には paths は使われていない。両者は同じ事実を指す: **paths は rules layer の機能で、SKILL.md には足さない方が良い**。

---

## Phase 3: Triage

**判定: 取り込まない (推奨どおり)**

理由:
- 90 スキル + skill-creator + skill-audit + writing-skills + skill-conflict-resolution + cwd-routing-matrix の成熟度に対して、記事は初級ガイドで新規価値なし
- Pruning-First 方針 (新規追加 < 既存強化) と整合
- Codex の最終判断「取り込み不要」を支持
- 唯一の微強化候補 (skill-audit examples discoverability) はユーザー判断でスキップ

Phase 4 (プラン生成) と Phase 5 (Handoff) はスキップ。

---

## 学び

1. **初級ガイドの absorb は希薄**: 成熟したセットアップに対する初級記事は、ほぼ全項目が Already になる。記事のレベル (初級/中級/上級) を Phase 1 で見極めて分析の深さを調整する余地あり
2. **「100% 適用 ≠ 品質保証」**: description 100% coverage は「フォーマット遵守」であって「誤発火率最適化」ではない (Codex 指摘)。今後 absorb で「100% Already」と即判定する前に「品質軸」も検証する
3. **paths field レイヤリング**: SKILL.md と rules で path-scope の責務を分離する設計は崩さない (skill=intent / rules=file constraint)
4. **community blogger のベンダーバイアス**: Anthropic 公式ではない community power user の主張は、特定 repo (superpowers/gstack) を権威化する傾向あり。記事の手法を採用する前に「公式仕様か community 慣例か」を区別する

---

## 関連リンク

- 既存 absorb 記事:
  - [`2026-04-19-top67-claude-skills-analysis.md`](2026-04-19-top67-claude-skills-analysis.md) — 64 棄却 (Pruning-First)
  - [`2026-04-23-skill-graphs-2.0-absorb-analysis.md`](2026-04-23-skill-graphs-2.0-absorb-analysis.md) — composition_depth 採用
  - [`2026-04-20-karpathy-skills-absorb-analysis.md`](2026-04-20-karpathy-skills-absorb-analysis.md) — 78/100 既実装
  - [`2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md`](2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md) — 23/92 採用
- 関連スキル: skill-creator, skill-audit, writing-skills (superpowers), skill-conflict-resolution.md
- ADR: ADR-0006 (Hook Philosophy 3 分類), ADR-0007 (Thin+Thick)
