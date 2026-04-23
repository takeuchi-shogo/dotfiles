---
status: active
last_reviewed: 2026-04-23
---

# Stale Doc Retirement Playbook

新しい pattern / ADR / skill を導入したときに、それと矛盾する旧ドキュメントを降格・削除する手順。Build to Delete 原則のドキュメント版実装。

## トリガ

以下のいずれかが発生したとき:
- 新しい ADR を `docs/adr/` に追加
- `/absorb` で外部知見を統合し、新 pattern が既存方針を置き換える
- 新 skill / hook / agent が既存の代替として機能する
- `doc-status-audit.py` で archive 判定された doc が 20 件超

## 6-step Numbered Workflow

### 1. Detect (旧 doc の特定)

新 pattern の kewyord で全ドキュメントを検索し、置き換え対象を列挙。

```shell
# 旧 pattern の命名を grep
rg -l "<old-pattern-name>" docs/ .config/claude/references/ .codex/

# 同一トピックの過去 research を確認
ls docs/research/ | grep <topic>
```

対象の選別基準:
- 新 pattern と方針が逆 → 降格必須
- 新 pattern と補完関係 → 残す（frontmatter に `see_also:` で相互リンク）
- 新 pattern の部分集合 → archive 候補（`superseded_by:` を付与）

### 2. Classify (frontmatter 更新)

旧 doc の frontmatter を archive に変更:

```yaml
---
status: archive           # active / reference → archive
last_reviewed: 2026-04-23
superseded_by: docs/adr/0008-new-pattern.md    # 置き換え先
archived_reason: "2026-04-23 に新 ADR で置換"
---
```

複数 doc をまとめて archive するときは `scripts/lifecycle/doc-status-audit.py --fix` ではなく手動で行う（archive 判定は load-bearing なのでスクリプト自動化しない）。

### 3. Pointer (先頭に明示マーカー)

旧 doc の本文先頭に 1 行目として archive マーカーを追加:

```markdown
> **[ARCHIVED 2026-04-23]** 本 doc は [new-pattern.md](../adr/0008-new-pattern.md) に置き換えられました。歴史的参照のみ。
```

この行で以下を達成:
- 読み手が冒頭で即座に archive と認識
- grep/semantic search で引かれても「ARCHIVED」で visible
- 次の Garden サイクルで削除候補として自動検出可能

### 4. Link audit (参照切れ検出)

archive 後に他 doc から旧 doc への link が切れないか確認:

```shell
task validate-readmes                      # local link 検証
rg -l "<old-doc-stem>" docs/ .config/      # 参照元を列挙
```

参照元があれば:
- link 先を新 doc に更新
- または `see_also:` として残す（歴史的文脈が必要な場合）

### 5. Wait (観察期間 30 日)

archive 直後に削除しない。30 日の観察期間を設ける理由:
- 実運用で参照されていないか `dead-weight-scan.py` で確認
- ユーザーが「archive にしたが必要だった」と気づく猶予
- 参照切れが発見されても復旧可能

観察期間中は `~/.claude/logs/dead-weight-*.jsonl` を `/improve` Garden フェーズで確認。

### 6. Delete (削除判断と実行)

30 日経過後、以下全て満たせば削除:
- `dead-weight-scan.py` で 30 日以上連続 `is_dead_weight=true`
- 参照元から全て link 更新済み（`task validate-readmes` green）
- `/improve` Garden で削除提案、ユーザー承認

削除実行:

```shell
# ファイル削除
git rm docs/research/OLD-pattern.md

# _index.md から該当行を削除（存在する場合）
$EDITOR docs/research/_index.md
```

削除を躊躇う場合の迂回ルート:
- `docs/archive/` ディレクトリに移動（deep archive）
- `superseded_by:` を残したまま削除せず保持

## 連携

- `.config/claude/references/improve-policy.md` Rule 51/52 — dead-weight-scan → Garden
- `scripts/lifecycle/dead-weight-scan.py` — 参照カウント + 経過日数
- `scripts/lifecycle/doc-status-audit.py` — frontmatter 一括監査
- `.config/claude/references/doc-status-schema.md` — status フィールド定義

## Anti-patterns (避けるべき挙動)

- **Bulk archive**: 一度に 50+ docs を archive → diff 爆発、参照切れ検出困難
- **Archive without pointer**: status 変更だけで本文に明示マーカーなし → grep で引かれ続ける
- **Delete without wait**: 30 日観察せず即削除 → 復旧不能、ユーザー困惑
- **Auto-delete**: スクリプトで自動削除 → 削除責任の不在、監査不能

## 頻度

- 新 ADR / 大きな absorb のたびに起動
- 月次 `/improve` Garden フェーズで定期 audit
- `dead-weight-scan.py` flagged が 20 件超えたら臨時実施
