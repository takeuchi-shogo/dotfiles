---
source: https://nyosegawa.com/posts/agents-md-generator/
date: 2026-03-27
status: integrated
---

## Source Summary

AGENTS.md は「生きたドキュメント」であるべきという主張。クローン時の自動生成、HTML コメントによるセクション保護、プレースホルダーの fill-remove ライフサイクルを提唱。agents-md-generator ツールでシェルラッパー経由の自動 seed を実装。

**主張**: AGENTS.md の陳腐化はコンテキスト汚染を招き、欠落より有害。自動生成 + 構造保護 + 積極メンテナンスが必要。

**手法**:
- git/ghq のシェルラッパーで clone 後に自動 seed
- HTML コメントバリアでエージェントの構造的書き換えを防止
- `[To be determined]` プレースホルダーの fill→remove ライフサイクル
- 含めるべき情報（非自明な判断、gotchas）と除外すべき情報（コードスタイル、ディレクトリ構造）の選別

**根拠**: Anthropic Best Practices、HumanLayer CLAUDE.md 長さ制約、実運用でのエージェントによるセクション自己削除の観察。

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | クローン時の自動 seed | **Gap** | `/init-project` は手動実行。clone 後の自動 seed なし |
| 3 | HTML コメントバリア | **Partial** | hooks で保護。インライン HTML コメントによるセクション保護なし |
| 4 | プレースホルダー戦略 | **Partial** | テンプレート生成はあるが placeholder→fill→remove ライフサイクルなし |

### Already (強化不要)

| # | 手法 | 既存の仕組み | 判定理由 |
|---|------|-------------|---------|
| 2 | 指示バジェット | IFScale + ETH Zurich 論文の知見統合済み | 「指示数ベース + 信号対雑音比」が上位互換 |
| 5 | コンテンツキュレーション | Progressive Disclosure + "hook > instruction" 原則 | 記事の除外基準は既存原則に包含 |
| 6 | 生きたドキュメント哲学 | doc-garden + /check-health + temporal-decay | 鮮度管理インフラが運用中 |

## Integration Decisions

全 Gap/Partial を取り込み:
1. ghq wrapper による clone 後自動 seed（`.config/zsh/functions/agents-md-seed.zsh`）
2. `/init-project` テンプレートに HTML コメントバリア + TBD プレースホルダー追加

## Plan

### Task 1: ghq clone 後の自動 seed
- **ファイル**: `.config/zsh/functions/agents-md-seed.zsh` (新規)
- **内容**: `_agents_md_seed()` ヘルパー + `ghq()` ラッパー関数
- **動作**: `ghq get` 成功後、CLAUDE.md/AGENTS.md 未存在なら最小テンプレートを seed

### Task 2: init-project テンプレート強化
- **ファイル**: `.config/claude/skills/init-project/references/level-templates.md` (既存修正)
- **内容**: ファクトリ委譲プロンプトに HTML コメントバリア + TBD プレースホルダー指示を追加
