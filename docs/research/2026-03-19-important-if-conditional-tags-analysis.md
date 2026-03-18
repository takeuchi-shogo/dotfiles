---
source: https://www.humanlayer.dev/blog/stop-claude-from-ignoring-your-claude-md
date: 2026-03-19
status: integrated
---

## Source Summary

**主張**: CLAUDE.md の特定セクションを `<important if="condition">` タグで囲むことで、Claude Code の指示遵守率が向上する。

**手法**:
- `<important if="condition">` で条件付きブロックを作成
- 条件が現在のタスクにマッチするときのみ、Claude がそのセクションを重視する
- プロジェクト構造等の常時適用情報は囲まず、ドメイン固有ガイダンスのみ対象

**根拠**:
- CLAUDE.md は `<system_reminder>` で囲まれ「may or may not be relevant」とモデルに伝達される
- ファイルが長くなるほど個別セクションが「任意」扱いされ無視されやすくなる
- 明示的条件が「いつこの指示が関連するか」のシグナルを提供し、遵守率を改善
- 定量データはないが「noticeably better adherence」との報告

**前提条件**: CLAUDE.md が長く、セクションごとに関連するタスクが異なる場合に有効

**補足知見**（HumanLayer 別記事 + Anthropic 公式）:
- 指示バジェット: ~150-200 指示で遵守率が均一に劣化。system prompt で ~50 消費済み
- 強調マーカー（IMPORTANT, YOU MUST）で個別指示の遵守率を向上可能
- hooks は deterministic、CLAUDE.md は advisory。確実に実行すべきルールは hook 化

## Gap Analysis

| 手法 | 判定 | 詳細 |
|------|------|------|
| `<important if>` 条件付きタグ | **Gap** | 未使用。セマンティックタグはあるが条件シグナルなし |
| 指示バジェット意識 | **Partial** | MEMORY.md に IFScale 記載あるが CLAUDE.md 自体には未反映 |
| 強調マーカー | **Partial** | 見出しレベルの IMPORTANT はあるが個別指示への付与は少ない |
| Progressive Disclosure | **Already** | references/, skills/, agents/ で分離済み |
| 簡潔さ（300行以内） | **Already** | 118行 → 130行（タグ追加後も十分簡潔） |
| hooks で確実な実行 | **Already** | 広範な hook 体系を構築済み |

## Integration Decisions

全3項目を統合:

1. **`<important if>` 条件付きタグの導入** — 6セクションに適用
2. **個別指示への強調マーカー追加** — `--no-verify` 禁止と lint config 保護に IMPORTANT: 付与
3. **分析レポートの保存** — 本ファイル

## Changes Made

### `<important if>` タグ適用（6セクション）

| 旧タグ | 新条件 |
|--------|--------|
| `<harness_guarantees>` | `<important if="you are modifying hooks, scripts, settings.json, or lint configuration files">` |
| `<plan_contract>` | `<important if="you are starting a non-trivial task or planning implementation">` |
| `<mandatory_skills>` | `<important if="you are about to implement, investigate, or review code">` |
| (なし) Change Surface Matrix | `<important if="you are modifying files in .config/claude/ or .bin/">` |
| (なし) コミット規則 | `<important if="you are creating a git commit">` |
| (なし) dotfiles 固有の注意 | `<important if="you are working with file paths, symlinks, or directory structure">` |

### 囲まなかったセクション（常時適用）

- Role（全セッション共通）
- `<agent_delegation>`（タスクアプローチ判断に常時必要）
- `<review_policy>`（コード変更後に常時必要）
- ワークフロー表（タスク規模判定に常時必要）
- `<core_principles>`（全行動の基盤）
- 「日本語で応答する」

### 強調マーカー追加

- `git commit --no-verify` → `IMPORTANT: git commit --no-verify は絶対に禁止。違反すると hook 体系が無効化される`
- lint config 保護 → `IMPORTANT:` プレフィックス追加
