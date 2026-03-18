# SkillNet 5D 評価・関係グラフ統合

**Date**: 2026-03-18
**Status**: Draft
**Source**: arXiv:2603.04448 — SkillNet: Create, Evaluate, and Connect AI Skills (zjunlp/SkillNet)

## Summary

SkillNet 論文の 5 次元スキル評価フレームワークと 4 種関係タイプを、既存の `skill-audit`、`skill-creator`、`skill-inventory.md` に統合する。新規ファイルは作成せず、既存 3 ファイルの拡張のみで完結する。

## Motivation

現在のスキル品質管理は A/B ベンチマーク（skill-audit）と 4 項目 Quality Gate（skill-creator）に依存しているが、スキル自体の静的品質を体系的に評価する仕組みがない。SkillNet の 5 次元評価は PhD 3 名による検証で QWK ≈ 1.000 の信頼性を持ち、15 万スキルの品質管理に使用されている実績がある。

## Approach

**アプローチ A（既存ツール拡張型）** を採用。理由:
- dotfiles はシンプリシティ最優先（KISS/YAGNI）
- ~56 スキルの管理に自動化スクリプトは過剰
- プロンプト原文が SkillNet コードから取得済みで、独自解釈不要

## Changes

### 1. skill-inventory.md — 関係テーブル拡充

**1a. arXiv 参照更新**

`arXiv:2603.11808` → `arXiv:2603.04448`

**1b. 関係タイプを 5 種に統一**

| 関係 | 由来 | 意味 |
|------|------|------|
| `depend_on` | SkillNet (既存 `depends-on` をリネーム) | A は B なしで実行不可 |
| `conflicts_with` | 独自 (維持) | A と B の同時使用禁止 |
| `belong_to` | SkillNet (既存 `is-a-subset-of` をリネーム) | A は B のワークフロー内の構成要素 |
| `similar_to` | SkillNet (新規) | A と B は機能的に等価・置換可能 |
| `compose_with` | SkillNet (新規) | A と B は独立だが頻繁に連携 |

`conflicts_with` は SkillNet 外だが残す。`similar_to` との違い:
- **`similar_to`**: 機能的に置換可能。同時使用は可能だが冗長（例: codex-review と review を状況に応じて選択）
- **`conflicts_with`**: 同時有効化が禁止。設計指針が矛盾するため併用すると出力品質が劣化する（例: frontend-design と ui-ux-pro-max）

**1a-2. ガイダンスセクション内の関係名表記も合わせて更新する**（`depends-on` → `depend_on`、`is-a-subset-of` → `belong_to` 等）。

**1a-3. skill-creator SKILL.md 内の arXiv 参照も更新**: Quality Gate セクション（line 77）の `arXiv:2603.11808` → `arXiv:2603.04448`。

**1c. 新規テーブル追加**

similar_to:

| Skill A | Skill B | 理由 |
|---------|---------|------|
| codex-review | review | どちらもコードレビュー。100行超では codex-review を先行 |
| senior-frontend | react-best-practices | React 最適化は両方カバー。深度が異なる |

compose_with:

| Source | Target | 理由 |
|--------|--------|------|
| spec | spike | spec で仕様定義 → spike で実験実装 |
| research | absorb | research で調査 → absorb で統合 |
| skill-creator | skill-audit | 作成後に品質監査 |

**1d. ガイダンス更新**

- `similar_to` 関係にあるスキルは、ユースケースに応じて使い分ける
- `compose_with` 関係にあるスキルは、連鎖実行を検討する

### 2. skill-audit — 5D Quality Scan ステップ追加

既存ワークフロー（Step 1-7）の **前段に** Step 0 として挿入。

**Step 0: 5D Quality Scan**

A/B ベンチマーク（重い）を回す前に、SKILL.md の静的品質を 5 次元でスクリーニング。

#### 5 次元の定義（SkillNet prompts.py:134-346 準拠）

| 次元 | Good | Average | Poor |
|------|------|---------|------|
| **Safety** | 破壊的操作をデフォルト回避、安全チェック含む、スコープ制限明示 | 良性ドメインだがリスク操作のセーフガード言及なし | 危険なアクション(delete/reset等)をガードなしで言及 |
| **Completeness** | 目標+手順+入出力が明確、前提条件(環境/パッケージ/権限)を記載 | 目標は明確だが手順/前提/出力が不十分 | 曖昧すぎて行動不能、核心的手順欠如 |
| **Executability** | 具体的アクション/コマンド/パラメータ。指示のみスキルは明確ガイダンスで OK | 概ね実行可能だが曖昧ステップ/環境前提あり | 実行不能("optimize it" 等の曖昧指示) |
| **Maintainability** | 狭いスコープ、モジュール性、明確な入出力、低結合 | 再利用部分はあるが境界や前提が不明確 | スコープ広すぎ or 密結合、適応方法不明 |
| **Cost-awareness** | 軽量タスクは本質的低コスト。重量タスクはバッチ/制限/キャッシュを明示 | コスト制御なしだが明らかに無駄な振る舞いもない | 無駄なワークフローを限度なく推奨 |

#### 追加ルール（SkillNet 原文準拠）

- `allowed_tools` が必要以上に広い場合 → Safety を 1 レベル下げ
- 医療/健康系で免責なし → Safety は最大 Average
- コア式/アルゴリズムの致命的エラー → Completeness を最大 Average（通常 Poor）
- 入力バリデーション欠如 → Completeness を最大 Average
- トリビアルなスクリプト（echo のみ等）→ Executability を最大 Average

#### 判定フロー

