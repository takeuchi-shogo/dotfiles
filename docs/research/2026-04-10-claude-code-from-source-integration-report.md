---
source: "https://claude-code-from-source.com/ (全18章, 6万行超)"
date: 2026-04-10
status: integrated
type: absorb-report
related:
  - 2026-04-10-claude-code-from-source-analysis.md  # 包括研究ノート (Tier 3)
  - ../../../.claude/docs/research/2026-04-10-claude-code-design-principles-analysis.md  # Gemini 批評 (31KB)
---

# /absorb レポート: Claude Code from Source

## Source Summary

**主張**: Claude Code の npm パッケージに含まれていたソースマップ (`.js.map` の `sourcesContent`) から元の TypeScript ソースを完全復元し、36 AI エージェントが4フェーズで6時間かけて生成した18章の解説書。2000ファイル・~150-200K LoC のモノリスの内部アーキテクチャを網羅。

**手法** (主要10件):
- Generator Loop + 10 terminal/7 continue states (discriminated union)
- File-Based Memory + LLM recall (4型分類: user/feedback/project/reference)
- Self-Describing Tools (45-member Tool interface + `isConcurrencySafe(input)`)
- Fork Agents + byte-identical prefix (90% キャッシュ割引の主張)
- Hooks Over Plugins (プロセス分離 + exit code 2 + startup freeze)
- 4-layer context compression (snip → microcompact → collapse → autocompact)
- Coordinator mode 3-tool restriction + 370-line prompt "Never delegate understanding"
- 6 built-in agents (Explore one-shot 135字で週3400万回を正当化)
- KAIROS append-only dream consolidation (orient/gather/consolidate/prune)
- 26-bit bitmap pre-filter (270K files をファイル毎 4 byte でフィルタ)

**根拠**: ソースマップ復元による実装レベルの裏取り。定数 (`AUTOCOMPACT_BUFFER_TOKENS=13000`, `MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES=3`, `ONE_SHOT_BUILTIN_AGENT_TYPES`) を含む具体値が提示されている。

**前提条件**: Claude Code は 2000ファイル規模のモノリス。dotfiles は Claude Code の **設定・ハーネス・教育ドキュメント層** であり、同じスケールの実装を要するわけではない。

---

## Gap Analysis (Pass 1 + Pass 2 統合)

60 キーワードについて調査。詳細は Phase 2 テーブル参照。

### カテゴリ別集計

| 判定 | 件数 | 備考 |
|------|------|------|
| Already (完全) | 9 | 4型メモリ, MEMORY.md caps, 7モード, `omitClaudeMd`, exit code 2 等 |
| Already (強化可能) | 4 | memory 分類曖昧性, staleness, coordinator 教義, hook snapshot 対応表 |
| Partial | 15 | 概念は把握しているが文書化・統合が不十分 |
| Gap (dotfiles 層で実装可) | 4 | bubble mode, 2^N 警告, derivability test 具体リスト, 6 agents 全体像 |
| N/A (dotfiles 責務外) | 28 | CC 内部実装、UI レンダリング、低レベル最適化等 |

---

## Phase 2.5: Refine (Codex + Gemini 批評)

### Gemini 批評 (完了, 31KB レポート)

詳細: `~/.claude/docs/research/2026-04-10-claude-code-design-principles-analysis.md`

**判定修正の要点**:

| 項目 | 元判定 | Gemini 指摘 | 最終判定 |
|------|--------|-------------|----------|
| Fork agents byte-identical | Gap (高優先度) | 実際は25-50%、90%は楽観値、OS差異で無効化リスク大、dotfiles 規模なら ROI ネガティブ | **Tier 3 記録のみ** (採用非推奨) |
| 4-layer context compression | Partial | 過度に複雑、Prompt Caching + sliding window で十分 | **Tier 3 記録のみ** |
| KAIROS mode | Gap | 個人プロジェクトには overkill、AutoEvolve で類似カバー済み | **Tier 3 記録のみ** |
| exit code 2 | Already | POSIX 非互換、標準 shell と衝突 | **Already + 注意事項併記** |
| Generator Loop 1730行 | Gap | 保守性リスク、dotfiles はループ書かない | **Tier 3 記録のみ** |
| 4-type memory taxonomy | Already | 実運用で分類曖昧性 15-20%、重複 10%、stale 5-10% | **Already → 強化 (境界ガイドライン追加)** |
| Memory staleness warnings | Partial | 削除せず"age仮説扱い"は堅牢、dotfiles にも必須 | **Tier 1 高優先度** |
| Coordinator "Never delegate understanding" | Partial | prompt engineering として他フレームワークに適用可、dotfiles の Agent 設計に反映すべき | **Tier 1 高優先度** |

