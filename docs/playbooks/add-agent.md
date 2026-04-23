---
status: active
last_reviewed: 2026-04-23
---

# Add Agent Playbook

新しい subagent を `.config/claude/agents/` に追加するときの 6-step。

## 前提

- agent = sub-context での専門タスク実行者（コードレビュー、デバッグ、リサーチ等）
- skill との違い: skill は手順、agent は context isolation + 専門 prompt
- 既存 agent を必ず確認（重複禁止）: `ls .config/claude/agents/`

## 6-step

### 1. Mode 決定

| Mode | 用途 | 例 |
|---|---|---|
| Read-only | 探索・調査・レビュー | code-reviewer, security-reviewer |
| Write-capable | 実装・修正 | golang-pro, typescript-pro |
| Background | 長時間タスク・並列 | autoevolve-core, codex-rescue |

**判定**:
- 副作用なしの分析 → Read-only
- ファイル編集が本質 → Write-capable
- 親 thread を pollute せず長時間 → Background

### 2. 既存 agent 重複確認

```bash
ls .config/claude/agents/ | head -50
grep -l "<関連トピック>" .config/claude/agents/*.md
```

近い agent があれば:
- 機能拡張で既存を改修
- 完全別物と判定できれば新規

### 3. YAML frontmatter 定義

```yaml
---
name: my-agent
description: |
  <1-2 行で何の専門家か + いつ使うか>。
  Use when: <発火条件 1>, <発火条件 2>.
  Do NOT use for: <反例 1>.
tools: Read, Bash, Glob, Grep         # 必要最小限
model: sonnet                          # opus / sonnet / haiku
---
```

**ポイント**:
- `tools` は最小権限（read-only なら Read/Glob/Grep のみ）
- `model` は task 規模で選ぶ（深い推論=opus、通常=sonnet、軽量=haiku）
- description は claude code agent picker で読まれる → 200 文字以内

### 4. プロンプト記述（本文）

`improve-policy.md` Rule 12: **ドメイン知識 ≥ 50%、行動指示 ≤ 50%**

```markdown
あなたは <専門領域> の専門家。

## ドメイン知識（50%以上）
- <主要パターン 1>
- <主要パターン 2>
- 既知の落とし穴: <Symptom-Cause-Fix>
- 過去の failure mode: <例>

## 行動指示（50%以下）
1. <ステップ 1>
2. <ステップ 2>
3. <出力フォーマット>
```

ドメイン知識が薄いと一般論しか返らず、行動指示だけだと専門家にならない。

### 5. スモークテスト

代表タスク 1 件で実行し、期待挙動を確認:

```text
Use the my-agent agent to: <代表タスク>
```

確認項目:
- 適切な tool 呼び出し（過剰 / 不足なし）
- 出力フォーマット遵守
- ドメイン知識が反映されているか

A/B 検証は `/skill-audit` の agent 版がないので manual。

### 6. Validate / Commit

```bash
task validate-configs                      # YAML frontmatter 構文
task validate-symlinks                     # symlink 経由参照

# agent 一覧の確認
ls .config/claude/agents/ | grep my-agent

git add .config/claude/agents/my-agent.md
git commit -m "feat(agents): add my-agent for ..."
```

## Anti-patterns

- ✗ tools に `*`（全権限）→ blast radius が広すぎる
- ✗ ドメイン知識なしの「行動指示だけ」prompt → 一般論しか返らない
- ✗ 既存 agent と機能重複（routing 精度↓）
- ✗ Read-only でいいのに Write-capable で作る
- ✗ description に Use when / Do NOT use の記載なし → 親 agent が呼べない

## 関連

- 設計原則: `.config/claude/references/agent-design-lessons.md`
- 委譲ガイド: `.config/claude/references/subagent-delegation-guide.md`
- 衝突パターン: `.config/claude/references/agent-conflict-patterns.md`
- 設定標準: `.config/claude/references/agent-config-standard.md`
- ドメイン知識比率: `.config/claude/references/improve-policy.md` Rule 11/12
