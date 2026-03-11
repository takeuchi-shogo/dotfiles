# Governance Setup Guide

## Branch Protection（推奨設定）

```bash
# GitHub CLI で設定
gh api repos/{owner}/{repo}/branches/main/protection -X PUT \
  --input - <<'EOF'
{
  "required_status_checks": {"strict": true, "contexts": ["ci"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 1},
  "restrictions": null
}
EOF
```

## CODEOWNERS

```
# Agent PRs require human review
.github/workflows/agent-* @{owner}
.github/agent-config/ @{owner}
```

## Agent Commit Identification

エージェントのコミットを識別するルール:
- ブランチ名: `agent/` プレフィックス
- PR ラベル: `automated` or `agent`
- Conventional commit format with emoji prefix

## Blast Radius Controls

- エージェントは feature branch でのみ操作。main/master への直接 push 禁止
- 各エージェント実行に `--max-cost` で予算上限を設定
- 全ワークフロージョブに `timeout-minutes` を設定
- PR レビュー必須（マージ前に人間の承認が必要）
