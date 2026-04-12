---
source: "Garry Tan - Ten Design Principles of Agentic AI Skills Design (Thin Harness, Fat Skills)"
date: 2026-04-12
status: integrated
---

# Garry Tan「Thin Harness, Fat Skills」分析レポート

## Source Summary

**主張**: AI の 10x-100x 成果差はモデル選択ではなく「Skill の書き方」から生まれる。Skill は再利用可能なプロセス記述（レシピ）であり、パラメータ化された method call として設計すべきである。Yegge の 100x プログラマー論を援用しながら、skill ベースのエージェント設計が複利的価値を生む構造を解説する。

**10 原則**:

1. **Recipes, Not Orders** — 命令ではなくレシピ。Skill はパラメータ化された method call として設計する。「〇〇しろ」ではなく「〇〇の場合にどう考えて何をするか」を記述する
2. **Teach Thinking, Not Conclusions** — 結論ではなく思考プロセスを教える。エージェントが反対の結論も導けるかどうかを「Invert Test」で検証する
3. **Judgment vs Computation 境界** — ディナーテーブルに 8 人か 800 人かで判断基準を変える。latent（判断が必要）vs deterministic（計算で決まる）の境界を意識する
4. **Diarization** — 全コンテンツを一度読み込んでから構造化プロファイルを生成する。断片処理ではなく全体把握 → 抽出のフロー
5. **Right Document at Right Moment** — 必要なドキュメントを必要なタイミングで提供する resolver パターン。情報の全量注入ではなく適時開示
6. **Fat Skills, Thin Harness, Dumb Tools** — 3 層設計。Skill に知性を集中させ、Harness は薄く保ち、Tool は単機能に留める
7. **Fast & Narrow Tools** — 目的特化の tool は汎用ブラウザ自動化比で 150x 速い。Chrome MCP vs Playwright CLI の比較がその根拠
8. **Chase "Pretty Good"** — OK な応答に改善余地がある。満足な応答ではなく「まあまあ」な応答を追跡して改善する
9. **Write Once, Runs Forever** — 一度きりの作業の skill 化を禁止する。繰り返し実行されうる作業だけを skill にする
10. **Same Process, Different World** — 同じ skill を異なるパラメータ（context / world）で使い回す。skill の汎用性がその価値を複利的に高める

**根拠**:
- Yegge の 100x プログラマー論（成果差はモデルではなくプロセスから）
- イベントマッチング skill の OK 率 12% → 4%（改善の実データ）
- Chrome MCP vs Playwright CLI の 150x 速度差（Narrow Tool の実測）
- 複数の本番 skill 運用事例

**前提条件**: skill ベースのエージェントハーネスを既に持っていること。また、モデルの性能改善が skill の複利価値を押し上げるという前提に立っている（skill は技術的負債ではなく資産として扱う）。SaaS プロダクト内の専任チームより、個人 harness に適用するほうが効果は相対的に高い。

---

## Phase 2: Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Parameterized Skill | **Partial** | frontmatter に `pattern` はあるが `parameters` 仕様なし。phase-based 設計に留まり、呼び出し側からパラメータを渡す設計が未明文化 |
| 2 | Teach Thinking, Not Conclusions | **Exists** | `skill-writing-principles.md` 原則 1「指示を書け、知恵を書くな」が対応。ただし「Invert Test」（反対結論を出せるか）の具体的テスト手法は欠如 |
| 3 | Judgment vs Computation 境界 | **Exists** | DBS Rubric + `determinism_boundary.md` が latent/deterministic 分類を体系化済み |
| 4 | Diarization（全読込み → 構造化 profile） | **Exists** | `absorb` / `improve` / `research` スキルが cross-document 合成を実装。全量読み込み → 抽出フローが確立 |
| 5 | Right Document at Right Moment（resolver） | **Exists** | CLAUDE.md 130 行 + `<important if>` 条件タグ + `references/` Progressive Disclosure が対応。必要時にのみ参照ドキュメントを展開する設計 |
| 6 | Fat Skills / Thin Harness / Dumb Tools 3 層 | **Exists** | `docs/agent-harness-contract.md` が 3 層アーキテクチャを明文化。scripts/runtime/policy/lifecycle 分離が実装済み |
| 7 | Fast & Narrow Tools | **Partial** | 実体（cmux CLI, codex CLI, gemini CLI）はあるが、「なぜ narrow にするか」の設計原則ドキュメントが不在。意識的選択を文書化した箇所なし |
| 8 | Chase "Pretty Good"（OK Learning Loop） | **Exists** | `skill-writing-principles.md` 原則 8 自己スコアリング + AutoEvolve が OK 応答追跡 → 改善ループを実装 |
| 9 | Codification Discipline（Write Once, Runs Forever） | **Exists** | 原則 3.5「5 ステップ × 2 回以上実行した作業を skill 化」が対応。一度きりの作業の skill 化を明示的に禁止 |
| 10 | Same Process, Different World | **Partial** | 概念は理解されているが「同じ skill をどう異なる world で使い回すか」の事例集・設計パターンが不在。#1 と連動した課題 |

