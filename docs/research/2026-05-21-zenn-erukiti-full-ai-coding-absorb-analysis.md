---
source: "https://zenn.dev/erukiti/articles/2512-full-ai-cofing"
date: 2026-05-21
status: integrated
title: "実践フルAIコーディングのための考え方とノウハウ"
author: "erukiti"
published_at: "2024-12-08"
fetch_route: "defuddle"
trusted: false
---

## Source Summary

**主張**: コーディングエージェントのみで本格プロダクト開発を回す「フルAIコーディング」を実践するには、LLM の原理的欠陥（非決定的振る舞い／与えられた情報全部を正とする／矛盾・未知への勝手な解釈／要約の下手くそさ）を前提とした **メカニズム的制約**（linter / レイヤー構造 / 結合テスト / フェイズ分割）と **人間側の運用**（コンテキスト汚染時のセッション破棄・人力レビュー・AIデトックス）が不可欠。プロンプトを頑張れば頑張るほど矛盾が増えるため、eslint・eslint-plugin-boundaries による mechanism 強制が唯一の現実的補完手段。

**手法 (12)**:
1. TypeScript + 固定推奨スタック (Node LTS / pnpm / eslint / vitest / husky / React / Result 型)。bun test は LLM 出力読み取り問題で強く非推奨
2. eslint 厳格制約 (enum/class/throw/try-catch 禁止、Zod safeParse 強制、eslint-plugin-boundaries で import 方向強制)
3. レイヤー構造 + 腐敗防止レイヤー (依存方向の一方向化を eslint レベルで強制)
4. 結合テスト中心 + カバレッジ 100% (フロント view と barrel export 除く)
5. TSDoc + 詳細コメント強制 (テストには前提・事前条件・検証項目を明記)
6. 見積もりプロンプト (編集ファイル+行+DB+I/O+ログ+疑問点+矛盾点+フェイズ分割可否)
7. テスト変更と実装変更の分離 (プロンプトで強制)
8. コンテキスト汚染時のセッション破棄 (汚染されたコンテキスト上の修正は自家中毒)
9. Playwright MCP + 批判系 MCP
10. 汎用 AGENTS.md (Fail Fast / 暗黙フォールバック絶対禁止 / モック・NO-OP 実装禁止 / 主語省略禁止)
11. AIデトックス (毎日数時間 + 週1日、メタ認知訓練、副交感神経刺激)
12. 素振り (個人開発で月1本量産練習)

**根拠**: 筆者が9ヶ月コーディングエージェントを実務+趣味で使用した実体験。「カバレッジ 100%！」「ユニットテスト正常！」と LLM が出力結果に騙される具体事例を多数列挙。GPT-5.1/Gemini-3 現行世代では半年〜2年以上解決しない問題と提示。

**前提条件**: 本格プロダクト開発（メンテナンス性重要）におけるフルAIコーディング。TypeScript + pnpm + vitest 中心。LLM/コーディングエージェントの基礎知識がある読者。

## Gap Analysis (Pass 1 + Pass 2 + Phase 2.5 修正後)

| # | 手法 | 修正前判定 | Phase 2.5 修正後 | 詳細 |
|---|------|-----------|------------------|------|
| 1 | TypeScript + 固定推奨スタック | Partial | Partial | rules/typescript.md で厳格 TS 設定は完備、ライブラリ選定ルール (vitest/bun) は未整備 |
| 2 | eslint 厳格制約 / plugin-boundaries | Partial | Partial | protect-linter-config で設定保護はあるが、enum/throw 禁止等の具体ルール推奨は不足 |
| 3 | レイヤー構造 + 腐敗防止 | Already 強化可能 | Already 強化可能 | 概念は subagent-delegation-guide で存在。eslint mechanism 強制は不足 |
| 4 | 結合テスト中心 + 100% | Partial | Partial | testing.md は 3層+80%+。結合テスト優位の明示なし |
| 5 | TSDoc + 詳細コメント強制 | Already 強化可能 | Already 強化可能 | 公開 API への TSDoc 強制はあるが、テストコメント強制は不足 |
| 6 | 見積もりプロンプト / フェイズ分割 | Already 強化可能 | Already 強化可能 | task-decomposition-guide.md は INVEST 中心、具体プロンプトテンプレ不足 |
| 7 | テスト変更と実装変更の分離 | Partial | Partial | guideline レベル、プロンプト強制不足 |
| 8 | コンテキスト汚染時のセッション破棄 | Already 強化可能 | **Already (強化不要)** | AutoEvolve + MEMORY.md schema + Reset>Compaction 3 回ルールで永続化済 (Gemini 検証通過) |
| 9 | Playwright MCP + 批判系 MCP | Partial | **N/A** | agent-browser CLI + ui-observer agent で代替済、polyglot/CLI-first 方針と整合 |
| 10 | 汎用 AGENTS.md (Fail Fast) | Already 強化可能 | Already 強化可能 | silent-failure-hunter は agent レベル、CLAUDE.md core principle として明文化不足 |
| 11 | AIデトックス | Partial | **N/A (harness 外)** | 人間側ヘルスケア。dotfiles harness 範囲外 |
| 12 | 素振り | Not Found | **N/A (harness 外)** | 同上 |

## Phase 2.5: Refine (Codex 待ち回避 + Gemini + Opus self-critique)

