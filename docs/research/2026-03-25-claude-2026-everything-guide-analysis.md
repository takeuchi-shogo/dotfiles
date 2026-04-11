---
source: "Everything Claude Has Shipped in 2026" by @kloss_xyz
date: 2026-03-25
status: integrated
---

## Source Summary

2026年3月23日時点の Claude 全機能ガイド。モデル (Opus/Sonnet/Haiku 4.6)、4モード (Chat/Cowork/Code/Projects)、拡張レイヤー (Skills/Agents/Hooks/Channels/MCP/Plugins)、API、ビジネス情報を網羅。

**主張**: 拡張レイヤーが真のレバレッジ。コンテキストファイルの品質がプロンプトスキルより重要。
**前提条件**: Claude Code/Cowork のパワーユーザー向け。初心者〜中級者の包括ガイド。

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 対応 |
|---|------|------|------|
| 1 | PostCompact hook | Gap | settings.json に追加済み |
| 2 | ExitWorktree hook | Gap | settings.json に追加済み |
| 3 | Telegram Channel | Partial | Discord のみ設定済み。Telegram は手動セットアップ待ち |
| 4 | effort "max" ルール | Partial | workflow-guide.md に使い分け基準を追加済み |

### Already (強化不要)

| # | 手法 | 既存の仕組み |
|---|------|-------------|
| 1 | Model routing | model-expertise-map.md, codex/gemini delegation rules |
| 2 | CLAUDE.md hierarchy + best practices | ~130行, conditional `<important if>`, IFScale メモリ |
| 3 | Rules directory with path scoping | 10 rules (言語別 + config) |
| 4 | Skills/Commands/Agents 体系 | 65+ skills, 30+ agents, 29 commands |
| 5 | Hooks 体系 | 8イベント, 20+ hooks, harness-rationale.md |
| 6 | Agent Teams | CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 |
| 7 | Subagents for context isolation | 30+ specialized agents |
| 8 | Independent review instance | 別エージェント(code-reviewer, codex-reviewer)で分離済み |
| 9 | Security scanning | security-reviewer + OWASP Top 10 + VeriGrey |
| 10 | Headless / CI/CD | autonomous + setup-background-agents + create-pr-wait |
| 11 | Context compaction 対策 | PreCompact hook + session-save + checkpoint |

### Already (強化済み)

| # | 手法 | 強化内容 |
|---|------|---------|
| 1 | MCP コスト監視 | /check-health に MCP トークンコストチェックステップ追加 |
| 2 | PostCompact ログ | PostCompact hook でコンパクションイベントをログ記録 |

### N/A (スコープ外)

Cowork 専用機能 (Connectors, Dispatch, Scheduled Tasks, Projects, Computer Use), Chrome extension, Voice mode, API Skills, Custom Visuals, Excel/PowerPoint add-ins

## Integration Decisions

- Gap #1-2: PostCompact + ExitWorktree hooks → settings.json に追加
- Partial #3: Telegram → 手動セットアップ待ち（BotFather でトークン作成が必要）
- Partial #4: effort "max" → workflow-guide.md に使い分け基準を追加
- 強化 #1: MCP コスト → /check-health に Step 3.7 として追加
- 強化 #2: PostCompact ログ → Gap #1 と同時実装

## Plan (実行済み)

1. settings.json: PostCompact + ExitWorktree hooks 追加
2. workflow-guide.md: Effort Level 使い分けセクション追加
3. check-health/SKILL.md: MCP コストチェック Step 3.7 追加

## Notes

- 記事は初心者〜中級者向けの包括ガイド。当セットアップは記事の全推奨事項を大幅に超えた構成
- 30+ の手法のうち、新規 Gap は 2 件のみ（PostCompact, ExitWorktree hooks）
- Cowork/API 系の機能は dotfiles スコープ外のため N/A
- Telegram Channel は必要時に `/discord:configure` の Telegram 版として手動セットアップ
