---
status: reference
last_reviewed: 2026-04-23
---

# CLI Tools (AGENTS.md 退避先)

このリポジトリに含まれる CLI ツール詳細。`AGENTS.md` から分離 (2026-04-23)。

## osa (OpenTelemetry Session Analyzer)

Claude Code のセッションログを解析し、ツール呼び出し統計・トークン使用量・ボトルネックを表示する。

```shell
# セッション一覧を表示
osa list
osa list --project dotfiles
osa list --json                  # JSON output for agents

# 直近セッションの統計を表示
osa analyze
osa analyze --last 5 --json      # JSON output for agents

# OTLP エンドポイントにエクスポート
osa export <session-file> --otlp http://localhost:4318
```

## validate_*.sh (.bin/)

dotfiles の検証スクリプト。`task validate` から一括実行可能。

```shell
task validate-configs       # config/script の構文チェック
task validate-symlinks      # managed symlink の検証
task validate-readmes       # README のローカルリンク検証
```

## 関連

- `AGENTS.md` — Codex 向け概要
- `Taskfile.yml` — task 定義の実体
- `.bin/` — validate/symlink スクリプト群