1. 対象スキルの SKILL.md + references/ + scripts/ を読む
2. 5 次元それぞれを Good/Average/Poor で判定
3. いずれかが Poor → audit report の「Improve」セクションに自動分類
4. 結果を audit report Summary テーブルの 5D 列に記録

#### audit report テーブル拡張（After イメージ）

5D 列は既存の A/B ベンチマーク列の**前に追加**する。既存列（Quality with/baseline/Delta）は維持。

```markdown
| Skill | Safety | Comp. | Exec. | Maint. | Cost | Quality (with) | Quality (baseline) | Delta | Recommendation |
|-------|--------|-------|-------|--------|------|----------------|--------------------| ------|----------------|
| skill-a | Good | Good | Avg | Good | Good | 7.5 | 6.0 | +1.5 | Keep |
| skill-b | Avg | Poor | Good | Avg | Good | — | — | — | Improve (5D) |
```

**5D のみ実行した場合**（A/B を省略）: Quality/Delta 列は `—` となり、Recommendation は 5D 結果のみで判断。

#### Step 0 と A/B の判定優先順位

5D 結果は A/B ベンチマーク結果を**上書きしない**。独立した判断軸として並記する:
- 5D で Poor あり → Recommendation に `(5D)` 注記を付与し「Improve」以上に分類
- A/B Delta が Keep でも 5D Poor があれば `Keep (5D: Improve)` と表記
- 最終判断は人間が両方を見て決定する

### 3. skill-creator — 5D Quality Check 追加

既存フローの SKILL.md 初稿完成後、Security Scan の直前に挿入。

```
Quality Gate (4項目) → Pattern Selection → Interview → Write SKILL.md
→ 5D Quality Check (新規)
→ Security Scan (既存)
→ Test Cases (既存)
```

#### チェック内容

```
1. Safety: 破壊的操作にガードがあるか？allowed_tools が必要最小限か？
2. Completeness: 前提条件・入出力・失敗モードが明示されているか？
3. Executability: 手順が具体的か？指示のみスキルの場合、ガイダンスが明確か？
4. Maintainability: スコープが狭く、モジュール性があり、他スキルと低結合か？
5. Cost-awareness: トークン効率を意識しているか？無駄なループや大量読み込みがないか？
```

Poor が 1 つでもあれば修正必須。Average は注記のみ。

## Evidence Sources

| 内容 | 出典 |
|------|------|
| 5 次元の定義・境界条件・追加ルール | [`zjunlp/SkillNet`](https://github.com/zjunlp/SkillNet) `skillnet-ai/src/skillnet_ai/prompts.py:134-346` (commit: initial release, 2026-03) |
| 4 関係タイプの定義 | [`zjunlp/SkillNet`](https://github.com/zjunlp/SkillNet) `skillnet-ai/src/skillnet_ai/prompts.py:838-893` |
| 評価の信頼性 | 論文 Section: PhD 3 名、200 スキル、QWK ≈ 1.000 |
| スキル定義フォーマット | [`zjunlp/SkillNet`](https://github.com/zjunlp/SkillNet) `experiments/src/skills/alfworld/*/SKILL.md` |

## Files Changed

| ファイル | 変更種別 | 変更量 |
|---------|---------|--------|
| `.config/claude/references/skill-inventory.md` | テーブル編集 | ~30 行追加・修正 |
| `.config/claude/skills/skill-audit/SKILL.md` | ステップ追加 | ~40 行追加 |
| `.config/claude/skills/skill-creator/SKILL.md` | セクション追加 | ~20 行追加 |

## Files NOT Changed

- CLAUDE.md, settings.json, hooks — 影響なし
- 新規ファイル — 作成しない
- scripts/ — 新規スクリプトなし

## Risks

- **低**: テーブルとチェックリストの追加のみ。既存ワークフローの動作に影響しない
- `is-a-subset-of` → `belong_to` のリネームで既存テーブル行が変わるが、`skill-audit` の参照は LLM ベースのため機械的な破損なし

## Future Upgrade Path

スキル数が増加し手動評価が負担になった場合、アプローチ B（Python スクリプト化）に移行可能:
- `scripts/eval/skillnet-evaluate.py` で LLM-as-Judge 自動評価
- `scripts/eval/skillnet-analyze.py` で関係グラフ自動構築
- SkillNet の `SKILL_EVALUATION_PROMPT` と `RELATIONSHIP_ANALYSIS_USER_PROMPT_TEMPLATE` をそのまま転用

## Acceptance Criteria

1. `skill-inventory.md` に 5 種の関係テーブル（depend_on, conflicts_with, belong_to, similar_to, compose_with）が存在し、arXiv 参照が 2603.04448 である
2. `skill-audit` SKILL.md に Step 0: 5D Quality Scan が存在し、5 次元の定義と Good/Average/Poor の境界条件が明記されている
3. `skill-creator` SKILL.md に 5D Quality Check セクションが存在し、Security Scan の前に配置されている
4. 全ての 5 次元定義が SkillNet `prompts.py` の原文に基づいている（独自解釈を含まない）。検証: Evidence Sources の GitHub URL からソースを参照
5. 既存のワークフロー（A/B ベンチマーク、Quality Gate 4 項目、Security Scan）が破壊されていない
6. audit report テンプレートに Safety/Comp./Exec./Maint./Cost 列が既存の Quality (with)/Quality (baseline)/Delta 列と並存している
7. `skill-creator` SKILL.md 内の arXiv 参照も `2603.04448` に更新されている
8. `skill-inventory.md` のガイダンスセクション内の関係名表記が新しい命名（`depend_on`, `belong_to` 等）に統一されている
