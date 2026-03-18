# Skill Folder Enrichment Design

## Motivation

記事 "Skills Are Not Just Markdown Files" の核心的洞察:
**スキルはフラットな Markdown ではなく、scripts/data/templates/references を含む自己完結パッケージであるべき。**

現在の dotfiles スキル構成:
- 56 スキル中 **30 がフラット（SKILL.md のみ）**、20 がマルチ .md、6 のみリッチフォルダ
- リッチスキル率 **11%**（目標: enrichment archetype に基づき適切に構造化）

本設計は、5つの enrichment archetype を定義し、全56スキルを分類・優先度付けして段階的にリッチ化する。

## Design Decisions

| 決定 | 選択 | 理由 |
|------|------|------|
| アプローチ | パターン駆動（Archetype） | スキル間の一貫性確保、skill-creator への統合で将来品質も底上げ |
| 実行順序 | Tier 1→2→3（impact順） | 高頻度×大gap から着手、早期に効果を実感 |
| Guard 型 | enrichment しない | freeze/careful/verification は SKILL.md で十分機能 |
| ファイル命名 | kebab-case（既存慣習準拠） | ui-ux-pro-max, skill-creator と統一 |
| 過剰 enrichment の抑止 | archetype の「必要構造」と「任意追加」を明確分離 | YAGNI 原則。不要なスクリプトは作らない |

## Architecture

### 5 Enrichment Archetypes

#### 1. Guard（ガード型）
操作をインターセプトし安全を担保。**enrichment 不要。**

```
skill-name/
└── SKILL.md
```

**該当**: freeze, careful, verification-before-completion

#### 2. Pipeline（パイプライン型）
複数フェーズを順序実行し、ゲートで品質を担保。

```
skill-name/
├── SKILL.md              # フロー定義 + ゲート条件
├── templates/            # 出力フォーマット（必須）
│   └── output-template.md
├── references/           # フェーズ別詳細ガイド（推奨）
└── scripts/              # 自動化ステップ（任意）
```

**該当**: review, research, improve, check-health, absorb, continuous-learning, epd, validate, spike, autonomous, init-project, skill-audit, hook-debugger, search-first, create-pr-wait, interviewing-issues, obsidian-knowledge, ai-workflow-audit, prompt-review

#### 3. Generator（ジェネレータ型）
構造化されたファイルを生成。

```
skill-name/
├── SKILL.md              # ワークフロー + 生成ルール
├── templates/            # 出力テンプレート（必須）
│   └── {output}-template.md
├── scripts/              # データ収集・整形（任意）
└── data/                 # ドメイン固有コンテンツ（任意）
```

**該当**: daily-report, eureka, spec, digest, timekeeper, github-pr, obsidian-content, obsidian-vault-setup, setup-background-agents, frontend-design, meeting-minutes, weekly-review, morning

#### 4. Knowledge Base（知識ベース型）
ドメイン知識を構造化し、意思決定を支援。

```
skill-name/
├── SKILL.md              # クイックリファレンス + 判断フロー
├── references/           # パターンカタログ・チェックリスト（必須）
│   └── {domain}-patterns.md
├── data/                 # CSV/JSON 判断マトリクス（任意）
└── scripts/              # 検証ツール（任意）
```

**該当**: edge-case-analysis, senior-frontend, senior-backend, senior-architect, graphql-expert, react-best-practices, vercel-composition-patterns, ui-ux-pro-max, buf-protobuf, web-design-guidelines, react-expert, userinterface-wiki, dev-insights

#### 5. Tool Wrapper（ツールラッパー型）
外部 CLI ツールの最適な使い方を教える。

```
skill-name/
├── SKILL.md              # コマンドリファレンス + ベストプラクティス
├── scripts/              # ヘルパースクリプト（推奨）
│   └── helper.sh
├── examples/             # 実行可能サンプル（任意）
└── references/           # CLI リファレンスカード（任意）
```

**該当**: codex, codex-review, gemini, debate, webapp-testing

