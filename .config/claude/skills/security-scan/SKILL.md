---
name: security-scan
allowed-tools: Bash(python3 *agentshield-filter.py*), Bash(npx ecc-agentshield *)
description: >
  AgentShield でエージェント設定のセキュリティ監査を実行する。CLAUDE.md、hooks、skills の安全性を検証。
  Triggers: 'security-scan', 'AgentShield', 'エージェント監査', 'agent security', '設定の安全性'.
  Do NOT use for: コードのセキュリティレビュー（use /security-review）、コード品質監査（use /audit）。
---

# Security Scan (AgentShield)

AgentShield (ecc-agentshield) で ~/.claude/ 配下の設定をセキュリティ監査する。
偽陽性フィルタ付きラッパーを使用。

## 引数

$ARGUMENTS

- 引数なし: `~/.claude/` をスキャン（デフォルト）
- `--fix`: auto-fixable な問題を自動修正
- `--format json`: JSON 出力（CI向け）
- `--path /path/to/.claude`: 対象変更
- `raw`: フィルタなしの生スキャン

## 実行

引数に `raw` が含まれる場合:

```bash
npx ecc-agentshield scan --path ~/.claude
```

それ以外（デフォルト）:

```bash
python3 $HOME/.claude/scripts/policy/agentshield-filter.py --path ~/.claude $ARGUMENTS
```

## スコアの解釈

| Grade | Score | 状態 |
|-------|-------|------|
| A | 90-100 | 堅牢 |
| B | 70-89 | 概ね良好 |
| C | 50-69 | 改善推奨 |
| D | 30-49 | 要対応 |
| F | 0-29 | 重大リスクあり |
