---
date: 2026-05-23
source_analysis: docs/research/2026-05-23-anthropic-complete-guide-building-skills-absorb-analysis.md
status: pending
scale: M-L
estimated_files: 8
priority: medium
---

# Plan: Anthropic Skills ガイド absorb 統合 (2026-05-23)

## Goal

Anthropic 公式 Skills ガイド (PDF 2026-01-27) の知見のうち Codex + Gemini 批評を経て採用された 5 件を dotfiles に統合する。既存の skill 設計優位 (5D Score / Gotchas / negative routing / tool scoping) を維持しつつ、eval 基盤・token tax 計測・category 管理・enforcement hook を強化する。

**採用しない判断を明記**: H16/H18/H39 全必須化 (公式 baseline の "全 skill に `## Critical`" と Subagent Inheritance) は Codex 批評で「dotfiles 優位維持」と判定されたため棄却済み。全 skill 一括変更は行わない。

---

## Tasks

### T1: 評価基盤の修正 (M) — 優先度: 高

**T1.1** `~/.claude/skills/skill-creator/scripts/run_eval.sh`

- 変更内容: SKILL.md を append するだけでなく、skill folder 全体 (scripts/ references/ assets/) をコンテキストにロードするよう修正
- 規模: S (スクリプト修正 ~20 行)
- 依存関係: なし (T1 内の先頭タスク)
- 検証: `bash run_eval.sh --dry-run` で出力に scripts/ references/ assets/ の内容が含まれること

**T1.2** `~/.claude/skills/skill-creator/scripts/aggregate.py`

- 変更内容: `--three-arm` フラグを実装する。arm_a.json / arm_b.json / arm_c.json を受け取り `delta_skill_vs_terse` と `delta_terse_vs_baseline` の 2 指標を出力する
- 規模: S (Python 追記 ~30 行)
- 依存関係: T1.1 完了後に実行 (eval 出力形式が確定してから)
- 検証: `python aggregate.py --three-arm arm_a.json arm_b.json arm_c.json` が JSON を出力すること

**T1.3** `~/.claude/skills/skill-creator/SKILL.md`

- 変更内容: Step 2.5 と Step 3 に「full-package eval が default になった (skill folder 全体をロード)」旨を追記
- 規模: XS (2-3 行追記)
- 依存関係: T1.1 完了後
- 検証: diff で追記行の存在確認

**T1.4** `~/.claude/skills/skill-audit/SKILL.md`

- 変更内容: Step 3「Optional: 3-arm evaluation」セクションの「現時点での最小実装」を「正式実装」に書き換え。`--three-arm` フラグの使用例を追記
- 規模: XS (3-5 行書き換え)
- 依存関係: T1.2 完了後
- 検証: diff で書き換え行 + 使用例の存在確認

---

### T2: Description Token Tax (S) — 優先度: 高

**T2.1** `~/.claude/skills/skill-audit/SKILL.md`

- 変更内容: Step 0.5 と Step 0.7 の間に **Step 0.6: Description Token Tax** を新設する
  ```
  ## Step 0.6: Description Token Tax
  1. enabled skill count: ls ~/.claude/skills/ | wc -l
  2. 各 skill の description 字数を合算
  3. budget 目安: 1000-1500 字相当
  4. over-budget の場合: Top heaviest skill を retire または description trim を推奨
  ```
- 規模: S (10-15 行追記)
- 依存関係: なし (T2 は T1 と独立)
- 検証: skill-audit 実行時に Step 0.6 が出力されること

---

### T3: Category 軸 + outcomes rubric (S) — 優先度: 中

**T3.1** `~/.claude/references/skill-inventory.md`

- 変更内容: 各 tier の skill リストに **use-case category 列** を追加する。カテゴリ値: Doc / Workflow / MCP-Enhance / Reference
- 規模: S (既存テーブルへの列追加)
- 依存関係: なし (T3 は T1/T2 と独立)
- 検証: `grep -c "Doc\|Workflow\|MCP-Enhance\|Reference" ~/.claude/references/skill-inventory.md` で全 tier に category が付与されていること

**T3.2** `~/.claude/skills/skill-audit/SKILL.md`

- 変更内容: 5D Quality Scan (Step 0) に **outcomes-not-features rubric** を追加する
  - description が「動詞+名詞+outcome」で始まるか
  - "features" 列挙になっていないか
  - 静的検査例: `grep -E "^(Add|Run|Generate|Check|Analyze|Build)"` で先頭動詞を確認
- 規模: XS (5-8 行追記)
- 依存関係: T2.1 の後に実施 (同ファイルへの変更を分割して diff を明確にする)
- 検証: Step 0 セクションに rubric が含まれること

---

### H10: README.md block hook (S) — 優先度: 中

**H10.1** `lefthook.yml` (dotfiles repo root)

