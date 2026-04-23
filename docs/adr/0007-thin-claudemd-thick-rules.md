# ADR-0007: Thin CLAUDE.md + Thick rules/

## Status

Accepted

## Context

ADR-0002 で Progressive Disclosure 3 層を採用したが、「CLAUDE.md をどの程度薄く保つか」の定量基準が未定義だった。結果として、CLAUDE.md は 500 行近くまで肥大化する傾向があり、新規ルール追加時の置き場判断が属人的になっていた。

2025-2026 の複数の実証研究・実運用事例が薄い CLAUDE.md の優位性を示した:

- **IFScale ベンチマーク (2025)**: 指示数増加で性能劣化パターンは 3 種（閾値型 100-150 で急激崩壊 / 線形型 / 指数型）。CLAUDE.md の実用上限は 40,000-50,000 文字
- **Progressive Disclosure 運用事例**: CLAUDE.md → docs/ 外部化で約 30% のハルシネーション削減が報告
- **akira_papa_AI の Obsidian × Claude Code 運用 (2026-03)**: CLAUDE.md 500→80 行削減で運用時間が激減。rules/ は 18 ファイルに厚く保持
- **当 dotfiles の実測**: CLAUDE.md は 94 行、rules/ は 18 ファイルという比率が既に稼働中だが、原則として明文化なし

ADR がないため、将来の変更で「CLAUDE.md に書く or rules/ に書く」の判断が揺らぎ、薄さが崩れるリスクがある。

## Decision

**CLAUDE.md は「薄く」保ち、rules/ は「厚く」保つ** ことを設計原則として明文化する。

### 定量基準

- **CLAUDE.md**: 上限 150 行（約 6,000-8,000 文字）、下限なし
- **rules/**: ファイル数上限なし、個別ファイルは 1 ファイル 200 行を目安に分割

### Token-based 上限（Gemini absorb 2026-04-23 追加）

行数 + 文字数 proxy の二段構え（最初は tiktoken 化しない）:
- **CLAUDE.md**: ≤ 4KB（推奨 3KB、~80 行）
- **AGENTS.md / .codex/AGENTS.md**: ≤ 4KB（~130 行）
- **references/ 単独**: ≤ 8KB（~200 行）
- 超過で **soft warning**（hard block しない）

根拠:
- `>4KB / ~4000 tokens` で Lost in the Middle 現象（2025 実証研究）
- AGENTS.md + 直接 reference の合計 token を定期計測すべき
- 行数だけでは日本語/コードブロック/表で実態とずれる

検証:
- `scripts/policy/claudemd-size-check.py` が PostToolUse hook で発火
- 警告は stderr に出力、ブロックしない

### 置き場判断ルール

CLAUDE.md に置くもの:
- 毎ターン必要な decision heuristics（KISS, search-first, 壊れたら STOP など）
- 常に参照すべき references へのポインタ
- `<important if="...">` 条件付きサブセクションで読み込みを絞る

rules/ に置くもの:
- 言語別ルール（go, typescript, rust 等）
- ドメイン別ルール（testing, security, code-quality 等）
- 横断原則（overconfidence-prevention, error-handling 等）
- `paths:` frontmatter で条件ロード可能なもの

references/ に置くもの:
- 詳細ワークフロー（workflow-guide, harness-stability 等）
- チェックリスト（pre-mortem-checklist 等）
- 技術調査結果（model-routing, brevity-tradeoff-research 等）

## Consequences

### Positive

- **性能維持**: IFScale 線形劣化領域 (100-150 指示) に入らずに済む
- **信号対雑音比**: 毎ターンの CLAUDE.md 読み込みが decision heuristics に集中
- **判断軸確立**: 新規ルール追加時の置き場判断が機械的に決まる
- **ハルシネーション削減**: Progressive Disclosure の効果 (~30%) を保てる
- **MEMORY.md との整合**: MEMORY.md もサマリ+パス参照のみ、という既存方針と一貫

### Negative

- **初動コスト**: 150 行を超えた時点で rules/ or references/ に分割する作業が発生
- **ポインタ維持コスト**: CLAUDE.md から references/rules への参照が壊れると情報が届かない（ただし doc-garden-check hook で検出可能）
- **判断の難しさ**: 「decision heuristic か / 詳細ワークフローか」の境界がグレーなケースがある

### Neutral

- ADR-0002（Progressive Disclosure）の具体化であり、矛盾はしない
- 既存 CLAUDE.md 94 行は基準を満たしており、マイグレーションコストなし
- 違反検出を hook 化する場合は、CLAUDE.md の行数チェック + `<important if>` タグ数の比率監視が候補
