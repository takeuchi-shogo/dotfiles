---
status: reference
last_reviewed: 2026-04-23
---

# cwd/path Routing Matrix

**目的**: cwd（カレントワーキングディレクトリ）の種類に応じて、どの rules/skills/agents を読む or 読まないかを明示する。記事「Obsidian × Claude Code」(akira_papa_AI, 2026-03) の「パススコープ限定ルール」概念を dotfiles 環境に適合させた運用ガイド。

**前提**:
- 既存の `rules/*.md` は `paths:` frontmatter でファイルパターン条件ロードを既に実現
- このドキュメントは **cwd レベル** の上位 routing を定義（ファイルパターンより粒度が粗い）
- 違反は hook で detect、block はしない（Soft guidance）

## Routing Matrix

| cwd 種類 | 判定ヒント | 読む rules | 読む skills (優先) | 避ける skills |
|---|---|---|---|---|
| **dotfiles root** | `~/dotfiles` or `$CLAUDE_CONFIG_DIR` の親 | 全 common/ + 言語別（編集対象に応じ） | harness 系（skill-creator, update-config, hook-debugger, improve）、メタ系（autoevolve-core） | Obsidian 系（vault 固有）、sprint-task-sync |
| **Obsidian Vault root** | `~/Documents/Obsidian Vault` 系列、`.obsidian/` が存在 | common/overconfidence-prevention, common/language-choice のみ | obsidian-content, obsidian-knowledge, obsidian-vault-setup, note, digest, obsidian:* | harness 系（skill-creator, update-config）、言語別 rules |
| **外部 repo (Go)** | `go.mod` 存在、`~/dotfiles` 外 | common/* + go.md | review, commit, create-pr-wait, golang-reviewer | dotfiles 固有 hooks 改修系、Obsidian 系 |
| **外部 repo (TS/React)** | `package.json` + tsx, `~/dotfiles` 外 | common/* + typescript.md + react.md | review, commit, frontend-design, react-best-practices | dotfiles 固有系、Obsidian 系 |
| **その他 (unknown cwd)** | 上記いずれにも該当しない | common/code-quality, common/security の 2 つのみ | 汎用 (review, commit, debate, gemini, codex) | 環境固有スキル全般 |

## 判定フロー

```
cwd を取得
├── .obsidian/ が存在 → Obsidian Vault root
├── $CLAUDE_CONFIG_DIR の親または ~/dotfiles → dotfiles root
├── go.mod が存在 → 外部 repo (Go)
├── package.json が存在（かつ tsx/jsx ファイルあり） → 外部 repo (TS/React)
└── それ以外 → unknown cwd
```

## 既存 paths: frontmatter との関係

この matrix は「cwd レベル」、paths: frontmatter は「ファイルレベル」の 2 層で動く:

1. **cwd matrix（上位）**: その cwd でそもそも関連しうる rules/skills 群を絞る
2. **paths: frontmatter（下位）**: 編集対象のファイルパターンで rules/*.md を実際にロード

例: Obsidian Vault root にいる場合、`rules/go.md` は cwd matrix で除外。dotfiles root にいて `*.go` を編集する場合のみ `rules/go.md` が paths: でロードされる。

## 運用ポリシー

### Do
- cwd を判定して、明らかに無関係な skill は suggest しない（file-pattern-router hook が参考にする）
- Obsidian Vault では Obsidian 系 skill を優先 suggest
- dotfiles root では harness 系 skill を優先 suggest

### Don't
- cwd matrix で除外された skill を Claude が勝手に trigger しない
- Obsidian Vault root で dotfiles 固有の hook 編集を提案しない（混線リスク）
- ユーザーが明示的に呼んだ skill を cwd matrix で block しない（Soft guidance のみ）

## 検証

```bash
# cwd 判定のセルフテスト
cd ~/dotfiles && pwd   # → dotfiles root 判定
cd "~/Documents/Obsidian Vault" && ls .obsidian/  # → Obsidian Vault 判定
```

## Codex/Gemini の指摘を反映した注意点

- **Codex (2026-04-21 批評)**: 「当方は dotfiles 起点なので、Vault root 前提スキルと任意 cwd から動く bridge script の境界評価が必要」→ matrix の「読む skills」列で明示
- **akira_papa_AI 記事の前提との差分**: 記事は「純 Obsidian Vault 運用」、当 dotfiles は「dev 中心 + Vault 連携」→ dotfiles root と Obsidian Vault root を明確に分離
- **不完全性の自認**: この matrix は初版。運用して違反パターンが見つかったら `/improve` で更新

## 参照

- `rules/*.md` の `paths:` frontmatter（ファイルパターン条件ロード）
- `references/context-profiles.md`（default/planning/debugging/incident のプロファイル切替）
- `references/model-routing.md`（モデル別ルーティング）
- `docs/adr/0002-progressive-disclosure-design.md`（3 層構造）
- `docs/adr/0007-thin-claudemd-thick-rules.md`（薄 CLAUDE.md + 厚 rules/）