### Archetype メタファイル

skill-creator が新スキル作成時に参照するメタ定義:

```
skill-creator/
└── references/
    └── skill-archetypes.md   # NEW: 5 archetype の定義・判断フロー・テンプレート
```

## Implementation: Tier 1（7スキル, 14ファイル）

最高優先度。高頻度使用 × 大きな enrichment gap。

### 1. review — Pipeline

| ファイル | 種別 | 内容 |
|---------|------|------|
| `templates/synthesis-report.md` | NEW | 統合レポートフォーマット（findings, conflicts, confidence scores） |
| `scripts/extract-diff-stats.sh` | NEW | git diff から行数・ファイル数・言語比率を構造化出力 |

### 2. research — Pipeline

| ファイル | 種別 | 内容 |
|---------|------|------|
| `templates/subtask-prompt.md` | NEW | サブタスク投入用プロンプトテンプレート（context injection + output format） |
| `references/model-assignment-guide.md` | NEW | モデル特性と割り当て基準（Gemini: 外部リサーチ, Codex: 深い推論, claude -p: デフォルト） |

### 3. improve — Pipeline

| ファイル | 種別 | 内容 |
|---------|------|------|
| `templates/improvement-report.md` | NEW | 改善提案レポート（hypothesis, evidence, proposed change, risk） |
| `templates/experiment-log.md` | NEW | A/B テスト記録（baseline, variant, metrics, verdict） |
| `references/analysis-categories.md` | NEW | 4カテゴリ分析の詳細判断基準（errors, quality, agents, skills） |

### 4. check-health — Pipeline

| ファイル | 種別 | 内容 |
|---------|------|------|
| `templates/health-report.md` | NEW | ヘルスチェック結果（staleness, drift, broken refs の一覧表） |
| `references/staleness-criteria.md` | NEW | 鮮度判定閾値（days since update, line divergence thresholds） |

### 5. absorb — Pipeline

| ファイル | 種別 | 内容 |
|---------|------|------|
| `templates/analysis-report.md` | NEW | ギャップ分析レポート（current state, article insights, gaps, priorities） |
| `templates/integration-plan.md` | NEW | 統合プラン（task list, files to modify, risk assessment） |
| `references/triage-criteria.md` | NEW | 知見の取捨選択基準（適用コスト vs 効果マトリクス） |

### 6. daily-report — Generator

| ファイル | 種別 | 内容 |
|---------|------|------|
| `scripts/collect-session-stats.sh` | NEW | セッション統計自動収集（commits, files changed, models used, duration） |

### 7. eureka — Generator

| ファイル | 種別 | 内容 |
|---------|------|------|
| `templates/breakthrough-template.md` | NEW | Problem → Insight → Implementation → Metrics → Reuse Pattern |

## Implementation: Tier 2（13スキル, 24ファイル）

中優先度。中頻度 or 中程度の gap。

### Pipeline（5スキル）

| スキル | 追加ファイル |
|--------|-------------|
| continuous-learning | `templates/pattern-record.md`, `references/detection-signals.md` |
| epd | `templates/phase-transition.md`, `references/workflow-decision.md` |
| validate | `templates/validation-report.md`, `references/criteria-extraction.md` |
| spike | `templates/spike-report.md` |
| interviewing-issues | `templates/structured-spec.md`, `references/question-patterns.md` |

### Generator（3スキル）

| スキル | 追加ファイル |
|--------|-------------|
| spec | `references/precision-ceiling.md` |
| digest | `references/metadata-inference.md` |
| timekeeper | `scripts/accuracy-tracker.sh` |

### Knowledge Base（3スキル）

| スキル | 追加ファイル |
|--------|-------------|
| senior-frontend | `references/a11y-checklist.md` |
| senior-backend | `references/security-checklist.md`, `templates/api-spec-template.md` |
| senior-architect | `templates/architecture-proposal.md`, `templates/tech-evaluation.md` |

### Tool Wrapper（4スキル）