---

## Phase 2.5: Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | エッセイが示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `skill-writing-principles.md` 原則 1（思考プロセスを書く） | Invert Test が欠けている。「反対の結論を導けるか？」という自己検証ステップが明示されていない | 原則 1 の下に「1.1 Invert Test」小節を追加。skill 作成時のセルフチェック項目として組み込む | **強化可能** |
| S2 | Progressive Disclosure（CLAUDE.md + `<important if>` + references/） | Negative routing（衝突時の優先度・読まない条件）が弱い。「いつ参照しないか」が未定義 | `skill-conflict-resolution.md` に negative routing ルールと優先度マトリクスを追加 | **強化可能** |
| S3 | `wrapper-vs-raw-boundary.md`（直前の absorb で追加済み） | Narrow tool の「速さ」根拠が既存設計に統合されていない | wrapper-vs-raw の判断軸に「速度 × narrow 度」を追加 | **強化不要**（既存設計で十分） |
| S4 | AutoEvolve + OK Learning Loop | OK 応答の追跡が friction-events.jsonl 経由のみで、skill 個別の改善サイクルとの接続が弱い | AutoEvolve と skill 個別スコアリングの接続を明文化 | **強化不要**（現行実装で対応範囲内） |

---

## Phase 2.5: Codex + Gemini 批評の要点

### Codex の指摘

- **Parameterized Skill の形式主義リスク**: frontmatter に `parameters` 仕様を追加することは、thin harness の原則に反する形式主義になりうる。YAML スキーマ化よりも「Invocation Pattern 事例集」として自然言語で例示するほうが、skill の柔軟性を損なわない
- **Invert Test の優先度**: 原則 #2 の Invert Test は、Parameterized Skill よりも実装コストが低く効果が高い。skill を書いた後の自己チェックとして即座に組み込める
- **Narrow Tools のドキュメント化コスト**: 原則 #7 の設計原則ドキュメント化は nice-to-have。既存の `wrapper-vs-raw-boundary.md` が実質的に同機能を果たしているため、重複リスクあり
- **総評**: このエッセイの最大の貢献は「Invocation Pattern（#10）と Invert Test（#2）」の 2 点。他は既存設計が十分に対応済み

### Gemini の指摘

- **実装済み率の評価**: エッセイの 10 原則は dotfiles で約 70% が実装済み。残り 30% は #1/#10（Parameterized Invocation）と #2（Invert Test）に集中している
- **業界収束**: Cursor / MCP / Goose などの主要ツールが同じ「thin harness + fat skill」の方向に収束しつつあることを確認。このエッセイはトレンドの先読みではなく確認
- **「100x」の過大評価**: Yegge の 100x 論は引用として機能するが、skill 設計単体での 100x は過大。10x 程度の見積もりが実態に近い
- **Negative routing の重要性**: エッセイでは触れられていないが、dotfiles における最大の実装ギャップは「衝突時の skill 優先度（negative routing）」。#5（resolver）の裏面として重要

---

## Integration Decisions

### Gap / Partial → 採用・スキップ

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A | Invocation Pattern 事例集（#1/#10 対応） | **採用** | Parameterized Skill の YAML 形式化は避けつつ、自然言語での invocation 事例を `skill-invocation-patterns.md` として新規作成。skill の世界横断再利用を促進 |
| B | Invert Test 追加（#2 強化） | **採用** | `skill-writing-principles.md` 原則 1 の下に小節追加。実装コスト S、効果は高い |
| C | Skill Conflict Resolution（#5 negative routing） | **採用** | `skill-conflict-resolution.md` 新規作成。衝突時の優先度・negative routing ルール・規模ガードを整備 |
| D | Narrow Tools 設計原則ドキュメント（#7） | **スキップ** | `wrapper-vs-raw-boundary.md` が実質的に対応済み。重複ドキュメント作成を避ける。nice-to-have に留める |
| E | 本レポート保存 | **採用** | `docs/research/` への格納で知見を永続化 |

### Already 強化 → 採用・スキップ

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | Invert Test（Task B に統合） | **採用** | Gap/Partial 対応の Task B として実装。重複エントリ省略 |
| S2 | Negative routing（Task C に統合） | **採用** | Gap/Partial 対応の Task C として実装 |
| S3 | wrapper-vs-raw + narrow tool 速度軸 | **スキップ** | 既存設計で十分。過剰な追記はドキュメント肥大化を招く |
| S4 | AutoEvolve と skill スコアリング接続 | **スキップ** | 現行実装の範囲内。別途 `/improve` 実行時に対処 |

