---
success_criteria: "ADR-0008 と PLANS.md の compound ceiling 記述、skill-audit の Step 0.7 が全て追加され、docs/research/ に分析レポート、MEMORY.md にポインタが揃っている"
---

# Skill Graphs 2.0 Absorb Integration Plan

## Goal

2026-04-23 に /absorb で取り込んだ「Skill Graphs 2.0」記事 (atoms/molecules/compounds 3層モデル) のうち、Codex/Gemini 批評を経て採択された 2 項目 (A1: composition_depth metric + compound ceiling gate、A2: Coordinator vs Human RAM ADR) をセットアップに統合する。

## Success Criteria

- [x] `docs/adr/0008-coordinator-vs-human-ram.md` が存在し、drive 責任のレイヤリング表が含まれる
- [x] `PLANS.md` に `## Compound Plan Ceiling` セクション (≤8 molecules 推奨 + 分割指針) が追加されている
- [x] `.config/claude/skills/skill-audit/SKILL.md` の Step 0.7 (Composition Depth Check) で depth 判定閾値 (1-2/3-5/6-8/9+) が定義されている
- [x] `docs/research/2026-04-23-skill-graphs-2.0-absorb-analysis.md` が absorb テンプレートに沿って保存されている
- [x] `MEMORY.md` の「外部知見索引」に 1 行ポインタが追記されている
- [x] `task validate-configs` が pass する (harness contract 維持)

## Scope

### 触るファイル
- `docs/adr/0008-coordinator-vs-human-ram.md` (新規)
- `PLANS.md` (追記のみ)
- `.config/claude/skills/skill-audit/SKILL.md` (Step 0.7 追加)
- `docs/research/2026-04-23-skill-graphs-2.0-absorb-analysis.md` (新規)
- `MEMORY.md` (1 行追記)
- この plan 自身

### 触らないファイル
- `CLAUDE.md` (本記事の採択範囲では修正不要、ADR-0008 がルールを引き受ける)
- 他の既存 ADR (0001-0007)
- 既存 skill の動作本体 (skill-audit 以外)
- hooks / scripts / settings.json (G1 Tool Poisoning は Already 判定で除外)

## Constraints

- **Pruning-First 維持**: 新規 skill・新規 hook は作らない。既存 skill-audit への Step 追加と ADR 明文化のみ
- **ADR-0001/0002/0006/0007 との整合**: ADR-0008 は drive 責任を追加するだけで既存 hook 4層分離・Progressive Disclosure・Hook Philosophy と矛盾させない
- **Never delegate understanding を壊さない**: Human RAM モデルは「レベル別の drive 責任」に翻訳して取り込み、並列 5 compound drive は採用しない
- **lint config 保護**: lint 設定ファイルは触らない
- **commit --no-verify 禁止**

## Validation

- `task validate-configs` — harness 契約の保全確認
- `task validate-symlinks` — symlink 未破壊確認
- `/review` (手動起動) — 追加コード/ドキュメントのレビュー
- 目視で 4 ファイル間の相互参照リンク (ADR-0008 ↔ PLANS.md ↔ skill-audit SKILL.md) が壊れていないこと

## Steps

1. **調査** — 既存 ADR 番号 / PLANS.md 構造 / skill-audit の挿入箇所確認 ✅
2. **ADR-0008 作成** — Coordinator vs Human RAM の drive 責任レイヤリング ✅
3. **skill-audit SKILL.md 編集** — Step 0.7 (Composition Depth Check) 追加 ✅
4. **PLANS.md 編集** — `## Compound Plan Ceiling` セクション追記 ✅
5. **分析レポート書き出し** — `docs/research/2026-04-23-skill-graphs-2.0-absorb-analysis.md`
6. **MEMORY.md 更新** — 外部知見索引に 1 行追加
7. **検証** — `task validate-configs`, 相互リンク確認, `/review` を提案

## Progress

- [x] Step 1 調査
- [x] Step 2 ADR-0008 作成
- [x] Step 3 skill-audit Step 0.7 追加
- [x] Step 4 PLANS.md 追記
- [x] Step 5 分析レポート保存 (docs/research/2026-04-23-skill-graphs-2.0-absorb-analysis.md)
- [x] Step 6 MEMORY.md ポインタ追記 (外部知見索引に 1 行)
- [x] Step 7 検証 (/review 5 エージェント: codex/code/cross-file/comment/gemini、C1 = ADR README 0007/0008 追加で BLOCK→PASS、C2-C4 = harness 既存変更は user 判断に escalation)

## Surprises & Discoveries

- **G1 (Tool Poisoning) は Gap ではなく Already**: Gemini の周辺知識調査では Gap 判定だったが、`.config/claude/scripts/policy/mcp-audit.py` (297行, skill-MCP scoping + sequence anomaly) と `mcp-response-inspector.py` (284行, VeriGrey arXiv:2603.17639 Gap #5 + AgentWatcher arXiv:2604.01194 10 rule classification) が既に稼働中。Phase 4 で除外
- **K5 (reliability testing) は Already だが問題領域が違う**: /skill-audit は単一 skill eval、記事の autoresearch は graph-level reliability。Codex の指摘通り「先行実装」ではなく「隣接領域の先行実装」が正確。Step 0.7 で graph-level 観測を補完する形で統合
- **Human RAM と Coordinator の衝突**: Codex が指摘。単純採用すると "Never delegate understanding" が壊れる。ADR-0008 で drive 責任のレイヤリングに翻訳して取り込む形に変換

## Decision Log

- **A4 却下 (K1/K7'/G2)**: ユーザー初回選択は「全部取り込み」だったが push back で選択肢 (b) に変更。Pruning-First と衝突するため K1 (3 層分類強制) と G2 (Skill Graph Embedding) は棄却、K7' (/epd 責務境界) は ADR-0008 に包含させる形で最小化
- **G1 除外**: 実装確認で mcp-audit + mcp-response-inspector が VeriGrey / AgentWatcher ベースで既存。Gemini の Gap 判定は誤り、Already (強化不要) に格下げ
- **composition_depth の挿入位置**: skill-audit の Step 0 (5D) ではなく Step 0.7 (独立セクション) として追加。5D は単一 skill の静的品質、composition depth は graph 全体の構造であり次元が違うため

## Outcome

- 全 6 件の Success Criteria を充足。`/absorb Skill Graphs 2.0` 統合は PASS
- Review Gate で以下を追加修正:
  - `docs/adr/README.md` に ADR-0007 + ADR-0008 を追記 (README 側の索引漏れを cross-file-reviewer が検出)
- Codex/code-reviewer/cross-file-reviewer が別途検出した 3 件 (settings.json `effortLevel: "xhigh"`, plan-implement-bridge.py / measure-instruction-budget.py の hook 削除) は本プランの範囲外であり、別セッションの harness 変更に起因。ユーザーに escalation 済み
- Comment-analyzer の数値・引用・行数検証はすべて PASS ($0.9^n$ math、arXiv ID、line count が実体と一致)
- Gemini は [OUTLIER] 除外 (他 3 reviewer との矛盾、Gemini bias「過度に楽観的」既知)

### 未解決事項

- harness 3 件 (effortLevel/2 hooks) はユーザー判断待ち。rollback / ADR 起草 / Rust 移行検証のいずれか
