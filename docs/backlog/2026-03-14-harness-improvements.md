# Harness Improvements Backlog

Field Report "The Harness Is the Product" (2026-03-14) の分析から導出した改善。

## 完了済み (2026-03-14)

- P0: 命令バジェット削減（common rules 条件ロード化）
- P0: 競争的レビューパターン（CLAUDE.md）
- P0: Codex レビュー時 xhigh 強制
- P1: GP-004/GP-005 PreToolUse ブロッキング（Rust）
- P1: 多段コンテキスト圧縮ガイダンス（PreCompact 拡張）
- P2: プロジェクト Playbook 自動蓄積
- P2: MEMORY.md アーカイブ機構
- P2: Scaffolding/Harness 分離の文書化

## バックログ（優先度順）

1. **PreCompact Rust 移行** (M) — pre-compact-save.js → Rust binary に統合。起動遅延削減。
2. **承認永続化パターン** (L) — OpenDev L3。パターンベース自動承認でセッション跨ぎの承認疲れ防止。
3. **GP-006/007/008 セマンティック検出** (M) — OCP/ISP/DIP はパターンマッチ困難。code-reviewer 起動時にチェックリスト注入で対応。
4. **命令追従率の定量計測** (L) — skill-audit A/B テストで各 rule の実効性を測定。ETH Zurich 方式。

## 参照

- OpenDev paper: https://arxiv.org/abs/2603.05344
- HumanLayer CLAUDE.md: https://www.humanlayer.dev/blog/writing-a-good-claude-md
- ETH Zurich AGENTbench: https://www.marktechpost.com/2026/02/25/new-eth-zurich-study-proves-your-ai-coding-agents-are-failing-because-your-agents-md-files-are-too-detailed/
- Augment Code context waste: https://www.augmentcode.com/blog/your-agents-context-is-a-junk-drawer
