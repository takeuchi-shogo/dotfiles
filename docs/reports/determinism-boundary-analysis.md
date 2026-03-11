# The Determinism Boundary × dotfiles リポジトリ 深層分析

**日付**: 2026-03-12
**契機**: Cornelius "Agentic Systems: The Determinism Boundary" 記事の調査

---

## 1. 決定論境界のマッピング

### 決定論的に保証されているもの（hooks）

| Hook | ファイル | 種類 | 保証内容 |
|------|---------|------|---------|
| `protect-linter-config.py` | PreToolUse(Edit\|Write) | Shell（完全決定論的） | リンター設定変更を `exit 2` でブロック |
| `auto-format.js` | PostToolUse(Edit\|Write) | Shell（完全決定論的） | Biome/Ruff/gofmt による自動整形 |
| `pre-commit-check.js` | PreToolUse(Bash) | Shell（完全決定論的） | コミットメッセージ検証 + シークレット検出 |
| `output-offload.py` | PostToolUse(Bash) | Shell（完全決定論的） | 150行/6000文字超を退避 |
| `completion-gate.py` | Stop | Shell（決定論的） | テスト実行 + Ralph Loop |
| `golden-check.py` | PostToolUse(Edit\|Write) | Shell（正規表現ベース） | GP-003〜005 を検出 |
| `suggest-compact.js` | PostToolUse(Edit\|Write) | Shell（決定論的） | 編集ループ検出（同一ファイル3回/10分） |
| `checkpoint_manager.py` | PostToolUse(Edit\|Write) | Shell（決定論的） | 3軸自動チェックポイント |
| `session-learner.py` | Stop/SessionEnd | Shell（決定論的） | イベント flush |
| permissions.deny | 設定 | パーミッション（完全決定論的） | `rm -rf`, `--no-verify`, `sudo` 等を絶対ブロック |

### 確率的コンプライアンスに依存しているもの（instructions）

| 指示 | 場所 | 現状 |
|------|------|------|
| Plan 作成の強制 | CLAUDE.md | Ralph Loop が部分補完。作成自体は未強制 |
| `/review` の実行 | CLAUDE.md | hook 強制なし |
| 検索してから実装 | CLAUDE.md コア原則 | hook 強制なし |
| エレガンスの追求 | CLAUDE.md コア原則 | 判断が必要。hook 化不可能 |
| C-001〜C-010 | constraints-library.md | プロンプト注入のソフト制約 |
| GP-001, GP-002 | golden-principles.md | golden-check.py で未実装 |

---

## 2. 決定論スペクトラム（完全版）

```
完全決定論 (exit 2 でブロック)
│  protect-linter-config.py    — リンター設定変更
│  pre-commit-check.js         — 保護ブランチ + シークレット
│  permissions.deny             — rm -rf, --no-verify, sudo
│
準決定論 (リトライ付きブロック)
│  completion-gate.py           — テスト失敗 + 未完了プラン (MAX_RETRIES=2)
│
自動実行 (ブロックなし)
│  auto-format.js               — Biome/Ruff/gofmt で自動整形
│  output-offload.py            — 大出力退避
│  checkpoint_manager.py        — 3軸自動チェックポイント
│  session-learner.py           — イベント永続化
│
警告 + コンテキスト注入
│  golden-check.py              — GP-003〜005 違反検出
│  error-to-codex.py            — エラー検出 + fix guide 注入
│  suggest-compact.js           — 編集ループ + コンパクション提案
│  post-test-analysis.py        — テスト失敗分析
│  plan-lifecycle.py            — プラン完了提案
│
提案のみ (additionalContext)
│  agent-router.py              — Codex/Gemini 委譲提案
│  suggest-gemini.py            — WebSearch → Gemini 提案
│
スキル (ユーザー起動)
│  /review, /check-health, /security-review
│
ドキュメント (参照のみ)
   GP-001, GP-002, C-001〜C-010, rules/common/*
```