- 変更内容: pre-commit hook を追加する
  ```yaml
  pre-commit:
    commands:
      no-skill-readme:
        run: |
          if find .config/claude/skills -name README.md | grep -q .; then
            echo "ERROR: skill folder に README.md は置かない (SKILL.md を使う)"
            exit 1
          fi
  ```
- 規模: XS (5-8 行追加)
- 依存関係: なし (H10 は T1/T2/T3 と独立)
- 検証: `.config/claude/skills/test/README.md` を作成して `git commit` → hook が block すること。その後テストファイルを削除

**H10.2** `~/.claude/references/skill-patterns.md` (または skill-writing-principles.md が存在する場合はそちら)

- 変更内容: 動的 enforcement の仕組みを documentation に追記。「validation-checklist の静的ルール (README.md 禁止) を lefthook pre-commit で動的に補強」を 1 段落追加
- 規模: XS (3-5 行追記)
- 依存関係: H10.1 完了後
- 検証: diff で追記行の存在確認

---

### H39: Pipeline/Guard/Gate 限定 `## Critical` top 化 (S) — 優先度: 低

**H39.1** `~/.claude/references/skill-patterns.md`

- 変更内容: Pipeline pattern セクションに以下を追記する
  > **`## Critical` section を top に置く** — Pipeline gate ("DO NOT proceed until") は Section header としてもまとめて SKILL.md の最上部近くに配置する。**適用対象: Pipeline / Guard / Gate 型 skill のみ。knowledge skill・reference skill には強要しない。**
- 規模: XS (5-8 行追記)
- 依存関係: H10.2 と同ファイル (H10.2 完了後に続けて実施)
- 検証: skill-patterns.md の Pipeline セクションに追記行が存在すること

---

## Dependencies

```
T1.1 → T1.2 → T1.3, T1.4 (T1 内は順序依存)
T2.1 → T3.2             (同ファイルへの変更は順序管理)
T3.1                    (独立)
H10.1 → H10.2 → H39.1  (同ファイル or 近接ファイルは順序管理)
```

T1 (script 修正) は T2/T3 (audit 拡張) より先に完了させると eval 基盤が整った状態で audit を拡張できる。H10/H39 は T1-T3 と独立して並行実施可能。

---

## Acceptance Criteria

| タスク | 完了条件 |
|--------|----------|
| T1 | `bash run_eval.sh --dry-run` で folder 全体がロードされること + `python aggregate.py --three-arm ...` が JSON 出力を返すこと |
| T2 | `skill-audit` 実行時に Step 0.6 が出力され、description token sum が数値で表示されること |
| T3 | `skill-inventory.md` の全 skill に category 列が付与されていること + Step 0 に outcomes rubric セクションが存在すること |
| H10 | `.config/claude/skills/*/README.md` を stage して commit → lefthook が exit 1 で block すること |
| H39 | `skill-patterns.md` の Pipeline セクションに `## Critical` 注記と「Pipeline/Guard/Gate のみ」の限定条件が明記されていること |

---

## Rollback

各タスクは git revert で安全に戻せる。

- **T1**: run_eval.sh / aggregate.py の git revert で eval 基盤を旧動作に戻せる
- **T2/T3**: SKILL.md への追記は revert で安全に取り除ける
- **H10 (lefthook hook)**: `lefthook.yml` から `no-skill-readme` command を削除するだけで無効化できる。段階的 enable: まず `skip: true` で dry-run 状態にして既存 skill に README.md がないことを確認してから有効化する
- **H39**: skill-patterns.md の追記を revert で戻せる

---

## Verification

実装完了後に以下を順に実行する:

```bash
# 1. config/symlink の健全性確認
task validate-configs
task validate-symlinks

# 2. lefthook hook の動作確認
touch .config/claude/skills/_test_dummy/README.md
git add .config/claude/skills/_test_dummy/README.md
git commit -m "test: hook check" --dry-run  # block されること
rm -rf .config/claude/skills/_test_dummy/

# 3. skill-audit dry-run (T2/T3 の出力確認)
# skill-audit を dry-run モードで実行し Step 0.6 の出力を確認

# 4. eval 基盤確認 (T1)
# cd ~/.claude/skills/skill-creator/scripts/
# bash run_eval.sh --dry-run 2>&1 | grep -E "scripts|references|assets"
```

---

## 採用しなかった手法 (記録)

Codex 批評で「公式 baseline 揃えるより dotfiles 優位維持」と判定されたため、以下は意図的に非採用:

- **H16 / H39 全必須化**: 全 skill への `## Critical` 強制 — knowledge skill の可読性を損なう。Pipeline/Guard/Gate のみに selective 適用 (H39 として採用)
- **H18 Subagent Inheritance**: PDF 原文に "subagent inheritance" という用語の明示を確認できず。community 推測の可能性があるため棄却
- **H30 A/B テスト**: 個人用途では ROI が低い
- **H34 version 管理**: overhead > benefit
