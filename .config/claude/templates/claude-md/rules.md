## IMPORTANT ルール

<agent_delegation>
タスクが並列実行可能、独立したコンテキストが必要、または専門知識が必要な場合にサブエージェントに委譲する。
単純なタスク、逐次操作、単一ファイル編集では直接作業する。
</agent_delegation>

<review_policy>
コード変更後のレビューは `/review` スキルのワークフローに従う（変更規模に応じてレビューアーを自動選択・並列起動・結果統合）。
</review_policy>

- 日本語で応答する

<important if="you are modifying hooks, scripts, settings.json, or lint configuration files">
- Harness contract: `docs/agent-harness-contract.md`。Hook が formatter/policy/completion gate/session を自動実行する
- IMPORTANT: `.eslintrc*`, `biome.json`, `.prettierrc*` 等の lint config は保護対象。設定ではなくコードを直す
- IMPORTANT: `git commit --no-verify` は絶対に禁止。違反すると hook 体系が無効化される
- コード変更は並列レビュー（codex-reviewer + code-reviewer）を受ける。初回から高品質なコードを書くこと
</important>

<important if="you are starting a non-trivial task or planning implementation">

- 非自明な変更では root の `PLANS.md` に従う。
- Claude Code の `plansDirectory` は `tmp/plans/` だが、長時間タスク、handoff、または将来参照したい plan は `docs/plans/` に昇格する。
- harness 変更、複数ディレクトリ変更、30 分以上の作業見込みでは plan を必須とする。

</important>

<important if="you are about to implement, investigate, or review code">

- 調査開始時は `/check-health` と `search-first` 系の workflow を優先する。
- 非自明なコード変更後のレビューは `/review` を使う。
- 完了前検証は `verification-before-completion` 系 workflow に従う。
- 長時間タスクや中断前は `/checkpoint` を使い、必要なら `docs/plans/` も更新する。
- 仕様が曖昧なまま実装に入らず、`/spec` や `/spike` を使う。
- 並列で別 task を走らせるときは worktree を使って session と filesystem を分離する。

</important>

<important if="you are modifying files in .config/claude/ or .bin/">

## Change Surface Matrix

- `.config/claude/CLAUDE.md`, `.config/claude/settings.json`, `.config/claude/scripts/`, `.config/claude/skills/`
  - 併せて見る: `PLANS.md`, `.config/claude/references/workflow-guide.md`, `docs/agent-harness-contract.md`
  - 最低検証: `task validate-configs`, `task validate-symlinks`
- `.config/claude/commands/`
  - 併せて見る: 対応する skill / script / workflow guide
  - 最低検証: 関連 skill / script の構文確認
- `.config/claude/agents/`, `.config/claude/references/`
  - 併せて見る: `references/workflow-guide.md` の Agent Routing Table、関連スキル定義
  - 最低検証: 参照整合性の目視確認（エージェント名・ファイルパスの一致）
- `.bin/symlink.sh`, `.bin/validate_symlinks.sh`
  - 併せて見る: Claude 側 symlink 対象、`Taskfile.yml`
  - 最低検証: `task symlink`, `task validate-symlinks`

</important>

<important if="you are creating a git commit">

## コミット規則

- conventional commit + 絵文字プレフィックス（例: ✨ feat:, 🐛 fix:, 📝 docs:, ♻️ refactor:, 🔧 chore:）
- `/commit` コマンドを使用

</important>