---

## 3. AOP 構造的同型性

### アスペクト相互作用
PostToolUse(Edit|Write) の4 hook チェーン（auto-format → suggest-compact → golden-check → checkpoint_manager）で、golden-check は tool_input.new_string（フォーマット前）を検査。現時点では実害なし。auto-format に自動修正機能を追加した場合に顕在化するリスク。

### Obliviousness（不可視性）
agent-harness-contract.md が hook の概要を伝えるが、具体的な閾値（output-offload の 150行、golden-check のクールダウン 300秒、checkpoint の 15編集/60%/30分）は不可視。

---

## 4. 硬化軌道（Documentation → Skill → Hook）

### Hook まで硬化完了
- コードフォーマット → auto-format.js
- リンター設定保護 → protect-linter-config.py
- 空 catch/except 検出 → golden-check.py GP-004
- any/interface{} 検出 → golden-check.py GP-005
- 依存ファイル変更警告 → golden-check.py GP-003
- テスト通過確認 → completion-gate.py
- 破壊的 git コマンド防止 → permissions.deny
- 大出力のオフロード → output-offload.py
- シークレット検出 → pre-commit-check.js（C-007 の部分硬化）

### Skill レベルで停滞
- コードレビュー → `/review`（Review Gate で準強制可能）
- セキュリティレビュー → `/security-review`（OWASP パターンの hook 化可能）
- Plan 作成 → Ralph Loop が部分補完

### Documentation レベル
- GP-001（共有ユーティリティ優先） — AST 解析が必要で hook 化困難
- GP-002（バウンダリバリデーション） — 正規表現で hook 化可能
- C-001〜C-010 — 一部 hook 化可能

### 逆方向の降格
- doc-garden-check.py — SessionStart hook → `/check-health` スキルに降格（過自動化からの学習的後退）

---

## 5. 過自動化リスク評価

現在の hook は全て「2人の熟練レビュアーが同意する」テストをパス。
agent-router.py のキーワードマッチは「提案」にとどまっているため安全。
自動委譲への昇格は過自動化リスクが高い。

---

## 6. 改善提案（優先度順）

| # | 提案 | 工数 | 効果 |
|---|------|------|------|
| 1 | golden-check に GP-002（バウンダリバリデーション）追加 | S | 正規表現追加 |
| 2 | completion-gate に Review Gate 追加 | M | `/review` の確実実行 |
| 3 | agent-harness-contract.md に hook 閾値サマリー追記 | S | Obliviousness 対策 |
| 4 | C-007 の分類を Hybrid に修正 | S | ドキュメント正確性 |
| 5 | Search-First Gate 追加 | M | 「検索してから実装」準強制 |
| 6 | doc-garden-check 降格の教訓を MEMORY.md に記録 | S | 過自動化の知見 |

---

## 7. 総合評価

| 記事の概念 | 実装度 | 評価 |
|-----------|-------|------|
| 決定論的 Hook 層 | 10/14 hook がシェルコマンド型 | 優秀 |
| 4層スペクトラム | Shell 中心（HTTP/Prompt/Agent 不在） | 適切 |
| 習慣システム | auto-format, protect-linter, completion-gate | 優秀 |
| AOP 相互作用対策 | golden-check がフォーマット前を検査 | 要注意 |
| 確率的内部の緩和 | output-offload, Progressive Disclosure | 良好 |
| 硬化軌道 | 9要素が Hook、4要素が Skill で停滞 | 良好 |
| 過自動化の抑制 | 全 hook が判断を含まない | 優秀 |
| 摩擦の記録 | AutoEvolve が痕跡を保存 | 良好 |

このリポジトリは記事が描く理想像にかなり近い実装を持つ。特に「hook は判断を含まない」原則の一貫性と、doc-garden-check の Hook→Skill 降格は、過自動化からの学習的後退として価値が高い。
