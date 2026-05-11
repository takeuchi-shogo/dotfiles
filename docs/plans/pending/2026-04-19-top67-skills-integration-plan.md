---
status: active
last_reviewed: 2026-04-23
---

# Top 67 Skills 記事 — 統合実装プラン

**Date:** 2026-04-19
**Source Analysis:** `docs/research/2026-04-19-top67-claude-skills-analysis.md`
**Status:** Pending — `/rpi` で実行予定
**Scale:** M (3-5 files)

## ゴール

Top 67 Skills 記事の Codex 批評済み採用項目 (2 新規 skill + 1 既存強化) を dotfiles に統合する。MEMORY.md の Pruning-First 方針 と IFScale 制約を守り、skill 数を 93 → 95 に限定する。

## Non-Goals

- 記事の他 64 skills は導入しない (N/A または既存で代替済み)
- Change Log Generator / API Doc Generator は Codex 批評で却下済み、再検討しない
- Superpowers plugin 追加インストールは不要 (既に installed)

## タスク

### T1: Ubiquitous Language skill 新規作成 【M規模, ~3 files】

**目的:** 会話/コード/PRD/Issue から DDD glossary を抽出し、語彙 drift を検出する。

**成果物:**
- `~/.claude/skills/ubiquitous-language/SKILL.md` (実体: `dotfiles/.config/claude/skills/ubiquitous-language/SKILL.md`)
- `templates/glossary-entry.md`
- `references/extraction-heuristics.md`

**SKILL.md 構造 (概要):**
- Trigger: 「用語集作って」「glossary」「ubiquitous language」「語彙 drift」
- Workflow:
  1. Extract — 会話 + 指定 code/PRD/Issue から固有名詞・動詞句を抽出 (Haiku 委譲)
  2. Normalize — 既存の `docs/glossary.md` と突き合わせ、同義語/曖昧語を検出 (Opus)
  3. Propose — 新規エントリと修正提案を提示
  4. Persist — `docs/glossary.md` に追記 + Obsidian `05-Literature/glossary-{domain}.md` に同期
- Output: glossary.md セクション追記 + drift レポート
- Anti-patterns: 一般語を glossary に入れない、コンテキスト無しで追加しない

**依存:** なし (単独 skill)

**受入基準:**
- skill 作成後、`~/.claude/skills/ubiquitous-language/SKILL.md` が存在
- `ls .config/claude/skills/ | wc -l` が +1
- 試験的に現セッションで実行し glossary エントリが生成できる

### T2: Dependency Auditor skill 新規作成 【S-M規模, ~2 files】

**目的:** package.json / go.mod / Cargo.toml / requirements.txt から脆弱性/放棄/license/major lag を検査。

**成果物:**
- `~/.claude/skills/dependency-auditor/SKILL.md`
- `references/severity-matrix.md` (Critical/High/Medium/Low 基準)

**SKILL.md 構造 (概要):**
- Trigger: 「依存監査」「dependency audit」「npm audit」「脆弱性チェック」「放棄パッケージ」
- Workflow:
  1. Detect — lockfile/manifest を自動検出 (package.json / go.mod / Cargo.toml / requirements.txt / pyproject.toml)
  2. Scan — Sonnet に並列実行委譲:
     - npm: `npm audit --json` + `npm outdated --json`
     - Go: `go list -m -u all` + `govulncheck`
     - Rust: `cargo outdated` + `cargo audit`
     - Python: `pip list --outdated --format=json` + `pip-audit`
  3. Cross-reference — 各パッケージの license (deprecated? unmaintained?) を確認
  4. Prioritize — severity-matrix.md に基づき Critical/High/Medium/Low に分類
  5. Report — 優先度付き修正リストを表示
- Output: `docs/audits/deps-{date}.md` に保存 (optional)
- Anti-patterns: 全依存を一括 major update しない、CI 無しで lockfile だけ更新しない

**依存:** なし (単独 skill)

**受入基準:**
- skill 作成後、`~/.claude/skills/dependency-auditor/SKILL.md` が存在
- 当 dotfiles で試験実行: `package.json` なし → Go/Python 検出のみ。適切なメッセージを出せる
- severity-matrix.md に CVSS based の分類基準が定義されている

### T3: `spec` skill 強化 (PRD interview phase 追加) 【S規模, 1 file】