### Gemini 周辺知識補完 (要点)
- eslint-plugin-boundaries + AI 自己修復ループは 2025-26 で定着
- **Polyglot 制約**: 「言語間で制約の厳格さに差があると、AI は緩い言語に複雑ロジックを押し込み、設計を歪める」 — 重要指摘
- MCP + プロンプトキャッシュによる「コンテキスト工学」が主流。MEMORY.md/スキル定義による永続化が知識喪失対策の主流（→ AutoEvolve + MEMORY.md schema で既にカバー）

### Opus self-critique
- (9, 11, 12) を Partial/Not Found から **N/A** に降格 (harness 範囲外、agent-browser で代替済)
- (8) を Already 強化可能 → **強化不要** に降格 (AutoEvolve + MEMORY.md schema で永続化済)
- TS 専用ルール (eslint-plugin-boundaries, Result 型, Zod) は **rules/typescript.md に閉じる**。CLAUDE.md core_principles には昇格させない (polyglot 配慮)

### Codex 状態
Codex は --background で task-mpeltjf6-atjhgv として投入済、結果待たず先行。後続セッションで `/codex:status task-mpeltjf6-atjhgv` で参照可能。

## Integration Decisions

### 採用 (6 項目)

| # | 項目 | 採用先 |
|---|------|--------|
| 10 | 暗黙フォールバック・モック・NO-OP 絶対禁止 (明文化) | CLAUDE.md core_principles 追記 |
| 6 | 見積もりプロンプトテンプレート | task-decomposition-guide.md 末尾追記 |
| 5 | テストコメント強制 TSDoc | rules/common/testing.md 追記 |
| 3 | eslint-plugin-boundaries (TS限定) | rules/typescript.md 追記 |
| 7 | テスト/実装フェイズ分離プロンプト | task-decomposition-guide.md 末尾追記 (T2 と統合) |
| 1 | TS 推奨スタック (vitest 優先) | rules/typescript.md 追記 (T4 と統合) |

### 棄却 (6 項目)

| # | 項目 | 理由 |
|---|------|------|
| 2 | eslint enum/class/throw 禁止 | (3) plugin-boundaries で構造強制は十分。enum/class/throw 全禁止は polyglot 不整合 + 過剰 |
| 4 | 結合テスト中心 + 100% | 既存 80%+ 目標を維持。記事の数字を直輸入しない (polyglot 配慮) |
| 8 | コンテキスト汚染検出 | AutoEvolve + MEMORY.md schema + Reset 3 回ルールで既存対応十分 |
| 9 | Playwright MCP + 批判系 MCP | agent-browser CLI + 批判系 agent (code/security/silent-failure) で代替済 |
| 11 | AIデトックス | harness 範囲外 (人間ヘルスケア) |
| 12 | 素振り | harness 範囲外 |

## Plan

### Task 1: 暗黙フォールバック・モック・NO-OP 絶対禁止の明文化
- **Files**: `.config/claude/CLAUDE.md`
- **Changes**: `<core_principles>` 内に新規 bullet 追加 — 「**暗黙フォールバック・モック残置・NO-OP 実装を絶対禁止**: 実装層で「とりあえず動かす」「後で直す」のためのモック・NO-OP・暗黙フォールバックを残してはならない。境界では Fail Fast、内部では Trust。詳細: silent-failure-hunter agent + dual-audience-cli-guide」
- **Size**: S

### Task 2: 見積もりプロンプト + フェイズ分離プロンプトの追加
- **Files**: `.config/claude/references/task-decomposition-guide.md`
- **Changes**: 末尾に 2 セクション追加
  - 「## M/L 規模タスクの事前見積もりプロンプト」 — 編集ファイル名+行番号+関連DBテーブル+カラム+ログ出力+I/O+疑問点+矛盾点+リファクタ必要箇所+フェイズ分割可否を列挙させるテンプレート
  - 「## テスト変更と実装変更のフェイズ分離プロンプト」 — 「ソースコード変更時はユニットテスト変更禁止」「ユニットテスト変更時はソースコード変更禁止」「適切にフェイズ分割せよ」
- **Size**: S

### Task 3: テストコメント強制 TSDoc
- **Files**: `.config/claude/rules/common/testing.md`
- **Changes**: 「## Test Comments」セクション追加 — 「テストには前提条件・事前条件・検証項目を TSDoc/docstring コメントで記述。プロジェクト外のエンジニアが読んで理解できる粒度」(polyglot 対応の汎用表現)
- **Size**: S

### Task 4: eslint-plugin-boundaries + vitest 推奨 (TS 限定)
- **Files**: `.config/claude/rules/typescript.md`
- **Changes**: 末尾に 2 セクション追加
  - 「## レイヤー強制 (eslint-plugin-boundaries)」 — 推奨理由 + allow/deny 例
  - 「## 推奨スタック」 — test runner は vitest 優先、bun test は LLM 出力読み取り問題のため非推奨
- **Size**: S

## 統合規模
4 ファイル変更 — 規模 **M**

## 関連ファイル
- `.config/claude/agents/silent-failure-hunter.md` (T1 と関係)
- `.config/claude/references/dual-audience-cli-guide.md` (T1 と関係)
- `docs/research/_index.md` (本レポート追加)
