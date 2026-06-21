---
source: "How to Review AI-Generated Code Like a Senior Developer (Mari, 2026 medium/X article)"
date: 2026-06-20
status: analyzed
adoption: narrow (1/9 step, Step 6 routing 漏れの構造補正)
family: code-review-best-practices
phase_25: skipped (家族飽和 + Step 6 単独に絞り込み、grill-me で確定)
---

## Source Summary

**Title:** How to Review AI-Generated Code Like a Senior Developer
**Author:** Mari (backend developer / technical writer)
**Form:** medium / X 系 essay (no peer review, opinion + 経験則)

**主張**: AI 生成コードは「動く」と「ship 可能」の間に大きな gap があり、レビューはそれ自体が writing と別 skill になる。9 ステップに分解:

1. 問題から始める (requirement-first)
2. 設計判断を問う (default の framework / DB を疑う)
3. 論理を読む (syntax ではなく logic / 境界値)
4. 隠れた前提を狩る (input 有効 / 外部 service 応答 / record 存在 / network 動作)
5. セキュリティを意図的に通す (auth / authz / input validation / secrets / SQL injection / hallucinated dependencies)
6. **実データ挙動を見る (N+1 / missing index / multiple calls / over-fetch)**
7. 過剰設計を削る (YAGNI)
8. エラーハンドリングを探す (happy path 偏重抑制)
9. 保守性を問う (6 か月後の自分が読めるか)

**統計引用**: 2026 study で AI backend code の 35% のみ secure + correct。Veracode 100+ models × 80 tasks で half に既知脆弱性。

## Phase 1.5 Saturation Gate

**Family**: code-review-best-practices
**N** (本記事込み): 10 (MEMORY.md 記載 N=9 "saturated-but-novel" の延長)
**判定**: 形式的に PASS (warning) (Mari 個人記事、エビデンスは公開統計引用)、grill-me で 1 件採用に絞り込み確定 → フル workflow 実行

### per-step 照合台帳 (Step 1-9 → matched_prior 名指し)

| Step | 主張 | verdict | matched_prior (3点セット) |
|------|------|---------|---------------------------|
| 1. 要件先行 | spec / 一文要件確認 → 実装との突合 | **rehash** | `skills/review/SKILL.md:218-228` Step 1.5 Design Rationale Check (M/L) + Step 4 Mandatory Review Dimensions "仕様整合性" + `agents/product-reviewer.md` spec file acceptance criteria |
| 2. 設計判断 | framework / DB の default 採用を疑う | **rehash** | `cross-cutting.md` CC-15 依存方向 + CC-11 Presumptive Structural Blockers (Cursor thermo-nuclear 由来) |
| 3. 論理 | syntax と logic を分離、境界値 / race condition | **rehash** | `agents/edge-case-hunter.md` + `agents/code-reviewer.md` Pass 1 全行 enumeration + `edge-case-analysis` skill |
| 4. 隠れた前提 | input 有効 / 外部応答 / record 存在 / network 動作 | **rehash** | `agents/edge-case-hunter.md` + `agents/silent-failure-hunter.md` + CC-2 エラーハンドリング可視性 |
| 5. セキュリティ | OWASP auth/authz, validation, secrets, SQLi, **slopsquatting** | **rehash (高品質)** | `agents/security-reviewer.md:208` Slopsquatting check 明示 (`npm info` / `pip index versions` / `go list -m` で CRITICAL 検出) + `agents/security-reviewer.md:259` supply chain rubric + `cross-cutting.md` CC-1 secrets + `references/review-checklists/security-baseline.md` + `references/review-checklists/injection-rules.md` |
| **6. 実データ挙動 (N+1 / index / batch / over-fetch)** | **partial** | `codex-reviewer.md:61` に明示 + `reviewer-capability-scores.md:32` に performance domain あり。**ただし cross-cutting.md / 言語別 checklist には項目なし、Step 2 dispatch trigger 未配線** → 200 行未満では誰も performance を見ない構造穴 |
| 7. 過剰設計を削る | YAGNI、wrapper / factory / service 層の積み増し抑制 | **rehash** | CC-11 Presumptive Structural Blockers (random if bolt-on / 薄い identity wrapper / `as any` 多用) + CC-12 File Size Crossing 1k + CC-13 Canonical Helper Leak + `agents/code-simplifier.md` + `skills/simplify` |
| 8. エラーハンドリング | happy path 偏重 / catch-all swallow / 失敗時 fallback | **rehash** | `agents/silent-failure-hunter.md` + CC-2 エラーハンドリング可視性 + `references/dual-audience-cli-guide.md` Fail Fast 境界 + `<core_principles>` "暗黙フォールバック・モック・NO-OP 絶対禁止" |
| 9. 保守性 | 6 か月後の自分が読めるか / 一貫性 / clever 抑制 | **rehash** | `agents/cross-file-reviewer.md` + `agents/type-design-analyzer.md` + `agents/longevity-reviewer.md` (200 行超で自動起動) + CC-8 Linguistic Anti-patterns |

**delta = 1** (rehash 8 + partial 1 = 採用検証対象 1)

## Phase 2 Pass 1 (実装確認 grep)