---

## Plan

### Task A: Invocation Pattern 事例集（新規作成）

- **File**: `.config/claude/references/skill-invocation-patterns.md`
- **Changes**: 同じ skill を異なる world で使い回す設計原則と事例集を記述。以下を含む:
  - "Same Process, Different World" 設計原則（Tan 原則 #10 の実装）
  - improve / absorb / research / モデルルーティング での実事例
  - Parameterized Invocation の自然言語パターン（YAML 形式主義を避けた記述）
  - いつ新規 skill を作り、いつ既存 skill をパラメータ変更で再利用するかの判断基準
- **Size**: M
- **Status**: 実装済み

### Task B: Invert Test 追加

- **File**: `.config/claude/skills/skill-creator/references/skill-writing-principles.md`
- **Changes**: 原則 1（思考プロセスを書く）の下に「1.1 Invert Test — 反対の結論を導けるか？」小節を追加。以下を含む:
  - Invert Test の定義と目的
  - skill 作成後の自己チェック手順（3 ステップ）
  - Invert Test が失敗する典型パターン（結論の埋め込み / 一方向フロー）
- **Size**: S
- **Status**: 実装済み

### Task C: Skill Conflict Resolution（新規作成）

- **File**: `.config/claude/references/skill-conflict-resolution.md`
- **Changes**: negative routing ルール、skill 衝突時の優先度、規模ガードを整備。以下を含む:
  - Negative routing の定義（「いつ skill を使わないか」）
  - 優先度マトリクス（skill 衝突時の解決順序）
  - 規模ガード（S/M/L タスクに対して呼び出してよい skill の組み合わせ制限）
  - Progressive Disclosure との関係（#5 の裏面としての位置づけ）
- **Size**: S
- **Status**: 実装済み

### Task D: Narrow Tools 設計原則ドキュメント — スキップ

- **理由**: `wrapper-vs-raw-boundary.md`（PostHog absorb で追加）が実質的に対応済み。重複作成を避ける。
- **Status**: スキップ

### Task E: 本レポート保存

- **File**: `docs/research/2026-04-12-tan-thin-harness-fat-skills-analysis.md`
- **Status**: 実装済み（本ファイル）

---

## 実装済みタスク詳細

### Task A: `skill-invocation-patterns.md`（新規）

以下の構成で実装:

1. **設計原則**: 同じ skill を異なる world で使い回す前提（Tan #10）
2. **事例集**:
   - `absorb` skill — 記事/論文/リポジトリ でパラメータ変更のみで同一フロー
   - `improve` skill — AutoEvolve (定期) / セッション後 / 手動 の 3 つの world
   - `research` skill — Codex/Gemini/Sonnet でモデルをパラメータとして切り替え
   - `review` skill — S/M/L 規模でレビューアーの組み合わせが変わるが skill は同一
3. **判断基準**: 「新規 skill か、パラメータ変更か」の決定木
4. **Parameterized Invocation パターン**: 自然言語での呼び出しパターン例示（形式主義を避けた記述）

### Task B: `skill-writing-principles.md` 追記

原則 1 の下に「1.1 Invert Test」を追加:

- **定義**: skill 作成後に「エージェントが反対の結論（例: 却下 / 採用しない / 別の選択）を出せるか」を確認するテスト
- **3 ステップ手順**: (1) skill の意図する結論を明示、(2) 反対結論のシナリオを想定、(3) skill がそのシナリオで反対結論を出せるか検証
- **失敗パターン**: 結論の埋め込み（"必ず〇〇を採用せよ" の埋め込み）/ 一方向フロー（分岐なし記述）

### Task C: `skill-conflict-resolution.md`（新規）

以下の構成で実装:

1. **Negative Routing 定義**: skill を「使わない条件」を明示。CLAUDE.md `<important if>` の裏面
2. **優先度マトリクス**:
   - 同一タスクに複数 skill が該当する場合の解決順序（specificity > recency > size）
   - 衝突検出の判断基準（同一 trigger / 重複 output / 矛盾する前提条件）