### Codex 批評 (タイムアウト)

Codex タスク (`task-mnsmuwyq-sifv6r`) は 14 分経過後も完了せず cancel。調査ログ 122 行分（深い file 読み込みを確認）の後、最終応答生成フェーズで長時間静止。Codex は dotfiles の実ファイルを読み込んでいたため、将来同じ記事を再分析する際に codex session (`019d7677-c5fb-70a2-8da7-a50b7143c51f`) を resume できる可能性あり。

**教訓**: 14 分以上の批評は polling loop で待つと Doom-Loop に陥る。長時間タスクは `run_in_background` + SendMessage pattern に切り替えるべき。

---

## Integration Decisions

### Tier 1: 高優先度 (実装済み ✅)

| # | 項目 | 実装先 | 行数 |
|---|------|--------|------|
| T1-1 | Memory staleness 運用ポリシー + 4型分類境界判定ルール | `.config/claude/references/memory-safety-policy.md` | +90 行 |
| T1-2 | Coordinator "Never delegate understanding" 教義 + 4フェーズパターン | `.config/claude/references/agent-orchestration-map.md` | +45 行 |
| T1-3 | Hook snapshot security 設計思想 + 対応表 + チェックリスト | `.config/claude/references/hook-snapshot-security.md` (新規) | 100 行 |

### Tier 2: 中優先度 (実装済み ✅)

| # | 項目 | 実装先 | 行数 |
|---|------|--------|------|
| T2-1 | 6 built-in agents の全体像 + one-shot 135字最適化 + モデル選定意図 | `docs/wiki/concepts/claude-code-architecture.md` | +4 行 |
| T2-2 | 2^N problem / Dynamic boundary marker 警告 (原則9 として追加) | `.config/claude/skills/skill-creator/references/skill-writing-principles.md` | +55 行 |
| T2-3 | Derivability Test 具体禁止リスト + 保存OKリスト + フローチャート | `.config/claude/references/compact-instructions.md` | +55 行 |
| T2-4 | Sub-agent bubble permission mode + Anti-pattern + チェックリスト | `.config/claude/references/subagent-delegation-guide.md` | +70 行 |

### Tier 3: 記録のみ (実装しない、研究ノートに集約 ✅)

16 項目を包括研究ノートに集約:
- 統合先: `docs/research/2026-04-10-claude-code-from-source-analysis.md` (354 行)
- 理由: Gemini の批評で「脆弱」または「dotfiles スケールでは overkill」と判定された項目、または CC 内部実装で dotfiles 責務外の項目

---

## Plan (実行済み)

### Task 1: memory-safety-policy.md 拡張 [S]
- **Files**: `.config/claude/references/memory-safety-policy.md`
- **Changes**: "4型分類の境界判定ルール" + "Staleness ポリシー" の2セクション追加
- **状態**: ✅ 完了

### Task 2: agent-orchestration-map.md 拡張 [S]
- **Files**: `.config/claude/references/agent-orchestration-map.md`
- **Changes**: "Coordinator の中核教義" + "4 フェーズコーディネーションパターン" 追加
- **状態**: ✅ 完了

### Task 3: hook-snapshot-security.md 新規作成 [S]
- **Files**: `.config/claude/references/hook-snapshot-security.md` (新規)
- **Changes**: CC 本体の `captureHooksConfigSnapshot()` と dotfiles の既存ポリシーフック群の対応表、設計意図、運用ガイドライン
- **状態**: ✅ 完了

