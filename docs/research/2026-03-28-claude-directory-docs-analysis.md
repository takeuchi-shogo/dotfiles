---
source: https://code.claude.com/docs/en/claude-directory
date: 2026-03-28
status: integrated
---

## Source Summary

Claude Code 公式ドキュメント「Explore the .claude directory」のインタラクティブファイルツリーエクスプローラー。
プロジェクトレベル（`.claude/`）とグローバルレベル（`~/.claude/`）の全ファイル構造、各ファイルの役割、
ロードタイミング、ベストプラクティスを網羅的に解説。

### 主な手法

1. `.worktreeinclude` — gitignored ファイルを worktree に自動コピー
2. `output-styles/` — セッション開始時にシステムプロンプトに注入するカスタムスタイル
3. `keybindings.json` — CLI キーボードショートカットのカスタマイズ
4. `argument-hint:` frontmatter — スキルの `/` メニューで引数ヒント表示
5. `$CLAUDE_SKILL_DIR` — スキル内シェルコマンドでスキルディレクトリを参照
6. `disable-model-invocation` / `user-invocable` — スキルの自動起動制御
7. `memory: project/local/user` — エージェントメモリのスコープ制御
8. commands → skills 移行推奨 — 公式は skills を推奨

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 統合内容 |
|---|------|------|----------|
| 1 | `.worktreeinclude` | Gap → 統合済み | `.env`, `.env.local`, `.env.worktree`, `settings.local.json`, `.config/zsh/local.zsh` |
| 2 | `output-styles/` | Gap → 統合済み | `concise.md`（超簡潔モード）、`teaching.md`（教育モード）を新規作成 |
| 3 | `keybindings.json` | Gap → 統合済み | スキーマ参照付きテンプレート。`Ctrl+E` で外部エディタ |
| 4 | `argument-hint:` | Partial → 統合済み | `prompt-review` に追加（唯一の欠落。10/71 → 11/71） |
| 5 | `$CLAUDE_SKILL_DIR` | Gap → 統合済み | `prompt-review` のスクリプトパスを `${CLAUDE_SKILL_DIR}/scripts/collect.py` に変更 |
| 6 | `disable-model-invocation` | Partial | 16/71 スキルで設定済み。superpowers ルーティングで代替 |

### Already 項目の強化分析

| # | 既存の仕組み | 強化内容 |
|---|-------------|----------|
| A | CLAUDE.md 136行 | 強化不要（200行以下推奨を遵守） |
| B | rules/ 全12ファイルに paths: 付き | 強化不要 |
| C | commands/ 29 + skills/ 71 | **強化済み**: 13 commands → skills/ に移行。commands/ 16 → skills/ 84 |
| D | agents/ 全32個 memory: user | **強化済み**: 14 agents → project、1 agent → local、17 agents → user 維持 |

## Integration Decisions

全7項目を統合:
1. `.worktreeinclude` 新規作成
2. `output-styles/` 新規作成（concise, teaching）
3. `keybindings.json` 新規作成
4. `argument-hint:` 追加（prompt-review）
5. `$CLAUDE_SKILL_DIR` 導入（prompt-review）
6. 13 commands → skills/ 移行
7. 15 agents のメモリスコープ変更（14 → project, 1 → local）

### Agent Memory スコープ変更詳細

**→ memory: project（14個）**:
backend-architect, build-fixer, code-reviewer, codex-reviewer, codex-risk-reviewer,
cross-file-reviewer, doc-gardener, frontend-developer, golang-pro, golang-reviewer,
nextjs-architecture-expert, security-reviewer, test-engineer, typescript-pro

**→ memory: local（1個）**:
product-reviewer

**memory: user 維持（17個）**:
autoevolve-core, codex-debugger, comment-analyzer, db-reader, debugger, design-reviewer,
document-factory, edge-case-hunter, gemini-explore, golden-cleanup, meta-analyzer,
safe-git-inspector, silent-failure-hunter, test-analyzer, triage-router, type-design-analyzer,
ui-observer