| キーワード | 存在判定 | 主要ファイル |
|------------|----------|--------------|
| N+1 / over-fetch / missing index | **partial (codex-reviewer 内蔵のみ)** | `agents/codex-reviewer.md:61` + `skills/review/references/reviewer-capability-scores.md:32` (performance domain) |
| Slopsquatting / hallucinated dependency | **exists (高品質)** | `agents/security-reviewer.md:208,259` + 検証コマンド明示 |
| Requirement-first / spec 整合性 | **exists** | `skills/review/SKILL.md:218,339,342,435` (Step 1.5 + product-reviewer + Mandatory Review Dimensions) |
| YAGNI / overengineering | **exists** | `agents/product-reviewer.md:44` + CC-11/12/13 + code-simplifier |

**真の gap**: Step 6 の routing 漏れ — capability score は登録、agent (codex-reviewer) は知っている、しかし cross-cutting に項目がなく、Step 2 dispatch trigger 未配線。200 行未満で codex-reviewer が呼ばれないケースで誰も performance を見ない。

## 採用 (1 件)

### Step 6 → CC-17 (cross-cutting) + 言語別 checklist 4 ファイル

**改修ファイル**:
1. `references/review-checklists/cross-cutting.md` — **CC-17 Performance with Real Data** 追加 (17a N+1 / 17b over-fetch / 17c missing index / 17d multiple calls + false positive 抑制 4 条項 + 検出方法 + 参照)
2. `references/review-checklists/go.md` — GO-18 (GORM Preload / FindInBatches / Select 列限定)
3. `references/review-checklists/typescript.md` — TS-24 (Prisma include / findMany batching / select 列限定 / Promise.all 並列化)
4. `references/review-checklists/python.md` — PY-13 (Django select_related/prefetch_related / SQLAlchemy joinedload/selectinload / only/defer / id__in バッチ化)
5. `references/review-checklists/rust.md` — RS-21 (Diesel inner_join / SQLx query macro / WHERE id = ANY / select 列限定 / Stream chunk)

**触らない**:
- `skills/review/SKILL.md` (Step 2 dispatch table / agent routing は変更しない — cross-cutting に入れたことで code-reviewer が全 review で見るようになる、dispatch trigger 追加は YAGNI)
- `agents/*.md` (全 14 reviewer agent)
- `skills/review/references/reviewer-routing.md` / `reviewer-capability-scores.md` / `review-consensus-policy.md`

**root cause 仮説**: cross-cutting (全 review 注入の共通観点) + 言語別 (具体的 fix recipe) の既存分業設計に **performance domain が抜けていた** だけ。新規 specialist agent を作る / 新規 dispatch routing を引く対応は不要 (Build-to-Delete + 既存重い設計を尊重)。

## 不採用 (8 件)

| Step | 不採用理由 |
|------|------------|
| 1 | Step 1.5 + Mandatory Review Dimensions "仕様整合性" + product-reviewer で全 review に既注入。S 規模は元々 light tier で省略可なので追加観点不要 |
| 2 | CC-15 + CC-11 で技術選定の自動疑問は既に走る。"Django vs FastAPI を毎回問え" は project context (実務 Go/TS) で N/A |
| 3 | edge-case-hunter + code-reviewer Pass 1 で境界値 / 全行 enumeration は強制済 |
| 4 | edge-case-hunter + silent-failure-hunter + CC-2 で input 有効 / 外部応答 / record 存在は既カバー |
| 5 | security-reviewer 17KB + Slopsquatting CRITICAL ハンドリングは記事より具体的かつ高品質 |
| 7 | CC-11/12/13 + code-simplifier で十分。Step 7 dispatch 追加は Sonnet imagination 罠を呼ぶ |
| 8 | silent-failure-hunter + CC-2 + dual-audience-cli-guide で Fail Fast / Trust 境界が既設計化済 |
| 9 | cross-file-reviewer + type-design-analyzer + longevity-reviewer (200 行超自動) + CC-8 で保守性軸は十分 |

## Phase 2.5 (skipped)

Mari 記事は essay (no peer review、Anthropic / Google 公式の体系記事ではない)、grill-me で 9→1 に確定済 (採用範囲が明確)、family saturated (N=10) で adversarial counter-source の ROI 低。

## family 教訓 (本回追加)

**code-review-best-practices family (N=10)**:

- **routing 漏れ vs 観点漏れの混同**: 「観点が無い」と「routing で呼ばれない」を分離して診断する。reviewer-capability-scores に domain 登録 + agent 内蔵チェック + cross-cutting/dispatch 未注入 = "正しく実装されたのに呼ばれない" 構造穴。本記事 Step 6 はこの構造穴を外圧で露出させた
- **既存 review skill の重い設計を尊重**: 697 行 SKILL.md + 14 reviewer agent + 4 reference は理由があって積み上がった。記事の 9 step 程度の外圧で SKILL.md 本体 (dispatch table / agent routing) を再構造化するのは過剰反応。**改修は cross-cutting / 言語別の最末端だけで足りる**
- **新規 specialist agent 追加は Build-to-Delete 違反のシグナル**: N+1 専用 performance-reviewer を作るのは 14→15 への増殖。既存 cross-cutting に項目追加で済む場合、新規 agent は YAGNI

## ledger 記録

- `promoted-ledger.jsonl`: 該当なし (cross-cutting CC-17 は新規 review checklist 項目、learned 昇格パスではない)
- MEMORY.md family 索引: "code-review-best-practices family (N=10)" に更新 + 本記事の 1 行教訓を追記
- `_index.md`: コード品質 / レビュー カテゴリに 1 行追記