**目的:** Write a PRD 相当の interview フェーズを既存 `spec` skill に Phase 0 として追加。/interview skill とは独立 (spec 専用の軽量版)。

**変更対象:** `.config/claude/skills/spec/SKILL.md`

**追加内容:**
- Phase 0: PRD Interview (新規)
  - AskUserQuestion で以下の 6 項目を順次収集 (各 1 問、スキップ可):
    1. Goals — この仕様で何を達成したいか
    2. Non-goals — 明示的にやらないこと
    3. User stories — 誰がどう使うか (1-3 個)
    4. Success metrics — 成功をどう測るか
    5. Constraints — 技術/ビジネス/時間の制約
    6. Related systems — 既存のどのシステム/コードに触れるか
  - 既存の Phase 1 (spec 生成) の前に実行
  - 「skip all」オプションで既存動作 (direct spec generation) も維持

**影響:**
- 既存 spec workflow の下位互換を保つ (skip all で従来通り)
- `/interview` skill は残す (より深い interview が必要な場合用)

**受入基準:**
- `spec` skill 実行時に "Phase 0: Interview を実行しますか？" が聞かれる
- Yes で 6 項目 interview、No で従来動作
- 生成される spec file に interview 回答が反映される

### T4: MEMORY.md 更新 【S規模, 1 file】

**変更対象:** `/Users/takeuchishougo/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`

**変更:**
1. `## 外部知見索引` セクションに 1 行追加:
   ```
   - [Top 67 Claude Skills absorb](../../../dotfiles/docs/research/2026-04-19-top67-claude-skills-analysis.md) — 2 新規 skill (ubiquitous-language, dependency-auditor) + spec skill 強化。64 却下 (Pruning-First)
   ```
2. `## Claude Code エージェント設定` の skill 件数を 93 → 95 に更新 (該当箇所があれば)

**受入基準:**
- 追記のみ、既存エントリは変更しない
- MEMORY.md 行数が <150 を維持

### T5: Wiki log 追記 【自動, 1 file】

**変更対象:** `docs/wiki/log.md`

**追加内容:**
```markdown
## [2026-04-19] ingest | Top 67 Claude Skills
- ソース: polydao 記事 (X/Twitter)
- 判定: 34 Already / 8 Partial / 2 Gap / 23 N/A
- 取り込み: ubiquitous-language skill, dependency-auditor skill, spec skill 強化
- 却下: Change Log / API Doc Generator 他 (Codex 批評後)
```

## 実行順序と依存

```
T1 (Ubiquitous Language skill) ─┐
T2 (Dependency Auditor skill)  ─┼→ T4 (MEMORY.md 更新) → T5 (wiki log)
T3 (spec skill 強化)           ─┘
```

T1, T2, T3 は独立なので並列可。T4, T5 は T1-T3 完了後。

## 規模・見積もり

- 合計: 5-6 files (新規 4 + 編集 2)
- 想定作業時間: 新セッションで 30-45 分
- 想定モデル: Opus (判断・SKILL.md 構造設計) + Sonnet (本文生成・テンプレート作成)

## リスクと緩和

| リスク | 緩和策 |
|--------|--------|
| Ubiquitous Language が既存 Obsidian ワークフローと衝突 | skill 内で Obsidian skill への委譲ポイントを明示 |
| Dependency Auditor の並列実行が遅い | 検出したマネージャーのみスキャン (不要な言語はスキップ) |
| spec skill 強化がワークフロー破壊 | Phase 0 skip all で従来動作を維持 |
| skill 追加による discovery cost 増 | Trigger keyword を絞り込み、description を <120 字に |

## Acceptance Criteria (全体)

- [ ] `~/.claude/skills/` に `ubiquitous-language/` と `dependency-auditor/` が存在
- [ ] `spec` skill に Phase 0 interview が動作する (skip all で従来動作維持)
- [ ] MEMORY.md に分析レポートへの 1 行ポインタが追記されている
- [ ] `docs/wiki/log.md` に ingest エントリが追加されている
- [ ] `task validate-configs` が PASS
- [ ] `task validate-symlinks` が PASS (新規 skill dir が symlink 経由でアクセス可能)

## Post-Implementation

- 新規 skill を現セッションで試験的に実行し、期待通り動作するか確認
- 1 週間後に skill-audit で description conflicts を検査
- 採用効果を 2 週間後に `/improve` セッションで評価
