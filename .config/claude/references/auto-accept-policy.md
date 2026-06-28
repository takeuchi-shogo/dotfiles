---
status: reference
last_reviewed: 2026-06-27
---

# Auto-Accept Policy

Plan 承認後、低リスクな変更を確認なしで実行するための判定基準。

## 判定マトリクス

### Auto-Accept（確認不要）

以下の **すべて** を満たす変更:
- 変更対象が `docs/`, `tests/`, `*.md`（CLAUDE.md を除く）のみ
- 単一ファイルの変更
- 既存の動作を変更しない（追加のみ）
- Plan で明示的に承認済みのスコープ内

### Confirm（要確認）

以下のいずれかに該当:
- 2ファイル以上の変更
- `scripts/`, `hooks/`, `commands/`, `agents/` の変更
- テストの削除・大幅変更
- 新しい依存関係の追加

### Never Auto-Accept（常に確認必須）

- `settings.json`, `settings.local.json` の変更
- `CLAUDE.md`, `.claudeignore` の変更
- セキュリティ関連ファイル（`*policy*`, `*security*`）
- `rm`, `git push`, `git reset` 等の破壊的操作
- 本番環境への影響がある変更
- `.env`, credentials, secrets を含むファイル

## 適用方法

1. Plan ステージで変更スコープを特定
2. 各変更を上記マトリクスで判定
3. Auto-Accept 対象のみ自動実行、それ以外はユーザーに確認
4. 判定に迷った場合は常に Confirm を選択（安全側に倒す）

## Auto Mode (公式機能) — 不採用の判断 anchor

Claude Code 公式の **Auto Mode** (AI classifier が各 tool call を allow/deny/escalate に自動分類、ユーザー発話から stated boundary 検出、Shift+Tab の Alt mode として `plan` 後に optional 出現) は実在し、**全プラン対応** (公式 docs "All plans"、research preview、grounding: 2026-06-27 `code.claude.com/docs/en/permission-modes`)。dotfiles は**意図的に不採用**:

- permission/safety の判断を LLM classifier に委譲せず、deterministic な allow/deny rule + hooks + on-request approval を維持する。理由: 監査可能性・再現性、Anthropic 自身が「誤許可あり」と明記、独立評価で曖昧境界の false-negative と file-edit coverage gap が指摘されている
- 同種の「LLM permission classifier」は 2026-05-31 cursor-run-mode absorb #4 / 2026-06-12 fable5-14steps で既に reject 済。Auto Mode の公式 1st-party 化・全プラン化はこの判断を覆さない (将来の automation-stack/permission 系 absorb の judgment anchor として記録)

## 注意事項

- このポリシーはガイドラインであり、hook による自動化は Phase 2 で検討
- `/careful` モード中は全変更が Confirm に昇格
- ユーザーが明示的に「全部やって」と指示した場合は Confirm 対象も実行可能
