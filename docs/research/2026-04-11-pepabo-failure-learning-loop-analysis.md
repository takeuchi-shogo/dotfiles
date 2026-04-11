---
created: 2026-04-11
source: https://zenn.dev/pepabo/articles/claude-code-failure-learning-loop
type: absorb-analysis
---

# pepabo「Claude Code 失敗学習ループ」吸収分析

## Source

- URL: https://zenn.dev/pepabo/articles/claude-code-failure-learning-loop
- 著者: あたに (GMOペパボ)
- 取得日: 2026-04-11

## 記事の要点 (Phase 1 Extract)

- **主張**: Claude Code はセッション間で記憶がリセットされるため、プロンプト工夫より「失敗蓄積→セッション跨ぎロード」の仕組みが本質
- **手法**: 3層構造 (第1層 memory=プロジェクト固有 / 第2層 rules=全プロジェクト共通 / 第3層 CLAUDE.md=エントリポイント)
- **記録フォーマット**: 「状況・失敗・正解」の3点セット
- **実績**: 3ヶ月運用で memory 15件 + rules 5件、月1-2件のペース。EUC-JP ファイル破壊事例は昇格後「一度も再発していない」
- **思想**: 最初から網羅的に書かず、実戦で検証されたものだけ残す反復型
- **具体例**: Claude Code の Edit/Write が内部的に UTF-8 処理するため、EUC-JP ファイルが UTF-8 変換されて日本語文字化け

## ギャップ分析 (Phase 2 + 2.5, 最終テーブル)

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 3層メモリ構造 | Partial | MEMORY.md が 60+記事索引化で認知負荷大。「動く」≠「読まれる」(Codex) |
| 2 | 「状況・失敗・正解」3点セット | Already (強化不要) | 現状「壊れた→直した + verify」の方が強い。失敗フィールド追加は over-engineering |
| 3 | 失敗昇格経路 | Partial | promote-patterns.py の「7日経過」は記事の「別プロジェクトで再発」より弱い |
| 4 | セッション跨ぎ学習ループ | Already | session-learner + AutoEvolve で実装済み |
| 5 | エンコーディング破壊対策 hook | N/A | repo scan: utf-8 346/us-ascii 53/binary 4、EUC-JP なし |
| 6 | レビュー指摘繰り返し検出 | Partial | post_bash.rs は diff 近傍判定で semantic「同種再発」検出ではない |
| 7 | 反復的ルール追加 | Partial | improve-policy.md の「全カテゴリ高頻度改善」は記事の「月1-2件」思想と衝突 |

## Codex セカンドオピニオン要約

- 記事の核心は「3層構造」ではなく「**記録しない基準**」と「**まず1件だけの導入容易性**」である
- 既存セットアップは「研究知見を吸収して体系化する力」が強すぎて「実戦で残す」思想を失いつつある
- 7層まで細分化したメモリは「参照されにくくなる」罠に陥っている可能性が高い
- 項目2 (3点セット) の「失敗」フィールド追加は over-engineering。現状の「壊れた→直した + verify」の方が強い
- 項目5 (エンコーディング) は repo scan で EUC-JP/Shift_JIS なしが実測された → N/A
- **最優先は追加機能ではなく pruning と昇格基準の厳格化**
- dotfiles は個人 harness で、記事の「20年 legacy codebase」前提とは異なる。破壊リスクより認知負荷・過自動化リスクが主敵

## Gemini 周辺知識補完要約

- atani 追従事例で「無限ループ・過剰修正」が新課題として浮上
- Context Pollution, Rule Bloat, Brittleness のリスクが既知
- Anthropic 公式は「コンテキスト最小化 + Tiered Loading (description のみ初期ロード)」を推奨
- UTF-8 変換問題は 2026 現在も「既知の不安定要素」として残存

## 取捨選択 (Phase 3)

### 取り込むもの

- **P1**: Pruning Loop 実運用強制 (MEMORY.md 棚卸し + 50件上限)
- **P2**: 昇格基準の厳格化 (7日経過 → 2回以上再発)
- **P2**: 「記録しない基準」の明文化 (continuous-learning に DNR-1〜7 追加)
- **P3**: improve-policy 思想調整 (全カテゴリ高頻度改善 → 月1-2件 実戦検証型)

### スキップするもの

- 項目2「失敗」フィールド追加 (over-engineering)
- 項目5 エンコーディング guard (N/A, 現環境に EUC-JP なし)
- semantic 再発検出 (過自動化リスク, pruning 優先)

## 統合プラン概要 (Phase 4)

1. `.config/claude/skills/continuous-learning/SKILL.md` — 「記録しない基準」DNR-1〜7 セクション追加
2. `.config/claude/references/improve-policy.md` — 「現在のフォーカス」を Pruning-First 思想に書き換え、Anti-Goodhart 明記
3. `.config/claude/references/dead-weight-scan-protocol.md` — MEMORY.md/lessons-learned の容量上限トリガー追加
4. `docs/research/_index.md` — MEMORY.md の 60+記事索引を受け取る新規ファイル
5. `.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md` — 外部知見統合セクション削減 (145→120行目安)
6. `scripts/runtime/promote-patterns.py` — 昇格ロジックを「7日経過」→「2+ 異なる scope で再発 OR 3+ 総出現」に変更、30日スタール dismiss 追加

## Key Insights

- **「機能の存在」≠「機能の有効性」**: Already 判定は危険。必ず Codex + Gemini で深掘りさせる
- **認知負荷は機能数ではなくエントリ数で増える**: MEMORY.md 60+ 索引は「読まれない MEMORY」の典型
- **Anti-Goodhart**: 改善件数を KPI にすると、記録しなくて良い観察も記録してしまう
- **記事の思想 ≠ 記事の手法**: 「3層構造」は表層。「実戦で残す」が本質

## Chaining (関連ドキュメント)

- 実装プラン: `docs/plans/2026-04-11-pruning-first-philosophy-shift.md`
- 関連: `references/improve-policy.md` (容量管理), `references/dead-weight-scan-protocol.md`, `skills/continuous-learning/SKILL.md` (Do-Not-Record Criteria)
