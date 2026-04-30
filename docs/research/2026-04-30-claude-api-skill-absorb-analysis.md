---
source: "https://claude.com/blog/claude-api-skill"
date: 2026-04-30
status: skipped
---

# Claude API skill now in CodeRabbit, JetBrains, Resolve AI, and Warp — Absorb Analysis

## Source Summary

- **タイトル**: Claude API skill now in CodeRabbit, JetBrains, Resolve AI, and Warp
- **著者**: Anthropic 公式
- **公開日**: 2026-04-29
- **主張**:
  1. claude-api skill が Claude Code 以外の 4 ツール (CodeRabbit, JetBrains, Resolve AI, Warp) に展開された
  2. skill は SDK 変更に追従し、新モデル・新 API 機能を自動的に把握する
- **5 テクニック**:
  1. Prompt caching optimization
  2. Context compaction for agent patterns
  3. Model migration automation (4.5→4.6→4.7, retired-model 置換)
  4. Managed agents onboarding (long-running research)
  5. SDK-aware code generation

## Article Claims

### 主張 1: Partner tool への skill 展開
claude-api skill が CodeRabbit・JetBrains・Resolve AI・Warp という 4 社の外部ツールに統合された。Anthropic がスキル配布エコシステムを他ツールに広げる動きとして提示。

### 主張 2: SDK 自動追従
skill は Anthropic SDK の変更に追従し、新モデルや新 API 機能を自動的に把握するとしている。partner tool に対しても最新情報を提供する配布モデルを想定。

### 5 テクニック listing
1. **Prompt caching optimization** — `cache_control` を使ったコスト削減 (最大 90%)
2. **Context compaction for agent patterns** — エージェント向け compaction プリミティブ
3. **Model migration automation** — 4.5→4.6→4.7 バージョンアップ + retired-model 置換スクリプト
4. **Managed agents onboarding** — 長時間リサーチ向けマネージドエージェント導入
5. **SDK-aware code generation** — Anthropic SDK を認識したコード生成

## Gap Analysis (Pass 1 + Pass 2 統合テーブル)

| # | 手法 | 判定 (修正後) | 詳細 |
|---|------|--------------|------|
| 1 | claude-api skill 本体 | Already (強化不要、独立 hygiene) | `everything-cc/skills/claude-api/SKILL.md` に存在するが Opus 4.1/Sonnet 4.0/Haiku 3.5 で陳腐化 (現行: 4.7/4.6/4.5)。Codex 批評で「記事採用判断を変える load-bearing ではない、単独 hygiene 修正」と判定。MEMORY.md の skills:verify mismatch 19 件の枠で既認識 |
| 2 | Prompt caching guidance | Already (強化不要) | 既存 SKILL.md に `cache_control` + `cache_read`/`cache_creation` + 90% Cost 表が揃っている |
| 3 | Context compaction primitives | Already (強化不要) | PreCompact/PostCompact hook + strategic-compact + `context-compaction-policy.md` が存在 |
| 4 | Model migration automation | N/A (Partial→N/A 修正) | Codex: 個人 dotfiles で migration 自動化スクリプト不要。ECC pull で同期されるなら dotfiles 側の仕事ではない |
| 5 | Managed agents onboarding | Already (強化不要) | `managed-agents-scheduling.md` + `setup-background-agents` skill で対応済み |
| 6 | SDK-aware code generation | N/A | Anthropic 公式の責務。dotfiles 側は `anthropic/skills` pull のみ |
| 7 | Partner tool integrations (CodeRabbit/JetBrains/Warp/Resolve AI) | N/A | 個人 dotfiles は Claude Code 中心、scope 外 |
| 8 | Skill distribution mechanism | Already (強化不要) | APM + everything-cc manifests + `skills-lock.json` で管理済み |

## Phase 2.5: Refine 結果

### Codex 批評結論
- Phase 2 判定を引き締め: Partial を N/A または未確認に降格
- claude-api model ID 陳腐化は load-bearing ではない — 単独 hygiene として独立処理すべき案件
- Pruning-First 推奨採用件数: **0 件**
- 「記事採用 0 件で単なるアナウンス」の可能性: 高

### Gemini 補完結論
- `anthropic/skills` repo は実在 (github.com/anthropics/skills) — ただし fork 維持コストは pull のメリットを下回る (推測)
- 公開 partner integration アナウンスメントは独立検証未確認
- 採用 0 件推奨で結論一致
- ※ Gemini 出力に含まれた「v2.1.116 / 2026-04-20 / 4日ラグ」等の具体数値は公式裏取り未確認のため `untrusted-stat` タグで記録

### 修正反映
- Pass 2 で Partial としていた #4 (Model migration automation) を N/A に格下げ (個人 dotfiles スコープ外)
- 全 8 項目が Already / N/A に収束し Gap なし → 採用 0 件確定

## Integration Decisions

**採用合計: 0 件**

- Gap / Partial: 全項目スキップ (該当なし)
- Already 強化: スキップ — model ID 更新 (#1) は独立 hygiene 扱い、吸収判断に連動させない
- Partner integration (#7): Claude Code 外ツールの話のため scope 外

## Lessons

1. **アナウンス記事のパターン認識**: Anthropic 公式の partner integration 発表は marketing 色が強く、個人 dotfiles に持ち込める新規 mechanism は少ない。技術的内容より普及拡大の意図が主体の記事は吸収候補として優先度が低い
2. **claude-api SKILL.md model ID 陳腐化は別件 hygiene**: SKILL.md 内のモデル ID (Opus 4.1/Sonnet 4.0/Haiku 3.5) の陳腐化は記事吸収とは独立した問題。MEMORY.md 既知 drift (skills:verify mismatch 19 件) の枠で処理し、吸収ループを汚染しない
3. **ベンダーバイアス警戒**: 公式記事であっても自社製品・エコシステム普及を目的とした宣伝記事として読む必要がある。Codex+Gemini 並列批評がこのバイアスを中和する
4. **Phase 2.5 価値の再確認**: Codex+Gemini 並列批評により Phase 2 の Partial 判定を引き締め、採用 0 件で正確に収束できた。アナウンス記事では特に批評フェーズが有効

## Plan

採用なし。独立 hygiene として記録のみ:

- `skills:verify` mismatch 修復 (claude-api model ID 更新) は既存 19 件 mismatch 対処タスクの一部として扱う
- 本 absorb セッションでは実装変更なし