3. **規模ガード**: S タスクに L 規模 skill を呼び出す過剰適用を防ぐルール
4. **Progressive Disclosure との関係**: resolver (#5) が「いつ開くか」を決め、conflict resolution が「衝突時にどちらを開くか」を決める補完的な位置づけ

---

## 取り込まなかった内容

- **Narrow Tools 設計原則ドキュメント化（原則 #7）**: `wrapper-vs-raw-boundary.md` が実質対応済み。thin harness 精神に反した重複文書は作成しない
- **Parameterized Skill の YAML スキーマ化**: Codex 批評に従い形式主義を避けた。invocation 事例集（自然言語）で代替
- **AutoEvolve × skill スコアリング接続強化**: 現行実装で範囲内。別途 `/improve` 実行時の課題として保留
- **Weekly Traces Hour 相当の仕組み**: 個人 harness での dead weight リスクあり（PostHog absorb の Codex 批評を踏襲）

---

## 総評

**エッセイの実質カバー率**: 70%（Exists 6 / Partial 3 / 実質 Gap 1）

**既存ハーネスが先行している領域**:

| 領域 | 対応ファイル |
|------|-------------|
| Thin Harness / Fat Skills 3 層設計 | `docs/agent-harness-contract.md` |
| Teach Thinking（思考プロセス記述） | `skill-writing-principles.md` 原則 1 |
| Judgment vs Computation 境界 | `determinism_boundary.md` + DBS Rubric |
| Diarization（全量 → 構造化） | `absorb` / `research` / `improve` skill 群 |
| Right Document at Right Moment | CLAUDE.md `<important if>` + Progressive Disclosure |
| OK Learning Loop | AutoEvolve + `skill-writing-principles.md` 原則 8 |
| Write Once, Runs Forever | 原則 3.5（5 ステップ × 2 回以上） |

**エッセイが明示した実質的ギャップ**:

- **#1/#10 Parameterized Invocation**: 事例集なし → Task A で対応
- **#2 Invert Test**: 具体的テスト手法なし → Task B で対応
- **#5 Negative Routing**: resolver はあるが衝突解決ルールなし → Task C で対応

**Codex 批評の貢献**:
- Parameterized Skill の YAML 形式化が「thin harness に反する形式主義リスク」であることを指摘。YAML スキーマ化を回避し、自然言語での Invocation Pattern 事例集に切り替えた判断の根拠を提供
- 優先度整理: Invocation Pattern + Invert Test を最優先、Narrow Tools ドキュメント化はスキップ

**Gemini 批評の貢献**:
- 「70% 実装済み」という定量評価で過度な実装を抑制
- Negative routing の重要性指摘（エッセイでは触れられていない、dotfiles 固有のギャップ）
- 「100x」の過大評価への牽制（実態は 10x 程度）

**エッセイ自体の評価**:

| 次元 | 評価 |
|---|---|
| 直接タスク生成力 | 中（3 タスク採用、1 スキップ） |
| 既存設計との重複 | 高（70% カバー済み） |
| Codex 批評の追加価値 | **高**（形式主義リスクの指摘でアーキテクチャ判断を修正） |
| Gemini 批評の追加価値 | **中**（70% 定量評価と negative routing の重要性を追加） |
| 長期参照価値 | 高（Invocation Patterns は新規 skill 設計時の参照ポイント） |

---

## 今後のアクション（フォロー）

- 新規 skill 作成時に `skill-invocation-patterns.md` を参照し、既存 skill のパラメータ変更で代替できないか検討する
- skill 作成後に Invert Test（`skill-writing-principles.md` 1.1）を self-check で実施する
- `skill-conflict-resolution.md` の規模ガードを、複数 skill が候補になるタスク実行時に参照する
- 3 ヶ月後に Narrow Tools の設計原則ドキュメント化の ROI を再評価（現状スキップ判断の検証）

---

## References

- エッセイ関連:
  - `/Users/takeuchishougo/dotfiles/.config/claude/references/harness-10-principles-checklist.md` — wquguru 由来の別系統 10 原則との関係（補完的。Tan のエッセイとは出典が異なるが設計思想は収束）
  - `/Users/takeuchishougo/dotfiles/.config/claude/skills/skill-creator/references/skill-writing-principles.md` 原則 8 — 自己スコアリング = Tan の OK Learning Loop (#8) の dotfiles 実装
- 変更ファイル:
  - `.config/claude/references/skill-invocation-patterns.md`（新規 / Task A）
  - `.config/claude/skills/skill-creator/references/skill-writing-principles.md`（追記 / Task B）
  - `.config/claude/references/skill-conflict-resolution.md`（新規 / Task C）
- 関連先行 absorb:
  - `docs/research/2026-04-11-posthog-agent-first-rules-analysis.md`（wrapper-vs-raw-boundary.md はここで追加 / Task D のスキップ根拠）
  - `docs/research/2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md`（skill-writing-principles.md の構造確認）
  - `docs/research/2026-04-10-notebooklm-claude-extend-sessions-analysis.md`（DBS Rubric / 原則 #3 の dotfiles 実装確認）

---

*Generated: /absorb Phase 4 — 2026-04-12*