| スキル | 追加ファイル |
|--------|-------------|
| codex | `references/model-selection.md`, `scripts/codex-helper.sh` |
| codex-review | `templates/review-output.md`, `references/review-checklist.md` |
| gemini | `references/context-preparation.md`, `scripts/prepare-context.sh` |
| debate | `templates/debate-synthesis.md`, `references/debate-styles.md` |

## Implementation: Tier 3（12スキル, 14ファイル）

低優先度。各1ファイル程度の底上げ。

| スキル | Archetype | 追加ファイル |
|--------|-----------|-------------|
| skill-audit | Pipeline | `templates/audit-report.md` |
| create-pr-wait | Pipeline | `templates/ci-fix-log.md` |
| obsidian-knowledge | Pipeline | `templates/moc-template.md` |
| ai-workflow-audit | Pipeline | `references/audit-checklist.md` |
| obsidian-content | Generator | `templates/content-templates.md` |
| obsidian-vault-setup | Generator | `references/plugin-recommendations.md` |
| frontend-design | Generator | `references/anti-patterns.md` |
| meeting-minutes | Generator | `templates/minutes-template.md` |
| weekly-review | Generator | `templates/weekly-report.md` |
| morning | Generator | `templates/morning-routine.md` |
| web-design-guidelines | KB | `references/checklist-by-category.md` |
| react-expert | KB | `references/api-quick-ref.md` |

## 変更不要スキル（24スキル）

### 完成済みリッチスキル（8スキル）
react-best-practices, vercel-composition-patterns, ui-ux-pro-max, webapp-testing, setup-background-agents, autonomous, skill-creator, prompt-review

### Guard 型（3スキル）
freeze, careful, verification-before-completion

### 概ね完成（7スキル）
github-pr, graphql-expert, buf-protobuf, hook-debugger, search-first, init-project, codex(README あり)

### 低頻度・現状維持（6スキル）
dev-insights, dev-ops-setup, kanban, capture, userinterface-wiki, dev-insights

## Cross-Cutting: skill-creator 統合

新スキル作成時に archetype を自動参照するため、以下を追加:

```
skill-creator/references/skill-archetypes.md
```

内容: 5 archetype の定義、判断フローチャート、各 archetype のファイル構造テンプレート。
skill-creator の SKILL.md の "Pattern Selection" フェーズで参照するよう指示を追加。

## Success Criteria

1. **構造カバレッジ**: Tier 1-3 対象の32スキルすべてが archetype の「必要構造」を満たす
2. **出力品質安定**: テンプレート追加スキルの出力が、テンプレートの構造に従う
3. **SKILL.md 軽量化**: references/ 分離により、該当スキルの SKILL.md 行数が平均10-20%削減
4. **skill-creator 統合**: 新スキル作成時に archetype 選択プロンプトが表示される
5. **既存機能の無破壊**: 全スキルが enrichment 前と同等以上に機能する

## Risks

| リスク | 影響 | 緩和策 |
|--------|------|--------|
| テンプレートが実態と乖離 | 生成品質低下 | 各テンプレートは既存出力を分析して作成 |
| SKILL.md の参照パス破損 | スキル動作不全 | 追加後にスキル呼び出しテストを実施 |
| 過剰 enrichment | メンテコスト増 | archetype の「任意」は本当に必要な場合のみ |
| スクリプトの環境依存 | 他マシンで動かない | POSIX 互換 sh + jq のみ使用 |

## Out of Scope

- 既存 SKILL.md の内容リライト（構造追加のみ）
- data/ (CSV/JSON) の新規作成（Tier 2-3 では不要と判断）
- スクリプトの自動テスト基盤構築
- hooks との連携変更

## Implementation Order

```
Tier 1 (7 skills, 14 files)
  → Tier 2 (13 skills, 24 files)
    → Tier 3 (12 skills, 14 files)
      → skill-creator 統合 (1 file)
        → 検証 (全スキル動作確認)
```

各 Tier 完了後にコミット。Tier 間でレビューチェックポイントを設ける。