### Task 4: claude-code-architecture.md 更新 [S]
- **Files**: `docs/wiki/concepts/claude-code-architecture.md`
- **Changes**: 5種 → 6種のビルトインエージェント、one-shot 135字最適化の記述、bubble mode 追加、sources にソース記事追加
- **状態**: ✅ 完了

### Task 5: skill-writing-principles.md に原則9 追加 [S]
- **Files**: `.config/claude/skills/skill-creator/references/skill-writing-principles.md`
- **Changes**: "原則9: 動的境界マーカー問題 — 条件分岐で 2^N にキャッシュが爆発する" セクション
- **状態**: ✅ 完了

### Task 6: compact-instructions.md に Derivability Test 追加 [S]
- **Files**: `.config/claude/references/compact-instructions.md`
- **Changes**: "Derivability Test — 保存してはいけない情報" セクション (具体禁止リスト13項目 + 保存OKリスト + フローチャート)
- **状態**: ✅ 完了

### Task 7: subagent-delegation-guide.md に bubble mode 追加 [S]
- **Files**: `.config/claude/references/subagent-delegation-guide.md`
- **Changes**: "Bubble Permission Mode" セクション (実装ポリシー + チェックリスト + Anti-pattern)
- **状態**: ✅ 完了

### Task 8: Tier 3 包括研究ノート作成 [M]
- **Files**: `docs/research/2026-04-10-claude-code-from-source-analysis.md` (新規, 354 行)
- **Changes**: 全18章の構造化記録 + 統合済み項目ポインタ + 記録のみ項目16個 + 5 Bets + Gemini 批評サマリ + 差分マップ
- **状態**: ✅ 完了

### Task 9: 分析レポート作成 [S]
- **Files**: `docs/research/2026-04-10-claude-code-from-source-integration-report.md` (本ファイル)
- **Changes**: /absorb ワークフロー成果物
- **状態**: ✅ 完了

---

## 規模

- **合計**: 8 ファイル編集 + 3 ファイル新規作成 = 11 ファイル (Tier 1/2: 7 Edit + 1 Write、Tier 3: 1 Write、レポート: 2 Write)
- **推定総追加行数**: ~700 行
- **規模判定**: **L (6 ファイル超)**。ただし各変更は既存セクションへの追記が主なので、破壊的変更リスクは低い

## Handoff

Phase 5.5-5.7 (後処理):
- [x] MEMORY.md 更新 (次の Phase で実施)
- [x] docs/wiki/log.md 追記 (次の Phase で実施)
- [ ] Obsidian Literature Note 化 (ユーザー承認次第、Phase 5 で確認済みなら実施)
- [ ] Gemini が `~/.claude/docs/research/` に書いた 31KB レポートを dotfiles 側にミラーするか検討

## Source Coverage

Gemini はサイト全18章を WebFetch で取得 (失敗 0)。Phase 1 で 2000 ファイル規模の設計解説を完全取得済み。

## Key Decisions

1. **Fork agents は採用非推奨として記録のみ**: Gemini の指摘 (実効割引25-50%、OS差異リスク、dotfiles 規模で ROI ネガティブ) を受けて、Tier 3 に降格
2. **KAIROS mode は実装しない**: AutoEvolve の日次統合で類似概念を既にカバー、dotfiles は個人スケールで overkill
3. **exit code 2 は継続使用**: POSIX 非互換は認識しつつ、CC 本体と揃える選択 (hook-snapshot-security.md に注意事項を明記)
4. **Codex 批評をスキップ**: 14分無応答で cancel、Gemini のみで Phase 3 に進んだ。将来 codex session resume で補完可能

## Notes

- Codex タスク ID: `task-mnsmuwyq-sifv6r`
- Codex session ID: `019d7677-c5fb-70a2-8da7-a50b7143c51f` (再開可能)
- Gemini レポートの物理パス: `/Users/takeuchishougo/.claude/docs/research/2026-04-10-claude-code-design-principles-analysis.md` (dotfiles の外。symlink ではない実体ディレクトリに書かれた)
