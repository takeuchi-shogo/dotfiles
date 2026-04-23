---
status: reference
last_reviewed: 2026-04-23
---

# System Prompt Policy

## 区分

| 区分 | 例 | 更新者 |
|------|-----|--------|
| Human-written | CLAUDE.md 本文、references/*.md | 人間 (ユーザー) |
| Hook-injected | golden-check 出力、plan-lifecycle 出力 | hooks (自動) |
| Auto-generated | MEMORY.md 自動追記、skill descriptions | AutoEvolve / tools |

## 方針

- Human-written セクションは `/improve` や AutoEvolve が**直接書き換えない**
- Hook-injected コンテンツは PreToolUse/PostToolUse コールバックで注入し、CLAUDE.md には含めない
- Auto-generated は `<!-- auto-generated -->` コメントで明示する (Markdown の場合)

## 品質保証

- Human-written 部分の変更は必ず Codex Review Gate を通す
- Auto-generated 部分の意図しない肥大化は measure-instruction-budget.py で検出する
