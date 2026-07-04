---
title: サージカルチェンジ
topics: [coding, decision, agent]
sources: [2026-04-12-karpathy-skills-analysis.md, 2026-04-20-karpathy-skills-absorb-analysis.md]
updated: 2026-07-05
confidence: emerging
source_count: 2
last_validated: 2026-07-05
---

# サージカルチェンジ

## 概要

サージカルチェンジは、Andrej Karpathy が提唱する LLM コーディング原則の一つで、タスクに無関係な改善・フォーマット変更・スコープ外の編集を行わないという規律である。他の3原則 (Think Before Coding / Simplicity First / Goal-Driven Execution) とあわせて、LLM が繰り返す3つの系統的エラー (暗黙的仮定・過剰実装・スコープ外の混入) に対抗する。dotfiles ではこの4原則を hard enforcement (hook によるブロック) ではなく instruction による soft nudge として扱うという哲学上の立場が明確にされており、この立場自体が Hook Philosophy ADR として成文化されている。

## 主要な知見

- **4原則のうち Goal-Driven Execution だけが唯一 deterministic block に接続される**: Think Before Coding・Simplicity First・Surgical Changes は human judgment または semantic advisory (hook が警告はするがブロックしない) にとどまるが、Goal-Driven Execution だけは `completion-gate.py` が `success_criteria` frontmatter を読んで完了ゲートとして機能する `[EXTRACTED, conf=85]`
- **PLANS.md と completion-gate.py の接続が断線していたという Gap の発見**: `completion-gate.py` は Plan frontmatter の `success_criteria:` を読む実装になっていたが、`PLANS.md` の Required Sections に Success Criteria の項目自体が存在せず、Goal-Driven Execution 原則を enforce すべき唯一の正統なゲートが実質的に fire しない状態だった `[EXTRACTED, conf=85]`
- **Hard enforcement を意図的に避ける立場が harness の哲学として成文化された**: `change-surface-advisor.py` のような scope 外変更検出は advisory (警告) にとどめ、post-write hook でブロックする設計は「semantic judgment を deterministic 化する無理筋」として明示的に却下された。この判断は ADR-0006 (Hook Philosophy) で deterministic block / semantic advisory / human judgment の3分類として文書化されている `[EXTRACTED, conf=85]`
- **配布 contract の破損という見落としがちな Gap**: Karpathy 原則を dotfiles/CLAUDE.md に反映しても、Codex (`.codex/AGENTS.md`) や Cursor (`.cursor/rules/global.mdc`) には伝播しておらず、マルチモデル運用をしているにもかかわらず Claude だけが強化される非対称が生じていた。さらに `CURSOR.md` が存在しない `.mdc`/`SKILL.md` ファイルを案内する壊れたリンクになっていた `[EXTRACTED, conf=80]`
- **多解釈の構造的列挙プロトコル (Interpretation A/B/C 形式) の追加**: Think Before Coding 原則を実効化するため、複数解釈がある場合に構造的に列挙するプロトコルと、分析麻痺を防ぐタイムボックスガードが `overconfidence-prevention.md` に組み込まれた `[EXTRACTED, conf=75]`
- **定量的な複雑度計測や pre-commit での仮定明示 regex enforcement は却下された**: Codex が提案したこれらの追加案は、儀式化 (performative compliance) やゲーミングのリスクを理由に棄却され、Surgical Changes 原則そのものが「厳格な自動化を増やさない」立場と整合していることが確認された `[EXTRACTED, conf=75]`
- **SDD (Specification Driven Development) が代替フレームワークとして台頭している**という Gemini の指摘があったが、既存の Plan → Codex Spec/Plan Gate → Implement のワークフローと重複するため独立採用はしていない `[INFERRED, conf=60]`

## 実践的な適用

`CLAUDE.md` の Editing rules セクション (「タスクに無関係な改善はしない」「隣接するコード・コメント・フォーマットは触らない」) がサージカルチェンジ原則の直接的な反映である。`rules/common/code-quality.md` にスコープ外変更の3層禁止 (コード/依存/設計) と過度な抽象化のアンチパターンが明文化されている。`PLANS.md` の Required Sections に Success Criteria が追加され、`completion-gate.py` との接続が閉じられた。`docs/adr/0006-hook-philosophy.md` が enforcement 哲学の3分類を定義し、既存 hook 群 (`protect-linter-config.py` は block、`change-surface-advisor.py` は advisory) を後付けで整理している。

## 関連概念

- [品質ゲート](quality-gates.md) — completion-gate.py など、Goal-Driven Execution 原則が接続する deterministic block の仕組み
- [Pre-generation Contract Pattern](pre-generation-contract.md) — Success Criteria の事前宣言と生成後の照合という設計思想との関連
- [ハーネスエンジニアリング](harness-engineering.md) — Hook Philosophy ADR による hook 3分類とハーネス全体の設計哲学
- [プルーニングファースト](pruning-first.md) — 新規 hook・enforcement を追加する前に既存 advisory で足りるかを判断する姿勢

## ソース

- [Andrej Karpathy Skills 分析](../../research/2026-04-12-karpathy-skills-analysis.md) — Karpathy4原則記事、多解釈列挙・スコープ規律・TDD事前宣言を追記統合
- [Karpathy Skills (andrej-karpathy-skills)](../../research/2026-04-20-karpathy-skills-absorb-analysis.md) — Karpathyコーディング原則記事を分析、4原則は実装済・PLANS.md接続とADR成文化など4タスク追加
